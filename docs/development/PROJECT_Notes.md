# Seestar Toolkit Project Notes

## Purpose

Convert and process ZWO Seestar S50 FIT/FITS files while building a
reusable foundation for later importing, organisation and export
workflows.

## Current Version

v1.1.0 (Development)

## Roadmap

-   [x] Stage 1 --- Project structure and foundations --- **Complete**
-   [x] Stage 2 --- FITS inspection and classification --- **Complete**
-   [x] Stage 3 --- Bayer demosaicing --- **Complete**
-   [x] Stage 4 --- RGB FITS processing/handling --- **Complete**
-   [x] Stage 5 --- TIFF writer --- **Complete**
-   [x] Stage 6 --- Command-line polish and batch processing --- **Complete**
-   [x] Stage 7 --- Archive organisation and file management --- **Complete**
-   [x] Stage 8 --- Testing with real Seestar datasets --- **Complete**
-   [ ] Stage 9 --- Packaging, documentation and release

> Stage 2 now includes reader-level recognition of RGB FITS images.
> Stage 4 provides handling for already-RGB FITS beyond basic reader-level
> layout detection.

## Completed Work

### Stage 1

-   Project structure established.
-   Python 3.13 development environment established.
-   Editable package installation working.
-   pytest and Ruff configured.
-   Git repository established.
-   CLI package foundation working.

### Stage 2 --- FITS inspection and classification.

-   FITS subsystem foundation added.
-   FITS image reader implemented.
-   FITS metadata inspection implemented.
-   Developer FITS inspection utilities added.
-   Real Seestar FITS layouts investigated and documented.
-   `FitsImageLayout` introduced.
-   `FitsImageData` extended with layout, shape and dimensionality.
-   2-dimensional FITS arrays recognised as raw Bayer images.
-   3-dimensional `(3, height, width)` FITS arrays recognised as RGB
    images.
-   Unsupported image layouts rejected.
-   Existing raw Bayer reader behaviour preserved.
-   Stage 2.2b.2 completed with Ruff clean and all tests passing.

### Stage 3.1a --- Bayer demosaicing foundation

-   Added the `seestar_toolkit.imaging` package.
-   Added the public `demosaic(image, bayer_pattern)` interface.
-   Added support for `RGGB`, `GRBG`, `GBRG` and `BGGR` Bayer patterns.
-   Added validation for unsupported Bayer patterns and non-2-dimensional input.
-   Established `(height, width, 3)` RGB output and `uint16` preservation.
-   Added a temporary channel-replication placeholder pending real interpolation.
-   Added 8 unit tests for the Stage 3.1a contract.
-   Stage 3.1a completed with 40 tests passing and Ruff clean.

### Stage 3.1b --- Genuine Bayer interpolation

-   Replaced the Stage 3.1a placeholder with genuine OpenCV Bayer interpolation.
-   Preserved the public `demosaic(image, bayer_pattern)` interface.
-   Verified `RGGB`, `GRBG`, `GBRG` and `BGGR` conversion mappings using
    deterministic synthetic Bayer data.
-   Verified RGB channel ordering and protected against accidental RGB/BGR
    reversal.
-   Preserved `(height, width, 3)` RGB output and `uint16` image data.
-   Preserved existing input validation.
-   Confirmed OpenCV is already declared as a project dependency.
-   Stage 3.1b completed with 44 tests passing and Ruff clean.

### Stage 3.1c --- Real Seestar FITS integration

-   Integrated the existing FITS reading and metadata-inspection path with
    the demosaicing layer using a real Seestar raw Bayer FITS fixture.
-   Confirmed raw Bayer layout and `RAW_LIGHT` classification through the
    existing FITS APIs.
-   Confirmed the `GRBG` Bayer pattern is obtained from FITS metadata and
    supplied directly to `demosaic(image, bayer_pattern)`.
-   Verified `(height, width, 3)` RGB output and `uint16` preservation.
-   Verified the source FITS fixture remains unmodified.
-   No production-code changes or additional integration abstraction were
    required.
-   Stage 3.1c completed with 45 tests passing and Ruff clean.

## Repository Refactoring

-   Moved project to repository root.
-   Moved documentation into `docs/`.
-   Added `docs/change_documents/` for stage implementation documents.
-   Reorganised unit test structure.
-   Added integration test scaffold.
-   Added developer tools under `tools/`.

## Stage 3 Summary

### Stage 3 --- Bayer demosaicing

Stage 3 implements conversion of raw 2-dimensional Bayer image data into
linear RGB image data.

The demosaicing layer operates independently of FITS parsing. It
receives image data and the Bayer pattern already identified by the FITS
inspection layer.

Requirements:

-   Input is a 2-dimensional NumPy Bayer image array.
-   Bayer pattern is supplied explicitly to the demosaicing layer.
-   Support the standard Bayer patterns `RGGB`, `GRBG`, `GBRG` and `BGGR`.
-   Seestar S50 raw FITS data currently observed uses `GRBG`.
-   Output is a 3-dimensional RGB array in `(height, width, 3)` form.
-   Preserve linear 16-bit image data and `uint16` output.
-   Keep image-processing behaviour separate from FITS parsing.

Stage 3 does not perform:

-   Image stretching.
-   Gamma correction.
-   White balance.
-   Colour enhancement.
-   TIFF output.

Stages 3.1a, 3.1b, 3.1c and 3.1d are complete. The image-processing package and
public `demosaic(image, bayer_pattern)` interface are established, genuine
OpenCV Bayer-to-RGB interpolation is implemented and tested for all four
supported Bayer patterns, and the real Seestar raw FITS-to-RGB integration
path has been validated.

Reconnaissance of six independent mosaic-session raw FITS files found that all
six are 2-dimensional `uint16` raw Bayer images using the normalized `GRBG`
pattern. All six demosaic successfully through the existing FITS inspection
and imaging APIs without mosaic-specific processing.

The reconnaissance also established that these known mosaic-session raw FITS
files do not contain a `MOSAIC` keyword. Mosaic-session origin therefore must
not be inferred or validated from a `MOSAIC` header field.

Stage 3.1d uses a small representative subset of the reconnaissance files
covering materially different header variants:

