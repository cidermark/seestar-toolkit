"""Tests for FITS inspection data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest

from seestar_toolkit.fits import FitsImageClass, FitsInspection


def test_fits_inspection_can_be_constructed() -> None:
    captured_at = datetime(2026, 7, 16, 2, 11, 37, tzinfo=UTC)

    inspection = FitsInspection(
        path=Path("image.fit"),
        hdu_index=0,
        width=1080,
        height=1920,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        exposure_seconds=10.0,
        gain=80.0,
        bayer_pattern="GRBG",
        object_name="NGC 6992",
        telescope="Seestar S50",
        instrument="Seestar S50",
        filter_name="LP",
        captured_at=captured_at,
        image_type="Light",
        image_class=FitsImageClass.RAW_LIGHT,
        total_exposure_seconds=10.0,
        exposure_ended_at=datetime(2026, 7, 16, 2, 11, 47),
        ra_degrees=314.0,
        dec_degrees=31.5,
        site_latitude=51.428,
        site_longitude=-0.753,
        eq_mode=0,
        ccd_temperature=20.0,
        focus_position=1500,
        aperture=5.0,
        focal_length=250.0,
        creator="ZWO Seestar S50",
        producer="ZWO",
        program="8.46",
        wide_camera=0,
    )

    assert inspection.path == Path("image.fit")
    assert inspection.width == 1080
    assert inspection.height == 1920
    assert inspection.exposure_seconds == 10.0
    assert inspection.gain == 80.0
    assert inspection.bayer_pattern == "GRBG"
    assert inspection.captured_at == captured_at
    assert inspection.image_type == "Light"
    assert inspection.total_exposure_seconds == 10.0
    assert inspection.eq_mode == 0
    assert inspection.focus_position == 1500
    assert inspection.program == "8.46"
    assert inspection.wide_camera == 0
    assert inspection.image_class is FitsImageClass.RAW_LIGHT


def test_fits_inspection_is_immutable() -> None:
    inspection = FitsInspection(
        path=Path("image.fit"),
        hdu_index=0,
        width=100,
        height=200,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        exposure_seconds=None,
        gain=None,
        bayer_pattern=None,
        object_name=None,
        telescope=None,
        instrument=None,
        filter_name=None,
        captured_at=None,
        image_type="Light",
        image_class=FitsImageClass.RAW_LIGHT,
        total_exposure_seconds=10.0,
        exposure_ended_at=datetime(2026, 7, 16, 2, 11, 47),
        ra_degrees=314.0,
        dec_degrees=31.5,
        site_latitude=51.428,
        site_longitude=-0.753,
        eq_mode=0,
        ccd_temperature=20.0,
        focus_position=1500,
        aperture=5.0,
        focal_length=250.0,
        creator="ZWO Seestar S50",
        producer="ZWO",
        program="8.46",
        wide_camera=0,
    )

    with pytest.raises(FrozenInstanceError):
        inspection.width = 300  # type: ignore[misc]

