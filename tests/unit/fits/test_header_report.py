"""Focused ENH-005b.1 header-report tests."""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.archive import ArchivePathSafetyError
from seestar_toolkit.fits.header_report import (
    HeaderReportError,
    generate_header_report,
    infer_header_report_path,
)

_B1_VALUES = {
    "BIAS": 12,
    "XORGSUBF": 10,
    "YORGSUBF": 20,
    "APERTURE": "S50",
    "EQMODE": 1,
    "WIDECAM": 0,
    "CCDXBIN": 1,
    "CCDYBIN": 1,
    "XPIXSZ": 2.4,
    "YPIXSZ": 2.4,
    "DATE-EXP": "2026-11-09T21:02:03",
    "TOTALEXP": 120.0,
    "STACKCNT": 12,
    "IMAGEW": 2160,
    "IMAGEH": 3840,
}

_SENSITIVE_VALUES = {
    "SITELAT": 51.5,
    "SITELONG": -1.2,
    "OBSERVER": "private",
    "OBSERVAT": "private",
    "SITENAME": "private",
    "SITEALT": 123,
    "LATITUDE": 51.5,
    "LONGITUD": -1.2,
    "AUTHOR": "private",
    "EMAIL": "private",
    "USERNAME": "private",
    "USER": "private",
    "HOSTNAME": "private",
    "FILENAME": "private",
    "FILEPATH": "private",
}


def _write_fits(path: Path) -> None:
    primary = fits.PrimaryHDU(np.arange(4, dtype=np.uint16).reshape(2, 2))
    primary.header["TELESCOP"] = ("S50 Pro_device", "device description")
    primary.header["DATE-OBS"] = "2026-11-06T20:00:00"
    primary.header["SITELAT"] = (51.5, "private site")
    primary.header["OBSERVER"] = "Private Person"
    primary.header["MYSTERY"] = ("secret unknown", "unknown note")
    primary.header.append(("GAIN", 80, "first gain"))
    primary.header.append(("GAIN", 90, "second gain"))
    primary.header.add_comment("private prose")
    primary.header.add_history("private history")
    extension = fits.ImageHDU(np.ones((1, 1), dtype=np.uint16), name="SECOND")
    extension.header["EXPTIME"] = 10.0
    fits.HDUList([primary, extension]).writeto(path)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_privacy_report_preserves_safe_replaces_sensitive_and_withholds_unknown(
    tmp_path: Path,
) -> None:
    source = tmp_path / "capture.fit"
    output = tmp_path / "report.txt"
    _write_fits(source)
    before = _digest(source)

    result = generate_header_report(source, output)

    report = output.read_text()
    assert result.hdu_count == 2
    assert report.index("GAIN = 80") < report.index("GAIN = 90")
    assert "--- HDU 0 ---" in report and "--- HDU 1 ---" in report
    assert "S50 Pro_device" in report
    assert "2026-11-06T20:00:00" in report
    assert "SITELAT = 0.0" in report
    assert "OBSERVER = 'REMOVED'" in report
    assert "MYSTERY = 'WITHHELD'" in report
    assert "COMMENT = 'WITHHELD'" in report
    assert "HISTORY = 'WITHHELD'" in report
    for private_text in (
        "Private Person",
        "secret unknown",
        "unknown note",
        "private site",
        "private prose",
        "private history",
        "device description",
    ):
        assert private_text not in report
    assert _digest(source) == before


def test_all_b1_keyword_values_are_preserved(tmp_path: Path) -> None:
    source = tmp_path / "b1.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    for keyword, value in _B1_VALUES.items():
        primary.header[keyword] = value
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    for keyword, value in _B1_VALUES.items():
        rendered = repr(value) if isinstance(value, str) else str(value)
        assert f"{keyword} = {rendered}" in report


@pytest.mark.parametrize("telescope", ("S50_test", "S50 Pro_test"))
def test_reviewed_light_descriptions_are_preserved(tmp_path: Path, telescope: str) -> None:
    source = tmp_path / "light.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    primary.header["TELESCOP"] = (telescope, "Telescope name")
    primary.header["BIAS"] = (16, "Correction from bias")
    primary.header["DATE-EXP"] = ("2026-11-09T21:02:03", "Exposure end time")
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    assert f"TELESCOP = '{telescope}' / 'Telescope name'" in report
    assert "BIAS = 16 / 'Correction from bias'" in report
    assert "DATE-EXP = '2026-11-09T21:02:03' / 'Exposure end time'" in report


