"""Integration tests for library-level Seestar archive orchestration."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
import tifffile
from astropy.io import fits

from seestar_toolkit import cli
from seestar_toolkit.archive import (
    ArchiveConfig,
    ArchiveFileOutcome,
    ArchiveIndexOutcome,
    ArchiveTiffOutcome,
    CollisionPolicy,
    ObservationStatus,
    SavedLocation,
    SeestarArchiveStatus,
    SourceAction,
    archive_seestar_session,
    discover_seestar_inputs,
    execute_archive_plan,
    indexing,
    orchestration,
    plan_seestar_archive,
    reconstruct_seestar_observations,
)
from seestar_toolkit.conversion import convert_fits_to_tiff

CAPTURED_AT = datetime(2026, 9, 3, 1, 0)
REAL_DATA = Path(__file__).parents[1] / "data/seestar"


def _header(*, captured_at: datetime, total_exposure: float | None = None) -> fits.Header:
    header = fits.Header()
    header["IMAGETYP"] = "Light"
    header["OBJECT"] = "Target"
    header["EXPTIME"] = 10.0
    header["FILTER"] = "LP"
    header["DATE-OBS"] = captured_at.isoformat()
    header["EQMODE"] = 0
    header["TELESCOP"] = "S50_12345678"
    header["SITELAT"] = 51.4
    header["SITELONG"] = -0.7
    if total_exposure is not None:
        header["TOTALEXP"] = total_exposure
    return header


def _write_raw(path: Path, captured_at: datetime = CAPTURED_AT) -> None:
    header = _header(captured_at=captured_at)
    header["BAYERPAT"] = "GRBG"
    mosaic = np.arange(80, dtype=np.uint16).reshape(8, 10) * 100
    fits.writeto(path, mosaic, header=header)


def _write_stack(path: Path, captured_at: datetime = CAPTURED_AT + timedelta(seconds=12)) -> None:
    header = _header(captured_at=captured_at, total_exposure=10.0)
    rgb_planes = np.stack(
        (
            np.full((8, 10), 1000, dtype=np.uint16),
            np.full((8, 10), 2000, dtype=np.uint16),
            np.full((8, 10), 3000, dtype=np.uint16),
        )
    )
    fits.writeto(path, rgb_planes, header=header)


def _source_tree(tmp_path: Path, *, light_count: int = 1, include_stack: bool = True):
    root = tmp_path / "My Works"
    product = root / "Target"
    lights = root / "Target_sub"
    product.mkdir(parents=True)
    lights.mkdir()
    light_paths = []
    for index in range(light_count):
        captured_at = CAPTURED_AT + timedelta(seconds=index * 11)
        path = lights / f"Light_{index + 1}_Target_20260903-0100{index:02d}.fit"
        _write_raw(path, captured_at)
        light_paths.append(path)
    stack_path = None
    if include_stack:
        stack_at = CAPTURED_AT + timedelta(seconds=light_count * 11 + 1)
        stack_path = product / "Stacked_1_Target_20260903-010030.fit"
        _write_stack(stack_path, stack_at)
    return root, tuple(light_paths), stack_path


def _planned(root: Path, archive_root: Path):
    discovery = discover_seestar_inputs(root)
    reconstruction = reconstruct_seestar_observations(discovery)
    return plan_seestar_archive(reconstruction, archive_root=archive_root)


def _fingerprint(path: Path) -> tuple[int, str]:
    content = path.read_bytes()
    return len(content), hashlib.sha256(content).hexdigest()


def test_real_seestar_copy_cli_reopens_tiffs_and_verifies_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    lights = root / "IC 434_sub"
    product.mkdir(parents=True)
    lights.mkdir()
    source_light = lights / "Light_IC 434.fit"
    source_stack = product / "Stacked_195_IC 434.fit"
    shutil.copyfile(REAL_DATA / "light.fit", source_light)
    shutil.copyfile(REAL_DATA / "stacked.fit", source_stack)
    jpeg = product / "Stacked_195_IC 434.jpg"
    jpeg.write_bytes(b"representative jpeg remains untouched")
    before = {path: _fingerprint(path) for path in (source_light, source_stack, jpeg)}
    archive_root = tmp_path / "archive"
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: ArchiveConfig())

    status = cli.main(["archive", str(root), str(archive_root), "--non-interactive"])

    assert status == 0
    assert {path: _fingerprint(path) for path in before} == before
    archived_light = next(archive_root.rglob("lights/*.fit"))
    archived_stack = next(archive_root.rglob("seestar_stacked/*.fit"))
    assert _fingerprint(archived_light) == _fingerprint(source_light)
    assert _fingerprint(archived_stack) == _fingerprint(source_stack)
    light_tiff = tifffile.imread(next(archive_root.rglob("tiff/*.tiff")))
    stack_tiff = tifffile.imread(next(archive_root.rglob("seestar_stacked/*.tiff")))
    assert light_tiff.shape == (1920, 1080, 3)
    assert stack_tiff.shape == (3840, 2160, 3)
    assert light_tiff.dtype == stack_tiff.dtype == np.uint16
    index = (archive_root / "IC 434/INDEX.md").read_text()
    assert "# IC 434" in index
    assert "### Observation 01" in index
    assert "S50_00000001" in index
    assert "Light subs: 1" in index
    assert "Stacked_195_IC 434.fit" in index
    assert "Seestar stack count: 195" in index
    assert "Archive complete" in capsys.readouterr().out


def test_full_copy_workflow_generates_raw_light_and_native_stack_tiffs(
    tmp_path: Path,
) -> None:
    root, lights, stack = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    jpeg = root / "Target/Stacked_1_Target.jpg"
    jpeg.write_bytes(b"jpeg remains ignored")
    before = {path: _fingerprint(path) for path in (*lights, stack, jpeg)}

    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.status is SeestarArchiveStatus.COMPLETE
    assert result.execution.copied_count == 2
    assert all(item.outcome is ArchiveTiffOutcome.CREATED for item in result.tiffs)
    planned = result.plan.observations[0]
    assert result.tiffs[0].tiff_destination == planned.lights[0].tiff_destination
    assert result.tiffs[1].tiff_destination == planned.stack.tiff_destination
    assert planned.lights[0].tiff_destination.parent.name == "tiff"
    assert planned.stack.tiff_destination.parent.name == "seestar_stacked"
    raw_tiff = tifffile.imread(planned.lights[0].tiff_destination)
    stack_tiff = tifffile.imread(planned.stack.tiff_destination)
    assert raw_tiff.shape == stack_tiff.shape == (8, 10, 3)
    assert raw_tiff.dtype == stack_tiff.dtype == np.uint16
    assert {path: _fingerprint(path) for path in (*lights, stack, jpeg)} == before
    assert tuple(archive_root.rglob("INDEX.md")) == (archive_root / "Target/INDEX.md",)


def test_target_index_contains_required_structured_metadata(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"

    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.indexes[0].outcome is ArchiveIndexOutcome.CREATED
    content = result.indexes[0].index_path.read_text()
    assert content == (
        "# Target\n\n"
        "## unknown — 2026-09-03\n\n"
        "### Observation 01\n\n"
        "- Telescope: S50_12345678\n"
        "- First light: 2026-09-03 01:00:00\n"
        "- Last light: 2026-09-03 01:00:00\n"
        "- Exposure: 10.0 s\n"
        "- Filter: LP\n"
        "- Light subs: 1\n"
        "- Seestar stack: Stacked_1_Target_20260903-010030.fit\n"
        "- Seestar stack count: 1\n"
        "- Capture mode: Alt-Az\n"
        "- GPS: 51.400000, -0.700000\n"
    )


def test_index_placement_follows_alternative_hierarchy(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"

    result = archive_seestar_session(
        root,
        archive_root=archive_root,
        hierarchy_template="{location}/{session_end_date}/{target}",
        explicit_location="Home",
    )

    assert result.indexes[0].index_path == archive_root / "Home/20260903/Target/INDEX.md"
    assert result.indexes[0].index_path.is_file()


def test_index_rerun_is_unchanged_and_does_not_duplicate_observation(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)
    content = first.indexes[0].index_path.read_bytes()

    second = archive_seestar_session(root, archive_root=archive_root)

    assert second.indexes[0].outcome is ArchiveIndexOutcome.UNCHANGED
    assert second.indexes[0].index_path.read_bytes() == content
    assert content.count(b"### Observation 01") == 1


def test_index_failure_is_partial_and_preserves_previous_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)
    index_path = first.indexes[0].index_path
    index_path.write_text("previous index\n")

    monkeypatch.setattr(indexing.os, "replace", Mock(side_effect=OSError("replace failed")))
    second = archive_seestar_session(root, archive_root=archive_root)

    assert second.indexes[0].outcome is ArchiveIndexOutcome.FAILED
    assert second.status is SeestarArchiveStatus.PARTIAL
    assert index_path.read_text() == "previous index\n"
    assert all(item.destination_path.exists() for item in second.execution.files)
    assert all(item.tiff_destination.exists() for item in first.tiffs)
    assert not tuple(index_path.parent.glob(".INDEX.md.*.tmp"))


def test_move_archives_originals_before_tiff_generation(tmp_path: Path) -> None:
    root, lights, stack = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    original_content = {path.name: path.read_bytes() for path in (*lights, stack)}

    result = archive_seestar_session(
        root,
        archive_root=archive_root,
        source_action=SourceAction.MOVE,
    )

    assert result.status is SeestarArchiveStatus.COMPLETE
    assert result.execution.moved_count == 2
    assert not any(path.exists() for path in (*lights, stack))
    assert all(item.archived_fits_path.exists() for item in result.tiffs)
    assert {
        item.destination_path.name: item.destination_path.read_bytes()
        for item in result.execution.files
    } == original_content
    assert all(item.tiff_destination.exists() for item in result.tiffs)


def test_incremental_real_archive_allocates_next_observation_and_preserves_history(
    tmp_path: Path,
) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)

    later_root = tmp_path / "Later Works"
    product = later_root / "Target"
    lights = later_root / "Target_sub"
    product.mkdir(parents=True)
    lights.mkdir()
    _write_raw(
        lights / "Light_2_Target_20260903-020000.fit",
        CAPTURED_AT + timedelta(hours=1),
    )
    _write_stack(
        product / "Stacked_1_Target_20260903-020012.fit",
        CAPTURED_AT + timedelta(hours=1, seconds=12),
    )

    second = archive_seestar_session(later_root, archive_root=archive_root)

    assert first.plan.observations[0].observation_name == "observation_01"
    assert second.plan.observations[0].observation_name == "observation_02"
    assert (archive_root / "Target/unknown/20260903/observation_01").is_dir()
    assert (archive_root / "Target/unknown/20260903/observation_02").is_dir()
    content = (archive_root / "Target/INDEX.md").read_text()
    assert content.count("### Observation 01") == 1
    assert content.count("### Observation 02") == 1


def test_lights_only_and_stack_only_workflows_do_not_invent_missing_frames(
    tmp_path: Path,
) -> None:
    lights_root, _, _ = _source_tree(tmp_path / "lights-case", include_stack=False)
    lights_result = archive_seestar_session(lights_root, archive_root=tmp_path / "lights-archive")

    stack_root = tmp_path / "stack-case/My Works"
    product = stack_root / "Target"
    product.mkdir(parents=True)
    _write_stack(product / "Stacked_3_Target_20260903-010012.fit")
    stack_result = archive_seestar_session(stack_root, archive_root=tmp_path / "stack-archive")

    assert lights_result.status is SeestarArchiveStatus.COMPLETE
    assert lights_result.plan.observations[0].stack is None
    assert "Seestar stack: none" in lights_result.indexes[0].index_path.read_text()
    assert stack_result.status is SeestarArchiveStatus.COMPLETE
    assert stack_result.plan.observations[0].lights == ()
    assert "Light subs: 0" in stack_result.indexes[0].index_path.read_text()
    assert "Stacked_3_Target" in stack_result.indexes[0].index_path.read_text()


def test_multiple_observations_have_separate_outputs_and_one_complete_index(
    tmp_path: Path,
) -> None:
    root = tmp_path / "My Works"
    product = root / "Target"
    lights = root / "Target_sub"
    product.mkdir(parents=True)
    lights.mkdir()
    for number, offset in ((1, 0), (2, 3600)):
        captured = CAPTURED_AT + timedelta(seconds=offset)
        _write_raw(lights / f"Light_{number}_Target_20260903-0{number}0000.fit", captured)
        _write_stack(
            product / f"Stacked_1_Target_20260903-0{number}0012.fit",
            captured + timedelta(seconds=12),
        )

    result = archive_seestar_session(root, archive_root=tmp_path / "archive")

    assert result.status is SeestarArchiveStatus.COMPLETE
    assert [item.observation_name for item in result.plan.observations] == [
        "observation_01",
        "observation_02",
    ]
    assert all(item.observation_directory.is_dir() for item in result.plan.observations)
    assert len(result.tiffs) == 4
    assert all(item.tiff_destination.is_file() for item in result.tiffs)
    content = result.indexes[0].index_path.read_text()
    assert content.count("### Observation") == 2


def test_archive_cli_dry_run_plans_without_any_filesystem_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, lights, stack = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    jpeg = root / "Target/preview.jpg"
    jpeg.write_bytes(b"untouched jpeg")
    sources = (*lights, stack, jpeg)
    before = {path: (_fingerprint(path), path.stat().st_mtime_ns) for path in sources}
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: ArchiveConfig())

    status = cli.main(["archive", str(root), str(archive_root), "--dry-run", "--non-interactive"])

    assert status == 0
    assert not archive_root.exists()
    assert {path: (_fingerprint(path), path.stat().st_mtime_ns) for path in sources} == before
    assert not tuple(tmp_path.rglob("*.tiff"))
    assert not tuple(tmp_path.rglob("*.tmp"))
    assert not tuple(tmp_path.rglob("INDEX.md"))
    output = capsys.readouterr().out
    assert "Plan observation_01" in output
    assert "target=Target" in output
    assert "location=unknown" in output
    assert "FITS" in output and "TIFF" in output
    assert f"Index: {archive_root / 'Target/INDEX.md'}" in output


@pytest.mark.parametrize(
    ("arguments", "source_exists", "summary"),
    [([], True, "2 copied"), (["--source-action", "move"], False, "2 moved")],
)
def test_archive_cli_real_copy_and_move_workflows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
    source_exists: bool,
    summary: str,
) -> None:
    root, lights, stack = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: ArchiveConfig())

    status = cli.main(["archive", str(root), str(archive_root), "--non-interactive", *arguments])

    assert status == 0
    assert all(path.exists() is source_exists for path in (*lights, stack))
    assert len(tuple(archive_root.rglob("*.fit"))) == 2
    assert len(tuple(archive_root.rglob("*.tiff"))) == 2
    output = capsys.readouterr().out
    assert summary in output
    assert tuple(archive_root.rglob("INDEX.md")) == (archive_root / "Target/INDEX.md",)
    assert "Indexes: 1 created" in output


@pytest.mark.parametrize(
    ("answers", "expected_location"),
    [([""], "Warfield"), (["n", "  Manual Site  "], "Manual Site"), (["n", ""], "unknown")],
)
def test_archive_cli_interactive_saved_match_accept_reject_or_unknown(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    answers: list[str],
    expected_location: str,
) -> None:
    root, _, _ = _source_tree(tmp_path)
    config = ArchiveConfig(saved_locations=(SavedLocation("Warfield", 51.4, -0.7, 100),))
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: config)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    prompt = Mock(side_effect=answers)
    monkeypatch.setattr("builtins.input", prompt)

    status = cli.main(["archive", str(root), str(tmp_path / "archive"), "--dry-run"])

    assert status == 0
    assert f"location={expected_location}" in capsys.readouterr().out
    assert prompt.call_count == len(answers)


@pytest.mark.parametrize(
    ("extra_arguments", "expected_location"),
    [([], "Warfield"), (["--location", "Explicit Place"], "Explicit Place")],
)
def test_archive_cli_noninteractive_saved_match_and_explicit_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    extra_arguments: list[str],
    expected_location: str,
) -> None:
    root, _, _ = _source_tree(tmp_path)
    config = ArchiveConfig(saved_locations=(SavedLocation("Warfield", 51.4, -0.7, 100),))
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: config)
    prompt = Mock(side_effect=AssertionError("must not prompt"))
    monkeypatch.setattr("builtins.input", prompt)

    status = cli.main(
        [
            "archive",
            str(root),
            str(tmp_path / "archive"),
            "--dry-run",
            "--non-interactive",
            *extra_arguments,
        ]
    )

    assert status == 0
    assert f"location={expected_location}" in capsys.readouterr().out
    prompt.assert_not_called()


def test_archive_cli_loads_real_config_and_cli_location_overrides_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _, _ = _source_tree(tmp_path)
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[archive]
hierarchy = "{location}/{session_end_date}/{target}"
source_action = "move"
collision_policy = "error"

[[locations]]
name = "GPS Home"
latitude = 51.4
longitude = -0.7
radius_m = 100
""".strip()
    )

    saved_status = cli.main(
        [
            "archive",
            str(root),
            str(tmp_path / "saved-archive"),
            "--config",
            str(config_path),
            "--dry-run",
            "--non-interactive",
        ]
    )
    saved_output = capsys.readouterr().out
    explicit_status = cli.main(
        [
            "archive",
            str(root),
            str(tmp_path / "explicit-archive"),
            "--config",
            str(config_path),
            "--location",
            "CLI Place",
            "--collision-policy",
            "skip-identical",
            "--dry-run",
            "--non-interactive",
        ]
    )
    explicit_output = capsys.readouterr().out

    assert saved_status == explicit_status == 0
    assert "location=GPS Home" in saved_output
    assert "saved-archive/GPS Home/20260903/Target" in saved_output
    assert "action=move" in saved_output
    assert "collision=error" in saved_output
    assert "location=CLI Place" in explicit_output
    assert "explicit-archive/CLI Place/20260903/Target" in explicit_output
    assert "collision=skip_identical" in explicit_output


