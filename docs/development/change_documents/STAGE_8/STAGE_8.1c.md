# Stage 8.1c — Toolkit Validation Against Datasets 05, 06, 07 and 09

## Status

START

## Purpose

Continue the Stage 8.1 evidence-gathering phase by applying the established validation procedure to four additional real Seestar datasets covering:

- additional mosaic captures;
- equatorial operation;
- firmware 7.75;
- firmware 9.31;
- further real-world variation in target, exposure, filter, timestamps and filesystem context.

Stage 8.1c must validate current Toolkit behaviour without modifying production code, tests, reconstruction rules or archive behaviour.

The purpose is to determine:

- whether the equal-timestamp reconstruction defect found in Dataset 02 recurs;
- whether the recurring filename/FITS timestamp diagnostics continue across EQ captures and older firmware;
- whether `_mosaic` filesystem naming continues to produce noisy target diagnostics;
- whether older firmware 7.75 remains compatible with current discovery and reconstruction behaviour;
- whether current Toolkit reconstruction correctly handles all four COMPLETE observations;
- whether new defect categories emerge before Dataset 08 multi-session validation.

A discrepancy is evidence to be recorded and classified. It is not permission to modify production behaviour.

## Starting Commit

Expected starting commit:

`330d69a` — Stage 8.1b: validate Datasets 02-04

Before validation begins, record the actual `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` entry for Stage 8.1b is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.1c.md` document may also be present as an intentional uncommitted documentation change before validation begins.

## Datasets

Validate the following datasets in this exact order.

### Dataset 05

`<private-test-data>/dataset_05_fw931_altaz_ngc6888_mosaic_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- target: NGC 6888;
- filesystem context: explicit Seestar mosaic naming;
- firmware family: 9.31;
- mount mode: AltAz.

### Dataset 06

`<private-test-data>/dataset_06_fw775_eq_ic1318_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- target: IC 1318;
- firmware family: 7.75;
- mount mode: equatorial.

### Dataset 07

`<private-test-data>/dataset_07_fw775_eq_ic5070_mosaic_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- target: IC 5070;
- filesystem context: explicit Seestar mosaic naming;
- firmware family: 7.75;
- mount mode: equatorial.

### Dataset 09

`<private-test-data>/dataset_09_fw931_eq_ngc281w_mosaic_single`

Frozen ground truth:

- genuine observations: 1;
- expected status: COMPLETE;
- target: NGC 281W;
- filesystem context: explicit Seestar mosaic naming;
- firmware family: 9.31;
- mount mode: equatorial.

Do not repeat the independent ground-truth characterisation.

Do not modify, rename, move, rewrite or otherwise alter any external dataset file.

Do not copy the complete datasets into the repository.

## Prior Stage 8.1 Evidence To Preserve

Stage 8.1a and Stage 8.1b established the following Toolkit findings.

These are evidence to compare against, not behaviours to remediate during Stage 8.1c.

### Recurring Timestamp Diagnostic

Datasets 01–04 all produced filename/FITS timestamp-conflict diagnostics.

Evidence so far indicates:

- FITS timestamps are correctly selected as authoritative;
- filename times are local time;
- FITS times are UTC;
- current comparison treats both as naive datetimes;
- this produces approximately one-hour conflict warnings;
- the warnings are noisy but did not alter membership in Datasets 01, 03 or 04.

Stage 8.1c must determine whether this repeats for firmware 7.75, firmware 9.31 and EQ captures.

### Dataset 02 Equal-Timestamp Reconstruction Defect

Dataset 02 established a material reconstruction defect:

- the final retained light and stack had exactly equal authoritative FITS timestamps;
- deterministic ordering placed the stack before the equal-timestamp light;
- the stack closed the observation using the preceding lights;
- the final light became a separate LIGHTS_ONLY observation;
- archive planning therefore produced two observations instead of one.

Stage 8.1c must explicitly check whether any Dataset 05, 06, 07 or 09 light/stack pairs have equal authoritative timestamps and, if so, how current reconstruction behaves.

Do not change tie ordering.

### Mosaic Directory Diagnostic

Dataset 02 established that:

- explicit `_mosaic` filesystem naming is visible through directory names/context;
- there is no dedicated typed mosaic field;
- `_mosaic` can produce noisy directory-target versus FITS-target disagreement diagnostics.

Stage 8.1c contains three additional explicit mosaic datasets and must measure whether this behaviour recurs.

Do not add a mosaic field or change target-normalisation behaviour.

## Scope

For each dataset, Stage 8.1c shall:

1. Verify source-dataset preservation.
2. Run current Toolkit discovery.
3. Record deterministic discovery counts and important metadata.
4. Run current Toolkit observation reconstruction.
5. Record observation count, status and complete membership.
6. Inspect authoritative timestamps and stack/light ordering.
7. Exercise existing read-only archive/session planning where supported.
8. Compare current Toolkit behaviour with frozen ground truth.
9. Record all material diagnostics and discrepancies.
10. Classify each material finding using the established Stage 8 scheme.
11. Compare new evidence with Stage 8.1a and Stage 8.1b findings.
12. Preserve all findings for Stage 8.1e consolidation.
13. Continue through all four datasets unless a failure makes meaningful validation impossible.

