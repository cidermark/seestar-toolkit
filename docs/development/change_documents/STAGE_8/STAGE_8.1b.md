# Stage 8.1b — Toolkit Validation Against Datasets 02–04

## Status

START

## Purpose

Continue the Stage 8.1 evidence-gathering phase by applying the validation procedure established in Stage 8.1a to three additional real Seestar datasets.

Stage 8.1b must validate current Toolkit behaviour without modifying production code or remediating discrepancies.

The purpose is to determine:

- whether the Dataset 01 findings recur across additional observations;
- whether legitimate `Unknown` target metadata affects discovery, reconstruction or archive planning;
- whether explicit Seestar mosaic filesystem naming is represented or affects current behaviour;
- whether firmware 8.46 and 9.31 behave consistently under current Toolkit assumptions;
- whether additional discovery, metadata, reconstruction, archive or diagnostic discrepancies emerge.

A discrepancy remains evidence to be recorded and classified. It is not permission to modify production behaviour.

## Starting Commit

Expected starting commit:

`5800b47` — Stage 8.1a: validate Dataset 01 baseline

Before validation begins, record the actual `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` entry for Stage 8.1a is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.1b.md` document may also be present as an intentional uncommitted documentation change before validation begins.

## Datasets

Validate the following datasets, in this order:

### Dataset 02

`<private-test-data>/dataset_02_fw846_altaz_unknown_mosaic_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- target label: legitimate `Unknown`;
- filesystem context: explicit Seestar mosaic naming;
- firmware family: 8.46;
- mount mode: AltAz.

### Dataset 03

`<private-test-data>/dataset_03_fw846_altaz_ngc6888_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- firmware family: 8.46;
- mount mode: AltAz.

### Dataset 04

`<private-test-data>/dataset_04_fw931_altaz_m27_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- firmware family: 9.31;
- mount mode: AltAz.

Do not repeat the independent ground-truth characterisation.

Do not modify, rename, move, rewrite or otherwise alter any external dataset file.

Do not copy the complete datasets into the repository.

## Scope

For each dataset, Stage 8.1b shall:

1. Verify source-dataset preservation.
2. Run current Toolkit discovery.
3. Record deterministic discovery counts and important metadata.
4. Run current Toolkit observation reconstruction.
5. Record observation count, status and membership.
6. Exercise existing read-only archive/session planning where supported.
7. Compare current Toolkit behaviour against frozen ground truth.
8. Record all material diagnostics and discrepancies.
9. Classify each material finding using the Stage 8 classification scheme.
10. Preserve findings for Stage 8.1e consolidation.
11. Continue to the next dataset even when a discrepancy is found, unless the discrepancy makes meaningful validation impossible.

Stage 8.1b must not remediate findings.

## Validation Order

Validation must proceed:

1. Dataset 02;
2. Dataset 03;
3. Dataset 04.

Each dataset receives its own comparison matrix and overall result.

A FAIL on Dataset 02 or Dataset 03 does not normally stop Stage 8.1b.

Continue validation so the same underlying assumption can be measured across multiple datasets.

Stop only if current behaviour prevents meaningful validation of subsequent datasets. If this occurs, document the blocking condition without modifying production code.

## Inclusions

### Environment

Record once at the start:

- Git HEAD;
- `git status --short`;
- Python executable;
- Python version;
- package import path;
- source/import context.

Use the project virtual environment and current source tree.

Use `PYTHONPATH=src` where required by the established development environment.

### Dataset Preservation

For each dataset, establish a before/after preservation check sufficient to demonstrate that validation did not modify the external data.

Prefer the same deterministic preservation approach used successfully in Stage 8.1a.

Record:

- file count;
- total bytes;
- content/file-state manifest hashes where practical.

### Discovery

For each dataset record, where available:

- total files/items;
- light FITS count;
- stacked FITS count;
- full-size JPEG count;
- thumbnail JPEG count;
- unknown-item count;
- source-directory context;
- product/sub-directory context;
- explicit mosaic/non-mosaic filesystem naming evidence;
- FITS classification;
- target;
- exposure;
- total exposure;
- filter;
- EQ/mount mode;
- Bayer pattern;
- telescope;
- instrument;
- GPS;
- FITS timestamps;
- filename timestamps where current reconstruction exposes them;
- `STACKCNT`;
- `TOTALEXP`;
- relevant diagnostics.

