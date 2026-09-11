"""TIFF output subsystem."""

from __future__ import annotations

from .exceptions import InvalidTiffImageError, TiffError, TiffWriteError
from .writer import write_tiff

__all__ = [
    "InvalidTiffImageError",
    "TiffError",
    "TiffWriteError",
    "write_tiff",
]