-   `mosaic_1.fit` --- `IRCUT` filter and `PROGRAM=5.34`.
-   `mosaic_4.fit` --- newer `PROGRAM=7.32` header variant, including
    `DATE-EXP` and `BIAS`.
-   `mosaic_6.fit` --- legacy `PROGRAM=3.31` header variant, generic
    telescope identifier, and no `EQMODE` or `WIDECAM`.

Stage 3.1d validated the three representative mosaic-session fixtures across
legacy, intermediate and newer header variants. All three follow the same
existing raw Bayer-to-RGB path without mosaic-specific production logic.
Stage 3.1d completed with 48 tests passing and Ruff clean.

Stage 3.1e final validation confirmed the complete Stage 3 contract with 48
tests passing and Ruff clean. Stage 3 is complete.

## Stage 4 Summary

### Stage 4 --- RGB FITS processing/handling

Stage 4.1a defines the handling contract for FITS images already stored as
RGB. The supported FITS input layout is channels-first `(3, height, width)`,
and the common toolkit RGB representation is `(height, width, 3)`.

Stage 4 layout normalization moves the channel axis from first to last while
preserving RGB channel order, numerical values and dtype precision.
Seestar `uint16` and Siril `float32` RGB FITS are both supported use cases.
Standard and mosaic stacks use the same contract, with no producer-specific
processing path currently required.

Stage 4.1b implements the public
`normalize_rgb_layout(image)` imaging-layer function. It converts supported
channels-first `(3, height, width)` RGB arrays into `(height, width, 3)` using
a channel-axis move while preserving RGB order, numerical values, `uint16` and
`float32` precision. Unsupported dimensionality and first-axis layouts are
rejected explicitly.

The same function handles Seestar, Siril, standard and mosaic RGB data without
producer- or mosaic-specific branches. Orientation correction and TIFF
conversion remain deferred.

Stage 4.1c validates the complete real Seestar RGB path for both the standard
`stacked.fit` and mosaic `stacked_mosaic.fit` fixtures. Both are classified as
`RGB_IMAGE`, retain channels-first `uint16` data through the FITS reader, and
normalize to channels-last `uint16` RGB with channel order and numerical values
preserved. Their retained `BAYERPAT=GRBG` metadata does not cause them to be
treated as raw Bayer data or demosaiced. No mosaic-specific Stage 4 RGB path is
required.

Stage 4.1d validates the same path for the standard `siril_stacked.fit` and
mosaic `siril_stacked_mosaic.fit` fixtures. Both are classified as `RGB_IMAGE`,
retain channels-first `float32` precision through the FITS reader, and normalize
to channels-last `float32` RGB with channel order and numerical values preserved.
No Siril-specific or mosaic-specific RGB path is required. Their observed
`[0, 1]` values remain fixture evidence rather than a universal floating-point
range rule, and orientation handling remains deferred.

### Stage 4 to Stage 5 handoff

Stage 4.1e defines the final RGB pixel-data contract consumed by Stage 5:

-   Shape is `(height, width, 3)` with channel order `R, G, B`.
-   Seestar RGB remains `uint16`, with numerical values preserved exactly.
-   Siril RGB remains `float32`, with numerical values preserved exactly.
-   The common representation is structural; Stage 4 does not impose a common
    numeric dtype.
-   The observed Siril `[0, 1]` range is fixture evidence, not a universal
    floating-point input rule.
-   Pixel handling does not branch by producer or mosaic origin.
-   Stage 4 applies no scaling, clipping, normalization, stretching, gamma,
    white balance, RGB equalisation or orientation correction.

Stage 5 owns all TIFF-specific decisions. These include sample type and bit
depth, photometric/channel conventions, metadata, validation, overwrite and
file-writing behaviour, direct `uint16` mapping, and the treatment of `float32`
data. If float-to-`uint16` conversion is selected, Stage 5 must explicitly
define and test the accepted input range, scaling, below- and above-range
handling, clipping, rounding, NaN, positive infinity and negative infinity.
Any such numeric representation conversion must preserve the linear processing
intent and must not become an implicit display stretch.

Orientation remains outside the Stage 4 handoff. Any future output-orientation
requirement must be specified separately from evidence.

Stage 4.1f final validation confirmed the complete Stage 4 contract with 58
tests passing and Ruff clean. Stage 4 is complete.

## Stage 5 Summary

### Stage 5 --- TIFF output

The low-level TIFF writer supports linear `(height, width, 3)` RGB data as
either directly preserved 16-bit `uint16` samples or directly preserved 32-bit
IEEE floating-point `float32` samples. It performs no implicit float-to-integer
conversion, scaling or clipping, does not impose a universal `[0, 1]` range,
and rejects non-finite `float32` samples.

The `convert_fits_to_tiff(input_path, output_path)` integration operation uses
existing FITS inspection and classification to route raw Bayer data through
demosaicing and already-RGB data through layout normalization. Both paths then
use the same TIFF writer without producer-specific, mosaic-specific, numeric or
orientation processing.

Stage 5.1e independently reopened and validated persisted TIFF output for the
authoritative raw Bayer, Seestar RGB and Siril RGB standard/mosaic fixture
matrix. Stage 5.1f final validation confirmed the complete Stage 5 contract
with 28 focused Stage 5 tests and 86 full-suite tests passing and Ruff clean.
Stage 5 is complete.

## Stage 6 Summary

### Stage 6.1a --- Conversion pipeline contract

The existing `convert_fits_to_tiff(input_path, output_path)` operation is the
single-file pipeline boundary for one explicit FIT/FITS input and one explicit
TIFF output. It orchestrates the existing FITS inspection/classification,
demosaicing or RGB-layout normalization, and TIFF-writing subsystems without
duplicating their responsibilities or transforming image data. Later Stage 6
work will add CLI and batch workflows around this boundary. Archive hierarchy,
file placement and archive directory creation remain Stage 7 responsibilities.

Stage 6.1b validates the raw Seestar route end-to-end through the public
pipeline using the standard `light.fit` and mosaic-session `mosaic_1.fit`
fixtures. Both are classified as `RAW_LIGHT`, use the metadata-derived `GRBG`
pattern and existing demosaicer, and produce channels-last `uint16` RGB TIFFs
without modifying their source FITS files. At Stage 6.1b completion, Seestar RGB
and Siril RGB route completion remained deferred to Stages 6.1c and 6.1d
respectively.

