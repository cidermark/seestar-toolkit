"""Immutable models for logical Seestar observation reconstruction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from .models import SeestarDiscoveryItem


class ObservationStatus(Enum):
    """Confidence and source completeness of a reconstructed observation."""

    COMPLETE = auto()
    LIGHTS_ONLY = auto()
    STACK_ONLY = auto()
    AMBIGUOUS = auto()
    UNRESOLVED = auto()


@dataclass(frozen=True, slots=True)
class TimestampEvidence:
    """Capture-time evidence selected for one discovered FITS candidate."""

    selected_at: datetime | None
    fits_at: datetime | None
    filename_at: datetime | None
    problem: str | None = None


@dataclass(frozen=True, slots=True)
class ObservationCompatibility:
    """Stable metadata evidence shared by an observation's source frames."""

    target: str | None
    exposure_seconds: float | None
    filter_name: str | None
    eq_mode: int | None


@dataclass(frozen=True, slots=True)
class ReconstructedObservation:
    """One logical observation, without archive numbering or path decisions."""

    lights: tuple[SeestarDiscoveryItem, ...]
    stack: SeestarDiscoveryItem | None
    first_light_at: datetime | None
    last_light_at: datetime | None
    stack_at: datetime | None
    status: ObservationStatus
    compatibility: ObservationCompatibility | None
    reported_stack_count: int | None
    problems: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ObservationReconstructionResult:
    """Deterministic logical observations plus non-frame discovery items."""

    observations: tuple[ReconstructedObservation, ...]
    excluded_items: tuple[SeestarDiscoveryItem, ...]
