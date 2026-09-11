from __future__ import annotations

from seestar_toolkit.fits import (
    FitsError,
    InvalidFitsFileError,
    MissingImageDataError,
)


def test_invalid_fits_file_error_is_fits_error() -> None:
    """InvalidFitsFileError should inherit from FitsError."""
    assert issubclass(InvalidFitsFileError, FitsError)


def test_missing_image_data_error_is_fits_error() -> None:
    """MissingImageDataError should inherit from FitsError."""
    assert issubclass(MissingImageDataError, FitsError)