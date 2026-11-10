"""Safe publication orchestration for the standalone ``pii-scrub`` command."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from .header_report import _archive_report_owner
from .privacy_processing import (
    FitsProcessingError,
    UnknownMetadataAction,
    UnknownMetadataOccurrence,
    transform_fits,
    validate_transformed_fits,
)

_DISPLAY_LIMIT = 160


class PiiScrubError(FitsProcessingError):
    """A privacy-processed FITS could not be safely published."""


class PiiScrubCancelled(PiiScrubError):
    """The user cancelled occurrence review before publication."""


@dataclass(frozen=True)
class PiiScrubResult:
    """Privacy-safe details of a successfully published scrub."""

    output_path: Path
    hdu_count: int
    replacement_count: int
    anonymized_unknown_count: int
    preserved_unknown_count: int


UnknownReviewer = Callable[[UnknownMetadataOccurrence, object], UnknownMetadataAction]


def safe_terminal_value(value: object, *, limit: int = _DISPLAY_LIMIT) -> str:
    """Render metadata without executable terminal controls or unbounded output."""
    rendered = ascii(value) if isinstance(value, str) else ascii(str(value))
    if len(rendered) <= limit:
        return rendered
    return f"{rendered[: limit - 3]}..."


def infer_pii_scrub_path(input_path: str | Path) -> Path:
    """Infer the approved archive-aware or ordinary scrub destination."""
    from seestar_toolkit.archive import ArchivePathSafetyError

    source = Path(input_path)
    try:
        owner = _archive_report_owner(source)
    except ArchivePathSafetyError as error:
        raise PiiScrubError("Unsafe archive path; refusing scrub destination") from error
    return (owner or source.parent) / "pii-scrubbed" / source.name


def _validate_paths(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise PiiScrubError("Input FITS is not a readable file")
    try:
        if source.resolve(strict=True) == destination.resolve(strict=False):
            raise PiiScrubError("Input and output must be different files")
    except OSError as error:
        raise PiiScrubError("Unable to validate input and output paths") from error
    if destination.exists() or destination.is_symlink():
        raise PiiScrubError("Output already exists; refusing to overwrite it")


def _publish_fits(source: Path, destination: Path, content: bytes) -> None:
    temporary: Path | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=".pii-scrub-", dir=destination.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        validate_transformed_fits(source, temporary.read_bytes())
        os.link(temporary, destination)
    except FileExistsError as error:
        raise PiiScrubError("Output already exists; refusing to overwrite it") from error
    except PiiScrubError:
        raise
    except (OSError, ValueError) as error:
        raise PiiScrubError("Unable to safely publish privacy-processed FITS") from error
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)


def scrub_fits(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    reviewer: UnknownReviewer | None = None,
) -> PiiScrubResult:
    """Transform one FITS and atomically publish it without replacing a file."""
    source = Path(input_path)
    destination = Path(output_path) if output_path is not None else infer_pii_scrub_path(source)
    _validate_paths(source, destination)

    def handle(occurrence: UnknownMetadataOccurrence) -> UnknownMetadataAction:
        if reviewer is None:
            return UnknownMetadataAction.ANONYMIZE
        replacement = _replacement_for_display(occurrence.value, occurrence.keyword)
        return reviewer(occurrence, replacement)

    transformed = transform_fits(source, unknown_handler=handle)
    _publish_fits(source, destination, transformed.content)
    return PiiScrubResult(
        destination,
        transformed.hdu_count,
        transformed.replacement_count,
        transformed.anonymized_unknown_count,
        transformed.preserved_unknown_count,
    )


def _replacement_for_display(value: object, keyword: str) -> object:
    from .header_report import _replacement

    return _replacement(value, keyword)
