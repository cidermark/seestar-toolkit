"""Unit tests for the Seestar Toolkit CLI."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from seestar_toolkit import __version__, cli
from seestar_toolkit.archive import (
    ArchiveConfig,
    CollisionPolicy,
    LightTiffCollisionDecision,
    LightTiffOutcome,
    LightTiffResult,
    SeestarArchiveStatus,
    SourceAction,
)
from seestar_toolkit.batch import BatchConversionResult, BatchFailure, BatchSuccess
from seestar_toolkit.fits import InvalidFitsFileError
from seestar_toolkit.tiff import TiffWriteError


def test_version_is_1_1_0() -> None:
    assert __version__ == "1.1.0"


def test_parser_accepts_single_file_convert_command() -> None:
    args = cli.build_parser().parse_args(["convert", "image.fit", "image.tiff"])

    assert args.command == "convert"
    assert args.input_fits == Path("image.fit")
    assert args.output_tiff == Path("image.tiff")


def test_parser_accepts_batch_convert_command() -> None:
    args = cli.build_parser().parse_args(["convert-batch", "input", "output"])

    assert args.command == "convert-batch"
    assert args.input_directory == Path("input")
    assert args.output_directory == Path("output")


def test_archive_command_and_options_are_registered() -> None:
    args = cli.build_parser().parse_args(
        [
            "archive",
            "source",
            "archive",
            "--dry-run",
            "--location",
            "Home",
            "--hierarchy",
            "{location}/{target}/{session_end_date}",
            "--source-action",
            "move",
            "--collision-policy",
            "error",
            "--non-interactive",
            "--convert-lights",
            "--config",
            "settings.toml",
        ]
    )

    assert args.command == "archive"
    assert args.source_root == Path("source")
    assert args.archive_root == Path("archive")
    assert args.dry_run
    assert args.source_action == "move"
    assert args.collision_policy == "error"
    assert args.convert_lights


def test_archive_help_documents_contract(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(["archive", "--help"])

    assert raised.value.code == 0
    output = capsys.readouterr().out
    for value in (
        "SOURCE_ROOT",
        "ARCHIVE_ROOT",
        "--dry-run",
        "--location",
        "--hierarchy",
        "--source-action",
        "--collision-policy",
        "--non-interactive",
        "--convert-lights",
        "--config",
    ):
        assert value in output
    normalized = " ".join(output.split())
    assert (
        "Create or verify TIFF derivatives for eligible archived individual lights for this "
        "archive invocation only."
    ) in normalized
    assert (
        "Run without prompts; automatically process applicable existing light FITS and safely "
        "skip differing-TIFF collisions."
    ) in normalized
    assert "not active" not in output
    assert "--unattended" not in output


@pytest.mark.parametrize(("answer", "expected"), [("", True), ("y", True), ("n", False)])
def test_existing_light_prompt_defaults_yes(
    monkeypatch: pytest.MonkeyPatch, answer: str, expected: bool
) -> None:
    monkeypatch.setattr("builtins.input", Mock(return_value=answer))

    assert cli._prompt_process_existing_lights(38, 20, 18) is expected


@pytest.mark.parametrize(
    ("has_duplicate", "answer", "expected"),
    [
        (False, "k", LightTiffCollisionDecision.KEEP_BOTH),
        (False, "r", LightTiffCollisionDecision.REPLACE_EXISTING),
        (False, "", LightTiffCollisionDecision.SKIP),
        (True, "r", LightTiffCollisionDecision.REPLACE_DUPLICATE),
        (True, "s", LightTiffCollisionDecision.SKIP),
    ],
)
def test_light_tiff_collision_prompt_choices(
    monkeypatch: pytest.MonkeyPatch,
    has_duplicate: bool,
    answer: str,
    expected: LightTiffCollisionDecision,
) -> None:
    monkeypatch.setattr("builtins.input", Mock(return_value=answer))

    assert cli._prompt_light_tiff_collision(Path("Light.tiff"), has_duplicate) is expected


def test_light_tiff_summary_preserves_all_seven_categories(
    capsys: pytest.CaptureFixture[str],
) -> None:
    light_tiffs = tuple(
        LightTiffResult(
            archived_fits_path=Path(f"Light-{outcome.name}.fit"),
            tiff_destination=Path(f"Light-{outcome.name}.tiff"),
            outcome=outcome,
            diagnostic="representative failure" if outcome is LightTiffOutcome.FAILED else None,
        )
        for outcome in LightTiffOutcome
    )
    result = SimpleNamespace(
        status=SeestarArchiveStatus.PARTIAL,
        execution=SimpleNamespace(
            copied_count=7,
            moved_count=0,
            skipped_count=0,
            failed_count=0,
            files=(),
        ),
        tiffs=(),
        light_tiffs=light_tiffs,
        existing_lights_declined=0,
        indexes=(),
    )

    cli._print_archive_result(result)

    output = capsys.readouterr().out
    for label in (
        "created",
        "primary replaced",
        "duplicate created",
        "duplicate replaced",
        "already present",
        "skipped",
        "failed",
    ):
        assert f"  1 {label}" in output


def test_light_tiff_summary_omits_zero_valued_categories(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = SimpleNamespace(
        status=SeestarArchiveStatus.COMPLETE,
        execution=SimpleNamespace(
            copied_count=1,
            moved_count=0,
            skipped_count=0,
            failed_count=0,
            files=(),
        ),
        tiffs=(),
        light_tiffs=(
            LightTiffResult(
                archived_fits_path=Path("Light.fit"),
                tiff_destination=Path("Light.tiff"),
                outcome=LightTiffOutcome.CREATED,
            ),
        ),
        existing_lights_declined=0,
        indexes=(),
    )

    cli._print_archive_result(result)

    output = capsys.readouterr().out
    assert "  1 created" in output
    assert "  0 " not in output


def test_archive_config_defaults_and_cli_overrides_pass_through(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loaded = ArchiveConfig(
        hierarchy="{location}/{target}/{session_end_date}",
        source_action=SourceAction.MOVE,
        collision_policy=CollisionPolicy.ERROR,
    )
    prepared = SimpleNamespace(
        plan=SimpleNamespace(observations=(), problems=()),
        discovery=SimpleNamespace(items=()),
        has_operational_problems=False,
    )
    monkeypatch.setattr(cli, "load_archive_config", Mock(return_value=loaded))
    prepare = Mock(return_value=prepared)
    monkeypatch.setattr(cli, "prepare_seestar_archive", prepare)

    status = cli.main(
        [
            "archive",
            "source",
            "/archive",
            "--dry-run",
            "--non-interactive",
            "--hierarchy",
            "{target}",
            "--source-action",
            "copy",
            "--collision-policy",
            "overwrite",
        ]
    )

    assert status == 0
    prepare.assert_called_once_with(
        Path("source"),
        archive_root=Path("/archive"),
        hierarchy_template="{target}",
        explicit_location=None,
        saved_locations=(),
        observation_date_policy="end",
    )


def test_archive_non_interactive_never_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    prepared = SimpleNamespace(
        plan=SimpleNamespace(observations=(), problems=()),
        discovery=SimpleNamespace(items=()),
        has_operational_problems=False,
    )
    monkeypatch.setattr(cli, "prepare_seestar_archive", Mock(return_value=prepared))
    prompt = Mock(side_effect=AssertionError("must not prompt"))
    monkeypatch.setattr("builtins.input", prompt)

    assert cli.main(["archive", "source", "/archive", "--dry-run", "--non-interactive"]) == 0
    prompt.assert_not_called()


def test_main_without_command_returns_success(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main([]) == 0
    assert "usage:" in capsys.readouterr().out


def test_convert_delegates_to_pipeline_and_reports_destination(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    output_path = Path("created image.tiff")
    convert = Mock(return_value=output_path)
    monkeypatch.setattr(cli, "convert_fits_to_tiff", convert)

    result = cli.main(["convert", "source image.fit", str(output_path)])

    assert result == 0
    convert.assert_called_once_with(Path("source image.fit"), output_path)
    captured = capsys.readouterr()
    assert str(output_path) in captured.out
    assert captured.err == ""


@pytest.mark.parametrize(
    "error",
    [
        InvalidFitsFileError("Unable to read FITS file: missing.fit"),
        ValueError("Unsupported FITS image classification: UNKNOWN"),
        TiffWriteError("Failed to write TIFF existing.tiff"),
    ],
)
def test_convert_reports_expected_failures_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: Exception,
) -> None:
    monkeypatch.setattr(cli, "convert_fits_to_tiff", Mock(side_effect=error))

    result = cli.main(["convert", "input.fit", "output.tiff"])

    assert result == 1
    captured = capsys.readouterr()
    assert str(error) in captured.err
    assert "Traceback" not in captured.err


def test_convert_help_documents_required_paths(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(["convert", "--help"])

    assert raised.value.code == 0
    output = capsys.readouterr().out
    assert "INPUT_FITS" in output
    assert "OUTPUT_TIFF" in output
    assert "one FIT/FITS image" in output


def test_convert_omitted_output_is_operational_inference_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = cli.main(["convert", "input.fit"])

    assert status == 1
    assert "Supply OUTPUT_TIFF explicitly" in capsys.readouterr().err


def test_convert_batch_reports_successes_failures_and_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = BatchConversionResult(
        discovered_count=2,
        successes=(BatchSuccess(Path("input/good.fit"), Path("output/good.tiff")),),
        failures=(BatchFailure(Path("input/bad.fit"), "invalid FITS"),),
    )
    convert = Mock(return_value=result)
    monkeypatch.setattr(cli, "convert_fits_directory", convert)

    status = cli.main(["convert-batch", "input", "output"])

    assert status == 1
    convert.assert_called_once_with(Path("input"), Path("output"))
    captured = capsys.readouterr()
    assert "Created TIFF: output/good.tiff" in captured.out
    assert "Batch complete: 2 discovered, 1 converted, 1 failed" in captured.out
    assert "Failed: input/bad.fit — invalid FITS" in captured.err
    assert "Traceback" not in captured.err


def test_convert_batch_full_success_returns_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = BatchConversionResult(
        discovered_count=1,
        successes=(BatchSuccess(Path("input/good.fit"), Path("output/good.tiff")),),
        failures=(),
    )
    monkeypatch.setattr(cli, "convert_fits_directory", Mock(return_value=result))

    assert cli.main(["convert-batch", "input", "output"]) == 0
    assert "1 discovered, 1 converted, 0 failed" in capsys.readouterr().out


def test_convert_batch_no_matches_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "convert_fits_directory",
        Mock(return_value=BatchConversionResult(0, (), ())),
    )

    assert cli.main(["convert-batch", "input", "output"]) == 1
    captured = capsys.readouterr()
    assert "No FIT/FITS files found" in captured.err
    assert "0 discovered, 0 converted, 0 failed" in captured.out


def test_convert_batch_setup_failure_is_clean(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "convert_fits_directory",
        Mock(side_effect=ValueError("Input directory does not exist: missing")),
    )

    assert cli.main(["convert-batch", "missing", "output"]) == 1
    captured = capsys.readouterr()
    assert "Input directory does not exist" in captured.err
    assert "Traceback" not in captured.err


def test_convert_batch_help_documents_required_directories(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(["convert-batch", "--help"])

    assert raised.value.code == 0
    output = capsys.readouterr().out
    assert "INPUT_DIR" in output
    assert "OUTPUT_DIR" in output
    assert "non-recursive" in output


def test_convert_batch_omitted_output_is_operational_inference_failure(
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = cli.main(["convert-batch", "input"])

    assert status == 1
    assert "Supply OUTPUT_DIR explicitly" in capsys.readouterr().err


def test_version_option_remains_working(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(["--version"])

    assert raised.value.code == 0
    assert f"seestar-toolkit {__version__}" in capsys.readouterr().out
