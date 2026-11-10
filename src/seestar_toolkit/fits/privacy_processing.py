"""Internal ENH-005c.1 FITS privacy-processing foundation."""

from __future__ import annotations

import re
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path

from astropy.io import fits
from astropy.io.fits.verify import VerifyError
from astropy.utils.exceptions import AstropyWarning

from .exceptions import FitsError
from .header_report import _SENSITIVE, _is_safe, _replacement, _safe_description

_FITS_BLOCK_SIZE = 2880
_SUPPORTED_HDU_TYPES = (
    fits.PrimaryHDU,
    fits.ImageHDU,
    fits.BinTableHDU,
    fits.CompImageHDU,
)
_COMPRESSED_STRUCTURAL = {
    "ZIMAGE",
    "ZTENSION",
    "ZBITPIX",
    "ZNAXIS",
    "ZPCOUNT",
    "ZGCOUNT",
    "ZCMPTYPE",
    "ZQUANTIZ",
    "ZDITHER0",
    "ZBLANK",
}
_COMPRESSED_STRUCTURAL_PATTERN = re.compile(r"Z(?:NAXIS|TILE|NAME|VAL|SCALE|ZERO)\d+")


class FitsProcessingError(FitsError):
    """A FITS file could not be transformed without violating ENH-005."""


class UnknownMetadataAction(Enum):
    """Internal occurrence-level handling for an unknown metadata value."""

    ANONYMIZE = "anonymize"
    PRESERVE = "preserve"


@dataclass(frozen=True)
class UnknownMetadataOccurrence:
    """One unknown value occurrence, identified without decision reuse."""

    hdu_index: int
    card_index: int
    keyword: str
    value: object


@dataclass(frozen=True)
class FitsHduStructure:
    """Byte layout and type of one supported HDU."""

    index: int
    hdu_type: str
    header_offset: int
    header_size: int
    data_offset: int
    data_size: int
    has_checksum: bool
    has_datasum: bool


@dataclass(frozen=True)
class FitsStructure:
    """Validated byte layout of a supported FITS stream."""

    size: int
    hdus: tuple[FitsHduStructure, ...]


@dataclass(frozen=True)
class FitsTransformResult:
    """An unpublished transformed FITS stream and safe summary counts."""

    content: bytes
    hdu_count: int
    replacement_count: int
    anonymized_unknown_count: int
    preserved_unknown_count: int


UnknownMetadataHandler = Callable[[UnknownMetadataOccurrence], UnknownMetadataAction]


def _anonymize_unknown(_occurrence: UnknownMetadataOccurrence) -> UnknownMetadataAction:
    return UnknownMetadataAction.ANONYMIZE


def _read_content(source: str | Path | bytes) -> bytes:
    if isinstance(source, bytes):
        return source
    try:
        return Path(source).read_bytes()
    except OSError as error:
        raise FitsProcessingError("Unable to read FITS input") from error


def _open_supported(content: bytes) -> fits.HDUList:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", AstropyWarning)
            hdus = fits.open(
                BytesIO(content),
                mode="readonly",
                memmap=False,
                lazy_load_hdus=True,
                do_not_scale_image_data=True,
            )
            len(hdus)
            hdus.verify("exception")
            return hdus
    except (OSError, ValueError, TypeError, VerifyError, AstropyWarning) as error:
        raise FitsProcessingError("Malformed or unsupported FITS input") from error


def _require_supported_hdu(hdu: fits.hdu.base._BaseHDU) -> None:
    if type(hdu) not in _SUPPORTED_HDU_TYPES:
        raise FitsProcessingError("Unsupported FITS HDU structure")
    if isinstance(hdu, fits.PrimaryHDU) and hdu.header.get("GROUPS", False):
        raise FitsProcessingError("Unsupported FITS random-groups structure")


def _physical_hdu(hdu: fits.hdu.base._BaseHDU) -> fits.hdu.base._BaseHDU:
    if isinstance(hdu, fits.CompImageHDU):
        return hdu._bintable
    return hdu