Do not infer mosaic status from image dimensions or WCS.

For Dataset 02, explicitly record how current Toolkit discovery represents the Seestar mosaic filesystem naming.

### Reconstruction

For every reconstructed observation record:

- observation index/identifier;
- reconstruction status;
- assigned stack;
- retained-light count;
- first retained light;
- last retained light;
- selected timestamps;
- target;
- exposure;
- filter;
- EQ/mount mode;
- reported stack count;
- diagnostics;
- unresolved FITS;
- ambiguous FITS;
- unassigned frame FITS.

Compare complete membership, not merely observation count and status.

### Timestamp Diagnostics

Dataset 01 produced timestamp-conflict diagnostics caused by comparing UTC FITS timestamps with local-time filename timestamps as naive datetimes.

For Datasets 02–04:

- record whether the same diagnostic pattern occurs;
- record diagnostic counts;
- record approximate offset/range;
- determine whether FITS timestamps remain correctly authoritative;
- do not fix the behaviour.

If the same root cause is supported by the evidence, reference the Dataset 01 finding rather than treating every warning as an independent defect.

### Unknown Target Validation

Dataset 02 uses `Unknown` as a legitimate Seestar target label.

Validate current behaviour without substituting or correcting the target.

Record:

- FITS target metadata;
- whether RA/DEC and WCS metadata are present where exposed;
- reconstruction target;
- archive target;
- whether `Unknown` causes rejection, ambiguity, incorrect grouping or planning problems.

The future explicit target-name correction/override capability remains a DEFERRED FEATURE.

Do not implement it.

### Mosaic Filesystem Validation

Dataset 02 is an explicit mosaic filesystem case.

Record:

- actual Seestar directory naming/context;
- how discovery currently represents that context;
- whether observation reconstruction succeeds;
- whether archive planning preserves correct observation membership;
- whether the absence of a typed mosaic field has any actual behavioural impact.

Do not add a mosaic field or change production models during Stage 8.1b.

### Archive/Session Planning

Where current public APIs permit read-only planning, record for each dataset:

- archive target;
- logical location;
- retained GPS;
- archive/session date;
- application of `capture_datetime + 12 hours`;
- observation/session numbering;
- planned light count;
- planned stack count;
- planning problems;
- proposed hierarchy.

Use a diagnostic/nonexistent archive root and verify that read-only planning does not create it.

Do not execute COPY or MOVE operations.

## Exclusions

Stage 8.1b must not:

- modify production code;
- modify tests;
- remediate timestamp diagnostics;
- alter timestamp precedence;
- change the two-second diagnostic threshold;
- alter cadence/grouping thresholds;
- change stack-count interpretation;
- infer mosaic status from dimensions or WCS;
- add a typed mosaic field;
- implement target-name correction/override;
- change archive naming;
- change session/observation terminology;
- copy full real datasets into the repository;
- create permanent regression fixtures;
- perform archive COPY or MOVE execution;
- begin Dataset 05 validation;
- define detailed remediation implementation before Stage 8.1e consolidation.

Documentation required to define or record this sub-stage is permitted.

## Discrepancy Classifications

Use the Stage 8 classifications unchanged:

### PASS

Toolkit behaviour agrees with frozen ground truth.

### INFO

Difference is informational and does not imply incorrect behaviour.

### DIAGNOSTIC

Primary result is correct, but a diagnostic is misleading, noisy or based on an invalid assumption.

### METADATA

Toolkit metadata interpretation differs materially from real data.

### DISCOVERY

Filesystem content is discovered or classified incorrectly.

### RECONSTRUCTION

Observation count, status or membership differs from ground truth.

### ARCHIVE

Observation reconstruction is correct but archive/session interpretation is incorrect.

### ROBUSTNESS

Legitimate input causes an unexpected exception, crash or inability to validate.

### DEFERRED FEATURE

The finding represents recognised future functionality outside the current validation/remediation scope.

