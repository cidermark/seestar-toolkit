"""FITS inspection subsystem."""

from __future__ import annotations

from .exceptions import (
    FitsError,
    InvalidFitsFileError,
    MissingImageDataError,
)
from .header_report import (
    HeaderReportError,
    HeaderReportResult,
    generate_header_report,
    infer_header_report_path,
    offer_report_menu,
)
from .inspector import inspect_fits
from .models import FitsImageClass, FitsImageData, FitsImageLayout, FitsInspection
from .pii_scrub import (
    PiiScrubCancelled,
    PiiScrubError,
    PiiScrubResult,
    infer_pii_scrub_path,
    safe_terminal_value,
    scrub_fits,
)
from .privacy_processing import (
    FitsHduStructure,
    FitsProcessingError,
    FitsStructure,
    FitsTransformResult,
    UnknownMetadataAction,
    UnknownMetadataOccurrence,
    inspect_fits_structure,
    transform_fits,
    validate_transformed_fits,
)
from .privacy_verification import (
    FitsVerificationError,
    FitsVerificationResult,
    PrivacyVerificationStatus,
    verify_fits_privacy,
)
from .reader import read_fits_image

__all__ = [
    "FitsError",
    "FitsImageData",
    "FitsHduStructure",
    "FitsInspection",
    "FitsProcessingError",
    "FitsStructure",
    "FitsTransformResult",
    "InvalidFitsFileError",
    "MissingImageDataError",
    "HeaderReportError",
    "HeaderReportResult",
    "generate_header_report",
    "infer_header_report_path",
    "offer_report_menu",
    "inspect_fits",
    "inspect_fits_structure",
    "read_fits_image",
    "transform_fits",
    "validate_transformed_fits",
    "UnknownMetadataAction",
    "UnknownMetadataOccurrence",
    "FitsImageLayout",
    "FitsImageClass",
    "PiiScrubCancelled",
    "PiiScrubError",
    "PiiScrubResult",
    "infer_pii_scrub_path",
    "safe_terminal_value",
    "scrub_fits",
    "FitsVerificationError",
    "FitsVerificationResult",
    "PrivacyVerificationStatus",
    "verify_fits_privacy",
]