Stage 6.1c validates the native Seestar RGB route end-to-end through the public
pipeline using `stacked.fit` and `stacked_mosaic.fit`. Both are classified as
`RGB_IMAGE`, retain channels-first `uint16` source data through the FITS reader,
use the existing RGB-layout normalizer, and produce channels-last `uint16` RGB
TIFFs without modifying their source files. Siril `float32` RGB route
completion remained deferred to Stage 6.1d at that point.

Stage 6.1d validates the Siril RGB route end-to-end through the same generic
`RGB_IMAGE` pipeline using `siril_stacked.fit` and
`siril_stacked_mosaic.fit`. Both retain channels-first 32-bit floating-point
source data through the FITS reader, use the shared RGB-layout normalizer, and
produce channels-last 32-bit IEEE floating-point RGB TIFFs with values
preserved and source files unchanged. No Siril-specific production branch is
required.

Stage 6.1e exposes all three validated routes through the user-facing
`seestar-toolkit convert INPUT_FITS OUTPUT_TIFF` command. The CLI remains a thin
adapter over `convert_fits_to_tiff()`, reports the created destination on
success, and reports expected FITS, classification and TIFF failures without a
traceback.

Stage 6.1f adds `seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR` as a thin
flat-directory orchestrator over the same single-file pipeline. It discovers
regular `.fit` and `.fits` files case-insensitively without recursion,
processes them in deterministic filename order, and maps source stems to
`.tiff` names in one explicit output directory. Expected per-file failures do
not stop later conversions; the command reports discovered, converted and
failed counts and returns non-zero for partial failure or no matches. Source
files are never moved, renamed, deleted or modified.

Stage 6.1f is conversion-only. Archive hierarchy/configuration and source-file
placement remain Stage 7 responsibilities, broad dataset qualification remains
Stage 8 work, and packaging/release remains Stage 9 work.

Stage 6.1g integrated validation exercises the public single-file pipeline and
configured console-script boundary for raw Seestar Bayer, native Seestar RGB,
and Siril RGB data. It also validates successful mixed batches, continuation
after invalid-input and existing-destination failures, no-match handling,
case-insensitive deterministic discovery, the non-recursive boundary, and
strong source preservation. The existing Stage 6 implementation passed this
workflow validation without a production-code defect or fix.

Stage 6.1g did not formally close Stage 6; that final closure audit was reserved
for Stage 6.1h. Archive hierarchy, metadata-derived placement, recursive
archive traversal, and source archive movement remained absent and deferred to
Stage 7.

Stage 6.1h final closure validation confirmed the public single-file pipeline,
all three supported real-data conversion routes, the single-file and batch CLI
contracts, exit statuses, expected-error handling, overwrite protection,
mixed-batch continuation, deterministic case-insensitive non-recursive
discovery, source preservation, and configured console/module entry points.
The complete test suite and Ruff checks passed, and no production defect or
unresolved Stage 6 blocker was found. Stage 6 is complete.

Stage 6 remains limited to conversion and flat-directory batch orchestration.
Archive organisation remains Stage 7, broad real-dataset qualification remains
Stage 8, and packaging/release remains Stage 9.

## Stage 7 --- Complete

### Stage 7 --- Archive organisation and file management

Stage 7 implements the archive organisation layer that turns Seestar source
material and Toolkit derivatives into a structured, permanent image archive.
Stage 7.1a defined the architecture and policy contracts; Stages 7.1b–7.1i
implemented and validated discovery, reconstruction, placement, safe file
operations, TIFF orchestration, CLI/dry-run behavior and derived indexes.

The archive hierarchy is configurable rather than hard-coded. The default
layout is:

`{target}/{location}/{session_end_date}`

Alternative layouts, such as:

`{location}/{session_end_date}/{target}`

are supported through shared configuration that can be used by the CLI and
any future user interface.

`session_end_date` is the archive-only grouping date calculated as
`date(capture_datetime + 12 hours)` and formatted `YYYYMMDD`. It does not alter
source timestamps or image metadata.

Every reconstructed observation uses `observation_01`, `observation_02`, and
so on. Each observation owns:

```text
observation_NN/
├── lights/
├── seestar_stacked/
└── tiff/
```

Original lights are stored directly in `lights/` for Siril-friendly access.
The original Seestar stack and its TIFF derivative stay together in
`seestar_stacked/`; individual-light TIFF derivatives go in `tiff/`. Original
FITS names are preserved and derivative names replace the FIT/FITS extension
with `.tiff`.

Stage 7 policy includes:

-   Construction of archive paths from available image metadata.
-   Creation of missing archive directories.
-   User-configurable ordering of archive hierarchy components.
-   Safe, deterministic path-component handling for metadata-derived target and
    logical location values.
-   Defined behaviour when required archive metadata is absent or incomplete.
-   Reconstruction of observations from FITS metadata, directory context,
    filenames and capture timing rather than treating directories as
    observations.
-   Recognised Seestar stack FITS files as primary observation-end markers;
    filename stack counts are supporting evidence only.
-   Safe missing-stack and ambiguity handling rather than silent grouping.
-   User-documented intentional merging of compatible captures by leaving only
    the final stack eligible for discovery.
-   Location precedence covering explicit names, nearest saved location by
    radius, interactive entry where applicable and `unknown`; reverse
    geocoding remains deferred.
-   Separate preservation of precise capture coordinates and logical location.
-   Placement of original FIT/FITS while recognised full-size/thumbnail JPEG
    material remains untouched under the implemented safe `ignore` policy.
-   Placement of generated TIFF files within the archive.
-   Preservation of original source image data.
-   Safe default `copy`, with `move` explicitly selected and validated before
    source removal.
-   Safe handling of identical duplicates and same-name/different-content
    collisions, using content evidence such as SHA-256 and no silent overwrite.
-   Batch archive organisation.
-   Dry-run through the real planning path with zero filesystem mutation.
-   Regenerable target-level `INDEX.md` files using real telescope identifiers
    where available.

