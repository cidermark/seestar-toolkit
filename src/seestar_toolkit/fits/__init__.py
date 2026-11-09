"""FITS inspection subsystem."""

from __future__ import annotations

from .exceptions import (
    FitsError,
    InvalidFitsFileError,
    MissingImageDataError,
)
from .header_report import (
    HeaderReportError,
    HeaderReportResult,
    generate_header_report,
    infer_header_report_path,
    offer_report_menu,
)
from .inspector import inspect_fits
from .models import FitsImageClass, FitsImageData, FitsImageLayout, FitsInspection
from .reader import read_fits_image

__all__ = [
    "FitsError",
    "FitsImageData",
    "FitsInspection",
    "InvalidFitsFileError",
    "MissingImageDataError",
    "HeaderReportError",
    "HeaderReportResult",
    "generate_header_report",
    "infer_header_report_path",
    "offer_report_menu",
    "inspect_fits",
    "read_fits_image",
    "FitsImageLayout",
    "FitsImageClass",
]
