# Seestar Toolkit Architecture

## 1. Project Overview

The Seestar Toolkit is a modular command-line application for importing,
organising, inspecting and converting ZWO Seestar S50 datasets.

Its primary objectives are to:

- Preserve the original Seestar data.
- Create a structured archive of observing sessions.
- Prepare datasets for processing with software such as Siril and AstroPanel.
- Provide a solid foundation for future GUI and workflow automation.

## 2. Design Philosophy

- Never modify or delete original Seestar files.
- Preserve all available metadata.
- Automate repetitive tasks wherever possible.
- Keep modules independent and reusable.
- Maintain cross-platform compatibility.
- Support future expansion without breaking existing functionality.
- Keep each committed development stage in a passing, testable state.
- Archive directory hierarchy will be user-configurable, with
  `{target}/{location}/{session_end_date}` as the default layout. The
  preference will be shared by the CLI and any future UI.

## 3. High-Level Architecture

Importer
    │
    ▼
Session Organiser
    │
    ▼
FITS Inspector / Reader
    │
    ├── Raw Bayer Detection
    ├── RGB Detection
    ├── Metadata Extraction
    └── Image Classification
    │
    ▼
Image Processor
    │
    ▼
Output Writers
    │
    ▼
Export Profiles

## 4. Module Responsibilities

### Importer

Responsibilities:

- Discover supported Seestar material beneath one `My Works`-style input root.
- Use FITS inspection together with directory context and filename evidence to
  classify lights, Seestar stacks, full-size JPEGs, thumbnails and unknown
  files.
- Supply discovery evidence to later observation reconstruction.

Does not modify source files or perform image conversion.

Stage 7 source discovery is exposed independently of the CLI through
`discover_seestar_inputs(root)`. The `seestar_toolkit.archive` package returns
an immutable, deterministically path-ordered `SeestarDiscoveryInventory` of
typed `SeestarDiscoveryItem` records. It scans only files directly in the work
root and directly in its child directories. It does not reconstruct
observations.

Discovery classifications are `LIGHT_FITS`, `SEESTAR_STACK_FITS`,
`SEESTAR_JPEG`, `THUMBNAIL_JPEG` and `UNKNOWN`. FIT/FITS candidates reuse the
Stage 2 `inspect_fits()` and `FitsImageClass` boundary. Directory and filename
evidence supplements that inspection rather than replacing it. Each item keeps
its source-directory context, directory and FITS target evidence, complete
`FitsInspection` when available, and a visible problem description for
malformed or ambiguous candidates. One expected FITS failure does not discard
other discoveries.

The generic `_sub` suffix identifies sub-source directory context. For target
comparison only, discovery and archive planning share one rule that removes a
terminal, case-insensitive `_mosaic` suffix after existing `_sub` handling.
Thus `Target_mosaic` and `Target_mosaic_sub` compare as `Target` without
rewriting source paths, stored directory evidence or FITS `OBJECT`. Genuine
normalized mismatches remain diagnostic; ordinary non-structural mosaic text
is unchanged. This comparison does not select or rewrite archive targets.
Typed mosaic evidence and target correction/override remain deferred; mosaic
state is not inferred from image dimensions or WCS.

### Session Organiser

Responsibilities:

- Build the archive hierarchy according to the configured directory layout.
- Reconstruct observations from file and metadata evidence rather than treating
  one source directory as one observation.
- Resolve archive metadata and plan safe observation destinations.
- Preserve original lights and Seestar-generated stacks.
- Place Toolkit-generated TIFF derivatives beside their owning source class.
- Apply explicit copy/move, duplicate/collision and dry-run policies.
- Generate regenerable target-level indexes.

Does NOT modify FITS image data.

### FITS Inspector / Reader

Responsibilities:

- Read FITS headers and image data.
- Extract metadata and validate FITS files.
- Distinguish supported image layouts.
- Identify 2-dimensional raw Bayer images.
- Identify 3-dimensional channels-first RGB images.
- Preserve shape, dimensionality, width, height, data type and bit depth.
- Detect Bayer pattern from metadata.
- Classify image type.

Current supported layouts:

- `FitsImageLayout.RAW_BAYER` --- 2-dimensional image arrays.
- `FitsImageLayout.RGB` --- 3-dimensional `(3, height, width)` arrays.

Unsupported image layouts are rejected by the reader.

### Image Processor

Responsibilities:

- Bayer demosaicing.
- Normalize supported channels-first RGB data into `(height, width, 3)` RGB.
- Preserve RGB channel order, numerical values and source dtype precision.
- Future image processing operations.

### Output Writers

Responsibilities:

