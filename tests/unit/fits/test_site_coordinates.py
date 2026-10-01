"""Strict site extraction examines every header/card without touching image data."""

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.fits.site_coordinates import SiteCoordinatesError, extract_site_coordinates


def write_headers(tmp_path, headers):
    hdus = [fits.PrimaryHDU(header=headers[0])]
    hdus.extend(fits.ImageHDU(header=header) for header in headers[1:])
    path = tmp_path / "site.fits"
    fits.HDUList(hdus).writeto(path)
    return path


def header(*cards):
    return fits.Header(cards)


def test_header_only_accepts_identical_duplicate_and_extension_evidence(tmp_path, monkeypatch):
    path = tmp_path / "site.fits"
    site = header(("SITELAT", 12), ("SITELAT", "12.0"), ("SITELONG", -34))
    fits.HDUList(
        [
            fits.PrimaryHDU(data=np.zeros((8, 8)), header=site),
            fits.ImageHDU(header=header(("SITELAT", 12.0), ("SITELONG", "-34"))),
            fits.ImageHDU(),
        ]
    ).writeto(path)

    def forbidden(*args, **kwargs):
        raise AssertionError("GPS must not load image arrays")

    monkeypatch.setattr(fits.PrimaryHDU, "data", property(forbidden))
    monkeypatch.setattr(fits.ImageHDU, "data", property(forbidden))
    point = extract_site_coordinates(path)
    assert (point.latitude, point.longitude) == (12, -34)


@pytest.mark.parametrize(
    "headers,message",
    [
        ([header(("RA", 12), ("DEC", 34))], "missing|Missing"),
        ([header(("SITELAT", 12)), header(("SITELONG", 34))], "HDU 0.*incomplete"),
        ([header(("SITELAT", 12), ("SITELONG", 34)), header(("SITELAT", 12))], "HDU 1.*incomplete"),
        ([header(("SITELAT", 12), ("SITELAT", 13), ("SITELONG", 34))], "HDU 0.*SITELAT.*conflict"),
        (
            [header(("SITELAT", 12), ("SITELONG", 34)), header(("SITELAT", 13), ("SITELONG", 34))],
            "HDU 0.*HDU 1|HDU 1.*HDU 0",
        ),
        ([header(("SITELAT", True), ("SITELONG", 34))], "SITELAT"),
        ([header(("SITELAT", "NaN"), ("SITELONG", 34))], "SITELAT"),
        ([header(("SITELAT", 91), ("SITELONG", 34))], "SITELAT"),
        ([header(("SITELAT", 12), ("SITELONG", "inf"))], "SITELONG"),
        ([header(("SITELAT", 12), ("SITELONG", -181))], "SITELONG"),
        ([header(("SITELAT", "12:30:00"), ("SITELONG", 34))], "SITELAT"),
    ],
)
def test_rejects_invalid_or_conflicting_site_evidence(tmp_path, headers, message):
    with pytest.raises(SiteCoordinatesError, match=message):
        extract_site_coordinates(write_headers(tmp_path, headers))


def test_extension_only_site_and_numeric_boundaries(tmp_path):
    point = extract_site_coordinates(
        write_headers(tmp_path, [header(), header(("SITELAT", "-90"), ("SITELONG", "180"))])
    )
    assert (point.latitude, point.longitude) == (-90, 180)


def test_missing_and_unreadable_fits(tmp_path):
    path = tmp_path / "bad.fits"
    with pytest.raises(SiteCoordinatesError):
        extract_site_coordinates(path)
    path.write_text("not FITS")
    with pytest.raises(SiteCoordinatesError):
        extract_site_coordinates(path)


def test_conflicting_longitude_and_invalid_later_duplicate(tmp_path):
    for duplicate in (35, "bad"):
        path = write_headers(
            tmp_path, [header(("SITELAT", 12), ("SITELONG", 34), ("SITELONG", duplicate))]
        )
        with pytest.raises(SiteCoordinatesError, match="HDU 0.*SITELONG"):
            extract_site_coordinates(path)
        path.unlink()


def test_malformed_extension_is_not_silently_ignored(tmp_path):
    path = write_headers(tmp_path, [header(("SITELAT", 12), ("SITELONG", 34))])
    with path.open("ab") as stream:
        stream.write(b"malformed extension".ljust(2880, b" "))
    with pytest.raises(SiteCoordinatesError, match="Unable to read"):
        extract_site_coordinates(path)


def test_table_hdu_site_does_not_require_convertible_image(tmp_path, monkeypatch):
    path = tmp_path / "table.fits"
    fits.HDUList(
        [fits.PrimaryHDU(), fits.BinTableHDU(header=header(("SITELAT", 1), ("SITELONG", 2)))]
    ).writeto(path)

    def forbidden(*args, **kwargs):
        raise AssertionError("No table data loading")

    monkeypatch.setattr(fits.BinTableHDU, "data", property(forbidden))
    assert extract_site_coordinates(path).latitude == 1