def test_archive_cli_empty_and_malformed_workflows_have_established_exit_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: ArchiveConfig())
    empty = tmp_path / "empty"
    empty.mkdir()

    assert (
        cli.main(["archive", str(empty), str(tmp_path / "empty-archive"), "--non-interactive"]) == 0
    )
    assert not (tmp_path / "empty-archive").exists()

    malformed = tmp_path / "malformed"
    malformed.mkdir()
    (malformed / "broken.fit").write_text("not a FITS file")
    status = cli.main(
        ["archive", str(malformed), str(tmp_path / "bad-archive"), "--non-interactive"]
    )

    assert status == 1
    assert "Archive failed" in capsys.readouterr().out
    assert not (tmp_path / "bad-archive").exists()


def test_archive_cli_partial_result_returns_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    monkeypatch.setattr(cli, "load_archive_config", lambda path=None: ArchiveConfig())
    arguments = ["archive", str(root), str(archive_root), "--non-interactive"]

    assert cli.main(arguments) == 0
    assert cli.main(arguments) == 1
    content = (archive_root / "Target/INDEX.md").read_text()
    assert content.count("### Observation 01") == 1


def test_identical_archived_fits_can_generate_missing_tiffs(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)
    for item in first.tiffs:
        item.tiff_destination.unlink()

    second = archive_seestar_session(root, archive_root=archive_root)

    assert second.execution.skipped_count == 2
    assert all(
        item.original_execution.outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL
        for item in second.tiffs
    )
    assert all(item.outcome is ArchiveTiffOutcome.CREATED for item in second.tiffs)
    assert second.status is SeestarArchiveStatus.COMPLETE


