"""Custom exceptions used by the TIFF output subsystem."""

from __future__ import annotations


class TiffError(Exception):
    """Base exception for all TIFF-related errors."""


class InvalidTiffImageError(TiffError):
    """Raised when image data does not satisfy the TIFF writer contract."""


class TiffWriteError(TiffError):
    """Raised when validated image data cannot be written as TIFF."""
