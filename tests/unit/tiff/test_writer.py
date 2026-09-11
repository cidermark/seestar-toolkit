"""Tests for linear RGB TIFF writing."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import tifffile

from seestar_toolkit.tiff import InvalidTiffImageError, TiffWriteError, write_tiff


def test_write_tiff_preserves_uint16_rgb_pixels(tmp_path: Path) -> None:
    image = np.array(
        [
            [[0, 1, 2], [255, 256, 257], [65533, 65534, 65535]],
            [[1000, 2000, 3000], [4000, 5000, 6000], [7000, 8000, 9000]],
        ],
        dtype=np.uint16,
    )
    output_path = tmp_path / "linear-rgb.tiff"

    result = write_tiff(image, output_path)

    assert result == output_path
    written = tifffile.imread(output_path)
    assert written.shape == image.shape
    assert written.dtype == np.uint16
    np.testing.assert_array_equal(written, image)

    with tifffile.TiffFile(output_path) as tiff:
        page = tiff.pages[0]
        assert page.photometric.name == "RGB"
        assert page.samplesperpixel == 3
        assert page.bitspersample == 16


def test_write_tiff_preserves_float32_rgb_pixels_and_sample_format(tmp_path: Path) -> None:
    image = np.array(
        [
            [[-2.5, -0.25, 0.0], [0.125, 0.5, 1.0]],
            [[1.25, 2.5, 10.0], [100.5, -10.75, 0.75]],
        ],
        dtype=np.float32,
    )
    output_path = tmp_path / "linear-float-rgb.tiff"

    result = write_tiff(image, output_path)

    assert result == output_path
    written = tifffile.imread(output_path)
    assert written.shape == image.shape
    assert written.dtype == np.float32
    np.testing.assert_array_equal(written, image)

    with tifffile.TiffFile(output_path) as tiff:
        page = tiff.pages[0]
        assert page.photometric.name == "RGB"
        assert page.samplesperpixel == 3
        assert page.bitspersample == 32
        assert page.sampleformat.name == "IEEEFP"


def test_write_tiff_preserves_big_endian_float32_pixels(tmp_path: Path) -> None:
    image = np.array(
        [[[-2.5, 0.5, 4.0], [10.0, 0.0, 1.25]]],
        dtype=">f4",
    )
    output_path = tmp_path / "big-endian-float-rgb.tiff"

    write_tiff(image, output_path)

    written = tifffile.imread(output_path)
    assert written.dtype.kind == "f"
    assert written.dtype.itemsize == 4
    np.testing.assert_array_equal(written, image)


@pytest.mark.parametrize(
    "shape",
    [
        (4, 5),
        (3, 4, 5),
        (4, 5, 1),
        (4, 5, 4),
    ],
)
def test_write_tiff_rejects_unsupported_shapes(tmp_path: Path, shape: tuple[int, ...]) -> None:
    image = np.zeros(shape, dtype=np.uint16)
    output_path = tmp_path / "invalid-shape.tiff"

    with pytest.raises(InvalidTiffImageError, match=r"shape \(height, width, 3\)"):
        write_tiff(image, output_path)

    assert not output_path.exists()


@pytest.mark.parametrize("dtype", [np.uint8, np.int16, np.uint32, np.float64])
def test_write_tiff_rejects_unsupported_dtypes(tmp_path: Path, dtype: np.dtype) -> None:
    image = np.zeros((4, 5, 3), dtype=dtype)
    output_path = tmp_path / "invalid-dtype.tiff"

    with pytest.raises(InvalidTiffImageError, match="dtype uint16 or float32"):
        write_tiff(image, output_path)

    assert not output_path.exists()


@pytest.mark.parametrize(
    ("value", "label"),
    [
        (np.nan, "NaN"),
        (np.inf, "positive infinity"),
        (-np.inf, "negative infinity"),
    ],
)
def test_write_tiff_rejects_non_finite_float32_values(
    tmp_path: Path, value: float, label: str
) -> None:
    image = np.zeros((4, 5, 3), dtype=np.float32)
    image[1, 2, 1] = value
    output_path = tmp_path / f"invalid-{label}.tiff"

    with pytest.raises(InvalidTiffImageError, match="finite"):
        write_tiff(image, output_path)

    assert not output_path.exists()


def test_write_tiff_accepts_string_destination(tmp_path: Path) -> None:
    image = np.zeros((4, 5, 3), dtype=np.uint16)
    output_path = tmp_path / "string-destination.tiff"

    result = write_tiff(image, str(output_path))

    assert result == output_path
    assert output_path.is_file()


def test_write_tiff_rejects_existing_destination_without_modifying_it(tmp_path: Path) -> None:
    image = np.zeros((4, 5, 3), dtype=np.uint16)
    output_path = tmp_path / "existing.tiff"
    original_content = b"existing file content"
    output_path.write_bytes(original_content)

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        write_tiff(image, output_path)

    assert output_path.read_bytes() == original_content


def test_write_tiff_does_not_create_missing_parent_directory(tmp_path: Path) -> None:
    image = np.zeros((4, 5, 3), dtype=np.uint16)
    output_path = tmp_path / "missing" / "output.tiff"

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        write_tiff(image, output_path)

    assert not output_path.parent.exists()
    assert not output_path.exists()


def test_write_tiff_wraps_unusable_destination(tmp_path: Path) -> None:
    image = np.zeros((4, 5, 3), dtype=np.uint16)

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        write_tiff(image, tmp_path)
