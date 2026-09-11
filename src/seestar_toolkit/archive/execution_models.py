"""Immutable policy and result models for archive file execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from .planning_models import ArchivePlan


class SourceAction(Enum):
    """Action applied to an original source FITS file."""

    COPY = auto()
    MOVE = auto()


class CollisionPolicy(Enum):
    """Policy for an already-existing destination."""

    SKIP_IDENTICAL = auto()
    OVERWRITE = auto()
    ERROR = auto()


class ArchiveFileOutcome(Enum):
    """Effective outcome for one planned original source file."""

    COPIED = auto()
    MOVED = auto()
    SKIPPED_IDENTICAL = auto()
    COLLISION = auto()
    FAILED = auto()
    PARTIAL = auto()


class ArchiveCollisionState(Enum):
    """Content relationship to a destination present before execution."""

    NONE = auto()
    IDENTICAL = auto()
    DIFFERENT = auto()


class ArchiveExecutionStatus(Enum):
    """Overall completion state for an archive execution request."""

    COMPLETE = auto()
    PARTIAL = auto()
    FAILED = auto()


@dataclass(frozen=True, slots=True)
class ArchiveFileExecutionResult:
    """Outcome and integrity evidence for one source FITS operation."""

    source_path: Path
    destination_path: Path
    requested_action: SourceAction
    outcome: ArchiveFileOutcome
    collision: ArchiveCollisionState
    source_sha256: str | None = None
    destination_sha256: str | None = None
    bytes_processed: int = 0
    diagnostic: str | None = None


@dataclass(frozen=True, slots=True)
class ArchiveExecutionResult:
    """Complete deterministic result for executing original files in a plan."""

    plan: ArchivePlan
    action: SourceAction
    collision_policy: CollisionPolicy
    files: tuple[ArchiveFileExecutionResult, ...]

    @property
    def copied_count(self) -> int:
        """Return the number of completed copy operations."""
        return sum(result.outcome is ArchiveFileOutcome.COPIED for result in self.files)

    @property
    def moved_count(self) -> int:
        """Return the number of completed move operations."""
        return sum(result.outcome is ArchiveFileOutcome.MOVED for result in self.files)

    @property
    def skipped_count(self) -> int:
        """Return the number of identical destinations safely skipped."""
        return sum(result.outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL for result in self.files)

    @property
    def failed_count(self) -> int:
        """Return the number of collision, failure or partial outcomes."""
        failures = {
            ArchiveFileOutcome.COLLISION,
            ArchiveFileOutcome.FAILED,
            ArchiveFileOutcome.PARTIAL,
        }
        return sum(result.outcome in failures for result in self.files)

    @property
    def status(self) -> ArchiveExecutionStatus:
        """Summarize whether execution completed, failed, or was partial."""
        if self.failed_count == 0:
            return ArchiveExecutionStatus.COMPLETE
        completed = self.copied_count + self.moved_count + self.skipped_count
        if completed or any(result.outcome is ArchiveFileOutcome.PARTIAL for result in self.files):
            return ArchiveExecutionStatus.PARTIAL
        return ArchiveExecutionStatus.FAILED
