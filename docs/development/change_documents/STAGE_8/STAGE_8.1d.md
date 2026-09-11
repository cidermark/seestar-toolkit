# Stage 8.1d — Toolkit Validation Against Dataset 08 Multi-Session Behaviour

## Status

START

## Purpose

Complete the Stage 8.1 real-data evidence-gathering phase by validating the hardest frozen dataset:

`dataset_08_fw931_eq_m57_three_sessions`

Dataset 08 contains three distinct real observations of the same target and is deliberately reserved until after the simpler single-observation datasets.

Stage 8.1d must validate current Toolkit behaviour without modifying production code, tests, reconstruction rules, timestamp rules, archive behaviour or data models.

The purpose is to determine:

- whether current reconstruction correctly separates three genuine observations sharing the same target, filter, mount mode and related metadata;
- whether observation boundaries survive a calendar-date transition;
- whether the agreed +12-hour astronomical-night/archive-date rule is applied consistently;
- how retained-light gaps interact with the current missing-stack/cadence assumptions;
- how current reconstruction behaves when retained-light count differs materially from `STACKCNT`;
- whether the previously confirmed equal-timestamp defect appears in any of the three sessions;
- whether Dataset 08 exposes additional reconstruction or archive defects not seen in Datasets 01–07 and 09.

A discrepancy is evidence to be recorded and classified. It is not permission to change production behaviour.

## Starting Commit

Expected starting commit:

`d5e7f92` — Stage 8.1c: validate Datasets 05-07 and 09

