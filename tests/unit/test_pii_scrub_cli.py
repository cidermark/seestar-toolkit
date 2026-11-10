"""Focused CLI integration tests for ENH-005c.2."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from seestar_toolkit import cli
from seestar_toolkit.fits import PiiScrubCancelled, PiiScrubError, UnknownMetadataAction


def test_parser_accepts_options_on_either_side_and_requires_one_input() -> None:
    before = cli.build_parser().parse_args(["pii-scrub", "--output", "out.fit", "in.fit"])
    after = cli.build_parser().parse_args(["pii-scrub", "in.fit", "--output", "out.fit"])
    assert before == after
    with pytest.raises(SystemExit) as raised:
        cli.main(["pii-scrub"])
    assert raised.value.code == 2
    with pytest.raises(SystemExit) as raised:
        cli.main(["pii-scrub", "one.fit", "two.fit"])
    assert raised.value.code == 2


@pytest.mark.parametrize(("stdin_tty", "stdout_tty"), ((False, True), (True, False)))
def test_noninteractive_mode_does_not_prompt_and_warns_without_values(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_tty: bool,
    stdout_tty: bool,
) -> None:
    scrub = Mock(
        return_value=SimpleNamespace(
            output_path=Path("out.fit"),
            anonymized_unknown_count=2,
            preserved_unknown_count=0,
        )
    )
    monkeypatch.setattr(cli, "scrub_fits", scrub)
    monkeypatch.setattr(cli.sys.stdin, "isatty", Mock(return_value=stdin_tty))
    monkeypatch.setattr(cli.sys.stdout, "isatty", Mock(return_value=stdout_tty))

    assert cli.main(["pii-scrub", "in.fit"]) == 0
    assert scrub.call_args.kwargs["reviewer"] is None
    assert "unknown metadata" in capsys.readouterr().err


def test_interactive_empty_invalid_then_a_p_and_warning(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    answers = iter(("", "invalid", "a", "p"))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    occurrence = SimpleNamespace(hdu_index=0, card_index=4, keyword="ODD", value="secret")
    assert cli._review_unknown_metadata(occurrence, "REMOVED") is UnknownMetadataAction.ANONYMIZE
    assert cli._review_unknown_metadata(occurrence, "REMOVED") is UnknownMetadataAction.PRESERVE
    output = capsys.readouterr().out
    assert output.count("Choose A, P, or Q") == 2


def test_interactive_q_returns_one_and_no_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.sys.stdin, "isatty", Mock(return_value=True))
    monkeypatch.setattr(cli.sys.stdout, "isatty", Mock(return_value=True))
    monkeypatch.setattr(cli, "scrub_fits", Mock(side_effect=PiiScrubCancelled("cancelled")))

    assert cli.main(["pii-scrub", "in.fit"]) == 1
    captured = capsys.readouterr()
    assert "no privacy-processed FITS" in captured.err
    assert "Created" not in captured.out


def test_preserved_unknown_emits_review_required_and_operational_failure_is_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.sys.stdin, "isatty", Mock(return_value=True))
    monkeypatch.setattr(cli.sys.stdout, "isatty", Mock(return_value=True))
    monkeypatch.setattr(
        cli,
        "scrub_fits",
        Mock(
            return_value=SimpleNamespace(
                output_path=Path("out.fit"),
                anonymized_unknown_count=0,
                preserved_unknown_count=1,
            )
        ),
    )
    assert cli.main(["pii-scrub", "in.fit"]) == 0
    assert "REVIEW REQUIRED" in capsys.readouterr().err

    monkeypatch.setattr(cli, "scrub_fits", Mock(side_effect=PiiScrubError("safe failure")))
    assert cli.main(["pii-scrub", "in.fit"]) == 1
    assert capsys.readouterr().err == "Error: safe failure\n"