- TIFF output.
- FITS output.
- Future PNG/JPEG support.

The Image Processor hands Output Writers linear `(height, width, 3)` RGB data.
This boundary is structural rather than dtype-unifying: validated Seestar RGB
remains `uint16`, while validated Siril RGB remains `float32`. Output Writers
own format-specific sample types, numeric conversion and range policies,
clipping and non-finite-value policies, metadata, and file-writing behaviour.
Pixel processing at this boundary does not branch by producer or mosaic origin.

The FITS-to-TIFF conversion service composes these boundaries: raw Bayer FITS
use the existing demosaicing path, while already-RGB FITS use the existing RGB
layout-normalization path. Both produce linear channels-last RGB data for the
same TIFF writer. Output naming, CLI, batch and archive policies remain outside
this conversion service.

The public single-file pipeline boundary is
`convert_fits_to_tiff(input_path, output_path)`. It orchestrates exactly one
explicit FIT/FITS input and one explicit TIFF destination, returns the
successful destination as a `pathlib.Path`, rejects unsupported
classifications, and allows subsystem exceptions to remain visible. Stage 6
exposes this boundary through the single-file `convert INPUT_FITS OUTPUT_TIFF`
CLI. Its `convert-batch INPUT_DIR OUTPUT_DIR` command is a thin orchestration
layer over that same operation: it scans one directory non-recursively for
case-insensitive `.fit`/`.fits` extensions, processes filename-sorted inputs,
and maps each source stem to a `.tiff` in one explicit flat output directory.
Expected per-file failures are recorded while later inputs continue, and a
structured result supplies the CLI summary counts. Stage 7 owns recursive
archive scanning, archive paths, placement, hierarchy creation, and source-file
movement; Stage 8 owns broad real-dataset qualification.

### Export Profiles

Initially:

- Siril
- AstroPanel
- Generic

## 5. Archive Architecture

### Terminology and grouping

- A **session** is an observing night or period at one location and may contain
  multiple targets or multiple observations of the same target.
- An **observation** is one discrete capture/run of one target.
- A **light** is an individual source sub-exposure belonging to an observation.
- A **Seestar stack** is the stack generated by the Seestar for an observation,
  distinct from later Siril or other application products.
- `session_end_date` is the archive grouping date calculated as
  `date(capture_datetime + 12 hours)` and formatted `YYYYMMDD`. This grouping
  rule never changes source timestamps or image metadata.

The hierarchy is configuration-driven. Its default is:

```text
{target}/{location}/{session_end_date}
```

Alternative token ordering, including
`{location}/{session_end_date}/{target}`, uses the same configuration model
rather than a separate code path.

Every observation has an explicit numbered directory, starting with
`observation_01`; the first observation is never initially flattened and later
restructured. The canonical default structure is:

```text
ARCHIVE_ROOT/
└── {target}/
    ├── INDEX.md
    └── {location}/
        └── {session_end_date}/
            ├── observation_01/
            │   ├── lights/
            │   ├── seestar_stacked/
            │   └── tiff/
            └── observation_02/
                ├── lights/
                ├── seestar_stacked/
                └── tiff/
```

Original light FIT/FITS files are placed directly in `lights/`, without an
extra `source/` or `fits/` level, so the observation remains convenient for
Siril and similar stacking software. TIFF derivatives of individual lights go
in `tiff/`. The original Seestar stack and its `.tiff` derivative remain
together in `seestar_stacked/`. Original FITS basenames are preserved wherever
practical; derivatives replace `.fit` or `.fits` with `.tiff`.

Future sibling frame directories such as `darks/`, `flats/` and `biases/` are
permitted by the architecture, but unused directories and calibration-frame
ingestion are not part of Stage 7.1a.

### Observation reconstruction

A Seestar target directory and related `_sub` directory may contain several
observations, so source directories do not define observation boundaries. A
recognised Seestar stacked FITS is the primary end marker for one observation.
Compatible preceding, unassigned lights may be associated with that stack.
Any stack count in its filename is supporting validation evidence, never an
instruction to take exactly the preceding number of lights.
Retained source-light count need not equal the reported stack count or FITS
`STACKCNT`. When valid exposure metadata and a reported filename count are
available, reconstruction checks that count against `TOTALEXP / EXPTIME`;
it does not diagnose a difference from retained-light membership. Stage 8
validated 135 retained lights with `STACKCNT=106`, `TOTALEXP=3180` and
`EXPTIME=30` without changing source membership.