def test_original_collision_is_ineligible_for_tiff(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    plan = _planned(root, archive_root)
    planned_file = plan.observations[0].lights[0]
    planned_file.fits_destination.parent.mkdir(parents=True)
    planned_file.fits_destination.write_bytes(b"different archived FITS")

    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.execution.files[0].outcome is ArchiveFileOutcome.COLLISION
    assert result.tiffs[0].outcome is ArchiveTiffOutcome.INELIGIBLE
    assert not planned_file.tiff_destination.exists()
    assert result.status is SeestarArchiveStatus.FAILED


def test_explicit_overwrite_replaces_different_fits_via_existing_safe_path(
    tmp_path: Path,
) -> None:
    root, lights, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)
    destination = first.execution.files[0].destination_path
    lights[0].unlink()
    header = _header(captured_at=CAPTURED_AT)
    header["BAYERPAT"] = "GRBG"
    fits.writeto(lights[0], np.full((8, 10), 4321, dtype=np.uint16), header=header)
    replacement = lights[0].read_bytes()

    second = archive_seestar_session(
        root,
        archive_root=archive_root,
        collision_policy=CollisionPolicy.OVERWRITE,
    )

    assert second.execution.files[0].outcome is ArchiveFileOutcome.COPIED
    assert destination.read_bytes() == replacement
    assert lights[0].read_bytes() == replacement
    assert second.tiffs[0].outcome is ArchiveTiffOutcome.COLLISION
    assert second.indexes[0].outcome in {
        ArchiveIndexOutcome.UPDATED,
        ArchiveIndexOutcome.UNCHANGED,
    }
    assert second.status is SeestarArchiveStatus.PARTIAL


