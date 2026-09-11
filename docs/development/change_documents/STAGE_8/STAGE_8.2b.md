# Stage 8.2b — Correct Filename/FITS Diagnostic Semantics

## Status

START

## Purpose

Remediate confirmed Stage 8 finding **F8-02**:

> The Toolkit currently compares Seestar filename timestamps and FITS timestamps as naive datetimes even though the Stage 8 real-data evidence establishes that the filename timestamp represents local wall time while the FITS timestamp represents UTC.

This produces recurring false timestamp-conflict diagnostics of approximately one hour across all nine validated real datasets.

Stage 8.2b must correct the diagnostic semantics while preserving all existing reconstruction behaviour.

This is a diagnostic-remediation stage only.

## Starting Commit

Expected starting commit:

`65872ec` — Stage 8.2a: correct equal-time reconstruction ordering

Before implementation begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.2a entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.2b.md` document may also be present as an intentional uncommitted documentation change.

## Authoritative Finding

### F8-02 — Filename/FITS Time-Basis Diagnostic

Classification:

`DIAGNOSTIC`

Severity:

`Low`

Priority:

`P2`

Evidence:

- observed in all nine real datasets;
- observed across firmware 7.75, 8.46 and 9.31;
- observed in AltAz and EQ captures;
- approximately one-hour differences are typical;
- FITS timestamps remain authoritative;
- no observation-membership error was caused by the diagnostic;
- filename timestamps remain useful fallback evidence where FITS time is unavailable.

Current invalid assumption:

> A naive timestamp parsed from the filename and a naive timestamp parsed from FITS share the same time basis and can therefore be directly compared as elapsed wall-clock values.

Stage 8.1 evidence establishes that this assumption is false for the characterised Seestar captures.

## Required Behaviour

The implementation must preserve the distinction between timestamp selection and timestamp diagnostics.

### Timestamp Selection

Preserve current precedence:

1. authoritative FITS `captured_at`, where available;
2. FITS `exposure_ended_at`, where applicable under current logic;
3. filename timestamp fallback where FITS time is unavailable;
4. unresolved otherwise.

Do not change selection ordering as part of Stage 8.2b.

### Timestamp Diagnostic Semantics

A conflict diagnostic should only claim a meaningful timestamp contradiction when the compared values are known to be on a comparable time basis.

Where the Toolkit has:

- authoritative FITS UTC-style time; and
- filename local-wall-clock time without explicit timezone provenance;

the simple numerical offset between those naive values must not automatically be classified as a timestamp conflict.

The fix must not invent a timezone.

Do not infer timezone from:

- GPS coordinates;
- operating-system timezone;
- archive location;
- network services;
- reverse geocoding.

No network dependency may be introduced.

### Genuine Conflict Protection

Where two timestamp sources are genuinely comparable under existing or new explicit provenance, a meaningful conflict diagnostic should remain possible.

If the current data model does not provide sufficient provenance to distinguish such a case, the implementation may suppress only the invalid filename-versus-FITS comparison while retaining all other comparable-time diagnostics.

The completion report must explain the selected policy precisely.

## Non-Regression Requirements

Stage 8.2b must preserve all known-correct Stage 8 behaviour.

### Reconstruction

Preserve:

- Stage 8.2a equal-time semantic ordering;
- Dataset 02 as one COMPLETE observation with 13 lights;
- Dataset 05 as one COMPLETE observation with 12 lights;
- Dataset 09 as one COMPLETE observation with 12 lights;
- Dataset 08 as three COMPLETE observations with 12, 1 and 135 lights;
- intermediate stacks as valid observation boundaries;
- incompatible equal-time light handling;
- no backward assignment of genuinely later lights.

### Timestamp Authority

Preserve:

- FITS timestamps as authoritative;
- filename timestamps as fallback evidence;
- selected observation ordering;
- cross-midnight handling;
- +12-hour astronomical-night/archive date.

### Mosaic Behaviour

Do not remediate F8-03.

The `_mosaic` directory/FITS target warnings are expected to remain until Stage 8.2c.

### Stack Count Behaviour

Do not remediate F8-04.

Dataset 08 Session 03 may continue to report its retained-light versus `STACKCNT` diagnostic until Stage 8.2d.

### Other Behaviour

Preserve:

- legitimate target `Unknown`;
- AltAz and EQ support;
- firmware 7.75, 8.46 and 9.31;
- RGB stack classification despite `BAYERPAT=GRBG`;
- cadence thresholds;
- lights-only fallback grouping;
- archive hierarchy;
- observation numbering;
- no retained-light-count-equals-STACKCNT assumption.

## Scope

Stage 8.2b includes:

1. inspect the current timestamp-selection and diagnostic code;
2. identify the exact comparison producing F8-02;
3. determine the narrowest safe diagnostic policy;
4. add focused regression tests;
5. implement the diagnostic correction;
6. prove FITS precedence is unchanged;
7. prove filename fallback remains functional;
8. prove reconstruction membership/order is unchanged;
9. run full repository tests and static checks;
10. perform focused read-only real-data qualification across representative datasets;
11. preferably verify the false warning is eliminated across all nine datasets if practical.

## Expected Production Area

Primary expected implementation area:

`src/seestar_toolkit/archive/reconstruction.py`

or the specific module currently responsible for timestamp selection/conflict diagnostics.

Changes elsewhere are permitted only when directly required and must be justified.

Do not perform unrelated refactoring.

## Regression Test Strategy

### RF8-02A — Local Filename / UTC FITS

Create generated temporary FITS evidence where:

- FITS authoritative timestamp is present;
- filename timestamp differs by a realistic local offset such as one hour;
- both values represent the same capture under different time bases.

Expected:

- FITS time is selected;
- no false timestamp-conflict diagnostic is emitted;
- reconstruction membership is unaffected.

### RF8-02B — FITS Precedence

Explicitly verify that the diagnostic cleanup does not change selected timestamp precedence.

Expected:

- FITS timestamp remains selected whenever authoritative FITS timing exists;
- filename does not replace FITS merely because the values differ.

### RF8-02C — Filename Fallback

Create a case where authoritative FITS capture time is unavailable but a valid filename timestamp exists.

Expected:

- filename timestamp remains usable as fallback;
- the frame remains reconstructable according to existing rules.

### RF8-02D — Genuine Comparable Conflict

Where practical within the current model, retain or add a case where two genuinely comparable timestamp sources disagree beyond the existing threshold.

Expected:

- meaningful conflict remains diagnosable.

If the current model cannot represent explicit comparable provenance, document why this case is not implementable without broadening scope.

### F8-01 Non-Regression

Include focused coverage showing Stage 8.2a equal-time ordering remains intact.

Do not change semantic tie-ordering.

## Real-Data Qualification

Qualification must remain read-only.

At minimum validate representative datasets spanning the known evidence:

### Dataset 01

`<private-test-data>/dataset_01_fw846_altaz_c27_single`

Expected:

- existing correct observation remains correct;
- prior approximately one-hour timestamp warnings are eliminated under the new policy.

### Dataset 02

`<private-test-data>/dataset_02_fw846_altaz_unknown_mosaic_single`

Expected:

- remains one COMPLETE observation with 13 lights;
- F8-01 remains fixed;
- timestamp warnings caused solely by local/UTC naive comparison disappear;
- F8-03 mosaic warnings remain;
- `Unknown` remains legitimate.

### Dataset 06

`<private-test-data>/dataset_06_fw775_eq_ic1318_single`

Expected:

- correct observation remains correct;
- firmware 7.75 and EQ behaviour remain intact;
- false local/UTC timestamp warnings disappear.

### Dataset 08

`<private-test-data>/dataset_08_fw931_eq_m57_three_sessions`

Expected:

- exactly three COMPLETE observations;
- membership 12 / 1 / 135;
- timestamp warnings caused by F8-02 disappear;
- F8-04 Session 03 count diagnostic remains;
- archive date remains 20260907.

### Optional Full Nine-Dataset Diagnostic Sweep

If practical, run a read-only diagnostic count across all nine datasets.

Expected:

- F8-02 false timestamp-conflict warnings are eliminated across the characterised evidence set;
- no reconstruction result changes except those already corrected by Stage 8.2a;
- F8-03 and F8-04 remain where applicable.

This sweep is strongly preferred because F8-02 was observed in all nine datasets.

## Dataset Preservation

Do not:

- modify;
- rename;
- move;
- copy into the repository;
- archive COPY/MOVE.

Record that real datasets remained unchanged.

Preservation manifests may be reused if the qualification mechanism is demonstrably read-only, but before/after verification is preferred where practical.

## Diagnostics Expected To Remain

After Stage 8.2b:

### F8-03

`_mosaic` directory-target diagnostics remain in Datasets 02, 05, 07 and 09.

### F8-04

Dataset 08 Session 03 retained-source versus accepted-stack-count diagnostic remains.

These are not Stage 8.2b failures.

## Exclusions

Stage 8.2b must not:

- change Stage 8.2a equal-time semantic ordering;
- remediate F8-03;
- remediate F8-04;
- change target normalization;
- add typed mosaic representation;
- change `STACKCNT` semantics;
- change cadence thresholds;
- change lights-only grouping;
- change archive hierarchy;
- change observation numbering;
- change +12-hour archive date logic;
- add target override/correction;
- infer timezone from GPS;
- infer timezone from machine locale;
- use reverse geocoding;
- add a network dependency;
- copy full real datasets into the repository;
- execute archive COPY/MOVE;
- begin Stage 8.2c;
- include unrelated cleanup/refactors.

## Implementation Guidance

Prefer representing uncertainty honestly over fabricating timezone knowledge.

The Toolkit knows that FITS time is authoritative for these captures.

It does not necessarily know the timezone represented by the filename.

Therefore:

- do not manufacture an offset;
- do not silently convert based on the developer machine;
- do not use location lookup;
- do not weaken FITS precedence.

The implementation should remove the invalid diagnostic assumption rather than force the two clocks to agree.

## Validation

Run focused tests first.

Then run:

`python -m pytest`

`ruff check .`

`git diff --check`

If Python files change, run project-standard formatting validation.

Then perform the required read-only real-data qualification.

## Completion Report

Return a complete Stage 8.2b completion report containing:

### Stage 8.2b Result

Use:

- PASS;
- PASS WITH FINDINGS;
- FAIL.

### Environment

Record:

- starting HEAD;
- working-tree state;
- Python executable/version;
- package import path.

### Root Cause Confirmation

Identify the exact current comparison responsible for F8-02.

### Diagnostic Policy

Explain precisely:

- which timestamp comparisons remain;
- which comparison is suppressed or changed;
- why;
- how genuine conflicts remain protected.

### Files Changed

List every changed file.

### Tests Added/Modified

Describe each focused regression.

### Focused Automated Validation

Report focused test results.

### Full Repository Validation

Report:

- pytest;
- Ruff;
- formatting check;
- `git diff --check`.

### Real-Data Qualification

Report Dataset 01, 02, 06 and 08 individually.

If the full nine-dataset sweep is performed, report per-dataset F8-02 diagnostic counts before/after or final counts.

### Reconstruction Non-Regression

Explicitly confirm observation counts and memberships remained correct.

### Deferred Findings

Confirm:

- F8-03 remains;
- F8-04 remains;
- Stage 8.2c not started.

### Dataset Preservation

Confirm no real dataset mutation/copy/archive action occurred.

### Git Diff Summary

Confirm no unrelated changes.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.2b is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `65872ec` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. The precise F8-02 timestamp diagnostic root cause is confirmed.
4. The implementation is scoped to F8-02 only.
5. FITS timestamps remain authoritative.
6. Filename timestamps remain available as fallback evidence.
7. Timestamp selection precedence is unchanged.
8. The invalid naive local-filename versus UTC-FITS conflict assumption is removed.
9. No timezone is invented for filename timestamps.
10. No timezone is inferred from GPS.
11. No timezone is inferred from operating-system locale/timezone.
12. No reverse-geocoding dependency is added.
13. No network dependency is added.
14. A realistic local-offset/FITS-UTC regression is covered.
15. That regression selects the FITS timestamp.
16. That regression no longer emits the false conflict diagnostic.
17. FITS-precedence regression coverage exists.
18. Filename-fallback regression coverage exists.
19. Filename fallback continues to work.
20. Genuine comparable-conflict protection is tested or inability to represent it narrowly is explicitly justified.
21. Stage 8.2a equal-time ordering remains protected by tests.
22. Dataset 01 remains correctly reconstructed.
23. Dataset 01 false F8-02 diagnostics are eliminated under the new policy.
24. Dataset 02 remains exactly one observation.
25. Dataset 02 remains COMPLETE.
26. Dataset 02 retains all 13 lights.
27. Dataset 02 uses the correct stack.
28. Dataset 02 F8-02 diagnostics are eliminated under the new policy.
29. Dataset 02 F8-03 mosaic diagnostics remain.
30. Dataset 02 legitimate `Unknown` behaviour remains unchanged.
31. Dataset 06 remains correctly reconstructed.
32. Dataset 06 firmware 7.75 behaviour remains intact.
33. Dataset 06 EQ behaviour remains intact.
34. Dataset 06 F8-02 diagnostics are eliminated under the new policy.
35. Dataset 08 remains exactly three observations.
36. All three Dataset 08 observations remain COMPLETE.
37. Dataset 08 memberships remain 12, 1 and 135.
38. Dataset 08 stack memberships remain correct.
39. Dataset 08 F8-02 diagnostics are eliminated under the new policy.
40. Dataset 08 F8-04 Session 03 diagnostic remains.
41. Dataset 08 cross-midnight behaviour remains intact.
42. Dataset 08 large-gap stack-backed behaviour remains intact.
43. Dataset 08 intermediate-stack boundaries remain intact.
44. Dataset 08 archive planning remains three observations.
45. Dataset 08 +12-hour archive date remains 20260907.
46. F8-01 remains fixed for Datasets 02, 05 and 09.
47. No observation membership changes are introduced by F8-02 remediation.
48. No observation count changes are introduced by F8-02 remediation.
49. Timestamp ordering of frames remains unchanged except for previously implemented Stage 8.2a semantic ties.
50. Timestamp conflict threshold is not repurposed to hide the timezone problem.
51. Cadence/grouping thresholds are unchanged.
52. `STACKCNT` semantics are unchanged.
53. No retained-light-count equality assumption is introduced.
54. F8-03 is not remediated.
55. F8-04 is not remediated.
56. No typed mosaic field is added.
57. No target correction/override is added.
58. Archive hierarchy is unchanged.
59. Observation numbering is unchanged.
60. +12-hour archive-date policy is unchanged.
61. AltAz support remains intact.
62. EQ support remains intact.
63. Firmware 7.75, 8.46 and 9.31 compatibility remains intact.
64. RGB stack classification despite `BAYERPAT=GRBG` remains intact.
65. No complete real dataset is copied into the repository.
66. No archive COPY or MOVE operation is executed.
67. Real datasets used for qualification remain unchanged.
68. Full repository pytest passes.
69. Ruff passes.
70. `git diff --check` passes.
71. Formatting validation passes where applicable.
72. Every changed file is identified.
73. No unrelated production refactor or cleanup is included.
74. The completion report clearly distinguishes F8-02 remediation from F8-03/F8-04.
75. A full nine-dataset F8-02 sweep is performed, or omission is explicitly justified.
76. Evidence is sufficient to proceed to Stage 8.2c without reopening F8-02 design.

## Expected Next Stage

After Stage 8.2b is reviewed, committed and documented, proceed to:

**Stage 8.2c — Normalize Structural Mosaic Suffix for Target Comparison**

Stage 8.2c will address F8-03 only.
