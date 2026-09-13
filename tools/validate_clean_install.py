"""Validate explicit wheel/sdist inputs in separate temporary candidate environments."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import importlib.metadata as md
import importlib.util
import json
import platform
import sys
from pathlib import Path
import cv2
import numpy as np
import tifffile
from astropy.io import fits
import seestar_toolkit
prefix = Path(sys.prefix).resolve()
module = Path(seestar_toolkit.__file__).resolve()
assert sys.prefix != sys.base_prefix
assert platform.system() == "Darwin" and platform.machine() == "arm64"
assert module.is_relative_to(prefix) and "site-packages" in module.parts
assert seestar_toolkit.__version__ == md.version("seestar-toolkit") == "1.1.0"
for name in ("pytest", "ruff", "build", "reportlab", "weasyprint", "fpdf"):
    assert importlib.util.find_spec(name) is None, name
for dist in md.distributions():
    direct = dist.read_text("direct_url.json")
    assert not direct or not json.loads(direct).get("dir_info", {}).get("editable", False)
raw = fits.getdata("input.fit")
assert raw.shape == (1920, 1080) and raw.dtype == np.uint16
assert fits.getheader("input.fit")["BAYERPAT"].strip() == "GRBG"
expected = cv2.cvtColor(raw, cv2.COLOR_BayerGB2RGB)
with tifffile.TiffFile("output.tiff") as tiff:
    assert tiff.pages[0].photometric.name == "RGB"
    assert tiff.pages[0].bitspersample == 16
    output = tiff.asarray()
assert output.shape == (1920, 1080, 3) and output.dtype == np.uint16
np.testing.assert_array_equal(output, expected)
print(json.dumps({
    "python": platform.python_version(), "architecture": platform.machine(),
    "macos": platform.mac_ver()[0],
    "module": str(module),
    "module_relative": "<venv>/" + str(module.relative_to(prefix)),
    "dependencies": {d.metadata["Name"]: d.version for d in md.distributions()},
    "runtime_requires": md.requires("seestar-toolkit"),
    "output_shape": list(output.shape), "output_dtype": str(output.dtype),
    "pixel_equality": True, "dependency_separation": True,
}))
"""


def validate(python: Path, artifact: Path, fixture: Path) -> dict:
    """Capture failures as evidence, then remove the environment and outputs."""
    record = {"artifact": artifact.name, "status": "FAIL", "steps": []}
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("PYTHON", "PIP_")) and k != "VIRTUAL_ENV"
    }
    env.update(PYTHONNOUSERSITE="1", PIP_CONFIG_FILE=os.devnull)
    with tempfile.TemporaryDirectory(prefix="seestar-clean-", dir="/tmp") as temporary:
        work = Path(temporary)
        venv = work / "venv"
        outside = work / "outside"
        outside.mkdir()
        staged = outside / artifact.name
        shutil.copyfile(artifact, staged)
        shutil.copyfile(fixture, outside / "input.fit")

        def run(label: str, args: list[str]) -> str:
            result = subprocess.run(args, cwd=outside, env=env, text=True, capture_output=True)
            output = result.stdout + result.stderr
            for source, replacement in (
                (str(work.resolve()), "<temp>"),
                (str(work), "<temp>"),
                (str(ROOT), "<repository>"),
            ):
                output = output.replace(source, replacement)
            record["steps"].append({"name": label, "exit_code": result.returncode})
            if result.returncode:
                record["failure_output"] = output
                raise RuntimeError(label)
            return result.stdout

        try:
            run("create_venv", [str(python), "-I", "-m", "venv", str(venv)])
            assert "include-system-site-packages = false" in (venv / "pyvenv.cfg").read_text()
            executable = str(venv / "bin/python")
            run(
                "install",
                [
                    executable,
                    "-I",
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    "--disable-pip-version-check",
                    str(staged),
                ],
            )
            run("pip_check", [executable, "-I", "-m", "pip", "check"])
            cli = str(venv / "bin/seestar-toolkit")
            for label, args in (
                ("cli_version", [cli, "--version"]),
                ("module_version", [executable, "-I", "-m", "seestar_toolkit", "--version"]),
            ):
                record[label] = run(label, args).strip()
                assert record[label] == "seestar-toolkit 1.1.0"
            assert "convert" in run("help", [cli, "--help"])
            run("real_conversion", [cli, "convert", "input.fit", "output.tiff"])
            assert (outside / "output.tiff").is_file()
            record.update(json.loads(run("runtime_probe", [executable, "-I", "-c", PROBE])))
            assert hashlib.sha256((outside / "input.fit").read_bytes()).digest() == (
                hashlib.sha256(fixture.read_bytes()).digest()
            )
            record["status"] = "PASS"
        except (RuntimeError, AssertionError) as error:
            record["failure"] = str(error) or "validation assertion"
    record["temporary_environment_removed"] = not work.exists()
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    fixture = ROOT / "tests/data/seestar/light.fit"
    approved = json.loads((ROOT / "tests/data/public_fixtures.json").read_text())
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    assert digest == approved["tests/data/seestar/light.fit"]["sha256"]
    artifacts = [args.wheel.resolve(), args.sdist.resolve()]
    assert artifacts[0].name == "seestar_toolkit-1.1.0-py3-none-any.whl"
    assert artifacts[1].name == "seestar_toolkit-1.1.0.tar.gz"
    records = []
    for artifact in artifacts:
        records.append(validate(args.python.resolve(), artifact, fixture))
        args.report.write_text(
            json.dumps(
                {
                    "fixture": "tests/data/seestar/light.fit",
                    "fixture_sha256": digest,
                    "results": records,
                },
                indent=2,
            )
            + "\n"
        )
        print(artifact.name, records[-1]["status"], flush=True)
    if any(r["status"] != "PASS" for r in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