def _require_unique_integrity_keywords(header: fits.Header) -> None:
    for keyword in ("CHECKSUM", "DATASUM"):
        if keyword in header and header.count(keyword) > 1:
            raise FitsProcessingError("Malformed duplicate FITS integrity keyword")


def inspect_fits_structure(source: str | Path | bytes) -> FitsStructure:
    """Inspect every supported HDU and return its exact padded byte layout."""
    content = _read_content(source)
    if not content or len(content) % _FITS_BLOCK_SIZE:
        raise FitsProcessingError("FITS stream is not aligned to 2880-byte blocks")
    hdus = _open_supported(content)
    try:
        structures: list[FitsHduStructure] = []
        expected_offset = 0
        for index, hdu in enumerate(hdus):
            _require_supported_hdu(hdu)
            physical = _physical_hdu(hdu)
            _require_unique_integrity_keywords(physical.header)
            info = hdu.fileinfo()
            if info is None:
                raise FitsProcessingError("Unable to determine FITS byte layout")
            header_offset = int(info["hdrLoc"])
            data_offset = int(info["datLoc"])
            data_size = int(info["datSpan"])
            if (
                header_offset != expected_offset
                or header_offset % _FITS_BLOCK_SIZE
                or data_offset % _FITS_BLOCK_SIZE
                or data_size % _FITS_BLOCK_SIZE
                or data_offset <= header_offset
            ):
                raise FitsProcessingError("Invalid FITS HDU ordering or alignment")
            structures.append(
                FitsHduStructure(
                    index=index,
                    hdu_type=type(hdu).__name__,
                    header_offset=header_offset,
                    header_size=data_offset - header_offset,
                    data_offset=data_offset,
                    data_size=data_size,
                    has_checksum="CHECKSUM" in physical.header,
                    has_datasum="DATASUM" in physical.header,
                )
            )
            expected_offset = data_offset + data_size
        if not structures or expected_offset != len(content):
            raise FitsProcessingError("Unsupported trailing or missing FITS content")
        return FitsStructure(size=len(content), hdus=tuple(structures))
    finally:
        hdus.close()


def _validate_input_checksums(hdus: fits.HDUList) -> None:
    try:
        for hdu in hdus:
            physical = _physical_hdu(hdu)
            if physical.verify_datasum() == 0 or physical.verify_checksum() == 0:
                raise FitsProcessingError("Input has an invalid existing FITS checksum")
    except (OSError, ValueError, TypeError) as error:
        raise FitsProcessingError("Input has an invalid existing FITS checksum") from error


def _transform_header(
    header: fits.Header,
    hdu_index: int,
    handler: UnknownMetadataHandler,
) -> tuple[fits.Header, int, int, int]:
    transformed = header.copy(strip=False)
    replacements = anonymized = preserved = 0
    original_cards = tuple(header.cards)
    for card_index, card in enumerate(original_cards):
        keyword = card.keyword
        if keyword in {"COMMENT", "HISTORY", ""}:
            transformed[card_index] = ("REMOVED", "")
            anonymized += 1
        elif keyword in _SENSITIVE:
            transformed[card_index] = (
                _replacement(card.value, keyword),
                _anonymized_description(keyword, card.comment),
            )
            replacements += 1
        elif _is_processing_safe(keyword):
            transformed[card_index] = (
                card.value,
                _anonymized_description(keyword, card.comment),
            )
        else:
            occurrence = UnknownMetadataOccurrence(
                hdu_index=hdu_index,
                card_index=card_index,
                keyword=keyword,
                value=card.value,
            )
            action = handler(occurrence)
            if not isinstance(action, UnknownMetadataAction):
                raise FitsProcessingError("Unknown metadata handler returned an invalid action")
            value = (
                card.value
                if action is UnknownMetadataAction.PRESERVE
                else _replacement(card.value, keyword)
            )
            transformed[card_index] = (value, "REMOVED" if card.comment else "")
            if action is UnknownMetadataAction.PRESERVE:
                preserved += 1
            else:
                anonymized += 1
    return transformed, replacements, anonymized, preserved


