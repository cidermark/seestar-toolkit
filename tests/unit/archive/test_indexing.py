"""Focused tests for derived target-level archive indexes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.archive import (
    ArchiveCollisionState,
    ArchiveExecutionResult,
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    ArchiveIndexOutcome,
    ArchivePlan,
    ArchivePlanningConfig,
    CollisionPolicy,
    ObservationArchiveMetadata,
    PlannedArchiveObservation,
    SourceAction,
    generate_archive_indexes,
    indexing,
    planned_index_paths,
)


def _planned_observation(
    archive_root: Path,
    *,
    target: str = "Target",
    location: str = "Home",
    date: str = "20260903",
    observation_name: str = "observation_01",
    hierarchy: str = "{target}/{location}/{session_end_date}",
) -> PlannedArchiveObservation:
    values = {"{target}": target, "{location}": location, "{session_end_date}": date}
    hierarchy_directory = archive_root.joinpath(*(values[item] for item in hierarchy.split("/")))
    observation_directory = hierarchy_directory / observation_name
    return PlannedArchiveObservation(
        reconstructed=Mock(),
        metadata=ObservationArchiveMetadata(
            logical_target=target,
            target_component=target,
            logical_location=location,
            location_component=location,
            source_latitude=None,
            source_longitude=None,
            session_end_date=date,
            telescope=None,
            diagnostics=(),
        ),
        hierarchy_directory=hierarchy_directory,
        observation_name=observation_name,
        observation_directory=observation_directory,
        lights_directory=observation_directory / "lights",
        seestar_stacked_directory=observation_directory / "seestar_stacked",
        tiff_directory=observation_directory / "tiff",
        lights=(),
        stack=None,
    )


def _plan(
    archive_root: Path,
    *observations: PlannedArchiveObservation,
    hierarchy: str = "{target}/{location}/{session_end_date}",
) -> ArchivePlan:
    return ArchivePlan(
        config=ArchivePlanningConfig(archive_root, hierarchy_template=hierarchy),
        observations=observations,
        problems=(),
    )


def _write_fits(path: Path, **overrides) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = fits.Header(
        {
            "OBJECT": "Target",
            "TELESCOP": "S50_99643794",
            "DATE-OBS": "2026-09-03T01:02:03",
            "EXPTIME": 10.0,
            "FILTER": "LP",
            "EQMODE": 1,
            "SITELAT": 51.123456,
            "SITELONG": -0.123456,
        }
    )
    for key, value in overrides.items():
        key = "DATE-OBS" if key == "DATE_OBS" else key
        if value is None:
            del header[key]
        else:
            header[key] = value
    fits.writeto(path, np.zeros((4, 4), dtype=np.uint16), header=header)


def _execution(
    plan: ArchivePlan, outcomes: tuple[tuple[Path, ArchiveFileOutcome], ...]
) -> ArchiveExecutionResult:
    files = tuple(
        ArchiveFileExecutionResult(
            source_path=path,
            destination_path=path,
            requested_action=SourceAction.COPY,
            outcome=outcome,
            collision=ArchiveCollisionState.NONE,
        )
        for path, outcome in outcomes
    )
    return ArchiveExecutionResult(plan, SourceAction.COPY, CollisionPolicy.SKIP_IDENTICAL, files)


def test_only_safely_established_lights_and_stack_are_reported(tmp_path: Path) -> None:
    observation = _planned_observation(tmp_path)
    plan = _plan(tmp_path, observation)
    good = observation.lights_directory / "Light_good.fit"
    identical = observation.lights_directory / "Light_identical.fit"
    failed = observation.lights_directory / "Light_failed.fit"
    stack = observation.seestar_stacked_directory / "Stacked_9_Target.fit"
    for path in (good, identical, failed, stack):
        _write_fits(path)
    execution = _execution(
        plan,
        (
            (good, ArchiveFileOutcome.COPIED),
            (identical, ArchiveFileOutcome.SKIPPED_IDENTICAL),
            (failed, ArchiveFileOutcome.FAILED),
            (stack, ArchiveFileOutcome.COLLISION),
        ),
    )

    result = generate_archive_indexes(plan, execution)

    content = result[0].index_path.read_text()
    assert "- Light subs: 2" in content
    assert "- Seestar stack: none" in content
    assert "- Seestar stack count: unknown" in content


def test_unknown_metadata_no_stack_and_markdown_headings_are_stable(tmp_path: Path) -> None:
    observation = _planned_observation(tmp_path, target="Target #1", location="Home [North]")
    plan = _plan(tmp_path, observation)
    light = observation.lights_directory / "Light.fit"
    _write_fits(
        light,
        OBJECT="Target #1",
        TELESCOP=None,
        DATE_OBS=None,
        EXPTIME=None,
        FILTER=None,
        EQMODE=None,
        SITELAT=None,
        SITELONG=None,
    )

    result = generate_archive_indexes(plan, _execution(plan, ((light, ArchiveFileOutcome.COPIED),)))

    content = result[0].index_path.read_text()
    assert content.startswith("# Target \\#1\n\n## Home \\[North\\] — 2026-09-03")
    assert "- Telescope: unknown" in content
    assert "- First light: unknown" in content
    assert "- Exposure: unknown" in content
    assert "- Filter: unknown" in content
    assert "- Seestar stack: none" in content
    assert "- Capture mode: unknown" in content
    assert "- GPS: unknown" in content
    assert content.endswith("\n")


def test_multiple_sessions_and_targets_have_deterministic_independent_indexes(
    tmp_path: Path,
) -> None:
    first = _planned_observation(tmp_path, date="20260902")
    second = _planned_observation(tmp_path, date="20260903")
    other = _planned_observation(tmp_path, target="Other", date="20260903")
    plan = _plan(tmp_path, second, other, first)
    outcomes = []
    for observation in (second, other, first):
        light = observation.lights_directory / f"Light_{observation.metadata.session_end_date}.fit"
        _write_fits(light, OBJECT=observation.metadata.logical_target)
        outcomes.append((light, ArchiveFileOutcome.COPIED))

    results = generate_archive_indexes(plan, _execution(plan, tuple(outcomes)))

    assert [item.index_path for item in results] == [
        tmp_path / "Other/INDEX.md",
        tmp_path / "Target/INDEX.md",
    ]
    target_content = (tmp_path / "Target/INDEX.md").read_text()
    assert target_content.index("2026-09-02") < target_content.index("2026-09-03")


def test_incremental_generation_preserves_historical_observation_without_duplicates(
    tmp_path: Path,
) -> None:
    first = _planned_observation(tmp_path, observation_name="observation_01")
    first_plan = _plan(tmp_path, first)
    first_light = first.lights_directory / "Light_first.fit"
    _write_fits(first_light)
    generate_archive_indexes(
        first_plan,
        _execution(first_plan, ((first_light, ArchiveFileOutcome.COPIED),)),
    )

    second = _planned_observation(tmp_path, observation_name="observation_02")
    second_plan = _plan(tmp_path, second)
    second_light = second.lights_directory / "Light_second.fit"
    _write_fits(second_light)
    result = generate_archive_indexes(
        second_plan,
        _execution(second_plan, ((second_light, ArchiveFileOutcome.COPIED),)),
    )

    content = result[0].index_path.read_text()
    assert result[0].outcome is ArchiveIndexOutcome.UPDATED
    assert content.count("### Observation 01") == 1
    assert content.count("### Observation 02") == 1
    assert content.index("Observation 01") < content.index("Observation 02")


def test_index_path_rejects_symlink_escape(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive"
    outside = tmp_path / "outside"
    archive_root.mkdir()
    outside.mkdir()
    (archive_root / "Target").symlink_to(outside, target_is_directory=True)
    observation = _planned_observation(archive_root)
    plan = _plan(archive_root, observation)

    with pytest.raises(OSError, match="escapes archive root"):
        planned_index_paths(plan)


def test_one_index_failure_does_not_prevent_independent_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failed_observation = _planned_observation(tmp_path, target="Broken")
    good_observation = _planned_observation(tmp_path, target="Good")
    plan = _plan(tmp_path, failed_observation, good_observation)
    failed_light = failed_observation.lights_directory / "Light.fit"
    good_light = good_observation.lights_directory / "Light.fit"
    _write_fits(failed_light, OBJECT="Broken")
    _write_fits(good_light, OBJECT="Good")
    real_replace = indexing.os.replace

    def selective_replace(source: Path, destination: Path) -> None:
        if "Broken" in Path(destination).parts:
            raise OSError("simulated failure")
        real_replace(source, destination)

    monkeypatch.setattr(indexing.os, "replace", selective_replace)

    results = generate_archive_indexes(
        plan,
        _execution(
            plan,
            (
                (failed_light, ArchiveFileOutcome.COPIED),
                (good_light, ArchiveFileOutcome.COPIED),
            ),
        ),
    )

    assert [item.outcome for item in results] == [
        ArchiveIndexOutcome.FAILED,
        ArchiveIndexOutcome.CREATED,
    ]
    assert not (tmp_path / "Broken/INDEX.md").exists()
    assert (tmp_path / "Good/INDEX.md").is_file()