Stage 8.1c must not remediate findings.

## Validation Order

Validation must proceed:

1. Dataset 05;
2. Dataset 06;
3. Dataset 07;
4. Dataset 09.

Each dataset receives its own comparison matrix and overall result.

A FAIL on an earlier dataset does not normally stop Stage 8.1c.

Continue so the same underlying assumptions can be measured across mosaic/non-mosaic, AltAz/EQ and firmware 7.75/9.31 data.

Stop only if current Toolkit behaviour prevents meaningful validation of subsequent datasets. If this occurs, document the blocking condition without modifying production code.

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

For each dataset, establish before/after preservation evidence sufficient to demonstrate that validation did not modify the external data.

Prefer the deterministic preservation method already used in Stage 8.1a and Stage 8.1b.

Record:

- file count;
- total bytes;
- content manifest hash;
- file-state manifest hash where practical.

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

For Datasets 05, 07 and 09, explicitly record how current Toolkit discovery represents the Seestar mosaic filesystem naming.

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

### Equal-Timestamp Analysis

For each dataset:

- compare the authoritative FITS timestamp of the final retained light with the assigned stack timestamp;
- explicitly state whether they are earlier/later/equal;
- if equal, record deterministic ordering and resulting membership;
- compare any equal-timestamp case with Dataset 02;
- do not change reconstruction ordering.

### Stack Evidence

For each stack record:

- `EXPTIME`;
- `STACKCNT`;
- `TOTALEXP`;
- retained-light FITS count;
- whether `STACKCNT == TOTALEXP / EXPTIME`;
- whether retained-light count equals `STACKCNT`.

A retained-light mismatch must not automatically be classified as a defect.

Use frozen ground truth and observation membership as the authority.

### Timestamp Diagnostics

For all four datasets:

- record whether the local-filename/UTC-FITS diagnostic pattern occurs;
- record warning count;
- record approximate offset/range;
- confirm whether FITS timestamps remain authoritative;
- compare firmware 7.75 and 9.31 behaviour with Datasets 01–04.

Do not remediate.

### Mosaic Filesystem Validation

For Datasets 05, 07 and 09 record:

- actual mosaic directory names;
- current discovery representation;
- directory/FITS target diagnostics;
- whether reconstruction succeeds;
- whether archive planning preserves correct target and membership;
- whether the lack of typed mosaic evidence causes any material behavioural failure.

Do not add new production metadata.

### Equatorial Validation

For Datasets 06, 07 and 09 explicitly record:

- FITS EQ/mount metadata;
- current Toolkit interpretation;
- whether EQ operation affects compatibility or reconstruction;
- whether archive planning behaves consistently with AltAz cases.

Do not change mount-mode interpretation.

### Firmware 7.75 Validation

Datasets 06 and 07 provide substantially older firmware evidence.

Compare with later firmware for metadata relied upon by current Toolkit behaviour, including:

- target;
- exposure;
- filter;
- timestamp availability;
- EQ mode;
- Bayer metadata;
- stack metadata;
- telescope/instrument identification;
- filesystem organisation.

Record observed differences only.

Do not add speculative compatibility behaviour.

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

Stage 8.1c must not:

- modify production code;
- modify tests;
- remediate the Dataset 02 equal-timestamp defect;
- alter light/stack tie ordering;
- remediate timestamp diagnostics;
- alter timestamp precedence;
- change the two-second diagnostic threshold;
- alter cadence/grouping thresholds;
- change stack-count interpretation;
- infer mosaic status from dimensions or WCS;
- add a typed mosaic field;
- change mosaic directory-target diagnostic behaviour;
- implement target-name correction/override;
- change archive naming;
- change session/observation terminology;
- copy full real datasets into the repository;
- create permanent regression fixtures;
- perform archive COPY or MOVE execution;
- begin Dataset 08 validation;
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

- Dataset 05: `D05-01`, `D05-02`, ...
- Dataset 06: `D06-01`, `D06-02`, ...
- Dataset 07: `D07-01`, `D07-02`, ...
- Dataset 09: `D09-01`, `D09-02`, ...

Where a finding repeats Stage 8.1a or Stage 8.1b evidence, explicitly identify the relationship.

## Cross-Dataset Analysis

At the end of Stage 8.1c, provide a concise comparison across Datasets 01–07 and 09 covering:

- successful versus failed reconstruction;
- equal-timestamp light/stack cases;
- timestamp-diagnostic recurrence;
- mosaic directory diagnostic recurrence;
- AltAz versus EQ behaviour;
- firmware 7.75 versus 8.46 versus 9.31;
- `STACKCNT`, `TOTALEXP` and retained-light relationships;
- any new defect categories.

Do not include Dataset 08 because it has not yet been validated against current Toolkit behaviour.

Do not turn this analysis into remediation design.

## Repository Validation

Because Stage 8.1c is read-only validation, production/test changes are not expected.