TOML is the human-readable configuration format. Configuration is shared by
the CLI and a possible future UI and currently covers hierarchy template,
saved locations, source action and collision policy; JPEG configuration,
geocoding and config persistence remain deferred. The archive metadata model
remains source-format-neutral where practical so a future DSLR adapter is
possible, but Stage 7 implements Seestar input only.

The agreed Stage 7 sequence is:

1. 7.1a --- architecture, configuration and policy contracts.
2. 7.1b --- Seestar input discovery and classification.
3. 7.1c --- observation reconstruction and stack association.
4. 7.1d --- archive metadata and destination path planning.
5. 7.1e --- safe archive file operations.
6. 7.1f --- TIFF generation and archive orchestration.
7. 7.1g --- archive CLI, interaction and dry-run.
8. 7.1h --- human-readable target indexes.
9. 7.1i --- complete Stage 7 workflow validation.
10. 7.1j --- formal Stage 7 closure.

Stage 7.1b introduces the independent
`discover_seestar_inputs(root)` API in `seestar_toolkit.archive`. It validates a
`My Works`-style root, scans the known shallow structure in deterministic path
order, and returns immutable typed inventory items classified as light FITS,
Seestar stack FITS, full-size JPEG, thumbnail JPEG or unknown. FIT/FITS
classification reuses the existing Stage 2 `inspect_fits()` and
`FitsImageClass` evidence; directory and filename context supplement rather
than replace it. Malformed or ambiguous per-file candidates remain visible
without preventing other discoveries.

Discovery is read-only and records no observation number, light-to-stack
association, grouping boundary, session end date or archive destination. The
generic `_sub` source-directory context is recognised, but no unconfirmed
mosaic-specific directory convention is hard-coded. Stage 7.1b establishes the
inventory boundary consumed by Stage 7.1c.

Stage 7.1c introduces
`reconstruct_seestar_observations(inventory)`, consuming the Stage 7.1b
inventory without rescanning. Recognised Seestar stacks close observations of
compatible preceding unassigned lights, so present intermediate stacks form
separate boundaries while an eligible final stack can intentionally close one
combined sequence when intermediate stacks are absent. Stack filename counts
are retained only as supporting evidence and never select exactly N lights.

FITS capture time is authoritative, with FITS exposure-end and then filename
time as fallbacks. Filename/FITS disagreements greater than two seconds remain
diagnostic. Association requires matching target, exposure and filter, rejects
known capture-mode conflicts, and uses a conservative 12-hour maximum span.
Compatible regular-cadence lights without a stack can form a `LIGHTS_ONLY`
result; large gaps, missing timestamps and insufficient compatibility evidence
remain `AMBIGUOUS` or `UNRESOLVED`. Stack-only cases remain visible.

Reconstruction is immutable and read-only. It assigns no final observation
directory name, session end date, location or archive path. Those decisions
were subsequently implemented by Stage 7.1d, with Stage 7.1c establishing the
reconstruction boundary consumed by that planning stage.

Stage 7.1d introduces `plan_seestar_archive(reconstruction, ...)`, an immutable,
read-only planning boundary that consumes Stage 7.1c output without rescanning
or regrouping sources. It resolves target evidence with FITS metadata first and
retains conflicts diagnostically; derives `session_end_date` from first-light
time, or stack time for stack-only observations, using the fixed +12-hour rule;
and expands configurable orderings of `{target}`, `{location}` and
`{session_end_date}` beneath an absolute archive root.

One reusable normalizer trims and collapses whitespace while preserving normal
spaces and case, replaces unsafe characters and separators deterministically,
and prevents absolute/traversal escapes. Logical source values remain separate
from normalized path components. Non-interactive location resolution uses an
explicit name first, otherwise the nearest configured GPS location within its
inclusive radius, otherwise `unknown`; it performs no reverse geocoding or
network access and retains exact captured GPS separately.

Planning assigns deterministic `observation_01` names within each
target/location/session group, expanding the number width above 99. It plans
original light destinations under `lights/`, light TIFF derivatives under
`tiff/`, and Seestar stack FITS/TIFF destinations together under
`seestar_stacked/`, preserving FITS filenames. Ambiguous, unresolved or untimed
observations remain visible as planning problems. Stage 7.1d creates no
directories or files and does not execute collision policy, generate TIFFs or
produce `INDEX.md`; those responsibilities remain in later Stage 7 work.

Stage 7.1e introduces `execute_archive_plan(plan, ...)`, which consumes the
Stage 7.1d plan without rediscovery, reconstruction or placement recalculation.
It executes original light and Seestar-stack FIT/FITS destinations only;
planned TIFF destinations remain untouched for Stage 7.1f.

`COPY` is the safe default source action. Explicit `MOVE` uses staged
copy-and-verify followed by source deletion; destination failure leaves the
source intact, while a deletion failure is reported as partial completion.
Writes use a same-directory temporary file, flush and filesystem sync,
streamed whole-file SHA-256 verification, then atomic replacement. Temporary
files are cleaned after expected failures.

The default collision policy skips identical content and reports different
content without mutation. An explicit error policy rejects every existing
destination, and explicit overwrite uses the same verified staged replacement
path. Identical MOVE collisions retain the source. Execution continues across
independent failures and returns immutable per-file outcomes plus aggregate
copy, move, skip, failure and complete/partial/failed status.

Execution defensively resolves archive and destination paths to prevent
traversal and destination-symlink escape, detects same-file/hardlink identity,
and rejects missing or non-regular sources and invalid destination parents.
Only parents required for executable FITS placements are created. Stage 7.1e
adds no TIFF conversion, compression, archive CLI, dry-run orchestration,
interactive prompting, reverse geocoding, JPEG operation or `INDEX.md`
generation. Those later responsibilities were implemented by the subsequent
Stage 7 sub-stages while preserving the Stage 7.1e execution boundary.

Stage 7.1f introduces the library-level
`archive_seestar_session(source_root, ...)` workflow. It composes the existing
discovery, reconstruction, planning and safe original-file execution APIs in
that order, then calls the established `convert_fits_to_tiff()` pipeline. Each
intermediate result remains available in the immutable aggregate result; none
of the underlying archive or image-processing behavior is duplicated.

