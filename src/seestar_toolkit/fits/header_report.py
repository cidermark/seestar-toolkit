"""Privacy-processed, header-only FITS reporting."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path

from astropy.io import fits
from astropy.io.fits.verify import VerifyError
from astropy.utils.exceptions import AstropyWarning

from .exceptions import FitsError

_SENSITIVE = {
    "SITELAT",
    "SITELONG",
    "OBSERVER",
    "OBSERVAT",
    "SITENAME",
    "SITEALT",
    "LATITUDE",
    "LONGITUD",
    "AUTHOR",
    "EMAIL",
    "USERNAME",
    "USER",
    "HOSTNAME",
    "FILENAME",
    "FILEPATH",
}

_SAFE = {
    "SIMPLE",
    "BITPIX",
    "EXTEND",
    "XTENSION",
    "PCOUNT",
    "GCOUNT",
    "GROUPS",
    "TFIELDS",
    "BSCALE",
    "BZERO",
    "BLANK",
    "DATAMIN",
    "DATAMAX",
    "CHECKSUM",
    "DATASUM",
    "EXTNAME",
    "EXTVER",
    "EXTLEVEL",
    "TELESCOP",
    "INSTRUME",
    "CREATOR",
    "PRODUCER",
    "PROGRAM",
    "OBJECT",
    "IMAGETYP",
    "DATE",
    "DATE-OBS",
    "DATE-END",
    "MJD-OBS",
    "MJD-END",
    "TIMESYS",
    "TIMEUNIT",
    "EXPTIME",
    "EXPOSURE",
    "GAIN",
    "OFFSET",
    "FILTER",
    "FOCUSPOS",
    "FOCALLEN",
    "FOCRATIO",
    "CCD-TEMP",
    "SET-TEMP",
    "SENSOR",
    "BAYERPAT",
    "XBAYROFF",
    "YBAYROFF",
    "XBINNING",
    "YBINNING",
    "PIXSIZE1",
    "PIXSIZE2",
    "RA",
    "DEC",
    "OBJCTRA",
    "OBJCTDEC",
    "EQUINOX",
    "RADESYS",
    "LONPOLE",
    "LATPOLE",
    "BIAS",
    "XORGSUBF",
    "YORGSUBF",
    "APERTURE",
    "EQMODE",
    "WIDECAM",
    "CCDXBIN",
    "CCDYBIN",
    "XPIXSZ",
    "YPIXSZ",
    "DATE-EXP",
    "TOTALEXP",
    "STACKCNT",
    "IMAGEW",
    "IMAGEH",
}

_SAFE_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"NAXIS\d*",
        r"WCSAXES",
        r"(?:CTYPE|CUNIT|CRPIX|CRVAL|CDELT|CROTA)\d+",
        r"(?:CD|PC)\d+_\d+",
        r"(?:PV|PS)\d+_\d+",
        r"(?:A|B|AP|BP)_(?:ORDER|\d+_\d+)",
        r"(?:TFORM|TTYPE|TUNIT|TNULL|TSCAL|TZERO|TDIM|TDISP)\d+",
    )
)

_SAFE_DESCRIPTIONS = frozenset(
    {
        ("SIMPLE", "file does conform to FITS standard"),
        ("BITPIX", "number of bits per data pixel"),
        ("NAXIS", "number of data axes"),
        ("NAXIS1", "length of data axis 1"),
        ("NAXIS2", "length of data axis 2"),
        ("NAXIS3", "length of data axis 3"),
        ("EXTEND", "FITS dataset may contain extensions"),
        ("BZERO", "offset data range to that of unsigned short"),
        ("BSCALE", "default scaling factor"),
        ("CREATOR", "Capture software"),
        ("PRODUCER", "Powered by ZWO"),
        ("BIAS", "Correction from bias"),
        ("XORGSUBF", "Subframe X position in binned pixels"),
        ("YORGSUBF", "Subframe Y position in binned pixels"),
        ("FOCALLEN", "Focal length of telescope in mm"),
        ("APERTURE", "Name of field of view aperture"),
        ("EQMODE", "Equatorial mode"),
        ("WIDECAM", "Is wide camera"),
        ("PROGRAM", "The name of the software task that created the"),
        ("XBINNING", "Camera X Bin"),
        ("YBINNING", "Camera Y Bin"),
        ("CCDXBIN", "Camera X Bin"),
        ("CCDYBIN", "Camera Y Bin"),
        ("XPIXSZ", "pixel size in microns (with binning)"),
        ("YPIXSZ", "pixel size in microns (with binning)"),
        ("IMAGETYP", "Type of image"),
        ("EXPOSURE", "Exposure time in seconds"),
        ("EXPTIME", "Exposure time in seconds"),
        ("CCD-TEMP", "sensor temperature in C"),
        ("RA", "Object Right Ascension in degrees"),
        ("DEC", "Object Declination in degrees"),
        ("SITELONG", "longitude of the imaging site in degrees"),
        ("SITELAT", "latitude of the imaging site in degrees"),
        ("DATE-OBS", "Image created time"),
        ("DATE-EXP", "Exposure end time"),
        ("FILTER", "Filter used when taking image"),
        ("INSTRUME", "Camera model"),
        ("BAYERPAT", "Bayer pattern"),
        ("GAIN", "Gain Value"),
        ("FOCUSPOS", "Focuser position in steps"),
        ("TELESCOP", "Telescope name"),
        ("OBJECT", "name or catalog number of object being imaged"),
        ("TOTALEXP", "Total Exposure Time in seconds"),
        ("STACKCNT", "Stack frames"),
        ("IMAGEW", "Image width,  in pixels."),
        ("IMAGEH", "Image height, in pixels."),
        ("A_ORDER", "Polynomial order, axis 1"),
        ("B_ORDER", "Polynomial order, axis 2"),
        ("AP_ORDER", "Inv polynomial order, axis 1"),
        ("BP_ORDER", "Inv polynomial order, axis 2"),
        ("CD1_1", "Transformation matrix"),
        ("CRPIX1", "X reference pixel"),
        ("CRPIX2", "Y reference pixel"),
        ("CRVAL1", "RA  of reference point"),
        ("CRVAL2", "DEC of reference point"),
        ("CTYPE1", "TAN (gnomic) projection + SIP distortions"),
        ("CTYPE2", "TAN (gnomic) projection + SIP distortions"),
        *(
            (keyword, "no comment")
            for keyword in {
                "A_0_0",
                "A_0_1",
                "A_0_2",
                "A_1_0",
                "A_1_1",
                "A_2_0",
                "B_0_0",
                "B_0_1",
                "B_0_2",
                "B_1_0",
                "B_1_1",
                "B_2_0",
                "AP_0_0",
                "AP_0_1",
                "AP_0_2",
                "AP_1_0",
                "AP_1_1",
                "AP_2_0",
                "BP_0_0",
                "BP_0_1",
                "BP_0_2",
                "BP_1_0",
                "BP_1_1",
                "BP_2_0",
                "CD1_2",
                "CD2_1",
                "CD2_2",
            }
        ),
    }
)

_OBSERVATION_DIRECTORY = re.compile(r"observation_(?=\d{2,}$)0*[1-9]\d*")
_FITS_SUFFIXES = {".fit", ".fits"}


class HeaderReportError(FitsError):
    """The header report could not be generated safely."""


@dataclass(frozen=True)
class HeaderReportResult:
    """Result details safe to display outside the generated report."""

    output_path: Path
    hdu_count: int
    card_count: int
    withheld_count: int
    replacement_count: int
    unscrubbed: bool


def _is_safe(keyword: str) -> bool:
    return keyword in _SAFE or any(pattern.fullmatch(keyword) for pattern in _SAFE_PATTERNS)


def _safe_description(keyword: str, description: str) -> str:
    if not description:
        return ""
    if (keyword, description) in _SAFE_DESCRIPTIONS:
        return description
    return "WITHHELD"


def _replacement(value: object, keyword: str) -> object:
    if keyword in {"SITELAT", "SITELONG"}:
        return 0.0
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 0
    if isinstance(value, float):
        return 0.0
    return "REMOVED"


def _display(value: object) -> str:
    """Render one value on one line without allowing terminal-control text."""
    if isinstance(value, str):
        return repr(value)
    return str(value)


def _safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._ -]", "_", path.stem).strip(" .")
    return stem or "FITS"


def infer_header_report_path(input_path: str | Path, *, unscrubbed: bool = False) -> Path:
    """Infer the separate report hierarchy without creating it."""
    source = Path(input_path)
    owner = _archive_report_owner(source) or source.parent
    suffix = "_header_UNSCRUBBED.txt" if unscrubbed else "_header.txt"
    return owner / "pii-scrubbed" / f"{_safe_stem(source)}{suffix}"


def _archive_report_owner(source: Path) -> Path | None:
    """Return a safely recognised observation, or None for an ordinary FITS."""
    from seestar_toolkit.archive import (
        ArchiveInferenceError,
        ArchivePathSafetyError,
        infer_archived_light_destination,
    )

    try:
        observation = infer_archived_light_destination(source).observation_directory
    except ArchivePathSafetyError:
        raise
    except ArchiveInferenceError:
        pass
    else:
        _require_safe_report_destination(observation)
        return observation

    stacked = source.parent
    observation = stacked.parent
    if (
        source.suffix.lower() not in _FITS_SUFFIXES
        or stacked.name != "seestar_stacked"
        or _OBSERVATION_DIRECTORY.fullmatch(observation.name) is None
    ):
        return None
    if observation.is_symlink() and not observation.exists():
        raise ArchivePathSafetyError("Observation path is an unsafe symlink")
    if not observation.exists() or not observation.is_dir():
        return None
    if stacked.is_symlink() and not stacked.exists():
        raise ArchivePathSafetyError("Canonical stacked path is an unsafe symlink")
    if not stacked.exists() or not stacked.is_dir():
        return None
    if source.is_symlink() and not source.exists():
        raise ArchivePathSafetyError("Archived stacked FITS is an unsafe symlink")
    if not source.exists() or not source.is_file():
        return None

    try:
        observation_real = observation.resolve(strict=True)
        stacked_real = stacked.resolve(strict=True)
        source_real = source.resolve(strict=True)
        destination_real = (observation / "pii-scrubbed").resolve(strict=False)
    except OSError as error:
        raise ArchivePathSafetyError("Unable to validate archived stacked paths") from error
    for candidate, label in (
        (stacked_real, "stacked path"),
        (source_real, "archived stacked FITS"),
        (destination_real, "inferred destination"),
    ):
        try:
            relative = candidate.relative_to(observation_real)
        except ValueError as error:
            raise ArchivePathSafetyError(
                f"Resolved {label} escapes the recognised observation"
            ) from error
        if not relative.parts:
            raise ArchivePathSafetyError(
                f"Resolved {label} is not beneath the recognised observation"
            )
    return observation


def _require_safe_report_destination(observation: Path) -> None:
    from seestar_toolkit.archive import ArchivePathSafetyError

    try:
        observation_real = observation.resolve(strict=True)
        destination_real = (observation / "pii-scrubbed").resolve(strict=False)
        relative = destination_real.relative_to(observation_real)
    except (OSError, ValueError) as error:
        raise ArchivePathSafetyError(
            "Resolved inferred destination escapes the recognised observation"
        ) from error
    if not relative.parts:
        raise ArchivePathSafetyError(
            "Resolved inferred destination is not beneath the recognised observation"
        )


def _validate_paths(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise HeaderReportError("Input FITS is not a readable file")
    try:
        if source.resolve() == destination.resolve():
            raise HeaderReportError("Input and output must be different files")
    except OSError as error:
        raise HeaderReportError("Unable to validate input and output paths") from error
    if destination.exists():
        raise HeaderReportError("Output already exists; refusing to overwrite it")


def _report_text(source: Path, *, unscrubbed: bool) -> tuple[str, int, int, int, int]:
    sections: list[str] = []
    card_count = withheld_count = replacement_count = 0
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", AstropyWarning)
            with fits.open(
                source,
                mode="readonly",
                memmap=True,
                lazy_load_hdus=True,
                do_not_scale_image_data=True,
            ) as hdus:
                for hdu_index, hdu in enumerate(hdus):
                    lines = [f"--- HDU {hdu_index} ---"]
                    for card in hdu.header.cards:
                        card_count += 1
                        keyword = card.keyword
                        if unscrubbed:
                            value, comment = card.value, card.comment
                        elif keyword in {"COMMENT", "HISTORY", ""}:
                            value, comment = "WITHHELD", ""
                            withheld_count += 1
                        elif keyword in _SENSITIVE:
                            value = _replacement(card.value, keyword)
                            comment = _safe_description(keyword, card.comment)
                            replacement_count += 1
                            if comment == "WITHHELD":
                                withheld_count += 1
                        elif _is_safe(keyword):
                            value = card.value
                            comment = _safe_description(keyword, card.comment)
                            withheld_count += comment == "WITHHELD"
                        else:
                            value, comment = "WITHHELD", ""
                            withheld_count += 1
                            if card.comment:
                                comment = "WITHHELD"
                                withheld_count += 1
                        rendered = f"{keyword or '<BLANK>'} = {_display(value)}"
                        if comment:
                            rendered += f" / {_display(comment)}"
                        lines.append(rendered)
                    sections.append("\n".join(lines))
                hdu_count = len(hdus)
    except (OSError, ValueError, TypeError, VerifyError, AstropyWarning) as error:
        raise HeaderReportError("Unable to read FITS headers") from error

    mode = "ORIGINAL HEADER — UNSCRUBBED" if unscrubbed else "PRIVACY-PROCESSED"
    summary = [
        "Seestar Toolkit FITS Header Report",
        f"Mode: {mode}",
        f"HDUs: {hdu_count}",
        f"Header cards: {card_count}",
    ]
    if not unscrubbed:
        summary.extend(
            [
                f"Sensitive values replaced: {replacement_count}",
                f"Unknown values/comments withheld: {withheld_count}",
            ]
        )
    return (
        "\n".join((*summary, "", *sections, "")),
        hdu_count,
        card_count,
        withheld_count,
        replacement_count,
    )


def _publish_text(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(prefix=".header-report-", dir=destination.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)
    except FileExistsError as error:
        raise HeaderReportError("Output already exists; refusing to overwrite it") from error
    except OSError as error:
        raise HeaderReportError("Unable to write header report") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def generate_header_report(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    unscrubbed: bool = False,
) -> HeaderReportResult:
    """Read every FITS header and atomically publish one new text report."""
    source = Path(input_path)
    destination = (
        Path(output_path)
        if output_path is not None
        else _infer_safe_report_path(source, unscrubbed=unscrubbed)
    )
    _validate_paths(source, destination)
    content, hdus, cards, withheld, replacements = _report_text(source, unscrubbed=unscrubbed)
    _publish_text(destination, content)
    return HeaderReportResult(destination, hdus, cards, withheld, replacements, unscrubbed)


def _infer_safe_report_path(source: Path, *, unscrubbed: bool) -> Path:
    from seestar_toolkit.archive import ArchivePathSafetyError

    try:
        return infer_header_report_path(source, unscrubbed=unscrubbed)
    except ArchivePathSafetyError as error:
        raise HeaderReportError("Unsafe archive path; refusing report destination") from error


def offer_report_menu(path: Path) -> None:
    """Offer non-essential macOS conveniences after a report is safely published."""
    while True:
        answer = input("(V)iew / (F)inder / (Q)uit [Q]: ").strip().casefold()
        if answer in {"", "q", "quit"}:
            return
        if answer in {"v", "view"}:
            command = ["open", str(path)] if sys.platform == "darwin" else None
        elif answer in {"f", "finder"}:
            command = ["open", "-R", str(path)] if sys.platform == "darwin" else None
        else:
            print("Choose View, Finder or Quit")
            continue
        if command is None:
            print("Warning: this convenience is available only on macOS", file=sys.stderr)
            continue
        try:
            subprocess.run(command, check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            print("Warning: unable to open the generated report", file=sys.stderr)
