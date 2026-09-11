"""Tests for read-only archive metadata and destination planning."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from seestar_toolkit.archive import (
    ArchivePlanningCollisionError,
    ArchivePlanningConfigurationError,
    DiscoveryClassification,
    ObservationCompatibility,
    ObservationReconstructionResult,
    ObservationStatus,
    ReconstructedObservation,
    SavedLocation,
    SeestarDiscoveryItem,
    SourceDirectoryContext,
    normalize_archive_component,
    plan_seestar_archive,
    session_end_date,
)
from seestar_toolkit.fits import FitsImageClass, FitsInspection

ROOT = Path("My Works")
ARCHIVE_ROOT = Path("/archive")
BASE_TIME = datetime(2026, 9, 1, 22, 0)


def _item(
    name: str,
    classification: DiscoveryClassification,
    *,
    target: str | None = "IC 434",
    directory_target: str | None = "IC 434",
    captured_at: datetime | None = BASE_TIME,
    latitude: float | None = 51.41234,
    longitude: float | None = -0.75123,
    telescope: str | None = "S50_99643794",
    source_directory: Path | None = None,
) -> SeestarDiscoveryItem:
    directory = source_directory or ROOT / (
        "IC 434" if classification is DiscoveryClassification.SEESTAR_STACK_FITS else "IC 434_sub"
    )
    inspection = FitsInspection(
        path=directory / name,
        hdu_index=0,
        width=10,
        height=8,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        exposure_seconds=10.0,
        gain=80.0,
        bayer_pattern="GRBG",
        object_name=target,
        telescope=telescope,
        instrument="Seestar S50",
        filter_name="LP",
        captured_at=captured_at,
        image_type="Light",
        image_class=(
            FitsImageClass.RAW_LIGHT
            if classification is DiscoveryClassification.LIGHT_FITS
            else FitsImageClass.RGB_IMAGE
        ),
        total_exposure_seconds=10.0,
        exposure_ended_at=None,
        ra_degrees=None,
        dec_degrees=None,
        site_latitude=latitude,
        site_longitude=longitude,
        eq_mode=0,
        ccd_temperature=None,
        focus_position=None,
        aperture=None,
        focal_length=None,
        creator="ZWO Seestar S50",
        producer="ZWO",
        program=None,
        wide_camera=None,
    )
    return SeestarDiscoveryItem(
        source_path=directory / name,
        classification=classification,
        source_directory=directory,
        directory_context=(
            SourceDirectoryContext.PRODUCT
            if classification is DiscoveryClassification.SEESTAR_STACK_FITS
            else SourceDirectoryContext.SUB
        ),
        directory_target=directory_target,
        metadata_target=target,
        fits_inspection=inspection,
    )


def _observation(
    *,
    lights: tuple[SeestarDiscoveryItem, ...] | None = None,
    stack: SeestarDiscoveryItem | None = None,
    first_at: datetime | None = BASE_TIME,
    stack_at: datetime | None = None,
    status: ObservationStatus = ObservationStatus.LIGHTS_ONLY,
) -> ReconstructedObservation:
    light_items = (
        lights
        if lights is not None
        else (_item("Light_IC 434_20260901-220000.fit", DiscoveryClassification.LIGHT_FITS),)
    )
    return ReconstructedObservation(
        lights=light_items,
        stack=stack,
        first_light_at=first_at,
        last_light_at=first_at,
        stack_at=stack_at,
        status=status,
        compatibility=ObservationCompatibility("IC 434", 10.0, "LP", 0),
        reported_stack_count=None,
        problems=(),
    )


def _plan(*observations: ReconstructedObservation, **kwargs):
    return plan_seestar_archive(
        ObservationReconstructionResult(observations=observations, excluded_items=()),
        archive_root=ARCHIVE_ROOT,
        **kwargs,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  IC   434  ", "IC 434"),
        ("Horse Head Nebula", "Horse Head Nebula"),
        ("Target/Name", "Target-Name"),
        ("Target\\Name:*?", "Target-Name-"),
        ("..", "unknown"),
        (".", "unknown"),
        ("/absolute/path", "-absolute-path"),
    ],
)
def test_path_component_normalization(value: str, expected: str) -> None:
    assert normalize_archive_component(value) == expected


def test_default_hierarchy_and_source_metadata_are_retained() -> None:
    observation = _observation()

    planned = _plan(observation, explicit_location="  Warfield   Church  ").observations[0]

    assert planned.hierarchy_directory == ARCHIVE_ROOT / "IC 434/Warfield Church/20260902"
    assert planned.metadata.logical_location == "  Warfield   Church  "
    assert planned.metadata.location_component == "Warfield Church"
    assert planned.metadata.logical_target == "IC 434"
    assert planned.metadata.source_latitude == 51.41234
    assert planned.metadata.source_longitude == -0.75123
    assert planned.metadata.telescope == "S50_99643794"


def test_alternative_hierarchy_ordering_uses_supported_tokens() -> None:
    planned = _plan(
        _observation(),
        hierarchy_template="{location}/{session_end_date}/{target}",
        explicit_location="Home",
    ).observations[0]

    assert planned.hierarchy_directory == ARCHIVE_ROOT / "Home/20260902/IC 434"


@pytest.mark.parametrize(
    ("template", "message"),
    [
        ("{target}/{planet}/{session_end_date}", "Unknown hierarchy token"),
        ("/{target}/{location}/{session_end_date}", "relative path"),
        ("../{target}/{location}/{session_end_date}", "unsafe component"),
        ("{target}\\{location}\\{session_end_date}", "relative path"),
        ("prefix-{target}/{location}/{session_end_date}", "one supported token"),
        ("{target}/{location}", "exactly once"),
    ],
)
def test_unsafe_or_unsupported_hierarchy_is_rejected(template: str, message: str) -> None:
    with pytest.raises(ArchivePlanningConfigurationError, match=message):
        _plan(_observation(), hierarchy_template=template)


def test_relative_archive_root_is_rejected_to_avoid_cwd_dependency() -> None:
    with pytest.raises(ArchivePlanningConfigurationError, match="absolute"):
        plan_seestar_archive(
            ObservationReconstructionResult((_observation(),), ()), archive_root="archive"
        )


def test_archive_root_with_traversal_is_rejected() -> None:
    with pytest.raises(ArchivePlanningConfigurationError, match="traversal"):
        plan_seestar_archive(
            ObservationReconstructionResult((_observation(),), ()),
            archive_root="/archive/../escape",
        )


@pytest.mark.parametrize(
    ("captured_at", "expected"),
    [
        (datetime(2026, 9, 1, 11, 59, 59), "20260901"),
        (datetime(2026, 9, 1, 12, 0, 0), "20260902"),
        (datetime(2026, 9, 1, 22, 0, 0), "20260902"),
        (datetime(2026, 9, 2, 1, 30, 0), "20260902"),
    ],
)
def test_session_end_date_uses_twelve_hour_rule(captured_at: datetime, expected: str) -> None:
    assert session_end_date(captured_at) == expected


def test_first_light_time_is_preferred_over_stack_time() -> None:
    stack = _item("Stacked_1_IC 434.fit", DiscoveryClassification.SEESTAR_STACK_FITS)
    observation = _observation(
        stack=stack,
        first_at=datetime(2026, 9, 1, 11, 0),
        stack_at=datetime(2026, 9, 1, 13, 0),
        status=ObservationStatus.COMPLETE,
    )

    assert _plan(observation).observations[0].metadata.session_end_date == "20260901"


def test_stack_time_supports_stack_only_planning() -> None:
    stack = _item("Stacked_1_IC 434.fit", DiscoveryClassification.SEESTAR_STACK_FITS)
    observation = _observation(
        lights=(),
        stack=stack,
        first_at=None,
        stack_at=BASE_TIME,
        status=ObservationStatus.STACK_ONLY,
    )

    planned = _plan(observation).observations[0]

    assert planned.observation_name == "observation_01"
    assert planned.stack is not None


def test_explicit_location_wins_over_saved_gps_match() -> None:
    saved = (SavedLocation("GPS home", 51.41234, -0.75123, 100),)
    metadata = (
        _plan(_observation(), explicit_location="Preferred name", saved_locations=saved)
        .observations[0]
        .metadata
    )

    assert metadata.logical_location == "Preferred name"


def test_nearest_matching_saved_location_wins_deterministically() -> None:
    saved = (
        SavedLocation("Farther", 51.4125, -0.75123, 100),
        SavedLocation("Nearest", 51.41235, -0.75123, 100),
    )

    metadata = _plan(_observation(), saved_locations=saved).observations[0].metadata

    assert metadata.logical_location == "Nearest"


def test_saved_location_radius_is_inclusive_and_no_match_is_unknown() -> None:
    same_point = SavedLocation("Exact", 51.41234, -0.75123, 0)
    assert (
        _plan(_observation(), saved_locations=(same_point,))
        .observations[0]
        .metadata.logical_location
        == "Exact"
    )

    no_match = SavedLocation("Elsewhere", 0, 0, 1)
    assert (
        _plan(_observation(), saved_locations=(no_match,)).observations[0].metadata.logical_location
        == "unknown"
    )


@pytest.mark.parametrize(
    "location",
    [
        SavedLocation("bad latitude", 91, 0, 1),
        SavedLocation("bad longitude", 0, 181, 1),
        SavedLocation("bad radius", 0, 0, -1),
        SavedLocation("infinite", float("inf"), 0, 1),
    ],
)
def test_invalid_saved_location_is_rejected(location: SavedLocation) -> None:
    with pytest.raises(ArchivePlanningConfigurationError, match="invalid"):
        _plan(_observation(), saved_locations=(location,))


def test_target_metadata_precedes_directory_and_conflict_is_visible() -> None:
    light = _item(
        "Light.fit",
        DiscoveryClassification.LIGHT_FITS,
        target="Metadata Target",
        directory_target="Directory Target",
    )
    observation = replace(
        _observation(lights=(light,)),
        compatibility=ObservationCompatibility("Metadata Target", 10, "LP", 0),
    )

    metadata = _plan(observation).observations[0].metadata

    assert metadata.logical_target == "Metadata Target"
    assert any("conflicts with directory" in message for message in metadata.diagnostics)


def test_missing_target_uses_explicit_unknown_with_diagnostic() -> None:
    light = _item(
        "Light.fit", DiscoveryClassification.LIGHT_FITS, target=None, directory_target=None
    )
    observation = replace(_observation(lights=(light,)), compatibility=None)

    metadata = _plan(observation).observations[0].metadata

    assert metadata.logical_target == "unknown"
    assert any("No target evidence" in message for message in metadata.diagnostics)


def test_mosaic_comparison_does_not_rewrite_directory_target_fallback() -> None:
    light = _item(
        "Light.fit",
        DiscoveryClassification.LIGHT_FITS,
        target=None,
        directory_target="Target_mosaic",
    )
    observation = replace(_observation(lights=(light,)), compatibility=None)

    metadata = _plan(observation).observations[0].metadata

    assert metadata.logical_target == "Target_mosaic"
    assert metadata.target_component == "Target_mosaic"
    assert metadata.diagnostics == ()


def test_one_and_multiple_observations_are_numbered_chronologically_per_group() -> None:
    later = _observation(
        lights=(_item("Light_later.fit", DiscoveryClassification.LIGHT_FITS),),
        first_at=BASE_TIME + timedelta(hours=1),
    )
    earlier = _observation(lights=(_item("Light_earlier.fit", DiscoveryClassification.LIGHT_FITS),))

    plan = _plan(later, earlier)

    by_source = {item.lights[0].source_path.name: item for item in plan.observations}
    assert by_source["Light_earlier.fit"].observation_name == "observation_01"
    assert by_source["Light_later.fit"].observation_name == "observation_02"


def test_numbering_is_scoped_by_hierarchy_group_and_unambiguous_above_99() -> None:
    observations = tuple(
        _observation(
            lights=(_item(f"Light_{index}.fit", DiscoveryClassification.LIGHT_FITS),),
            first_at=BASE_TIME + timedelta(seconds=index),
        )
        for index in range(100)
    )

    plan = _plan(*reversed(observations))

    names = {item.observation_name for item in plan.observations}
    assert "observation_001" in names
    assert "observation_100" in names
    assert len(names) == 100


def test_numbering_restarts_for_a_different_target_group() -> None:
    first = _observation()
    other_light = _item(
        "Light_other.fit",
        DiscoveryClassification.LIGHT_FITS,
        target="NGC 7000",
        directory_target="NGC 7000",
    )
    second = replace(
        _observation(lights=(other_light,)),
        compatibility=ObservationCompatibility("NGC 7000", 10, "LP", 0),
    )

    assert {item.observation_name for item in _plan(first, second).observations} == {
        "observation_01"
    }


def test_missing_telescope_identifier_remains_explicitly_absent() -> None:
    light = _item("Light.fit", DiscoveryClassification.LIGHT_FITS, telescope=None)

    assert _plan(_observation(lights=(light,))).observations[0].metadata.telescope is None


def test_light_and_stack_fits_and_tiff_destinations_follow_contract() -> None:
    light = _item("Light_Target.FITS", DiscoveryClassification.LIGHT_FITS)
    stack = _item("Stacked_1_Target.fit", DiscoveryClassification.SEESTAR_STACK_FITS)
    observation = _observation(
        lights=(light,), stack=stack, stack_at=BASE_TIME, status=ObservationStatus.COMPLETE
    )

    planned = _plan(observation).observations[0]

    assert planned.lights_directory.name == "lights"
    assert planned.tiff_directory.name == "tiff"
    assert planned.seestar_stacked_directory.name == "seestar_stacked"
    assert planned.lights[0].fits_destination.name == "Light_Target.FITS"
    assert planned.lights[0].tiff_destination.name == "Light_Target.tiff"
    assert planned.stack is not None
    assert planned.stack.fits_destination.name == "Stacked_1_Target.fit"
    assert planned.stack.tiff_destination.name == "Stacked_1_Target.tiff"
    assert planned.stack.fits_destination.parent == planned.seestar_stacked_directory
    assert planned.stack.tiff_destination.parent == planned.seestar_stacked_directory
    assert all(
        path.is_relative_to(ARCHIVE_ROOT)
        for path in (
            planned.lights[0].fits_destination,
            planned.lights[0].tiff_destination,
            planned.stack.fits_destination,
            planned.stack.tiff_destination,
        )
    )


@pytest.mark.parametrize("status", [ObservationStatus.AMBIGUOUS, ObservationStatus.UNRESOLVED])
def test_unsafe_reconstruction_status_is_retained_as_problem(status: ObservationStatus) -> None:
    result = _plan(_observation(status=status))

    assert result.observations == ()
    assert result.problems[0].observation.status is status
    assert "not safe" in result.problems[0].messages[-1]


def test_missing_observation_time_is_retained_as_problem() -> None:
    result = _plan(_observation(first_at=None))

    assert result.observations == ()
    assert "No safe observation timestamp" in result.problems[0].messages[-1]


def test_distinct_sources_mapping_to_one_destination_are_rejected() -> None:
    first = _item(
        "Light.fit",
        DiscoveryClassification.LIGHT_FITS,
        source_directory=ROOT / "first",
    )
    second = _item(
        "Light.fit",
        DiscoveryClassification.LIGHT_FITS,
        source_directory=ROOT / "second",
    )
    observation = _observation(lights=(first, second))

    with pytest.raises(ArchivePlanningCollisionError, match="Distinct sources"):
        _plan(observation)


def test_planning_is_deterministic_and_does_not_mutate_filesystem(tmp_path: Path) -> None:
    archive_root = tmp_path / "archive-does-not-exist"
    reconstruction = ObservationReconstructionResult((_observation(),), ())

    first = plan_seestar_archive(reconstruction, archive_root=archive_root)
    second = plan_seestar_archive(reconstruction, archive_root=archive_root)

    assert first == second
    assert not archive_root.exists()
    assert not tuple(tmp_path.rglob("*.tiff"))
    assert not tuple(tmp_path.rglob("INDEX.md"))
