"""Custom exceptions used by the FITS inspection subsystem."""

from __future__ import annotations


class FitsError(Exception):
    """Base exception for all FITS-related errors."""


class InvalidFitsFileError(FitsError):
    """Raised when a file is not a valid FITS file."""


class MissingImageDataError(FitsError):
    """Raised when a FITS file contains no image data."""