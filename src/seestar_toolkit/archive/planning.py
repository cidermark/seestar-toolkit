"""Read-only archive metadata and destination planning."""

from __future__ import annotations

import math
import re
import string
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from .exceptions import ArchivePlanningCollisionError, ArchivePlanningConfigurationError
from .models import SeestarDiscoveryItem
from .planning_models import (
    ArchivePlan,
    ArchivePlanningConfig,
    ArchivePlanningProblem,
    ObservationArchiveMetadata,
    PlannedArchiveObservation,
    PlannedFile,
    SavedLocation,
)
from .reconstruction_models import (
    ObservationReconstructionResult,
    ObservationStatus,
    ReconstructedObservation,
)
from .target_comparison import directory_target_for_comparison

_SUPPORTED_TOKENS = frozenset({"target", "location", "session_end_date"})
_UNSAFE_COMPONENT_CHARACTERS = re.compile(r'[\x00-\x1f<>:"/\\|?*]+')
_WHITESPACE = re.compile(r"\s+")
_EARTH_RADIUS_M = 6_371_008.8


def normalize_archive_component(value: str) -> str:
    """Return one deterministic, readable and traversal-safe path component."""
    normalized = _WHITESPACE.sub(" ", value.strip())
    normalized = _UNSAFE_COMPONENT_CHARACTERS.sub("-", normalized).strip()
    if not normalized or normalized in {".", ".."}:
        return "unknown"
    return normalized


def session_end_date(capture_datetime: datetime) -> str:
    """Return the archive observing-night token using the fixed +12-hour rule."""
    return (capture_datetime + timedelta(hours=12)).date().strftime("%Y%m%d")


def plan_seestar_archive(
    reconstruction: ObservationReconstructionResult,
    *,
    archive_root: str | Path,
    hierarchy_template: str = "{target}/{location}/{session_end_date}",
    explicit_location: str | None = None,
    saved_locations: tuple[SavedLocation, ...] = (),
) -> ArchivePlan:
    """Plan archive destinations from an existing reconstruction without I/O."""
    config = ArchivePlanningConfig(
        archive_root=Path(archive_root),
        hierarchy_template=hierarchy_template,
        saved_locations=tuple(saved_locations),
        explicit_location=explicit_location,
    )
    _validate_config(config)

    candidates: list[tuple[ReconstructedObservation, ObservationArchiveMetadata, Path]] = []
    problems: list[ArchivePlanningProblem] = []
    for observation in reconstruction.observations:
        candidate = _observation_candidate(observation, config)
        if isinstance(candidate, ArchivePlanningProblem):
            problems.append(candidate)
        else:
            candidates.append(candidate)

    grouped: dict[
        tuple[str, str, str],
        list[tuple[ReconstructedObservation, ObservationArchiveMetadata, Path]],
    ] = defaultdict(list)
    for candidate in candidates:
        metadata = candidate[1]
        grouped[
            (metadata.target_component, metadata.location_component, metadata.session_end_date)
        ].append(candidate)

    planned: list[PlannedArchiveObservation] = []
    destinations: dict[Path, Path] = {}
    for group_key in sorted(grouped):
        group = sorted(grouped[group_key], key=lambda item: _observation_sort_key(item[0]))
        width = max(2, len(str(len(group))))
        for index, (observation, metadata, hierarchy_directory) in enumerate(group, start=1):
            observation_name = f"observation_{index:0{width}d}"
            planned_observation = _planned_observation(
                observation, metadata, hierarchy_directory, observation_name
            )
            _record_destinations(planned_observation, destinations)
            planned.append(planned_observation)

    planned.sort(key=lambda item: item.observation_directory.as_posix())
    return ArchivePlan(config=config, observations=tuple(planned), problems=tuple(problems))


def _validate_config(config: ArchivePlanningConfig) -> None:
    if not config.archive_root.is_absolute():
        raise ArchivePlanningConfigurationError("archive_root must be an absolute path")
    if ".." in config.archive_root.parts:
        raise ArchivePlanningConfigurationError("archive_root must not contain traversal")
    _template_tokens(config.hierarchy_template)
    for location in config.saved_locations:
        if not math.isfinite(location.latitude) or not -90 <= location.latitude <= 90:
            raise ArchivePlanningConfigurationError(
                f"Saved location {location.name!r} has invalid latitude"
            )
        if not math.isfinite(location.longitude) or not -180 <= location.longitude <= 180:
            raise ArchivePlanningConfigurationError(
                f"Saved location {location.name!r} has invalid longitude"
            )
        if not math.isfinite(location.radius_m) or location.radius_m < 0:
            raise ArchivePlanningConfigurationError(
                f"Saved location {location.name!r} has invalid matching radius"
            )


