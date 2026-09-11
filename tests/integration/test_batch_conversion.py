"""Integration tests for flat-directory batch conversion with real FITS data."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import tifffile

from seestar_toolkit.batch import convert_fits_directory

DATA_DIR = Path(__file__).parents[1] / "data"


def _fingerprint(path: Path) -> tuple[int, int, bytes]:
    stat = path.stat()
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").digest()
    return stat.st_size, stat.st_mtime_ns, digest


def test_batch_converts_mixed_real_fits_and_preserves_sources(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    input_directory.mkdir()
    fixtures = {
        "raw.FIT": DATA_DIR / "seestar" / "light.fit",
        "native.fits": DATA_DIR / "seestar" / "stacked.fit",
        "siril.FITS": DATA_DIR / "reference" / "siril_stacked.fit",
    }
    originals_before = {name: _fingerprint(path) for name, path in fixtures.items()}
    copied_sources = {}
    for name, fixture in fixtures.items():
        copied_sources[name] = Path(shutil.copy2(fixture, input_directory / name))
    copies_before = {name: _fingerprint(path) for name, path in copied_sources.items()}

    result = convert_fits_directory(input_directory, output_directory)

    assert result.discovered_count == 3
    assert result.succeeded_count == 3
    assert result.failed_count == 0
    raw = tifffile.imread(output_directory / "raw.tiff")
    native = tifffile.imread(output_directory / "native.tiff")
    siril = tifffile.imread(output_directory / "siril.tiff")
    assert raw.ndim == native.ndim == siril.ndim == 3
    assert raw.shape[-1] == native.shape[-1] == siril.shape[-1] == 3
    assert raw.dtype.kind == native.dtype.kind == "u"
    assert raw.dtype.itemsize == native.dtype.itemsize == 2
    assert siril.dtype.kind == "f"
    assert siril.dtype.itemsize == 4
    assert {path.name for path in input_directory.iterdir()} == set(fixtures)
    assert {name: _fingerprint(path) for name, path in copied_sources.items()} == copies_before
    assert {name: _fingerprint(path) for name, path in fixtures.items()} == originals_before


def test_batch_continues_after_invalid_real_file(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    input_directory.mkdir()
    invalid = input_directory / "a_invalid.fit"
    invalid.write_text("not a FITS file")
    valid = Path(
        shutil.copy2(
            DATA_DIR / "seestar" / "stacked.fit",
            input_directory / "z_valid.fit",
        )
    )
    invalid_before = _fingerprint(invalid)
    valid_before = _fingerprint(valid)

    result = convert_fits_directory(input_directory, output_directory)

    assert result.discovered_count == 2
    assert result.succeeded_count == 1
    assert result.failed_count == 1
    assert result.successes[0].input_path == valid
    assert result.failures[0].input_path == invalid
    assert "FITS" in result.failures[0].reason
    assert (output_directory / "z_valid.tiff").is_file()
    assert not (output_directory / "a_invalid.tiff").exists()
    assert _fingerprint(invalid) == invalid_before
    assert _fingerprint(valid) == valid_before


def test_batch_preserves_existing_destination_and_continues(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    input_directory.mkdir()
    output_directory.mkdir()
    shutil.copy2(DATA_DIR / "seestar" / "light.fit", input_directory / "a_existing.fit")
    shutil.copy2(DATA_DIR / "seestar" / "stacked.fit", input_directory / "b_new.fit")
    existing = output_directory / "a_existing.tiff"
    original_content = b"existing destination content"
    existing.write_bytes(original_content)

    result = convert_fits_directory(input_directory, output_directory)

    assert result.discovered_count == 2
    assert result.succeeded_count == 1
    assert result.failed_count == 1
    assert result.failures[0].input_path.name == "a_existing.fit"
    assert existing.read_bytes() == original_content
    assert (output_directory / "b_new.tiff").is_file()
