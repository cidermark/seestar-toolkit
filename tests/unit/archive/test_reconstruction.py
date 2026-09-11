"""Tests for conservative Seestar observation reconstruction."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from seestar_toolkit.archive import (
    DiscoveryClassification,
    ObservationStatus,
    SeestarDiscoveryInventory,
    SeestarDiscoveryItem,
    SourceDirectoryContext,
    reconstruct_seestar_observations,
)
from seestar_toolkit.fits import FitsImageClass, FitsInspection

ROOT = Path("My Works")
BASE_TIME = datetime(2026, 1, 3, 22, 0, 0)


def _item(
    classification: DiscoveryClassification,
    name: str,
    captured_at: datetime | None,
    *,
    target: str | None = "IC 434",
    exposure: float | None = 10.0,
    filter_name: str | None = "LP",
    eq_mode: int | None = 0,
    directory_target: str | None = "IC 434",
    problem: str | None = None,
    total_exposure: float | None = None,
) -> SeestarDiscoveryItem:
    source_directory = ROOT / (
        "IC 434" if classification is DiscoveryClassification.SEESTAR_STACK_FITS else "IC 434_sub"
    )
    inspection = FitsInspection(
        path=source_directory / name,
        hdu_index=0,
        width=10,
        height=8,
        dtype=np.dtype(np.uint16),
        bit_depth=16,
        exposure_seconds=exposure,
        gain=80.0,
        bayer_pattern="GRBG",
        object_name=target,
        telescope="S50_12345678",
        instrument="Seestar S50",
        filter_name=filter_name,
        captured_at=captured_at,
        image_type="Light",
        image_class=(
            FitsImageClass.RAW_LIGHT
            if classification is DiscoveryClassification.LIGHT_FITS
            else FitsImageClass.RGB_IMAGE
        ),
        total_exposure_seconds=total_exposure,
        exposure_ended_at=None,
        ra_degrees=None,
        dec_degrees=None,
        site_latitude=None,
        site_longitude=None,
        eq_mode=eq_mode,
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
        source_path=source_directory / name,
        classification=classification,
        source_directory=source_directory,
        directory_context=(
            SourceDirectoryContext.PRODUCT
            if classification is DiscoveryClassification.SEESTAR_STACK_FITS
            else SourceDirectoryContext.SUB
        ),
        directory_target=directory_target,
        metadata_target=target,
        fits_inspection=inspection,
        problem=problem,
    )


def _non_frame(classification: DiscoveryClassification, name: str) -> SeestarDiscoveryItem:
    source_directory = ROOT / "IC 434"
    return SeestarDiscoveryItem(
        source_path=source_directory / name,
        classification=classification,
        source_directory=source_directory,
        directory_context=SourceDirectoryContext.PRODUCT,
        directory_target="IC 434",
        metadata_target=None,
        fits_inspection=None,
        problem="not an observation frame"
        if classification is DiscoveryClassification.UNKNOWN
        else None,
    )


def _inventory(*items: SeestarDiscoveryItem) -> SeestarDiscoveryInventory:
    return SeestarDiscoveryInventory(root=ROOT, items=items)


def _observation_with_stack(result, name: str):
    return next(
        observation
        for observation in result.observations
        if observation.stack is not None and observation.stack.source_path.name == name
    )


def test_stack_closes_compatible_preceding_light_sequence() -> None:
    light_1 = _item(DiscoveryClassification.LIGHT_FITS, "Light_1.fit", BASE_TIME)
    light_2 = _item(
        DiscoveryClassification.LIGHT_FITS, "Light_2.fit", BASE_TIME + timedelta(seconds=11)
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_target.fit",
        BASE_TIME + timedelta(seconds=25),
    )

    result = reconstruct_seestar_observations(_inventory(stack, light_2, light_1))

    assert len(result.observations) == 1
    observation = result.observations[0]
    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == (light_1, light_2)
    assert observation.stack == stack
    assert observation.first_light_at == BASE_TIME
    assert observation.last_light_at == BASE_TIME + timedelta(seconds=11)
    assert observation.stack_at == BASE_TIME + timedelta(seconds=25)


def test_equal_time_compatible_light_is_considered_before_stack() -> None:
    earlier = _item(DiscoveryClassification.LIGHT_FITS, "Light_earlier.fit", BASE_TIME)
    final = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_final.fit",
        BASE_TIME + timedelta(seconds=11),
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_target.fit",
        BASE_TIME + timedelta(seconds=11),
    )

    result = reconstruct_seestar_observations(_inventory(stack, final, earlier))

    assert len(result.observations) == 1
    assert result.observations[0].status is ObservationStatus.COMPLETE
    assert result.observations[0].lights == (earlier, final)
    assert result.observations[0].stack == stack


def test_equal_time_incompatible_light_is_not_consumed_by_stack() -> None:
    compatible = _item(DiscoveryClassification.LIGHT_FITS, "Light_compatible.fit", BASE_TIME)
    incompatible = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_incompatible.fit",
        BASE_TIME + timedelta(seconds=11),
        target="NGC 7000",
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_target.fit",
        BASE_TIME + timedelta(seconds=11),
    )

    result = reconstruct_seestar_observations(_inventory(stack, incompatible, compatible))

    assert _observation_with_stack(result, stack.source_path.name).lights == (compatible,)
    assert any(observation.lights == (incompatible,) for observation in result.observations)


def test_light_later_than_equal_time_stack_is_not_assigned_backwards() -> None:
    final = _item(DiscoveryClassification.LIGHT_FITS, "Light_final.fit", BASE_TIME)
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_target.fit",
        BASE_TIME,
    )
    later = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_later.fit",
        BASE_TIME + timedelta(seconds=1),
    )

    result = reconstruct_seestar_observations(_inventory(later, stack, final))

    assert _observation_with_stack(result, stack.source_path.name).lights == (final,)
    assert any(observation.lights == (later,) for observation in result.observations)


def test_equal_time_stacks_remain_deterministic_and_consume_only_compatible_lights() -> None:
    first_light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_first.fit",
        BASE_TIME,
    )
    second_light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_second.fit",
        BASE_TIME,
        target="NGC 7000",
    )
    first_stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_a.fit",
        BASE_TIME,
    )
    second_stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_b.fit",
        BASE_TIME,
        target="NGC 7000",
    )

    result = reconstruct_seestar_observations(
        _inventory(second_stack, second_light, first_stack, first_light)
    )

    assert _observation_with_stack(result, first_stack.source_path.name).lights == (first_light,)
    assert _observation_with_stack(result, second_stack.source_path.name).lights == (second_light,)


def test_intermediate_stacks_create_separate_boundaries() -> None:
    light_1 = _item(DiscoveryClassification.LIGHT_FITS, "Light_1.fit", BASE_TIME)
    stack_1 = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_first.fit",
        BASE_TIME + timedelta(seconds=12),
    )
    light_2 = _item(
        DiscoveryClassification.LIGHT_FITS, "Light_2.fit", BASE_TIME + timedelta(seconds=20)
    )
    stack_2 = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_second.fit",
        BASE_TIME + timedelta(seconds=32),
    )

    result = reconstruct_seestar_observations(_inventory(light_1, stack_1, light_2, stack_2))

    assert len(result.observations) == 2
    assert _observation_with_stack(result, "Stacked_1_first.fit").lights == (light_1,)
    assert _observation_with_stack(result, "Stacked_1_second.fit").lights == (light_2,)


def test_equal_time_fix_preserves_compact_multi_session_stack_boundaries() -> None:
    first_lights = (
        _item(DiscoveryClassification.LIGHT_FITS, "Light_1a.fit", BASE_TIME),
        _item(
            DiscoveryClassification.LIGHT_FITS,
            "Light_1b.fit",
            BASE_TIME + timedelta(seconds=11),
        ),
    )
    first_stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_first.fit",
        BASE_TIME + timedelta(seconds=11),
    )
    second_light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_2.fit",
        BASE_TIME + timedelta(minutes=10),
    )
    second_stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_second.fit",
        BASE_TIME + timedelta(minutes=10, seconds=12),
    )
    third_lights = (
        _item(
            DiscoveryClassification.LIGHT_FITS,
            "Light_3a.fit",
            BASE_TIME + timedelta(minutes=20),
            exposure=30.0,
        ),
        _item(
            DiscoveryClassification.LIGHT_FITS,
            "Light_3b.fit",
            BASE_TIME + timedelta(minutes=25),
            exposure=30.0,
        ),
    )
    third_stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_third.fit",
        BASE_TIME + timedelta(minutes=25, seconds=31),
        exposure=30.0,
    )

    result = reconstruct_seestar_observations(
        _inventory(
            third_stack,
            second_light,
            first_stack,
            *third_lights,
            second_stack,
            *first_lights,
        )
    )

    assert len(result.observations) == 3
    assert all(
        observation.status is ObservationStatus.COMPLETE for observation in result.observations
    )
    assert _observation_with_stack(result, first_stack.source_path.name).lights == first_lights
    assert _observation_with_stack(result, second_stack.source_path.name).lights == (second_light,)
    assert _observation_with_stack(result, third_stack.source_path.name).lights == third_lights


def test_final_stack_intentionally_merges_compatible_lights_without_intermediate_stack() -> None:
    lights = tuple(
        _item(
            DiscoveryClassification.LIGHT_FITS,
            f"Light_{index}.fit",
            BASE_TIME + timedelta(minutes=index * 10),
        )
        for index in range(3)
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_final.fit",
        BASE_TIME + timedelta(minutes=31),
    )

    result = reconstruct_seestar_observations(_inventory(*lights, stack))

    observation = _observation_with_stack(result, "Stacked_2_final.fit")
    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == lights
    assert observation.reported_stack_count == 2
    assert "source lights were associated" not in " ".join(observation.problems)


def test_post_stack_light_is_not_assigned_backwards() -> None:
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_0_first.fit",
        BASE_TIME,
    )
    later_light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_later.fit",
        BASE_TIME + timedelta(seconds=10),
    )

    result = reconstruct_seestar_observations(_inventory(stack, later_light))

    assert _observation_with_stack(result, "Stacked_0_first.fit").lights == ()
    lights_only = next(
        observation for observation in result.observations if observation.stack is None
    )
    assert lights_only.lights == (later_light,)
    assert lights_only.status is ObservationStatus.LIGHTS_ONLY


@pytest.mark.parametrize(
    ("field", "different"),
    [
        pytest.param("target", "NGC 7000", id="target"),
        pytest.param("exposure", 20.0, id="exposure"),
        pytest.param("filter_name", "IRCUT", id="filter"),
        pytest.param("eq_mode", 1, id="capture-mode"),
    ],
)
def test_incompatible_light_is_not_consumed_by_stack(field: str, different: object) -> None:
    arguments = {field: different}
    light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_incompatible.fit",
        BASE_TIME,
        **arguments,
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_target.fit",
        BASE_TIME + timedelta(seconds=15),
    )

    result = reconstruct_seestar_observations(_inventory(light, stack))

    assert (
        _observation_with_stack(result, "Stacked_1_target.fit").status
        is ObservationStatus.STACK_ONLY
    )
    assert any(observation.lights == (light,) for observation in result.observations)


def test_retained_count_greater_than_stack_count_is_not_an_error() -> None:
    lights = tuple(
        _item(
            DiscoveryClassification.LIGHT_FITS,
            f"Light_{index}.fit",
            BASE_TIME + timedelta(seconds=index * 31),
            exposure=30.0,
        )
        for index in range(135)
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_106_target.fit",
        BASE_TIME + timedelta(seconds=135 * 31),
        exposure=30.0,
        total_exposure=3180.0,
    )

    observation = reconstruct_seestar_observations(_inventory(*lights, stack)).observations[0]

    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == lights
    assert observation.reported_stack_count == 106
    assert observation.problems == ()


def test_retained_count_less_than_stack_count_does_not_fabricate_lights() -> None:
    lights = tuple(
        _item(
            DiscoveryClassification.LIGHT_FITS,
            f"Light_{index}.fit",
            BASE_TIME + timedelta(seconds=index * 31),
            exposure=30.0,
        )
        for index in range(2)
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_3_target.fit",
        BASE_TIME + timedelta(seconds=70),
        exposure=30.0,
        total_exposure=90.0,
    )

    observation = reconstruct_seestar_observations(_inventory(*lights, stack)).observations[0]

    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == lights
    assert observation.reported_stack_count == 3
    assert observation.problems == ()


def test_missing_stack_count_remains_supported() -> None:
    light = _item(DiscoveryClassification.LIGHT_FITS, "Light_1.fit", BASE_TIME)
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_target.fit",
        BASE_TIME + timedelta(seconds=11),
        total_exposure=10.0,
    )

    observation = reconstruct_seestar_observations(_inventory(light, stack)).observations[0]

    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == (light,)
    assert observation.reported_stack_count is None
    assert observation.problems == ()


def test_contradictory_stack_metadata_is_diagnosed_without_changing_membership() -> None:
    lights = tuple(
        _item(
            DiscoveryClassification.LIGHT_FITS,
            f"Light_{index}.fit",
            BASE_TIME + timedelta(seconds=index * 31),
            exposure=30.0,
        )
        for index in range(2)
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_106_target.fit",
        BASE_TIME + timedelta(seconds=70),
        exposure=30.0,
        total_exposure=3000.0,
    )

    observation = reconstruct_seestar_observations(_inventory(*lights, stack)).observations[0]

    assert observation.status is ObservationStatus.COMPLETE
    assert observation.lights == lights
    assert observation.reported_stack_count == 106
    assert any("stack metadata disagree" in problem for problem in observation.problems)


def test_stack_only_candidates_remain_separate() -> None:
    stack_1 = _item(DiscoveryClassification.SEESTAR_STACK_FITS, "Stacked_0_a.fit", BASE_TIME)
    stack_2 = _item(DiscoveryClassification.SEESTAR_STACK_FITS, "Stacked_0_b.fit", BASE_TIME)

    result = reconstruct_seestar_observations(_inventory(stack_2, stack_1))

    assert len(result.observations) == 2
    assert all(
        observation.status is ObservationStatus.STACK_ONLY for observation in result.observations
    )
    assert [observation.stack.source_path.name for observation in result.observations] == [
        "Stacked_0_a.fit",
        "Stacked_0_b.fit",
    ]


def test_regular_cadence_lights_without_stack_form_conservative_lights_only_result() -> None:
    lights = tuple(
        _item(
            DiscoveryClassification.LIGHT_FITS,
            f"Light_{index}.fit",
            BASE_TIME + timedelta(seconds=index * 11),
        )
        for index in range(3)
    )

    result = reconstruct_seestar_observations(_inventory(*lights))

    assert len(result.observations) == 1
    assert result.observations[0].status is ObservationStatus.LIGHTS_ONLY
    assert result.observations[0].lights == lights


def test_large_gap_in_lights_only_data_is_explicitly_ambiguous() -> None:
    light_1 = _item(DiscoveryClassification.LIGHT_FITS, "Light_1.fit", BASE_TIME)
    light_2 = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_2.fit",
        BASE_TIME + timedelta(hours=2),
    )

    observation = reconstruct_seestar_observations(_inventory(light_1, light_2)).observations[0]

    assert observation.status is ObservationStatus.AMBIGUOUS
    assert "temporal gap" in " ".join(observation.problems)


def test_missing_timestamp_light_remains_unresolved() -> None:
    light = _item(DiscoveryClassification.LIGHT_FITS, "Light_without_time.fit", None)

    observation = reconstruct_seestar_observations(_inventory(light)).observations[0]

    assert observation.status is ObservationStatus.UNRESOLVED
    assert observation.lights == (light,)
    assert "No usable" in " ".join(observation.problems)


def test_filename_timestamp_is_used_when_fits_timestamp_is_missing() -> None:
    light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_target_20260103-220000.fit",
        None,
    )

    observation = reconstruct_seestar_observations(_inventory(light)).observations[0]

    assert observation.status is ObservationStatus.LIGHTS_ONLY
    assert observation.first_light_at == BASE_TIME
    assert "filename timestamp selected" in " ".join(observation.problems)


def test_missing_core_compatibility_evidence_remains_unresolved() -> None:
    light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_without_filter.fit",
        BASE_TIME,
        filter_name=None,
    )

    observation = reconstruct_seestar_observations(_inventory(light)).observations[0]

    assert observation.status is ObservationStatus.UNRESOLVED
    assert "sufficient evidence" in " ".join(observation.problems)


def test_light_too_distant_from_stack_is_not_silently_associated() -> None:
    light = _item(DiscoveryClassification.LIGHT_FITS, "Light_old.fit", BASE_TIME)
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_1_later.fit",
        BASE_TIME + timedelta(hours=13),
    )

    result = reconstruct_seestar_observations(_inventory(light, stack))

    assert (
        _observation_with_stack(result, "Stacked_1_later.fit").status
        is ObservationStatus.STACK_ONLY
    )
    assert any(observation.lights == (light,) for observation in result.observations)


def test_fits_timestamp_is_authoritative_without_comparing_filename_wall_time() -> None:
    light = _item(
        DiscoveryClassification.LIGHT_FITS,
        "Light_target_20260103-230000.fit",
        BASE_TIME,
    )

    observation = reconstruct_seestar_observations(_inventory(light)).observations[0]

    assert observation.first_light_at == BASE_TIME
    assert "FITS and filename timestamps differ" not in " ".join(observation.problems)


def test_chronological_order_uses_timestamp_not_filename() -> None:
    earlier = _item(DiscoveryClassification.LIGHT_FITS, "Z_later_name.fit", BASE_TIME)
    later = _item(
        DiscoveryClassification.LIGHT_FITS,
        "A_earlier_name.fit",
        BASE_TIME + timedelta(seconds=11),
    )
    stack = _item(
        DiscoveryClassification.SEESTAR_STACK_FITS,
        "Stacked_2_target.fit",
        BASE_TIME + timedelta(seconds=22),
    )

    observation = reconstruct_seestar_observations(_inventory(later, stack, earlier)).observations[
        0
    ]

    assert observation.lights == (earlier, later)


def test_unknown_and_jpeg_items_are_excluded_from_observations() -> None:
    light = _item(DiscoveryClassification.LIGHT_FITS, "Light.fit", BASE_TIME)
    jpeg = _non_frame(DiscoveryClassification.SEESTAR_JPEG, "preview.jpg")
    unknown = _non_frame(DiscoveryClassification.UNKNOWN, "bad.fit")

    result = reconstruct_seestar_observations(_inventory(jpeg, light, unknown))

    assert result.observations[0].lights == (light,)
    assert result.excluded_items == (jpeg, unknown)


def test_reconstruction_introduces_no_archive_path_or_numbering_fields() -> None:
    light = _item(DiscoveryClassification.LIGHT_FITS, "Light.fit", BASE_TIME)

    observation = reconstruct_seestar_observations(_inventory(light)).observations[0]

    assert not hasattr(observation, "observation_number")
    assert not hasattr(observation, "observation_directory")
    assert not hasattr(observation, "session_end_date")
    assert not hasattr(observation, "archive_path")
    assert not hasattr(observation, "tiff_path")


def test_reconstruction_does_not_mutate_source_file(tmp_path: Path) -> None:
    source = tmp_path / "Light.fit"
    source.write_bytes(b"source data")
    item = _item(DiscoveryClassification.LIGHT_FITS, "Light.fit", BASE_TIME)
    item = SeestarDiscoveryItem(
        source_path=source,
        classification=item.classification,
        source_directory=tmp_path,
        directory_context=item.directory_context,
        directory_target=item.directory_target,
        metadata_target=item.metadata_target,
        fits_inspection=item.fits_inspection,
    )
    stat = source.stat()
    digest = hashlib.sha256(source.read_bytes()).digest()

    reconstruct_seestar_observations(SeestarDiscoveryInventory(tmp_path, (item,)))

    final_stat = source.stat()
    assert final_stat.st_size == stat.st_size
    assert final_stat.st_mtime_ns == stat.st_mtime_ns
    assert hashlib.sha256(source.read_bytes()).digest() == digest
