"""Conservative reconstruction of observations from a discovery inventory."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .models import (
    DiscoveryClassification,
    SeestarDiscoveryInventory,
    SeestarDiscoveryItem,
)
from .reconstruction_models import (
    ObservationCompatibility,
    ObservationReconstructionResult,
    ObservationStatus,
    ReconstructedObservation,
    TimestampEvidence,
)

_FILENAME_TIMESTAMP = re.compile(r"(?P<date>\d{8})-(?P<time>\d{6})(?:_|$)")
_STACK_COUNT = re.compile(r"^stacked_(?P<count>\d+)_", re.IGNORECASE)
_SEESTAR_DEVICE_ID = re.compile(r"s50_[0-9a-f]{8}")
_MAX_STACK_ASSOCIATION_GAP = timedelta(hours=12)
_MIN_LIGHTS_ONLY_CADENCE_LIMIT = timedelta(seconds=60)


@dataclass(frozen=True, slots=True)
class _FrameEvidence:
    item: SeestarDiscoveryItem
    timestamp: TimestampEvidence


def reconstruct_seestar_observations(
    inventory: SeestarDiscoveryInventory,
) -> ObservationReconstructionResult:
    """Reconstruct logical observations without rescanning or mutating sources."""
    frame_classifications = {
        DiscoveryClassification.LIGHT_FITS,
        DiscoveryClassification.SEESTAR_STACK_FITS,
    }
    frame_items = tuple(
        item for item in inventory.items if item.classification in frame_classifications
    )
    excluded_items = tuple(
        item for item in inventory.items if item.classification not in frame_classifications
    )
    frames = tuple(_FrameEvidence(item, _timestamp_evidence(item)) for item in frame_items)
    timed_frames = sorted(
        (frame for frame in frames if frame.timestamp.selected_at is not None),
        key=lambda frame: (
            frame.timestamp.selected_at,
            _frame_semantic_order(frame),
            _relative_path(inventory.root, frame.item.source_path),
        ),
    )
    missing_time_lights = [
        frame
        for frame in frames
        if frame.timestamp.selected_at is None
        and frame.item.classification is DiscoveryClassification.LIGHT_FITS
    ]
    missing_time_stacks = [
        frame
        for frame in frames
        if frame.timestamp.selected_at is None
        and frame.item.classification is DiscoveryClassification.SEESTAR_STACK_FITS
    ]

    pending_lights: list[_FrameEvidence] = []
    observations: list[ReconstructedObservation] = []
    for frame in timed_frames:
        if frame.item.classification is DiscoveryClassification.LIGHT_FITS:
            pending_lights.append(frame)
            continue

        compatible = [light for light in pending_lights if _association_is_compatible(light, frame)]
        if compatible:
            # An unidentified stack must not bridge contradictory light identities.
            compatible = _telescope_groups(compatible)[0]
            observations.append(_stack_observation(compatible, frame))
            compatible_paths = {light.item.source_path for light in compatible}
            pending_lights = [
                light for light in pending_lights if light.item.source_path not in compatible_paths
            ]
        else:
            observations.append(_stack_observation([], frame))

    observations.extend(_lights_only_observations(pending_lights))
    observations.extend(_unresolved_light_observation(frame) for frame in missing_time_lights)
    observations.extend(_stack_observation([], frame) for frame in missing_time_stacks)
    observations.sort(key=lambda observation: _observation_sort_key(inventory.root, observation))
    return ObservationReconstructionResult(
        observations=tuple(observations),
        excluded_items=excluded_items,
    )


def _frame_semantic_order(frame: _FrameEvidence) -> int:
    """Order equal-time lights before stacks so stacks close complete evidence."""
    return 0 if frame.item.classification is DiscoveryClassification.LIGHT_FITS else 1


def _timestamp_evidence(item: SeestarDiscoveryItem) -> TimestampEvidence:
    inspection = item.fits_inspection
    fits_at = None
    if inspection is not None:
        fits_at = inspection.captured_at or inspection.exposure_ended_at
    fits_at = _normalise_datetime(fits_at)
    filename_at = _filename_timestamp(item.source_path)
    problem = None
    if fits_at is None and filename_at is not None:
        problem = "FITS timestamp unavailable; filename timestamp selected"
    elif fits_at is None:
        problem = "No usable FITS or filename timestamp"
    return TimestampEvidence(
        selected_at=fits_at or filename_at,
        fits_at=fits_at,
        filename_at=filename_at,
        problem=problem,
    )


def _filename_timestamp(path: Path) -> datetime | None:
    matches = tuple(_FILENAME_TIMESTAMP.finditer(path.stem))
    if not matches:
        return None
    match = matches[-1]
    try:
        return datetime.strptime(f"{match.group('date')}{match.group('time')}", "%Y%m%d%H%M%S")
    except ValueError:
        return None


def _normalise_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(UTC).replace(tzinfo=None)
    return value


def _association_is_compatible(light: _FrameEvidence, stack: _FrameEvidence) -> bool:
    light_at = light.timestamp.selected_at
    stack_at = stack.timestamp.selected_at
    if light_at is None or stack_at is None:
        return False
    gap = stack_at - light_at
    if gap < timedelta(0) or gap > _MAX_STACK_ASSOCIATION_GAP:
        return False
    return _metadata_is_compatible(light.item, stack.item)


def _metadata_is_compatible(first: SeestarDiscoveryItem, second: SeestarDiscoveryItem) -> bool:
    first_key = _compatibility_key(first)
    second_key = _compatibility_key(second)
    if first_key is None or second_key is None:
        return False
    return (
        first_key[0] == second_key[0]
        and math.isclose(first_key[1], second_key[1], rel_tol=0.0, abs_tol=1e-6)
        and first_key[2] == second_key[2]
        and _capture_mode_is_compatible(first, second)
        and _telescope_is_compatible(first, second)
    )


def _compatibility_key(item: SeestarDiscoveryItem) -> tuple[str, float, str] | None:
    inspection = item.fits_inspection
    target = item.target_candidate
    if (
        inspection is None
        or target is None
        or inspection.exposure_seconds is None
        or inspection.filter_name is None
    ):
        return None
    return (
        target.strip().casefold(),
        inspection.exposure_seconds,
        inspection.filter_name.strip().casefold(),
    )


def _capture_mode_is_compatible(first: SeestarDiscoveryItem, second: SeestarDiscoveryItem) -> bool:
    first_mode = first.fits_inspection.eq_mode if first.fits_inspection else None
    second_mode = second.fits_inspection.eq_mode if second.fits_inspection else None
    return first_mode is None or second_mode is None or first_mode == second_mode


def _telescope_identity(item: SeestarDiscoveryItem) -> str | None:
    """Recognise only the evidenced S50 serial form, not generic model names."""
    telescope = item.fits_inspection.telescope if item.fits_inspection else None
    return _recognised_telescope_identity(telescope)


def _recognised_telescope_identity(telescope: str | None) -> str | None:
    """Normalise the narrow BUG-002 device convention for both archive stages."""
    if telescope is None:
        return None
    identity = telescope.strip().casefold()
    return identity if _SEESTAR_DEVICE_ID.fullmatch(identity) else None


def _telescope_is_compatible(first: SeestarDiscoveryItem, second: SeestarDiscoveryItem) -> bool:
    first_id = _telescope_identity(first)
    second_id = _telescope_identity(second)
    return first_id is None or second_id is None or first_id == second_id


def _telescope_groups(lights: list[_FrameEvidence]) -> list[list[_FrameEvidence]]:
    """Split ordered lights only on contradictory known device identities.

    Unknown identities join the first compatible group. Retain each group's
    known identity so an unknown frame cannot bridge two distinct devices.
    """
    groups: list[list[_FrameEvidence]] = []
    identities: list[str | None] = []
    for light in lights:
        identity = _telescope_identity(light.item)
        for index, known in enumerate(identities):
            if identity is None or known is None or identity == known:
                groups[index].append(light)
                identities[index] = known or identity
                break
        else:
            groups.append([light])
            identities.append(identity)
    return groups


def _stack_observation(
    lights: list[_FrameEvidence], stack: _FrameEvidence
) -> ReconstructedObservation:
    stack_count = _stack_count(stack.item.source_path)
    problems = _frame_problems((*lights, stack))
    stack_metadata_problem = _stack_metadata_problem(stack.item, stack_count)
    if stack_metadata_problem is not None:
        problems.append(stack_metadata_problem)
    if not lights:
        problems.append("Recognised Seestar stack has no compatible preceding lights")
    light_times = tuple(light.timestamp.selected_at for light in lights)
    return ReconstructedObservation(
        lights=tuple(light.item for light in lights),
        stack=stack.item,
        first_light_at=min(light_times) if light_times else None,
        last_light_at=max(light_times) if light_times else None,
        stack_at=stack.timestamp.selected_at,
        status=ObservationStatus.COMPLETE if lights else ObservationStatus.STACK_ONLY,
        compatibility=_compatibility(stack.item),
        reported_stack_count=stack_count,
        problems=tuple(problems),
    )


def _stack_metadata_problem(stack: SeestarDiscoveryItem, stack_count: int | None) -> str | None:
    inspection = stack.fits_inspection
    if inspection is None or stack_count is None:
        return None
    exposure = inspection.exposure_seconds
    total_exposure = inspection.total_exposure_seconds
    if (
        exposure is None
        or total_exposure is None
        or not math.isfinite(exposure)
        or not math.isfinite(total_exposure)
        or exposure <= 0
        or total_exposure < 0
    ):
        return None
    integrated_exposures = total_exposure / exposure
    if math.isclose(integrated_exposures, stack_count, rel_tol=1e-9, abs_tol=1e-6):
        return None
    return (
        "Seestar stack metadata disagree: "
        f"reported count {stack_count} does not match TOTALEXP / EXPTIME "
        f"({integrated_exposures:g})"
    )


def _lights_only_observations(
    lights: list[_FrameEvidence],
) -> list[ReconstructedObservation]:
    compatible_groups: dict[tuple[str, float, str, int], list[_FrameEvidence]] = defaultdict(list)
    unresolved: list[_FrameEvidence] = []
    for light in lights:
        key = _compatibility_key(light.item)
        if key is None:
            unresolved.append(light)
            continue
        mode = light.item.fits_inspection.eq_mode if light.item.fits_inspection else None
        compatible_groups[
            (key[0], round(key[1], 6), key[2], mode if mode is not None else -1)
        ].append(light)

    observations = [
        _lights_only_group(device_group)
        for _, group in sorted(compatible_groups.items(), key=lambda entry: entry[0])
        for device_group in _telescope_groups(
            sorted(group, key=lambda frame: frame.timestamp.selected_at)
        )
    ]
    observations.extend(_unresolved_light_observation(light) for light in unresolved)
    return observations


def _lights_only_group(lights: list[_FrameEvidence]) -> ReconstructedObservation:
    light_times = tuple(light.timestamp.selected_at for light in lights)
    gaps = tuple(
        later - earlier for earlier, later in zip(light_times, light_times[1:], strict=False)
    )
    exposure = lights[0].item.fits_inspection.exposure_seconds
    cadence_limit = max(
        _MIN_LIGHTS_ONLY_CADENCE_LIMIT,
        timedelta(seconds=(exposure or 0) * 5),
    )
    ambiguous = any(gap > cadence_limit for gap in gaps)
    problems = _frame_problems(lights)
    if ambiguous:
        problems.append(
            "Compatible lights contain a temporal gap too large for conservative grouping"
        )
    else:
        problems.append("No recognised Seestar stack closes these compatible lights")
    return ReconstructedObservation(
        lights=tuple(light.item for light in lights),
        stack=None,
        first_light_at=min(light_times),
        last_light_at=max(light_times),
        stack_at=None,
        status=ObservationStatus.AMBIGUOUS if ambiguous else ObservationStatus.LIGHTS_ONLY,
        compatibility=_compatibility(lights[0].item),
        reported_stack_count=None,
        problems=tuple(problems),
    )


def _unresolved_light_observation(frame: _FrameEvidence) -> ReconstructedObservation:
    problems = _frame_problems((frame,))
    problems.append("Light lacks sufficient evidence for conservative grouping")
    return ReconstructedObservation(
        lights=(frame.item,),
        stack=None,
        first_light_at=frame.timestamp.selected_at,
        last_light_at=frame.timestamp.selected_at,
        stack_at=None,
        status=ObservationStatus.UNRESOLVED,
        compatibility=_compatibility(frame.item),
        reported_stack_count=None,
        problems=tuple(problems),
    )


def _compatibility(item: SeestarDiscoveryItem) -> ObservationCompatibility | None:
    inspection = item.fits_inspection
    if inspection is None:
        return None
    return ObservationCompatibility(
        target=item.target_candidate,
        exposure_seconds=inspection.exposure_seconds,
        filter_name=inspection.filter_name,
        eq_mode=inspection.eq_mode,
    )


def _frame_problems(frames: tuple[_FrameEvidence, ...] | list[_FrameEvidence]) -> list[str]:
    problems: list[str] = []
    for frame in frames:
        if frame.item.problem is not None:
            problems.append(f"{frame.item.source_path.name}: {frame.item.problem}")
        if frame.timestamp.problem is not None:
            problems.append(f"{frame.item.source_path.name}: {frame.timestamp.problem}")
    return problems


def _stack_count(path: Path) -> int | None:
    match = _STACK_COUNT.match(path.stem)
    return int(match.group("count")) if match else None


def _observation_sort_key(
    root: Path, observation: ReconstructedObservation
) -> tuple[datetime, str]:
    times = tuple(
        time
        for time in (
            observation.first_light_at,
            observation.stack_at,
        )
        if time is not None
    )
    paths = tuple(light.source_path for light in observation.lights)
    if observation.stack is not None:
        paths = (*paths, observation.stack.source_path)
    path_key = min(_relative_path(root, path) for path in paths)
    return min(times) if times else datetime.max, path_key


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