Logical reconstruction is exposed through
`reconstruct_seestar_observations(inventory)`. It consumes the existing
`SeestarDiscoveryInventory` directly and never rescans the filesystem. The
immutable result contains chronological `ReconstructedObservation` values with
`COMPLETE`, `LIGHTS_ONLY`, `STACK_ONLY`, `AMBIGUOUS` or `UNRESOLVED` status,
plus excluded JPEG/unknown discovery items. It assigns no archive observation
number or destination path.

For each FITS candidate, `FitsInspection.captured_at` is the preferred capture
time and `exposure_ended_at` is the FITS fallback. A Seestar filename timestamp
is used only when FITS time is unavailable and is otherwise retained as
fallback evidence. Filename local wall time without timezone provenance is
not directly compared with FITS time to generate offset-conflict diagnostics.
No timezone is inferred. A missing timestamp never drops the source item.
Selected timestamps are ordered chronologically, with lights considered before
stacks at an equal timestamp and root-relative path providing deterministic
ordering within that semantic priority. Compatibility checks still reject
incompatible equal-time lights, and genuinely later lights are not assigned
backward to an earlier stack.

Light-to-stack association requires explicit matching target, exposure and
filter evidence. Exposure comparison permits only a one-microsecond numeric
tolerance; known differing equatorial/capture modes are incompatible. A light
must precede its stack by no more than 12 hours. Missing core evidence,
conflicts or a wider gap prevent association and leave the light visible for
conservative fallback or unresolved reporting.

Lights without a usable stack require a later safe fallback based on temporal,
cadence and compatible metadata evidence. Ambiguous non-interactive grouping
must be reported rather than guessed.

The implemented non-interactive fallback groups fully compatible timed lights
only when consecutive gaps do not exceed the greater of 60 seconds or five
exposure durations. Larger gaps remain one explicit `AMBIGUOUS` result rather
than being silently split. Missing timestamps or core compatibility evidence
produce `UNRESOLVED` results. A stack without compatible preceding lights
remains a distinct `STACK_ONLY` result.

#### Intentional observation merging

Users may intentionally merge compatible consecutive captures by making all
but the final stack ineligible for discovery. Multiple eligible stacks create
multiple boundaries; one final eligible stack may close one combined group of
compatible preceding lights. Moving intermediate stacks outside the input root,
using a deliberately unsupported extension, or a future explicit exclusion
mechanism is more reliable than assuming a rename hides a classifiable stack.
This affects grouping only and never combines or changes source image data.

The discovery inventory deliberately contains no observation number, associated
stack, session end date or grouping result. These decisions begin in Stage
7.1c. Reconstruction adds logical association only; final `observation_01`
naming, `session_end_date`, location and archive path planning remain Stage
7.1d.

### Archive metadata and destination planning

`plan_seestar_archive(reconstruction, ...)` consumes the immutable Stage 7.1c
result directly. It does not discover files or reconstruct observations. The
planner returns immutable metadata and destination models only; it performs no
filesystem operations and does not call TIFF conversion.

The planner uses first-light capture time where available, or stack time for a
stack-only observation, and applies `date(capture_datetime + 12 hours)` to form
the `YYYYMMDD` session token. Ambiguous or unresolved reconstruction results,
and observations without safe time evidence, remain explicit planning problems
rather than receiving authoritative destinations.

Target resolution prefers retained FITS metadata, then reconstructed target
evidence, then directory context, with `unknown` as the explicit final fallback.
Conflicting evidence remains diagnostic. Exact source target, GPS and telescope
metadata is retained separately from logical and path-normalized values.

The default hierarchy template is `{target}/{location}/{session_end_date}` and
the same model supports alternative ordering of those three tokens. Archive
roots must be absolute. Templates and normalized components cannot introduce
absolute paths or traversal. Component normalization trims outer whitespace,
collapses repeated whitespace, preserves ordinary spaces and case, replaces
unsafe filesystem characters and path separators with `-`, and maps empty,
`.` or `..` values to `unknown`.

Non-interactive location resolution uses an explicit logical name first, then
the nearest saved GPS location within its inclusive radius, otherwise
`unknown`. Saved coordinates and radii are validated, exact capture coordinates
remain available, and planning has no network or reverse-geocoder dependency.

Within each target/location/session group, observations are sorted by retained
capture time and deterministic source-path evidence and numbered from
`observation_01`. Width expands above 99 observations to prevent ambiguity.
Planned original lights retain their filenames under `lights/`; their `.tiff`
derivatives are planned under `tiff/`. A Seestar stack and its `.tiff`
derivative are both planned under `seestar_stacked/`. In-memory destination
collisions between distinct sources are rejected; filesystem collision and
content policy remains Stage 7.1e.

### Safe archive file execution

