"""Tests for FITS file reading."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.fits import (
    FitsImageLayout,
    InvalidFitsFileError,
    MissingImageDataError,
    read_fits_image,
)


def test_read_fits_image_reads_primary_hdu(tmp_path: Path) -> None:
    image_path = tmp_path / "primary.fit"
    expected_data = np.arange(12, dtype=np.uint16).reshape(3, 4)

    fits.writeto(image_path, expected_data)

    result = read_fits_image(image_path)

    assert result.path == image_path
    assert result.hdu_index == 0
    assert result.width == 4
    assert result.height == 3
    assert result.dtype == np.dtype(np.uint16)
    assert result.bit_depth == 16
    assert result.layout is FitsImageLayout.RAW_BAYER
    assert result.shape == (3, 4)
    assert result.ndim == 2
    np.testing.assert_array_equal(result.data, expected_data)

def test_read_fits_image_reads_rgb_primary_hdu(tmp_path: Path) -> None:
    image_path = tmp_path / "rgb.fit"
    expected_data = np.arange(
        3 * 4 * 5,
        dtype=np.uint16,
    ).reshape(3, 4, 5)

    fits.writeto(image_path, expected_data)

    result = read_fits_image(image_path)

    assert result.path == image_path
    assert result.hdu_index == 0
    assert result.layout is FitsImageLayout.RGB
    assert result.shape == (3, 4, 5)
    assert result.ndim == 3
    assert result.width == 5
    assert result.height == 4
    assert result.dtype == np.dtype(np.uint16)
    assert result.bit_depth == 16
    np.testing.assert_array_equal(result.data, expected_data)

def test_read_fits_image_reads_image_extension(tmp_path: Path) -> None:
    image_path = tmp_path / "extension.fit"
    expected_data = np.arange(20, dtype=np.int16).reshape(4, 5)

    hdus = fits.HDUList(
        [
            fits.PrimaryHDU(),
            fits.ImageHDU(data=expected_data),
        ]
    )
    hdus.writeto(image_path)

    result = read_fits_image(image_path)

    assert result.hdu_index == 1
    assert result.width == 5
    assert result.height == 4
    assert result.dtype.kind == "i"
    assert result.dtype.itemsize == 2
    assert result.bit_depth == 16
    np.testing.assert_array_equal(result.data, expected_data)


def test_read_fits_image_copies_header(tmp_path: Path) -> None:
    image_path = tmp_path / "header.fit"
    header = fits.Header()
    header["OBJECT"] = "NGC 6992"

    fits.writeto(
        image_path,
        np.zeros((2, 3), dtype=np.uint16),
        header=header,
    )

    result = read_fits_image(image_path)

    assert result.header["OBJECT"] == "NGC 6992"


def test_read_fits_image_rejects_invalid_file(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.fit"
    invalid_path.write_text("This is not a FITS file.", encoding="utf-8")

    with pytest.raises(
        InvalidFitsFileError,
        match="Unable to read FITS file",
    ):
        read_fits_image(invalid_path)


def test_read_fits_image_rejects_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.fit"

    with pytest.raises(
        InvalidFitsFileError,
        match="Unable to read FITS file",
    ):
        read_fits_image(missing_path)


def test_read_fits_image_rejects_file_without_image_data(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "empty.fit"
    fits.PrimaryHDU().writeto(image_path)

    with pytest.raises(
        MissingImageDataError,
        match="contains no supported image data",
    ):
        read_fits_image(image_path)


def test_read_fits_image_ignores_non_2d_data(tmp_path: Path) -> None:
    image_path = tmp_path / "one-dimensional.fit"
    fits.writeto(
        image_path,
        np.arange(10, dtype=np.int16),
    )

    with pytest.raises(
        MissingImageDataError,
        match="contains no supported image data",
    ):
        read_fits_image(image_path)
    
def test_read_fits_image_rejects_unsupported_3d_data(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "unsupported-3d.fit"

    fits.writeto(
        image_path,
        np.zeros((4, 10, 20), dtype=np.uint16),
    )

    with pytest.raises(
        MissingImageDataError,
        match="contains no supported image data",
    ):
        read_fits_image(image_path)