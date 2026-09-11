"""Immutable results for library-level Seestar archive orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from .execution_models import (
    ArchiveExecutionResult,
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
)
from .index_models import ArchiveIndexOutcome, ArchiveIndexResult
from .models import DiscoveryClassification, SeestarDiscoveryInventory
from .planning_models import ArchivePlan
from .reconstruction_models import ObservationReconstructionResult


class ArchiveTiffOutcome(Enum):
    """Outcome of one planned TIFF derivative."""

    CREATED = auto()
    INELIGIBLE = auto()
    COLLISION = auto()
    FAILED = auto()


class SeestarArchiveStatus(Enum):
    """Aggregate state of one complete library archive workflow."""

    COMPLETE = auto()
    PARTIAL = auto()
    FAILED = auto()


@dataclass(frozen=True, slots=True)
class ArchiveTiffResult:
    """Outcome for one TIFF planned from an archived original FITS file."""

    archived_fits_path: Path
    tiff_destination: Path
    original_execution: ArchiveFileExecutionResult
    outcome: ArchiveTiffOutcome
    diagnostic: str | None = None


@dataclass(frozen=True, slots=True)
class PreparedSeestarArchive:
    """Non-mutating discovery, reconstruction and planning result."""

    discovery: SeestarDiscoveryInventory
    reconstruction: ObservationReconstructionResult
    plan: ArchivePlan

    @property
    def has_operational_problems(self) -> bool:
        """Return whether preparation found unsafe supported FITS or planning problems."""
        bad_fits = any(
            item.classification is DiscoveryClassification.UNKNOWN
            and item.source_path.suffix.casefold() in {".fit", ".fits"}
            for item in self.discovery.items
        )
        return bool(self.plan.problems) or bad_fits


@dataclass(frozen=True, slots=True)
class SeestarArchiveResult:
    """All intermediate and final results from one archive workflow."""

    discovery: SeestarDiscoveryInventory
    reconstruction: ObservationReconstructionResult
    plan: ArchivePlan
    execution: ArchiveExecutionResult
    tiffs: tuple[ArchiveTiffResult, ...]
    indexes: tuple[ArchiveIndexResult, ...] = ()

    @property
    def status(self) -> SeestarArchiveStatus:
        """Return deterministic complete, partial, or failed workflow status."""
        archive_success_outcomes = {
            ArchiveFileOutcome.COPIED,
            ArchiveFileOutcome.MOVED,
            ArchiveFileOutcome.SKIPPED_IDENTICAL,
            ArchiveFileOutcome.PARTIAL,
        }
        archive_success = any(
            result.outcome in archive_success_outcomes for result in self.execution.files
        )
        tiff_success = any(result.outcome is ArchiveTiffOutcome.CREATED for result in self.tiffs)
        bad_fits_discovery = any(
            item.classification is DiscoveryClassification.UNKNOWN
            and item.source_path.suffix.casefold() in {".fit", ".fits"}
            for item in self.discovery.items
        )
        has_problem = (
            bool(self.plan.problems)
            or bad_fits_discovery
            or self.execution.failed_count > 0
            or any(result.outcome is not ArchiveTiffOutcome.CREATED for result in self.tiffs)
            or any(result.outcome is ArchiveIndexOutcome.FAILED for result in self.indexes)
        )
        if not has_problem:
            return SeestarArchiveStatus.COMPLETE
        if archive_success or tiff_success:
            return SeestarArchiveStatus.PARTIAL
        return SeestarArchiveStatus.FAILED