Original FITS placement always precedes its TIFF conversion. Only `COPIED`,
`MOVED` and SHA-256-verified `SKIPPED_IDENTICAL` outcomes are TIFF-eligible.
Conversion reads the successfully archived FITS destination, so explicit MOVE
continues to work, and writes only to the TIFF destination already calculated
by Stage 7.1d. Collision, failure and partial original outcomes are
conservatively ineligible.

TIFF parents are created only for eligible conversions after resolved-path
containment checks. Existing TIFFs are preserved and reported as collisions;
the existing exclusive-create TIFF contract remains unchanged. TIFF failure
does not roll back a valid archived FITS or restore a moved source, and later
independent conversions continue. Aggregate `COMPLETE`, `PARTIAL` and `FAILED`
states retain planning, original-operation and TIFF failures rather than
hiding them. An empty source tree is a complete no-op that creates no archive.

Stage 7.1f established the library-level orchestration boundary subsequently
used by the Stage 7.1g archive CLI and dry-run workflow; target indexes were
added in Stage 7.1h. No JPEG operation, compression, reverse geocoding, network
service, interactive prompting, DSLR ingestion or new image conversion logic
was introduced by Stage 7.1f.

Stage 7 is deliberately separate from Stage 6. Stage 6 provides the
command-line and batch-processing capabilities needed to operate on multiple
images; Stage 7 uses those foundations to organise the resulting files into
their permanent archive structure.

Stage 6 `convert` and flat, non-recursive `convert-batch` behaviour remains
unchanged. Stage 8 will subsequently perform broad real-dataset qualification,
and Stage 9 remains packaging and release work.

## FITS Metadata Findings

Observed raw Seestar headers include `EXPOSURE`, `EXPTIME`, `TOTALEXP`,
`GAIN`, `BAYERPAT`, `OBJECT`, `FILTER`, `DATE-OBS`, `DATE-EXP`, `RA`,
`DEC`, `EQMODE`, `SITELAT`, `SITELONG`, `TELESCOP`, `INSTRUME` and
`IMAGETYP`.

Current working interpretation:

-   `EXPOSURE` and `EXPTIME` appear to represent individual exposure
    time.
-   `TOTALEXP` represents total exposure where applicable.
-   A stack exposure count may be derivable as `TOTALEXP / EXPOSURE`
    when both values are valid and meaningful.
-   `EQMODE` requires verification with suitable equatorial capture
    data.
-   Mosaic status cannot be assumed from dimensions alone.
-   Known raw FITS captured during mosaic sessions may contain no `MOSAIC`
    keyword; mosaic-session origin therefore cannot currently be inferred
    reliably from that header field.

## Capture-Mode Notes

-   Solar video and Solar timelapse produce MP4 files rather than
    individual FITS captures.
-   Lunar behaviour is believed to be similar but requires confirmation.
-   Planetary capture behaviour remains to be confirmed.
-   Seestar creates an in-telescope stacked/processed reference image in
    its object folder, while individual lights are stored in the
    corresponding sub-frame folder.
-   A Seestar mosaic capture session can result from expanding the capture
    frame beyond the normal field of view, rotating the capture frame, or
    both.
-   Raw subframes from observed mosaic sessions remain standard
    2-dimensional `uint16` `GRBG` Bayer light frames and do not require
    mosaic-specific demosaicing.
-   Reference Siril Seestar preprocessing scripts use the same debayer step
    for standard and mosaic-session lights. Their workflows diverge later
    during registration: the standard script uses normal registration,
    while the mosaic script plate-solves the sequence and applies registration
    with expanded framing.
-   The reviewed Siril scripts perform normalization and RGB equalisation
    during stacking rather than during debayering, supporting the toolkit
    decision to keep Stage 3 linear and colour-neutral.

## Design Decisions

-   Python 3.13.
-   `astropy` for FITS handling.
-   `tifffile` for TIFF work.
-   OpenCV for Bayer demosaicing and later image-processing stages.
-   Preserve linear image data and original files.
-   Use explicit image-layout classification rather than requiring
    callers to infer layout from NumPy dimensionality.
-   Current supported layouts: `FitsImageLayout.RAW_BAYER` and
    `FitsImageLayout.RGB`.
-   Archive directory hierarchy will be user-configurable, with
    `{target}/{location}/{session_end_date}` as the default layout. The
    preference will be shared by the CLI and any future UI.
-   Archive organisation and file relocation are owned by Stage 7 rather than
    the Stage 6 batch-processing layer.

## Development Environment

The active development virtual environment is stored on local disk
rather than inside the iCloud-hosted repository.

Editable installation from a virtual environment inside the iCloud
project caused Python path / `.pth` processing problems. Recreating the
environment locally with Python 3.13 resolved the issue.

Current environment:

-   Python 3.13
-   Editable install: `python -m pip install -e ".[dev]"`
-   Project source remains in the iCloud-hosted Git repository.

## Documentation Structure

-   `ARCHITECTURE.md` --- architecture and module responsibilities.
-   `PROJECT_Notes.md` --- roadmap, progress, findings and design
    decisions.
-   `SEESTAR_FITS_REFERENCE.md` --- observed FITS layouts and header
    reference.
-   `CHANGELOG.md` --- committed development stages.
-   `change_documents/` --- detailed implementation
    instructions.

## Known Issues / Open Questions

-   Confirm planetary capture output format.
-   Confirm Lunar capture output behaviour.
-   Continue documenting header differences between raw and stacked FITS
    files.
-   Investigate why the standard Siril Seestar preprocessing script applies
    `mirrorx_single result` while the mosaic preprocessing script does not.

## Stage 7.1g Progress

Stage 7.1g implements the dedicated archive CLI as a thin adapter over the
existing Stage 7 discovery, reconstruction, planning, safe original-file
execution and TIFF orchestration APIs. Archive preparation is now separately
callable so dry-run and real execution share one authoritative plan without
repeating discovery or reconstruction.

The command supports explicit roots, dry-run, location, hierarchy, COPY/MOVE,
collision policy, non-interactive operation and read-only TOML configuration.
The default configuration path is `~/.config/seestar-toolkit/config.toml`;
CLI values override configuration and configuration overrides safe built-in
defaults. Interactive terminal use can accept or reject a saved GPS match and
enter a one-run manual location, while non-interactive operation never prompts.
No reverse geocoder, INDEX.md generation, compression, JPEG operation or
config writing was included in Stage 7.1g; indexes followed in Stage 7.1h.

