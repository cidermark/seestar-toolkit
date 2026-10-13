"""Tests for safe individual-light TIFF finalisation."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from seestar_toolkit.archive import (
    ArchiveCollisionState,
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    LightTiffCollisionDecision,
    LightTiffOutcome,
    SourceAction,
    finalise_archived_light_tiff,
    is_light_tiff_eligible,
    light_tiff,
)

DATA = Path(__file__).parents[2] / "data" / "seestar"


def _archived_light(tmp_path: Path, name: str = "Light.fit") -> tuple[Path, Path, Path]:
    archive_root = tmp_path / "archive"
    observation = archive_root / "Target/Home/20260903/observation_01"
    source = observation / "fits_images/lights" / name
    source.parent.mkdir(parents=True)
    shutil.copyfile(DATA / "light.fit", source)
    return archive_root, observation, source


def _finalise(
    archive_root: Path,
    observation: Path,
    source: Path,
    decision: LightTiffCollisionDecision | None = None,
):
    return finalise_archived_light_tiff(
        source,
        archive_root=archive_root,
        observation_directory=observation,
        decision=decision,
    )


def test_creates_primary_from_authoritative_archived_bayer_fits(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.CREATED
    assert result.tiff_destination == observation / "tiff_images/lights/Light.tiff"
    assert result.tiff_destination.is_file()
    assert source.is_file()
    assert not (observation / "tmp").exists()


def test_creates_primary_from_authoritative_archived_rgb_fits(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path, "Light.fits")
    shutil.copyfile(DATA / "stacked.fit", source)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.CREATED
    assert result.tiff_destination.is_file()


def test_identical_existing_primary_is_verified_and_preserved(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    first = _finalise(archive_root, observation, source)
    before = first.tiff_destination.read_bytes()

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.ALREADY_PRESENT
    assert first.tiff_destination.read_bytes() == before
    assert not (observation / "tmp").exists()


@pytest.mark.parametrize(
    ("decision", "outcome", "primary_expected", "duplicate_expected"),
    [
        (
            LightTiffCollisionDecision.KEEP_BOTH,
            LightTiffOutcome.DUPLICATE_CREATED,
            b"old",
            True,
        ),
        (
            LightTiffCollisionDecision.REPLACE_EXISTING,
            LightTiffOutcome.PRIMARY_REPLACED,
            None,
            False,
        ),
        (LightTiffCollisionDecision.SKIP, LightTiffOutcome.SKIPPED, b"old", False),
    ],
)
def test_differing_primary_uses_requested_engine_decision(
    tmp_path: Path,
    decision: LightTiffCollisionDecision,
    outcome: LightTiffOutcome,
    primary_expected: bytes | None,
    duplicate_expected: bool,
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old")

    result = _finalise(archive_root, observation, source, decision)

    duplicate = primary.with_name("Light.tiff.duplicate")
    assert result.outcome is outcome
    if primary_expected is not None:
        assert primary.read_bytes() == primary_expected
    else:
        assert primary.read_bytes() != b"old"
    assert duplicate.exists() is duplicate_expected
    assert not (observation / "tmp").exists()


@pytest.mark.parametrize(
    ("decision", "outcome", "duplicate_expected"),
    [
        (LightTiffCollisionDecision.REPLACE_DUPLICATE, LightTiffOutcome.DUPLICATE_REPLACED, None),
        (LightTiffCollisionDecision.SKIP, LightTiffOutcome.SKIPPED, b"old duplicate"),
    ],
)
def test_existing_duplicate_allows_only_replace_or_skip(
    tmp_path: Path,
    decision: LightTiffCollisionDecision,
    outcome: LightTiffOutcome,
    duplicate_expected: bytes | None,
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    duplicate = primary.with_name("Light.tiff.duplicate")
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old primary")
    duplicate.write_bytes(b"old duplicate")

    result = _finalise(archive_root, observation, source, decision)

    assert result.outcome is outcome
    assert primary.read_bytes() == b"old primary"
    if duplicate_expected is None:
        assert duplicate.read_bytes() != b"old duplicate"
    else:
        assert duplicate.read_bytes() == duplicate_expected
    assert not duplicate.with_name("Light.tiff.duplicate.2").exists()


def test_failed_conversion_preserves_fits_and_leaves_no_derivative_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    before = source.read_bytes()

    def fail_conversion(*_args) -> None:
        raise ValueError("bad")

    monkeypatch.setattr(light_tiff, "convert_fits_to_tiff", fail_conversion)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert source.read_bytes() == before
    assert not (observation / "tiff_images").exists()
    assert not (observation / "tmp").exists()


def test_failed_replacement_preserves_existing_primary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old")

    def fail_replace(*_args) -> None:
        raise OSError("no replace")

    monkeypatch.setattr(light_tiff.os, "replace", fail_replace)

    result = _finalise(
        archive_root, observation, source, LightTiffCollisionDecision.REPLACE_EXISTING
    )

    assert result.outcome is LightTiffOutcome.FAILED
    assert primary.read_bytes() == b"old"


def test_hash_failure_preserves_existing_primary_and_archived_fits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old")

    def fail_hash(_path: Path) -> str:
        raise OSError("no read")

    monkeypatch.setattr(light_tiff, "sha256_file", fail_hash)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert primary.read_bytes() == b"old"
    assert source.is_file()
    assert not (observation / "tmp").exists()


def test_failed_new_primary_promotion_rolls_back_created_derivative_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)

    def fail_link(*_args) -> None:
        raise OSError("no link")

    monkeypatch.setattr(light_tiff.os, "link", fail_link)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert "no link" in (result.diagnostic or "")
    assert source.is_file()
    assert not (observation / "tiff_images").exists()
    assert not (observation / "tmp").exists()


def test_successful_converter_without_candidate_creates_no_derivative_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    monkeypatch.setattr(light_tiff, "convert_fits_to_tiff", lambda *_args: None)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert source.is_file()
    assert not (observation / "tiff_images").exists()
    assert not (observation / "tmp").exists()


def test_failed_duplicate_replacement_preserves_primary_and_duplicate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    duplicate = primary.with_name("Light.tiff.duplicate")
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old primary")
    duplicate.write_bytes(b"old duplicate")

    def fail_replace(*_args) -> None:
        raise OSError("no duplicate replace")

    monkeypatch.setattr(light_tiff.os, "replace", fail_replace)
    result = _finalise(
        archive_root, observation, source, LightTiffCollisionDecision.REPLACE_DUPLICATE
    )

    assert result.outcome is LightTiffOutcome.FAILED
    assert primary.read_bytes() == b"old primary"
    assert duplicate.read_bytes() == b"old duplicate"
    assert source.is_file()


def test_candidate_cleanup_failure_is_reported_and_preserves_archived_fits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)

    def leave_partial_candidate(_source: Path, candidate: Path) -> None:
        candidate.write_bytes(b"partial")
        raise ValueError("conversion failed")

    def fail_cleanup(_candidate: Path) -> None:
        raise OSError("no unlink")

    monkeypatch.setattr(light_tiff, "convert_fits_to_tiff", leave_partial_candidate)
    monkeypatch.setattr(light_tiff, "_remove_candidate", fail_cleanup)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert "candidate cleanup failed: no unlink" in (result.diagnostic or "")
    assert source.is_file()
    assert (observation / "tmp").is_dir()


def test_engine_created_workspace_removal_failure_changes_success_to_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    workspace = observation / "tmp"
    original_rmdir = Path.rmdir

    def guarded_rmdir(path: Path) -> None:
        if path == workspace:
            raise OSError("no workspace removal")
        original_rmdir(path)

    monkeypatch.setattr(Path, "rmdir", guarded_rmdir)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert "workspace cleanup failed: no workspace removal" in (result.diagnostic or "")
    assert result.tiff_destination.is_file()
    assert source.is_file()
    assert workspace.is_dir()


def test_exact_owned_stale_candidate_is_cleaned_and_unknown_workspace_content_survives(
    tmp_path: Path,
) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    workspace = observation / "tmp"
    workspace.mkdir()
    stale = workspace / f".seestar-toolkit-enh003-{'0' * 32}.tiff"
    lookalike = workspace / ".seestar-toolkit-enh003-stale.tiff"
    unknown = workspace / "note.txt"
    unknown_directory = workspace / ".seestar-toolkit-enh003-directory.tiff"
    outside = tmp_path / "outside.txt"
    unknown_symlink = workspace / ".seestar-toolkit-enh003-symlink.tiff"
    stale.write_bytes(b"stale")
    lookalike.write_bytes(b"keep lookalike")
    unknown.write_text("keep")
    unknown_directory.mkdir()
    outside.write_text("outside")
    unknown_symlink.symlink_to(outside)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.CREATED
    assert not stale.exists()
    assert lookalike.read_bytes() == b"keep lookalike"
    assert unknown.read_text() == "keep"
    assert unknown_directory.is_dir()
    assert unknown_symlink.is_symlink()
    assert outside.read_text() == "outside"
    assert workspace.is_dir()


def test_primary_destination_symlink_is_rejected_without_following_it(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    outside = tmp_path / "outside-primary.tiff"
    outside.write_bytes(b"outside primary")
    primary.parent.mkdir(parents=True)
    primary.symlink_to(outside)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert primary.is_symlink()
    assert outside.read_bytes() == b"outside primary"
    assert source.is_file()


def test_duplicate_destination_symlink_is_rejected_without_following_it(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    primary = observation / "tiff_images/lights/Light.tiff"
    duplicate = primary.with_name("Light.tiff.duplicate")
    outside = tmp_path / "outside-duplicate.tiff"
    primary.parent.mkdir(parents=True)
    primary.write_bytes(b"old primary")
    outside.write_bytes(b"outside duplicate")
    duplicate.symlink_to(outside)

    result = _finalise(
        archive_root, observation, source, LightTiffCollisionDecision.REPLACE_DUPLICATE
    )

    assert result.outcome is LightTiffOutcome.FAILED
    assert primary.read_bytes() == b"old primary"
    assert duplicate.is_symlink()
    assert outside.read_bytes() == b"outside duplicate"
    assert source.is_file()


def test_workspace_symlink_is_rejected_without_following_it(tmp_path: Path) -> None:
    archive_root, observation, source = _archived_light(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (observation / "tmp").symlink_to(outside, target_is_directory=True)

    result = _finalise(archive_root, observation, source)

    assert result.outcome is LightTiffOutcome.FAILED
    assert not tuple(outside.iterdir())
    assert source.is_file()


def test_only_verified_move_deletion_partial_is_eligible() -> None:
    base = dict(
        source_path=Path("/source.fit"),
        destination_path=Path("/archive.fit"),
        requested_action=SourceAction.MOVE,
        collision=ArchiveCollisionState.NONE,
    )

    assert is_light_tiff_eligible(
        ArchiveFileExecutionResult(
            **base,
            outcome=ArchiveFileOutcome.PARTIAL,
            destination_established=True,
        )
    )
    assert not is_light_tiff_eligible(
        ArchiveFileExecutionResult(**base, outcome=ArchiveFileOutcome.PARTIAL)
    )
