"""Focused ENH-005c.1 internal FITS processing foundation tests."""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.fits.privacy_processing import (
    FitsProcessingError,
    UnknownMetadataAction,
    inspect_fits_structure,
    transform_fits,
    validate_transformed_fits,
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _data_spans(content: bytes) -> list[bytes]:
    with fits.open(BytesIO(content), memmap=False, do_not_scale_image_data=True) as hdus:
        spans = []
        for hdu in hdus:
            info = hdu.fileinfo()
            assert info is not None
            start = info["datLoc"]
            spans.append(content[start : start + info["datSpan"]])
        return spans


def test_single_and_multi_hdu_data_are_byte_identical_and_source_is_unchanged(
    tmp_path: Path,
) -> None:
    source = tmp_path / "multi.fit"
    primary = fits.PrimaryHDU(np.arange(12, dtype=np.uint16).reshape(3, 4))
    primary.header["OBSERVER"] = "Private Person"
    image = fits.ImageHDU(np.array([[1.5, 2.5]], dtype=np.float32), name="IMAGE")
    image.header["EMAIL"] = "private@example.invalid"
    fits.HDUList([primary, image]).writeto(source)
    before = source.read_bytes()

    result = transform_fits(source)

    assert _digest(source) == hashlib.sha256(before).hexdigest()
    assert result.hdu_count == 2
    assert _data_spans(result.content) == _data_spans(before)
    with fits.open(BytesIO(result.content), memmap=False) as hdus:
        assert hdus[0].header["OBSERVER"] == "REMOVED"
        assert hdus[1].header["EMAIL"] == "REMOVED"


def test_type_preserving_replacements_safe_metadata_and_unknown_occurrences(
    tmp_path: Path,
) -> None:
    source = tmp_path / "privacy.fit"
    primary = fits.PrimaryHDU()
    primary.header["SITELAT"] = 51.5
    primary.header["SITEALT"] = 120
    primary.header["AUTHOR"] = True
    primary.header["OBSERVER"] = "Private Person"
    primary.header["TELESCOP"] = ("S50 Pro_device", "Telescope name")
    primary.header.append(("MYSTERY", "one", "private description"))
    primary.header.append(("MYSTERY", 42, "another private description"))
    primary.header.add_comment("private comment")
    primary.header.add_history("private history")
    primary.writeto(source)
    seen: list[tuple[int, int, str, object]] = []

    def decide(occurrence):  # type: ignore[no-untyped-def]
        seen.append(
            (occurrence.hdu_index, occurrence.card_index, occurrence.keyword, occurrence.value)
        )
        return (
            UnknownMetadataAction.PRESERVE
            if occurrence.value == 42
            else (UnknownMetadataAction.ANONYMIZE)
        )

    result = transform_fits(source, unknown_handler=decide)

    with fits.open(BytesIO(result.content), memmap=False) as hdus:
        header = hdus[0].header
        assert header["SITELAT"] == 0.0
        assert header["SITEALT"] == 0
        assert header["AUTHOR"] is False
        assert header["OBSERVER"] == "REMOVED"
        assert header["TELESCOP"] == "S50 Pro_device"
        assert header.comments["TELESCOP"] == "Telescope name"
        assert header["MYSTERY"] == "REMOVED"
        assert header[("MYSTERY", 1)] == 42
        assert header.comments[("MYSTERY", 0)] == "REMOVED"
        assert header.comments[("MYSTERY", 1)] == "REMOVED"
        assert list(header["COMMENT"]) == ["REMOVED"]
        assert list(header["HISTORY"]) == ["REMOVED"]
    assert [item[3] for item in seen] == ["one", 42]


def test_hierarch_and_continue_are_transformed_as_complete_logical_values(
    tmp_path: Path,
) -> None:
    source = tmp_path / "long.fit"
    primary = fits.PrimaryHDU()
    primary.header["HIERARCH PRIVATE CONTACT FIELD"] = "secret"
    primary.header["OBSERVER"] = "private-" * 30
    primary.header["TELESCOP"] = "S50 Pro_" + "device" * 30
    primary.writeto(source)

    result = transform_fits(source)

    assert b"CONTINUE" in source.read_bytes()
    with fits.open(BytesIO(result.content), memmap=False) as hdus:
        assert hdus[0].header["PRIVATE CONTACT FIELD"] == "REMOVED"
        assert hdus[0].header["OBSERVER"] == "REMOVED"
        assert hdus[0].header["TELESCOP"] == "S50 Pro_" + "device" * 30


def test_header_rewrite_keeps_later_hdus_aligned_without_changing_data(tmp_path: Path) -> None:
    source = tmp_path / "growth.fit"
    primary = fits.PrimaryHDU(np.arange(8, dtype=np.uint8))
    for index in range(33):
        primary.header[f"UNKN{index:03d}"] = index
    extension = fits.ImageHDU(np.arange(5, dtype=np.int16))
    fits.HDUList([primary, extension]).writeto(source)
    original = source.read_bytes()

    def grow(occurrence):  # type: ignore[no-untyped-def]
        return UnknownMetadataAction.PRESERVE

    result = transform_fits(source, unknown_handler=grow)
    structure = inspect_fits_structure(result.content)

    assert len(result.content) % 2880 == 0
    assert all(hdu.header_offset % 2880 == 0 for hdu in structure.hdus)
    assert all(hdu.data_offset % 2880 == 0 for hdu in structure.hdus)
    assert _data_spans(result.content) == _data_spans(original)


@pytest.mark.parametrize("kind", ("binary_table", "compressed_image"))
def test_supported_table_and_compressed_image_data_are_copied_raw(
    tmp_path: Path, kind: str
) -> None:
    source = tmp_path / f"{kind}.fit"
    if kind == "binary_table":
        extension = fits.BinTableHDU.from_columns(
            [fits.Column(name="VALUE", format="J", array=np.array([1, 2, 3]))]
        )
    else:
        extension = fits.CompImageHDU(np.arange(16, dtype=np.int16).reshape(4, 4))
    extension.header["OBSERVER"] = "Private Person"
    fits.HDUList([fits.PrimaryHDU(), extension]).writeto(source)
    original = source.read_bytes()

    result = transform_fits(source)

    assert _data_spans(result.content) == _data_spans(original)
    with fits.open(BytesIO(result.content), memmap=False) as hdus:
        assert hdus[1].header["OBSERVER"] == "REMOVED"


def test_valid_checksums_are_valid_after_transform_and_absent_ones_stay_absent(
    tmp_path: Path,
) -> None:
    checked = tmp_path / "checked.fit"
    unchecked = tmp_path / "unchecked.fit"
    hdu = fits.PrimaryHDU(np.arange(8, dtype=np.int16))
    hdu.header["OBSERVER"] = "Private Person"
    hdu.writeto(checked, checksum=True)
    with fits.open(checked, memmap=False) as hdus:
        original_datasum = hdus[0].header["DATASUM"]
    unchecked_hdu = fits.PrimaryHDU(np.arange(8, dtype=np.int16))
    unchecked_hdu.header["OBSERVER"] = "Private Person"
    unchecked_hdu.writeto(unchecked)

    checked_result = transform_fits(checked)
    unchecked_result = transform_fits(unchecked)

    with fits.open(BytesIO(checked_result.content), memmap=False) as hdus:
        assert hdus[0].verify_checksum() == 1
        assert hdus[0].verify_datasum() == 1
        assert hdus[0].header["DATASUM"] == original_datasum
    with fits.open(BytesIO(unchecked_result.content), memmap=False) as hdus:
        assert "CHECKSUM" not in hdus[0].header
        assert "DATASUM" not in hdus[0].header


@pytest.mark.parametrize("keyword", ("CHECKSUM", "DATASUM"))
def test_invalid_existing_integrity_keyword_is_rejected(tmp_path: Path, keyword: str) -> None:
    source = tmp_path / "invalid.fit"
    fits.PrimaryHDU(np.arange(8, dtype=np.int16)).writeto(source, checksum=True)
    content = bytearray(source.read_bytes())
    offset = content.index(keyword.encode("ascii"))
    value_offset = offset + 11
    content[value_offset] = ord("X")
    source.write_bytes(content)

    with pytest.raises(FitsProcessingError, match="invalid existing FITS checksum"):
        transform_fits(source)


def test_malformed_and_unsupported_inputs_are_rejected_safely(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.fit"
    malformed.write_bytes(b"not a FITS file")
    ascii_table = tmp_path / "ascii-table.fit"
    table = fits.TableHDU.from_columns(
        [fits.Column(name="VALUE", format="I4", array=np.array([1, 2]))]
    )
    fits.HDUList([fits.PrimaryHDU(), table]).writeto(ascii_table)

    for source in (malformed, ascii_table):
        with pytest.raises(FitsProcessingError):
            transform_fits(source)


def test_validation_rejects_changed_data_and_trailing_partial_output(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    fits.PrimaryHDU(np.arange(8, dtype=np.uint8)).writeto(source)
    result = transform_fits(source)
    changed = bytearray(result.content)
    structure = inspect_fits_structure(result.content)
    changed[structure.hdus[0].data_offset] ^= 1

    with pytest.raises(FitsProcessingError, match="data block changed"):
        validate_transformed_fits(source, bytes(changed))
    with pytest.raises(FitsProcessingError, match="aligned"):
        inspect_fits_structure(result.content + b"partial")
