"""FITS file reading functionality."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from astropy.io import fits

from .exceptions import InvalidFitsFileError, MissingImageDataError
from .models import FitsImageData, FitsImageLayout


def read_fits_image(path: Path) -> FitsImageData:
    """Read the first supported image from a FITS file.

    The HDUs are inspected in order. The first HDU containing either a
    two-dimensional image or a three-dimensional channels-first RGB image
    is returned.

    Args:
        path: Path to the FITS file.

    Returns:
        The image data and associated FITS metadata.

    Raises:
        InvalidFitsFileError: If the file cannot be opened as a FITS file.
        MissingImageDataError: If the FITS file contains no supported image data.
"""
    source_path = Path(path)

    try:
        with fits.open(source_path, memmap=False) as hdus:
            for hdu_index, hdu in enumerate(hdus):
                if hdu.data is None:
                    continue

                data = np.asarray(hdu.data)

                if data.ndim == 2:
                    layout = FitsImageLayout.RAW_BAYER
                    height, width = data.shape
                elif data.ndim == 3 and data.shape[0] == 3:
                    layout = FitsImageLayout.RGB
                    _, height, width = data.shape
                else:
                    continue
                
                image_data = data.copy()

                return FitsImageData(
                    layout=layout,
                    shape=image_data.shape,
                    path=source_path,
                    hdu_index=hdu_index,
                    width=width,
                    height=height,
                    ndim=image_data.ndim,
                    dtype=image_data.dtype,
                    bit_depth=image_data.dtype.itemsize * 8,
                    header=hdu.header.copy(),
                    data=image_data,
                )
                
    except (OSError, ValueError) as error:
        raise InvalidFitsFileError(
            f"Unable to read FITS file: {source_path}"
        ) from error

    raise MissingImageDataError(
        f"FITS file contains no supported image data: {source_path}"
    )