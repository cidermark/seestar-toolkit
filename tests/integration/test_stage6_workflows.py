"""Integrated Stage 6 workflow validation through public and CLI boundaries."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import tifffile

from seestar_toolkit import __version__
from seestar_toolkit.conversion import convert_fits_to_tiff
from seestar_toolkit.fits import read_fits_image

PROJECT_ROOT = Path(__file__).parents[2]
DATA_DIR = PROJECT_ROOT / "tests" / "data"
CONSOLE_SCRIPT = Path(sys.executable).with_name("seestar-toolkit")


def _fingerprint(path: Path) -> tuple[int, int, bytes]:
    stat = path.stat()
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").digest()
    return stat.st_size, stat.st_mtime_ns, digest


def _run_console(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [CONSOLE_SCRIPT, *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("relative_path", "expected_kind", "expected_itemsize"),
    [
        pytest.param("seestar/light.fit", "u", 2, id="raw-seestar"),
        pytest.param("seestar/stacked.fit", "u", 2, id="native-seestar-rgb"),
        pytest.param("reference/siril_stacked.fit", "f", 4, id="siril-rgb"),
    ],
)
def test_public_pipeline_real_routes_reopen_and_preserve_source(
    tmp_path: Path,
    relative_path: str,
    expected_kind: str,
    expected_itemsize: int,
) -> None:
    input_path = DATA_DIR / relative_path
    output_path = tmp_path / "explicit destination.tiff"
    image = read_fits_image(input_path)
    source_before = _fingerprint(input_path)

    result = convert_fits_to_tiff(input_path, output_path)

    assert result == output_path
    assert output_path.is_file()
    written = tifffile.imread(output_path)
    assert written.shape == (image.height, image.width, 3)
    assert written.dtype.kind == expected_kind
    assert written.dtype.itemsize == expected_itemsize
    assert _fingerprint(input_path) == source_before


def test_configured_single_file_cli_success_and_expected_failures(tmp_path: Path) -> None:
    assert CONSOLE_SCRIPT.is_file()
    input_path = DATA_DIR / "seestar" / "light.fit"
    source_before = _fingerprint(input_path)
    output_path = tmp_path / "created.tiff"

    success = _run_console("convert", str(input_path), str(output_path))

    assert success.returncode == 0
    assert f"Created TIFF: {output_path}" in success.stdout
    assert success.stderr == ""
    assert output_path.is_file()
    assert _fingerprint(input_path) == source_before

    missing_output = tmp_path / "missing-output.tiff"
    missing = _run_console("convert", str(tmp_path / "missing.fit"), str(missing_output))
    assert missing.returncode == 1
    assert "Unable to read FITS file" in missing.stderr
    assert "Traceback" not in missing.stderr
    assert not missing_output.exists()

    existing_content = output_path.read_bytes()
    existing = _run_console("convert", str(input_path), str(output_path))
    assert existing.returncode == 1
    assert "Failed to write TIFF" in existing.stderr
    assert "Traceback" not in existing.stderr
    assert output_path.read_bytes() == existing_content


def test_configured_cli_mixed_batch_is_ordered_case_insensitive_and_non_recursive(
    tmp_path: Path,
) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    nested_directory = input_directory / "nested"
    nested_directory.mkdir(parents=True)
    fixture_mapping = {
        "01_raw.fit": DATA_DIR / "seestar" / "light.fit",
        "02_native.FIT": DATA_DIR / "seestar" / "stacked.fit",
        "03_siril.fits": DATA_DIR / "reference" / "siril_stacked.fit",
        "04_raw.FITS": DATA_DIR / "seestar" / "light.fit",
    }
    sources = {
        name: Path(shutil.copy2(fixture, input_directory / name))
        for name, fixture in fixture_mapping.items()
    }
    shutil.copy2(DATA_DIR / "seestar" / "stacked.fit", nested_directory / "ignored.fit")
    (input_directory / "notes.txt").write_text("ignored")
    source_names_before = {path.name for path in input_directory.iterdir()}
    source_fingerprints = {name: _fingerprint(path) for name, path in sources.items()}

    result = _run_console("convert-batch", str(input_directory), str(output_directory))

    assert result.returncode == 0
    assert "Batch complete: 4 discovered, 4 converted, 0 failed" in result.stdout
    assert result.stderr == ""
    created_lines = [
        line for line in result.stdout.splitlines() if line.startswith("Created TIFF:")
    ]
    assert [Path(line.removeprefix("Created TIFF: ")).name for line in created_lines] == [
        "01_raw.tiff",
        "02_native.tiff",
        "03_siril.tiff",
        "04_raw.tiff",
    ]
    assert {path.name for path in output_directory.iterdir()} == {
        "01_raw.tiff",
        "02_native.tiff",
        "03_siril.tiff",
        "04_raw.tiff",
    }
    assert not (output_directory / "ignored.tiff").exists()
    assert tifffile.imread(output_directory / "01_raw.tiff").dtype.name == "uint16"
    assert tifffile.imread(output_directory / "02_native.tiff").dtype.name == "uint16"
    assert tifffile.imread(output_directory / "03_siril.tiff").dtype.name == "float32"
    assert tifffile.imread(output_directory / "04_raw.tiff").shape[-1] == 3
    assert {path.name for path in input_directory.iterdir()} == source_names_before
    assert {name: _fingerprint(path) for name, path in sources.items()} == source_fingerprints


def test_configured_cli_partial_failure_continues_to_later_file(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    invalid = input_directory / "01_invalid.fit"
    invalid.write_text("not FITS")
    valid = Path(
        shutil.copy2(
            DATA_DIR / "seestar" / "stacked.fit",
            input_directory / "02_valid.fits",
        )
    )
    source_fingerprints = {path: _fingerprint(path) for path in (invalid, valid)}
    output_directory = tmp_path / "output"

    result = _run_console("convert-batch", str(input_directory), str(output_directory))

    assert result.returncode == 1
    assert "01_invalid.fit" in result.stderr
    assert "Unable to read FITS file" in result.stderr
    assert "Traceback" not in result.stderr
    assert "Batch complete: 2 discovered, 1 converted, 1 failed" in result.stdout
    assert (output_directory / "02_valid.tiff").is_file()
    assert not (output_directory / "01_invalid.tiff").exists()
    assert {path: _fingerprint(path) for path in (invalid, valid)} == source_fingerprints


def test_configured_cli_existing_batch_destination_is_preserved_and_continues(
    tmp_path: Path,
) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    input_directory.mkdir()
    output_directory.mkdir()
    shutil.copy2(DATA_DIR / "seestar" / "light.fit", input_directory / "01_existing.fit")
    shutil.copy2(DATA_DIR / "seestar" / "stacked.fit", input_directory / "02_new.fit")
    existing = output_directory / "01_existing.tiff"
    existing_content = b"protected existing destination"
    existing.write_bytes(existing_content)

    result = _run_console("convert-batch", str(input_directory), str(output_directory))

    assert result.returncode == 1
    assert "01_existing.fit" in result.stderr
    assert "Traceback" not in result.stderr
    assert "Batch complete: 2 discovered, 1 converted, 1 failed" in result.stdout
    assert existing.read_bytes() == existing_content
    assert (output_directory / "02_new.tiff").is_file()


def test_configured_cli_no_match_batch_reports_failure(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    (input_directory / "notes.md").write_text("not an image")

    result = _run_console("convert-batch", str(input_directory), str(tmp_path / "output"))

    assert result.returncode == 1
    assert "No FIT/FITS files found" in result.stderr
    assert "Traceback" not in result.stderr
    assert "Batch complete: 0 discovered, 0 converted, 0 failed" in result.stdout


def test_configured_cli_version_help_and_no_command_remain_compatible() -> None:
    version = _run_console("--version")
    convert_help = _run_console("convert", "--help")
    batch_help = _run_console("convert-batch", "--help")
    no_command = _run_console()

    assert version.returncode == 0
    assert f"seestar-toolkit {__version__}" in version.stdout
    assert convert_help.returncode == 0
    assert "INPUT_FITS" in convert_help.stdout
    assert "OUTPUT_TIFF" in convert_help.stdout
    assert batch_help.returncode == 0
    assert "INPUT_DIR" in batch_help.stdout
    assert "OUTPUT_DIR" in batch_help.stdout
    assert "non-recursive" in batch_help.stdout
    assert no_command.returncode == 0
    assert "convert" in no_command.stdout
    assert "convert-batch" in no_command.stdout
