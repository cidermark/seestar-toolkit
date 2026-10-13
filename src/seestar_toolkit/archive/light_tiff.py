"""Safe finalisation of optional TIFF derivatives for archived individual lights."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from uuid import uuid4

from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsError
from seestar_toolkit.tiff import TiffError

from .execution import sha256_file
from .execution_models import ArchiveFileExecutionResult, ArchiveFileOutcome

_OWNED_CANDIDATE_PREFIX = ".seestar-toolkit-enh003-"
_OWNED_CANDIDATE_SUFFIX = ".tiff"
_OWNED_CANDIDATE_NAME = re.compile(
    rf"{re.escape(_OWNED_CANDIDATE_PREFIX)}[0-9a-f]{{32}}{re.escape(_OWNED_CANDIDATE_SUFFIX)}"
)


class LightTiffOutcome(Enum):
    """Outcome of one individual-light derivative attempt."""

    CREATED = auto()
    PRIMARY_REPLACED = auto()
    DUPLICATE_CREATED = auto()
    DUPLICATE_REPLACED = auto()
    ALREADY_PRESENT = auto()
    SKIPPED = auto()
    FAILED = auto()


class LightTiffCollisionDecision(Enum):
    """Engine-level choice for a differing existing light TIFF."""

    KEEP_BOTH = auto()
    REPLACE_EXISTING = auto()
    REPLACE_DUPLICATE = auto()
    SKIP = auto()


@dataclass(frozen=True, slots=True)
class LightTiffResult:
    """Structured result for one archived-light TIFF operation."""

    archived_fits_path: Path
    tiff_destination: Path
    outcome: LightTiffOutcome
    duplicate_destination: Path | None = None
    diagnostic: str | None = None


def is_light_tiff_eligible(result: ArchiveFileExecutionResult) -> bool:
    """Return whether verified archived FITS evidence permits later conversion.

    A generic ``PARTIAL`` is deliberately insufficient.  Only the existing
    move-delete failure representation records that the destination was
    established before the later source-removal problem.
    """

    return result.outcome in {
        ArchiveFileOutcome.COPIED,
        ArchiveFileOutcome.MOVED,
        ArchiveFileOutcome.SKIPPED_IDENTICAL,
    } or (result.outcome is ArchiveFileOutcome.PARTIAL and result.destination_established)


def finalise_archived_light_tiff(
    archived_fits: str | Path,
    *,
    archive_root: str | Path,
    observation_directory: str | Path,
    decision: LightTiffCollisionDecision | None = None,
) -> LightTiffResult:
    """Convert one authoritative archived light and finalise it safely.

    The caller supplies a previously established FITS beneath the observation's
    ``fits_images/lights`` directory.  No source-tree path participates in this
    operation.  ``None`` is a safe skip for a differing TIFF collision; later
    orchestration owns prompting and supplies an explicit decision.
    """

    source = Path(archived_fits)
    root = Path(archive_root)
    observation = Path(observation_directory)
    primary = observation / "tiff_images" / "lights" / source.with_suffix(".tiff").name
    duplicate = primary.with_name(f"{primary.name}.duplicate")
    base = {"archived_fits_path": source, "tiff_destination": primary}
    candidate: Path | None = None
    workspace_created = False
    created_final_directories: list[Path] = []
    result: LightTiffResult

    try:
        root_real = _validate_archive_paths(root, observation, source, primary)
        workspace, workspace_created = _prepare_workspace(root_real, observation)
        _remove_stale_owned_candidates(workspace)
        candidate = workspace / f"{_OWNED_CANDIDATE_PREFIX}{uuid4().hex}{_OWNED_CANDIDATE_SUFFIX}"
        convert_fits_to_tiff(source, candidate)
        _validate_candidate(candidate, workspace, root_real)

        if primary.exists() or primary.is_symlink():
            _require_regular_file(primary, root_real, "Existing primary TIFF")
            if sha256_file(candidate) == sha256_file(primary):
                _remove_candidate(candidate)
                candidate = None
                result = LightTiffResult(**base, outcome=LightTiffOutcome.ALREADY_PRESENT)
            else:
                result = _finalise_collision(
                    candidate,
                    primary=primary,
                    duplicate=duplicate,
                    root_real=root_real,
                    base=base,
                    decision=decision or LightTiffCollisionDecision.SKIP,
                )
        else:
            _promote_new(candidate, primary, root_real, created_final_directories)
            candidate = None
            result = LightTiffResult(**base, outcome=LightTiffOutcome.CREATED)
    except (FitsError, TiffError, ValueError, OSError) as error:
        cleanup_error = _cleanup_candidate(candidate)
        message = str(error)
        if cleanup_error is not None:
            message = f"{message}; candidate cleanup failed: {cleanup_error}"
        result = LightTiffResult(**base, outcome=LightTiffOutcome.FAILED, diagnostic=message)

    if result.outcome is LightTiffOutcome.FAILED:
        rollback_errors = _rollback_created_directories(created_final_directories)
        if rollback_errors:
            result = _failed_result(base, result.diagnostic, *rollback_errors)

    workspace_error = _remove_workspace_if_created_empty(observation / "tmp", workspace_created)
    if workspace_error is not None:
        result = _failed_result(
            base,
            result.diagnostic if result.outcome is LightTiffOutcome.FAILED else None,
            f"workspace cleanup failed: {workspace_error}",
        )
    return result


def _finalise_collision(
    candidate: Path,
    *,
    primary: Path,
    duplicate: Path,
    root_real: Path,
    base: dict[str, Path],
    decision: LightTiffCollisionDecision,
) -> LightTiffResult:
    has_duplicate = duplicate.exists() or duplicate.is_symlink()
    if has_duplicate:
        _require_regular_file(duplicate, root_real, "Existing duplicate TIFF")
        if decision is LightTiffCollisionDecision.REPLACE_DUPLICATE:
            _replace(candidate, duplicate, root_real)
            return LightTiffResult(
                **base,
                outcome=LightTiffOutcome.DUPLICATE_REPLACED,
                duplicate_destination=duplicate,
            )
        if decision is not LightTiffCollisionDecision.SKIP:
            raise ValueError("Only replace-duplicate or skip is valid when a duplicate exists")
    elif decision is LightTiffCollisionDecision.KEEP_BOTH:
        _promote_new(candidate, duplicate, root_real)
        return LightTiffResult(
            **base,
            outcome=LightTiffOutcome.DUPLICATE_CREATED,
            duplicate_destination=duplicate,
        )
    elif decision is LightTiffCollisionDecision.REPLACE_EXISTING:
        _replace(candidate, primary, root_real)
        return LightTiffResult(**base, outcome=LightTiffOutcome.PRIMARY_REPLACED)
    elif decision is not LightTiffCollisionDecision.SKIP:
        raise ValueError("Invalid TIFF collision decision")

    _remove_candidate(candidate)
    return LightTiffResult(**base, outcome=LightTiffOutcome.SKIPPED)


def _validate_archive_paths(root: Path, observation: Path, source: Path, primary: Path) -> Path:
    if not root.is_absolute() or not observation.is_absolute() or not source.is_absolute():
        raise OSError("Archive root, observation directory, and archived FITS must be absolute")
    root_real = root.resolve(strict=False)
    observation_real = observation.resolve(strict=False)
    _require_beneath(root_real, observation_real)
    expected_source_parent = observation / "fits_images" / "lights"
    if source.parent != expected_source_parent:
        raise OSError("Archived light FITS is not in observation fits_images/lights")
    _require_regular_file(source, root_real, "Archived light FITS")
    _require_beneath(root_real, primary.resolve(strict=False))
    return root_real


def _prepare_workspace(root_real: Path, observation: Path) -> tuple[Path, bool]:
    workspace = observation / "tmp"
    existed = workspace.exists() or workspace.is_symlink()
    if workspace.is_symlink():
        raise OSError("Light TIFF workspace must not be a symlink")
    if existed:
        if not workspace.is_dir():
            raise OSError("Light TIFF workspace is not a directory")
    else:
        workspace.mkdir(parents=True)
    _require_beneath(root_real, workspace.resolve(strict=True))
    return workspace, not existed


def _remove_stale_owned_candidates(workspace: Path) -> None:
    for path in workspace.iterdir():
        if _is_owned_candidate_name(path.name) and path.is_file() and not path.is_symlink():
            path.unlink()


def _is_owned_candidate_name(name: str) -> bool:
    return _OWNED_CANDIDATE_NAME.fullmatch(name) is not None


def _validate_candidate(candidate: Path, workspace: Path, root_real: Path) -> None:
    if candidate.parent != workspace or not _is_owned_candidate_name(candidate.name):
        raise OSError("TIFF candidate is not the expected owned workspace file")
    _require_regular_file(candidate, root_real, "Owned TIFF candidate")
    if candidate.parent.resolve(strict=True) != workspace.resolve(strict=True):
        raise OSError("TIFF candidate is outside the intended workspace")


def _ensure_final_parent(
    destination: Path, root_real: Path, created_directories: list[Path]
) -> None:
    parent = destination.parent
    missing: list[Path] = []
    existing = parent
    while not (existing.exists() or existing.is_symlink()):
        missing.append(existing)
        existing = existing.parent
    if existing.is_symlink() or not existing.is_dir():
        raise OSError("Light TIFF destination hierarchy is not a real directory")
    _require_beneath(root_real, existing.resolve(strict=True))
    for directory in reversed(missing):
        directory.mkdir()
        created_directories.append(directory)
        _require_beneath(root_real, directory.resolve(strict=True))
    if parent.is_symlink() or not parent.is_dir():
        raise OSError("Light TIFF destination parent must be a real directory")
    _require_beneath(root_real, parent.resolve(strict=True))


def _promote_new(
    candidate: Path,
    destination: Path,
    root_real: Path,
    created_directories: list[Path] | None = None,
) -> None:
    tracked_directories = [] if created_directories is None else created_directories
    _ensure_final_parent(destination, root_real, tracked_directories)
    if destination.exists() or destination.is_symlink():
        raise OSError(f"Light TIFF destination already exists: {destination}")
    os.link(candidate, destination)
    candidate.unlink()


def _replace(candidate: Path, destination: Path, root_real: Path) -> None:
    _ensure_final_parent(destination, root_real, [])
    _require_regular_file(destination, root_real, "Existing TIFF")
    os.replace(candidate, destination)


def _require_regular_file(path: Path, root_real: Path, label: str) -> None:
    if path.is_symlink():
        raise OSError(f"{label} must not be a symlink")
    if not path.is_file():
        raise OSError(f"{label} is not a regular file: {path}")
    _require_beneath(root_real, path.resolve(strict=True))


def _remove_candidate(candidate: Path) -> None:
    if candidate.is_symlink() or not candidate.is_file():
        raise OSError("Owned TIFF candidate is not a regular file")
    candidate.unlink()


def _cleanup_candidate(candidate: Path | None) -> OSError | None:
    if candidate is None or not (candidate.exists() or candidate.is_symlink()):
        return None
    try:
        _remove_candidate(candidate)
    except OSError as error:
        return error
    return None


def _rollback_created_directories(created_directories: list[Path]) -> tuple[str, ...]:
    errors: list[str] = []
    for directory in reversed(created_directories):
        try:
            directory.rmdir()
        except OSError as error:
            errors.append(f"derivative directory rollback failed for {directory}: {error}")
    return tuple(errors)


def _remove_workspace_if_created_empty(workspace: Path, workspace_created: bool) -> OSError | None:
    if not workspace_created:
        return None
    try:
        workspace.rmdir()
    except OSError as error:
        return error
    return None


def _failed_result(
    base: dict[str, Path], diagnostic: str | None, *additional: str
) -> LightTiffResult:
    message = "; ".join(part for part in (diagnostic, *additional) if part)
    return LightTiffResult(
        **base,
        outcome=LightTiffOutcome.FAILED,
        diagnostic=message,
    )


def _require_beneath(root: Path, path: Path) -> None:
    if path == root:
        raise OSError(f"Light TIFF path must be beneath archive root: {path}")
    try:
        path.relative_to(root)
    except ValueError as error:
        raise OSError(f"Light TIFF path escapes archive root: {path}") from error
