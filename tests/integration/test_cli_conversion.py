"""Integration tests for single-file conversion through the CLI module entry point."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import tifffile

from seestar_toolkit.fits import read_fits_image

PROJECT_ROOT = Path(__file__).parents[2]
DATA_DIR = PROJECT_ROOT / "tests" / "data"


def _file_digest(path: Path) -> bytes:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").digest()


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "seestar_toolkit", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("relative_path", "expected_kind", "expected_itemsize"),
    [
        pytest.param("seestar/light.fit", "u", 2, id="raw-seestar"),
        pytest.param("seestar/stacked_mosaic.fit", "u", 2, id="native-seestar-rgb"),
        pytest.param("reference/siril_stacked.fit", "f", 4, id="siril-rgb"),
    ],
)
def test_module_cli_converts_representative_real_fits(
    tmp_path: Path,
    relative_path: str,
    expected_kind: str,
    expected_itemsize: int,
) -> None:
    input_path = DATA_DIR / relative_path
    output_path = tmp_path / "converted image.tiff"
    image = read_fits_image(input_path)
    source_stat = input_path.stat()
    source_digest = _file_digest(input_path)

    result = _run_cli("convert", str(input_path), str(output_path))

    assert result.returncode == 0
    assert str(output_path) in result.stdout
    assert result.stderr == ""
    assert output_path.is_file()
    written = tifffile.imread(output_path)
    assert written.shape == (image.height, image.width, 3)
    assert written.dtype.kind == expected_kind
    assert written.dtype.itemsize == expected_itemsize
    final_stat = input_path.stat()
    assert final_stat.st_size == source_stat.st_size
    assert final_stat.st_mtime_ns == source_stat.st_mtime_ns
    assert _file_digest(input_path) == source_digest


def test_module_cli_reports_missing_input_without_traceback(tmp_path: Path) -> None:
    missing_input = tmp_path / "missing.fit"
    output_path = tmp_path / "output.tiff"

    result = _run_cli("convert", str(missing_input), str(output_path))

    assert result.returncode == 1
    assert "Unable to read FITS file" in result.stderr
    assert "Traceback" not in result.stderr
    assert not output_path.exists()


def test_module_cli_rejects_invalid_fits_without_traceback(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.fit"
    output_path = tmp_path / "output.tiff"
    input_path.write_text("not a FITS file")

    result = _run_cli("convert", str(input_path), str(output_path))

    assert result.returncode == 1
    assert "FITS" in result.stderr
    assert "Traceback" not in result.stderr
    assert not output_path.exists()


def test_module_cli_preserves_existing_destination(tmp_path: Path) -> None:
    input_path = DATA_DIR / "seestar" / "light.fit"
    output_path = tmp_path / "existing.tiff"
    original_content = b"existing file content"
    output_path.write_bytes(original_content)

    result = _run_cli("convert", str(input_path), str(output_path))

    assert result.returncode == 1
    assert "Failed to write TIFF" in result.stderr
    assert "Traceback" not in result.stderr
    assert output_path.read_bytes() == original_content
