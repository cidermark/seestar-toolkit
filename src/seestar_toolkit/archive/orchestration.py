"""Library-level composition of the established Seestar archive pipeline."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsError, inspect_fits
from seestar_toolkit.tiff import TiffError

from .discovery import discover_seestar_inputs
from .execution import execute_archive_plan, sha256_file
from .execution_models import (
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    CollisionPolicy,
    SourceAction,
)
from .indexing import generate_archive_indexes
from .light_tiff import (
    LightTiffCollisionDecider,
    finalise_archived_light_tiff,
    is_light_tiff_eligible,
)
from .orchestration_models import (
    ArchiveTiffOutcome,
    ArchiveTiffResult,
    PreparedSeestarArchive,
    SeestarArchiveResult,
)
from .planning import plan_seestar_archive
from .planning_models import ArchivePlan, PlannedFile, SavedLocation
from .reconstruction import (
    _recognised_telescope_identity,
    _telescope_identity,
    reconstruct_seestar_observations,
)

_TIFF_ELIGIBLE_OUTCOMES = frozenset(
    {
        ArchiveFileOutcome.COPIED,
        ArchiveFileOutcome.MOVED,
        ArchiveFileOutcome.SKIPPED_IDENTICAL,
    }
)
_OBSERVATION_DIRECTORY = re.compile(r"^observation_(?P<number>\d+)$")


def archive_seestar_session(
    source_root: str | Path,
    *,
    archive_root: str | Path,
    hierarchy_template: str = "{target}/{location}/{session_end_date}",
    explicit_location: str | None = None,
    saved_locations: tuple[SavedLocation, ...] = (),
    observation_date_policy: str = "end",
    source_action: SourceAction = SourceAction.COPY,
    collision_policy: CollisionPolicy = CollisionPolicy.SKIP_IDENTICAL,
    convert_lights: bool = False,
    process_existing_lights: Callable[[int, int, int], bool] | None = None,
    light_tiff_collision_decider: LightTiffCollisionDecider | None = None,
) -> SeestarArchiveResult:
    """Run the established Seestar archive and TIFF pipeline in safe order."""
    prepared = prepare_seestar_archive(
        source_root,
        archive_root=archive_root,
        hierarchy_template=hierarchy_template,
        explicit_location=explicit_location,
        saved_locations=saved_locations,
        observation_date_policy=observation_date_policy,
    )
    return execute_prepared_seestar_archive(
        prepared,
        source_action=source_action,
        collision_policy=collision_policy,
        convert_lights=convert_lights,
        process_existing_lights=process_existing_lights,
        light_tiff_collision_decider=light_tiff_collision_decider,
    )


def prepare_seestar_archive(
    source_root: str | Path,
    *,
    archive_root: str | Path,
    hierarchy_template: str = "{target}/{location}/{session_end_date}",
    explicit_location: str | None = None,
    saved_locations: tuple[SavedLocation, ...] = (),
    observation_date_policy: str = "end",
) -> PreparedSeestarArchive:
    """Discover, reconstruct, and plan without filesystem mutation."""
    discovery = discover_seestar_inputs(source_root)
    reconstruction = reconstruct_seestar_observations(discovery)
    plan = plan_seestar_archive(
        reconstruction,
        archive_root=archive_root,
        hierarchy_template=hierarchy_template,
        explicit_location=explicit_location,
        saved_locations=saved_locations,
        observation_date_policy=observation_date_policy,
    )
    plan = _reconcile_incremental_observations(plan)
    return PreparedSeestarArchive(discovery=discovery, reconstruction=reconstruction, plan=plan)


def _reconcile_incremental_observations(plan: ArchivePlan) -> ArchivePlan:
    """Reuse compatible filename matches, reserving each selection once per plan."""
    existing_by_hierarchy: dict[Path, dict[int, Path]] = {}
    reserved_by_hierarchy: dict[Path, set[int]] = {}
    identity_cache: dict[Path, frozenset[str] | None] = {}
    reconciled = []
    for observation in plan.observations:
        hierarchy = observation.hierarchy_directory
        if hierarchy not in existing_by_hierarchy:
            existing_by_hierarchy[hierarchy] = _existing_observation_directories(hierarchy)
        existing = existing_by_hierarchy[hierarchy]
        reserved = reserved_by_hierarchy.setdefault(hierarchy, set())
        current_number = int(observation.observation_name.removeprefix("observation_"))
        incoming_ids = {
            identity
            for item in (
                *observation.reconstructed.lights,
                *((observation.reconstructed.stack,) if observation.reconstructed.stack else ()),
            )
            if (identity := _telescope_identity(item)) is not None
        }
        relative_files = [
            Path("fits_images/lights") / item.source_path.name for item in observation.lights
        ]
        if observation.stack is not None:
            relative_files.append(Path("seestar_stacked") / observation.stack.source_path.name)

        # Prefer the original number when several compatible filename matches exist.
        selected = None
        for number in sorted(existing, key=lambda n: (n != current_number, n)):
            directory = existing[number]
            if number in reserved or not any(
                (directory / path).is_file() for path in relative_files
            ):
                continue
            if directory not in identity_cache:
                identity_cache[directory] = _archived_device_identities(directory)
            archived_ids = identity_cache[directory]
            # None means unreadable, not successfully inspected missing TELESCOP.
            if archived_ids is not None and len(archived_ids | incoming_ids) <= 1:
                selected = number
                break
        if selected is None:
            selected = max((*existing, *reserved), default=0) + 1
            name = f"observation_{selected:0{max(2, len(str(selected)))}d}"
        else:
            name = existing[selected].name
        reserved.add(selected)
        reconciled.append(_rename_planned_observation(observation, name))
    return replace(plan, observations=tuple(reconciled))


def _existing_observation_directories(hierarchy: Path) -> dict[int, Path]:
    if not hierarchy.is_dir():
        return {}
    directories = {}
    for path in sorted(hierarchy.iterdir()):
        match = _OBSERVATION_DIRECTORY.fullmatch(path.name)
        if not match or not path.is_dir() or path.is_symlink():
            continue
        try:
            has_archived_fits = any(
                child.is_file() and child.suffix.casefold() in {".fit", ".fits"}
                for directory in (path / "fits_images" / "lights", path / "seestar_stacked")
                if directory.is_dir() and not directory.is_symlink()
                for child in directory.iterdir()
            )
        except OSError:
            # Reserve inaccessible history rather than treating its number as free.
            has_archived_fits = True
        if has_archived_fits:
            directories[int(match.group("number"))] = path
    return directories


def _archived_device_identities(directory: Path) -> frozenset[str] | None:
    """Read all relevant FITS; an inspection failure makes this history unsafe to reuse."""
    identities = set()
    try:
        for frame_directory in (
            directory / "fits_images" / "lights",
            directory / "seestar_stacked",
        ):
            if frame_directory.is_symlink():
                return None
            if not frame_directory.is_dir():
                continue
            for path in sorted(frame_directory.iterdir()):
                if path.suffix.casefold() not in {".fit", ".fits"}:
                    continue
                if path.is_symlink():
                    return None
                if not path.is_file():
                    continue
                identity = _recognised_telescope_identity(inspect_fits(path).telescope)
                if identity is not None:
                    identities.add(identity)
    except (FitsError, OSError):
        return None
    return frozenset(identities)


def _rename_planned_observation(observation, name: str):
    if observation.observation_name == name:
        return observation
    directory = observation.hierarchy_directory / name
    lights_directory = directory / "fits_images" / "lights"
    stack_directory = directory / "seestar_stacked"
    tiff_directory = directory / "tiff_images" / "lights"
    lights = tuple(
        replace(
            item,
            fits_destination=lights_directory / item.fits_destination.name,
            tiff_destination=(
                tiff_directory / item.tiff_destination.name
                if item.tiff_destination is not None
                else None
            ),
        )
        for item in observation.lights
    )
    stack = (
        replace(
            observation.stack,
            fits_destination=stack_directory / observation.stack.fits_destination.name,
            tiff_destination=stack_directory / observation.stack.tiff_destination.name,
        )
        if observation.stack
        else None
    )
    return replace(
        observation,
        observation_name=name,
        observation_directory=directory,
        lights_directory=lights_directory,
        seestar_stacked_directory=stack_directory,
        tiff_directory=tiff_directory,
        lights=lights,
        stack=stack,
    )


def execute_prepared_seestar_archive(
    prepared: PreparedSeestarArchive,
    *,
    source_action: SourceAction = SourceAction.COPY,
    collision_policy: CollisionPolicy = CollisionPolicy.SKIP_IDENTICAL,
    convert_lights: bool = False,
    process_existing_lights: Callable[[int, int, int], bool] | None = None,
    light_tiff_collision_decider: LightTiffCollisionDecider | None = None,
) -> SeestarArchiveResult:
    """Execute originals and TIFFs from one already-prepared archive plan."""
    execution = execute_archive_plan(
        prepared.plan,
        action=source_action,
        collision_policy=collision_policy,
    )
    pairs = tuple(zip(_planned_files(prepared.plan), execution.files, strict=True))
    paired_files = iter(pairs)
    tiffs = tuple(
        _generate_tiff(prepared.plan, planned_file, file_execution)
        for planned_file, file_execution in paired_files
        if planned_file.tiff_destination is not None
    )
    indexes = generate_archive_indexes(prepared.plan, execution)
    light_tiffs = ()
    declined = 0
    if convert_lights:
        eligible = [
            (planned, result)
            for planned, result in pairs
            if planned.tiff_destination is None and is_light_tiff_eligible(result)
        ]
        existing = [
            pair for pair in eligible if pair[1].outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL
        ]
        new = [
            pair for pair in eligible if pair[1].outcome is not ArchiveFileOutcome.SKIPPED_IDENTICAL
        ]
        selected_existing = existing
        if existing and process_existing_lights is not None:
            create_count = sum(
                not (
                    _light_tiff_destination(planned).exists()
                    or _light_tiff_destination(planned).is_symlink()
                )
                for planned, _ in existing
            )
            compare_count = len(existing) - create_count
            if not process_existing_lights(len(existing), create_count, compare_count):
                selected_existing = []
                declined = len(existing)
        light_tiffs = tuple(
            finalise_archived_light_tiff(
                result.destination_path,
                archive_root=prepared.plan.config.archive_root,
                observation_directory=_observation_for_light(prepared.plan, planned),
                collision_decider=light_tiff_collision_decider,
            )
            for planned, result in (*new, *selected_existing)
        )
    return SeestarArchiveResult(
        discovery=prepared.discovery,
        reconstruction=prepared.reconstruction,
        plan=prepared.plan,
        execution=execution,
        tiffs=tiffs,
        indexes=indexes,
        light_tiffs=light_tiffs,
        existing_lights_declined=declined,
    )


def _observation_for_light(plan: ArchivePlan, planned_file: PlannedFile) -> Path:
    for observation in plan.observations:
        if planned_file in observation.lights:
            return observation.observation_directory
    raise ValueError("Planned light does not belong to an observation")


def _light_tiff_destination(planned_file: PlannedFile) -> Path:
    return (
        planned_file.fits_destination.parents[2]
        / "tiff_images"
        / "lights"
        / planned_file.fits_destination.with_suffix(".tiff").name
    )


def light_tiff_dry_run_counts(
    prepared: PreparedSeestarArchive, collision_policy: CollisionPolicy
) -> tuple[int, int, int]:
    """Return would-create, requires-comparison, and previously-archived counts."""
    create = compare = existing = 0
    for observation in prepared.plan.observations:
        for light in observation.lights:
            previously_archived = False
            if light.fits_destination.exists() or light.fits_destination.is_symlink():
                if collision_policy is CollisionPolicy.ERROR:
                    continue
                try:
                    identical = sha256_file(light.source_path) == sha256_file(
                        light.fits_destination
                    )
                except OSError:
                    continue
                if not identical and collision_policy is not CollisionPolicy.OVERWRITE:
                    continue
                previously_archived = identical
            destination = _light_tiff_destination(light)
            if destination.exists() or destination.is_symlink():
                compare += 1
            else:
                create += 1
            if previously_archived:
                existing += 1
    return create, compare, existing


def _planned_files(plan: ArchivePlan) -> tuple[PlannedFile, ...]:
    return tuple(
        planned_file
        for observation in plan.observations
        for planned_file in (
            *observation.lights,
            *((observation.stack,) if observation.stack else ()),
        )
    )


def _generate_tiff(
    plan: ArchivePlan,
    planned_file: PlannedFile,
    file_execution: ArchiveFileExecutionResult,
) -> ArchiveTiffResult:
    archived_fits = file_execution.destination_path
    destination = planned_file.tiff_destination
    if destination is None:
        raise ValueError("TIFF generation requires a planned TIFF destination")
    base = {
        "archived_fits_path": archived_fits,
        "tiff_destination": destination,
        "original_execution": file_execution,
    }
    if file_execution.outcome not in _TIFF_ELIGIBLE_OUTCOMES:
        return ArchiveTiffResult(
            **base,
            outcome=ArchiveTiffOutcome.INELIGIBLE,
            diagnostic=(
                "Original FITS archive outcome is not eligible for TIFF generation: "
                f"{file_execution.outcome.name}"
            ),
        )
    try:
        _prepare_tiff_destination(plan.config.archive_root, destination)
        if destination.exists():
            return ArchiveTiffResult(
                **base,
                outcome=ArchiveTiffOutcome.COLLISION,
                diagnostic="TIFF destination already exists; existing file preserved",
            )
        convert_fits_to_tiff(archived_fits, destination)
    except (FitsError, TiffError, ValueError, OSError) as error:
        return ArchiveTiffResult(
            **base,
            outcome=ArchiveTiffOutcome.FAILED,
            diagnostic=f"TIFF generation failed: {error}",
        )
    return ArchiveTiffResult(**base, outcome=ArchiveTiffOutcome.CREATED)


def _prepare_tiff_destination(archive_root: Path, destination: Path) -> None:
    if not archive_root.is_absolute() or not destination.is_absolute() or ".." in destination.parts:
        raise OSError("TIFF destination is not an absolute safe path")
    root_real = archive_root.resolve(strict=False)
    destination_real = destination.resolve(strict=False)
    _require_beneath(root_real, destination_real)
    destination.parent.mkdir(parents=True, exist_ok=True)
    parent_real = destination.parent.resolve(strict=True)
    _require_beneath(root_real, parent_real)
    if destination.is_symlink():
        _require_beneath(root_real, destination.resolve(strict=False))
    elif destination.exists() and not destination.is_file():
        raise OSError(f"TIFF destination is not a regular file: {destination}")


def _require_beneath(root: Path, path: Path) -> None:
    if path == root:
        raise OSError(f"TIFF destination must be beneath archive root: {path}")
    try:
        path.relative_to(root)
    except ValueError as error:
        raise OSError(f"TIFF destination escapes archive root: {path}") from error
