"""Focused ENH-005c.3 independent-verification tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.fits import (
    FitsVerificationError,
    PrivacyVerificationStatus,
    UnknownMetadataAction,
    scrub_fits,
    verify_fits_privacy,
)


def _write(path: Path, *headers: list[tuple[str, object, str]]) -> bytes:
    hdus: list[fits.hdu.base._BaseHDU] = []
    for index, cards in enumerate(headers):
        hdu = (
            fits.PrimaryHDU(np.arange(4, dtype=np.uint16).reshape(2, 2))
            if index == 0
            else fits.ImageHDU(np.arange(3, dtype=np.int16))
        )
        for card in hdu.header.cards:
            card.comment = ""
        for keyword, value, description in cards:
            if keyword == "COMMENT":
                hdu.header.add_comment(value)
            elif keyword == "HISTORY":
                hdu.header.add_history(value)
            else:
                hdu.header.append((keyword, value, description))
        hdus.append(hdu)
    fits.HDUList(hdus).writeto(path)
    return path.read_bytes()


def test_pass_reports_safe_names_counts_without_loading_pixel_arrays(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "pass.fit"
    original = _write(
        source,
        [("TELESCOP", "S50 Pro_device", "Telescope name"), ("SITELAT", 0.0, "")],
    )
    data_getter = Mock(side_effect=AssertionError("pixel data loaded"))
    monkeypatch.setattr(fits.PrimaryHDU, "data", property(data_getter))

    result = verify_fits_privacy(source)

    assert result.status is PrivacyVerificationStatus.PASS
    assert result.safe_keyword_counts["TELESCOP"] == 1
    assert result.safe_keyword_counts["SITELAT"] == 1
    assert result.violation_count == result.unknown_count == 0
    assert source.read_bytes() == original
    assert data_getter.call_count == 0


def test_fail_precedes_review_and_covers_duplicates_hdus_descriptions_and_free_text(
    tmp_path: Path,
) -> None:
    source = tmp_path / "fail.fit"
    _write(
        source,
        [
            ("OBSERVER", "Private Person", ""),
            ("MYSTERY", "unknown-one", "private description"),
            ("MYSTERY", "unknown-two", ""),
            ("COMMENT", "private comment", ""),
        ],
        [("EMAIL", "REMOVED", "private description"), ("HISTORY", "REMOVED", "")],
    )

    result = verify_fits_privacy(source)

    assert result.status is PrivacyVerificationStatus.FAIL
    assert result.violation_count == 4  # sensitive value, two descriptions, and COMMENT
    assert result.unknown_count == 2
    assert result.safe_keyword_counts["EMAIL"] == 1


def test_unknown_and_previously_preserved_unknown_require_review(tmp_path: Path) -> None:
    source = tmp_path / "review.fit"
    _write(
        source,
        [("MYSTERY", "REMOVED", ""), ("PRESERVE", "original unknown", "REMOVED")],
    )

    result = verify_fits_privacy(source)

    assert result.status is PrivacyVerificationStatus.REVIEW_REQUIRED
    assert result.unknown_count == 2
    assert result.violation_count == 0

    scrub_source = tmp_path / "preserve-source.fit"
    _write(scrub_source, [("MYSTERY", "preserved by reviewer", "")])
    scrubbed = scrub_fits(
        scrub_source,
        reviewer=lambda _occurrence, _replacement: UnknownMetadataAction.PRESERVE,
    )
    preserved_result = verify_fits_privacy(scrubbed.output_path)
    assert preserved_result.status is PrivacyVerificationStatus.REVIEW_REQUIRED
    assert preserved_result.unknown_count == 1


def test_compliant_removed_descriptions_comment_and_history_pass(tmp_path: Path) -> None:
    source = tmp_path / "free-text.fit"
    _write(
        source,
        [
            ("TELESCOP", "S50", "REMOVED"),
            ("COMMENT", "REMOVED", ""),
            ("HISTORY", "REMOVED", ""),
        ],
    )

    result = verify_fits_privacy(source)

    assert result.status is PrivacyVerificationStatus.PASS


def test_report_is_safe_exact_no_overwrite_and_source_unchanged(tmp_path: Path) -> None:
    source = tmp_path / "private-name.fit"
    original = _write(source, [("OBSERVER", "Secret Name", "")])
    report = tmp_path / "reports/result.txt"

    result = verify_fits_privacy(source, report)

    text = report.read_text()
    assert result.output_path == report
    assert "Status: FAIL" in text
    assert "OBSERVER: 1" in text
    assert "Secret Name" not in text
    assert "private-name" not in text
    assert source.read_bytes() == original
    with pytest.raises(FitsVerificationError, match="refusing to overwrite"):
        verify_fits_privacy(source, report)
    with pytest.raises(FitsVerificationError, match="different files"):
        verify_fits_privacy(source, source)
    alias = tmp_path / "alias.txt"
    alias.symlink_to(source)
    with pytest.raises(FitsVerificationError, match="different files"):
        verify_fits_privacy(source, alias)


def test_report_publication_failure_cleans_temporary_and_does_not_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "input.fit"
    _write(source, [("TELESCOP", "S50", "")])
    destination = tmp_path / "result.txt"
    monkeypatch.setattr(
        "seestar_toolkit.fits.privacy_verification.os.link", Mock(side_effect=OSError())
    )

    with pytest.raises(FitsVerificationError, match="publish verification report"):
        verify_fits_privacy(source, destination)

    assert not destination.exists()
    assert not tuple(tmp_path.glob(".pii-verify-*"))


def test_report_publication_race_never_replaces_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "input.fit"
    _write(source, [("TELESCOP", "S50", "")])
    destination = tmp_path / "result.txt"

    def collide(_temporary: Path, target: Path) -> None:
        target.write_text("racing file")
        raise FileExistsError

    monkeypatch.setattr("seestar_toolkit.fits.privacy_verification.os.link", collide)
    with pytest.raises(FitsVerificationError, match="refusing to overwrite"):
        verify_fits_privacy(source, destination)

    assert destination.read_text() == "racing file"
    assert not tuple(tmp_path.glob(".pii-verify-*"))


def test_malformed_unsupported_and_unsafe_report_paths_are_operational_errors(
    tmp_path: Path,
) -> None:
    malformed = tmp_path / "malformed.fit"
    malformed.write_bytes(b"not FITS")
    table = tmp_path / "unsupported.fit"
    fits.HDUList(
        [
            fits.PrimaryHDU(),
            fits.TableHDU.from_columns(
                [fits.Column(name="V", format="I4", array=np.array([1, 2]))]
            ),
        ]
    ).writeto(table)
    for source in (malformed, table):
        with pytest.raises(FitsVerificationError):
            verify_fits_privacy(source)

    source = tmp_path / "input.fit"
    _write(source, [("TELESCOP", "S50", "")])
    dangling = tmp_path / "dangling.txt"
    dangling.symlink_to(tmp_path / "missing.txt")
    with pytest.raises(FitsVerificationError, match="refusing to overwrite"):
        verify_fits_privacy(source, dangling)
