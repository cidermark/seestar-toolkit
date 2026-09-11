"""Tests for read-only Seestar input discovery and classification."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.archive import (
    ArchiveDiscoveryError,
    DiscoveryClassification,
    SourceDirectoryContext,
    discover_seestar_inputs,
)
from seestar_toolkit.fits import FitsImageClass


def _write_raw_light(path: Path, *, target: str = "IC 434") -> None:
    header = fits.Header()
    header["IMAGETYP"] = "Light"
    header["OBJECT"] = target
    header["BAYERPAT"] = "GRBG"
    fits.writeto(path, np.zeros((8, 10), dtype=np.uint16), header=header)


def _write_rgb_stack(path: Path, *, target: str = "IC 434") -> None:
    header = fits.Header()
    header["OBJECT"] = target
    fits.writeto(path, np.zeros((3, 8, 10), dtype=np.uint16), header=header)


def _tree_fingerprint(root: Path) -> tuple[tuple[str, int, int, bytes], ...]:
    records = []
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        stat = path.stat()
        with path.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").digest()
        records.append((path.relative_to(root).as_posix(), stat.st_size, stat.st_mtime_ns, digest))
    return tuple(records)


def test_discovery_classifies_supported_shallow_sources_deterministically(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    lights = root / "IC 434_sub"
    product.mkdir(parents=True)
    lights.mkdir()
    (lights / "notes.txt").write_text("unrelated")
    (product / "Stacked_example_thn.JPG").write_bytes(b"thumbnail")
    (lights / "Light_example.JPEG").write_bytes(b"preview")
    _write_rgb_stack(product / "Stacked_example.FITS")
    _write_raw_light(lights / "Light_example.FIT")

    inventory = discover_seestar_inputs(root)

    assert [item.source_path.relative_to(root).as_posix() for item in inventory.items] == [
        "IC 434/Stacked_example.FITS",
        "IC 434/Stacked_example_thn.JPG",
        "IC 434_sub/Light_example.FIT",
        "IC 434_sub/Light_example.JPEG",
        "IC 434_sub/notes.txt",
    ]
    assert [item.classification for item in inventory.items] == [
        DiscoveryClassification.SEESTAR_STACK_FITS,
        DiscoveryClassification.THUMBNAIL_JPEG,
        DiscoveryClassification.LIGHT_FITS,
        DiscoveryClassification.SEESTAR_JPEG,
        DiscoveryClassification.UNKNOWN,
    ]


def test_discovery_returns_empty_inventory_for_empty_root(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    root.mkdir()

    inventory = discover_seestar_inputs(str(root))

    assert inventory.root == root
    assert inventory.items == ()


def test_discovery_rejects_missing_root(tmp_path: Path) -> None:
    root = tmp_path / "missing"

    with pytest.raises(ArchiveDiscoveryError, match="does not exist"):
        discover_seestar_inputs(root)


def test_discovery_rejects_file_as_root(tmp_path: Path) -> None:
    root = tmp_path / "not-a-directory"
    root.write_text("file")

    with pytest.raises(ArchiveDiscoveryError, match="not a directory"):
        discover_seestar_inputs(root)


def test_discovery_retains_directory_and_fits_target_evidence(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    sub = root / "Directory Target_sub"
    sub.mkdir(parents=True)
    source = sub / "Light_target.fit"
    _write_raw_light(source, target="Metadata Target")

    item = discover_seestar_inputs(root).items[0]

    assert item.directory_context is SourceDirectoryContext.SUB
    assert item.source_directory == sub
    assert item.directory_target == "Directory Target"
    assert item.metadata_target == "Metadata Target"
    assert item.target_candidate == "Metadata Target"
    assert "target evidence disagree" in (item.problem or "")
    assert item.fits_inspection is not None
    assert item.fits_inspection.image_class is FitsImageClass.RAW_LIGHT


@pytest.mark.parametrize(
    ("directory_name", "filename", "write_fits"),
    [
        pytest.param(
            "Target_mosaic",
            "Stacked_1_target.fit",
            _write_rgb_stack,
            id="product-directory",
        ),
        pytest.param(
            "Target_mosaic_sub",
            "Light_target.fit",
            _write_raw_light,
            id="sub-directory",
        ),
    ],
)
def test_structural_mosaic_suffix_is_normalized_only_for_target_comparison(
    tmp_path: Path,
    directory_name: str,
    filename: str,
    write_fits,
) -> None:
    root = tmp_path / "My Works"
    source_directory = root / directory_name
    source_directory.mkdir(parents=True)
    source = source_directory / filename
    write_fits(source, target="Target")

    item = discover_seestar_inputs(root).items[0]

    assert item.source_path == source
    assert item.source_directory == source_directory
    assert item.directory_target == "Target_mosaic"
    assert item.metadata_target == "Target"
    assert item.problem is None


def test_structural_mosaic_suffix_does_not_hide_genuine_target_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "My Works"
    sub = root / "Target A_mosaic_sub"
    sub.mkdir(parents=True)
    _write_raw_light(sub / "Light_target.fit", target="Target B")

    item = discover_seestar_inputs(root).items[0]

    assert item.directory_target == "Target A_mosaic"
    assert item.metadata_target == "Target B"
    assert "'Target A_mosaic' != 'Target B'" in (item.problem or "")


def test_non_structural_mosaic_text_is_not_rewritten(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "Mosaic Galaxy"
    product.mkdir(parents=True)
    _write_rgb_stack(product / "Stacked_1_target.fit", target="Mosaic Galaxy")

    item = discover_seestar_inputs(root).items[0]

    assert item.directory_target == "Mosaic Galaxy"
    assert item.metadata_target == "Mosaic Galaxy"
    assert item.problem is None


def test_fits_inspection_overrides_misleading_stack_filename(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    sub = root / "IC 434_sub"
    sub.mkdir(parents=True)
    _write_raw_light(sub / "Stacked_misleading.fit")

    item = discover_seestar_inputs(root).items[0]

    assert item.classification is DiscoveryClassification.LIGHT_FITS
    assert "conflicts" in (item.problem or "")


def test_ambiguous_rgb_fits_is_unknown_with_visible_problem(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    sub = root / "IC 434_sub"
    sub.mkdir(parents=True)
    _write_rgb_stack(sub / "Light_misleading.fit")

    item = discover_seestar_inputs(root).items[0]

    assert item.classification is DiscoveryClassification.UNKNOWN
    assert "lacks sufficient" in (item.problem or "")
    assert item.fits_inspection is not None


def test_malformed_fits_is_reported_without_losing_valid_item(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    sub = root / "IC 434_sub"
    sub.mkdir(parents=True)
    (sub / "01_bad.fit").write_text("not FITS")
    _write_raw_light(sub / "02_good.fits")

    inventory = discover_seestar_inputs(root)

    assert len(inventory.items) == 2
    assert inventory.items[0].classification is DiscoveryClassification.UNKNOWN
    assert "Unable to read FITS file" in (inventory.items[0].problem or "")
    assert inventory.items[1].classification is DiscoveryClassification.LIGHT_FITS


def test_multiple_stacks_remain_individual_items_without_observation_fields(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    product.mkdir(parents=True)
    _write_rgb_stack(product / "Stacked_001.fit")
    _write_rgb_stack(product / "Stacked_002.fit")

    inventory = discover_seestar_inputs(root)
    stacks = inventory.items_of_type(DiscoveryClassification.SEESTAR_STACK_FITS)

    assert [item.source_path.name for item in stacks] == ["Stacked_001.fit", "Stacked_002.fit"]
    assert not hasattr(stacks[0], "observation")
    assert not hasattr(stacks[0], "associated_stack")
    assert not hasattr(stacks[0], "session_end_date")


def test_discovery_is_shallow_and_does_not_assume_mosaic_directory_name(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    provisional = root / "Target_mosaic_sub"
    nested = provisional / "nested"
    nested.mkdir(parents=True)
    _write_raw_light(provisional / "Light_mosaic.fit", target="Target")
    _write_raw_light(nested / "Light_nested.fit", target="Target")

    inventory = discover_seestar_inputs(root)

    assert [item.source_path.name for item in inventory.items] == ["Light_mosaic.fit"]
    assert inventory.items[0].directory_context is SourceDirectoryContext.SUB
    assert inventory.items[0].directory_target == "Target_mosaic"


def test_discovery_does_not_mutate_source_tree(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    sub = root / "IC 434_sub"
    product.mkdir(parents=True)
    sub.mkdir()
    _write_rgb_stack(product / "Stacked_example.fit")
    _write_raw_light(sub / "Light_example.fit")
    (sub / "Light_example.jpg").write_bytes(b"jpeg")
    before = _tree_fingerprint(root)

    discover_seestar_inputs(root)

    assert _tree_fingerprint(root) == before
    assert not tuple(root.rglob("*.tiff"))
    assert not tuple(root.rglob("INDEX.md"))
