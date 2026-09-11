"""Typed models returned by Seestar archive discovery."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from seestar_toolkit.fits import FitsInspection


class DiscoveryClassification(Enum):
    """Source-file categories understood by Stage 7 discovery."""

    LIGHT_FITS = auto()
    SEESTAR_STACK_FITS = auto()
    SEESTAR_JPEG = auto()
    THUMBNAIL_JPEG = auto()
    UNKNOWN = auto()


class SourceDirectoryContext(Enum):
    """Known shallow relationship between a candidate and the work root."""

    ROOT = auto()
    PRODUCT = auto()
    SUB = auto()


@dataclass(frozen=True, slots=True)
class SeestarDiscoveryItem:
    """One classified source candidate and the evidence used to classify it."""

    source_path: Path
    classification: DiscoveryClassification
    source_directory: Path
    directory_context: SourceDirectoryContext
    directory_target: str | None
    metadata_target: str | None
    fits_inspection: FitsInspection | None
    problem: str | None = None

    @property
    def target_candidate(self) -> str | None:
        """Return authoritative metadata target first, then directory context."""
        return self.metadata_target or self.directory_target


@dataclass(frozen=True, slots=True)
class SeestarDiscoveryInventory:
    """Deterministically ordered result of one discovery request."""

    root: Path
    items: tuple[SeestarDiscoveryItem, ...]

    def items_of_type(
        self, classification: DiscoveryClassification
    ) -> tuple[SeestarDiscoveryItem, ...]:
        """Return inventory items with one discovery classification."""
        return tuple(item for item in self.items if item.classification is classification)
