import numpy as np
import pytest

from seestar_toolkit.imaging.demosaic import demosaic

PATTERN_TILES = {
    "RGGB": (("R", "G"), ("G", "B")),
    "GRBG": (("G", "R"), ("B", "G")),
    "GBRG": (("G", "B"), ("R", "G")),
    "BGGR": (("B", "G"), ("G", "R")),
}
CHANNEL_VALUES = {"R": 1000, "G": 2000, "B": 4000}


def make_bayer_image(bayer_pattern):
    tile = PATTERN_TILES[bayer_pattern]
    image = np.empty((8, 8), dtype=np.uint16)

    for row in range(image.shape[0]):
        for column in range(image.shape[1]):
            image[row, column] = CHANNEL_VALUES[tile[row % 2][column % 2]]

    return image


@pytest.mark.parametrize("bayer_pattern", ["RGGB", "GRBG", "GBRG", "BGGR"])
def test_demosaic_accepts_supported_bayer_patterns(bayer_pattern):
    image = np.zeros((4, 6), dtype=np.uint16)

    result = demosaic(image, bayer_pattern)

    assert isinstance(result, np.ndarray)
    assert result.shape == (4, 6, 3)


def test_demosaic_rejects_unsupported_bayer_pattern():
    image = np.zeros((4, 6), dtype=np.uint16)

    with pytest.raises(ValueError, match="Unsupported Bayer pattern: 'RGB'"):
        demosaic(image, "RGB")


@pytest.mark.parametrize(
    "image",
    [
        np.zeros(4, dtype=np.uint16),
        np.zeros((2, 4, 6), dtype=np.uint16),
    ],
)
def test_demosaic_rejects_non_2_dimensional_image(image):
    with pytest.raises(ValueError, match="Bayer image must be 2-dimensional"):
        demosaic(image, "GRBG")


def test_demosaic_preserves_uint16_dtype():
    image = np.zeros((4, 6), dtype=np.uint16)

    result = demosaic(image, "GRBG")

    assert result.dtype == np.uint16


@pytest.mark.parametrize("bayer_pattern", ["RGGB", "GRBG", "GBRG", "BGGR"])
def test_demosaic_interpolates_each_pattern_to_rgb(bayer_pattern):
    image = make_bayer_image(bayer_pattern)

    result = demosaic(image, bayer_pattern)

    expected_rgb = np.array([1000, 2000, 4000], dtype=np.uint16)
    assert np.all(result[2:-2, 2:-2] == expected_rgb)
    assert not np.array_equal(result[3, 3], np.repeat(image[3, 3], 3))
