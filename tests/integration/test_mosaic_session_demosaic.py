"""Integration tests for demosaicing raw FITS from Seestar mosaic sessions."""

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
from seestar_toolkit.imaging.demosaic import demosaic


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("mosaic_1.fit", id="ircut-program-5.34"),
        pytest.param("mosaic_4.fit", id="newer-program-7.32"),
        pytest.param("mosaic_6.fit", id="legacy-program-3.31"),
    ],
)
def test_mosaic_session_raw_fits_demosaics_to_rgb(filename: str) -> None:
    fits_path = Path(__file__).parents[1] / "data" / "seestar" / filename

    image = read_fits_image(fits_path)
    inspection = inspect_fits(fits_path)

    assert image.layout is FitsImageLayout.RAW_BAYER
    assert inspection.image_class is FitsImageClass.RAW_LIGHT
    assert image.ndim == 2
    assert image.data.ndim == 2
    assert inspection.bayer_pattern == "GRBG"

    rgb = demosaic(image.data, inspection.bayer_pattern)

    assert isinstance(rgb, np.ndarray)
    assert rgb.shape == (*image.data.shape, 3)
    assert rgb.shape[2] == 3
    assert image.data.dtype == np.uint16
    assert rgb.dtype == np.uint16
    assert rgb.size > 0
    assert np.any(rgb)
