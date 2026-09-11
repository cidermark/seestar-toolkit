"""Higher-level image conversion operations."""

from __future__ import annotations

from pathlib import Path

from .fits import FitsImageClass, inspect_fits, read_fits_image
from .imaging.demosaic import demosaic
from .imaging.rgb import normalize_rgb_layout
from .tiff import write_tiff


def convert_fits_to_tiff(input_path: str | Path, output_path: str | Path) -> Path:
    """Orchestrate conversion of one supported FITS image to one RGB TIFF.

    Args:
        input_path: FIT/FITS file to inspect, read, and convert.
        output_path: Explicit destination passed to the TIFF writer.

    Returns:
        The successful TIFF destination returned by the TIFF writer.

    Raises:
        FitsError: If FITS inspection or reading fails.
        ValueError: If classification or image processing rejects the input.
        TiffError: If TIFF validation or writing fails.
    """
    inspection = inspect_fits(Path(input_path))
    image = read_fits_image(Path(input_path))

    if inspection.image_class is FitsImageClass.RAW_LIGHT:
        rgb = demosaic(image.data, inspection.bayer_pattern)
    elif inspection.image_class is FitsImageClass.RGB_IMAGE:
        rgb = normalize_rgb_layout(image.data)
    else:
        raise ValueError(f"Unsupported FITS image classification: {inspection.image_class.name}")

    return write_tiff(rgb, output_path)
