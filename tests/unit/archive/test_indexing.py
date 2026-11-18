"""Focused tests for derived target-level archive indexes."""

from __future__ import annotations

from itertools import permutations
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
    telescope: str = "S50_99643794",
) -> PlannedArchiveObservation:
    values = {
        "{target}": target,
        "{location}": location,
        "{session_end_date}": date,
        "{telescope}": telescope,
    }
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
            telescope=telescope,
            diagnostics=(),
            resolved_telescope_identity=telescope.casefold(),
            telescope_component=telescope,
        ),
        hierarchy_directory=hierarchy_directory,
        observation_name=observation_name,
        observation_directory=observation_directory,
        lights_directory=observation_directory / "fits_images" / "lights",
        seestar_stacked_directory=observation_directory / "seestar_stacked",
        tiff_directory=observation_directory / "tiff_images" / "lights",
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


HIERARCHY_TOKEN_ORDERS = tuple(
    ordering
    for length in range(1, 5)
    for ordering in permutations(
        ("{target}", "{location}", "{session_end_date}", "{telescope}"), length
    )
)


@pytest.mark.parametrize("tokens", HIERARCHY_TOKEN_ORDERS)
def test_index_generation_supports_every_valid_hierarchy_ordering(
    tmp_path: Path, tokens: tuple[str, ...]
) -> None:
    hierarchy = "/".join(tokens)
    observation = _planned_observation(tmp_path, hierarchy=hierarchy)
    plan = _plan(tmp_path, observation, hierarchy=hierarchy)
    light = observation.lights_directory / "Light.fit"
    _write_fits(light)

    result = generate_archive_indexes(plan, _execution(plan, ((light, ArchiveFileOutcome.COPIED),)))

    values = {
        "{target}": "Target",
        "{location}": "Home",
        "{session_end_date}": "20260903",
        "{telescope}": "S50_99643794",
    }
    target_position = tokens.index("{target}") if "{target}" in tokens else None
    expected_parent = (
        tmp_path.joinpath(*(values[token] for token in tokens[: target_position + 1]))
        if target_position is not None
        else tmp_path
    )
    assert [item.index_path for item in result] == [expected_parent / "INDEX.md"]
    content = result[0].index_path.read_text()
    if "{target}" in tokens:
        assert content.startswith("# Target\n")
    else:
        assert content.startswith("# Archive\n")
        assert "- Target: Target" in content
        assert not (tmp_path / "Target").exists()


def test_archive_root_index_retains_each_target_without_artificial_directories(
    tmp_path: Path,
) -> None:
    first = _planned_observation(
        tmp_path,
        target="Target One",
        telescope="S50_00000001",
        hierarchy="{telescope}",
    )
    second = _planned_observation(
        tmp_path,
        target="Target Two",
        telescope="S50_00000002",
        hierarchy="{telescope}",
    )
    plan = _plan(tmp_path, first, second, hierarchy="{telescope}")
    first_light = first.lights_directory / "Light_one.fit"
    second_light = second.lights_directory / "Light_two.fit"
    _write_fits(first_light, OBJECT="Target One", TELESCOP="S50_00000001")
    _write_fits(second_light, OBJECT="Target Two", TELESCOP="S50_00000002")

    result = generate_archive_indexes(
        plan,
        _execution(
            plan,
            (
                (first_light, ArchiveFileOutcome.COPIED),
                (second_light, ArchiveFileOutcome.COPIED),
            ),
        ),
    )

    assert [item.index_path for item in result] == [tmp_path / "INDEX.md"]
    content = result[0].index_path.read_text()
    assert content.count("- Target: Target One") == 1
    assert content.count("- Target: Target Two") == 1
    assert "- Archive path: S50_00000001/observation_01" in content
    assert "- Archive path: S50_00000002/observation_01" in content
    assert not (tmp_path / "Target One").exists()
    assert not (tmp_path / "Target Two").exists()


def _target_free_incremental_plan(
    archive_root: Path,
    *,
    historical_object: str | None = None,
) -> tuple[ArchivePlan, Path, Path]:
    historical = _planned_observation(
        archive_root,
        target="Historical Target",
        telescope="S50_00000001",
        hierarchy="{telescope}",
    )
    current = _planned_observation(
        archive_root,
        target="Current Target",
        telescope="S50_00000002",
        hierarchy="{telescope}",
    )
    historical_light = historical.lights_directory / "Historical.fit"
    current_light = current.lights_directory / "Current.fit"
    if not historical_light.exists():
        _write_fits(
            historical_light,
            OBJECT=historical_object,
            TELESCOP="S50_00000001",
        )
    _write_fits(current_light, OBJECT="Current Target", TELESCOP="S50_00000002")
    return (
        _plan(archive_root, current, hierarchy="{telescope}"),
        historical_light,
        current_light,
    )


