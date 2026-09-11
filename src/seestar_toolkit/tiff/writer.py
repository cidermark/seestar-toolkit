"""Write linear RGB image data to TIFF files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import tifffile

from .exceptions import InvalidTiffImageError, TiffWriteError


def write_tiff(image: np.ndarray, path: str | Path) -> Path:
    """Write a supported linear RGB array to a new TIFF and return its destination."""
    if image.ndim != 3 or image.shape[2] != 3:
        raise InvalidTiffImageError(
            f"TIFF image must have shape (height, width, 3); got {image.shape}"
        )
    is_uint16 = image.dtype.kind == "u" and image.dtype.itemsize == 2
    is_float32 = image.dtype.kind == "f" and image.dtype.itemsize == 4
    if not (is_uint16 or is_float32):
        raise InvalidTiffImageError(
            f"TIFF image must have dtype uint16 or float32; got {image.dtype}"
        )
    if is_float32 and not np.isfinite(image).all():
        raise InvalidTiffImageError("TIFF float32 image must contain only finite values")

    output_path = Path(path)
    try:
        with output_path.open("xb") as output_file:
            tifffile.imwrite(output_file, image, photometric="rgb")
    except (OSError, ValueError) as exc:
        raise TiffWriteError(f"Failed to write TIFF {output_path}: {exc}") from exc

    return output_path
