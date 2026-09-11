"""Tests for safe execution of planned original archive files."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pytest

from seestar_toolkit.archive import (
    ArchiveCollisionState,
    ArchiveExecutionError,
    ArchiveExecutionStatus,
    ArchiveFileOutcome,
    ArchivePlan,
    ArchivePlanningConfig,
    CollisionPolicy,
    DiscoveryClassification,
    ObservationCompatibility,
    ObservationReconstructionResult,
    ObservationStatus,
    PlannedArchiveObservation,
    PlannedFile,
    ReconstructedObservation,
    SeestarDiscoveryItem,
    SourceAction,
    SourceDirectoryContext,
    execute_archive_plan,
    execution,
    plan_seestar_archive,
    sha256_file,
)


def _plan(
    archive_root: Path,
    files: tuple[PlannedFile, ...],
    *,
    stack: PlannedFile | None = None,
) -> ArchivePlan:
    observation_directory = archive_root / "Target/unknown/20260903/observation_01"
    observation = PlannedArchiveObservation(
        reconstructed=cast(Any, None),
        metadata=cast(Any, None),
        hierarchy_directory=observation_directory.parent,
        observation_name="observation_01",
        observation_directory=observation_directory,
        lights_directory=observation_directory / "lights",
        seestar_stacked_directory=observation_directory / "seestar_stacked",
        tiff_directory=observation_directory / "tiff",
        lights=files,
        stack=stack,
    )
    return ArchivePlan(
        config=ArchivePlanningConfig(archive_root=archive_root),
        observations=(observation,),
        problems=(),
    )


def _file(source: Path, destination: Path) -> PlannedFile:
    return PlannedFile(
        source_path=source,
        fits_destination=destination,
        tiff_destination=destination.with_suffix(".tiff"),
    )


def test_execution_consumes_destination_from_real_planner_contract(tmp_path: Path) -> None:
    source_directory = tmp_path / "My Works/Target_sub"
    source_directory.mkdir(parents=True)
    source = source_directory / "Light.fit"
    source.write_bytes(b"planned source")
    item = SeestarDiscoveryItem(
        source_path=source,
        classification=DiscoveryClassification.LIGHT_FITS,
        source_directory=source_directory,
        directory_context=SourceDirectoryContext.SUB,
        directory_target="Target",
        metadata_target=None,
        fits_inspection=None,
    )
    captured_at = datetime(2026, 9, 3, 1, 0)
    observation = ReconstructedObservation(
        lights=(item,),
        stack=None,
        first_light_at=captured_at,
        last_light_at=captured_at,
        stack_at=None,
        status=ObservationStatus.LIGHTS_ONLY,
        compatibility=ObservationCompatibility("Target", 10, "LP", 0),
        reported_stack_count=None,
        problems=(),
    )
    archive_root = tmp_path / "archive"
    plan = plan_seestar_archive(
        ObservationReconstructionResult((observation,), ()), archive_root=archive_root
    )

    result = execute_archive_plan(plan)

    assert result.files[0].destination_path == plan.observations[0].lights[0].fits_destination
    assert result.files[0].destination_path.read_bytes() == b"planned source"


def test_copy_is_default_creates_parents_and_preserves_exact_source(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    content = bytes(range(256)) * 20
    source.write_bytes(content)
    archive_root = tmp_path / "archive"
    destination = archive_root / "Target/unknown/20260903/observation_01/lights/source.fit"

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert source.read_bytes() == content
    assert destination.read_bytes() == content
    assert result.action is SourceAction.COPY
    assert result.status is ArchiveExecutionStatus.COMPLETE
    assert result.copied_count == 1
    assert result.moved_count == result.skipped_count == result.failed_count == 0
    file_result = result.files[0]
    assert file_result.outcome is ArchiveFileOutcome.COPIED
    assert file_result.collision is ArchiveCollisionState.NONE
    assert file_result.source_path == source
    assert file_result.destination_path == destination
    assert file_result.source_sha256 == hashlib.sha256(content).hexdigest()
    assert file_result.destination_sha256 == file_result.source_sha256
    assert file_result.bytes_processed == len(content)


def test_move_must_be_explicit_and_removes_source_after_destination_success(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.fits"
    source.write_bytes(b"astronomical source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "Target/unknown/20260903/observation_01/lights/source.fits"

    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)), action=SourceAction.MOVE
    )

    assert not source.exists()
    assert destination.read_bytes() == b"astronomical source"
    assert result.files[0].outcome is ArchiveFileOutcome.MOVED
    assert result.moved_count == 1


def test_failed_destination_write_during_move_retains_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"

    def fail_write(*args, **kwargs) -> None:
        raise OSError("simulated write failure")

    monkeypatch.setattr(execution, "_stage_and_replace", fail_write)
    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)), action=SourceAction.MOVE
    )

    assert source.read_bytes() == b"source"
    assert not destination.exists()
    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "simulated write failure" in (result.files[0].diagnostic or "")


def test_move_source_delete_failure_is_explicit_partial_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    original_unlink = Path.unlink

    def guarded_unlink(path: Path, *args, **kwargs) -> None:
        if path == source:
            raise PermissionError("simulated source protection")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", guarded_unlink)
    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)), action=SourceAction.MOVE
    )

    assert source.read_bytes() == destination.read_bytes() == b"source"
    assert result.status is ArchiveExecutionStatus.PARTIAL
    assert result.failed_count == 1
    assert result.files[0].outcome is ArchiveFileOutcome.PARTIAL
    assert "source removal failed" in (result.files[0].diagnostic or "")


@pytest.mark.parametrize(
    ("source_kind", "expected"),
    [("missing", "does not exist"), ("directory", "regular file")],
)
def test_missing_or_non_regular_source_is_reported(
    tmp_path: Path, source_kind: str, expected: str
) -> None:
    source = tmp_path / "source.fit"
    if source_kind == "directory":
        source.mkdir()
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.status is ArchiveExecutionStatus.FAILED
    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert expected in (result.files[0].diagnostic or "")
    assert not archive_root.exists()


def test_source_and_destination_same_file_is_rejected(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    source = archive_root / "source.fit"
    source.write_bytes(b"source")

    result = execute_archive_plan(_plan(archive_root, (_file(source, source),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "same file" in (result.files[0].diagnostic or "")
    assert source.read_bytes() == b"source"


def test_source_and_destination_hardlink_identity_is_rejected(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    destination = archive_root / "source.fit"
    os.link(source, destination)

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "same file" in (result.files[0].diagnostic or "")
    assert source.read_bytes() == destination.read_bytes() == b"source"


def test_identical_destination_is_skipped_and_copy_rerun_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"identical")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    plan = _plan(archive_root, (_file(source, destination),))

    first = execute_archive_plan(plan)
    first_mtime = destination.stat().st_mtime_ns
    second = execute_archive_plan(plan)

    assert first.files[0].outcome is ArchiveFileOutcome.COPIED
    assert second.files[0].outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL
    assert second.files[0].collision is ArchiveCollisionState.IDENTICAL
    assert second.skipped_count == 1
    assert second.status is ArchiveExecutionStatus.COMPLETE
    assert destination.stat().st_mtime_ns == first_mtime
    assert source.exists()


def test_move_with_identical_destination_safely_retains_source(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"identical")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"identical")

    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)), action=SourceAction.MOVE
    )

    assert result.files[0].outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL
    assert source.exists()


def test_error_policy_reports_even_identical_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"identical")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"identical")

    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)),
        collision_policy=CollisionPolicy.ERROR,
    )

    assert result.files[0].outcome is ArchiveFileOutcome.COLLISION
    assert source.read_bytes() == destination.read_bytes() == b"identical"


def test_same_size_different_content_is_never_overwritten_by_default(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"target")

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.COLLISION
    assert result.files[0].collision is ArchiveCollisionState.DIFFERENT
    assert source.read_bytes() == b"source"
    assert destination.read_bytes() == b"target"


def test_explicit_overwrite_replaces_different_content_safely(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"new source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"old target")

    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)),
        collision_policy=CollisionPolicy.OVERWRITE,
    )

    assert result.files[0].outcome is ArchiveFileOutcome.COPIED
    assert result.files[0].collision is ArchiveCollisionState.DIFFERENT
    assert source.read_bytes() == destination.read_bytes() == b"new source"


def test_explicit_move_overwrite_removes_source_only_after_replacement(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"new source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"old target")

    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)),
        action=SourceAction.MOVE,
        collision_policy=CollisionPolicy.OVERWRITE,
    )

    assert result.files[0].outcome is ArchiveFileOutcome.MOVED
    assert not source.exists()
    assert destination.read_bytes() == b"new source"


def test_failed_explicit_overwrite_preserves_previous_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"new source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"old target")

    def fail_replace(*args, **kwargs) -> None:
        raise OSError("simulated atomic replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    result = execute_archive_plan(
        _plan(archive_root, (_file(source, destination),)),
        action=SourceAction.MOVE,
        collision_policy=CollisionPolicy.OVERWRITE,
    )

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert result.files[0].collision is ArchiveCollisionState.DIFFERENT
    assert source.read_bytes() == b"new source"
    assert destination.read_bytes() == b"old target"
    assert not tuple(destination.parent.glob(".source.fit.tmp-*"))


def test_sha256_reads_in_bounded_chunks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "source.fit"
    content = b"stream this content"
    source.write_bytes(content)
    original_open = Path.open
    read_sizes: list[int] = []

    class ReadSpy:
        def __init__(self, wrapped) -> None:
            self.wrapped = wrapped

        def __enter__(self):
            self.wrapped.__enter__()
            return self

        def __exit__(self, *args):
            return self.wrapped.__exit__(*args)

        def read(self, size: int = -1):
            read_sizes.append(size)
            return self.wrapped.read(size)

    def spy_open(path: Path, *args, **kwargs):
        return ReadSpy(original_open(path, *args, **kwargs))

    monkeypatch.setattr(Path, "open", spy_open)

    assert sha256_file(source, chunk_size=4) == hashlib.sha256(content).hexdigest()
    assert read_sizes
    assert set(read_sizes) == {4}


def test_forged_destination_outside_root_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    outside = tmp_path / "outside/source.fit"

    result = execute_archive_plan(_plan(archive_root, (_file(source, outside),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "escapes archive root" in (result.files[0].diagnostic or "")
    assert not outside.exists()


def test_destination_symlink_escape_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    outside = tmp_path / "outside"
    archive_root.mkdir()
    outside.mkdir()
    (archive_root / "linked").symlink_to(outside, target_is_directory=True)
    destination = archive_root / "linked/source.fit"

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "escapes archive root" in (result.files[0].diagnostic or "")
    assert not (outside / "source.fit").exists()


def test_existing_non_directory_parent_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    parent = archive_root / "not-a-directory"
    parent.write_bytes(b"file")
    destination = parent / "source.fit"

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert source.exists()


def test_failed_staged_verification_leaves_no_destination_or_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    real_hash = execution.sha256_file

    def mismatched_temporary_hash(path: Path, **kwargs) -> str:
        if path.name.startswith(".source.fit.tmp-"):
            return "not-the-source-hash"
        return real_hash(path, **kwargs)

    monkeypatch.setattr(execution, "sha256_file", mismatched_temporary_hash)
    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert source.exists()
    assert not destination.exists()
    assert not tuple(destination.parent.glob(".source.fit.tmp-*"))


def test_light_and_stack_originals_execute_but_tiff_plans_do_not(tmp_path: Path) -> None:
    light = tmp_path / "Light.fit"
    stack = tmp_path / "Stacked.fits"
    light.write_bytes(b"light")
    stack.write_bytes(b"stack")
    archive_root = tmp_path / "archive"
    observation = archive_root / "Target/unknown/20260903/observation_01"
    light_plan = _file(light, observation / "lights/Light.fit")
    stack_plan = _file(stack, observation / "seestar_stacked/Stacked.fits")

    result = execute_archive_plan(_plan(archive_root, (light_plan,), stack=stack_plan))

    assert result.copied_count == 2
    assert light_plan.fits_destination.read_bytes() == b"light"
    assert stack_plan.fits_destination.read_bytes() == b"stack"
    assert not light_plan.tiff_destination.exists()
    assert not stack_plan.tiff_destination.exists()
    assert not (observation / "tiff").exists()
    assert not tuple(archive_root.rglob("INDEX.md"))


def test_forged_jpeg_source_is_not_executed(tmp_path: Path) -> None:
    source = tmp_path / "preview.jpg"
    source.write_bytes(b"jpeg")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/preview.jpg"

    result = execute_archive_plan(_plan(archive_root, (_file(source, destination),)))

    assert result.files[0].outcome is ArchiveFileOutcome.FAILED
    assert source.exists()
    assert not archive_root.exists()


def test_independent_operations_continue_and_report_partial_completion(tmp_path: Path) -> None:
    valid = tmp_path / "valid.fit"
    valid.write_bytes(b"valid")
    missing = tmp_path / "missing.fit"
    archive_root = tmp_path / "archive"
    valid_destination = archive_root / "safe/valid.fit"
    missing_destination = archive_root / "safe/missing.fit"

    result = execute_archive_plan(
        _plan(
            archive_root,
            (_file(valid, valid_destination), _file(missing, missing_destination)),
        )
    )

    assert [item.outcome for item in result.files] == [
        ArchiveFileOutcome.COPIED,
        ArchiveFileOutcome.FAILED,
    ]
    assert result.status is ArchiveExecutionStatus.PARTIAL
    assert result.copied_count == result.failed_count == 1
    assert valid_destination.read_bytes() == b"valid"
    assert not missing_destination.exists()


def test_stale_move_plan_reports_missing_source_after_success(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"source")
    archive_root = tmp_path / "archive"
    destination = archive_root / "safe/source.fit"
    plan = _plan(archive_root, (_file(source, destination),))

    first = execute_archive_plan(plan, action=SourceAction.MOVE)
    second = execute_archive_plan(plan, action=SourceAction.MOVE)

    assert first.files[0].outcome is ArchiveFileOutcome.MOVED
    assert second.files[0].outcome is ArchiveFileOutcome.FAILED
    assert "does not exist" in (second.files[0].diagnostic or "")


def test_unplanned_problems_create_no_directories(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    plan = ArchivePlan(
        config=ArchivePlanningConfig(archive_root=archive_root),
        observations=(),
        problems=(cast(Any, object()),),
    )

    result = execute_archive_plan(plan)

    assert result.files == ()
    assert result.status is ArchiveExecutionStatus.COMPLETE
    assert not archive_root.exists()


def test_invalid_policy_types_are_rejected_before_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path / "archive", ())

    with pytest.raises(ArchiveExecutionError, match="SourceAction"):
        execute_archive_plan(plan, action=cast(Any, "move"))
    with pytest.raises(ArchiveExecutionError, match="CollisionPolicy"):
        execute_archive_plan(plan, collision_policy=cast(Any, "overwrite"))