def test_failed_original_archive_operation_does_not_generate_tiff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    real_execute = execute_archive_plan

    def remove_source_then_execute(plan, **kwargs):
        plan.observations[0].lights[0].source_path.unlink()
        return real_execute(plan, **kwargs)

    monkeypatch.setattr(orchestration, "execute_archive_plan", remove_source_then_execute)
    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.execution.files[0].outcome is ArchiveFileOutcome.FAILED
    assert result.tiffs[0].outcome is ArchiveTiffOutcome.INELIGIBLE
    assert not result.tiffs[0].tiff_destination.exists()
    assert result.status is SeestarArchiveStatus.FAILED


def test_existing_tiff_is_preserved_and_reported(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)
    destination = first.tiffs[0].tiff_destination
    before = _fingerprint(destination)

    second = archive_seestar_session(root, archive_root=archive_root)

    assert second.execution.files[0].outcome is ArchiveFileOutcome.SKIPPED_IDENTICAL
    assert second.tiffs[0].outcome is ArchiveTiffOutcome.COLLISION
    assert _fingerprint(destination) == before
    assert second.status is SeestarArchiveStatus.PARTIAL


def test_tiff_failure_after_move_preserves_archived_fits_without_restoring_source(
    tmp_path: Path,
) -> None:
    root, lights, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    plan = _planned(root, archive_root)
    tiff_destination = plan.observations[0].lights[0].tiff_destination
    tiff_destination.parent.mkdir(parents=True)
    tiff_destination.write_bytes(b"existing TIFF")

    result = archive_seestar_session(
        root,
        archive_root=archive_root,
        source_action=SourceAction.MOVE,
    )

    assert result.execution.files[0].outcome is ArchiveFileOutcome.MOVED
    assert result.tiffs[0].outcome is ArchiveTiffOutcome.COLLISION
    assert result.tiffs[0].archived_fits_path.exists()
    assert not lights[0].exists()
    assert tiff_destination.read_bytes() == b"existing TIFF"
    assert result.indexes[0].outcome is ArchiveIndexOutcome.CREATED
    assert "### Observation 01" in result.indexes[0].index_path.read_text()
    assert result.status is SeestarArchiveStatus.PARTIAL


