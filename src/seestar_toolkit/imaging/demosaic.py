"""Bayer demosaicing."""

import cv2
import numpy as np

BAYER_TO_RGB_CONVERSIONS = {
    "RGGB": cv2.COLOR_BayerBG2RGB,
    "GRBG": cv2.COLOR_BayerGB2RGB,
    "GBRG": cv2.COLOR_BayerGR2RGB,
    "BGGR": cv2.COLOR_BayerRG2RGB,
}


def demosaic(image: np.ndarray, bayer_pattern: str) -> np.ndarray:
    """Convert a 2-dimensional Bayer image to an RGB image."""
    if bayer_pattern not in BAYER_TO_RGB_CONVERSIONS:
        raise ValueError(f"Unsupported Bayer pattern: {bayer_pattern!r}")

    if image.ndim != 2:
        raise ValueError("Bayer image must be 2-dimensional")

    return cv2.cvtColor(image, BAYER_TO_RGB_CONVERSIONS[bayer_pattern])
