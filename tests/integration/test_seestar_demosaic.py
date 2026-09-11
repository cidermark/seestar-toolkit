"""Integration tests for demosaicing real Seestar FITS data."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from seestar_toolkit.fits import (
    FitsImageClass,
    FitsImageLayout,
    inspect_fits,
    read_fits_image,
)
from seestar_toolkit.imaging.demosaic import demosaic


def _file_digest(path: Path) -> bytes:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").digest()


def test_real_seestar_raw_fits_demosaics_to_rgb() -> None:
    fits_path = Path(__file__).parents[1] / "data" / "seestar" / "light.fit"
    source_stat = fits_path.stat()
    source_digest = _file_digest(fits_path)

    image = read_fits_image(fits_path)
    inspection = inspect_fits(fits_path)

    assert image.layout is FitsImageLayout.RAW_BAYER
    assert image.ndim == 2
    assert image.data.ndim == 2
    assert inspection.image_class is FitsImageClass.RAW_LIGHT
    assert inspection.bayer_pattern == "GRBG"

    rgb = demosaic(image.data, inspection.bayer_pattern)

    assert isinstance(rgb, np.ndarray)
    assert rgb.shape == (*image.data.shape, 3)
    assert rgb.shape[2] == 3
    assert image.data.dtype == np.uint16
    assert rgb.dtype == np.uint16
    assert rgb.size > 0
    assert np.any(rgb)

    final_stat = fits_path.stat()
    assert final_stat.st_size == source_stat.st_size
    assert final_stat.st_mtime_ns == source_stat.st_mtime_ns
    assert _file_digest(fits_path) == source_digest
