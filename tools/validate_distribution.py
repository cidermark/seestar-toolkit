"""Build from clean inputs, inspect both archives and test runtime-only installs."""

from __future__ import annotations

import configparser
import email
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=cwd, env=env, check=True)


def inspect_archive(path: Path, project: dict, modules: set[str]) -> None:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            files = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
        metadata_path = "seestar_toolkit-1.1.0.dist-info/METADATA"
        source_prefix = ""
        allowed = modules | {
            "seestar_toolkit-1.1.0.dist-info/" + n
            for n in (
                "METADATA",
                "WHEEL",
                "RECORD",
                "entry_points.txt",
                "top_level.txt",
                "licenses/LICENSE",
            )
        }
    else:
        with tarfile.open(path) as archive:
            files = {}
            for member in archive.getmembers():
                assert member.isdir() or member.isfile(), "Unexpected archive link/type"
                if member.isfile():
                    stream = archive.extractfile(member)
                    assert stream is not None
                    files[member.name.split("/", 1)[1]] = stream.read()
        metadata_path = "PKG-INFO"
        source_prefix = "src/"
        allowed = (
            {source_prefix + m for m in modules}
            | {
                "pyproject.toml",
                "MANIFEST.in",
                "README.md",
                "CHANGELOG.md",
                "LICENSE",
                "PKG-INFO",
                "setup.cfg",
            }
            | {
                "src/seestar_toolkit.egg-info/" + n
                for n in (
                    "PKG-INFO",
                    "SOURCES.txt",
                    "dependency_links.txt",
                    "entry_points.txt",
                    "requires.txt",
                    "top_level.txt",
                )
            }
        )
    assert set(files) <= allowed, f"Unexpected distribution members: {set(files) - allowed}"
    assert {source_prefix + m for m in modules} <= set(files), "Missing package modules"
    for content in files.values():
        assert not re.search(
            rb"/Users/|/Volumes/|/home/|[A-Z]:\\Users\\|"
            rb"com~apple~CloudDocs|BEGIN [A-Z ]*PRIVATE KEY",
            content,
        ), "Private path or credential marker in distribution"
    metadata = email.message_from_bytes(files[metadata_path])
    assert metadata["Name"] == project["name"] == "seestar-toolkit"
    assert metadata["Version"] == project["version"] == "1.1.0"
    assert metadata["Author"] == "Mark Wymer"
    assert metadata["License-Expression"] == "MIT"
    assert metadata["Requires-Python"] == project["requires-python"] == ">=3.11"
    requirements = metadata.get_all("Requires-Dist", [])
    runtime = {r.replace(" ", "") for r in requirements if ";" not in r}
    assert runtime == {r.replace(" ", "") for r in project["dependencies"]}
    assert set(metadata.get_all("Provides-Extra", [])) == {"dev", "build"}
    assert (ROOT / "README.md").read_text().strip() == metadata.get_payload().strip()
    license_path = next(n for n in files if n.endswith("LICENSE"))
    assert files[license_path] == (ROOT / "LICENSE").read_bytes()
    entry = next(n for n in files if n.endswith("entry_points.txt"))
    parser = configparser.ConfigParser()
    parser.read_string(files[entry].decode())
    assert dict(parser["console_scripts"]) == {"seestar-toolkit": "seestar_toolkit.cli:main"}
    print(f"PASS: {path.name}: {len(files)} allowed members; metadata/license/entry point")


SMOKE = """
import importlib.metadata as md
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
import tifffile
from astropy.io import fits
import seestar_toolkit
from seestar_toolkit.conversion import convert_fits_to_tiff
module = Path(seestar_toolkit.__file__).resolve()
assert module.is_relative_to(Path(sys.prefix).resolve())
assert "site-packages" in module.parts
assert seestar_toolkit.__version__ == md.version("seestar-toolkit") == "1.1.0"
for name in ("pytest", "ruff", "build", "reportlab", "weasyprint", "fpdf"):
    assert importlib.util.find_spec(name) is None, name
for name in ("astropy", "numpy", "cv2", "tifffile"):
    assert importlib.util.find_spec(name) is not None, name
image = np.arange(3 * 7 * 5, dtype=np.float32).reshape(3, 7, 5) / 128
fits.writeto("smoke.fit", image)
convert_fits_to_tiff("smoke.fit", "smoke.tiff")
np.testing.assert_array_equal(tifffile.imread("smoke.tiff"), np.moveaxis(image, 0, -1))
print("PASS: runtime-only import:", module.relative_to(Path(sys.prefix)))
print("Runtime distributions:", json.dumps(sorted(d.metadata["Name"] for d in md.distributions())))
"""


def smoke(artifact: Path, directory: Path) -> None:
    environment = directory / "environment"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / "bin/python"
    outside = directory / "outside"
    outside.mkdir()
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    run(
        str(python),
        "-I",
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        str(artifact),
        cwd=outside,
        env=env,
    )
    run(str(python), "-I", "-m", "pip", "check", cwd=outside, env=env)
    for command in (
        [str(environment / "bin/seestar-toolkit"), "--version"],
        [str(python), "-I", "-m", "seestar_toolkit", "--version"],
    ):
        output = subprocess.check_output(command, cwd=outside, env=env, text=True).strip()
        assert output == "seestar-toolkit 1.1.0", repr(output)
        print(f"PASS: {artifact.name} entry point: {output}")
    run(str(python), "-I", "-c", SMOKE, cwd=outside, env=env)


def main() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    with tempfile.TemporaryDirectory(prefix="seestar-distribution-") as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        for name in ("pyproject.toml", "MANIFEST.in", "README.md", "CHANGELOG.md", "LICENSE"):
            shutil.copyfile(ROOT / name, source / name)
        modules = set()
        for module in (ROOT / "src/seestar_toolkit").rglob("*.py"):
            relative = module.relative_to(ROOT)
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(module, target)
            modules.add(str(module.relative_to(ROOT / "src")))
        output = work / "dist"
        # Default build makes an sdist, then builds the wheel FROM that sdist.
        run(sys.executable, "-m", "build", "--outdir", str(output), cwd=source)
        assert {p.name for p in output.iterdir()} == {
            "seestar_toolkit-1.1.0-py3-none-any.whl",
            "seestar_toolkit-1.1.0.tar.gz",
        }
        for artifact in sorted(output.iterdir()):
            inspect_archive(artifact, project, modules)
            smoke(artifact, work / artifact.name)
    print("PASS: isolated build, wheel and sdist runtime validation; temporary outputs removed")


if __name__ == "__main__":
    main()
