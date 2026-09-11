"""Real-fixture integration coverage for Seestar archive discovery."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from seestar_toolkit.archive import DiscoveryClassification, discover_seestar_inputs

DATA_DIR = Path(__file__).parents[1] / "data" / "seestar"


def _fingerprint(path: Path) -> tuple[int, int, bytes]:
    stat = path.stat()
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").digest()
    return stat.st_size, stat.st_mtime_ns, digest


def test_discovery_reuses_fits_inspection_for_real_light_and_stack(tmp_path: Path) -> None:
    root = tmp_path / "My Works"
    product = root / "IC 434"
    sub = root / "IC 434_sub"
    product.mkdir(parents=True)
    sub.mkdir()
    light = Path(shutil.copy2(DATA_DIR / "light.fit", sub / "Light_real.fit"))
    stack = Path(shutil.copy2(DATA_DIR / "stacked.fit", product / "Stacked_real.FITS"))
    originals = (DATA_DIR / "light.fit", DATA_DIR / "stacked.fit")
    original_before = tuple(_fingerprint(path) for path in originals)
    copies_before = (_fingerprint(light), _fingerprint(stack))

    inventory = discover_seestar_inputs(root)

    assert [item.classification for item in inventory.items] == [
        DiscoveryClassification.SEESTAR_STACK_FITS,
        DiscoveryClassification.LIGHT_FITS,
    ]
    assert all(item.fits_inspection is not None for item in inventory.items)
    assert (_fingerprint(light), _fingerprint(stack)) == copies_before
    assert tuple(_fingerprint(path) for path in originals) == original_before