Before validation begins, record the actual `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` entry for Stage 8.1c is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.1d.md` document may also be present as an intentional uncommitted documentation change before validation begins.

## Dataset

Validate only:

`<private-test-data>/dataset_08_fw931_eq_m57_three_sessions`

Do not validate any other dataset during Stage 8.1d.

Do not repeat the independent ground-truth characterisation.

Do not modify, rename, move, rewrite or otherwise alter any external dataset file.

Do not copy the complete dataset into the repository.

## Frozen Ground Truth

Dataset 08 contains exactly three distinct COMPLETE observations.

All three belong to target:

`M 57`

The dataset proves that separate real observations may share:

- target;
- exposure;
- filter;
- mount mode;
- observing night;
- telescope/instrument identity;
- broad filesystem location.

They must nevertheless remain distinct observations.

Important frozen evidence includes:

- observation/session separation is real and must not be inferred solely from target/exposure/filter/mount compatibility;
- one observation crosses midnight;
- calendar date alone must not split an observation;
- the agreed archive/session date rule is based on `capture_datetime + 12 hours`;
- session 03 contains 135 retained 30-second light FITS;
- session 03 stack metadata reports `STACKCNT=106`;
- session 03 `TOTALEXP=3180`;
- `STACKCNT == TOTALEXP / EXPTIME` remains internally consistent;
- retained-light FITS count does not necessarily equal `STACKCNT`;
- genuine retained-light gaps can exceed the current simple cadence assumptions;
- the stack timestamp may duplicate a final-light timestamp or represent a later exposure.

Treat these as frozen observations, not hypotheses.

## Prior Stage 8.1 Evidence To Preserve

The following findings from Datasets 01–07 and 09 must be carried into Stage 8.1d as evidence only.

### Equal-Timestamp Reconstruction Defect

Datasets 02, 05 and 09 each failed reconstruction because the final retained light and stack had exactly equal authoritative FITS timestamps.

Current deterministic ordering processed the stack first, causing the final light to become a separate LIGHTS_ONLY observation.

No dataset with a non-equal final-light/stack timestamp has shown this specific defect so far.

For each Dataset 08 observation, explicitly check whether any light/stack authoritative timestamps are equal and whether ordering affects membership.

Do not change tie ordering.

### Filename/FITS Timestamp Diagnostic

Datasets 01–07 and 09 all produced roughly one-hour timestamp-conflict diagnostics caused by comparison of local filename time with UTC FITS time as naive datetimes.

FITS timestamps remained authoritative.

Measure the same behaviour in Dataset 08.

Do not remediate timestamp diagnostics.

### Mosaic Directory Diagnostic

Explicit mosaic datasets 02, 05, 07 and 09 produced noisy directory-target/FITS-target disagreement diagnostics due to `_mosaic` naming.

Dataset 08 is not being used to reopen or redesign mosaic handling.

Only record mosaic-related evidence if it genuinely appears in Dataset 08.

### Stack Evidence

Across Datasets 01–07 and 09:

- `STACKCNT == TOTALEXP / EXPTIME` held;
- source-light count happened also to equal `STACKCNT`;
- associated-light count differed only where the equal-timestamp defect separated a light.

Dataset 08 is specifically expected to break the assumption that retained source-light count must equal `STACKCNT`.

Do not treat that mismatch as a defect without independent evidence.

## Scope

Stage 8.1d shall:

1. Verify source-dataset preservation.
2. Run current Toolkit discovery.
3. Record deterministic discovery counts and metadata.
4. Run current Toolkit observation reconstruction.
5. Compare Toolkit observation count with frozen expected count of three.
6. Compare Toolkit statuses with three COMPLETE observations.
7. Examine full light/stack membership for every reconstructed observation.
8. Establish how current reconstruction chooses observation boundaries.
9. Inspect retained-light timing gaps relevant to reconstruction.
10. Explicitly examine the cross-midnight observation.
11. Check final-light/stack authoritative timestamp ordering for all three ground-truth observations.
12. Record `EXPTIME`, `STACKCNT`, `TOTALEXP`, retained-light count and associated-light count for every stack.
13. Exercise existing read-only archive/session planning where supported.
14. Compare planned observation/session structure with frozen ground truth.
15. Validate the +12-hour archive/session-date rule.
16. Record all material diagnostics and discrepancies.
17. Classify every material finding using the established Stage 8 scheme.
18. Preserve the evidence for Stage 8.1e consolidation.
19. Avoid all remediation.

## Environment

Record once at the start:

- Git HEAD;
- `git status --short`;
- Python executable;
- Python version;
- package import path;
- source/import context.

Use the project virtual environment and current source tree.

Use `PYTHONPATH=src` where required.

## Dataset Preservation

Establish before/after preservation evidence sufficient to demonstrate that validation did not modify the external data.

Prefer the deterministic preservation method used in Stage 8.1a–c.

Record:

- file count;
- total bytes;
- content manifest hash;
- file-state manifest hash where practical.

## Discovery

Record, where available:

- total files/items;
- light FITS count;
- stacked FITS count;
- full-size JPEG count;
- thumbnail JPEG count;
- unknown-item count;
- product/sub/root directory contexts;
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
- authoritative FITS timestamps;
- filename timestamps where exposed;
- `STACKCNT`;
- `TOTALEXP`;
- relevant diagnostics.

Do not infer observation boundaries from filenames alone.

## Ground-Truth Observation Comparison

The completion report must establish three explicit ground-truth observation sections:

- Ground-truth observation 1;
- Ground-truth observation 2;
- Ground-truth observation 3.

For each, identify the corresponding Toolkit reconstruction result or explain why no one-to-one match exists.

For each ground-truth observation record:

- expected light membership;
- expected stack;
- expected COMPLETE status;
- first retained light;
- last retained light;
- selected/authoritative times;
- exposure;
- filter;
- EQ mode;
- stack count;
- total exposure;
- whether it crosses midnight;
- relevant retained-light gaps;
- final-light/stack timestamp relationship.

Then compare current Toolkit output against it.

## Reconstruction

For every Toolkit reconstructed observation record:

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

Do not merely compare counts.

Compare exact membership and boundaries.

## Session Separation Analysis

Dataset 08 must be used to determine whether current reconstruction can distinguish three genuine observations that share compatible metadata.

Record:

- why the current algorithm separates or merges each section;
- stack positions relative to lights;
- time gaps between retained lights;
- time gaps around stack boundaries;
- whether any boundary depends on cadence threshold assumptions;
- whether intermediate stack evidence is sufficient to separate sessions;
- whether any observation is merged incorrectly with another;
- whether any observation is split incorrectly.

Do not redesign the algorithm.

## Cross-Midnight Analysis

At least one real observation crosses midnight.

Explicitly record:

- first and last authoritative capture times;
- calendar-date transition;
- whether reconstruction remains a single observation;
- whether archive/session dating remains on the correct astronomical night;
- whether any current logic uses calendar date in a way that causes an incorrect split.

Do not alter date logic.

## Retained-Light Gap Analysis

Frozen evidence states that genuine observations can contain retained-light gaps greater than current simple cadence thresholds.

Measure relevant gaps in Dataset 08.

Record:

- maximum retained-light gap within each ground-truth observation;
- current threshold applicable to that exposure;
- whether Toolkit reconstruction remains correct;
- whether any LIGHTS_ONLY fallback or boundary logic is triggered;
- whether a genuine observation is split because of a gap.

Do not change cadence thresholds.

## Equal-Timestamp Analysis

For each ground-truth observation:

- compare final retained-light authoritative FITS timestamp with stack timestamp;
- explicitly state earlier/later/equal;
- if equal, record deterministic ordering;
- compare behaviour with Datasets 02, 05 and 09;
- identify whether any resulting split is the already-known equal-timestamp defect or a distinct issue.

Do not change tie ordering.

## Stack Evidence

For each stack record:

- `EXPTIME`;
- `STACKCNT`;
- `TOTALEXP`;
- `TOTALEXP / EXPTIME`;
- total retained source-light FITS count assigned by frozen ground truth;
- Toolkit associated-light count.

Explicitly preserve the distinction between:

- stack acceptance/count metadata;
- retained source light files;
- current Toolkit membership.

For session 03, specifically compare:

- 30-second exposure;
- `STACKCNT=106`;
- `TOTALEXP=3180`;
- 135 retained source-light FITS.

The 135-versus-106 difference is frozen valid evidence and must not be classified as an error merely because the counts differ.

## Timestamp Diagnostics

Record:

- total timestamp-conflict diagnostic count;
- approximate offset/range;
- whether the same local-filename/UTC-FITS pattern repeats;
- whether FITS timestamps remain authoritative;
- whether any diagnostic affects actual reconstruction.

Do not remediate.

## Archive/Session Planning

Where current public APIs permit read-only planning, record:

- planned observation count;
- target;
- logical location;
- retained GPS;
- archive/session date;
- application of `capture_datetime + 12 hours`;
- observation/session numbering;
- planned light count per observation;
- planned stack count per observation;
- planning problems;
- proposed hierarchy.

Verify whether the three real observations remain distinct in planning.

Use a diagnostic/nonexistent archive root and verify that read-only planning does not create it.

Do not execute COPY or MOVE operations.

## Exclusions

Stage 8.1d must not:

- modify production code;
- modify tests;
- remediate equal-timestamp ordering;
- alter light/stack tie ordering;
- remediate timestamp diagnostics;
- alter timestamp precedence;
- change the timestamp-conflict threshold;
- change cadence/grouping thresholds;
- change stack-count interpretation;
- assume retained-light count must equal `STACKCNT`;
- alter session-boundary rules;
- alter archive-date logic;
- change observation/session terminology;
- add target correction/override;
- add mosaic metadata;
- copy the complete dataset into the repository;
- create permanent regression fixtures;
- execute archive COPY or MOVE;
- validate any additional dataset;
- begin Stage 8.1e remediation design;
- implement any fix.

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

Observation count, status, boundaries or membership differ from ground truth.

### ARCHIVE

Observation reconstruction is correct but archive/session interpretation is incorrect.

### ROBUSTNESS

Legitimate input causes an unexpected exception, crash or inability to validate.

### DEFERRED FEATURE

The finding represents recognised future functionality outside current validation/remediation scope.

## Dataset Result Classification

Dataset 08 receives one overall result:

- PASS
- PASS WITH FINDINGS
- FAIL — discrepancy recorded

A FAIL does not itself authorise remediation.

## Comparison Output

Produce a dataset-level comparison table:

| ID | Component | Ground truth / expected | Toolkit actual | Classification | Impact |
|----|-----------|-------------------------|----------------|----------------|--------|

Use stable identifiers:

`D08-01`, `D08-02`, ...

Also provide a compact per-ground-truth-observation table showing:

| Observation | Expected status | Expected retained lights | Stack count | Toolkit match | Toolkit status | Toolkit lights | Boundary/membership result |
|-------------|-----------------|--------------------------|-------------|---------------|----------------|----------------|----------------------------|

## Cross-Stage 8.1 Evidence Summary

At the end of Stage 8.1d provide a concise evidence summary across all nine datasets and all 11 frozen real observations covering:

- correct versus incorrect reconstruction;
- equal-timestamp cases;
- timestamp diagnostic recurrence;
- mosaic diagnostic recurrence;
- AltAz versus EQ;
- firmware 7.75, 8.46 and 9.31;
- cross-midnight behaviour;
- retained-light gap behaviour;
- `STACKCNT`, `TOTALEXP` and retained-light relationships;
- multi-observation/session separation;
- archive planning consequences;
- any new defect category.

This is evidence consolidation only.

Do not design fixes yet.

## Repository Validation

At the end run:

`python -m pytest`

`ruff check .`

`git diff --check`

Record complete summary results.

If no Python files changed, formatting validation may be recorded as not applicable.

## Completion Report

Return a completion report containing:

### Stage 8.1d Result

Overall:

- PASS;
- PASS WITH FINDINGS; or
- FAIL — discrepancy recorded.

### Environment

Record validation environment and working-tree state.

### Dataset Preservation

Record before/after evidence.

### Discovery Summary

Record inventory and important metadata.

### Ground-Truth Observation 1

Full expected-versus-actual comparison.

### Ground-Truth Observation 2

Full expected-versus-actual comparison.

### Ground-Truth Observation 3

Full expected-versus-actual comparison.

### Toolkit Reconstruction Summary

List every reconstructed observation and exact membership outcome.

### Session Separation Analysis

Explain current observed boundaries without redesigning them.

### Cross-Midnight Analysis

Record behaviour against frozen expectation.

### Retained-Light Gap Analysis

Record measured gaps and current threshold behaviour.

### Equal-Timestamp Analysis

Record all three final-light/stack relationships.

### Stack Evidence

Record stack metadata versus retained source-light counts.

### Timestamp Diagnostics

Record recurrence and effect.

### Archive/Session Planning

Record planned structure and +12-hour date behaviour.

### Dataset 08 Comparison Matrix

Use stable `D08-*` identifiers.

### Cross-Stage 8.1 Evidence Summary

Cover all nine datasets / 11 real observations.

### Deferred Remediation Candidates

List candidate areas for Stage 8.1e consolidation.

Do not design fixes.

### Repository Validation

Record pytest, Ruff and `git diff --check`.

### Files Changed

Explicitly identify all files changed during Stage 8.1d.

No production/test changes are expected.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.1d is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `d5e7f92` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. Only Dataset 08 is validated.
4. The external dataset is verified unchanged after validation.
5. Discovery inventory and classifications are recorded.
6. Current Toolkit reconstruction output is recorded in full.
7. Toolkit observation count is compared with frozen expected count of three.
8. Toolkit statuses are compared with three COMPLETE observations.
9. Exact light/stack membership is examined against all three ground-truth observations.
10. Each ground-truth observation is mapped to Toolkit output or the lack of a valid mapping is explained.
11. Session/observation boundary behaviour is explicitly analysed.
12. Shared target/exposure/filter/mount compatibility is not assumed to imply one observation.
13. Intermediate stack evidence is examined as a session-separation signal.
14. Cross-midnight observation behaviour is explicitly validated.
15. Calendar date alone is not accepted as a valid reason to split a real observation.
16. The +12-hour astronomical-night/archive-date rule is checked.
17. Relevant retained-light gaps are measured.
18. The current cadence threshold applicable to those gaps is recorded.
19. Any gap-induced split or ambiguity is classified.
20. Final-light/stack authoritative timestamp ordering is checked for ground-truth observation 1.
21. Final-light/stack authoritative timestamp ordering is checked for ground-truth observation 2.
22. Final-light/stack authoritative timestamp ordering is checked for ground-truth observation 3.
23. Any equal-timestamp case is compared with the confirmed Dataset 02/05/09 defect.
24. `EXPTIME`, `STACKCNT`, `TOTALEXP` and retained-light counts are recorded for every stack.
25. `STACKCNT == TOTALEXP / EXPTIME` is checked for every stack where metadata permits.
26. Retained-light count versus `STACKCNT` is recorded without assuming equality.
27. Session 03 is explicitly checked against frozen evidence of 135 retained 30-second lights, `STACKCNT=106`, `TOTALEXP=3180`.
28. Timestamp-conflict diagnostics are measured.
29. FITS timestamp precedence is confirmed.
30. Read-only archive/session planning is exercised where supported.
31. Planned observation count is compared with the frozen expected count of three.
32. Planned membership is compared with reconstruction/ground truth.
33. Planning problems are recorded.
34. Diagnostic archive root non-creation is verified.
35. Every material discrepancy is classified.
36. Dataset 08 receives an explicit PASS, PASS WITH FINDINGS or FAIL result.
37. Findings are distinguished between root causes and downstream consequences.
38. No discrepancy is remediated.
39. No production code is changed.
40. No tests are changed.
41. No light/stack tie-ordering change is made.
42. No timestamp rule/threshold is changed.
43. No cadence/grouping threshold is changed.
44. No stack-count interpretation change is made.
45. No assumption that retained lights must equal `STACKCNT` is introduced.
46. No target correction/override capability is implemented.
47. No complete real dataset is copied into the repository.
48. No permanent regression fixture is created.
49. No archive COPY or MOVE operation is executed.
50. No other dataset is validated.
51. Full repository pytest passes.
52. Ruff passes.
53. `git diff --check` passes.
54. The completion report identifies every file changed during the sub-stage.
55. The completion report includes a cross-Stage 8.1 evidence summary covering all nine datasets / 11 frozen observations.
56. Deferred remediation candidates are preserved for Stage 8.1e without detailed remediation design.
57. The completion report provides sufficient evidence to proceed directly to Stage 8.1e discrepancy consolidation.

## Expected Next Stage

After Stage 8.1d closure, Stage 8.1e will consolidate and classify all discrepancies observed across:

- nine real-world datasets;
- 11 frozen real observations.

Stage 8.1e will determine the remediation workstreams and ordering.

Production remediation must not begin during Stage 8.1d.
