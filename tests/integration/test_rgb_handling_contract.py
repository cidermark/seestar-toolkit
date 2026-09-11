"""Contract tests for handling already-RGB FITS image data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from seestar_toolkit.fits import (
    FitsImageClass,
    FitsImageLayout,
    inspect_fits,
    read_fits_image,
)
from seestar_toolkit.imaging.rgb import normalize_rgb_layout


@pytest.mark.parametrize(
    ("filename", "source_shape"),
    [
        pytest.param("siril_stacked.fit", (3, 1920, 1080), id="standard"),
        pytest.param("siril_stacked_mosaic.fit", (3, 17, 11), id="mosaic"),
    ],
)
def test_siril_stacked_fits_normalizes_to_rgb(
    filename: str,
    source_shape: tuple[int, int, int],
) -> None:
    fits_path = Path(__file__).parents[1] / "data" / "reference" / filename

    image = read_fits_image(fits_path)
    inspection = inspect_fits(fits_path)

    assert image.layout is FitsImageLayout.RGB
    assert inspection.image_class is FitsImageClass.RGB_IMAGE
    assert image.ndim == 3
    assert image.shape == source_shape
    assert image.data.shape == (3, image.height, image.width)
    assert image.data.dtype.kind == "f"
    assert image.data.dtype.itemsize == 4

    normalized = normalize_rgb_layout(image.data)

    assert normalized.shape == (image.height, image.width, 3)
    assert normalized.dtype.kind == "f"
    assert normalized.dtype.itemsize == 4
    for row, column in ((0, 0), (image.height // 2, image.width // 2), (-1, -1)):
        assert image.data[0, row, column] == normalized[row, column, 0]
        assert image.data[1, row, column] == normalized[row, column, 1]
        assert image.data[2, row, column] == normalized[row, column, 2]


@pytest.mark.parametrize(
    ("filename", "source_shape"),
    [
        pytest.param("stacked.fit", (3, 3840, 2160), id="standard"),
        pytest.param("stacked_mosaic.fit", (3, 2304, 1296), id="mosaic"),
    ],
)
def test_seestar_stacked_fits_normalizes_to_rgb(
    filename: str,
    source_shape: tuple[int, int, int],
) -> None:
    fits_path = Path(__file__).parents[1] / "data" / "seestar" / filename

    image = read_fits_image(fits_path)
    inspection = inspect_fits(fits_path)

    assert image.layout is FitsImageLayout.RGB
    assert inspection.image_class is FitsImageClass.RGB_IMAGE
    assert image.ndim == 3
    assert image.shape == source_shape
    assert image.data.shape == (3, image.height, image.width)
    assert image.data.dtype == np.uint16
    assert inspection.bayer_pattern == "GRBG"

    normalized = normalize_rgb_layout(image.data)

    assert normalized.shape == (image.height, image.width, 3)
    assert normalized.dtype == np.uint16
    for row, column in ((0, 0), (image.height // 2, image.width // 2), (-1, -1)):
        assert image.data[0, row, column] == normalized[row, column, 0]
        assert image.data[1, row, column] == normalized[row, column, 1]
        assert image.data[2, row, column] == normalized[row, column, 2]
