"""Archive discovery contracts for Seestar source material."""

from .config import (
    DEFAULT_HIERARCHY,
    DEFAULT_OBSERVATION_DATE_POLICY,
    ArchiveConfig,
    default_archive_config_path,
    load_archive_config,
)
from .discovery import discover_seestar_inputs
from .exceptions import (
    ArchiveCanonicalLightsMissingError,
    ArchiveConfigError,
    ArchiveDiscoveryError,
    ArchiveExecutionError,
    ArchiveInferenceError,
    ArchivePathSafetyError,
    ArchivePlanningCollisionError,
    ArchivePlanningConfigurationError,
    ArchivePlanningError,
)
from .execution import execute_archive_plan, sha256_file
from .execution_models import (
    ArchiveCollisionState,
    ArchiveExecutionResult,
    ArchiveExecutionStatus,
    ArchiveFileExecutionResult,
    ArchiveFileOutcome,
    CollisionPolicy,
    SourceAction,
)
from .index_models import ArchiveIndexOutcome, ArchiveIndexResult
from .indexing import generate_archive_indexes, planned_index_paths
from .light_tiff import (
    LightTiffCollisionDecider,
    LightTiffCollisionDecision,
    LightTiffOutcome,
    LightTiffResult,
    finalise_archived_light_tiff,
    is_light_tiff_eligible,
)
from .models import (
    DiscoveryClassification,
    SeestarDiscoveryInventory,
    SeestarDiscoveryItem,
    SourceDirectoryContext,
)
from .orchestration import (
    archive_seestar_session,
    execute_prepared_seestar_archive,
    light_tiff_dry_run_counts,
    prepare_seestar_archive,
)
from .orchestration_models import (
    ArchiveTiffOutcome,
    ArchiveTiffResult,
    PreparedSeestarArchive,
    SeestarArchiveResult,
    SeestarArchiveStatus,
)
from .planning import normalize_archive_component, plan_seestar_archive, session_end_date
from .planning_models import (
    ArchivePlan,
    ArchivePlanningConfig,
    ArchivePlanningProblem,
    ObservationArchiveMetadata,
    PlannedArchiveObservation,
    PlannedFile,
    SavedLocation,
)
from .recognition import (
    ArchiveBatchInference,
    ArchivedLightInference,
    infer_archived_light_destination,
    resolve_archive_batch_input,
)
from .reconstruction import reconstruct_seestar_observations
from .reconstruction_models import (
    ObservationCompatibility,
    ObservationReconstructionResult,
    ObservationStatus,
    ReconstructedObservation,
    TimestampEvidence,
)

__all__ = [
    "ArchiveDiscoveryError",
    "ArchiveCanonicalLightsMissingError",
    "ArchiveConfig",
    "ArchiveConfigError",
    "ArchiveCollisionState",
    "ArchiveExecutionError",
    "ArchiveExecutionResult",
    "ArchiveExecutionStatus",
    "ArchiveInferenceError",
    "ArchivePathSafetyError",
    "ArchiveBatchInference",
    "ArchivedLightInference",
    "ArchiveIndexOutcome",
    "ArchiveIndexResult",
    "ArchiveFileExecutionResult",
    "ArchiveFileOutcome",
    "ArchivePlan",
    "ArchivePlanningCollisionError",
    "ArchivePlanningConfig",
    "ArchivePlanningConfigurationError",
    "ArchivePlanningError",
    "ArchivePlanningProblem",
    "ArchiveTiffOutcome",
    "ArchiveTiffResult",
    "LightTiffCollisionDecision",
    "LightTiffCollisionDecider",
    "LightTiffOutcome",
    "LightTiffResult",
    "DiscoveryClassification",
    "CollisionPolicy",
    "DEFAULT_HIERARCHY",
    "DEFAULT_OBSERVATION_DATE_POLICY",
    "SeestarDiscoveryInventory",
    "SeestarDiscoveryItem",
    "SourceDirectoryContext",
    "ObservationCompatibility",
    "ObservationArchiveMetadata",
    "ObservationReconstructionResult",
    "ObservationStatus",
    "ReconstructedObservation",
    "PlannedArchiveObservation",
    "PlannedFile",
    "PreparedSeestarArchive",
    "SavedLocation",
    "SeestarArchiveResult",
    "SeestarArchiveStatus",
    "SourceAction",
    "TimestampEvidence",
    "archive_seestar_session",
    "discover_seestar_inputs",
    "default_archive_config_path",
    "execute_archive_plan",
    "execute_prepared_seestar_archive",
    "light_tiff_dry_run_counts",
    "load_archive_config",
    "generate_archive_indexes",
    "finalise_archived_light_tiff",
    "is_light_tiff_eligible",
    "infer_archived_light_destination",
    "normalize_archive_component",
    "plan_seestar_archive",
    "planned_index_paths",
    "prepare_seestar_archive",
    "reconstruct_seestar_observations",
    "resolve_archive_batch_input",
    "session_end_date",
    "sha256_file",
]
