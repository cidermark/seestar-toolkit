"""Immutable outcomes for derived archive indexes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class ArchiveIndexOutcome(Enum):
    """Outcome of one target-level index operation."""

    CREATED = auto()
    UPDATED = auto()
    UNCHANGED = auto()
    FAILED = auto()


@dataclass(frozen=True, slots=True)
class ArchiveIndexResult:
    """Outcome and diagnostic for one derived target-level index."""

    index_path: Path
    outcome: ArchiveIndexOutcome
    diagnostic: str | None = None
