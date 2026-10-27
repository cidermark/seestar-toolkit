"""Tests for read-only current-archive recognition and destination inference."""

from __future__ import annotations

from pathlib import Path

import pytest

from seestar_toolkit.archive import (
    ArchiveCanonicalLightsMissingError,
    ArchiveInferenceError,
    ArchivePathSafetyError,
    infer_archived_light_destination,
    resolve_archive_batch_input,
)


def _observation(tmp_path: Path, *, lights: bool = True) -> Path:
    observation = tmp_path / "Target/Home/20261027/observation_01"
    if lights:
        (observation / "fits_images/lights").mkdir(parents=True)
    else:
        observation.mkdir(parents=True)
    return observation


@pytest.mark.parametrize("input_level", ("observation", "fits_images", "lights"))
def test_batch_forms_resolve_current_observation(tmp_path: Path, input_level: str) -> None:
    observation = _observation(tmp_path)
    inputs = {
        "observation": observation,
        "fits_images": observation / "fits_images",
        "lights": observation / "fits_images/lights",
    }

    result = resolve_archive_batch_input(inputs[input_level])

    assert result.observation_directory == observation
    assert result.source_directory == observation / "fits_images/lights"
    assert result.inferred_output_directory == observation / "tiff_images/lights"


def test_batch_recognition_accepts_empty_lights_and_does_not_create_output(
    tmp_path: Path,
) -> None:
    observation = _observation(tmp_path)

    result = resolve_archive_batch_input(observation)

    assert result.source_directory.is_dir()
    assert tuple(result.source_directory.iterdir()) == ()
    assert not result.inferred_output_directory.exists()


def test_batch_recognition_does_not_require_archive_siblings_or_ancestors(
    tmp_path: Path,
) -> None:
    observation = tmp_path / "observation_123"
    (observation / "fits_images/lights").mkdir(parents=True)

    result = resolve_archive_batch_input(observation)

    assert result.observation_directory == observation


@pytest.mark.parametrize("suffix", (".fit", ".fits", ".FIT", ".FiTs"))
def test_single_file_inference_preserves_stem_and_accepts_fits_suffixes(
    tmp_path: Path, suffix: str
) -> None:
    observation = _observation(tmp_path)
    source = observation / "fits_images/lights" / f"Light M 42.v1{suffix}"
    source.write_bytes(b"not inspected")

    result = infer_archived_light_destination(source)

    assert result.observation_directory == observation
    assert result.input_path == source
    assert result.output_path == observation / "tiff_images/lights/Light M 42.v1.tiff"
    assert not (observation / "tiff_images").exists()


def test_existing_tiff_directory_is_accepted_without_inspection(tmp_path: Path) -> None:
    observation = _observation(tmp_path)
    output = observation / "tiff_images/lights"
    output.mkdir(parents=True)
    (output / "existing.tiff").write_bytes(b"existing")

    result = resolve_archive_batch_input(observation)

    assert result.inferred_output_directory == output


def test_missing_canonical_lights_is_distinct_from_unrecognised_input(tmp_path: Path) -> None:
    observation = _observation(tmp_path, lights=False)

    with pytest.raises(ArchiveCanonicalLightsMissingError, match="canonical lights"):
        resolve_archive_batch_input(observation)

    ordinary = tmp_path / "ordinary"
    ordinary.mkdir()
    with pytest.raises(ArchiveInferenceError, match="recognised observation"):
        resolve_archive_batch_input(ordinary)


@pytest.mark.parametrize(
    "relative",
    (
        "lights/source.fit",
        "seestar_stacked/stack.fit",
        "fits_images/lights/source.txt",
    ),
)
def test_single_file_rejects_historical_stack_and_non_fits_paths(
    tmp_path: Path, relative: str
) -> None:
    observation = _observation(tmp_path)
    source = observation / relative
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"fixture")

    with pytest.raises(ArchiveInferenceError):
        infer_archived_light_destination(source)

    assert not (observation / "tiff_images").exists()


def test_single_file_rejects_non_archive_path(tmp_path: Path) -> None:
    source = tmp_path / "source.fit"
    source.write_bytes(b"fixture")

    with pytest.raises(ArchiveInferenceError, match="archived light"):
        infer_archived_light_destination(source)


def test_batch_rejects_historical_layout(tmp_path: Path) -> None:
    observation = _observation(tmp_path, lights=False)
    historical = observation / "lights"
    historical.mkdir()

    with pytest.raises(ArchiveInferenceError, match="current archive input"):
        resolve_archive_batch_input(historical)


def test_single_file_rejects_symlink_escape_without_side_effects(tmp_path: Path) -> None:
    observation = _observation(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    source = outside / "source.fit"
    source.write_bytes(b"fixture")
    archived_link = observation / "fits_images/lights/source.fit"
    archived_link.symlink_to(source)

    with pytest.raises(ArchivePathSafetyError, match="escapes"):
        infer_archived_light_destination(archived_link)

    assert not (observation / "tiff_images").exists()


def test_batch_rejects_canonical_lights_symlink_escape(tmp_path: Path) -> None:
    observation = _observation(tmp_path, lights=False)
    outside = tmp_path / "outside"
    outside.mkdir()
    fits_images = observation / "fits_images"
    fits_images.mkdir()
    (fits_images / "lights").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ArchivePathSafetyError, match="escapes"):
        resolve_archive_batch_input(observation)

    assert not (observation / "tiff_images").exists()


def test_inferred_output_symlink_escape_is_rejected(tmp_path: Path) -> None:
    observation = _observation(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (observation / "tiff_images").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ArchivePathSafetyError, match="escapes"):
        resolve_archive_batch_input(observation)

    assert tuple(outside.iterdir()) == ()
