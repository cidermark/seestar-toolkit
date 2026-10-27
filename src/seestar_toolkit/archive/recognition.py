"""Read-only recognition and destination inference for current archives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .exceptions import (
    ArchiveCanonicalLightsMissingError,
    ArchiveInferenceError,
    ArchivePathSafetyError,
)

_OBSERVATION_DIRECTORY = re.compile(r"observation_(?=\d{2,}$)0*[1-9]\d*")
_FITS_SUFFIXES = {".fit", ".fits"}


@dataclass(frozen=True, slots=True)
class ArchiveBatchInference:
    """Canonical source and inferred destination for one observation."""

    observation_directory: Path
    source_directory: Path
    inferred_output_directory: Path


@dataclass(frozen=True, slots=True)
class ArchivedLightInference:
    """An archived light and its inferred TIFF destination."""

    observation_directory: Path
    input_path: Path
    output_path: Path


def resolve_archive_batch_input(input_path: str | Path) -> ArchiveBatchInference:
    """Resolve a supported current-archive batch input without modifying it."""
    supplied = Path(input_path)
    observation = _observation_from_batch_input(supplied)
    _require_existing_observation(observation)

    source = observation / "fits_images" / "lights"
    if source.is_symlink() and not source.exists():
        raise ArchivePathSafetyError(f"Canonical lights path is an unsafe symlink: {source}")
    if not source.exists():
        raise ArchiveCanonicalLightsMissingError(
            f"Recognised observation is missing its canonical lights directory: {source}"
        )
    if not source.is_dir():
        raise ArchiveCanonicalLightsMissingError(
            f"Canonical lights path is not a directory: {source}"
        )

    output = observation / "tiff_images" / "lights"
    observation_real = observation.resolve(strict=True)
    _require_beneath_observation(observation_real, source.resolve(strict=True), "lights path")
    _require_beneath_observation(
        observation_real, output.resolve(strict=False), "inferred destination"
    )
    return ArchiveBatchInference(
        observation_directory=observation,
        source_directory=source,
        inferred_output_directory=output,
    )


def infer_archived_light_destination(input_path: str | Path) -> ArchivedLightInference:
    """Infer a TIFF path for one direct current-archive light without conversion."""
    source = Path(input_path)
    if source.suffix.lower() not in _FITS_SUFFIXES:
        raise ArchiveInferenceError(
            f"Archive destination inference requires a .fit or .fits archived light: {source}"
        )

    lights = source.parent
    if lights.name != "lights" or lights.parent.name != "fits_images":
        raise ArchiveInferenceError(
            "Input is not an archived light directly under "
            f"observation_NN/fits_images/lights: {source}"
        )
    observation = lights.parent.parent
    if not _is_observation_name(observation.name):
        raise ArchiveInferenceError(
            f"Input is not within a recognised observation_NN current archive: {source}"
        )

    batch = resolve_archive_batch_input(lights)
    if source.is_symlink() and not source.exists():
        raise ArchivePathSafetyError(f"Archived light is an unsafe symlink: {source}")
    if not source.exists():
        raise ArchiveInferenceError(f"Archived light does not exist: {source}")
    if not source.is_file():
        raise ArchiveInferenceError(f"Archived light is not a file: {source}")

    observation_real = observation.resolve(strict=True)
    _require_beneath_observation(observation_real, source.resolve(strict=True), "archived light")
    output = batch.inferred_output_directory / f"{source.stem}.tiff"
    _require_beneath_observation(
        observation_real, output.resolve(strict=False), "inferred destination"
    )
    return ArchivedLightInference(
        observation_directory=observation,
        input_path=source,
        output_path=output,
    )


def _observation_from_batch_input(path: Path) -> Path:
    if _is_observation_name(path.name):
        return path
    if path.name == "fits_images" and _is_observation_name(path.parent.name):
        return path.parent
    if (
        path.name == "lights"
        and path.parent.name == "fits_images"
        and _is_observation_name(path.parent.parent.name)
    ):
        return path.parent.parent
    raise ArchiveInferenceError(
        "Path is not a recognised observation current archive input at "
        "observation_NN, fits_images, or "
        f"fits_images/lights: {path}"
    )


def _is_observation_name(name: str) -> bool:
    return _OBSERVATION_DIRECTORY.fullmatch(name) is not None


def _require_existing_observation(observation: Path) -> None:
    if observation.is_symlink() and not observation.exists():
        raise ArchivePathSafetyError(f"Observation path is an unsafe symlink: {observation}")
    if not observation.exists() or not observation.is_dir():
        raise ArchiveInferenceError(
            f"Path does not identify an existing recognised observation: {observation}"
        )


def _require_beneath_observation(observation: Path, candidate: Path, label: str) -> None:
    try:
        relative = candidate.relative_to(observation)
    except ValueError as error:
        raise ArchivePathSafetyError(
            f"Resolved {label} escapes the recognised observation: {candidate}"
        ) from error
    if not relative.parts:
        raise ArchivePathSafetyError(f"Resolved {label} is not beneath the observation")
