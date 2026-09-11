"""Unit tests for the single-file conversion pipeline contract."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from seestar_toolkit import conversion
from seestar_toolkit.fits import FitsImageClass
from seestar_toolkit.tiff import TiffWriteError


def test_convert_fits_to_tiff_routes_raw_light_through_demosaic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = np.zeros((4, 6), dtype=np.uint16)
    rgb = np.zeros((4, 6, 3), dtype=np.uint16)
    inspection = SimpleNamespace(image_class=FitsImageClass.RAW_LIGHT, bayer_pattern="GRBG")
    image = SimpleNamespace(data=raw)
    output_path = Path("output.tiff")
    inspect_fits = Mock(return_value=inspection)
    read_fits_image = Mock(return_value=image)
    demosaic = Mock(return_value=rgb)
    normalize_rgb_layout = Mock()
    write_tiff = Mock(return_value=output_path)
    monkeypatch.setattr(conversion, "inspect_fits", inspect_fits)
    monkeypatch.setattr(conversion, "read_fits_image", read_fits_image)
    monkeypatch.setattr(conversion, "demosaic", demosaic)
    monkeypatch.setattr(conversion, "normalize_rgb_layout", normalize_rgb_layout)
    monkeypatch.setattr(conversion, "write_tiff", write_tiff)

    result = conversion.convert_fits_to_tiff("input.fit", output_path)

    assert result == output_path
    inspect_fits.assert_called_once_with(Path("input.fit"))
    read_fits_image.assert_called_once_with(Path("input.fit"))
    demosaic.assert_called_once_with(raw, "GRBG")
    normalize_rgb_layout.assert_not_called()
    write_tiff.assert_called_once_with(rgb, output_path)


def test_convert_fits_to_tiff_routes_rgb_image_through_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    channels_first = np.zeros((3, 4, 6), dtype=np.float32)
    rgb = np.zeros((4, 6, 3), dtype=np.float32)
    inspection = SimpleNamespace(image_class=FitsImageClass.RGB_IMAGE, bayer_pattern=None)
    image = SimpleNamespace(data=channels_first)
    input_path = Path("input.fit")
    inspect_fits = Mock(return_value=inspection)
    read_fits_image = Mock(return_value=image)
    demosaic = Mock()
    normalize_rgb_layout = Mock(return_value=rgb)
    write_tiff = Mock(return_value=Path("output.tiff"))
    monkeypatch.setattr(conversion, "inspect_fits", inspect_fits)
    monkeypatch.setattr(conversion, "read_fits_image", read_fits_image)
    monkeypatch.setattr(conversion, "demosaic", demosaic)
    monkeypatch.setattr(conversion, "normalize_rgb_layout", normalize_rgb_layout)
    monkeypatch.setattr(conversion, "write_tiff", write_tiff)

    result = conversion.convert_fits_to_tiff(input_path, "output.tiff")

    assert result == Path("output.tiff")
    inspect_fits.assert_called_once_with(input_path)
    read_fits_image.assert_called_once_with(input_path)
    demosaic.assert_not_called()
    normalize_rgb_layout.assert_called_once_with(channels_first)
    write_tiff.assert_called_once_with(rgb, "output.tiff")


def test_convert_fits_to_tiff_rejects_unsupported_classification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inspection = SimpleNamespace(image_class=FitsImageClass.UNKNOWN, bayer_pattern=None)
    monkeypatch.setattr(conversion, "inspect_fits", Mock(return_value=inspection))
    monkeypatch.setattr(
        conversion,
        "read_fits_image",
        Mock(return_value=SimpleNamespace(data=np.zeros((4, 6), dtype=np.uint16))),
    )
    demosaic = Mock()
    normalize_rgb_layout = Mock()
    write_tiff = Mock()
    monkeypatch.setattr(conversion, "demosaic", demosaic)
    monkeypatch.setattr(conversion, "normalize_rgb_layout", normalize_rgb_layout)
    monkeypatch.setattr(conversion, "write_tiff", write_tiff)

    with pytest.raises(ValueError, match="Unsupported FITS image classification: UNKNOWN"):
        conversion.convert_fits_to_tiff("input.fit", "output.tiff")

    demosaic.assert_not_called()
    normalize_rgb_layout.assert_not_called()
    write_tiff.assert_not_called()


def test_convert_fits_to_tiff_propagates_subsystem_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = TiffWriteError("write failed")
    inspection = SimpleNamespace(image_class=FitsImageClass.RGB_IMAGE, bayer_pattern=None)
    channels_first = np.zeros((3, 4, 6), dtype=np.uint16)
    rgb = np.zeros((4, 6, 3), dtype=np.uint16)
    monkeypatch.setattr(conversion, "inspect_fits", Mock(return_value=inspection))
    monkeypatch.setattr(
        conversion, "read_fits_image", Mock(return_value=SimpleNamespace(data=channels_first))
    )
    monkeypatch.setattr(conversion, "normalize_rgb_layout", Mock(return_value=rgb))
    monkeypatch.setattr(conversion, "write_tiff", Mock(side_effect=error))

    with pytest.raises(TiffWriteError) as raised:
        conversion.convert_fits_to_tiff("input.fit", "output.tiff")

    assert raised.value is error
