"""Integration tests for converting supported FITS images to TIFF."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import tifffile

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import (
    FitsImageClass,
    InvalidFitsFileError,
    inspect_fits,
    read_fits_image,
)
from seestar_toolkit.imaging.demosaic import demosaic
from seestar_toolkit.imaging.rgb import normalize_rgb_layout
from seestar_toolkit.tiff import TiffWriteError

DATA_DIR = Path(__file__).parents[1] / "data"


@pytest.mark.parametrize(
    ("relative_path", "image_class", "expected_dtype", "bits_per_sample", "sample_format"),
    [
        pytest.param(
            "seestar/light.fit",
            FitsImageClass.RAW_LIGHT,
            np.uint16,
            16,
            "UINT",
            id="raw-standard",
        ),
        pytest.param(
            "seestar/mosaic_1.fit",
            FitsImageClass.RAW_LIGHT,
            np.uint16,
            16,
            "UINT",
            id="raw-mosaic",
        ),
        pytest.param(
            "seestar/stacked.fit",
            FitsImageClass.RGB_IMAGE,
            np.uint16,
            16,
            "UINT",
            id="seestar-standard",
        ),
        pytest.param(
            "seestar/stacked_mosaic.fit",
            FitsImageClass.RGB_IMAGE,
            np.uint16,
            16,
            "UINT",
            id="seestar-mosaic",
        ),
        pytest.param(
            "reference/siril_stacked.fit",
            FitsImageClass.RGB_IMAGE,
            np.float32,
            32,
            "IEEEFP",
            id="siril-standard",
        ),
        pytest.param(
            "reference/siril_stacked_mosaic.fit",
            FitsImageClass.RGB_IMAGE,
            np.float32,
            32,
            "IEEEFP",
            id="siril-mosaic",
        ),
    ],
)
def test_convert_fits_to_tiff_preserves_processing_path_output(
    tmp_path: Path,
    relative_path: str,
    image_class: FitsImageClass,
    expected_dtype: np.dtype,
    bits_per_sample: int,
    sample_format: str,
) -> None:
    input_path = DATA_DIR / relative_path
    output_path = tmp_path / "converted.tiff"

    result = convert_fits_to_tiff(input_path, output_path)

    assert result == output_path
    assert output_path.is_file()
    image = read_fits_image(input_path)
    inspection = inspect_fits(input_path)
    assert inspection.image_class is image_class

    if image_class is FitsImageClass.RAW_LIGHT:
        expected = demosaic(image.data, inspection.bayer_pattern)
    else:
        expected = normalize_rgb_layout(image.data)

    with tifffile.TiffFile(output_path) as tiff:
        page = tiff.pages[0]
        assert page.photometric.name == "RGB"
        assert page.samplesperpixel == 3
        assert page.bitspersample == bits_per_sample
        assert tifffile.SAMPLEFORMAT(page.sampleformat).name == sample_format

    written = tifffile.memmap(output_path, mode="r")
    assert written.shape == (image.height, image.width, 3)
    assert written.dtype.kind == np.dtype(expected_dtype).kind
    assert written.dtype.itemsize == np.dtype(expected_dtype).itemsize
    for row_start in range(0, image.height, 256):
        row_stop = min(row_start + 256, image.height)
        np.testing.assert_array_equal(written[row_start:row_stop], expected[row_start:row_stop])


def test_convert_fits_to_tiff_preserves_existing_destination(tmp_path: Path) -> None:
    input_path = DATA_DIR / "seestar" / "light.fit"
    output_path = tmp_path / "existing.tiff"
    original_content = b"existing file content"
    output_path.write_bytes(original_content)

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        convert_fits_to_tiff(input_path, output_path)

    assert output_path.read_bytes() == original_content


def test_convert_fits_to_tiff_does_not_create_missing_parent(tmp_path: Path) -> None:
    input_path = DATA_DIR / "seestar" / "light.fit"
    output_path = tmp_path / "missing" / "output.tiff"

    with pytest.raises(TiffWriteError, match="Failed to write TIFF"):
        convert_fits_to_tiff(input_path, output_path)

    assert not output_path.parent.exists()
    assert not output_path.exists()


def test_convert_invalid_fits_does_not_create_tiff(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.fit"
    output_path = tmp_path / "output.tiff"
    input_path.write_text("not a FITS file")

    with pytest.raises(InvalidFitsFileError, match="FITS"):
        convert_fits_to_tiff(input_path, output_path)

    assert not output_path.exists()