def test_independent_tiff_generation_continues_after_conversion_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, _ = _source_tree(tmp_path, light_count=2)
    archive_root = tmp_path / "archive"
    real_convert = convert_fits_to_tiff

    def fail_first_light(input_path: Path, output_path: Path) -> Path:
        if input_path.name.startswith("Light_1_"):
            raise ValueError("simulated conversion failure")
        return real_convert(input_path, output_path)

    monkeypatch.setattr(orchestration, "convert_fits_to_tiff", fail_first_light)
    result = archive_seestar_session(root, archive_root=archive_root)

    assert [item.outcome for item in result.tiffs] == [
        ArchiveTiffOutcome.FAILED,
        ArchiveTiffOutcome.CREATED,
        ArchiveTiffOutcome.CREATED,
    ]
    assert all(item.archived_fits_path.exists() for item in result.tiffs)
    assert result.indexes[0].outcome is ArchiveIndexOutcome.CREATED
    assert "- Light subs: 2" in result.indexes[0].index_path.read_text()
    assert result.status is SeestarArchiveStatus.PARTIAL


def test_planning_ambiguity_remains_visible_and_unexecuted(tmp_path: Path) -> None:
    root, lights, _ = _source_tree(tmp_path, light_count=1, include_stack=False)
    second = root / "Target_sub/Light_2_Target_20260903-030000.fit"
    _write_raw(second, CAPTURED_AT + timedelta(hours=2))
    archive_root = tmp_path / "archive"

    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.reconstruction.observations[0].status is ObservationStatus.AMBIGUOUS
    assert result.plan.problems
    assert result.execution.files == result.tiffs == ()
    assert result.status is SeestarArchiveStatus.FAILED
    assert lights[0].exists() and second.exists()
    assert not archive_root.exists()


