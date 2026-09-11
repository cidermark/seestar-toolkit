# Stage 8.1a — Toolkit Validation Protocol and Dataset 01 Baseline

## Status

START

## Purpose

Establish the formal Stage 8 Toolkit-versus-ground-truth validation procedure and apply it to the first real Seestar dataset.

Stage 8.1a is a measurement and evidence-gathering sub-stage.

It must determine how the current Toolkit behaves against the independently established and frozen ground truth without changing production behaviour in response to any discrepancy found.

A discrepancy discovered during this sub-stage is to be recorded and classified, not immediately corrected.

## Starting Commit

Expected starting production baseline:

`db4db43` — Stage 7.1j: validate and close Stage 7

Before beginning, record the actual `HEAD` commit.

The normal intentionally pending `docs/CHANGELOG.md` entry from the preceding committed stage is permitted and must not automatically be treated as an unexpected dirty working tree.

## Dataset

Use only:

`<private-test-data>/dataset_01_fw846_altaz_c27_single`

Do not copy or move the full dataset into the repository.

Do not modify any file in the external real-data dataset.

## Frozen Ground Truth

Dataset 01 contains:

- one real Seestar observation;
- expected observation status: COMPLETE.

The independent ground-truth characterisation phase is complete.

Do not repeat or redefine that ground truth during this sub-stage.

## Scope

Stage 8.1a shall:

1. Establish a repeatable validation/reporting procedure suitable for all nine Stage 8 datasets.
2. Execute current Toolkit discovery against Dataset 01.
3. Execute current Toolkit observation reconstruction against Dataset 01.
4. Exercise existing read-only archive/session interpretation where existing Stage 7 APIs permit it.
5. Compare Toolkit behaviour with the frozen ground truth.
6. Record all relevant diagnostics and discrepancies.
7. Classify discrepancies without altering production behaviour.
8. Produce a concise baseline report that can be compared consistently with later datasets.

## Inclusions

Validation shall record, where available:

### Discovery

- discovered item counts;
- light FITS count;
- stack FITS count;
- JPEG count;
- thumbnail JPEG count;
- unknown-item count;
- directory/source context;
- FITS classification;
- target metadata;
- exposure;
- filter;
- EQ/mount mode;
- FITS timestamps;
- filename timestamps where already exposed by the Toolkit;
- STACKCNT;
- TOTALEXP;
- BAYERPAT;
- explicit filesystem mosaic/non-mosaic context.

### Observation Reconstruction

For every observation returned:

- reconstruction status;
- observation count;
- assigned stack;
- retained-light count;
- first retained light;
- last retained light;
- relevant timestamps;
- target;
- exposure;
- filter;
- EQ/mount mode;
- diagnostics;
- excluded FITS;
- unresolved FITS;
- ambiguous FITS.

### Existing Archive/Session Interpretation

Where existing APIs allow read-only inspection:

- archive target;
- astronomical/archive date;
- proposed session number;
- observation/session association.

No actual archive operation is required.

## Exclusions

Stage 8.1a must not:

- modify production code;
- modify existing production behaviour;
- change reconstruction thresholds;
- change timestamp precedence;
- change cadence rules;
- change stack-count rules;
- implement target-name correction or override;
- modify archive naming rules;
- move, rename, delete or rewrite real dataset files;
- copy the complete dataset into `tests/data/seestar/`;
- create permanent regression fixtures;
- opportunistically fix a discrepancy found during Dataset 01 validation;
- begin Dataset 02 validation.

Temporary read-only diagnostic commands or validation scripts may be used, provided they do not alter production code or source datasets.

Any repository files added solely to support validation must be clearly justified in the completion report.

## Authoritative Evidence Rules

The independently established Stage 8 ground truth is authoritative.

Current Toolkit behaviour must be compared against it rather than used to redefine it.

The following independently established findings must be treated as evidence available to the later Stage 8 analysis and must not be discarded simply because they conflict with current implementation assumptions:

- FITS timestamps are authoritative.
- Filename/FITS timestamp differences greater than two seconds occur legitimately.
- Genuine observations can contain retained-light gaps exceeding existing cadence thresholds.
- STACKCNT need not equal retained-light FITS count.
- STACKCNT has remained consistent with TOTALEXP / EXPTIME in the characterised datasets.
- Mosaic status cannot safely be inferred from image dimensions or WCS.
- Explicit Seestar mosaic filesystem naming is consistent across the characterised firmware versions.
- BAYERPAT=GRBG may be present on RGB stacked FITS.
- Stack timestamps may duplicate the final light or represent a subsequent exposure.
- `Unknown` is a legitimate target label.
- Identical target/exposure/filter/mount metadata does not guarantee that captures belong to one observation.
- Observations may cross midnight.
- Archive-date interpretation uses the previously agreed +12-hour astronomical-night rule.

Stage 8.1a does not need to exercise every one of these conditions. They are frozen context for the complete Stage 8.1 validation sequence.

## Discrepancy Classifications

Use the following classifications:

### PASS

