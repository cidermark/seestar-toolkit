"""Focused ENH-004b archive-aware CLI integration tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from seestar_toolkit import cli

DATA_DIR = Path(__file__).parents[1] / "data"


def _observation(tmp_path: Path) -> Path:
    observation = tmp_path / "Target/Home/20261027/observation_01"
    (observation / "fits_images/lights").mkdir(parents=True)
    return observation


@pytest.mark.parametrize("suffix", (".fit", ".fits", ".FIT", ".FiTs"))
def test_single_file_infers_output_and_creates_it_lazily(
    tmp_path: Path, suffix: str, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)
    source = Path(
        shutil.copy2(
            DATA_DIR / "seestar/light.fit",
            observation / "fits_images/lights" / f"Light M 42.v1{suffix}",
        )
    )

    assert cli.main(["convert", str(source)]) == 0

    output = observation / "tiff_images/lights/Light M 42.v1.tiff"
    assert output.is_file()
    assert f"Created TIFF: {output}" in capsys.readouterr().out


@pytest.mark.parametrize("relative", ("seestar_stacked/stack.fit", "lights/source.fit"))
def test_single_file_inference_rejects_unsupported_structure_without_creation(
    tmp_path: Path, relative: str, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)
    source = observation / relative
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"not inspected")

    assert cli.main(["convert", str(source)]) == 1

    assert "Supply OUTPUT_TIFF explicitly" in capsys.readouterr().err
    assert not (observation / "tiff_images").exists()


def test_invalid_archived_fits_does_not_create_inferred_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)
    source = observation / "fits_images/lights/invalid.fit"
    source.write_text("not FITS")

    assert cli.main(["convert", str(source)]) == 1

    assert "Unable to read FITS file" in capsys.readouterr().err
    assert not (observation / "tiff_images").exists()


def test_inferred_directory_creation_does_not_replace_existing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)
    source = Path(
        shutil.copy2(
            DATA_DIR / "seestar/light.fit",
            observation / "fits_images/lights/light.fit",
        )
    )
    obstruction = observation / "tiff_images"
    obstruction.write_bytes(b"preserve")

    assert cli.main(["convert", str(source)]) == 1

    assert "Unable to create output directory" in capsys.readouterr().err
    assert obstruction.read_bytes() == b"preserve"


@pytest.mark.parametrize("level", ("observation", "fits_images", "lights"))
@pytest.mark.parametrize("explicit", (False, True))
def test_batch_resolves_all_archive_levels_with_inferred_or_explicit_output(
    tmp_path: Path,
    level: str,
    explicit: bool,
    capsys: pytest.CaptureFixture[str],
) -> None:
    observation = _observation(tmp_path)
    shutil.copy2(DATA_DIR / "seestar/light.fit", observation / "fits_images/lights/a.FIT")
    inputs = {
        "observation": observation,
        "fits_images": observation / "fits_images",
        "lights": observation / "fits_images/lights",
    }
    output = tmp_path / "explicit" if explicit else observation / "tiff_images/lights"
    arguments = ["convert-batch", str(inputs[level])]
    if explicit:
        arguments.append(str(output))

    assert cli.main(arguments) == 0

    captured = capsys.readouterr()
    assert (output / "a.tiff").is_file()
    assert "Batch status: SUCCESS" in captured.out
    assert ("Inferred output directory:" in captured.out) is (not explicit)


def test_empty_archive_batch_fails_without_creating_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)

    assert cli.main(["convert-batch", str(observation)]) == 1

    captured = capsys.readouterr()
    assert "no eligible FIT/FITS files" in captured.err
    assert "Batch status: FAILED" in captured.out
    assert not (observation / "tiff_images").exists()


def test_missing_canonical_lights_is_operational_failure_even_with_explicit_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = tmp_path / "observation_01"
    observation.mkdir()

    assert cli.main(["convert-batch", str(observation), str(tmp_path / "output")]) == 1

    assert "missing its canonical lights directory" in capsys.readouterr().err
    assert not (tmp_path / "output").exists()


def test_ordinary_batch_requires_output_but_explicit_form_remains_supported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "ordinary"
    source.mkdir()
    shutil.copy2(DATA_DIR / "seestar/light.fit", source / "light.fit")

    assert cli.main(["convert-batch", str(source)]) == 1
    assert "Supply OUTPUT_DIR explicitly" in capsys.readouterr().err

    output = tmp_path / "output"
    assert cli.main(["convert-batch", str(source), str(output)]) == 0
    assert (output / "light.tiff").is_file()


def test_inferred_batch_continues_after_invalid_and_collision(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    observation = _observation(tmp_path)
    lights = observation / "fits_images/lights"
    (lights / "01_invalid.fit").write_text("not FITS")
    shutil.copy2(DATA_DIR / "seestar/light.fit", lights / "02_collision.fit")
    shutil.copy2(DATA_DIR / "seestar/stacked.fit", lights / "03_valid.fits")
    output = observation / "tiff_images/lights"
    output.mkdir(parents=True)
    collision = output / "02_collision.tiff"
    collision.write_bytes(b"preserve")

    assert cli.main(["convert-batch", str(observation)]) == 1

    captured = capsys.readouterr()
    assert "01_invalid.fit" in captured.err
    assert "02_collision.fit" in captured.err
    assert collision.read_bytes() == b"preserve"
    assert (output / "03_valid.tiff").is_file()
    assert "Batch status: PARTIAL SUCCESS" in captured.out


def test_help_documents_optional_archive_aware_forms(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for command in ("convert", "convert-batch"):
        with pytest.raises(SystemExit) as raised:
            cli.main([command, "--help"])
        assert raised.value.code == 0
        output = " ".join(capsys.readouterr().out.split())
        assert "archive" in output.lower()
        assert "[OUTPUT_" in output

    root_help = " ".join(cli.build_parser().format_help().split())
    assert "archive-aware output inference" in root_help
    assert "archive-aware input and output inference" in root_help