def test_target_free_incremental_index_recovers_historical_target_by_archive_path(
    tmp_path: Path,
) -> None:
    historical = _planned_observation(
        tmp_path,
        target="Historical Target",
        telescope="S50_00000001",
        hierarchy="{telescope}",
    )
    first_plan = _plan(tmp_path, historical, hierarchy="{telescope}")
    historical_light = historical.lights_directory / "Historical.fit"
    _write_fits(historical_light, OBJECT=None, TELESCOP="S50_00000001")
    first = generate_archive_indexes(
        first_plan,
        _execution(first_plan, ((historical_light, ArchiveFileOutcome.COPIED),)),
    )
    assert first[0].outcome is ArchiveIndexOutcome.CREATED

    second_plan, _, current_light = _target_free_incremental_plan(tmp_path)
    second = generate_archive_indexes(
        second_plan,
        _execution(second_plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert second[0].outcome is ArchiveIndexOutcome.UPDATED
    content = (tmp_path / "INDEX.md").read_text()
    assert content.count("- Target: Historical Target") == 1
    assert content.count("- Target: Current Target") == 1
    assert "- Archive path: S50_00000001/observation_01" in content
    assert "- Archive path: S50_00000002/observation_01" in content


def test_missing_root_index_is_not_needed_when_historical_fits_has_target(
    tmp_path: Path,
) -> None:
    plan, _, current_light = _target_free_incremental_plan(
        tmp_path, historical_object="Historical FITS Target"
    )

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.CREATED
    content = (tmp_path / "INDEX.md").read_text()
    assert "- Target: Historical FITS Target" in content
    assert "- Target: Current Target" in content


def test_historical_fits_target_overrides_stale_root_index_record(tmp_path: Path) -> None:
    plan, _, current_light = _target_free_incremental_plan(
        tmp_path, historical_object="Historical FITS Target"
    )
    (tmp_path / "INDEX.md").write_text(
        "# Archive\n\n### Observation 01\n\n"
        "- Target: Stale Target\n"
        "- Archive path: S50_00000001/observation_01\n"
    )

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.UPDATED
    content = (tmp_path / "INDEX.md").read_text()
    assert "- Target: Historical FITS Target" in content
    assert "Stale Target" not in content


def test_later_historical_fits_target_overrides_stale_root_index_record(
    tmp_path: Path,
) -> None:
    plan, historical_light, current_light = _target_free_incremental_plan(tmp_path)
    later_light = historical_light.with_name("Later.fit")
    _write_fits(
        later_light,
        OBJECT="Reliable Later FITS Target",
        TELESCOP="S50_00000001",
    )
    (tmp_path / "INDEX.md").write_text(
        "# Archive\n\n### Observation 01\n\n"
        "- Target: Stale Target\n"
        "- Archive path: S50_00000001/observation_01\n"
    )

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.UPDATED
    content = (tmp_path / "INDEX.md").read_text()
    assert "- Target: Reliable Later FITS Target" in content
    assert "Stale Target" not in content


def test_later_historical_fits_target_avoids_unnecessary_missing_index_failure(
    tmp_path: Path,
) -> None:
    plan, historical_light, current_light = _target_free_incremental_plan(tmp_path)
    later_light = historical_light.with_name("Later.fit")
    _write_fits(
        later_light,
        OBJECT="Reliable Later FITS Target",
        TELESCOP="S50_00000001",
    )

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.CREATED
    content = (tmp_path / "INDEX.md").read_text()
    assert "- Target: Reliable Later FITS Target" in content
    assert "- Target: Current Target" in content


def test_missing_root_index_fails_when_historical_target_recovery_is_required(
    tmp_path: Path,
) -> None:
    plan, _, current_light = _target_free_incremental_plan(tmp_path)

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.FAILED
    assert result[0].diagnostic is not None
    assert "S50_00000001/observation_01" in result[0].diagnostic
    assert "missing" in result[0].diagnostic
    assert not (tmp_path / "INDEX.md").exists()


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (
            "# Archive\n\n### Observation 01\n\n- Target: Historical Target\n",
            "malformed",
        ),
        (
            "# Archive\n\n### Observation 01\n\n"
            "- Target: Historical Target\n"
            "- Archive path: S50_00000001/observation_01\n\n"
            "### Observation 01\n\n"
            "- Target: Historical Target\n"
            "- Archive path: S50_00000001/observation_01\n",
            "ambiguous",
        ),
        (
            "# Archive\n\n### Observation 01\n\n"
            "- Target: Historical Target\n"
            "- Archive path: S50_00000001/observation_01\n\n"
            "### Observation 01\n\n"
            "- Target: Different Target\n"
            "- Archive path: S50_00000001/observation_01\n",
            "inconsistent",
        ),
        (
            "# Archive\n\n### Observation 01\n\n"
            "- Target: Other Target\n"
            "- Archive path: S50_99999999/observation_01\n",
            "no exact matching record",
        ),
    ],
)
def test_required_historical_recovery_rejects_invalid_index_and_preserves_it(
    tmp_path: Path,
    content: str,
    reason: str,
) -> None:
    plan, _, current_light = _target_free_incremental_plan(tmp_path)
    index_path = tmp_path / "INDEX.md"
    index_path.write_text(content)
    before = index_path.read_bytes()

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.FAILED
    assert result[0].diagnostic is not None
    assert "S50_00000001/observation_01" in result[0].diagnostic
    assert reason in result[0].diagnostic
    assert index_path.read_bytes() == before


def test_required_historical_recovery_rejects_unreadable_index_bytes(
    tmp_path: Path,
) -> None:
    plan, _, current_light = _target_free_incremental_plan(tmp_path)
    index_path = tmp_path / "INDEX.md"
    index_path.write_bytes(b"\xff\xfe")
    before = index_path.read_bytes()

    result = generate_archive_indexes(
        plan,
        _execution(plan, ((current_light, ArchiveFileOutcome.COPIED),)),
    )

    assert result[0].outcome is ArchiveIndexOutcome.FAILED
    assert result[0].diagnostic is not None
    assert "S50_00000001/observation_01" in result[0].diagnostic
    assert "unreadable" in result[0].diagnostic
    assert index_path.read_bytes() == before


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
