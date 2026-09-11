"""Real-fixture integration coverage for observation reconstruction."""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
from astropy.io import fits

from seestar_toolkit.archive import (
    ObservationStatus,
    discover_seestar_inputs,
    reconstruct_seestar_observations,
)

DATA_DIR = Path(__file__).parents[1] / "data" / "seestar"


def _write_frame(path: Path, captured_at: datetime, *, stack: bool) -> None:
    header = fits.Header()
    header["DATE-OBS"] = captured_at.isoformat()
    header["OBJECT"] = "IC 434"
    header["EXPTIME"] = 10.0
    header["FILTER"] = "LP"
    header["EQMODE"] = 0
    if stack:
        data = np.zeros((3, 8, 10), dtype=np.uint16)
    else:
        header["IMAGETYP"] = "Light"
        header["BAYERPAT"] = "GRBG"
        data = np.zeros((8, 10), dtype=np.uint16)
    fits.writeto(path, data, header=header)


def _fingerprint(path: Path) -> tuple[int, int, bytes]:
    stat = path.stat()
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").digest()
    return stat.st_size, stat.st_mtime_ns, digest


def test_real_discovery_inventory_reconstructs_without_source_mutation(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    sub = root / "IC 434_sub"
    product.mkdir(parents=True)
    sub.mkdir()
    light = Path(shutil.copy2(DATA_DIR / "light.fit", sub / "Light_real.fit"))
    stack = Path(shutil.copy2(DATA_DIR / "stacked.fit", product / "Stacked_195_real.fit"))
    copies_before = (_fingerprint(light), _fingerprint(stack))

    inventory = discover_seestar_inputs(root)
    result = reconstruct_seestar_observations(inventory)

    assert len(result.observations) == 1
    observation = result.observations[0]
    assert observation.status is ObservationStatus.COMPLETE
    assert [item.source_path for item in observation.lights] == [light]
    assert observation.stack is not None
    assert observation.stack.source_path == stack
    assert observation.reported_stack_count == 195
    assert (_fingerprint(light), _fingerprint(stack)) == copies_before


def test_generated_fits_equal_time_light_is_associated_before_stack(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    sub = root / "IC 434_sub"
    product.mkdir(parents=True)
    sub.mkdir()
    captured_at = datetime(2026, 1, 3, 22, 0, 0)
    light = sub / "Light_IC 434_10.0s_LP_20260103-220000.fit"
    stack = product / "Stacked_1_IC 434_10.0s_LP_20260103-220000.fit"
    _write_frame(light, captured_at, stack=False)
    _write_frame(stack, captured_at, stack=True)

    result = reconstruct_seestar_observations(discover_seestar_inputs(root))

    assert len(result.observations) == 1
    assert result.observations[0].status is ObservationStatus.COMPLETE
    assert [item.source_path for item in result.observations[0].lights] == [light]
    assert result.observations[0].stack is not None
    assert result.observations[0].stack.source_path == stack


def test_generated_fits_utc_time_is_not_compared_with_local_filename_time(
    tmp_path: Path,
) -> None:
    root = tmp_path / "My Works"
    sub = root / "IC 434_sub"
    sub.mkdir(parents=True)
    captured_at = datetime(2026, 1, 3, 22, 0, 0)
    light = sub / "Light_IC 434_10.0s_LP_20260103-230000.fit"
    _write_frame(light, captured_at, stack=False)

    result = reconstruct_seestar_observations(discover_seestar_inputs(root))
    observation = result.observations[0]

    assert observation.first_light_at == captured_at
    assert "FITS and filename timestamps differ" not in " ".join(observation.problems)