## Dataset Result Classification

Each dataset must receive one overall result:

- PASS
- PASS WITH FINDINGS
- FAIL — discrepancy recorded

A FAIL does not itself authorise remediation.

## Comparison Output

For each dataset produce:

| ID | Component | Ground truth / expected | Toolkit actual | Classification | Impact |
|----|-----------|-------------------------|----------------|----------------|--------|

Use stable identifiers:

- Dataset 02: `D02-01`, `D02-02`, ...
- Dataset 03: `D03-01`, `D03-02`, ...
- Dataset 04: `D04-01`, `D04-02`, ...

Where a finding clearly repeats a Stage 8.1a finding, explicitly identify the relationship.

## Repository Validation

Because Stage 8.1b is read-only validation, production/test changes are not expected.

At the end run:

`python -m pytest`

`ruff check .`

`git diff --check`

Record complete summary results.

If no Python files changed, formatting validation may be recorded as not applicable.

## Completion Report

Return a completion report containing:

### Stage 8.1b result

Overall:

- PASS;
- PASS WITH FINDINGS; or
- FAIL — discrepancy recorded.

### Environment

Record the validation environment and working-tree state.

### Dataset 02

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- `Unknown` target behaviour;
- mosaic filesystem behaviour;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Dataset 03

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Dataset 04

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Cross-Dataset Findings

Summarise:

- findings repeated from Dataset 01;
- findings repeated across Datasets 02–04;
- firmware-related differences;
- mosaic-related evidence;
- `Unknown` target evidence;
- any new candidate defect categories.

Do not turn this summary into a remediation design.

### Deferred Remediation Candidates

List candidate areas for Stage 8.1e consolidation only.

### Repository Validation

Record pytest, Ruff and `git diff --check`.

### Files Changed

Explicitly identify all files changed during Stage 8.1b.

No production code or test changes are expected.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.1b is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches the expected Stage 8.1a baseline or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. Datasets 02, 03 and 04 are validated in the specified order.
4. All three external datasets are verified unchanged after validation.
5. Discovery behaviour is recorded for all three datasets.
6. Reconstruction behaviour is recorded for all three datasets.
7. Each dataset's Toolkit observation count is compared against the frozen expected count of one.
8. Each dataset's Toolkit observation status is compared against COMPLETE.
9. Light/stack membership is examined for every reconstructed observation.
10. Dataset 02 legitimate `Unknown` target behaviour is explicitly validated.
11. Dataset 02 explicit mosaic filesystem context is explicitly recorded and compared with current Toolkit representation.
12. Timestamp diagnostics are measured across all three datasets and compared with the Dataset 01 finding.
13. FITS timestamp precedence is checked for all three datasets.
14. Read-only archive/session planning is exercised for all three datasets where supported.
15. The +12-hour archive-date rule is checked for all three datasets.
16. Every material discrepancy is classified.
17. Each dataset receives an explicit PASS, PASS WITH FINDINGS or FAIL result.
18. Repeated findings are consolidated conceptually rather than counted as unrelated defects.
19. Firmware 8.46 versus 9.31 evidence is summarised without speculative implementation changes.
20. No discrepancy is remediated.
21. No production code is changed.
22. No tests are changed to accommodate real-data discrepancies.
23. No full real-world dataset is copied into the repository.
24. No permanent regression fixture is created.
25. No archive COPY or MOVE operation is executed.
26. The future target-name correction/override capability remains deferred.
27. Dataset 05 validation is not started.
28. Full repository pytest passes.
29. Ruff passes.
30. `git diff --check` passes.
31. The completion report identifies every file changed during the sub-stage.
32. The completion report contains a cross-dataset findings section suitable for later Stage 8.1e consolidation.

## Expected Next Stage

After Stage 8.1b closure, Stage 8.1c will validate:

- `dataset_05_fw931_altaz_ngc6888_mosaic_single`
- `dataset_06_fw775_eq_ic1318_single`
- `dataset_07_fw775_eq_ic5070_mosaic_single`
- `dataset_09_fw931_eq_ngc281w_mosaic_single`

Production remediation remains deferred.
