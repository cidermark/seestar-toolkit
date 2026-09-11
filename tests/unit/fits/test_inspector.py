"""Tests for FITS metadata inspection."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from astropy.io import fits

from seestar_toolkit.fits import FitsImageClass, inspect_fits


def test_inspect_fits_extracts_metadata(tmp_path: Path) -> None:
    image_path = tmp_path / "seestar.fit"
    data = np.zeros((1920, 1080), dtype=np.uint16)

    header = fits.Header()
    header["EXPTIME"] = 10.0
    header["GAIN"] = 80
    header["BAYERPAT"] = "grbg"
    header["OBJECT"] = "NGC 6992"
    header["TELESCOP"] = "Seestar S50"
    header["INSTRUME"] = "Seestar S50"
    header["FILTER"] = "LP"
    header["DATE-OBS"] = "2026-07-16T02:11:37Z"
    header["IMAGETYP"] = "Light"
    header["TOTALEXP"] = 120.0
    header["DATE-EXP"] = "2026-07-16T02:11:47Z"
    header["RA"] = 314.374995
    header["DEC"] = 31.583889
    header["SITELAT"] = 51.428
    header["SITELONG"] = -0.753501
    header["EQMODE"] = 1
    header["CCD-TEMP"] = 17.5
    header["FOCUSPOS"] = 1636
    header["APERTURE"] = 5.0
    header["FOCALLEN"] = 250.0
    header["CREATOR"] = "ZWO Seestar S50"
    header["PRODUCER"] = "ZWO"
    header["PROGRAM"] = "8.46"
    header["WIDECAM"] = 0

    fits.writeto(image_path, data, header=header)

    result = inspect_fits(image_path)

    assert result.path == image_path
    assert result.hdu_index == 0
    assert result.width == 1080
    assert result.height == 1920
    assert result.bit_depth == 16
    assert result.exposure_seconds == 10.0
    assert result.gain == 80.0
    assert result.bayer_pattern == "GRBG"
    assert result.object_name == "NGC 6992"
    assert result.telescope == "Seestar S50"
    assert result.instrument == "Seestar S50"
    assert result.filter_name == "LP"
    assert result.captured_at == datetime(
        2026,
        7,
        16,
        2,
        11,
        37,
        tzinfo=UTC,
    )
    assert result.image_type == "Light"
    assert result.total_exposure_seconds == 120.0
    assert result.exposure_ended_at == datetime(
        2026, 7, 16, 2, 11, 47, tzinfo=UTC
    )
    assert result.ra_degrees == 314.374995
    assert result.dec_degrees == 31.583889
    assert result.site_latitude == 51.428
    assert result.site_longitude == -0.753501
    assert result.eq_mode == 1
    assert result.ccd_temperature == 17.5
    assert result.focus_position == 1636
    assert result.aperture == 5.0
    assert result.focal_length == 250.0
    assert result.creator == "ZWO Seestar S50"
    assert result.producer == "ZWO"
    assert result.program == "8.46"
    assert result.wide_camera == 0
    assert result.image_class is FitsImageClass.RAW_LIGHT

def test_inspect_fits_handles_missing_optional_metadata(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "minimal.fit"

    fits.writeto(
        image_path,
        np.zeros((10, 20), dtype=np.uint16),
    )

    result = inspect_fits(image_path)

    assert result.width == 20
    assert result.height == 10
    assert result.exposure_seconds is None
    assert result.gain is None
    assert result.bayer_pattern is None
    assert result.object_name is None
    assert result.telescope is None
    assert result.instrument is None
    assert result.filter_name is None
    assert result.captured_at is None
    assert result.image_type is None
    assert result.image_class is FitsImageClass.UNKNOWN
    assert result.total_exposure_seconds is None
    assert result.exposure_ended_at is None
    assert result.ra_degrees is None
    assert result.dec_degrees is None
    assert result.site_latitude is None
    assert result.site_longitude is None
    assert result.eq_mode is None
    assert result.ccd_temperature is None
    assert result.focus_position is None
    assert result.aperture is None
    assert result.focal_length is None
    assert result.creator is None
    assert result.producer is None
    assert result.program is None
    assert result.wide_camera is None
    


def test_inspect_fits_handles_invalid_optional_values(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "invalid-metadata.fit"
    header = fits.Header()
    header["EXPTIME"] = "not-a-number"
    header["GAIN"] = "unknown"
    header["DATE-OBS"] = "not-a-date"
    header["BAYERPAT"] = "  grbg  "
    header["OBJECT"] = "   "
    header["TOTALEXP"] = "not-a-number"
    header["DATE-EXP"] = "not-a-date"
    header["RA"] = "unknown"
    header["DEC"] = "unknown"
    header["SITELAT"] = "unknown"
    header["SITELONG"] = "unknown"
    header["EQMODE"] = "unknown"
    header["CCD-TEMP"] = "unknown"
    header["FOCUSPOS"] = "unknown"
    header["APERTURE"] = "unknown"
    header["FOCALLEN"] = "unknown"
    header["WIDECAM"] = "unknown"

    fits.writeto(
        image_path,
        np.zeros((10, 20), dtype=np.uint16),
        header=header,
    )

    result = inspect_fits(image_path)

    assert result.exposure_seconds is None
    assert result.gain is None
    assert result.captured_at is None
    assert result.bayer_pattern == "GRBG"
    assert result.object_name is None
    assert result.total_exposure_seconds is None
    assert result.exposure_ended_at is None
    assert result.ra_degrees is None
    assert result.dec_degrees is None
    assert result.site_latitude is None
    assert result.site_longitude is None
    assert result.eq_mode is None
    assert result.ccd_temperature is None
    assert result.focus_position is None
    assert result.aperture is None
    assert result.focal_length is None
    assert result.wide_camera is None
    
def test_inspect_fits_classifies_rgb_image(tmp_path: Path) -> None:
    image_path = tmp_path / "rgb.fit"
    data = np.zeros((3, 10, 20), dtype=np.uint16)

    fits.writeto(image_path, data)

    result = inspect_fits(image_path)

    assert result.image_class is FitsImageClass.RGB_IMAGE
    
def test_inspect_fits_classifies_unknown_raw_image(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "unknown.fit"
    data = np.zeros((10, 20), dtype=np.uint16)

    fits.writeto(image_path, data)

    result = inspect_fits(image_path)

    assert result.image_class is FitsImageClass.UNKNOWN

