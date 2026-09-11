"""Package version and public entry-point contracts."""

import importlib.metadata
import runpy
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import seestar_toolkit

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_exposes_version() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as source:
        authoritative = tomllib.load(source)["project"]["version"]
    assert authoritative == "1.1.0"
    assert seestar_toolkit.__version__ == authoritative
    assert importlib.metadata.version("seestar-toolkit") == authoritative


def test_version_uses_distribution_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def metadata_version(name: str) -> str:
        assert name == "seestar-toolkit"
        return "9.8.7"

    monkeypatch.setattr(importlib.metadata, "version", metadata_version)
    namespace = runpy.run_path(seestar_toolkit.__file__)
    assert namespace["__version__"] == "9.8.7"


def test_uninstalled_package_does_not_invent_version(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_version(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing_version)
    with pytest.raises(importlib.metadata.PackageNotFoundError):
        runpy.run_path(seestar_toolkit.__file__)


@pytest.mark.parametrize("module", [False, True], ids=["console", "module"])
@pytest.mark.parametrize(
    ("argument", "expected_code"), [("--version", 0), ("--help", 0), ("--invalid-option", 2)]
)
def test_public_entry_points(
    module: bool, argument: str, expected_code: int, tmp_path: Path
) -> None:
    command = (
        [sys.executable, "-m", "seestar_toolkit"]
        if module
        else [str(Path(sys.executable).with_name("seestar-toolkit"))]
    )
    result = subprocess.run(
        [*command, argument], cwd=tmp_path, capture_output=True, text=True, check=False
    )
    assert result.returncode == expected_code
    if argument == "--version":
        assert result.stdout.strip() == f"seestar-toolkit {seestar_toolkit.__version__}"
    elif argument == "--help":
        assert all(name in result.stdout for name in ("convert", "convert-batch", "archive"))
    else:
        assert "error:" in result.stderr
