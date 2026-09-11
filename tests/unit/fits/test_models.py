from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest
from astropy.io.fits import Header

from seestar_toolkit.fits import (
    FitsImageData,
    FitsImageLayout,
)


def test_fits_image_layout_enum() -> None:
    """Verify supported FITS image layouts."""

    assert FitsImageLayout.RAW_BAYER.name == "RAW_BAYER"
    assert FitsImageLayout.RGB.name == "RGB"
    
def test_fits_image_data_creation() -> None:
    """A FitsImageData instance should store the supplied values."""

    image = FitsImageData(
        layout=FitsImageLayout.RAW_BAYER,
        shape=(1920, 1080),
        ndim=2,
        path=Path("image.fit"),
        hdu_index=0,
        width=100,
        height=200,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        header=Header(),
        data=np.zeros((200, 100), dtype=np.uint16),
    )

    assert image.path == Path("image.fit")
    assert image.width == 100
    assert image.height == 200
    assert image.bit_depth == 16
    assert image.hdu_index == 0
    assert image.layout is FitsImageLayout.RAW_BAYER
    assert image.shape == (1920, 1080)
    assert image.ndim == 2


def test_fits_image_data_is_immutable() -> None:
    """FitsImageData should be immutable."""

    image = FitsImageData(
        layout=FitsImageLayout.RAW_BAYER,
        shape=(1920, 1080),
        ndim=2,
        path=Path("image.fit"),
        hdu_index=0,
        width=100,
        height=200,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        header=Header(),
        data=np.zeros((200, 100), dtype=np.uint16),
    )

    with pytest.raises(FrozenInstanceError):
        image.width = 500