## Stage 7.1h Progress

Stage 7.1h adds derived target-level `INDEX.md` generation after original FITS
and TIFF execution. Index placement follows the concrete `{target}` token in
the configured hierarchy, including hierarchies where target is not first.
Indexes are deterministic convenience views and are never parsed as
authoritative archive state.

Incremental regeneration scans only the physical target subtree and reuses the
Stage 2 FITS inspector for archived historical metadata. It counts only safely
established original lights, keeps reported stack count separate, and retains
an observation even if its TIFF derivative fails. Same-directory temporary
writes plus atomic replacement preserve an existing index on failure. Typed
created, updated, unchanged, and failed results feed aggregate archive status.
Dry-run reports planned index paths while retaining all Stage 7.1g zero-write
guarantees.

## Stage 7.1i Validation

Stage 7.1i exercises the complete archive path through discovery,
reconstruction, location resolution, planning, safe FITS archival, TIFF
generation, target indexing and CLI reporting. The matrix covers real Seestar
raw-light/native-stack fixtures plus genuine synthetic FITS for COPY, MOVE,
dry-run, rerun, collision, overwrite, partial failure, empty/malformed input,
lights-only, stack-only, multiple observations, incremental sessions,
alternative hierarchy and configuration/location precedence.

Integrated incremental validation exposed one existing-contract defect: a
later invocation containing only a new observation in an existing
target/location/session was initially numbered `observation_01`, merging it
with prior archive history. Archive preparation now performs a narrow,
read-only reconciliation after the established planner. A destination with a
matching archived filename remains the same observation for rerun/collision
semantics; a genuinely new source set is allocated after existing numbered
observation directories containing archived FITS. This preserves Stage 7.1d
planning and Stage 7.1e collision behavior while producing `observation_02`
for incremental imports. No other production defect or new feature was found.
Stage 7.1i completed the integrated validation used by the final closure audit.

## Stage 7.1j Closure Audit

Stage 7.1j reconciled the complete Stage 7 architecture, public APIs, CLI,
configuration, safety policies, dry-run, TIFF orchestration, derived indexes,
incremental-observation correction, tests and documentation. Focused Stage 7
regressions and the full project quality gates passed without a new production
defect. Stage 6 `convert` and flat, non-recursive `convert-batch` behavior is
unchanged. JPEG operations, compression, reverse geocoding, configuration
persistence and DSLR ingestion remain explicitly deferred. Stage 8 remains
broad real-dataset qualification and Stage 9 remains packaging/release.

Stage 7 --- Archive organisation and file management is complete.

## Stage 8 --- Real-Data Qualification and Closure

Stage 8 is complete following the
[Stage 8.3a closure audit](change_documents/STAGE_8/STAGE_8.3a.md).
The audit uses [Stage 8.2g](change_documents/STAGE_8/STAGE_8.2g.md) at
`a329bd9` as the authoritative final real-data regression evidence; ground
truth was not regenerated during closure.

Stage 8.1a–d qualified the frozen nine-dataset corpus and Stage 8.1e
consolidated its discrepancies before production remediation. The completed
fixes are F8-01 equal-time light-before-stack ordering, F8-02 filename/FITS
timestamp diagnostic semantics, F8-03 discovery structural mosaic comparison,
F8-03A the same comparison in archive planning, and F8-04 stack-count
diagnostic semantics. FITS timestamp authority and filename fallback remain
intact; retained-light membership remains independent of STACKCNT.

[Stage 8.2e](change_documents/STAGE_8/STAGE_8.2e.md) remains a failed full
regression: it exposed the separate F8-03A archive-planning path after the
initial four fixes. [Stage 8.2f](change_documents/STAGE_8/STAGE_8.2f.md)
corrected that path using a shared comparison-only rule. Stage 8.2g then
passed the full replacement regression with all 117 criteria satisfied.
The earlier failure is preserved as historical evidence.

Final qualification covers 9 datasets, 11 COMPLETE observations, 326 retained
lights, 11 assigned stacks and 11 archive plans with the frozen dates and
membership intact. Before/after fingerprints establish preservation of all
1,020 external dataset files (2,061,243,868 bytes). Qualification required no
archive COPY/MOVE or complete dataset copies in the repository. Firmware
7.75/8.46/9.31, AltAz/EQ, same-target multiple observations, cross-midnight
evidence, large light gaps, equal timestamps, structural mosaic names,
legitimate Unknown, RGB stacks containing BAYERPAT, and retained-count versus
STACKCNT divergence are covered. All five confirmed findings are resolved.

Stage 8.3a passed 314 repository tests, Ruff, applicable formatting and
`git diff --check` without production or test-code changes. Architecture
documentation now records the established Stage 8 comparison, timestamp,
ordering and stack-count semantics; archive hierarchy, numbering and the
+12-hour date policy are unchanged. Earlier stage progress sections remain
historical descriptions of their original implementation baselines.

DF8-01 typed mosaic evidence and DF8-02 target correction/override remain
deliberately deferred and non-blocking. No known Stage 8 defect remains open.
Stage 9 --- Packaging and release is future work and must begin only in a
separately defined workflow. No Stage 9 implementation or closure commit was
created during this audit; the pending CHANGELOG workflow is preserved.

## Future Ideas

-   GUI
-   macOS app bundle
-   Windows executable
-   Linux package
-   Optional Siril integration
-   Option to add the the Telescope type/name to the archive directory hierarchy
-   Option to regenerate the entire archive structure if the user chooses a
    different structure
-   Archive observing-night date policy: consider making the archive date
    convention configurable, allowing users to choose how sessions spanning
    midnight are assigned to a calendar date (for example, start-date, end-date
    or the current fixed observing-night rollover convention).
-   Configurable telescope identity in archive hierarchy — Consider allowing the
    telescope type and/or user-defined telescope name to be included as an
    optional archive hierarchy component. This would support archives containing
    captures from multiple Seestar models or individual telescopes while
    preserving the existing configurable hierarchy approach.
-   Archive structure regeneration — Consider providing a controlled method for
    rebuilding or reorganising an existing Seestar Toolkit archive when the user
    changes the configured archive hierarchy. The operation should reconstruct
    the archive from existing archived data rather than requiring the user to
    reorganise directories manually, with dry-run, collision handling,
    verification and data-safety behaviour appropriate to a potentially large
    archive.