def _template_tokens(template: str) -> tuple[str, ...]:
    if not template or template.startswith(("/", "\\")) or "\\" in template:
        raise ArchivePlanningConfigurationError("Hierarchy template must be a relative path")
    components = template.split("/")
    if any(component in {"", ".", ".."} for component in components):
        raise ArchivePlanningConfigurationError("Hierarchy template contains an unsafe component")
    tokens: list[str] = []
    for component in components:
        parsed = tuple(string.Formatter().parse(component))
        if len(parsed) != 1 or parsed[0][0] or parsed[0][1] is None or parsed[0][2:4] != ("", None):
            raise ArchivePlanningConfigurationError(
                "Each hierarchy component must be one supported token"
            )
        token = parsed[0][1]
        if token not in _SUPPORTED_TOKENS:
            raise ArchivePlanningConfigurationError(f"Unknown hierarchy token: {token}")
        tokens.append(token)
    if set(tokens) != _SUPPORTED_TOKENS or len(tokens) != len(_SUPPORTED_TOKENS):
        raise ArchivePlanningConfigurationError(
            "Hierarchy template must contain each supported token exactly once"
        )
    return tuple(tokens)


def _observation_candidate(
    observation: ReconstructedObservation, config: ArchivePlanningConfig
) -> tuple[ReconstructedObservation, ObservationArchiveMetadata, Path] | ArchivePlanningProblem:
    diagnostics = list(observation.problems)
    if observation.status in {ObservationStatus.AMBIGUOUS, ObservationStatus.UNRESOLVED}:
        return ArchivePlanningProblem(
            observation=observation,
            messages=(*diagnostics, "Observation status is not safe for authoritative placement"),
        )
    capture_at = observation.first_light_at or observation.stack_at
    if capture_at is None:
        return ArchivePlanningProblem(
            observation=observation,
            messages=(*diagnostics, "No safe observation timestamp for session grouping"),
        )

    logical_target, target_diagnostics = _resolve_target(observation)
    diagnostics.extend(target_diagnostics)
    latitude, longitude, gps_diagnostics = _source_gps(observation)
    diagnostics.extend(gps_diagnostics)
    logical_location = _resolve_location(
        explicit=config.explicit_location,
        latitude=latitude,
        longitude=longitude,
        saved_locations=config.saved_locations,
    )
    date_token = session_end_date(capture_at)
    metadata = ObservationArchiveMetadata(
        logical_target=logical_target,
        target_component=normalize_archive_component(logical_target),
        logical_location=logical_location,
        location_component=normalize_archive_component(logical_location),
        source_latitude=latitude,
        source_longitude=longitude,
        session_end_date=date_token,
        telescope=_telescope(observation),
        diagnostics=tuple(diagnostics),
    )
    values = {
        "target": metadata.target_component,
        "location": metadata.location_component,
        "session_end_date": date_token,
    }
    hierarchy = config.archive_root.joinpath(
        *(values[token] for token in _template_tokens(config.hierarchy_template))
    )
    _require_beneath_root(config.archive_root, hierarchy)
    return observation, metadata, hierarchy


def _resolve_target(observation: ReconstructedObservation) -> tuple[str, tuple[str, ...]]:
    items = _observation_items(observation)
    metadata_values = _unique_values(item.metadata_target for item in items)
    directory_values = _unique_values(item.directory_target for item in items)
    diagnostics: list[str] = []
    if len(metadata_values) > 1:
        diagnostics.append(f"Conflicting FITS target evidence: {metadata_values!r}")
    if (
        metadata_values
        and directory_values
        and any(
            directory_target_for_comparison(directory).casefold() != metadata_values[0].casefold()
            for directory in directory_values
        )
    ):
        diagnostics.append(
            f"FITS target {metadata_values[0]!r} conflicts with "
            f"directory evidence {directory_values!r}"
        )
    if metadata_values:
        return metadata_values[0], tuple(diagnostics)
    compatibility_target = observation.compatibility.target if observation.compatibility else None
    if compatibility_target and compatibility_target.strip():
        return compatibility_target, tuple(diagnostics)
    if directory_values:
        return directory_values[0], tuple(diagnostics)
    diagnostics.append("No target evidence; using explicit unknown fallback")
    return "unknown", tuple(diagnostics)