def test_empty_source_is_complete_without_creating_archive(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    root.mkdir()
    archive_root = tmp_path / "archive"

    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.discovery.items == ()
    assert result.reconstruction.observations == ()
    assert result.plan.observations == ()
    assert result.execution.files == result.tiffs == ()
    assert result.status is SeestarArchiveStatus.COMPLETE
    assert not archive_root.exists()


def test_malformed_fits_only_workflow_is_failed(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    root.mkdir()
    source = root / "broken.fit"
    source.write_text("not FITS")

    result = archive_seestar_session(root, archive_root=tmp_path / "archive")

    assert result.status is SeestarArchiveStatus.FAILED
    assert source.read_text() == "not FITS"


def test_forged_tiff_destination_escape_is_not_executed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    outside = tmp_path / "outside.tiff"
    real_plan = plan_seestar_archive

    def forge_tiff_destination(reconstruction, **kwargs):
        plan = real_plan(reconstruction, **kwargs)
        observation = plan.observations[0]
        forged_file = replace(observation.lights[0], tiff_destination=outside)
        forged_observation = replace(observation, lights=(forged_file,))
        return replace(plan, observations=(forged_observation,))

    monkeypatch.setattr(orchestration, "plan_seestar_archive", forge_tiff_destination)
    result = archive_seestar_session(root, archive_root=archive_root)

    assert result.execution.files[0].outcome is ArchiveFileOutcome.COPIED
    assert result.tiffs[0].outcome is ArchiveTiffOutcome.FAILED
    assert "escapes archive root" in (result.tiffs[0].diagnostic or "")
    assert not outside.exists()
    assert result.status is SeestarArchiveStatus.PARTIAL


def test_source_policies_are_passed_through_to_execution(tmp_path: Path) -> None:
    root, _, _ = _source_tree(tmp_path, include_stack=False)
    archive_root = tmp_path / "archive"
    first = archive_seestar_session(root, archive_root=archive_root)

    second = archive_seestar_session(
        root,
        archive_root=archive_root,
        collision_policy=CollisionPolicy.ERROR,
    )

    assert first.execution.action is SourceAction.COPY
    assert first.execution.collision_policy is CollisionPolicy.SKIP_IDENTICAL
    assert second.execution.collision_policy is CollisionPolicy.ERROR
    assert second.execution.files[0].outcome is ArchiveFileOutcome.COLLISION
    assert second.tiffs[0].outcome is ArchiveTiffOutcome.INELIGIBLE
