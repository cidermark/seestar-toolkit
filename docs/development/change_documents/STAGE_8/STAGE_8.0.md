# Stage 8 — Testing with Real Seestar Datasets

## Status

STARTED — 2026-09-04

Starting commit: `db4db43` — Stage 7.1j: validate and close Stage 7

The expected pending working-tree change at Stage 8 start is `docs/CHANGELOG.md`, containing the Stage 7.1j commit entry. This is intentional and must be carried into the first Stage 8 development commit.

## Purpose

Stage 8 qualifies the functionality established in Stages 1–7 against real Seestar datasets.

Stage 8 is primarily a validation and qualification stage, not a feature-development stage.

Its purpose is to:

- compare current Toolkit behaviour systematically against independently established real-world ground truth;
- identify and classify genuine defects in existing Stage 1–7 behaviour;
- distinguish misleading diagnostics and invalid assumptions from true reconstruction failures;
- identify deferred capabilities without expanding scope opportunistically;
- remediate confirmed defects only after the accumulated validation evidence has been reviewed;
- re-run the real-world qualification set after remediation;
- create small permanent regression fixtures only where they provide lasting value;
- perform a formal Stage 8 closure audit before Stage 9 begins.

## Real-World Dataset Collection

The complete Stage 8 real-world datasets are retained outside the repository at:

`<private-test-data>/`

They are:

1. `dataset_01_fw846_altaz_c27_single`
2. `dataset_02_fw846_altaz_unknown_mosaic_single`
3. `dataset_03_fw846_altaz_ngc6888_single`
4. `dataset_04_fw931_altaz_m27_single`
5. `dataset_05_fw931_altaz_ngc6888_mosaic_single`
6. `dataset_06_fw775_eq_ic1318_single`
7. `dataset_07_fw775_eq_ic5070_mosaic_single`
8. `dataset_08_fw931_eq_m57_three_sessions`
9. `dataset_09_fw931_eq_ngc281w_mosaic_single`

The complete datasets must not be moved into `tests/data/seestar/` during the validation phase.

Small curated permanent regression fixtures may be created later, after Toolkit behaviour has been compared against the full dataset collection and remediation requirements have been established.

## Frozen Ground Truth

Independent ground-truth characterisation of all nine datasets was completed before Toolkit validation began.

That work is authoritative input to Stage 8 and must not be repeated or reinterpreted merely to match current Toolkit behaviour.

The nine datasets contain 11 genuine observations:

- Datasets 01–07 each contain one COMPLETE observation.
- Dataset 08 contains three separate COMPLETE observations.
- Dataset 09 contains one COMPLETE observation.

Therefore:

- total datasets: 9;
- total genuine observations: 11;
- all 11 observations are COMPLETE.

## Established Real-World Findings

The independent characterisation phase established the following facts.

These are frozen evidence for Stage 8 validation and later remediation analysis.

### Timestamp behaviour

- FITS timestamps are authoritative when available.
- Filename timestamps routinely differ from FITS timestamps by more than the existing two-second diagnostic threshold.
- Stack timestamps may duplicate the timestamp of the final retained light.
- A stack timestamp may instead represent a subsequent exposure after the final retained light.

### Observation cadence and grouping

- Genuine single observations can contain retained-light gaps greater than the current cadence thresholds.
- The same target, exposure, filter and mount mode may contain more than one distinct observation.
- An observation may cross midnight and must not be split merely because the calendar date changes.
- Dataset 08 provides a real validation case for the established `capture_datetime + 12 hours` astronomical-night/archive-date rule.

### Stack metadata

- `STACKCNT` does not necessarily equal the number of retained light FITS files.
- Dataset 08 session 03 contains 135 retained 30-second light FITS files while the stack reports `STACKCNT=106` and `TOTALEXP=3180`.
- Across the characterised datasets, `STACKCNT == TOTALEXP / EXPTIME` has remained consistent.

### Mosaic identification

- Mosaic status cannot safely be inferred from image dimensions.
- Mosaic status cannot safely be inferred from WCS.
- Explicit Seestar mosaic filesystem naming is consistent across firmware 7.75, 8.46 and 9.31 and is therefore the strongest currently established real-world mosaic indicator.

### FITS classification metadata

- `BAYERPAT=GRBG` remains present on RGB stacked FITS files.
- Therefore `BAYERPAT` alone cannot identify raw Bayer image data.

### Target metadata

- `Unknown` is a legitimate Seestar target label.
- An `Unknown` target may still contain valid RA, DEC and WCS metadata.
- A future explicit target-name correction/override capability is required for legitimate `Unknown` or reframed targets.
- That capability must not be implemented opportunistically during Stage 8 validation.

