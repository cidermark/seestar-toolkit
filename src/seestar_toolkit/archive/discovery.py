"""Read-only discovery of known shallow Seestar work-root content."""

from __future__ import annotations

from pathlib import Path

from seestar_toolkit.fits import FitsError, FitsImageClass, FitsInspection, inspect_fits

from .exceptions import ArchiveDiscoveryError
from .models import (
    DiscoveryClassification,
    SeestarDiscoveryInventory,
    SeestarDiscoveryItem,
    SourceDirectoryContext,
)
from .target_comparison import directory_target_for_comparison

_FITS_SUFFIXES = {".fit", ".fits"}
_JPEG_SUFFIXES = {".jpg", ".jpeg"}
_SUB_DIRECTORY_SUFFIX = "_sub"


def discover_seestar_inputs(root: str | Path) -> SeestarDiscoveryInventory:
    """Discover source candidates beneath one shallow Seestar work root.

    Files directly in the root and directly in its child directories are
    inspected. Deeper directories are deliberately outside Stage 7.1b.
    Individual FITS failures are retained as unknown discovery items; invalid
    root requests fail the whole operation.
    """
    work_root = Path(root)
    if not work_root.exists():
        raise ArchiveDiscoveryError(f"Seestar input root does not exist: {work_root}")
    if not work_root.is_dir():
        raise ArchiveDiscoveryError(f"Seestar input root is not a directory: {work_root}")

    items = tuple(_classify_candidate(work_root, path) for path in _candidate_paths(work_root))
    return SeestarDiscoveryInventory(root=work_root, items=items)


def _candidate_paths(root: Path) -> tuple[Path, ...]:
    candidates: list[Path] = []
    for child in root.iterdir():
        if child.is_file():
            candidates.append(child)
        elif child.is_dir():
            candidates.extend(path for path in child.iterdir() if path.is_file())
    return tuple(sorted(candidates, key=lambda path: path.relative_to(root).as_posix()))


def _classify_candidate(root: Path, path: Path) -> SeestarDiscoveryItem:
    source_directory = path.parent
    context, directory_target = _directory_evidence(root, source_directory)
    suffix = path.suffix.casefold()

    if suffix in _FITS_SUFFIXES:
        return _classify_fits(path, source_directory, context, directory_target)

    if suffix in _JPEG_SUFFIXES:
        classification = (
            DiscoveryClassification.THUMBNAIL_JPEG
            if path.stem.casefold().endswith("_thn")
            else DiscoveryClassification.SEESTAR_JPEG
        )
        return SeestarDiscoveryItem(
            source_path=path,
            classification=classification,
            source_directory=source_directory,
            directory_context=context,
            directory_target=directory_target,
            metadata_target=None,
            fits_inspection=None,
        )

    return SeestarDiscoveryItem(
        source_path=path,
        classification=DiscoveryClassification.UNKNOWN,
        source_directory=source_directory,
        directory_context=context,
        directory_target=directory_target,
        metadata_target=None,
        fits_inspection=None,
        problem=f"Unsupported source-file extension: {path.suffix or '<none>'}",
    )


def _classify_fits(
    path: Path,
    source_directory: Path,
    context: SourceDirectoryContext,
    directory_target: str | None,
) -> SeestarDiscoveryItem:
    try:
        inspection = inspect_fits(path)
    except FitsError as error:
        return SeestarDiscoveryItem(
            source_path=path,
            classification=DiscoveryClassification.UNKNOWN,
            source_directory=source_directory,
            directory_context=context,
            directory_target=directory_target,
            metadata_target=None,
            fits_inspection=None,
            problem=str(error),
        )

    classification, problem = _fits_discovery_classification(path, context, inspection)
    target_problem = _target_evidence_problem(directory_target, inspection.object_name)
    return SeestarDiscoveryItem(
        source_path=path,
        classification=classification,
        source_directory=source_directory,
        directory_context=context,
        directory_target=directory_target,
        metadata_target=inspection.object_name,
        fits_inspection=inspection,
        problem=_join_problems(problem, target_problem),
    )


def _fits_discovery_classification(
    path: Path,
    context: SourceDirectoryContext,
    inspection: FitsInspection,
) -> tuple[DiscoveryClassification, str | None]:
    stacked_name = path.stem.casefold().startswith("stacked_")

    if inspection.image_class is FitsImageClass.RAW_LIGHT:
        problem = (
            "FITS RAW_LIGHT classification conflicts with stacked filename evidence"
            if stacked_name
            else None
        )
        return DiscoveryClassification.LIGHT_FITS, problem

    if inspection.image_class is FitsImageClass.RGB_IMAGE:
        if stacked_name or context is SourceDirectoryContext.PRODUCT:
            problem = (
                "Stack filename occurs in a sub-source directory"
                if stacked_name and context is SourceDirectoryContext.SUB
                else None
            )
            return DiscoveryClassification.SEESTAR_STACK_FITS, problem
        return (
            DiscoveryClassification.UNKNOWN,
            "RGB FITS lacks sufficient Seestar stack filename or product-directory evidence",
        )

    return (
        DiscoveryClassification.UNKNOWN,
        f"Unsupported FITS image classification: {inspection.image_class.name}",
    )


def _directory_evidence(
    root: Path, source_directory: Path
) -> tuple[SourceDirectoryContext, str | None]:
    if source_directory == root:
        return SourceDirectoryContext.ROOT, None

    name = source_directory.name
    if name.casefold().endswith(_SUB_DIRECTORY_SUFFIX):
        target = name[: -len(_SUB_DIRECTORY_SUFFIX)] or None
        return SourceDirectoryContext.SUB, target
    return SourceDirectoryContext.PRODUCT, name


def _target_evidence_problem(
    directory_target: str | None, metadata_target: str | None
) -> str | None:
    if (
        directory_target is not None
        and metadata_target is not None
        and directory_target_for_comparison(directory_target).casefold()
        != metadata_target.casefold()
    ):
        return (
            "Directory and FITS target evidence disagree: "
            f"{directory_target!r} != {metadata_target!r}"
        )
    return None


def _join_problems(*problems: str | None) -> str | None:
    present = tuple(problem for problem in problems if problem is not None)
    return "; ".join(present) if present else None
