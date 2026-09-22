"""Library-level composition of the established Seestar archive pipeline."""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsError
from seestar_toolkit.tiff import TiffError

from .discovery import discover_seestar_inputs
from .execution import execute_archive_plan
from .execution_models import (
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    CollisionPolicy,
    SourceAction,
)
from .indexing import generate_archive_indexes
from .orchestration_models import (
    ArchiveTiffOutcome,
    ArchiveTiffResult,
    PreparedSeestarArchive,
    SeestarArchiveResult,
)
from .planning import plan_seestar_archive
from .planning_models import ArchivePlan, PlannedFile, SavedLocation
from .reconstruction import reconstruct_seestar_observations

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
    source_action: SourceAction = SourceAction.COPY,
    collision_policy: CollisionPolicy = CollisionPolicy.SKIP_IDENTICAL,
) -> SeestarArchiveResult:
    """Run the established Seestar archive and TIFF pipeline in safe order."""
    prepared = prepare_seestar_archive(
        source_root,
        archive_root=archive_root,
        hierarchy_template=hierarchy_template,
        explicit_location=explicit_location,
        saved_locations=saved_locations,
    )
    return execute_prepared_seestar_archive(
        prepared,
        source_action=source_action,
        collision_policy=collision_policy,
    )


def prepare_seestar_archive(
    source_root: str | Path,
    *,
    archive_root: str | Path,
    hierarchy_template: str = "{target}/{location}/{session_end_date}",
    explicit_location: str | None = None,
    saved_locations: tuple[SavedLocation, ...] = (),
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
    )
    plan = _reconcile_incremental_observations(plan)
    return PreparedSeestarArchive(discovery=discovery, reconstruction=reconstruction, plan=plan)


def _reconcile_incremental_observations(plan: ArchivePlan) -> ArchivePlan:
    """Keep rerun destinations but allocate new observations after archived history."""
    used_by_hierarchy: dict[Path, set[int]] = {}
    reconciled = []
    for observation in plan.observations:
        hierarchy = observation.hierarchy_directory
        used = used_by_hierarchy.setdefault(hierarchy, _existing_observation_numbers(hierarchy))
        current_number = int(observation.observation_name.removeprefix("observation_"))
        current_has_matching_file = any(
            item.fits_destination.exists()
            for item in (
                *observation.lights,
                *((observation.stack,) if observation.stack else ()),
            )
        )
        if current_number not in used or current_has_matching_file:
            selected = current_number
        else:
            selected = max(used, default=0) + 1
        used.add(selected)
        name = f"observation_{selected:0{max(2, len(str(selected)))}d}"
        reconciled.append(_rename_planned_observation(observation, name))
    return replace(plan, observations=tuple(reconciled))


def _existing_observation_numbers(hierarchy: Path) -> set[int]:
    if not hierarchy.is_dir():
        return set()
    numbers = set()
    for path in hierarchy.iterdir():
        match = _OBSERVATION_DIRECTORY.fullmatch(path.name)
        if not match or not path.is_dir() or path.is_symlink():
            continue
        has_archived_fits = any(
            child.is_file() and child.suffix.casefold() in {".fit", ".fits"}
            for directory in (path / "lights", path / "seestar_stacked")
            if directory.is_dir() and not directory.is_symlink()
            for child in directory.iterdir()
        )
        if has_archived_fits:
            numbers.add(int(match.group("number")))
    return numbers


def _rename_planned_observation(observation, name: str):
    if observation.observation_name == name:
        return observation
    directory = observation.hierarchy_directory / name
    lights_directory = directory / "lights"
    stack_directory = directory / "seestar_stacked"
    tiff_directory = directory / "tiff"
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
) -> SeestarArchiveResult:
    """Execute originals and TIFFs from one already-prepared archive plan."""
    execution = execute_archive_plan(
        prepared.plan,
        action=source_action,
        collision_policy=collision_policy,
    )
    paired_files = zip(_planned_files(prepared.plan), execution.files, strict=True)
    tiffs = tuple(
        _generate_tiff(prepared.plan, planned_file, file_execution)
        for planned_file, file_execution in paired_files
        if planned_file.tiff_destination is not None
    )
    indexes = generate_archive_indexes(prepared.plan, execution)
    return SeestarArchiveResult(
        discovery=prepared.discovery,
        reconstruction=prepared.reconstruction,
        plan=prepared.plan,
        execution=execution,
        tiffs=tiffs,
        indexes=indexes,
    )


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