-   Configurable observing-night date rule — v1.1.0 uses a fixed 12-hour
    rollover rule when determining the observing-night date. Consider allowing
    the user to configure how an observing night is assigned, potentially
    including start-date, end-date or configurable rollover-time behaviour. Any
    future implementation must preserve deterministic grouping of captures that
    span midnight.
-   Location consistency checking and configuration updates — When a user
    supplies an explicit location label and the FITS contains usable GPS
    coordinates, consider comparing those coordinates with saved locations.
    Detect conflicts such as coordinates matching a different saved location, or
    a supplied name/coordinate combination not represented in the configuration.
    In interactive use, offer an appropriate correction or the option to
    add/update the saved location. This requires a future configuration-writing
    capability because v1.1.0 configuration is deliberately read-only. This is
    the enhancement we discussed yesterday. I like preserving the distinction
    between detecting a discrepancy and deciding what the Toolkit should
    subsequently do about it
-   anonymise command — Consider providing an explicit command for creating
    privacy-sanitised copies of FIT/FITS files for sharing, testing or support.
    Remove or replace identifying metadata such as observing-site coordinates
    and device identifiers while preserving the astronomical image data and
    metadata required to interpret the capture correctly. The original FITS file
    must never be modified in place; the command should produce a separate
    anonymised copy and report what metadata was removed or changed. A future
    workflow could support anonymise → verify → share.
-   Archive with batch conversion option
    Add an explicit option to seestar-toolkit archive allowing the user to
    request FITS → TIFF batch conversion of archived light frames as part
    of the same operation.
    Default archive behaviour remains archive-only. Batch conversion occurs only
    when explicitly requested. The option should reuse the existing
    convert-batch processing pipeline rather than introduce a separate
    conversion implementation.

## BUG-001 — archive light-TIFF side effect

Normal archive operation now preserves individual light FITS files without
automatically converting them or creating an observation-level `tiff/`
directory. The required TIFF companion for a Seestar-created stacked FITS
continues to be generated under `seestar_stacked/`. The earlier Stage 7 records
describe the former contract and remain unchanged as historical evidence. The
explicit archive plus batch-conversion option above remains a separate future
enhancement.

## Stage 9.1b documentation boundary and future work

Development guidance and detailed stage evidence now live in `docs/development/`;
`docs/user/` is reserved for the later Quick Start and User Guide. Root README
and CHANGELOG are transitional public entry points. This file remains the sole
internal future-enhancement authority; historical progress sections describe
their original stage state, not current navigation instructions.

The following remain future work and are not v1.1.0 support claims:

- S50 Pro validation/support using suitable representative evidence.
- S30 and S30 Pro validation/support if representative datasets are available.
- DSLR/conventional-camera ingestion and archive reconstruction.
- Solar/Lunar/Planetary MP4 processing, including frame extraction for stacking,
  preservation of useful timing/frame metadata and suitable output formats.
- GUI and an easier/native macOS installer.
- A privacy-conscious `seestar-toolkit diagnostics` command.
- Possible Linux/Windows support and possible PyPI publication.
- GitHub Discussions if community interest warrants it.

Current development setup is in [DEV_README.md](DEV_README.md); local private
capture policy is in [REAL_DATA_TESTING.md](REAL_DATA_TESTING.md).


## Stage 9.1d distribution validation — formally complete

Distribution CI and package validators are implemented for candidate Python
3.11–3.14 on macOS arm64. The current public history begins at `0cdc6c2`;
pre-public `master` remains separate and must not be merged or recreated.
Tracked public-safe fixtures are guarded by reviewed byte hashes. Builds and
runtime-only wheel/sdist smoke checks use isolated temporary environments.

Stage 9.1d formally closed at `c3c14dc` with green GitHub Actions and
329 tests on each candidate Python line. Its [report](change_documents/STAGE_9/STAGE_9.1d_REPORT.md)
preserves Run 1 FAIL, whitespace remediation and Run 2 PASS. That evidence
is unchanged by Stage 9.2a.

## Stage 9.2a — clean installation and Python support

Clean wheel/sdist installations on native macOS arm64 establish the v1.1.0
Python support range as 3.11–3.14 inclusive, combined with Stage 9.1d CI.
Metadata bounds installation to `>=3.11,<3.15` and lists those four classifiers;
no runtime dependency or production code change was required. Initial and
rebuilt final artifacts use separate fresh venvs for every candidate/artifact.
Real public-safe FITS conversion, installed imports and runtime-only dependency
separation are recorded in the [9.2a report](change_documents/STAGE_9/STAGE_9.2a_REPORT.md).

Stage 9.2a is formally COMPLETE at `1f7de39`, as confirmed by Stage review
in the Stage 9.2b starting context. v1.1.0 remains unreleased.

## Stage 9.2b — installed CLI, functional and storage validation

Stage 9.2b remains STARTED after passing technical checkpoints A–D. The
[completion audit](change_documents/STAGE_9/STAGE_9.2b_REPORT.md) records all 186
criteria. Formal closure readiness is FAIL pending independent review, approved
user commit and post-commit gates (criteria 140, 182–185).

Original USB EIO/disappearance and unconfirmed old-device cleanup remain FAIL
history; a different replacement device and NAS validation passed with cleanup.
Their current expected absence does not invalidate those results. No storage was
accessed in D. Source/runtime privacy and local uninstall checks passed; no
production defect or new feature was introduced. The actual archive/config/CLI
contracts remain authoritative for later documentation.

All owned local final-audit environments and data were removed. Stage 9.3/9.4
have not begun. The pending Stage 9.2a CHANGELOG closure entry is preserved;
no Stage 9.2b commit exists or has been invented.

## Stage 9.3a — Markdown documentation audit

Current baseline is `62cab64`, the Stage 9.2b validation closure commit supplied
for this Stage. Earlier pre-commit status paragraphs and checkpoint failure
evidence above remain historical records; no post-commit CI evidence is invented.

