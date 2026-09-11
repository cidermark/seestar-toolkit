"""Flat-directory batch conversion orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .conversion import convert_fits_to_tiff
from .fits import FitsError
from .tiff import TiffError


@dataclass(frozen=True, slots=True)
class BatchSuccess:
    """One successful source-to-destination conversion."""

    input_path: Path
    output_path: Path


@dataclass(frozen=True, slots=True)
class BatchFailure:
    """One expected per-file conversion failure."""

    input_path: Path
    reason: str


@dataclass(frozen=True, slots=True)
class BatchConversionResult:
    """Structured outcome of one flat-directory batch conversion."""

    discovered_count: int
    successes: tuple[BatchSuccess, ...]
    failures: tuple[BatchFailure, ...]

    @property
    def succeeded_count(self) -> int:
        """Return the number of successful conversions."""
        return len(self.successes)

    @property
    def failed_count(self) -> int:
        """Return the number of failed conversions."""
        return len(self.failures)


def convert_fits_directory(
    input_directory: str | Path,
    output_directory: str | Path,
) -> BatchConversionResult:
    """Convert supported FIT/FITS files from one flat directory.

    The explicit output directory is created when absent, but its parent must
    already exist. Expected conversion failures are recorded per file so later
    files can still be processed.
    """
    source_directory = Path(input_directory)
    destination_directory = Path(output_directory)

    if not source_directory.exists():
        raise ValueError(f"Input directory does not exist: {source_directory}")
    if not source_directory.is_dir():
        raise ValueError(f"Input path is not a directory: {source_directory}")
    if destination_directory.exists() and not destination_directory.is_dir():
        raise ValueError(f"Output path is not a directory: {destination_directory}")
    if not destination_directory.exists():
        try:
            destination_directory.mkdir()
        except OSError as error:
            raise ValueError(
                f"Unable to create output directory: {destination_directory}"
            ) from error

    inputs = sorted(
        (
            path
            for path in source_directory.iterdir()
            if path.is_file() and path.suffix.lower() in {".fit", ".fits"}
        ),
        key=lambda path: path.name,
    )
    successes: list[BatchSuccess] = []
    failures: list[BatchFailure] = []

    for input_path in inputs:
        output_path = destination_directory / f"{input_path.stem}.tiff"
        try:
            destination = convert_fits_to_tiff(input_path, output_path)
        except (FitsError, TiffError, ValueError) as error:
            failures.append(BatchFailure(input_path=input_path, reason=str(error)))
        else:
            successes.append(BatchSuccess(input_path=input_path, output_path=destination))

    return BatchConversionResult(
        discovered_count=len(inputs),
        successes=tuple(successes),
        failures=tuple(failures),
    )
