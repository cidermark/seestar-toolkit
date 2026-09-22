"""Command-line interface for Seestar Toolkit."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from seestar_toolkit import __version__
from seestar_toolkit.archive import (
    ArchiveConfigError,
    ArchiveDiscoveryError,
    ArchiveExecutionError,
    ArchiveFileOutcome,
    ArchiveIndexOutcome,
    ArchivePlanningError,
    ArchiveTiffOutcome,
    CollisionPolicy,
    PreparedSeestarArchive,
    SavedLocation,
    SeestarArchiveStatus,
    SourceAction,
    execute_prepared_seestar_archive,
    load_archive_config,
    plan_seestar_archive,
    planned_index_paths,
    prepare_seestar_archive,
)
from seestar_toolkit.batch import convert_fits_directory
from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import FitsError
from seestar_toolkit.tiff import TiffError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seestar-toolkit",
        description="Convert supported FIT/FITS images into linear RGB TIFF files.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging.",
    )

    subparsers = parser.add_subparsers(dest="command")

    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert one FIT/FITS image to one TIFF.",
        description=(
            "Convert one FIT/FITS image to one TIFF. Supported inputs include raw Seestar "
            "Bayer, native Seestar RGB, and Siril RGB images."
        ),
    )
    convert_parser.add_argument(
        "input_fits",
        metavar="INPUT_FITS",
        type=Path,
        help="Input FIT/FITS image path.",
    )
    convert_parser.add_argument(
        "output_tiff",
        metavar="OUTPUT_TIFF",
        type=Path,
        help="Explicit output TIFF path.",
    )

    batch_parser = subparsers.add_parser(
        "convert-batch",
        help="Convert a flat directory of FIT/FITS images to TIFF.",
        description=(
            "Convert supported FIT/FITS files in one non-recursive input directory "
            "to an explicit output directory."
        ),
    )
    batch_parser.add_argument(
        "input_directory",
        metavar="INPUT_DIR",
        type=Path,
        help="Input directory scanned non-recursively for FIT/FITS files.",
    )

    archive_parser = subparsers.add_parser(
        "archive",
        help="Plan or execute a Seestar session archive.",
        description=(
            "Discover and reconstruct a Seestar work directory, plan its archive, "
            "archive FITS originals, and create a TIFF companion for each Seestar stack."
        ),
    )
    archive_parser.add_argument("source_root", metavar="SOURCE_ROOT", type=Path)
    archive_parser.add_argument("archive_root", metavar="ARCHIVE_ROOT", type=Path)
    archive_parser.add_argument(
        "--dry-run", action="store_true", help="Show the archive plan without writing files."
    )
    archive_parser.add_argument("--location", help="Use this location for every observation.")
    archive_parser.add_argument(
        "--hierarchy", help="Archive hierarchy template; overrides configuration."
    )
    archive_parser.add_argument(
        "--source-action",
        choices=("copy", "move"),
        help="Archive originals by copy (default) or explicit move.",
    )
    archive_parser.add_argument(
        "--collision-policy",
        choices=("skip-identical", "error", "overwrite"),
        help="Policy for existing FITS destinations (default: skip-identical).",
    )
    archive_parser.add_argument(
        "--non-interactive", action="store_true", help="Never prompt for a location."
    )
    archive_parser.add_argument(
        "--config", type=Path, metavar="PATH", help="Explicit archive TOML configuration."
    )
    batch_parser.add_argument(
        "output_directory",
        metavar="OUTPUT_DIR",
        type=Path,
        help="Explicit flat output directory for stem-matched .tiff files.",
    )

    return parser


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "convert":
        try:
            destination = convert_fits_to_tiff(args.input_fits, args.output_tiff)
        except (FitsError, TiffError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        print(f"Created TIFF: {destination}")
        return 0

    if args.command == "convert-batch":
        try:
            result = convert_fits_directory(args.input_directory, args.output_directory)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        for success in result.successes:
            print(f"Created TIFF: {success.output_path}")
        for failure in result.failures:
            print(f"Failed: {failure.input_path} — {failure.reason}", file=sys.stderr)

        if result.discovered_count == 0:
            print(
                f"No FIT/FITS files found in: {args.input_directory}",
                file=sys.stderr,
            )
        print(
            f"Batch complete: {result.discovered_count} discovered, "
            f"{result.succeeded_count} converted, {result.failed_count} failed"
        )
        return 0 if result.discovered_count > 0 and result.failed_count == 0 else 1

    if args.command == "archive":
        return _run_archive(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


def _run_archive(args: argparse.Namespace) -> int:
    try:
        config = load_archive_config(args.config)
        hierarchy = args.hierarchy if args.hierarchy is not None else config.hierarchy
        action = (
            {"copy": SourceAction.COPY, "move": SourceAction.MOVE}[args.source_action]
            if args.source_action is not None
            else config.source_action
        )
        collision_policy = (
            {
                "skip-identical": CollisionPolicy.SKIP_IDENTICAL,
                "error": CollisionPolicy.ERROR,
                "overwrite": CollisionPolicy.OVERWRITE,
            }[args.collision_policy]
            if args.collision_policy is not None
            else config.collision_policy
        )
        explicit_location = _explicit_location(args.location)
        prepared = prepare_seestar_archive(
            args.source_root,
            archive_root=args.archive_root,
            hierarchy_template=hierarchy,
            explicit_location=explicit_location,
            saved_locations=config.saved_locations,
        )
        interactive = not args.non_interactive and sys.stdin.isatty()
        if interactive and explicit_location is None:
            prepared = _resolve_interactive_location(prepared, config.saved_locations)
        if args.dry_run:
            _print_archive_plan(prepared, action, collision_policy)
            return 1 if prepared.has_operational_problems else 0
        result = execute_prepared_seestar_archive(
            prepared,
            source_action=action,
            collision_policy=collision_policy,
        )
    except (
        ArchiveConfigError,
        ArchiveDiscoveryError,
        ArchivePlanningError,
        ArchiveExecutionError,
        OSError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    _print_archive_result(result)
    return 0 if result.status is SeestarArchiveStatus.COMPLETE else 1


def _explicit_location(value: str | None) -> str | None:
    if value is None:
        return None
    location = value.strip()
    if not location:
        raise ArchiveConfigError("--location must not be empty")
    return location


def _resolve_interactive_location(
    prepared: PreparedSeestarArchive, saved_locations: tuple[SavedLocation, ...]
) -> PreparedSeestarArchive:
    locations = {item.metadata.logical_location for item in prepared.plan.observations}
    if len(locations) > 1:
        return prepared
    current = next(iter(locations), "unknown")
    saved_names = {location.name for location in saved_locations}
    if current in saved_names:
        answer = input(f"Location matched: {current}. Use this location? [Y/n] ").strip()
        if answer.casefold() not in {"", "y", "yes"}:
            return _replan_with_manual_location(prepared)
        return prepared
    if current == "unknown":
        coordinates = {
            (item.metadata.source_latitude, item.metadata.source_longitude)
            for item in prepared.plan.observations
            if item.metadata.source_latitude is not None
            and item.metadata.source_longitude is not None
        }
        if len(coordinates) > 1:
            raise ArchiveConfigError(
                "Multiple unmatched observation locations require --location or --non-interactive"
            )
        return _replan_with_manual_location(prepared)
    return prepared


def _replan_with_manual_location(prepared: PreparedSeestarArchive) -> PreparedSeestarArchive:
    entered = input("Location name (blank for unknown): ").strip() or "unknown"
    config = prepared.plan.config
    plan = plan_seestar_archive(
        prepared.reconstruction,
        archive_root=config.archive_root,
        hierarchy_template=config.hierarchy_template,
        explicit_location=entered,
        saved_locations=config.saved_locations,
    )
    return PreparedSeestarArchive(
        discovery=prepared.discovery,
        reconstruction=prepared.reconstruction,
        plan=plan,
    )


def _print_archive_plan(
    prepared: PreparedSeestarArchive,
    action: SourceAction,
    collision_policy: CollisionPolicy,
) -> None:
    print(
        f"Dry run: {len(prepared.plan.observations)} observation(s); "
        f"action={action.name.lower()}; collision={collision_policy.name.lower()}"
    )
    for observation in prepared.plan.observations:
        metadata = observation.metadata
        print(
            f"Plan {observation.observation_name}: target={metadata.logical_target}; "
            f"location={metadata.logical_location}; date={metadata.session_end_date}; "
            f"destination={observation.observation_directory}"
        )
        for planned in (*observation.lights, *((observation.stack,) if observation.stack else ())):
            message = f"  FITS {planned.source_path} -> {planned.fits_destination}"
            if planned.tiff_destination is not None:
                message += f"; TIFF -> {planned.tiff_destination}"
            print(message)
    for problem in prepared.plan.problems:
        print(f"Planning problem: {'; '.join(problem.messages)}", file=sys.stderr)
    for item in prepared.discovery.items:
        if item.problem:
            print(f"Discovery problem: {item.source_path}: {item.problem}", file=sys.stderr)
    for index_path in planned_index_paths(prepared.plan):
        print(f"Index: {index_path}")


def _print_archive_result(result) -> None:
    execution = result.execution
    print(
        f"Archive {result.status.name.lower()}: {execution.copied_count} copied, "
        f"{execution.moved_count} moved, {execution.skipped_count} skipped identical, "
        f"{execution.failed_count} original failures"
    )
    created = sum(item.outcome is ArchiveTiffOutcome.CREATED for item in result.tiffs)
    failed = len(result.tiffs) - created
    print(f"TIFFs: {created} created, {failed} skipped/collided/failed")
    index_counts = {
        outcome: sum(item.outcome is outcome for item in result.indexes)
        for outcome in ArchiveIndexOutcome
    }
    print(
        f"Indexes: {index_counts[ArchiveIndexOutcome.CREATED]} created, "
        f"{index_counts[ArchiveIndexOutcome.UPDATED]} updated, "
        f"{index_counts[ArchiveIndexOutcome.UNCHANGED]} unchanged, "
        f"{index_counts[ArchiveIndexOutcome.FAILED]} failed"
    )
    for item in execution.files:
        if item.outcome in {
            ArchiveFileOutcome.COLLISION,
            ArchiveFileOutcome.FAILED,
            ArchiveFileOutcome.PARTIAL,
        }:
            print(
                f"Original {item.outcome.name.lower()}: {item.source_path}: {item.diagnostic}",
                file=sys.stderr,
            )
    for item in result.tiffs:
        if item.outcome is not ArchiveTiffOutcome.CREATED:
            print(
                f"TIFF {item.outcome.name.lower()}: {item.tiff_destination}: {item.diagnostic}",
                file=sys.stderr,
            )
    for item in result.indexes:
        if item.outcome is ArchiveIndexOutcome.FAILED:
            print(f"Index failed: {item.index_path}: {item.diagnostic}", file=sys.stderr)
