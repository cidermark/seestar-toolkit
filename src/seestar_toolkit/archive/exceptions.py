"""Exceptions raised by archive discovery, planning and execution."""


class ArchiveDiscoveryError(Exception):
    """Raised when a discovery request cannot inspect its input root."""


class ArchivePlanningError(Exception):
    """Base exception for invalid archive-planning requests."""


class ArchivePlanningConfigurationError(ArchivePlanningError):
    """Raised when archive-planning configuration is invalid or unsafe."""


class ArchivePlanningCollisionError(ArchivePlanningError):
    """Raised when distinct sources map to one in-memory destination."""


class ArchiveExecutionError(Exception):
    """Raised when an archive execution request itself is invalid."""


class ArchiveConfigError(Exception):
    """Raised when archive TOML configuration cannot be loaded safely."""


class ArchiveInferenceError(Exception):
    """Raised when a path is not a recognised current archive input."""


class ArchiveCanonicalLightsMissingError(ArchiveInferenceError):
    """Raised when a recognised observation lacks its canonical lights directory."""


class ArchivePathSafetyError(ArchiveInferenceError):
    """Raised when symbolic-link resolution escapes a recognised observation."""
