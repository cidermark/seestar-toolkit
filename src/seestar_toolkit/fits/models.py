"""Data models used by the FITS inspection subsystem."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

import numpy as np
from astropy.io.fits import Header


class FitsImageLayout(Enum):
    """Semantic layout of image data stored in a FITS file."""

    RAW_BAYER = auto()
    RGB = auto()
    
class FitsImageClass(Enum):
    """High-level classification derived from reliable FITS evidence."""

    RAW_LIGHT = auto()
    RGB_IMAGE = auto()
    UNKNOWN = auto()
    
@dataclass(frozen=True, slots=True)
class FitsImageData:
    """Immutable representation of image data read from a FITS file."""

    layout: FitsImageLayout
    shape: tuple[int, ...]
    path: Path
    hdu_index: int
    width: int
    height: int
    ndim: int
    dtype: np.dtype
    bit_depth: int
    header: Header
    data: np.ndarray

@dataclass(frozen=True, slots=True)
class FitsInspection:
    """Normalised metadata extracted from a FITS image."""

    path: Path
    hdu_index: int
    width: int
    height: int
    dtype: np.dtype[np.generic]
    bit_depth: int
    exposure_seconds: float | None
    gain: float | None
    bayer_pattern: str | None
    object_name: str | None
    telescope: str | None
    instrument: str | None
    filter_name: str | None
    captured_at: datetime | None
    image_type: str | None
    image_class: FitsImageClass
    total_exposure_seconds: float | None
    exposure_ended_at: datetime | None
    ra_degrees: float | None
    dec_degrees: float | None
    site_latitude: float | None
    site_longitude: float | None
    eq_mode: int | None
    ccd_temperature: float | None
    focus_position: int | None
    aperture: float | None
    focal_length: float | None
    creator: str | None
    producer: str | None
    program: str | None
    wide_camera: int | None
    