def test_reviewed_stacked_wcs_and_sip_descriptions_are_preserved(
    tmp_path: Path,
) -> None:
    source = tmp_path / "stacked.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    primary.header["STACKCNT"] = (7, "Stack frames")
    primary.header["IMAGEW"] = (2160, "Image width,  in pixels.")
    primary.header["IMAGEH"] = (3840, "Image height, in pixels.")
    primary.header["CTYPE1"] = (
        "RA---TAN-SIP",
        "TAN (gnomic) projection + SIP distortions",
    )
    primary.header["CRPIX1"] = (1498.0, "X reference pixel")
    primary.header["A_ORDER"] = (2, "Polynomial order, axis 1")
    primary.header["A_0_0"] = (0.0, "no comment")
    primary.header["CD1_2"] = (-0.0003, "no comment")
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    for description in (
        "Stack frames",
        "Image width,  in pixels.",
        "Image height, in pixels.",
        "TAN (gnomic) projection + SIP distortions",
        "X reference pixel",
        "Polynomial order, axis 1",
    ):
        assert f"/ '{description}'" in report
    assert report.count("/ 'no comment'") == 2


def test_unapproved_descriptions_and_free_text_are_always_withheld(
    tmp_path: Path,
) -> None:
    source = tmp_path / "comments.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    primary.header["TELESCOP"] = ("S50_test", "hostile description")
    primary.header["CTYPE1"] = ("RA---TAN-SIP", "modified projection description")
    primary.header["CRPIX1"] = (1498.0, "no comment")
    primary.header["MYSTERY"] = ("unknown value", "unknown description")
    primary.header.add_comment("standalone private comment")
    primary.header.add_history("standalone private history")
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    assert "TELESCOP = 'S50_test' / 'WITHHELD'" in report
    assert "CTYPE1 = 'RA---TAN-SIP' / 'WITHHELD'" in report
    assert "CRPIX1 = 1498.0 / 'WITHHELD'" in report
    assert "MYSTERY = 'WITHHELD' / 'WITHHELD'" in report
    assert "COMMENT = 'WITHHELD'" in report
    assert "HISTORY = 'WITHHELD'" in report
    for private_text in (
        "hostile description",
        "modified projection description",
        "unknown value",
        "unknown description",
        "standalone private comment",
        "standalone private history",
    ):
        assert private_text not in report


def test_sensitive_value_replacement_is_independent_of_description(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sensitive.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    primary.header["SITELAT"] = (51.5, "latitude of the imaging site in degrees")
    primary.header["OBSERVER"] = ("Private Person", "unapproved observer description")
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    assert "SITELAT = 0.0 / 'latitude of the imaging site in degrees'" in report
    assert "OBSERVER = 'REMOVED' / 'WITHHELD'" in report
    assert "Private Person" not in report
    assert "unapproved observer description" not in report


def test_all_sensitive_keywords_and_replacement_types(tmp_path: Path) -> None:
    source = tmp_path / "sensitive-types.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    for keyword, value in _SENSITIVE_VALUES.items():
        primary.header[keyword] = value
    primary.header["AUTHOR"] = True
    primary.header["SITEALT"] = 123
    primary.header["LATITUDE"] = 51.5
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    assert "SITELAT = 0.0" in report
    assert "SITELONG = 0.0" in report
    assert "AUTHOR = False" in report
    assert "SITEALT = 0" in report
    assert "LATITUDE = 0.0" in report
    for keyword, value in _SENSITIVE_VALUES.items():
        if keyword in {"SITELAT", "SITELONG", "AUTHOR", "SITEALT", "LATITUDE"}:
            continue
        replacement = "0.0" if isinstance(value, float) else "'REMOVED'"
        assert f"{keyword} = {replacement}" in report
    assert "private" not in report


def test_long_safe_string_is_readable_and_unknown_hierarch_value_is_withheld(
    tmp_path: Path,
) -> None:
    source = tmp_path / "complex.fit"
    output = tmp_path / "report.txt"
    primary = fits.PrimaryHDU()
    telescope = "S50 Pro_" + "device" * 20
    primary.header["TELESCOP"] = telescope
    primary.header["HIERARCH PRIVATE CUSTOM FIELD"] = "do not disclose"
    primary.writeto(source)

    generate_header_report(source, output)

    report = output.read_text()
    assert telescope in report
    assert "PRIVATE CUSTOM FIELD = 'WITHHELD'" in report
    assert "do not disclose" not in report


def test_default_ordinary_and_archive_owned_paths(tmp_path: Path) -> None:
    ordinary = tmp_path / "captures/Light 001.fit"
    light = tmp_path / "archive/observation_02/fits_images/lights/Light.fit"
    stacked = tmp_path / "archive/observation_02/seestar_stacked/Stacked.fits"
    for source in (ordinary, light, stacked):
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"existing")

    assert infer_header_report_path(ordinary) == (
        ordinary.parent / "pii-scrubbed/Light 001_header.txt"
    )
    assert infer_header_report_path(light) == (light.parents[2] / "pii-scrubbed/Light_header.txt")
    assert infer_header_report_path(stacked) == (
        stacked.parents[1] / "pii-scrubbed/Stacked_header.txt"
    )


