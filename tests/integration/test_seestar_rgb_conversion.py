"""Integration tests for the public native Seestar RGB conversion route."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import tifffile

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsImageClass, FitsImageLayout, inspect_fits, read_fits_image
from seestar_toolkit.tiff import TiffWriteError

DATA_DIR = Path(__file__).parents[1] / "data" / "seestar"


def _file_digest(path: Path) -> bytes:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").digest()


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("stacked.fit", id="standard-native-seestar-rgb"),
        pytest.param("stacked_mosaic.fit", id="mosaic-native-seestar-rgb"),
    ],
)
def test_real_seestar_rgb_converts_to_uint16_tiff_without_modifying_source(
    tmp_path: Path, filename: str
) -> None:
    input_path = DATA_DIR / filename
    output_path = tmp_path / f"{input_path.stem}.tiff"
    source_stat = input_path.stat()
    source_digest = _file_digest(input_path)

    image = read_fits_image(input_path)
    inspection = inspect_fits(input_path)

    assert image.layout is FitsImageLayout.RGB
    assert inspection.image_class is FitsImageClass.RGB_IMAGE
    assert image.data.shape == (3, image.height, image.width)
    assert image.data.dtype == np.uint16

    result = convert_fits_to_tiff(input_path, output_path)

    assert result == output_path
    assert output_path.is_file()
    written = tifffile.imread(output_path)
    assert written.shape == (image.height, image.width, 3)
    assert written.dtype == np.uint16

    final_stat = input_path.stat()
    assert input_path.is_file()
    assert final_stat.st_size == source_stat.st_size
    assert final_stat.st_mtime_ns == source_stat.st_mtime_ns
    assert _file_digest(input_path) == source_digest


def test_seestar_rgb_conversion_preserves_existing_destination(tmp_path: Path) -> None:
    input_path = DATA_DIR / "stacked_mosaic.fit"
    output_path = tmp_path / "existing.tiff"
    original_content = b"existing file content"
    output_path.write_bytes(original_content)

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        convert_fits_to_tiff(input_path, output_path)

    assert output_path.read_bytes() == original_content
