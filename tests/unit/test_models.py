"""Tests for the Stage 2 FITS inspection data models."""

from datetime import UTC, datetime
from pathlib import Path

from seestar_toolkit.models import (
    CaptureType,
    ColourMode,
    DetectionSource,
    FitsInfo,
    FrameType,
    ImageClassification,
    LocationInfo,
    ValidationSeverity,
)


def test_fits_info_minimum_construction() -> None:
    info = FitsInfo(
        path=Path("/tmp/example.fit"),
        filename="example.fit",
    )

    assert info.filename == "example.fit"
    assert info.classification.frame_type is FrameType.UNKNOWN
    assert info.location.latitude is None
    assert info.messages == []


def test_location_information() -> None:
    location = LocationInfo(
        latitude=51.4281,
        longitude=-0.7532,
        raw_latitude="51.4281",
        raw_longitude="-0.7532",
        is_valid=True,
    )

    assert location.latitude == 51.4281
    assert location.longitude == -0.7532
    assert location.is_valid is True


def test_image_classification() -> None:
    classification = ImageClassification(
        frame_type=FrameType.LIGHT,
        capture_type=CaptureType.MOSAIC_SUB,
        colour_mode=ColourMode.BAYER,
        frame_type_source=DetectionSource.HEADER,
        capture_type_source=DetectionSource.FILENAME,
        colour_mode_source=DetectionSource.HEADER,
    )

    assert classification.frame_type is FrameType.LIGHT
    assert classification.capture_type is CaptureType.MOSAIC_SUB
    assert classification.colour_mode is ColourMode.BAYER


def test_validation_messages() -> None:
    info = FitsInfo(
        path=Path("/tmp/example.fit"),
        filename="example.fit",
    )

    info.add_message(
        "missing-object",
        "The FITS header does not contain an OBJECT keyword.",
        field_name="object_name",
    )

    assert info.has_warnings is True
    assert info.has_errors is False
    assert len(info.messages) == 1
    assert info.messages[0].code == "missing-object"


def test_error_detection() -> None:
    info = FitsInfo(
        path=Path("/tmp/example.fit"),
        filename="example.fit",
    )

    info.add_message(
        "invalid-image",
        "The FITS file does not contain image data.",
        severity=ValidationSeverity.ERROR,
    )

    assert info.has_errors is True


def test_json_friendly_dictionary() -> None:
    info = FitsInfo(
        path=Path("/tmp/example.fit"),
        filename="example.fit",
        dimensions=(1920, 1080),
        width=1080,
        height=1920,
        observation_date=datetime(
            2026,
            7,
            3,
            21,
            41,
            45,
            tzinfo=UTC,
        ),
        location=LocationInfo(
            latitude=51.4281,
            longitude=-0.753316,
            is_valid=True,
        ),
        classification=ImageClassification(
            frame_type=FrameType.LIGHT,
            capture_type=CaptureType.MOSAIC_SUB,
            colour_mode=ColourMode.BAYER,
        ),
        raw_header={"OBJECT": "NGC 7000"},
    )

    result = info.to_dict()

    assert result["path"] == "/tmp/example.fit"
    assert result["dimensions"] == [1920, 1080]
    assert result["observation_date"] == "2026-07-03T21:41:45+00:00"
    assert result["classification"]["frame_type"] == "light"
    assert "raw_header" not in result

    result_with_header = info.to_dict(include_raw_header=True)

    assert result_with_header["raw_header"]["OBJECT"] == "NGC 7000"
