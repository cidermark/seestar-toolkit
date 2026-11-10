"""Focused CLI tests for ENH-005b.1."""

from pathlib import Path
from subprocess import CalledProcessError
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from astropy.io import fits

from seestar_toolkit import cli
from seestar_toolkit.fits.header_report import HeaderReportError


def test_header_report_parser_accepts_options_on_either_side() -> None:
    before = cli.build_parser().parse_args(
        ["header-report", "--output", "report.txt", "--noprompt", "image.fit"]
    )
    after = cli.build_parser().parse_args(
        ["header-report", "image.fit", "--output", "report.txt", "--noprompt"]
    )

    assert before == after
    assert before.input_fits == Path("image.fit")


def test_noscrub_is_not_available(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="0"):
        cli.main(["header-report", "--help"])

    output = capsys.readouterr().out
    assert "--output" in output
    assert "--noprompt" in output
    assert "--noscrub" not in output

    with pytest.raises(SystemExit) as raised:
        cli.main(["header-report", "image.fit", "--noscrub"])

    assert raised.value.code == 2


def test_success_and_noprompt_suppress_menu(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    result = SimpleNamespace(output_path=Path("report.txt"))
    generate = Mock(return_value=result)
    menu = Mock()
    monkeypatch.setattr(cli, "generate_header_report", generate)
    monkeypatch.setattr(cli, "offer_report_menu", menu)

    assert cli.main(["header-report", "--noprompt", "image.fit"]) == 0

    menu.assert_not_called()
    assert "Created header report: report.txt" in capsys.readouterr().out


@pytest.mark.parametrize(("stdin_tty", "stdout_tty"), ((False, True), (True, False)))
def test_noninteractive_stream_suppresses_menu(
    monkeypatch: pytest.MonkeyPatch, stdin_tty: bool, stdout_tty: bool
) -> None:
    result = SimpleNamespace(output_path=Path("report.txt"))
    monkeypatch.setattr(cli, "generate_header_report", Mock(return_value=result))
    menu = Mock()
    monkeypatch.setattr(cli, "offer_report_menu", menu)
    monkeypatch.setattr(cli.sys.stdin, "isatty", Mock(return_value=stdin_tty))
    monkeypatch.setattr(cli.sys.stdout, "isatty", Mock(return_value=stdout_tty))

    assert cli.main(["header-report", "image.fit"]) == 0
    menu.assert_not_called()


def test_both_tty_streams_offer_menu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = SimpleNamespace(output_path=Path("report.txt"))
    monkeypatch.setattr(cli, "generate_header_report", Mock(return_value=result))
    menu = Mock()
    monkeypatch.setattr(cli, "offer_report_menu", menu)
    monkeypatch.setattr(cli.sys.stdin, "isatty", Mock(return_value=True))
    monkeypatch.setattr(cli.sys.stdout, "isatty", Mock(return_value=True))

    assert cli.main(["header-report", "image.fit"]) == 0
    menu.assert_called_once_with(Path("report.txt"))


@pytest.mark.parametrize("answer", ("v", "f"))
def test_viewer_and_finder_failures_are_warnings(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    answer: str,
) -> None:
    responses = iter((answer, "q"))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))
    monkeypatch.setattr(cli.sys, "platform", "darwin")
    run = Mock(side_effect=CalledProcessError(1, ["open"]))
    monkeypatch.setattr("seestar_toolkit.fits.header_report.subprocess.run", run)

    from seestar_toolkit.fits.header_report import offer_report_menu

    offer_report_menu(Path("report.txt"))

    assert "Warning: unable to open" in capsys.readouterr().err
    expected = ["open", "report.txt"] if answer == "v" else ["open", "-R", "report.txt"]
    run.assert_called_once_with(expected, check=True, capture_output=True)


def test_operational_failure_returns_one_without_sensitive_exception_details(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "generate_header_report",
        Mock(side_effect=HeaderReportError("Unable to read FITS headers")),
    )

    assert cli.main(["header-report", "image.fit", "--noprompt"]) == 1
    assert capsys.readouterr().err == "Error: Unable to read FITS headers\n"


def test_existing_destination_returns_one_without_numeric_suffix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "image.fit"
    fits.PrimaryHDU().writeto(source)
    destination = tmp_path / "report.txt"
    destination.write_text("existing")

    assert (
        cli.main(
            ["header-report", source.as_posix(), "--output", destination.as_posix(), "--noprompt"]
        )
        == 1
    )

    assert destination.read_text() == "existing"
    assert not (tmp_path / "report_1.txt").exists()
    assert "refusing to overwrite" in capsys.readouterr().err


def test_argument_error_uses_exit_code_two() -> None:
    with pytest.raises(SystemExit) as raised:
        cli.main(["header-report", "--noprompt"])

    assert raised.value.code == 2