## Validation Principle

The first Stage 8 implementation phase is evidence gathering.

A discrepancy is an observation, not permission to change production code.

Toolkit behaviour must first be compared systematically against the frozen ground truth across the real-world dataset collection.

Production remediation must not begin merely because the first dataset exposes a discrepancy.

Failures are accumulated, classified and analysed before remediation sub-stages are defined.

An exception may be made only if current Toolkit behaviour prevents meaningful validation of later datasets altogether. Such a case must be explicitly reviewed and documented before any production change is authorised.

## Validation Sequence

Validation proceeds incrementally so that simple behaviour is understood before complex multi-observation cases are introduced.

The intended sequence is:

### Stage 8.1a

Establish the validation protocol and validate Dataset 01.

### Stage 8.1b

Validate Datasets 02, 03 and 04.

These extend validation across:

- legitimate `Unknown` target metadata;
- mosaic filesystem structure;
- additional AltAz observations;
- firmware 8.46 and 9.31;
- differing targets and observation sizes.

### Stage 8.1c

Validate Datasets 05, 06, 07 and 09.

These extend validation across:

- additional mosaics;
- equatorial operation;
- firmware 7.75;
- firmware 9.31;
- wider real-world metadata variation.

### Stage 8.1d

Validate Dataset 08.

Dataset 08 is deliberately validated after the simpler datasets because it contains three distinct COMPLETE observations sharing the same target/exposure/filter/mount family and includes the strongest grouping, cadence, stack-count and cross-midnight evidence.

### Stage 8.1e

Consolidate the results from all nine datasets and all 11 observations.

No production remediation should begin before this consolidation unless an earlier failure prevents meaningful continuation of validation.

Stage 8.1e determines:

- the underlying defects represented by the accumulated findings;
- which findings are diagnostics rather than behavioural defects;
- which existing assumptions are invalid;
- which existing contracts require correction;
- which matters are deferred capabilities;
- the remediation sub-stages required under Stage 8.2.

### Stage 8.2x

Implement narrowly scoped remediation sub-stages derived from Stage 8.1e evidence.

Each remediation sub-stage must:

- identify the established behaviour or contract being corrected;
- reference the Stage 8 validation evidence;
- make the minimum coherent production change;
- receive automated regression coverage;
- preserve unrelated behaviour;
- run the complete relevant repository validation suite.

### Final real-data regression

After remediation, repeat the applicable real-world validation across all nine datasets.

The final expected result is recognition of all 11 genuine COMPLETE observations with correct membership and archive/session interpretation.

### Permanent regression fixtures

Only after the real-world remediation cycle is understood should Stage 8 consider extracting small curated fixtures into the repository.

Permanent fixtures should be minimal, purposeful and derived from clearly documented real-world behaviours.

The complete external datasets remain the authoritative broad qualification collection and do not need to be committed to Git.

### Formal Stage 8 closure audit

A dedicated final Stage 8 closure sub-stage must perform an audit equivalent to Stage 6.1h and Stage 7.1j.

Stage 9 must not begin during that audit.

## Validation Areas

Across the accumulated Stage 8 work, validate the applicable existing contracts for:

- FITS inspection;
- FITS classification;
- raw Bayer handling;
- RGB FITS handling;
- demosaicing;
- linear 16-bit RGB TIFF output;
- single-file conversion;
- flat non-recursive batch conversion;
- Seestar input discovery;
- observation reconstruction;
- observation membership;
- session grouping;
- astronomical/archive date calculation;
- archive planning;
- deterministic session numbering;
- archive COPY execution;
- explicit MOVE execution;
- Seestar stacked FITS preservation;
- stacked TIFF generation;
- archive index and metadata output;
- safe handling of unsupported or excluded inputs;
- JPEG non-interference.

Not every area must be exercised independently by every dataset.

## Read-Only Validation Rule

During Stage 8.1 validation:

- do not modify production code;
- do not change reconstruction thresholds;
- do not alter timestamp precedence;
- do not change cadence rules;
- do not change stack-count interpretation;
- do not change mosaic rules;
- do not change archive naming rules;
- do not implement target-name correction;
- do not move, rename, delete or rewrite source datasets;
- do not perform destructive archive operations;
- do not move the complete datasets into the repository.

Existing read-only discovery, reconstruction and archive-planning APIs may be exercised.

Temporary diagnostic commands or validation scripts may be used where required, provided they do not alter production behaviour or the real source datasets.

