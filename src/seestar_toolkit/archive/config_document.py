"""Document-aware configuration inspection and scalar edits, independent of any UI."""

from __future__ import annotations

import copy
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import TOMLKitError
from tomlkit.toml_document import TOMLDocument

from .config import (
    DEFAULT_HIERARCHY,
    DEFAULT_OBSERVATION_DATE_POLICY,
    _collision_policy,
    _observation_date_policy,
    _parse_config,
    _saved_location,
    _source_action,
    default_archive_config_path,
    resolve_config_path,
)
from .exceptions import ArchiveConfigError, ArchivePlanningConfigurationError
from .planning import _haversine_m, _template_tokens, normalize_archive_component

BUILTIN_SETTINGS = {
    "archive.hierarchy": DEFAULT_HIERARCHY,
    "archive.source_action": "copy",
    "archive.collision_policy": "skip-identical",
    "archive.observation_date_policy": DEFAULT_OBSERVATION_DATE_POLICY,
}


@dataclass(frozen=True)
class ConfigState:
    target: Path
    content: bytes | None
    metadata: tuple[int, ...] | None
    links: tuple[tuple[str, int, int, int, int], ...]


@dataclass(frozen=True)
class ConfigDocument:
    path: Path
    explicit: bool
    state: ConfigState
    raw: TOMLDocument

    @property
    def target(self) -> Path:
        return self.state.target

    @property
    def exists(self) -> bool:
        return self.state.content is not None


@dataclass(frozen=True)
class ConfigSetting:
    name: str
    value: Any
    source: str
    error: str | None = None


@dataclass(frozen=True)
class ConfigInspection:
    settings: tuple[ConfigSetting, ...]
    locations: tuple[Any, ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ConfigEdit:
    document: ConfigDocument
    text: str
    setting: str
    previous: ConfigSetting
    proposed: ConfigSetting
    changed: bool
    warnings: tuple[str, ...]


def _file_metadata(info: os.stat_result) -> tuple[int, ...]:
    # Reads may update access time; only identity, content metadata and permissions matter.
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        info.st_mode,
    )


def _state(path: Path, explicit: bool) -> ConfigState:
    target, exists = resolve_config_path(path, explicit=explicit)
    links = []
    for part in (*path.parents, path):
        if part.is_symlink():
            info = part.lstat()
            links.append((str(part), info.st_dev, info.st_ino, info.st_mtime_ns, info.st_ctime_ns))
    if not exists:
        return ConfigState(target, None, None, tuple(links))
    before = target.stat()
    content = target.read_bytes()
    after = target.stat()
    if _file_metadata(before) != _file_metadata(after):
        raise ArchiveConfigError("Configuration changed while reading; retry")
    metadata = _file_metadata(after)
    return ConfigState(target, content, metadata, tuple(links))


def read_config_document(path: str | Path | None = None) -> ConfigDocument:
    """Read raw TOML, retaining invalid known values for inspection and targeted repair."""
    selected = (Path(path) if path is not None else default_archive_config_path()).absolute()
    try:
        state = _state(selected, path is not None)
        raw = (
            tomlkit.parse(state.content.decode("utf-8"))
            if state.content is not None
            else tomlkit.document()
        )
        # Recheck resolution as well as bytes after reading/parsing a possible link.
        if state != _state(selected, path is not None):
            raise ArchiveConfigError("Configuration changed while reading; retry")
        return ConfigDocument(selected, path is not None, state, raw)
    except (OSError, UnicodeError, TOMLKitError) as error:
        raise ArchiveConfigError(f"Unable to read configuration {selected}: {error}") from error


def _scalar_value(name: str, value: Any) -> str:
    try:
        if name == "archive.hierarchy":
            if not isinstance(value, str):
                raise ArchiveConfigError("archive.hierarchy must be a string")
            _template_tokens(value)
            return value
        if name == "archive.source_action":
            return _source_action(value).name.lower()
        if name == "archive.collision_policy":
            return _collision_policy(value).name.lower().replace("_", "-")
        if name == "archive.observation_date_policy":
            return _observation_date_policy(value)
    except ArchivePlanningConfigurationError as error:
        raise ArchiveConfigError(f"{name}: {error}") from error
    raise ArchiveConfigError(f"Unsupported preference: {name}")


def _location_warnings(locations) -> tuple[str, ...]:
    warnings = []
    for index, location in enumerate(locations):
        if location.radius_m == 0:
            warnings.append(f"Location {location.name!r} has a legacy zero radius")
        for other in locations[:index]:
            if location.name.strip().casefold() == other.name.strip().casefold():
                warnings.append(
                    f"Legacy duplicate location name: {location.name!r}, {other.name!r}"
                )
            elif (
                normalize_archive_component(location.name).casefold()
                == normalize_archive_component(other.name).casefold()
            ):
                warnings.append(
                    f"Legacy cleaned location name conflict: {location.name!r}, {other.name!r}"
                )
            try:
                distance = _haversine_m(
                    location.latitude, location.longitude, other.latitude, other.longitude
                )
            except ValueError:
                warnings.append(
                    f"Unable to compare location circles: {location.name!r}, {other.name!r}"
                )
                continue
            if distance <= location.radius_m + other.radius_m + 1e-9:
                warnings.append(
                    f"Legacy touching/overlapping locations: {location.name!r}, {other.name!r} "
                    f"(distance {distance:g} m; radii {location.radius_m:g}, {other.radius_m:g} m)"
                )
    return tuple(warnings)