@pytest.mark.parametrize(
    "relative",
    (
        "observation_02/Light.fit",
        "observation_02/lights/Light.fit",
        "observation_02/fits_images/Light.fit",
        "observation_bad/fits_images/lights/Light.fit",
    ),
)
def test_archive_like_recognition_failures_use_ordinary_fallback(
    tmp_path: Path, relative: str
) -> None:
    source = tmp_path / relative
    source.parent.mkdir(parents=True)
    source.write_bytes(b"existing")

    assert infer_header_report_path(source) == (
        source.parent / "pii-scrubbed" / f"{source.stem}_header.txt"
    )


@pytest.mark.parametrize("kind", ("light", "stacked"))
def test_archive_source_symlink_escape_is_rejected(tmp_path: Path, kind: str) -> None:
    observation = tmp_path / "observation_02"
    source_dir = observation / ("fits_images/lights" if kind == "light" else "seestar_stacked")
    source_dir.mkdir(parents=True)
    outside = tmp_path / "outside.fit"
    outside.write_bytes(b"existing")
    source = source_dir / "source.fit"
    source.symlink_to(outside)

    with pytest.raises(ArchivePathSafetyError, match="escapes"):
        infer_header_report_path(source)

    with pytest.raises(HeaderReportError, match="Unsafe archive path"):
        generate_header_report(source)


@pytest.mark.parametrize("kind", ("light", "stacked"))
def test_archive_destination_symlink_escape_is_rejected(tmp_path: Path, kind: str) -> None:
    observation = tmp_path / "observation_02"
    source_dir = observation / ("fits_images/lights" if kind == "light" else "seestar_stacked")
    source_dir.mkdir(parents=True)
    source = source_dir / "source.fit"
    source.write_bytes(b"existing")
    outside = tmp_path / "outside"
    outside.mkdir()
    (observation / "pii-scrubbed").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ArchivePathSafetyError, match="destination escapes"):
        infer_header_report_path(source)

    assert tuple(outside.iterdir()) == ()


@pytest.mark.parametrize("alias_kind", ("symlink", "equivalent"))
def test_resolved_source_destination_alias_is_rejected(tmp_path: Path, alias_kind: str) -> None:
    source = tmp_path / "capture.fit"
    _write_fits(source)
    if alias_kind == "symlink":
        alias = tmp_path / "alias.fit"
        alias.symlink_to(source)
    else:
        alias = tmp_path / "unused" / ".." / source.name

    with pytest.raises(HeaderReportError, match="different files"):
        generate_header_report(source, alias)


def test_headers_are_read_without_accessing_hdu_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "capture.fit"
    output = tmp_path / "report.txt"
    source.write_bytes(b"placeholder")

    class HeaderOnlyHdu:
        header = fits.Header({"TELESCOP": "S50_test"})

        @property
        def data(self) -> object:
            raise AssertionError("image data was loaded")

    class HeaderOnlyList(list[HeaderOnlyHdu]):
        def __enter__(self) -> HeaderOnlyList:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    opened = Mock(return_value=HeaderOnlyList([HeaderOnlyHdu(), HeaderOnlyHdu()]))
    monkeypatch.setattr("seestar_toolkit.fits.header_report.fits.open", opened)

    result = generate_header_report(source, output)

    assert result.hdu_count == 2
    opened.assert_called_once_with(
        source,
        mode="readonly",
        memmap=True,
        lazy_load_hdus=True,
        do_not_scale_image_data=True,
    )


def test_explicit_output_is_exact_and_never_overwritten(tmp_path: Path) -> None:
    source = tmp_path / "capture.fit"
    output = tmp_path / "exact.name"
    _write_fits(source)
    output.write_text("existing")

    with pytest.raises(HeaderReportError, match="refusing to overwrite"):
        generate_header_report(source, output)

    assert output.read_text() == "existing"
    assert not (tmp_path / "exact_1.name").exists()


def test_failure_does_not_publish_incomplete_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "capture.fit"
    output = tmp_path / "report.txt"
    _write_fits(source)
    before = _digest(source)
    monkeypatch.setattr("os.link", Mock(side_effect=OSError("failure")))

    with pytest.raises(HeaderReportError, match="Unable to write"):
        generate_header_report(source, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".header-report-*"))
    assert _digest(source) == before
