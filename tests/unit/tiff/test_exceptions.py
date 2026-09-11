"""Tests for TIFF-specific exceptions."""

from __future__ import annotations

from seestar_toolkit.tiff import InvalidTiffImageError, TiffError, TiffWriteError


def test_tiff_exceptions_inherit_from_tiff_error() -> None:
    assert issubclass(InvalidTiffImageError, TiffError)
    assert issubclass(TiffWriteError, TiffError)
