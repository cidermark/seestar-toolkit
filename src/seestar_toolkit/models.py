"""Core data models used by the Seestar FITS inspector."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


class FrameType(StrEnum):
    """The calibration or image-frame type."""

    LIGHT = "light"
    DARK = "dark"
    FLAT = "flat"
    BIAS = "bias"
    UNKNOWN = "unknown"


class CaptureType(StrEnum):
    """How the image was captured or produced."""

    NORMAL_SUB = "normal_sub"
    MOSAIC_SUB = "mosaic_sub"
    STACKED = "stacked"
    UNKNOWN = "unknown"


class ColourMode(StrEnum):
    """The colour representation of the image data."""

    BAYER = "bayer"
    RGB = "rgb"
    MONO = "mono"
    UNKNOWN = "unknown"


class DetectionSource(StrEnum):
    """The evidence used to determine a classification."""

    HEADER = "header"
    FILENAME = "filename"
    IMAGE_DATA = "image_data"
    COMBINED = "combined"
    UNKNOWN = "unknown"


class ValidationSeverity(StrEnum):
    """Severity of a validation message."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True)
class ValidationMessage:
    """A non-fatal information, warning, or error message."""

    code: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.WARNING
    field_name: str | None = None


@dataclass(slots=True)
class LocationInfo:
    """Capture-location metadata extracted from a FITS header."""

    latitude: float | None = None
    longitude: float | None = None
    elevation_metres: float | None = None

    # Original values are retained in case a future FITS file uses
    # an unexpected coordinate representation.
    raw_latitude: Any | None = None
    raw_longitude: Any | None = None
    raw_elevation: Any | None = None

    is_valid: bool | None = None


@dataclass(slots=True)
class ImageClassification:
    """Classification assigned to an inspected image."""

    frame_type: FrameType = FrameType.UNKNOWN
    capture_type: CaptureType = CaptureType.UNKNOWN
    colour_mode: ColourMode = ColourMode.UNKNOWN

    frame_type_source: DetectionSource = DetectionSource.UNKNOWN
    capture_type_source: DetectionSource = DetectionSource.UNKNOWN
    colour_mode_source: DetectionSource = DetectionSource.UNKNOWN


@dataclass(slots=True)
class FitsInfo:
    """Normalised metadata and image properties from one FITS file."""

    # File identity
    path: Path
    filename: str
    file_size_bytes: int | None = None

    # FITS structure
    hdu_count: int = 0
    primary_hdu_type: str | None = None
    dimensions: tuple[int, ...] | None = None
    width: int | None = None
    height: int | None = None
    data_type: str | None = None
    bit_depth: int | None = None

    # Capture metadata
    object_name: str | None = None
    exposure_seconds: float | None = None
    total_exposure_seconds: float | None = None
    gain: float | None = None
    filter_name: str | None = None
    sensor_temperature_c: float | None = None
    focus_position: int | None = None

    # Dates
    observation_date: datetime | None = None
    exposure_end_date: datetime | None = None

    # Optics and sensor
    focal_length_mm: float | None = None
    aperture: float | None = None
    pixel_size_x_um: float | None = None
    pixel_size_y_um: float | None = None
    binning_x: int | None = None
    binning_y: int | None = None
    bayer_pattern: str | None = None

    # Telescope/software identity
    creator: str | None = None
    producer: str | None = None
    instrument: str | None = None
    telescope: str | None = None
    program_version: str | None = None
    firmware_version: str | None = None

    # Telescope state
    equatorial_mode: bool | None = None
    wide_camera: bool | None = None
    bias_level: float | None = None

    # Sky coordinates, expressed in decimal degrees
    right_ascension_deg: float | None = None
    declination_deg: float | None = None

    # Normalised subordinate models
    location: LocationInfo = field(default_factory=LocationInfo)
    classification: ImageClassification = field(
        default_factory=ImageClassification
    )
    messages: list[ValidationMessage] = field(default_factory=list)

    # Complete original header, retained for diagnostics and future support.
    raw_header: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def has_errors(self) -> bool:
        """Return True when inspection produced at least one error."""

        return any(
            item.severity is ValidationSeverity.ERROR
            for item in self.messages
        )

    @property
    def has_warnings(self) -> bool:
        """Return True when inspection produced at least one warning."""

        return any(
            item.severity is ValidationSeverity.WARNING
            for item in self.messages
        )

    def add_message(
        self,
        code: str,
        message: str,
        *,
        severity: ValidationSeverity = ValidationSeverity.WARNING,
        field_name: str | None = None,
    ) -> None:
        """Add a validation message to the inspection result."""

        self.messages.append(
            ValidationMessage(
                code=code,
                message=message,
                severity=severity,
                field_name=field_name,
            )
        )

    def to_dict(self, *, include_raw_header: bool = False) -> dict[str, Any]:
        """Return a JSON-friendly dictionary representation."""

        result = asdict(self)

        if not include_raw_header:
            result.pop("raw_header", None)

        return _make_json_friendly(result)


def _make_json_friendly(value: Any) -> Any:
    """Recursively convert model values into JSON-compatible values."""

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, StrEnum):
        return value.value

    if isinstance(value, tuple):
        return [_make_json_friendly(item) for item in value]

    if isinstance(value, list):
        return [_make_json_friendly(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): _make_json_friendly(item)
            for key, item in value.items()
        }

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Some FITS-header values may be NumPy or Astropy scalar types.
    # Preserve them in diagnostic output using their string form.
    return str(value)
