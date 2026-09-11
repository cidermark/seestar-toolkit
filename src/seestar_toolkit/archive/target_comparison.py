"""Shared comparison-only semantics for Seestar directory target evidence."""

_MOSAIC_DIRECTORY_SUFFIX = "_mosaic"


def directory_target_for_comparison(directory_target: str) -> str:
    """Remove the structural mosaic suffix after discovery's existing `_sub` handling.

    Use only for comparison, never to replace stored evidence or select targets.
    """
    if directory_target.casefold().endswith(_MOSAIC_DIRECTORY_SUFFIX):
        return directory_target[: -len(_MOSAIC_DIRECTORY_SUFFIX)]
    return directory_target
