"""Read-only TOML configuration loading for archive workflows."""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .exceptions import ArchiveConfigError
from .execution_models import CollisionPolicy, SourceAction
from .planning_models import SavedLocation

DEFAULT_HIERARCHY = "{target}/{location}/{session_end_date}"


@dataclass(frozen=True, slots=True)
class ArchiveConfig:
    """Validated archive settings loaded from one optional TOML file."""

    hierarchy: str = DEFAULT_HIERARCHY
    source_action: SourceAction = SourceAction.COPY
    collision_policy: CollisionPolicy = CollisionPolicy.SKIP_IDENTICAL
    saved_locations: tuple[SavedLocation, ...] = ()


def default_archive_config_path() -> Path:
    """Return the deterministic default per-user archive configuration path."""
    return Path.home() / ".config" / "seestar-toolkit" / "config.toml"


def load_archive_config(path: str | Path | None = None) -> ArchiveConfig:
    """Load validated archive configuration without writing any files.

    A missing default path is equivalent to built-in defaults. A path supplied
    explicitly is required to exist. Unknown keys are ignored for forward
    compatibility.
    """
    explicit = path is not None
    config_path = Path(path) if explicit else default_archive_config_path()
    if not config_path.exists():
        if explicit:
            raise ArchiveConfigError(f"Archive configuration file does not exist: {config_path}")
        return ArchiveConfig()
    if not config_path.is_file():
        raise ArchiveConfigError(f"Archive configuration path is not a file: {config_path}")
    try:
        with config_path.open("rb") as config_file:
            data = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ArchiveConfigError(
            f"Unable to load archive configuration {config_path}: {error}"
        ) from error
    if not isinstance(data, dict):
        raise ArchiveConfigError("Archive configuration root must be a TOML table")
    return _parse_config(data)


def _parse_config(data: dict[str, Any]) -> ArchiveConfig:
    archive = data.get("archive", {})
    if not isinstance(archive, dict):
        raise ArchiveConfigError("[archive] must be a TOML table")
    hierarchy = archive.get("hierarchy", DEFAULT_HIERARCHY)
    if not isinstance(hierarchy, str):
        raise ArchiveConfigError("archive.hierarchy must be a string")
    source_action = _source_action(archive.get("source_action", "copy"))
    collision_policy = _collision_policy(archive.get("collision_policy", "skip-identical"))
    locations_data = data.get("locations", [])
    if not isinstance(locations_data, list):
        raise ArchiveConfigError("locations must be an array of tables")
    locations = tuple(_saved_location(value, index) for index, value in enumerate(locations_data))
    return ArchiveConfig(
        hierarchy=hierarchy,
        source_action=source_action,
        collision_policy=collision_policy,
        saved_locations=locations,
    )


def _source_action(value: Any) -> SourceAction:
    if not isinstance(value, str):
        raise ArchiveConfigError("archive.source_action must be 'copy' or 'move'")
    mapping = {"copy": SourceAction.COPY, "move": SourceAction.MOVE}
    try:
        return mapping[value.casefold()]
    except KeyError as error:
        raise ArchiveConfigError(f"Unsupported archive source action: {value!r}") from error


def _collision_policy(value: Any) -> CollisionPolicy:
    if not isinstance(value, str):
        raise ArchiveConfigError(
            "archive.collision_policy must be 'skip-identical', 'error', or 'overwrite'"
        )
    mapping = {
        "skip-identical": CollisionPolicy.SKIP_IDENTICAL,
        "error": CollisionPolicy.ERROR,
        "overwrite": CollisionPolicy.OVERWRITE,
    }
    try:
        return mapping[value.casefold()]
    except KeyError as error:
        raise ArchiveConfigError(f"Unsupported archive collision policy: {value!r}") from error


def _saved_location(value: Any, index: int) -> SavedLocation:
    label = f"locations[{index}]"
    if not isinstance(value, dict):
        raise ArchiveConfigError(f"{label} must be a TOML table")
    missing = tuple(
        key for key in ("name", "latitude", "longitude", "radius_m") if key not in value
    )
    if missing:
        raise ArchiveConfigError(f"{label} is missing required fields: {', '.join(missing)}")
    name = value["name"]
    if not isinstance(name, str) or not name.strip():
        raise ArchiveConfigError(f"{label}.name must be a non-empty string")
    latitude = _finite_number(value["latitude"], f"{label}.latitude")
    longitude = _finite_number(value["longitude"], f"{label}.longitude")
    radius = _finite_number(value["radius_m"], f"{label}.radius_m")
    if not -90 <= latitude <= 90:
        raise ArchiveConfigError(f"{label}.latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ArchiveConfigError(f"{label}.longitude must be between -180 and 180")
    if radius < 0:
        raise ArchiveConfigError(f"{label}.radius_m must be non-negative")
    return SavedLocation(name=name, latitude=latitude, longitude=longitude, radius_m=radius)


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ArchiveConfigError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ArchiveConfigError(f"{field} must be finite")
    return number
