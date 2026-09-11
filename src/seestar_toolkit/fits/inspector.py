"""FITS metadata inspection functionality."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from astropy.io.fits import Header

from .models import FitsImageClass, FitsImageLayout, FitsInspection
from .reader import read_fits_image


def inspect_fits(path: Path) -> FitsInspection:
    """Inspect an image-bearing FITS file.

    Args:
        path: Path to the FITS file.

    Returns:
        Normalised metadata extracted from the first two-dimensional image HDU.

    Raises:
        InvalidFitsFileError: If the file cannot be opened as a FITS file.
        MissingImageDataError: If no two-dimensional image data exists.
    """
    image = read_fits_image(path)
    header = image.header

    image_type = _read_text(header, "IMAGETYP")
    image_class = _classify_image(
        layout=image.layout,
        image_type=image_type,
    )

    return FitsInspection(
        path=image.path,
        hdu_index=image.hdu_index,
        width=image.width,
        height=image.height,
        dtype=image.dtype,
        bit_depth=image.bit_depth,
        exposure_seconds=_read_float(header, "EXPTIME"),
        gain=_read_float(header, "GAIN"),
        bayer_pattern=_read_text(header, "BAYERPAT", uppercase=True),
        object_name=_read_text(header, "OBJECT"),
        telescope=_read_text(header, "TELESCOP"),
        instrument=_read_text(header, "INSTRUME"),
        filter_name=_read_text(header, "FILTER"),
        captured_at=_read_datetime(header, "DATE-OBS"),
        image_type=image_type,
        image_class=image_class,
        total_exposure_seconds=_read_float(header, "TOTALEXP"),
        exposure_ended_at=_read_datetime(header, "DATE-EXP"),
        ra_degrees=_read_float(header, "RA"),
        dec_degrees=_read_float(header, "DEC"),
        site_latitude=_read_float(header, "SITELAT"),
        site_longitude=_read_float(header, "SITELONG"),
        eq_mode=_read_int(header, "EQMODE"),
        ccd_temperature=_read_float(header, "CCD-TEMP"),
        focus_position=_read_int(header, "FOCUSPOS"),
        aperture=_read_float(header, "APERTURE"),
        focal_length=_read_float(header, "FOCALLEN"),
        creator=_read_text(header, "CREATOR"),
        producer=_read_text(header, "PRODUCER"),
        program=_read_text(header, "PROGRAM"),
        wide_camera=_read_int(header, "WIDECAM"),
    )

def _classify_image(
    *,
    layout: FitsImageLayout,
    image_type: str | None,
) -> FitsImageClass:
    if layout is FitsImageLayout.RGB:
        return FitsImageClass.RGB_IMAGE

    if (
        layout is FitsImageLayout.RAW_BAYER
        and image_type is not None
        and image_type.casefold() == "light"
    ):
        return FitsImageClass.RAW_LIGHT

    return FitsImageClass.UNKNOWN

def _read_text(
    header: Header,
    key: str,
    *,
    uppercase: bool = False,
) -> str | None:
    """Read and normalise a text value from a FITS header."""
    value = header.get(key)

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if uppercase:
        return text.upper()

    return text


def _read_float(header: Header, key: str) -> float | None:
    """Read a floating-point value from a FITS header."""
    value: Any = header.get(key)

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _read_int(header: Header, key: str) -> int | None:
    value = header.get(key)

    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def _read_datetime(header: Header, key: str) -> datetime | None:
    """Read an ISO-8601 timestamp from a FITS header."""
    value = _read_text(header, key)

    if value is None:
        return None

    normalised_value = value

    if normalised_value.endswith("Z"):
        normalised_value = f"{normalised_value[:-1]}+00:00"

    try:
        return datetime.fromisoformat(normalised_value)
    except ValueError:
        return None