def _anonymized_description(keyword: str, description: str) -> str:
    safe = _safe_description(keyword, description)
    return "REMOVED" if safe == "WITHHELD" else safe


def _is_processing_safe(keyword: str) -> bool:
    return (
        _is_safe(keyword)
        or keyword in _COMPRESSED_STRUCTURAL
        or _COMPRESSED_STRUCTURAL_PATTERN.fullmatch(keyword) is not None
    )


def _recalculate_existing_checksum(hdu: fits.hdu.base._BaseHDU, header: fits.Header) -> None:
    if "CHECKSUM" not in header:
        return
    datasum = int(header["DATASUM"]) if "DATASUM" in header else 0
    original_header = hdu._header
    try:
        hdu._header = header
        header["CHECKSUM"] = hdu._calculate_checksum(datasum)
    except (ValueError, TypeError, OverflowError) as error:
        raise FitsProcessingError("Unable to recalculate existing FITS checksum") from error
    finally:
        hdu._header = original_header


def transform_fits(
    source: str | Path | bytes,
    *,
    unknown_handler: UnknownMetadataHandler | None = None,
) -> FitsTransformResult:
    """Transform eligible headers and return validated, unpublished FITS bytes."""
    content = _read_content(source)
    structure = inspect_fits_structure(content)
    hdus = _open_supported(content)
    handler = unknown_handler or _anonymize_unknown
    output = bytearray()
    replacements = anonymized = preserved = 0
    try:
        _validate_input_checksums(hdus)
        for layout, hdu in zip(structure.hdus, hdus, strict=True):
            physical = _physical_hdu(hdu)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", AstropyWarning)
                    header, replaced, hidden, kept = _transform_header(
                        physical.header, layout.index, handler
                    )
                    _recalculate_existing_checksum(physical, header)
                    header_bytes = header.tostring(endcard=True, padding=True).encode("ascii")
            except (UnicodeEncodeError, ValueError, VerifyError, AstropyWarning) as error:
                raise FitsProcessingError("Unable to encode transformed FITS header") from error
            if len(header_bytes) % _FITS_BLOCK_SIZE:
                raise FitsProcessingError("Transformed FITS header is not block aligned")
            output.extend(header_bytes)
            output.extend(content[layout.data_offset : layout.data_offset + layout.data_size])
            replacements += replaced
            anonymized += hidden
            preserved += kept
    finally:
        hdus.close()
    result = FitsTransformResult(
        content=bytes(output),
        hdu_count=len(structure.hdus),
        replacement_count=replacements,
        anonymized_unknown_count=anonymized,
        preserved_unknown_count=preserved,
    )
    validate_transformed_fits(content, result.content)
    return result


def validate_transformed_fits(source: str | Path | bytes, transformed: bytes) -> None:
    """Reject transformed bytes unless structure, data, and checksums are safe."""
    source_content = _read_content(source)
    source_structure = inspect_fits_structure(source_content)
    output_structure = inspect_fits_structure(transformed)
    if len(source_structure.hdus) != len(output_structure.hdus):
        raise FitsProcessingError("Transformed FITS HDU order changed")
    for source_hdu, output_hdu in zip(source_structure.hdus, output_structure.hdus, strict=True):
        if source_hdu.hdu_type != output_hdu.hdu_type:
            raise FitsProcessingError("Transformed FITS HDU order changed")
        source_data = source_content[
            source_hdu.data_offset : source_hdu.data_offset + source_hdu.data_size
        ]
        output_data = transformed[
            output_hdu.data_offset : output_hdu.data_offset + output_hdu.data_size
        ]
        if source_data != output_data:
            raise FitsProcessingError("Transformed FITS data block changed")
        if source_hdu.has_checksum != output_hdu.has_checksum:
            raise FitsProcessingError("Transformed FITS checksum presence changed")
        if source_hdu.has_datasum != output_hdu.has_datasum:
            raise FitsProcessingError("Transformed FITS datasum presence changed")
    output_hdus = _open_supported(transformed)
    try:
        _validate_input_checksums(output_hdus)
    finally:
        output_hdus.close()
