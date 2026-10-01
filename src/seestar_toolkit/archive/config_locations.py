"""Prepare location edits and report matches without prompts or filesystem writes."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import tomlkit
from tomlkit.items import Array, Comment

from .config import _parse_config, _saved_location
from .config_document import ConfigDocument, ConfigEdit, ConfigSetting, _location_warnings
from .exceptions import ArchiveConfigError, ArchivePlanningConfigurationError
from .planning import _haversine_m, _template_tokens, normalize_archive_component
from .planning_models import SavedLocation


@dataclass(frozen=True)
class LocationMatch:
    location: SavedLocation
    distance_m: float


def _validated_document(raw):
    try:
        config = _parse_config(raw.unwrap())
        _template_tokens(config.hierarchy)
        return config
    except (ArchiveConfigError, ArchivePlanningConfigurationError) as error:
        raise ArchiveConfigError(
            f"Proposed configuration is invalid; not saved: {error}"
        ) from error


def _name_identity(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ArchiveConfigError("Location name must be a non-empty string")
    return name.strip().casefold()


def _find_location(document: ConfigDocument, name: str) -> int | None:
    identity = _name_identity(name)
    entries = document.raw.unwrap().get("locations", [])
    if not isinstance(entries, list):
        raise ArchiveConfigError("locations must be an array of tables; repair manually")
    matches = [
        index
        for index, entry in enumerate(entries)
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and entry["name"].strip().casefold() == identity
    ]
    if len(matches) > 1:
        raise ArchiveConfigError(f"Ambiguous location {name!r}; manual disambiguation is required")
    return matches[0] if matches else None


def _validate_edited_location(location: SavedLocation, others: tuple[SavedLocation, ...]) -> None:
    if location.name.strip() in {".", ".."}:
        raise ArchiveConfigError("Location name must not be '.' or '..'")
    if location.radius_m <= 0:
        raise ArchiveConfigError("An edited location radius_m must be strictly positive")
    identity = _name_identity(location.name)
    cleaned = normalize_archive_component(location.name).casefold()
    for other in others:
        if (
            identity == _name_identity(other.name)
            or cleaned == normalize_archive_component(other.name).casefold()
        ):
            raise ArchiveConfigError(
                f"Location name conflict: {location.name!r} and {other.name!r} "
                "share a logical or cleaned directory name"
            )
        distance = _haversine_m(
            location.latitude, location.longitude, other.latitude, other.longitude
        )
        if distance <= location.radius_m + other.radius_m + 1e-9:
            raise ArchiveConfigError(
                f"Locations {location.name!r} and {other.name!r} touch or overlap: "
                f"distance {distance:g} m; radii {location.radius_m:g}, {other.radius_m:g} m"
            )


def _edit_result(document, proposed, name, previous, following, mutated) -> ConfigEdit:
    config = _validated_document(proposed)
    original = document.state.content.decode("utf-8") if document.exists else ""
    text = tomlkit.dumps(proposed) if mutated else original
    _validated_document(tomlkit.parse(text))
    return ConfigEdit(
        document,
        text,
        f"location {name!r}",
        ConfigSetting(name, previous, "saved" if previous is not None else "absent"),
        ConfigSetting(name, following, "saved" if following is not None else "absent"),
        text != original,
        _location_warnings(config.saved_locations),
    )


def prepare_location_edit(
    document: ConfigDocument,
    name: str,
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_m: float | None = None,
    rename: str | None = None,
    update: bool = False,
) -> ConfigEdit:
    """Validate one combined creation/update; the caller owns update authorisation.

    None means an unspecified field. Invalid readable entries can be repaired
    provided the complete proposed document then satisfies the existing schema.
    """
    if all(value is None for value in (latitude, longitude, radius_m, rename)):
        raise ArchiveConfigError("At least one location change field is required")
    index = _find_location(document, name)
    if index is None and (update or rename is not None):
        raise ArchiveConfigError("--update and --rename require an existing location")
    previous = document.raw.unwrap()["locations"][index] if index is not None else None
    following: dict[str, Any] = (
        copy.deepcopy(previous)
        if previous is not None
        else {
            "name": name.strip(),
            "radius_m": 100.0,
        }
    )
    changes = {}
    if rename is not None:
        _name_identity(rename)
        changes["name"] = rename.strip()
    for key, value in (("latitude", latitude), ("longitude", longitude), ("radius_m", radius_m)):
        if value is not None:
            changes[key] = value
    following.update(changes)
    selected = _saved_location(following, index if index is not None else 0)
    proposed = copy.deepcopy(document.raw)
    mutated = index is None
    if index is None:
        if "locations" not in proposed:
            proposed["locations"] = tomlkit.aot()
        table = (
            tomlkit.inline_table() if isinstance(proposed["locations"], Array) else tomlkit.table()
        )
        table.update(following)
        proposed["locations"].append(table)
    else:
        for key, value in changes.items():
            if (
                key not in previous
                or previous[key] != value
                or (isinstance(previous[key], bool) and not isinstance(value, bool))
            ):
                proposed["locations"][index][key] = value
                mutated = True
    config = _validated_document(proposed)
    selected_index = index if index is not None else len(config.saved_locations) - 1
    _validate_edited_location(
        selected,
        tuple(location for i, location in enumerate(config.saved_locations) if i != selected_index),
    )
    return _edit_result(document, proposed, name, previous, following, mutated)


def prepare_location_removal(document: ConfigDocument, name: str) -> ConfigEdit:
    """Remove only a unique named entry; unrelated new-rule conflicts may remain."""
    index = _find_location(document, name)
    proposed = copy.deepcopy(document.raw)
    previous = None
    if index is not None:
        previous = document.raw.unwrap()["locations"][index]
        removed = proposed["locations"][index]
        # Standalone notes can describe the following entry. Keep them even when
        # removing this table; its own field/inline comments belong to the deletion.
        if hasattr(removed.value, "body"):
            for key, item in removed.value.body:
                if key is None and isinstance(item, Comment):
                    proposed.add(copy.deepcopy(item))
        del proposed["locations"][index]
    return _edit_result(document, proposed, name, previous, None, index is not None)


def matching_locations(
    document: ConfigDocument, latitude: float, longitude: float
) -> tuple[LocationMatch, ...]:
    """Return every containing location in archive nearest/name tie-break order."""
    # No successful matching is reported against invalid configuration.
    config = _validated_document(document.raw)
    _saved_location(dict(name="query", latitude=latitude, longitude=longitude, radius_m=0), 0)
    matches = []
    for location in config.saved_locations:
        distance = _haversine_m(latitude, longitude, location.latitude, location.longitude)
        if distance <= location.radius_m + 1e-9:
            matches.append(LocationMatch(location, distance))
    return tuple(
        sorted(
            matches,
            key=lambda match: (
                match.distance_m,
                match.location.name.casefold(),
                match.location.name,
            ),
        )
    )
