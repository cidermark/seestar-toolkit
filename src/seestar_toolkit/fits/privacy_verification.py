"""Read-only ENH-005c.3 FITS privacy verification."""

from __future__ import annotations

import os
import tempfile
from collections import Counter
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .header_report import _SENSITIVE, _replacement, _safe_description
from .privacy_processing import (
    FitsProcessingError,
    _is_processing_safe,
    _open_supported,
    _physical_hdu,
    _read_content,
    _validate_input_checksums,
    inspect_fits_structure,
)


class FitsVerificationError(FitsProcessingError):
    """A FITS input or verification report could not be handled safely."""


class PrivacyVerificationStatus(Enum):
    """Approved ENH-005 verification classifications."""

    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW REQUIRED"


@dataclass(frozen=True)
class FitsVerificationResult:
    """Privacy-safe verification summary."""

    status: PrivacyVerificationStatus
    hdu_count: int
    safe_keyword_counts: dict[str, int]
    violation_count: int
    unknown_count: int
    output_path: Path | None


def _is_compliant_replacement(keyword: str, value: object) -> bool:
    replacement = _replacement(value, keyword)
    return type(value) is type(replacement) and value == replacement


def _description_is_compliant(keyword: str, description: str) -> bool:
    return (
        not description
        or description == "REMOVED"
        or _safe_description(keyword, description) != "WITHHELD"
    )


def _verification_text(result: FitsVerificationResult) -> str:
    lines = [
        "Seestar Toolkit FITS Privacy Verification",
        f"Status: {result.status.value}",
        f"HDUs inspected: {result.hdu_count}",
        f"Confirmed violations: {result.violation_count}",
        f"Unknown metadata occurrences: {result.unknown_count}",
        "Safe keyword occurrences:",
    ]
    lines.extend(
        f"{keyword}: {count}" for keyword, count in sorted(result.safe_keyword_counts.items())
    )
    if not result.safe_keyword_counts:
        lines.append("(none)")
    return "\n".join((*lines, ""))


def _validate_report_paths(source: Path, destination: Path) -> None:
    try:
        source_real = source.resolve(strict=True)
        destination_real = destination.resolve(strict=False)
    except OSError as error:
        raise FitsVerificationError("Unable to validate input and report paths") from error
    if source_real == destination_real:
        raise FitsVerificationError("Input and output must be different files")
    if destination.exists() or destination.is_symlink():
        raise FitsVerificationError("Output already exists; refusing to overwrite it")


def _publish_report(destination: Path, content: str) -> None:
    temporary: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=".pii-verify-", dir=destination.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)
    except FileExistsError as error:
        raise FitsVerificationError("Output already exists; refusing to overwrite it") from error
    except OSError as error:
        raise FitsVerificationError("Unable to safely publish verification report") from error
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)


def verify_fits_privacy(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> FitsVerificationResult:
    """Inspect every FITS header without loading pixels or modifying the source."""
    source = Path(input_path)
    if not source.is_file():
        raise FitsVerificationError("Input FITS is not a readable file")
    destination = Path(output_path) if output_path is not None else None
    if destination is not None:
        _validate_report_paths(source, destination)

    try:
        content = _read_content(source)
        structure = inspect_fits_structure(content)
        hdus = _open_supported(content)
        safe_counts: Counter[str] = Counter()
        violations = unknowns = 0
        try:
            _validate_input_checksums(hdus)
            for hdu in hdus:
                header = _physical_hdu(hdu).header
                for card in header.cards:
                    keyword = card.keyword
                    if keyword in {"COMMENT", "HISTORY", ""}:
                        violations += card.value != "REMOVED"
                    elif keyword in _SENSITIVE:
                        safe_counts[keyword] += 1
                        violations += not _is_compliant_replacement(keyword, card.value)
                        violations += not _description_is_compliant(keyword, card.comment)
                    elif _is_processing_safe(keyword):
                        safe_counts[keyword] += 1
                        violations += not _description_is_compliant(keyword, card.comment)
                    else:
                        unknowns += 1
                        violations += not _description_is_compliant(keyword, card.comment)
        finally:
            hdus.close()
    except FitsProcessingError as error:
        raise FitsVerificationError(str(error)) from error

    if violations:
        status = PrivacyVerificationStatus.FAIL
    elif unknowns:
        status = PrivacyVerificationStatus.REVIEW_REQUIRED
    else:
        status = PrivacyVerificationStatus.PASS
    result = FitsVerificationResult(
        status=status,
        hdu_count=len(structure.hdus),
        safe_keyword_counts=dict(sorted(safe_counts.items())),
        violation_count=violations,
        unknown_count=unknowns,
        output_path=destination,
    )
    if destination is not None:
        _publish_report(destination, _verification_text(result))
    return result
