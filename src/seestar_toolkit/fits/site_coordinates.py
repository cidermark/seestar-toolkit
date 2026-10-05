"""Strict header-only observing-site extraction for explicit configuration commands."""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from pathlib import Path

from astropy.io import fits
from astropy.io.fits.verify import VerifyError
from astropy.utils.exceptions import AstropyWarning

from .exceptions import FitsError


class SiteCoordinatesError(FitsError):
    """Site evidence is missing, unreadable, incomplete or contradictory."""


@dataclass(frozen=True)
class SiteCoordinates:
    latitude: float
    longitude: float


def _coordinate(value, key: str, hdu_index: int, occurrence: int) -> float:
    label = f"HDU {hdu_index} {key} card {occurrence}"
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise SiteCoordinatesError(f"{label}: expected numeric degrees")
    try:
        number = float(value)
    except (ValueError, OverflowError) as error:
        raise SiteCoordinatesError(f"{label}: expected numeric degrees") from error
    limit = 90 if key == "SITELAT" else 180
    if not math.isfinite(number) or not -limit <= number <= limit:
        raise SiteCoordinatesError(f"{label}: expected finite degrees in [-{limit}, {limit}]")
    return number


def extract_site_coordinates(path: str | Path) -> SiteCoordinates:
    """Read all HDU headers, including duplicate cards, without accessing HDU data."""
    evidence = None
    evidence_hdu = None
    try:
        with warnings.catch_warnings():
            # Astropy may otherwise warn and skip a malformed extension header.
            warnings.simplefilter("error", AstropyWarning)
            with fits.open(
                path,
                mode="readonly",
                memmap=True,
                lazy_load_hdus=True,
                do_not_scale_image_data=True,
            ) as hdus:
                for index, hdu in enumerate(hdus):
                    values = {"SITELAT": [], "SITELONG": []}
                    for card in hdu.header.cards:
                        if card.keyword in values:
                            entries = values[card.keyword]
                            entries.append(
                                _coordinate(card.value, card.keyword, index, len(entries) + 1)
                            )
                    if not any(values.values()):
                        continue
                    if not all(values.values()):
                        raise SiteCoordinatesError(f"HDU {index}: incomplete SITELAT/SITELONG pair")
                    for key, entries in values.items():
                        if len(set(entries)) != 1:
                            raise SiteCoordinatesError(
                                f"HDU {index} {key}: conflicting duplicate cards "
                                f"(occurrences 1–{len(entries)})"
                            )
                    point = SiteCoordinates(values["SITELAT"][0], values["SITELONG"][0])
                    if evidence is not None and evidence != point:
                        raise SiteCoordinatesError(
                            f"Conflicting SITELAT/SITELONG pairs in HDU {evidence_hdu} "
                            f"and HDU {index}"
                        )
                    evidence, evidence_hdu = point, index
    except (OSError, ValueError, TypeError, VerifyError, AstropyWarning) as error:
        raise SiteCoordinatesError(f"Unable to read FITS site headers: {path}") from error
    if evidence is None:
        raise SiteCoordinatesError(f"Missing SITELAT/SITELONG site coordinates: {path}")
    return evidence
