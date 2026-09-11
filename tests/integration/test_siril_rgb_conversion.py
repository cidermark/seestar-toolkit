"""Integration tests for the public Siril RGB conversion route."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import tifffile

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsImageClass, FitsImageLayout, inspect_fits, read_fits_image
from seestar_toolkit.imaging.rgb import normalize_rgb_layout
from seestar_toolkit.tiff import TiffWriteError

DATA_DIR = Path(__file__).parents[1] / "data" / "reference"


def _file_digest(path: Path) -> bytes:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").digest()


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("siril_stacked.fit", id="standard-siril-rgb"),
        pytest.param("siril_stacked_mosaic.fit", id="mosaic-siril-rgb"),
    ],
)
def test_siril_rgb_converts_to_float32_tiff_without_modifying_source(
    tmp_path: Path, filename: str
) -> None:
    input_path = DATA_DIR / filename
    output_path = tmp_path / f"{input_path.stem}.tiff"
    source_stat = input_path.stat()
    source_digest = _file_digest(input_path)

    image = read_fits_image(input_path)
    inspection = inspect_fits(input_path)
    expected = normalize_rgb_layout(image.data)

    assert image.layout is FitsImageLayout.RGB
    assert inspection.image_class is FitsImageClass.RGB_IMAGE
    assert image.data.shape == (3, image.height, image.width)
    assert image.data.dtype.kind == "f"
    assert image.data.dtype.itemsize == 4

    result = convert_fits_to_tiff(input_path, output_path)

    assert result == output_path
    assert output_path.is_file()
    written = tifffile.imread(output_path)
    assert written.shape == (image.height, image.width, 3)
    assert written.dtype.kind == "f"
    assert written.dtype.itemsize == 4
    assert np.min(written) == np.min(expected)
    assert np.max(written) == np.max(expected)
    for row, column in ((0, 0), (image.height // 2, image.width // 2), (-1, -1)):
        np.testing.assert_array_equal(written[row, column], expected[row, column])

    final_stat = input_path.stat()
    assert input_path.is_file()
    assert final_stat.st_size == source_stat.st_size
    assert final_stat.st_mtime_ns == source_stat.st_mtime_ns
    assert _file_digest(input_path) == source_digest


def test_siril_rgb_conversion_preserves_existing_destination(tmp_path: Path) -> None:
    input_path = DATA_DIR / "siril_stacked.fit"
    output_path = tmp_path / "existing.tiff"
    original_content = b"existing file content"
    output_path.write_bytes(original_content)

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        convert_fits_to_tiff(input_path, output_path)

    assert output_path.read_bytes() == original_content


def test_synthetic_siril_mosaic_preserves_linear_pixels_and_orientation(tmp_path: Path) -> None:
    input_path = DATA_DIR / "siril_stacked_mosaic.fit"
    image = read_fits_image(input_path)
    assert image.header["PROGRAM"] == "Siril synthetic fixture"
    assert image.header["IMAGETYP"] == "Light"
    assert image.header["BITPIX"] == -32
    assert "BAYERPAT" not in image.header
    assert "ROWORDER" not in image.header
    assert image.header["CTYPE1"] == "RA---TAN"
    assert image.header["CTYPE2"] == "DEC--TAN"
    assert image.header["PC1_2"] == -0.6
    assert image.header["PC2_1"] == 0.6

    # Independent pixel oracle: catches flips, transposes, channel swaps,
    # stretching and normalization, even if the shared layout helper regresses.
    expected = np.empty((17, 11, 3), dtype=np.float32)
    for row in range(17):
        for column in range(11):
            expected[row, column] = [
                (channel * 256 + row * 12 + column) / 1024 for channel in range(3)
            ]
    np.testing.assert_array_equal(image.data, expected.transpose(2, 0, 1))
    output_path = convert_fits_to_tiff(input_path, tmp_path / "synthetic.tiff")
    np.testing.assert_array_equal(tifffile.imread(output_path), expected)
