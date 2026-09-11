"""Unit tests for flat-directory batch conversion."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from seestar_toolkit import batch
from seestar_toolkit.fits import InvalidFitsFileError
from seestar_toolkit.tiff import TiffWriteError


def test_batch_discovers_supported_extensions_in_deterministic_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    output_directory = tmp_path / "output"
    for name in ("zeta.fits", "Alpha.FIT", "middle.FITS", "beta.fit", "notes.txt"):
        (input_directory / name).write_text("fixture")
    nested = input_directory / "nested"
    nested.mkdir()
    (nested / "ignored.fit").write_text("fixture")
    convert = Mock(side_effect=lambda _source, destination: destination)
    monkeypatch.setattr(batch, "convert_fits_to_tiff", convert)

    result = batch.convert_fits_directory(input_directory, output_directory)

    assert [call.args[0].name for call in convert.call_args_list] == [
        "Alpha.FIT",
        "beta.fit",
        "middle.FITS",
        "zeta.fits",
    ]
    assert [success.output_path.name for success in result.successes] == [
        "Alpha.tiff",
        "beta.tiff",
        "middle.tiff",
        "zeta.tiff",
    ]
    assert result.discovered_count == 4
    assert result.succeeded_count == 4
    assert result.failed_count == 0
    assert output_directory.is_dir()


@pytest.mark.parametrize(
    ("setup", "message"),
    [
        ("missing", "does not exist"),
        ("file", "not a directory"),
    ],
)
def test_batch_rejects_invalid_input_directory(tmp_path: Path, setup: str, message: str) -> None:
    input_path = tmp_path / "input"
    if setup == "file":
        input_path.write_text("not a directory")

    with pytest.raises(ValueError, match=message):
        batch.convert_fits_directory(input_path, tmp_path / "output")


def test_batch_rejects_output_path_that_is_not_directory(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    output_path = tmp_path / "output"
    output_path.write_text("not a directory")

    with pytest.raises(ValueError, match="Output path is not a directory"):
        batch.convert_fits_directory(input_directory, output_path)


def test_batch_does_not_create_missing_output_parent(tmp_path: Path) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()

    with pytest.raises(ValueError, match="Unable to create output directory"):
        batch.convert_fits_directory(input_directory, tmp_path / "missing" / "output")


def test_batch_continues_after_expected_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_directory = tmp_path / "input"
    output_directory = tmp_path / "output"
    input_directory.mkdir()
    output_directory.mkdir()
    for name in ("a.fit", "b.fit", "c.fit"):
        (input_directory / name).write_text("fixture")
    convert = Mock(
        side_effect=[
            InvalidFitsFileError("invalid FITS"),
            output_directory / "b.tiff",
            TiffWriteError("destination exists"),
        ]
    )
    monkeypatch.setattr(batch, "convert_fits_to_tiff", convert)

    result = batch.convert_fits_directory(input_directory, output_directory)

    assert convert.call_count == 3
    assert result.discovered_count == 3
    assert result.succeeded_count == 1
    assert result.failed_count == 2
    assert [failure.input_path.name for failure in result.failures] == ["a.fit", "c.fit"]
    assert [failure.reason for failure in result.failures] == [
        "invalid FITS",
        "destination exists",
    ]


def test_batch_does_not_swallow_unexpected_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    (input_directory / "image.fit").write_text("fixture")
    monkeypatch.setattr(
        batch,
        "convert_fits_to_tiff",
        Mock(side_effect=RuntimeError("programming defect")),
    )

    with pytest.raises(RuntimeError, match="programming defect"):
        batch.convert_fits_directory(input_directory, tmp_path / "output")


def test_batch_empty_directory_returns_empty_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_directory = tmp_path / "input"
    input_directory.mkdir()
    (input_directory / "notes.md").write_text("ignored")
    convert = Mock()
    monkeypatch.setattr(batch, "convert_fits_to_tiff", convert)

    result = batch.convert_fits_directory(input_directory, tmp_path / "output")

    assert result.discovered_count == 0
    assert result.succeeded_count == 0
    assert result.failed_count == 0
    convert.assert_not_called()
