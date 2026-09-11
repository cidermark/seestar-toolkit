"""Derived, deterministic target-level archive index generation."""

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


def planned_index_paths(plan: ArchivePlan) -> tuple[Path, ...]:
    """Return deterministic concrete target-level index paths without I/O."""
    paths = {_target_directory(plan, observation) / "INDEX.md" for observation in plan.observations}
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
            rendered = _render(records)
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


def _target_directory(plan: ArchivePlan, observation: PlannedArchiveObservation) -> Path:
    tokens = plan.config.hierarchy_template.split("/")
    target_position = tokens.index("{target}")
    relative = observation.hierarchy_directory.relative_to(plan.config.archive_root)
    target_directory = plan.config.archive_root.joinpath(*relative.parts[: target_position + 1])
    _require_safe_path(plan.config.archive_root, target_directory / "INDEX.md")
    return target_directory


def _records_for_index(
    plan: ArchivePlan,
    index_path: Path,
    current_outcomes: dict[Path, ArchiveFileOutcome],
) -> tuple[_IndexObservation, ...]:
    target_directory = index_path.parent
    if not target_directory.exists():
        return ()
    records = []
    for observation_directory in sorted(
        (
            path
            for path in target_directory.rglob("observation_*")
            if path.is_dir() and ((path / "lights").is_dir() or (path / "seestar_stacked").is_dir())
        ),
        key=lambda path: path.as_posix(),
    ):
        record = _record_from_directory(
            plan, target_directory, observation_directory, current_outcomes
        )
        if record is not None:
            records.append(record)
    return tuple(
        sorted(
            records,
            key=lambda item: (item.location.casefold(), item.session_date, item.observation_name),
        )
    )


def _record_from_directory(
    plan: ArchivePlan,
    target_directory: Path,
    observation_directory: Path,
    current_outcomes: dict[Path, ArchiveFileOutcome],
) -> _IndexObservation | None:
    hierarchy_directory = observation_directory.parent
    relative = hierarchy_directory.relative_to(plan.config.archive_root)
    tokens = plan.config.hierarchy_template.split("/")
    if len(relative.parts) != len(tokens):
        return None
    values = dict(zip(tokens, relative.parts, strict=True))
    if target_directory != plan.config.archive_root.joinpath(
        *relative.parts[: tokens.index("{target}") + 1]
    ):
        return None
    light_paths = _established_fits(observation_directory / "lights", current_outcomes)
    stack_paths = _established_fits(observation_directory / "seestar_stacked", current_outcomes)
    if not light_paths and not stack_paths:
        return None
    light_inspections = tuple(inspect_fits(path) for path in light_paths)
    stack_path = stack_paths[0] if stack_paths else None
    stack_inspection = inspect_fits(stack_path) if stack_path else None
    evidence = (*light_inspections, *((stack_inspection,) if stack_inspection else ()))
    representative = evidence[0]
    first_light = _minimum(item.captured_at for item in light_inspections)
    last_light = _maximum(item.captured_at for item in light_inspections)
    return _IndexObservation(
        target=representative.object_name or values["{target}"],
        location=values["{location}"],
        session_date=values["{session_end_date}"],
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


def _render(records: tuple[_IndexObservation, ...]) -> str:
    lines = [f"# {_escape(records[0].target)}", ""]
    current_group = None
    for record in records:
        group = (record.location, record.session_date)
        if group != current_group:
            lines.extend(
                [f"## {_escape(record.location)} — {_display_date(record.session_date)}", ""]
            )
            current_group = group
        number = record.observation_name.removeprefix("observation_")
        lines.extend(
            [
                f"### Observation {_escape(number)}",
                "",
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