## Discrepancy Classifications

Every material validation finding must be assigned one of the following classifications.

### PASS

Toolkit behaviour agrees with frozen ground truth.

### INFO

A difference is informational and does not imply incorrect behaviour.

### DIAGNOSTIC

The primary result is correct but a Toolkit diagnostic is misleading, noisy or based on an invalid assumption.

### METADATA

Toolkit metadata interpretation materially disagrees with the real data.

### DISCOVERY

Filesystem content is discovered or classified incorrectly.

### RECONSTRUCTION

Observation count, status or membership disagrees with ground truth.

### ARCHIVE

Observation reconstruction is correct but session/archive interpretation is incorrect.

### ROBUSTNESS

Legitimate real-world input causes an unexpected exception, crash or inability to perform validation.

### DEFERRED FEATURE

The finding represents recognised future functionality that is deliberately outside the current validation/remediation scope.

## Dataset Result

Each dataset validation receives one overall result:

- **PASS** — Toolkit behaviour agrees with ground truth and no material finding remains.
- **PASS WITH FINDINGS** — the principal result agrees with ground truth but informational, diagnostic or deferred findings were recorded.
- **FAIL — discrepancy recorded** — one or more material Toolkit behaviours disagree with ground truth.

A FAIL during Stage 8.1 does not by itself authorise a production-code change.

## Evidence Requirements

Each dataset report should record, where applicable:

### Environment

- Git HEAD;
- working-tree status;
- Python executable/version;
- import context.

The intentionally pending preceding `docs/CHANGELOG.md` entry must be distinguished from unexpected working-tree changes.

### Discovery

- discovered item counts;
- FITS light count;
- stack FITS count;
- JPEG and thumbnail count;
- unknown-item count;
- source/directory context;
- important FITS classifications and metadata;
- existing diagnostics.

### Reconstruction

For each Toolkit observation:

- status;
- stack assignment;
- retained-light count;
- first and last retained light;
- observation timestamps;
- target;
- exposure;
- filter;
- mount/EQ mode;
- diagnostics;
- unassigned, ambiguous or unresolved FITS.

### Archive/session interpretation

Where current read-only APIs permit:

- archive target;
- astronomical/archive date;
- session number;
- observation/session association.

### Comparison matrix

Each material finding should record:

- finding ID;
- component;
- frozen expected behaviour;
- actual Toolkit behaviour;
- classification;
- impact;
- whether it requires Stage 8.1e review.

## JPEG Qualification

Representative real datasets retain genuine Seestar-created JPEG and thumbnail files.

Stage 8 must verify the established Stage 7 contract that these files are not treated as FITS inputs and are not accidentally copied, moved, deleted or modified by archive behaviour.

Repeated identical JPEG coverage is not required for every dataset once the behaviour is established.

## Firmware Coverage

The real-world collection covers Seestar firmware:

- 7.75;
- 8.46;
- 9.31.

Stage 8 therefore validates metadata and filesystem assumptions across multiple firmware generations without manufacturing compatibility cases.

Firmware differences should be recorded from observed data.

Fundamentally new formats remain deferred capabilities unless existing project requirements explicitly require support.

## Established Boundaries

Stage 8 must preserve the following project boundaries unless accumulated validation demonstrates that an existing contract is defective:

- Stage 6 `convert-batch` remains flat and non-recursive.
- Stage 7 owns archive discovery and organisation.
- Default archive hierarchy remains `{target}/{location}/{session_end_date}`.
- Session grouping uses `capture_datetime + 12 hours`.
- COPY remains the safe default.
- MOVE remains explicit.
- JPEGs remain untouched.
- No compression.
- No reverse geocoding or network dependency.
- No configuration persistence or writing.
- No DSLR ingestion.
- No UI development.
- No opportunistic architectural expansion.
- No speculative format support.
- Target-name correction/override is deferred.
- Stage 9 remains packaging and release.

## Stage 8 Completion Principle

Stage 8 is complete when:

- all nine real-world datasets have been systematically validated against frozen ground truth;
- all 11 genuine observations have documented Toolkit comparison evidence;
- accumulated failures have been consolidated and classified;
- confirmed existing-contract defects have received appropriately scoped remediation and regression coverage;
- deferred capabilities remain explicitly separated from defects;
- applicable real-world validation has been repeated after remediation;
- permanent regression fixtures have been created only where justified;
- repository tests and linting pass;
- documentation accurately records final behaviour and known deferred work;
- the formal Stage 8 closure audit passes.

Stage 9 must not begin until Stage 8 has been formally closed.