def inspect_config_document(document: ConfigDocument) -> ConfigInspection:
    """Resolve each managed scalar independently; never disguise an invalid value as a default."""
    raw = document.raw.unwrap()
    archive = raw.get("archive", {})
    errors = []
    settings = []
    for name, default in BUILTIN_SETTINGS.items():
        key = name.split(".")[1]
        if not isinstance(archive, dict):
            error = "[archive] must be a TOML table"
            settings.append(ConfigSetting(name, archive, "saved", error))
            if error not in errors:
                errors.append(error)
            continue
        saved = key in archive
        value = archive.get(key, default)
        try:
            resolved = _scalar_value(name, value)
            settings.append(ConfigSetting(name, resolved, "saved" if saved else "default"))
        except ArchiveConfigError as error:
            errors.append(str(error))
            settings.append(ConfigSetting(name, value, "saved", str(error)))
    locations = raw.get("locations", [])
    valid_locations = []
    if not isinstance(locations, list):
        errors.append("locations must be an array of tables")
        locations = [locations]
    else:
        for index, value in enumerate(locations):
            try:
                valid_locations.append(_saved_location(value, index))
            except ArchiveConfigError as error:
                errors.append(str(error))
    return ConfigInspection(
        tuple(settings), tuple(locations), tuple(errors), _location_warnings(valid_locations)
    )


def prepare_archive_edit(
    document: ConfigDocument, setting: str, value: str | None = None
) -> ConfigEdit:
    """Prepare and fully validate a scalar set, or unset when value is None, without writing."""
    if setting not in BUILTIN_SETTINGS:
        raise ArchiveConfigError(f"Unsupported preference: {setting}")
    normalised = _scalar_value(setting, value) if value is not None else None
    inspection = inspect_config_document(document)
    previous = next(item for item in inspection.settings if item.name == setting)
    proposed = copy.deepcopy(document.raw)
    archive = proposed.get("archive")
    if archive is not None and not isinstance(archive, dict):
        raise ArchiveConfigError("[archive] must be a TOML table; repair its structure manually")
    key = setting.split(".")[1]
    mutated = False
    if value is None:
        if archive is not None and key in archive:
            comment = archive.item(key).trivia.comment
            del archive[key]
            if comment:
                archive.add(tomlkit.comment(comment.removeprefix("#").lstrip()))
            mutated = True
    elif not (
        previous.source == "saved" and previous.error is None and previous.value == normalised
    ):
        if archive is None:
            proposed["archive"] = tomlkit.table()
        proposed["archive"][key] = normalised
        mutated = True
    try:
        runtime = _parse_config(proposed.unwrap())
        _template_tokens(runtime.hierarchy)
    except (ArchiveConfigError, ArchivePlanningConfigurationError) as error:
        raise ArchiveConfigError(
            f"Proposed configuration is invalid; not saved: {error}"
        ) from error
    original = document.state.content.decode("utf-8") if document.exists else ""
    text = tomlkit.dumps(proposed) if mutated else original
    # Validate the serialised representation too before any filesystem mutation.
    _parse_config(tomlkit.parse(text).unwrap())
    next_setting = ConfigSetting(
        setting,
        normalised if value is not None else BUILTIN_SETTINGS[setting],
        "saved" if value is not None else "default",
    )
    return ConfigEdit(
        document,
        text,
        setting,
        previous,
        next_setting,
        text != original,
        _location_warnings(runtime.saved_locations),
    )


def _require_unchanged(document: ConfigDocument) -> None:
    try:
        current = _state(document.path, document.explicit)
    except (ArchiveConfigError, OSError) as error:
        raise ArchiveConfigError("Configuration changed or became inaccessible; retry") from error
    if current != document.state:
        raise ArchiveConfigError("Configuration changed since reading; retry")


def persist_config_edit(edit: ConfigEdit) -> None:
    """Persist a prepared edit atomically, preserving links and target permissions."""
    temporary = None
    try:
        _require_unchanged(edit.document)
        if not edit.changed:
            return
        target = edit.document.target
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor, name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        temporary = Path(name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(edit.text.encode("utf-8"))
            stream.flush()
            mode = stat.S_IMODE(edit.document.state.metadata[-1]) if edit.document.exists else 0o600
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        _require_unchanged(edit.document)
        os.replace(temporary, target)
    except OSError as error:
        raise ArchiveConfigError(
            f"Unable to save configuration {edit.document.path}: {error}"
        ) from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                raise ArchiveConfigError(
                    f"Unable to clean temporary configuration {temporary}: {error}"
                ) from error