`execute_archive_plan(plan, ...)` consumes the Stage 7.1d `ArchivePlan`
directly and executes only each `PlannedFile.fits_destination`. It does not
rediscover inputs, reconstruct observations, recalculate placement, or execute
the separately planned TIFF destinations.

`SourceAction.COPY` is the default. `SourceAction.MOVE` must be selected
explicitly and uses copy-verify-delete semantics so the source is removed only
after its destination has been established. If source deletion then fails, the
destination remains valid and the result explicitly reports partial completion.
Independent file failures do not discard earlier results or prevent later
operations from being attempted.

Writes are staged in a uniquely named temporary file beside the destination,
flushed, synchronized and verified with streamed whole-file SHA-256 before an
atomic replacement. Expected failures clean the staged file. Explicit
`CollisionPolicy.OVERWRITE` can replace different destination content using
this staging path; a failed atomic replacement preserves the previous file.

The default `CollisionPolicy.SKIP_IDENTICAL` skips byte-identical existing
destinations and fails safely on different content. `CollisionPolicy.ERROR`
reports every existing destination as a collision, while `OVERWRITE` remains
explicit. Identical MOVE collisions retain the source rather than interpreting
a stale destination as permission to delete it. Filename, size and mtime alone
are never treated as content identity.

Execution revalidates absolute-root containment using resolved paths after
directory creation, rejecting traversal, same-file/hardlink confusion,
non-regular sources, non-directory parents and destination symlink escapes.
Only required FITS parent directories are created. No TIFF conversion,
compression, JPEG operation, index generation, network call, prompting or CLI
behavior belongs to this layer.

### Integrated Seestar archive orchestration

`archive_seestar_session(source_root, ...)` is the library-level composition
boundary for Stage 7. It calls, in order, `discover_seestar_inputs()`,
`reconstruct_seestar_observations()`, `plan_seestar_archive()` and
`execute_archive_plan()`, then delegates eligible derivative creation to the
existing `convert_fits_to_tiff()` pipeline. It retains every intermediate
result for later presentation and does not duplicate FITS inspection,
demosaicing, RGB normalization, TIFF writing, reconstruction, placement or
original-file safety logic.

TIFF conversion occurs only after the corresponding original archive result is
`COPIED`, `MOVED` or `SKIPPED_IDENTICAL`. `COLLISION`, `FAILED` and `PARTIAL`
original outcomes are conservatively ineligible. The archived FITS destination
is always the conversion input, allowing TIFF creation after MOVE and ensuring
an identical archived FITS can produce a missing derivative. The TIFF output
is exactly the destination retained in its Stage 7.1d `PlannedFile`.

Eligible TIFF parent directories are created only after resolved-path archive
containment is revalidated. A pre-existing TIFF is preserved and reported as a
collision; conversion retains the TIFF writer's exclusive-create behavior.
FITS/TIFF conversion failures are reported per derivative and do not roll back
or restore successfully archived originals. Independent eligible conversions
continue after expected failures.

The immutable `SeestarArchiveResult` exposes discovery, reconstruction, plan,
original execution, per-TIFF results and derived index results. Aggregate
status is `COMPLETE` only when there are no planning, original-operation,
supported-FITS discovery, TIFF or index problems; mixed useful progress and
problems is `PARTIAL`; a workflow with problems and no usable archived result
is `FAILED`. A genuinely empty input is a deterministic no-op `COMPLETE`
result and creates no archive root.

The library orchestration performs no JPEG action, compression, reverse
geocoding, network operation or prompting. The CLI adds configuration,
interaction and dry-run presentation around the same preparation/execution
boundaries; real execution generates derived indexes after FITS/TIFF work.

### Path and safety policy

Metadata-derived target and logical-location components are trimmed, repeated
whitespace is collapsed, and ordinary single spaces and case are preserved.
Path separators and unsafe characters are replaced with `-`; empty, `.` and
`..` components become the explicit safe value `unknown`. Absolute templates,
relative archive roots and traversal outside the archive root are rejected.

The safe default source action is `copy`. `move` is explicit and removes a
source only after successful, validated destination creation.
Uncompressed originals remain the baseline; future compression policy may be
added only after representative measurements and workflow review.

Identical destination content is determined with streamed whole-file SHA-256.
Skip-identical is the safe default, error and overwrite policies are explicit,
and the same filename with different content is never silently overwritten.

Dry-run follows the same discovery, classification, reconstruction, metadata,
path, collision, TIFF-placement and file-action planning path as a real run,
but performs zero filesystem mutation and generates no archive TIFF or index.

### Ancillary products and indexes