def _source_gps(
    observation: ReconstructedObservation,
) -> tuple[float | None, float | None, tuple[str, ...]]:
    coordinates = []
    for item in _observation_items(observation):
        inspection = item.fits_inspection
        if (
            inspection is not None
            and inspection.site_latitude is not None
            and inspection.site_longitude is not None
        ):
            coordinate = (inspection.site_latitude, inspection.site_longitude)
            if coordinate not in coordinates:
                coordinates.append(coordinate)
    diagnostics = ()
    if len(coordinates) > 1:
        diagnostics = (f"Conflicting source GPS evidence: {coordinates!r}",)
    return (*coordinates[0], diagnostics) if coordinates else (None, None, diagnostics)


def _resolve_location(
    *,
    explicit: str | None,
    latitude: float | None,
    longitude: float | None,
    saved_locations: tuple[SavedLocation, ...],
) -> str:
    if explicit is not None and explicit.strip():
        return explicit
    if latitude is None or longitude is None:
        return "unknown"
    matches = []
    for location in saved_locations:
        distance = _haversine_m(latitude, longitude, location.latitude, location.longitude)
        if distance <= location.radius_m + 1e-9:
            matches.append((distance, location.name.casefold(), location.name))
    return min(matches)[2] if matches else "unknown"


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    latitude_1, latitude_2 = math.radians(lat1), math.radians(lat2)
    latitude_delta = math.radians(lat2 - lat1)
    longitude_delta = math.radians(lon2 - lon1)
    a = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(latitude_1) * math.cos(latitude_2) * math.sin(longitude_delta / 2) ** 2
    )
    return _EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _telescope(observation: ReconstructedObservation) -> str | None:
    for item in _observation_items(observation):
        if item.fits_inspection is not None and item.fits_inspection.telescope is not None:
            return item.fits_inspection.telescope
    return None


def _observation_items(observation: ReconstructedObservation) -> tuple[SeestarDiscoveryItem, ...]:
    return (*observation.lights, *((observation.stack,) if observation.stack else ()))


def _unique_values(values) -> tuple[str, ...]:
    unique: dict[str, str] = {}
    for value in values:
        if value is not None and value.strip():
            unique.setdefault(value.strip().casefold(), value)
    return tuple(unique[key] for key in sorted(unique))


def _observation_sort_key(observation: ReconstructedObservation) -> tuple[datetime, str]:
    capture_at = observation.first_light_at or observation.stack_at or datetime.max
    paths = tuple(item.source_path.as_posix() for item in _observation_items(observation))
    return capture_at, min(paths, default="")


def _planned_observation(
    observation: ReconstructedObservation,
    metadata: ObservationArchiveMetadata,
    hierarchy_directory: Path,
    observation_name: str,
) -> PlannedArchiveObservation:
    observation_directory = hierarchy_directory / observation_name
    lights_directory = observation_directory / "lights"
    stack_directory = observation_directory / "seestar_stacked"
    tiff_directory = observation_directory / "tiff"
    lights = tuple(
        PlannedFile(
            source_path=item.source_path,
            fits_destination=lights_directory / item.source_path.name,
            tiff_destination=None,
        )
        for item in observation.lights
    )
    stack = None
    if observation.stack is not None:
        stack = PlannedFile(
            source_path=observation.stack.source_path,
            fits_destination=stack_directory / observation.stack.source_path.name,
            tiff_destination=stack_directory
            / observation.stack.source_path.with_suffix(".tiff").name,
        )
    return PlannedArchiveObservation(
        reconstructed=observation,
        metadata=metadata,
        hierarchy_directory=hierarchy_directory,
        observation_name=observation_name,
        observation_directory=observation_directory,
        lights_directory=lights_directory,
        seestar_stacked_directory=stack_directory,
        tiff_directory=tiff_directory,
        lights=lights,
        stack=stack,
    )


def _record_destinations(
    observation: PlannedArchiveObservation, destinations: dict[Path, Path]
) -> None:
    files = (*observation.lights, *((observation.stack,) if observation.stack else ()))
    for planned_file in files:
        destinations_to_record = (planned_file.fits_destination,)
        if planned_file.tiff_destination is not None:
            destinations_to_record += (planned_file.tiff_destination,)
        for destination in destinations_to_record:
            previous = destinations.get(destination)
            if previous is not None and previous != planned_file.source_path:
                raise ArchivePlanningCollisionError(
                    f"Distinct sources {previous} and {planned_file.source_path} "
                    f"map to {destination}"
                )
            destinations[destination] = planned_file.source_path


def _require_beneath_root(root: Path, destination: Path) -> None:
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise ArchivePlanningConfigurationError(
            f"Planned destination escapes archive root: {destination}"
        ) from error
