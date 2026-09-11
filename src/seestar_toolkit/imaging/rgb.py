"""RGB image layout handling."""

import numpy as np


def normalize_rgb_layout(image: np.ndarray) -> np.ndarray:
    """Move a channels-first RGB array to channels-last layout."""
    if image.ndim != 3:
        raise ValueError("RGB image must be 3-dimensional")

    if image.shape[0] != 3:
        raise ValueError("RGB image must have exactly 3 channels on the first axis")

    return np.moveaxis(image, 0, -1)
