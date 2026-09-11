"""Integration tests for the public raw Bayer FITS conversion route."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
import tifffile

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsImageClass, FitsImageLayout, inspect_fits, read_fits_image

DATA_DIR = Path(__file__).parents[1] / "data" / "seestar"


def _file_digest(path: Path) -> bytes:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").digest()


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("light.fit", id="standard-raw-light"),
        pytest.param("mosaic_1.fit", id="mosaic-session-raw-light"),
    ],
)
def test_real_raw_light_converts_to_uint16_rgb_tiff_without_modifying_source(
    tmp_path: Path, filename: str
) -> None:
    input_path = DATA_DIR / filename
    output_path = tmp_path / f"{input_path.stem}.tiff"
    source_stat = input_path.stat()
    source_digest = _file_digest(input_path)

    image = read_fits_image(input_path)
    inspection = inspect_fits(input_path)

    assert image.layout is FitsImageLayout.RAW_BAYER
    assert inspection.image_class is FitsImageClass.RAW_LIGHT
    assert inspection.bayer_pattern == "GRBG"

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
