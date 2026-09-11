"""Generated-FITS coverage for discovery and planning target comparisons."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.archive import (
    discover_seestar_inputs,
    plan_seestar_archive,
    reconstruct_seestar_observations,
)


@pytest.mark.parametrize(
    ("directory_name", "target", "mismatch"),
    [
        ("Target_mosaic", "Target", False),
        ("Target_mosaic_sub", "Target", False),
        ("Target_MOSAIC_SUB", "target", False),
        ("Unknown_mosaic", "Unknown", False),
        ("Target A_mosaic", "Target B", True),
        ("Target A_mosaic_sub", "Target B", True),
        ("Mosaic Galaxy", "Mosaic Galaxy", False),
        ("Target_mosaic_field", "Target_mosaic_field", False),
        ("Target_mosaic_field", "Target_field", True),
    ],
)
def test_discovery_and_planning_agree_on_structural_mosaic_comparison(
    tmp_path: Path, directory_name: str, target: str, mismatch: bool
) -> None:
    root = tmp_path / "My Works"
    directory = root / directory_name
    directory.mkdir(parents=True)
    is_sub = directory_name.casefold().endswith("_sub")
    source = directory / ("Light_target.fit" if is_sub else "Stacked_1_target.fit")
    header = fits.Header()
    header["OBJECT"] = target
    header["DATE-OBS"] = "2026-09-06T21:00:00"
    header["EXPTIME"] = 10.0
    header["FILTER"] = "LP"
    header["EQMODE"] = 0
    header["BAYERPAT"] = "GRBG"
    if is_sub:
        header["IMAGETYP"] = "Light"
    fits.writeto(source, np.zeros((8, 10) if is_sub else (3, 8, 10), dtype=np.uint16), header)
    original_bytes = source.read_bytes()
    inventory = discover_seestar_inputs(root)
    item = inventory.items[0]
    reconstruction = reconstruct_seestar_observations(inventory)
    archive_root = tmp_path / "archive"

    plan = plan_seestar_archive(reconstruction, archive_root=archive_root)

    assert plan.problems == ()
    assert len(plan.observations) == 1
    planned = plan.observations[0]
    assert planned.reconstructed is reconstruction.observations[0]
    assert planned.metadata.logical_target == target
    assert planned.metadata.target_component == target
    assert planned.metadata.session_end_date == "20260907"
    assert ("target evidence disagree" in (item.problem or "")) is mismatch
    planning_conflicts = [
        message for message in planned.metadata.diagnostics if "conflicts with directory" in message
    ]
    assert bool(planning_conflicts) is mismatch
    if mismatch:
        assert repr(target) in planning_conflicts[0]
        assert repr(item.directory_target) in planning_conflicts[0]
    else:
        assert item.problem is None
        assert planned.metadata.diagnostics == planned.reconstructed.problems
    assert item.source_path == source
    assert item.source_directory == directory
    assert item.directory_target == (directory_name[:-4] if is_sub else directory_name)
    assert item.metadata_target == target
    assert item.fits_inspection is not None
    assert item.fits_inspection.object_name == target
    planned_file = planned.lights[0] if is_sub else planned.stack
    assert planned_file is not None
    assert planned_file.source_path == source
    assert source.read_bytes() == original_bytes
    assert not archive_root.exists()