Seestar full-size JPEG and `*_thn.jpg` thumbnail classifications remain
distinct. Stage 7 leaves both JPEG classes untouched under the implemented
safe ignore behaviour. Future JPEG-management policy may introduce explicit
keep or destructive discard choices, but those operations are not implemented
in Stage 7.

Each concrete target directory has a regenerable `INDEX.md` derived from the
archived FITS content and current structured execution results. Placement is
calculated from the `{target}` position in the configured hierarchy rather
than assuming `archive_root/target`. Existing indexes are never parsed as
archive metadata. Historical observations are reconstructed, when necessary,
with the established FITS inspector so incremental runs retain older entries.

The deterministic index records location, session, planned observation number,
capture range, exposure, filter, safely established light count, safely
established stack and its distinct reported count, capture mode, GPS, and the
actual telescope identifier such as `S50_99643794`. Writes use a same-directory
temporary file and atomic replacement. Index failure is reported independently
and makes an otherwise successful archive partial without rolling back FITS or
TIFF output.

Archive preparation reconciles planned observation numbers with already
established numbered directories for incremental invocations. Matching
archived filenames retain their existing observation number so reruns and
collisions remain stable; a new source set for the same concrete
target/location/session is assigned after existing observation directories
that contain archived FITS. This is a read-only adjustment before execution
and does not change the standalone Stage 7.1d planner contract.

## 6. Processing Workspace

The toolkit may generate temporary workspaces for software that expects
a conventional folder structure such as `lights/` and `darks/`. The
archive remains untouched.

## 7. Archive Metadata Model

Archive planning will use source-format-neutral metadata where practical,
including source path, target, logical location, precise capture coordinates,
capture datetime, session end date, observation, frame type, source format,
telescope identifier and derived files. A Seestar-specific discovery layer
obtains these values from FITS metadata, directory context and filename
evidence. This separation leaves room for a future DSLR/EXIF adapter without
implementing DSLR ingestion in Stage 7.

The FITS subsystem currently normalises core inspection metadata
including exposure, gain, Bayer pattern, object, filter, telescope,
instrument and capture time.

## 8. Configuration and Location Resolution

Stage 7 configuration is human-readable and reusable by the CLI and a future
UI. TOML is the implemented configuration format. It currently covers the
archive hierarchy template, saved locations, source action and collision
policy. The archive root is supplied explicitly to the archive command.
JPEG-management configuration, reverse geocoding, configuration persistence
and source-storage/compression policy remain deferred.

Implemented logical location resolution uses this precedence:

1. explicit CLI/user location;
2. nearest configured location whose radius contains the capture coordinates;
3. interactive manual handling where applicable;
4. `unknown`.

Saved locations contain a logical name, latitude, longitude and matching
radius. If radii overlap, geographical distance decides and the nearest match
wins, never configuration file order. Non-interactive operation never waits
for input and falls back safely when no saved location matches. Precise
captured coordinates remain separate from the logical location label. No
network or reverse-geocoding service is implemented in Stage 7; such a service
may be considered as a future extension.

## 9. Error Handling

The toolkit should detect and report:

- Corrupt or unreadable FITS files.
- FITS files containing no supported image data.
- Missing metadata.
- Duplicate imports.
- Unknown Bayer patterns.
- Mixed sessions.
- Missing reference folders.

## 10. Future Enhancements

- Desktop GUI
- macOS application bundle
- Windows installer
- Linux package
- PixInsight export profile
- Additional image formats
- Plugin architecture

## 11. Development Notes

Implementation progress and roadmap are maintained in
`PROJECT_Notes.md`.

Observed Seestar FITS structures and headers are maintained in
`SEESTAR_FITS_REFERENCE.md`.

Individual implementation instructions are maintained in
`change_documents/`.

This document describes the target architecture while recording
important implemented architectural behaviour.

## 12. Archive CLI and Configuration

Stage 7.1g exposes `archive SOURCE_ROOT ARCHIVE_ROOT` as a thin CLI adapter.
The CLI loads optional TOML configuration, then calls the shared archive
preparation path for discovery, reconstruction, location resolution and
planning. Real execution consumes that prepared result through the Stage
7.1e/7.1f execution and TIFF orchestration APIs; dry-run renders it and stops.
There is no duplicate FITS parser, observation reconstructor, path planner,
collision implementation, or TIFF converter in the CLI.

The default read-only configuration path is
`~/.config/seestar-toolkit/config.toml`. CLI values override configuration,
which overrides the safe built-in COPY, `skip-identical`, and
`{target}/{location}/{session_end_date}` defaults. Saved GPS locations use the
existing `SavedLocation` model. No network geocoder or configuration writer is
present. The existing `convert-batch` command remains flat and non-recursive.
