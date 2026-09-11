"""Apply the established formatting scope without rewriting historical debt."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "src/seestar_toolkit/archive",
    "tests/unit/archive",
    "tests/integration/test_archive_orchestration.py",
    "tests/integration/test_archive_planning.py",
    "tests/integration/test_archive_reconstruction.py",
    "src/seestar_toolkit/cli.py",
    "tests/unit/test_cli.py",
    "tools/generate_siril_mosaic_fixture.py",
    "tests/integration/test_siril_rgb_conversion.py",
    "tests/integration/test_rgb_handling_contract.py",
    "tests/integration/test_fits_to_tiff_conversion.py",
    "tools/check_formatting.py",
    "tests/unit/test_distribution_validation.py",
    "tools/check_public_inputs.py",
    "tools/validate_distribution.py",
]

if __name__ == "__main__":
    subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", *PATHS], cwd=ROOT, check=True
    )
