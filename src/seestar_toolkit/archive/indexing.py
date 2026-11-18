"""Derived, deterministic archive index generation."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from seestar_toolkit.fits import FitsError, inspect_fits

from .execution_models import ArchiveExecutionResult, ArchiveFileOutcome
from .index_models import ArchiveIndexOutcome, ArchiveIndexResult
from .planning_models import ArchivePlan, PlannedArchiveObservation

_ESTABLISHED = frozenset(
    {
        ArchiveFileOutcome.COPIED,
        ArchiveFileOutcome.MOVED,
        ArchiveFileOutcome.SKIPPED_IDENTICAL,
    }
)
_FITS_SUFFIXES = frozenset({".fit", ".fits"})
_STACK_COUNT = re.compile(r"^stacked_(?P<count>\d+)_", re.IGNORECASE)
_MARKDOWN_SPECIAL = re.compile(r"([\\`*_[\]<>#|])")


@dataclass(frozen=True, slots=True)
class _IndexObservation:
    target: str
    archive_path: str
    location: str
    session_date: str
    observation_name: str
    telescope: str | None
    first_light: datetime | None
    last_light: datetime | None
    exposure: float | None
    filter_name: str | None
    light_count: int
    stack_filename: str | None
    reported_stack_count: int | None
    eq_mode: int | None
    latitude: float | None
    longitude: float | None


class _HistoricalTargetLookup:
    """Recover one historical target from the generated root-index record format."""

    def __init__(self, index_path: Path) -> None:
        self._index_path = index_path
        self._content: str | None = None

    def target_for(self, archive_path: str) -> str:
        content = self._read(archive_path)
        if not content.startswith("# Archive\n"):
            self._fail(archive_path, "index is malformed: missing archive heading")
        headings = tuple(re.finditer(r"^### Observation .+$", content, re.MULTILINE))
        if not headings:
            self._fail(archive_path, "index is malformed: no observation records")

        records: dict[str, list[str]] = {}
        for position, heading in enumerate(headings):
            end = headings[position + 1].start() if position + 1 < len(headings) else len(content)
            lines = content[heading.end() : end].splitlines()
            targets = [
                line.removeprefix("- Target: ") for line in lines if line.startswith("- Target: ")
            ]
            paths = [
                line.removeprefix("- Archive path: ")
                for line in lines
                if line.startswith("- Archive path: ")
            ]
            if len(paths) != 1 or len(targets) != 1 or not targets[0].strip():
                self._fail(archive_path, "index is malformed: incomplete observation record")
            records.setdefault(paths[0], []).append(targets[0])

        matches = records.get(archive_path, [])
        if not matches:
            self._fail(archive_path, "index has no exact matching record")
        unique_targets = set(matches)
        if len(matches) > 1:
            reason = (
                "index has ambiguous duplicate records"
                if len(unique_targets) == 1
                else "index has inconsistent targets for the same archive path"
            )
            self._fail(archive_path, reason)
        return matches[0]

    def _read(self, archive_path: str) -> str:
        if self._content is not None:
            return self._content
        try:
            self._content = self._index_path.read_text()
        except FileNotFoundError:
            self._fail(archive_path, "archive-root INDEX.md is missing")
        except (OSError, UnicodeError) as error:
            self._fail(archive_path, f"archive-root INDEX.md is unreadable: {error}")
        return self._content

    @staticmethod
    def _fail(archive_path: str, reason: str) -> None:
        raise ValueError(f"Historical target recovery failed for {archive_path}: {reason}")


def planned_index_paths(plan: ArchivePlan) -> tuple[Path, ...]:
    """Return deterministic target-level or archive-root index paths without I/O."""
    paths = {_index_directory(plan, observation) / "INDEX.md" for observation in plan.observations}
    return tuple(sorted(paths, key=lambda path: path.as_posix()))


def generate_archive_indexes(
    plan: ArchivePlan, execution: ArchiveExecutionResult
) -> tuple[ArchiveIndexResult, ...]:
    """Safely generate all target indexes represented by an executed plan."""
    outcomes = {result.destination_path: result.outcome for result in execution.files}
    results = []
    for index_path in planned_index_paths(plan):
        try:
            records = _records_for_index(plan, index_path, outcomes)
            if not records:
                continue
            rendered = _render(
                records,
                archive_root_index="{target}" not in plan.config.hierarchy_template.split("/"),
            )
            results.append(_write_index(plan.config.archive_root, index_path, rendered))
        except (FitsError, OSError, ValueError) as error:
            results.append(
                ArchiveIndexResult(
                    index_path=index_path,
                    outcome=ArchiveIndexOutcome.FAILED,
                    diagnostic=f"Index generation failed: {error}",
                )
            )
    return tuple(results)


def _index_directory(plan: ArchivePlan, observation: PlannedArchiveObservation) -> Path:
    tokens = plan.config.hierarchy_template.split("/")
    if "{target}" not in tokens:
        index_directory = plan.config.archive_root
    else:
        target_position = tokens.index("{target}")
        relative = observation.hierarchy_directory.relative_to(plan.config.archive_root)
        index_directory = plan.config.archive_root.joinpath(*relative.parts[: target_position + 1])
    _require_safe_path(plan.config.archive_root, index_directory / "INDEX.md")
    return index_directory


def _records_for_index(
    plan: ArchivePlan,
    index_path: Path,
    current_outcomes: dict[Path, ArchiveFileOutcome],
) -> tuple[_IndexObservation, ...]:
    index_directory = index_path.parent
    if not index_directory.exists():
        return ()
    archive_root_index = "{target}" not in plan.config.hierarchy_template.split("/")
    historical_targets = _HistoricalTargetLookup(index_path) if archive_root_index else None
    records = []
    for observation_directory in sorted(
        (
            path
            for path in index_directory.rglob("observation_*")
            if path.is_dir()
            and ((path / "fits_images" / "lights").is_dir() or (path / "seestar_stacked").is_dir())
        ),
        key=lambda path: path.as_posix(),
    ):
        record = _record_from_directory(
            plan,
            index_directory,
            observation_directory,
            current_outcomes,
            historical_targets=historical_targets,
        )
        if record is not None:
            records.append(record)
    return tuple(
        sorted(
            records,
            key=lambda item: (
                *((item.target.casefold(),) if archive_root_index else ()),
                item.location.casefold(),
                item.session_date,
                item.observation_name,
                *((item.archive_path,) if archive_root_index else ()),
            ),
        )
    )


def _record_from_directory(
    plan: ArchivePlan,
    index_directory: Path,
    observation_directory: Path,
    current_outcomes: dict[Path, ArchiveFileOutcome],
    *,
    historical_targets: _HistoricalTargetLookup | None = None,
) -> _IndexObservation | None:
    hierarchy_directory = observation_directory.parent
    relative = hierarchy_directory.relative_to(plan.config.archive_root)
    tokens = plan.config.hierarchy_template.split("/")
    if len(relative.parts) != len(tokens):
        return None
    values = dict(zip(tokens, relative.parts, strict=True))
    if "{target}" in tokens:
        expected_index_directory = plan.config.archive_root.joinpath(
            *relative.parts[: tokens.index("{target}") + 1]
        )
    else:
        expected_index_directory = plan.config.archive_root
    if index_directory != expected_index_directory:
        return None
    archive_path = observation_directory.relative_to(plan.config.archive_root).as_posix()
    if historical_targets is not None and _has_current_collision(
        observation_directory, current_outcomes
    ):
        raise ValueError(
            f"Root index publication is unsafe for {archive_path}: "
            "a current archive collision prevents reliable record regeneration"
        )
    light_paths = _established_fits(
        observation_directory / "fits_images" / "lights", current_outcomes
    )
    stack_paths = _established_fits(observation_directory / "seestar_stacked", current_outcomes)
    if not light_paths and not stack_paths:
        return None
    light_inspections = tuple(inspect_fits(path) for path in light_paths)
    stack_path = stack_paths[0] if stack_paths else None
    stack_inspection = inspect_fits(stack_path) if stack_path else None
    evidence = (*light_inspections, *((stack_inspection,) if stack_inspection else ()))
    first_light = _minimum(item.captured_at for item in light_inspections)
    last_light = _maximum(item.captured_at for item in light_inspections)
    planned = next(
        (item for item in plan.observations if item.observation_directory == observation_directory),
        None,
    )
    target = planned.metadata.logical_target if planned is not None else _fits_target(evidence)
    if target is None:
        target = values.get("{target}")
    if target is None:
        if historical_targets is None:
            target = "unknown"
        else:
            target = historical_targets.target_for(archive_path)
    return _IndexObservation(
        target=target,
        archive_path=archive_path,
        location=(
            values.get("{location}")
            or (planned.metadata.logical_location if planned is not None else "unknown")
        ),
        session_date=(
            values.get("{session_end_date}")
            or (planned.metadata.session_end_date if planned is not None else "unknown")
        ),
        observation_name=observation_directory.name,
        telescope=_first(item.telescope for item in evidence),
        first_light=first_light,
        last_light=last_light,
        exposure=_first(item.exposure_seconds for item in evidence),
        filter_name=_first(item.filter_name for item in evidence),
        light_count=len(light_paths),
        stack_filename=stack_path.name if stack_path else None,
        reported_stack_count=_reported_stack_count(stack_path),
        eq_mode=_first(item.eq_mode for item in evidence),
        latitude=_first(item.site_latitude for item in evidence),
        longitude=_first(item.site_longitude for item in evidence),
    )


def _has_current_collision(
    observation_directory: Path,
    current_outcomes: dict[Path, ArchiveFileOutcome],
) -> bool:
    return any(
        outcome is ArchiveFileOutcome.COLLISION
        and destination.is_relative_to(observation_directory)
        for destination, outcome in current_outcomes.items()
    )


def _fits_target(inspections) -> str | None:
    """Return the planner-compatible deterministic target from all FITS evidence."""
    unique: dict[str, str] = {}
    for inspection in inspections:
        value = inspection.object_name
        if value is not None and value.strip():
            unique.setdefault(value.strip().casefold(), value)
    return unique[min(unique)] if unique else None


def _established_fits(
    directory: Path, current_outcomes: dict[Path, ArchiveFileOutcome]
) -> tuple[Path, ...]:
    if not directory.is_dir():
        return ()
    return tuple(
        path
        for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        if path.is_file()
        and path.suffix.casefold() in _FITS_SUFFIXES
        and current_outcomes.get(path, ArchiveFileOutcome.SKIPPED_IDENTICAL) in _ESTABLISHED
    )


def _render(records: tuple[_IndexObservation, ...], *, archive_root_index: bool = False) -> str:
    lines = ["# Archive" if archive_root_index else f"# {_escape(records[0].target)}", ""]
    current_group = None
    for record in records:
        group = (
            (record.target, record.location, record.session_date)
            if archive_root_index
            else (record.location, record.session_date)
        )
        if group != current_group:
            heading = (
                f"## {_escape(record.target)} — {_escape(record.location)} — "
                f"{_display_date(record.session_date)}"
                if archive_root_index
                else f"## {_escape(record.location)} — {_display_date(record.session_date)}"
            )
            lines.extend([heading, ""])
            current_group = group
        number = record.observation_name.removeprefix("observation_")
        details = [
            f"### Observation {_escape(number)}",
            "",
        ]
        if archive_root_index:
            details.append(f"- Target: {_value(record.target)}")
            details.append(f"- Archive path: {record.archive_path}")
        details.extend(
            [
                f"- Telescope: {_value(record.telescope)}",
                f"- First light: {_datetime(record.first_light)}",
                f"- Last light: {_datetime(record.last_light)}",
                f"- Exposure: {_exposure(record.exposure)}",
                f"- Filter: {_value(record.filter_name)}",
                f"- Light subs: {record.light_count}",
                f"- Seestar stack: {_value(record.stack_filename, missing='none')}",
                f"- Seestar stack count: {_value(record.reported_stack_count)}",
                f"- Capture mode: {_capture_mode(record.eq_mode)}",
                f"- GPS: {_gps(record.latitude, record.longitude)}",
                "",
            ]
        )
        lines.extend(details)
    return "\n".join(lines)


def _write_index(archive_root: Path, index_path: Path, content: str) -> ArchiveIndexResult:
    _require_safe_path(archive_root, index_path)
    if index_path.is_symlink():
        raise OSError(f"Index path must not be a symlink: {index_path}")
    previous = index_path.read_text() if index_path.exists() else None
    if previous == content:
        return ArchiveIndexResult(index_path, ArchiveIndexOutcome.UNCHANGED)
    if not index_path.parent.is_dir():
        raise OSError(f"Index target directory does not exist: {index_path.parent}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".INDEX.md.", suffix=".tmp", dir=index_path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, index_path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    outcome = ArchiveIndexOutcome.CREATED if previous is None else ArchiveIndexOutcome.UPDATED
    return ArchiveIndexResult(index_path, outcome)


def _require_safe_path(archive_root: Path, path: Path) -> None:
    if not archive_root.is_absolute() or not path.is_absolute() or ".." in path.parts:
        raise OSError("Index path is not an absolute safe path")
    root_real = archive_root.resolve(strict=False)
    path_real = path.resolve(strict=False)
    if path_real == root_real:
        raise OSError("Index path must be beneath archive root")
    try:
        path_real.relative_to(root_real)
    except ValueError as error:
        raise OSError(f"Index path escapes archive root: {path}") from error


def _first(values):
    return next((value for value in values if value is not None), None)


def _minimum(values):
    present = tuple(value for value in values if value is not None)
    return min(present) if present else None


def _maximum(values):
    present = tuple(value for value in values if value is not None)
    return max(present) if present else None


def _reported_stack_count(path: Path | None) -> int | None:
    if path is None:
        return None
    match = _STACK_COUNT.match(path.name)
    return int(match.group("count")) if match else None


def _escape(value: object) -> str:
    return _MARKDOWN_SPECIAL.sub(r"\\\1", str(value).replace("\n", " ").replace("\r", " "))


def _value(value: object | None, *, missing: str = "unknown") -> str:
    return missing if value is None else str(value).replace("\n", " ").replace("\r", " ")


def _datetime(value: datetime | None) -> str:
    return "unknown" if value is None else value.isoformat(sep=" ", timespec="seconds")


def _exposure(value: float | None) -> str:
    return "unknown" if value is None else f"{value:.1f} s"


def _capture_mode(value: int | None) -> str:
    return {0: "Alt-Az", 1: "Equatorial"}.get(value, "unknown")


def _gps(latitude: float | None, longitude: float | None) -> str:
    if latitude is None or longitude is None:
        return "unknown"
    return f"{latitude:.6f}, {longitude:.6f}"


def _display_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    except ValueError:
        return _escape(value)
