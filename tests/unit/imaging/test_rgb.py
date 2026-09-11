import numpy as np
import pytest

from seestar_toolkit.imaging.rgb import normalize_rgb_layout


@pytest.mark.parametrize("dtype", [np.uint16, np.float32])
def test_normalize_rgb_layout_preserves_channels_values_and_dtype(dtype):
    image = np.empty((3, 2, 4), dtype=dtype)
    image[0] = 100
    image[1] = 200
    image[2] = 300

    result = normalize_rgb_layout(image)

    assert result.shape == (2, 4, 3)
    assert result.dtype == image.dtype
    np.testing.assert_array_equal(result[:, :, 0], image[0])
    np.testing.assert_array_equal(result[:, :, 1], image[1])
    np.testing.assert_array_equal(result[:, :, 2], image[2])


@pytest.mark.parametrize(
    "image",
    [
        np.zeros((4, 5), dtype=np.uint16),
        np.zeros((1, 2, 3, 4), dtype=np.uint16),
    ],
)
def test_normalize_rgb_layout_rejects_non_3_dimensional_input(image):
    with pytest.raises(ValueError, match="RGB image must be 3-dimensional"):
        normalize_rgb_layout(image)


def test_normalize_rgb_layout_rejects_unsupported_first_axis():
    image = np.zeros((4, 5, 6), dtype=np.uint16)

    with pytest.raises(
        ValueError,
        match="RGB image must have exactly 3 channels on the first axis",
    ):
        normalize_rgb_layout(image)


def test_normalize_rgb_layout_rejects_channels_last_input():
    image = np.zeros((4, 5, 3), dtype=np.uint16)

    with pytest.raises(
        ValueError,
        match="RGB image must have exactly 3 channels on the first axis",
    ):
        normalize_rgb_layout(image)
