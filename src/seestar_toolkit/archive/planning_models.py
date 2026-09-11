"""Immutable models for archive metadata and destination planning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .reconstruction_models import ReconstructedObservation


@dataclass(frozen=True, slots=True)
class SavedLocation:
    """A named GPS location and its inclusive matching radius in metres."""

    name: str
    latitude: float
    longitude: float
    radius_m: float


@dataclass(frozen=True, slots=True)
class ArchivePlanningConfig:
    """Reusable non-interactive archive-planning configuration."""

    archive_root: Path
    hierarchy_template: str = "{target}/{location}/{session_end_date}"
    saved_locations: tuple[SavedLocation, ...] = ()
    explicit_location: str | None = None


@dataclass(frozen=True, slots=True)
class ArchivePlanningProblem:
    """A visible reason why an observation was not planned authoritatively."""

    observation: ReconstructedObservation
    messages: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PlannedFile:
    """One source FITS and its planned source and TIFF destinations."""

    source_path: Path
    fits_destination: Path
    tiff_destination: Path


@dataclass(frozen=True, slots=True)
class ObservationArchiveMetadata:
    """Logical source metadata retained separately from path components."""

    logical_target: str
    target_component: str
    logical_location: str
    location_component: str
    source_latitude: float | None
    source_longitude: float | None
    session_end_date: str
    telescope: str | None
    diagnostics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PlannedArchiveObservation:
    """One reconstructed observation and all of its planned destinations."""

    reconstructed: ReconstructedObservation
    metadata: ObservationArchiveMetadata
    hierarchy_directory: Path
    observation_name: str
    observation_directory: Path
    lights_directory: Path
    seestar_stacked_directory: Path
    tiff_directory: Path
    lights: tuple[PlannedFile, ...]
    stack: PlannedFile | None


@dataclass(frozen=True, slots=True)
class ArchivePlan:
    """Deterministic read-only archive plan and unresolved observations."""

    config: ArchivePlanningConfig
    observations: tuple[PlannedArchiveObservation, ...]
    problems: tuple[ArchivePlanningProblem, ...]
