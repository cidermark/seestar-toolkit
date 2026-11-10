"""Focused CLI integration tests for ENH-005c.3."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from seestar_toolkit import cli
from seestar_toolkit.fits import FitsVerificationError, PrivacyVerificationStatus


def test_parser_accepts_verify_options_on_either_side_and_requires_one_input() -> None:
    before = cli.build_parser().parse_args(
        ["pii-scrub", "--verify", "--output", "report.txt", "in.fit"]
    )
    after = cli.build_parser().parse_args(
        ["pii-scrub", "in.fit", "--output", "report.txt", "--verify"]
    )
    assert before == after
    with pytest.raises(SystemExit) as raised:
        cli.main(["pii-scrub", "--verify"])
    assert raised.value.code == 2
    with pytest.raises(SystemExit) as raised:
        cli.main(["pii-scrub", "--verify", "one.fit", "two.fit"])
    assert raised.value.code == 2


@pytest.mark.parametrize(
    ("status", "exit_code"),
    [
        (PrivacyVerificationStatus.PASS, 0),
        (PrivacyVerificationStatus.FAIL, 1),
        (PrivacyVerificationStatus.REVIEW_REQUIRED, 1),
    ],
)
def test_status_exit_codes_output_and_noninteractive_operation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    status: PrivacyVerificationStatus,
    exit_code: int,
) -> None:
    verify = Mock(
        return_value=SimpleNamespace(
            status=status,
            hdu_count=2,
            safe_keyword_counts={"TELESCOP": 2, "SITELAT": 1},
            violation_count=1 if status is PrivacyVerificationStatus.FAIL else 0,
            unknown_count=1 if status is PrivacyVerificationStatus.REVIEW_REQUIRED else 0,
            output_path=Path("report.txt"),
        )
    )
    monkeypatch.setattr(cli, "verify_fits_privacy", verify)
    monkeypatch.setattr("builtins.input", Mock(side_effect=AssertionError("prompted")))

    assert cli.main(["pii-scrub", "--verify", "in.fit", "--output", "report.txt"]) == exit_code
    captured = capsys.readouterr()
    assert f"Verification: {status.value}" in captured.out
    assert "TELESCOP: 2" in captured.out
    assert "SITELAT: 1" in captured.out
    assert "report.txt" in captured.out
    verify.assert_called_once_with(Path("in.fit"), Path("report.txt"))


def test_report_path_is_safely_rendered(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli,
        "verify_fits_privacy",
        Mock(
            return_value=SimpleNamespace(
                status=PrivacyVerificationStatus.PASS,
                hdu_count=1,
                safe_keyword_counts={},
                violation_count=0,
                unknown_count=0,
                output_path=Path("report\x1b[2J.txt"),
            )
        ),
    )

    assert cli.main(["pii-scrub", "--verify", "in.fit"]) == 0
    output = capsys.readouterr().out
    assert "\x1b" not in output
    assert "\\x1b" in output


def test_operational_error_is_safe_and_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli, "verify_fits_privacy", Mock(side_effect=FitsVerificationError("safe diagnostic"))
    )

    assert cli.main(["pii-scrub", "--verify", "private.fit"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Error: safe diagnostic\n"