Toolkit behaviour agrees with ground truth.

### INFO

Difference is informational and does not imply incorrect behaviour.

### DIAGNOSTIC

Primary Toolkit result is correct, but a diagnostic is misleading, noisy or based on an invalid assumption.

### METADATA

Toolkit metadata interpretation differs materially from the real data.

### DISCOVERY

Filesystem content is discovered or classified incorrectly.

### RECONSTRUCTION

Observation count, status or membership differs from ground truth.

### ARCHIVE

Observation reconstruction is correct but archive/session interpretation is incorrect.

### ROBUSTNESS

Legitimate real-world input causes an unexpected exception, crash or inability to complete validation.

### DEFERRED FEATURE

Behaviour corresponds to a recognised future feature that is deliberately outside the validation/remediation scope.

## Validation Procedure

### Step 1 — Environment

Record:

- current Git HEAD;
- `git status --short`;
- Python executable;
- Python version;
- installed package/import context.

Use the project virtual environment and ensure the current source tree is being exercised.

If required by the existing development environment, use:

`PYTHONPATH=src`

Do not install or upgrade dependencies unless validation genuinely cannot proceed, and report any such issue rather than changing the environment silently.

### Step 2 — Discovery Validation

Run the current Stage 7 discovery implementation against Dataset 01.

Produce a concise deterministic summary rather than relying solely on a full object `repr`.

The report must provide enough detail to determine exactly what the Toolkit discovered and how FITS files were classified.

### Step 3 — Reconstruction Validation

Run the current Stage 7 observation reconstruction implementation against Dataset 01.

Produce a deterministic summary showing:

- observation count;
- status;
- stack assignment;
- retained-light count and membership boundaries;
- relevant metadata;
- diagnostics;
- excluded/unassigned input.

### Step 4 — Archive/Session Validation

Where current Stage 7 public APIs support read-only planning or interpretation, exercise them and report the proposed archive/session result.

Do not create or modify an archive.

If no suitable read-only public interface currently exists, record that fact. Do not add production functionality merely to make this validation step possible.

### Step 5 — Compare with Ground Truth

Expected:

- observation count: 1;
- observation status: COMPLETE.

Compare the complete Toolkit result, not merely the final status.

Record each material finding with:

- identifier;
- component;
- expected behaviour;
- actual behaviour;
- discrepancy classification;
- severity/impact;
- whether it should be investigated during the later Stage 8.1e consolidation.

### Step 6 — Stop Without Remediation

Do not fix discrepancies.

Stage 8.1a ends with an evidence report for Dataset 01.

## Validation Output Format

The completion report should contain:

### Environment

- HEAD
- working-tree status
- Python/import information

### Dataset Summary

- dataset path
- ground-truth observation count/status

### Discovery Result

Concise counts and important metadata.

### Reconstruction Result

For each reconstructed observation:

- observation identifier/index;
- status;
- stack;
- retained-light count;
- first light;
- last light;
- metadata;
- diagnostics.

### Archive/Session Result

Read-only result if available.

### Comparison Matrix

| ID | Component | Ground truth / expected | Toolkit actual | Classification | Impact |
|----|-----------|-------------------------|----------------|----------------|--------|

### Overall Dataset 01 Result

One of:

- PASS
- PASS WITH FINDINGS
- FAIL — discrepancy recorded

A FAIL during Stage 8.1a does not authorise production-code changes.

### Deferred Remediation Candidates

List candidate areas only.

Do not propose or implement detailed fixes unless needed to explain a finding.

## Closure Criteria

Stage 8.1a is complete only when all of the following are satisfied:

1. The actual starting Git HEAD has been recorded.
2. Existing intentional CHANGELOG dirtiness has been distinguished from unexpected changes.
3. Dataset 01 has been processed in place without modifying it.
4. Current discovery behaviour has been recorded.
5. Current reconstruction behaviour has been recorded.
6. Toolkit observation count has been compared with the expected count of one.
7. Toolkit observation status has been compared with COMPLETE.
8. Light/stack membership has been examined rather than checking status alone.
9. Relevant Toolkit diagnostics have been recorded.
10. Existing read-only archive/session behaviour has been tested where a suitable API already exists, or its absence has been documented.
11. Every material discrepancy has been classified.
12. No discrepancy has been remediated.
13. No production code has been changed.
14. No full real-world dataset has been copied into the repository.
15. No permanent regression fixture has been created.
16. The validation procedure is sufficiently repeatable to apply unchanged to later Stage 8.1 datasets.
17. The completion report clearly states whether Dataset 01 is PASS, PASS WITH FINDINGS, or FAIL.
18. Dataset 02 work has not started.

## Expected Next Stage

After Stage 8.1a closure:

Stage 8.1b will apply the frozen validation procedure to:

- `dataset_02_fw846_altaz_unknown_mosaic_single`
- `dataset_03_fw846_altaz_ngc6888_single`
- `dataset_04_fw931_altaz_m27_single`

Production remediation remains deferred until the wider Stage 8.1 evidence set has been collected.