At the end run:

`python -m pytest`

`ruff check .`

`git diff --check`

Record complete summary results.

If no Python files changed, formatting validation may be recorded as not applicable.

## Completion Report

Return a completion report containing:

### Stage 8.1c Result

Overall:

- PASS;
- PASS WITH FINDINGS; or
- FAIL — discrepancy recorded.

### Environment

Record the validation environment and working-tree state.

### Dataset 05

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- equal-timestamp analysis;
- stack evidence;
- mosaic filesystem behaviour;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Dataset 06

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- equal-timestamp analysis;
- stack evidence;
- EQ behaviour;
- firmware 7.75 evidence;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Dataset 07

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- equal-timestamp analysis;
- stack evidence;
- mosaic filesystem behaviour;
- EQ behaviour;
- firmware 7.75 evidence;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Dataset 09

Include:

- frozen ground truth;
- preservation evidence;
- inventory/discovery summary;
- reconstruction summary;
- equal-timestamp analysis;
- stack evidence;
- mosaic filesystem behaviour;
- EQ behaviour;
- firmware 9.31 evidence;
- timestamp diagnostic behaviour;
- archive/session result;
- comparison matrix;
- dataset disposition.

### Cross-Dataset Findings

Summarise evidence across Datasets 01–07 and 09.

### Deferred Remediation Candidates

List candidate areas for Stage 8.1e consolidation only.

Do not design or implement fixes.

### Repository Validation

Record pytest, Ruff and `git diff --check`.

### Files Changed

Explicitly identify all files changed during Stage 8.1c.

No production code or test changes are expected.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.1c is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `330d69a` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. Datasets 05, 06, 07 and 09 are validated in the specified order.
4. All four external datasets are verified unchanged after validation.
5. Discovery behaviour is recorded for all four datasets.
6. Reconstruction behaviour is recorded for all four datasets.
7. Each dataset's Toolkit observation count is compared with the frozen expected count of one.
8. Each dataset's Toolkit observation status is compared with COMPLETE.
9. Complete light/stack membership is examined for every reconstructed observation.
10. Final-light versus stack authoritative FITS timestamp ordering is explicitly checked for all four datasets.
11. Any equal-timestamp case is compared directly with the Dataset 02 reconstruction defect.
12. `EXPTIME`, `STACKCNT`, `TOTALEXP` and retained-light count are recorded for all four stacks where exposed.
13. `STACKCNT == TOTALEXP / EXPTIME` is checked for all four datasets where metadata permits.
14. Retained-light count versus `STACKCNT` is recorded without assuming equality is required.
15. Timestamp diagnostics are measured across all four datasets.
16. FITS timestamp precedence is checked for all four datasets.
17. Dataset 05 mosaic filesystem behaviour is explicitly validated.
18. Dataset 07 mosaic filesystem behaviour is explicitly validated.
19. Dataset 09 mosaic filesystem behaviour is explicitly validated.
20. Mosaic-related directory/FITS target diagnostics are measured where present.
21. Dataset 06 equatorial metadata and behaviour are explicitly validated.
22. Dataset 07 equatorial metadata and behaviour are explicitly validated.
23. Dataset 09 equatorial metadata and behaviour are explicitly validated.
24. Firmware 7.75 evidence from Datasets 06 and 07 is compared with later firmware without speculative code changes.
25. Firmware 9.31 evidence from Datasets 05 and 09 is recorded.
26. Read-only archive/session planning is exercised for all four datasets where supported.
27. The +12-hour archive-date rule is checked for all four datasets.
28. Every material discrepancy is classified.
29. Each dataset receives an explicit PASS, PASS WITH FINDINGS or FAIL result.
30. Repeated findings are consolidated conceptually rather than treated as unrelated defects.
31. A cross-dataset comparison covering Datasets 01–07 and 09 is provided.
32. No discrepancy is remediated.
33. No production code is changed.
34. No tests are changed to accommodate real-data discrepancies.
35. No light/stack tie-ordering change is made.
36. No timestamp rule or threshold is changed.
37. No typed mosaic field is added.
38. No target correction/override capability is implemented.
39. No full real-world dataset is copied into the repository.
40. No permanent regression fixture is created.
41. No archive COPY or MOVE operation is executed.
42. Dataset 08 validation is not started.
43. Full repository pytest passes.
44. Ruff passes.
45. `git diff --check` passes.
46. The completion report identifies every file changed during the sub-stage.
47. Deferred remediation candidates are preserved for Stage 8.1e without detailed remediation design.
48. The Stage 8.1c report provides sufficient evidence to proceed to Dataset 08 validation without production remediation unless a genuinely blocking issue is identified.

## Expected Next Stage

After Stage 8.1c closure, Stage 8.1d will validate:

`dataset_08_fw931_eq_m57_three_sessions`

Dataset 08 contains three distinct COMPLETE observations and is deliberately deferred until the simpler single-observation datasets have been measured.

Production remediation remains deferred until Stage 8.1e consolidation unless current Toolkit behaviour makes meaningful Dataset 08 validation impossible.