Stage 9.3a is STARTED. Checkpoint A audits the validated 1.1.0 CLI and designs
the authoritative User Guide, abbreviated Quick Start and public root documents.
The [specification](change_documents/STAGE_9/STAGE_9.3a.md) defines 65 closure
criteria; the [progress report](change_documents/STAGE_9/STAGE_9.3a_REPORT.md)
records the fact matrix, discrepancies and content outlines. Checkpoints B/C
are not begun. Python 3.11–3.14 support remains established; v1.1.0 is Unreleased.

Documentation must preserve shallow archive discovery, read-only config, actual
observation/date naming and both uint16 Seestar and float32 Siril TIFF output.
Use explicit copy in introductory archive examples so existing config cannot
select move. No public guide, package metadata or production change is made in A.
The pending Stage 9.2b development CHANGELOG entry remains unchanged. PDFs and
release checksum artifacts belong to Stage 9.3b, not this documentation stage.

### Stage 9.3a Checkpoint B — guides written

Checkpoint B is PASS pending independent review; Stage 9.3a remains STARTED.
The authoritative [User Guide](../user/SEESTAR_TOOLKIT_USER_GUIDE.md) and
abbreviated [Quick Start](../user/SEESTAR_TOOLKIT_QUICK_START.md) now document
validated 1.1.0 behaviour, including shallow discovery, explicit dry-run/copy,
read-only config and uint16 Seestar versus float32 Siril TIFFs.

The [appended report](change_documents/STAGE_9/STAGE_9.3a_REPORT.md) records 50
command occurrences, validation categories and the preserved helper failure/fix.
B uses an existing source-matching installation and disposable public-safe inputs;
no new wheel/sdist or release artifact was created. Actual clean artifact install
proof remains Stage 9.2a. Root documentation and final validation await explicit
Checkpoint C authorisation. The pending development CHANGELOG remains unchanged;
v1.1.0 remains Unreleased and no Stage 9.3a commit exists.

### Stage 9.3a Checkpoint C — public documentation and final audit

The public README, CHANGELOG, CONTRIBUTING guidance and GitHub Bug Report /
Feature Request forms are implemented. The README presents archive organisation
as the principal use case, links ordinary users to `docs/user`, and keeps support
claims within the validated S50, macOS Apple-silicon and Python 3.11–3.14 scope.
Full pytest, configured formatting, public fixture/history checks, whitespace
and final wheel/sdist distribution validation passed during the first audit. Its
failure remains recorded in the Stage 9.3a evidence. Final Checkpoint C
revalidation has not yet been run. Criteria 62–65 remain formal PENDING gates.
No PDF, checksum, commit, push, release publication or later-stage work occurred.

#### Checkpoint C final remediation revalidation

Checkpoint C is PASS and Stage 9.3a technical/documentation closure readiness is
PASS. Fresh full validation passes, including 330 tests, Ruff, configured
formatting, whitespace, public fixture/history checks, documentation/Issue-form
checks, installed entry points and isolated wheel/sdist validation. The original
Checkpoint C failure and later scope cleanup remain preserved in the Stage
evidence. Criteria 62–65 remain PENDING independent review, user closure commit
and post-commit verification gates. Stage 9.3a remains STARTED; v1.1.0 remains
Unreleased, and no later stage has begun.

## Stage 9.3b — PDF generation and documentation validation

Stage 9.3a closed at `e45ca0d`. Stage 9.3b Checkpoint A is PASS and defines the
repository PDF pipeline without implementing it. The two approved Markdown guide
hashes remain unchanged. The proposed development-only wrapper uses Pandoc with
an explicit XeLaTeX toolchain and embedded declared fonts, then independently
checks extracted content, links, metadata, geometry, fonts and rendered pages.
Two clean builds must be byte-identical before the PDFs are accepted.

The final repository artifacts will be a PDF and a two-entry SHA-256 manifest
beside each authoritative Markdown guide. Accepted PDF mtimes will match their
Markdown source mtimes. Only the PDFs enter the later release ZIP; Stage 9.4 owns
ZIP assembly and its external checksum. Checkpoint B requires independent review
and explicit authorisation. No generator, PDF, manifest, CI change or later-stage
artifact was produced in A.

### Stage 9.3b Checkpoint B continuation

The authorised PDF implementation and validation are recorded in the
[Stage 9.3b report](change_documents/STAGE_9/STAGE_9.3b_REPORT.md).
Both frozen guides and their approved PDFs are preserved. Independent human
visual review of all 32 pages is PASS. The final technical evidence is recorded
separately from independent closure review, user commit and post-commit gates.
Stage 9.3b remains STARTED; no Stage 9.4 artifact has been assembled.

## Stage 9.4a — release candidate and public repository readiness

Checkpoint A is complete, including the controlled privacy-history remediation
and final fresh-remote verification. Checkpoint B has assembled and validated a
private, untracked v1.1.0 candidate from exact committed source `0b0a6bf`.
Two independent builds are byte-identical; the seven-file ZIP, external checksum,
nested distributions, clean installs, entry points and documentation PDFs pass.
Checkpoint B passed independent review. Checkpoint C's exact-tree audit is PASS,
including PDF-hash reconciliation, privacy/scope review and final quality gates.
Stage 9.4a is ready for independent final review and closure commit authorization.
Commit, post-commit validation/CI, formal completion, tag, publication and Stage
9.4b remain pending.

### Stage 9.4b — final release and publication

Stage 9.4b is STARTED. Checkpoint A audit/design is PASS and defines 60 criteria
across design, exact-tree Gate 1, publication, public Gate 2 and final closure.
Criteria 1–12 pass; criteria 13–60 remain PENDING.

The final tag must contain the release date deliberately declared by the release
owner and pass full exact-commit validation before Gate 1 GO. Incidental UTC
rollover during continuous publication is harmless; deliberate postponement to
a different chosen release day requires updated outputs, full Gate 1 validation
and a new GO. No release action or Gate 2 action occurred in A.

#### Checkpoint B — proposed final release tree

The proposed dated v1.1.0 tree is technically validated. Public documents,
PDFs/manifests, release tooling and focused tests represent the declared
`2026-09-23` state. Full validation and repeated candidate builds pass;
generated artifacts remain outside Git. Criteria 13–25 pass, while 26–28 await
the final commit/clean-tree review, exact-commit remote CI and independent GO.
