"""Safe execution of original FITS placements from an existing archive plan."""

from __future__ import annotations

import hashlib
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from .exceptions import ArchiveExecutionError
from .execution_models import (
    ArchiveCollisionState,
    ArchiveExecutionResult,
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    CollisionPolicy,
    SourceAction,
)
from .planning_models import ArchivePlan, PlannedFile

_COPY_CHUNK_SIZE = 1024 * 1024
_FITS_SUFFIXES = frozenset({".fit", ".fits"})


def sha256_file(path: str | Path, *, chunk_size: int = _COPY_CHUNK_SIZE) -> str:
    """Return a streamed SHA-256 digest of one file."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        while chunk := source.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def execute_archive_plan(
    plan: ArchivePlan,
    *,
    action: SourceAction = SourceAction.COPY,
    collision_policy: CollisionPolicy = CollisionPolicy.SKIP_IDENTICAL,
) -> ArchiveExecutionResult:
    """Execute only original FITS placements, continuing independent failures."""
    if not isinstance(action, SourceAction):
        raise ArchiveExecutionError("action must be a SourceAction")
    if not isinstance(collision_policy, CollisionPolicy):
        raise ArchiveExecutionError("collision_policy must be a CollisionPolicy")
    archive_root = plan.config.archive_root
    if not archive_root.is_absolute() or ".." in archive_root.parts:
        raise ArchiveExecutionError("ArchivePlan contains an invalid archive root")

    files = tuple(
        planned_file
        for observation in plan.observations
        for planned_file in (
            *observation.lights,
            *((observation.stack,) if observation.stack else ()),
        )
    )
    results = tuple(
        _execute_file(
            planned_file,
            archive_root=archive_root,
            action=action,
            collision_policy=collision_policy,
        )
        for planned_file in files
    )
    return ArchiveExecutionResult(
        plan=plan,
        action=action,
        collision_policy=collision_policy,
        files=results,
    )


def _execute_file(
    planned_file: PlannedFile,
    *,
    archive_root: Path,
    action: SourceAction,
    collision_policy: CollisionPolicy,
) -> ArchiveFileExecutionResult:
    source = planned_file.source_path
    destination = planned_file.fits_destination
    base = {
        "source_path": source,
        "destination_path": destination,
        "requested_action": action,
    }
    if source.suffix.casefold() not in _FITS_SUFFIXES:
        return _failure(base, "Planned source is not a FIT/FITS file")

    try:
        _validate_source(source)
        root_real, destination_real = _validate_destination(archive_root, destination)
        if destination.exists() and os.path.samefile(source, destination):
            return _failure(base, "Source and destination identify the same file")
        destination.parent.mkdir(parents=True, exist_ok=True)
        _validate_destination_after_creation(root_real, destination)

        source_hash = sha256_file(source)
        source_size = source.stat().st_size
        if destination.exists():
            return _handle_existing_destination(
                planned_file,
                base=base,
                source_hash=source_hash,
                source_size=source_size,
                destination_real=destination_real,
                root_real=root_real,
                action=action,
                collision_policy=collision_policy,
            )

        _stage_and_replace(source, destination, source_hash, root_real)
        return _finish_action(
            base,
            source=source,
            action=action,
            source_hash=source_hash,
            source_size=source_size,
            collision=ArchiveCollisionState.NONE,
        )
    except OSError as error:
        return _failure(base, f"Filesystem operation failed: {error}")


def _validate_source(source: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Source file does not exist: {source}")
    if not source.is_file():
        raise OSError(f"Source is not a regular file: {source}")


def _validate_destination(archive_root: Path, destination: Path) -> tuple[Path, Path]:
    if not destination.is_absolute() or ".." in destination.parts:
        raise OSError(f"Planned destination is not an absolute safe path: {destination}")
    root_real = archive_root.resolve(strict=False)
    destination_real = destination.resolve(strict=False)
    _require_beneath(root_real, destination_real)
    return root_real, destination_real


def _validate_destination_after_creation(root_real: Path, destination: Path) -> None:
    parent_real = destination.parent.resolve(strict=True)
    _require_beneath(root_real, parent_real)
    if destination.is_symlink():
        destination_real = destination.resolve(strict=False)
        _require_beneath(root_real, destination_real)
    elif destination.exists() and not destination.is_file():
        raise OSError(f"Destination is not a regular file: {destination}")


def _require_beneath(root: Path, path: Path) -> None:
    if path == root:
        raise OSError(f"Destination must be beneath archive root: {path}")
    try:
        path.relative_to(root)
    except ValueError as error:
        raise OSError(f"Destination escapes archive root: {path}") from error


def _handle_existing_destination(
    planned_file: PlannedFile,
    *,
    base: dict,
    source_hash: str,
    source_size: int,
    destination_real: Path,
    root_real: Path,
    action: SourceAction,
    collision_policy: CollisionPolicy,
) -> ArchiveFileExecutionResult:
    destination = planned_file.fits_destination
    destination_hash = sha256_file(destination)
    collision = (
        ArchiveCollisionState.IDENTICAL
        if source_hash == destination_hash
        else ArchiveCollisionState.DIFFERENT
    )
    if collision is ArchiveCollisionState.IDENTICAL:
        if collision_policy is CollisionPolicy.ERROR:
            return ArchiveFileExecutionResult(
                **base,
                outcome=ArchiveFileOutcome.COLLISION,
                collision=collision,
                source_sha256=source_hash,
                destination_sha256=destination_hash,
                diagnostic="Destination already exists, including identical content",
            )
        return ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.SKIPPED_IDENTICAL,
            collision=collision,
            source_sha256=source_hash,
            destination_sha256=destination_hash,
            diagnostic="Identical destination already present; source retained",
        )

    if collision_policy is not CollisionPolicy.OVERWRITE:
        return ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.COLLISION,
            collision=collision,
            source_sha256=source_hash,
            destination_sha256=destination_hash,
            diagnostic="Destination contains different content; no files changed",
        )

    _require_beneath(root_real, destination_real)
    try:
        _stage_and_replace(planned_file.source_path, destination, source_hash, root_real)
    except OSError as error:
        return ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.FAILED,
            collision=collision,
            source_sha256=source_hash,
            destination_sha256=destination_hash,
            diagnostic=f"Safe destination replacement failed: {error}",
        )
    return _finish_action(
        base,
        source=planned_file.source_path,
        action=action,
        source_hash=source_hash,
        source_size=source_size,
        collision=collision,
        previous_destination_hash=destination_hash,
    )


def _stage_and_replace(source: Path, destination: Path, source_hash: str, root_real: Path) -> None:
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.tmp-",
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as staged, source.open("rb") as input_file:
            while chunk := input_file.read(_COPY_CHUNK_SIZE):
                staged.write(chunk)
            staged.flush()
            os.fsync(staged.fileno())
        if sha256_file(temporary_path) != source_hash:
            raise OSError("Staged destination content verification failed")
        _validate_destination_after_creation(root_real, destination)
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            with suppress(OSError):
                temporary_path.unlink(missing_ok=True)


def _finish_action(
    base: dict,
    *,
    source: Path,
    action: SourceAction,
    source_hash: str,
    source_size: int,
    collision: ArchiveCollisionState,
    previous_destination_hash: str | None = None,
) -> ArchiveFileExecutionResult:
    if action is SourceAction.COPY:
        return ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.COPIED,
            collision=collision,
            source_sha256=source_hash,
            destination_sha256=source_hash,
            bytes_processed=source_size,
            diagnostic=(
                "Different destination content replaced after explicit overwrite"
                if previous_destination_hash is not None
                else None
            ),
        )
    try:
        source.unlink()
    except OSError as error:
        return ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.PARTIAL,
            collision=collision,
            source_sha256=source_hash,
            destination_sha256=source_hash,
            bytes_processed=source_size,
            diagnostic=f"Destination established but source removal failed: {error}",
        )
    return ArchiveFileExecutionResult(
        **base,
        outcome=ArchiveFileOutcome.MOVED,
        collision=collision,
        source_sha256=source_hash,
        destination_sha256=source_hash,
        bytes_processed=source_size,
    )


def _failure(base: dict, diagnostic: str) -> ArchiveFileExecutionResult:
    return ArchiveFileExecutionResult(
        **base,
        outcome=ArchiveFileOutcome.FAILED,
        collision=ArchiveCollisionState.NONE,
        diagnostic=diagnostic,
    )
