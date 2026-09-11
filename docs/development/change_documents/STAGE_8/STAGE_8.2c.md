# Stage 8.2c — Normalize Structural Mosaic Suffix for Target Comparison

## Status

START

## Purpose

Remediate confirmed Stage 8 finding **F8-03**:

> Seestar structural `_mosaic` filesystem suffixes are currently treated as part of the logical target name when directory-derived target evidence is compared with FITS `OBJECT`.

This creates false directory/FITS target mismatch diagnostics in all four characterised explicit mosaic datasets:

- Dataset 02;
- Dataset 05;
- Dataset 07;
- Dataset 09.

Stage 8.2c must remove those false diagnostics while preserving genuine target mismatch detection.

This stage must not introduce typed mosaic metadata or otherwise broaden the data model.

## Starting Commit

Expected starting commit:

`a5fda62` — Stage 8.2b: correct filename FITS diagnostic semantics

Before implementation begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.2b entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.2c.md` document may also be present as an intentional uncommitted documentation change.

## Authoritative Finding

### F8-03 — Structural Mosaic Suffix Target Diagnostic

Classification:

`DIAGNOSTIC`

Severity:

`Low`

Priority:

`P2`

Evidence:

- Dataset 02;
- Dataset 05;
- Dataset 07;
- Dataset 09.

Representative evidence:

Directory:

`NGC 6888_mosaic`

FITS target:

`NGC 6888`

and corresponding subdirectory:

`NGC 6888_mosaic_sub`

The Stage 8.1 evidence establishes that `_mosaic` is Seestar structural filesystem syntax rather than part of the logical target identity.

Dataset 07 is an important non-regression case because it reconstructed correctly despite the diagnostic noise. Therefore F8-03 is a diagnostic-semantics defect, not a reconstruction defect.

## Required Behaviour

For target-comparison purposes only:

1. recognize the established Seestar structural `_mosaic` suffix;
2. recognize the corresponding `_mosaic_sub` source-directory form;
3. compare the normalized logical directory target with FITS `OBJECT`;
4. do not emit a mismatch diagnostic when the normalized values match;
5. continue to emit a mismatch diagnostic when the normalized directory target genuinely differs from FITS `OBJECT`;
6. preserve the original source path and original directory evidence;
7. preserve FITS `OBJECT` as the authoritative logical target where current behaviour does so;
8. do not infer mosaic status from dimensions;
9. do not infer mosaic status from WCS;
10. do not add a typed mosaic field.

Normalization must be narrowly limited to recognized structural syntax.

Do not create broad target-name rewriting rules.

## Structural Forms

The implementation must account for the two observed forms:

- `<target>_mosaic`
- `<target>_mosaic_sub`

The normalization must not incorrectly strip arbitrary text merely because a target contains the word `mosaic` elsewhere.

Use suffix semantics, not substring replacement.

Examples:

`NGC 6888_mosaic` -> logical comparison target `NGC 6888`

`NGC 6888_mosaic_sub` -> logical comparison target `NGC 6888`

A genuine target such as:

`Mosaic Galaxy`

must remain unchanged unless it actually ends with one of the recognized Seestar structural suffixes.

## Non-Regression Requirements

### Reconstruction

Preserve all corrected reconstruction behaviour from Stages 8.2a and 8.2b.

Specifically preserve:

- Dataset 02: one COMPLETE observation with 13 lights;
- Dataset 05: one COMPLETE observation with 12 lights;
- Dataset 09: one COMPLETE observation with 12 lights;
- Dataset 08: three COMPLETE observations with 12, 1 and 135 lights;
- equal-time semantic light-before-stack ordering;
- incompatible equal-time handling;
- genuinely later light protection;
- intermediate-stack session boundaries;
- cross-midnight behaviour;
- large-gap stack-backed behaviour.

### Timestamp Behaviour

Preserve Stage 8.2b:

- FITS timestamps remain authoritative;
- filename timestamps remain fallback evidence;
- false local/UTC timestamp conflict diagnostics remain eliminated;
- no timezone inference is introduced.

### Target Behaviour

Preserve:

- legitimate target `Unknown`;
- FITS `OBJECT` logical target;
- genuine directory/FITS target mismatch diagnostics;
- case-insensitive comparison where already defined by current architecture;
- whitespace behaviour unless directly required for existing comparison semantics.

Do not add target correction/override.

### Mosaic Feature Boundary

Typed mosaic evidence remains deferred.

Stage 8.2c may normalize structural suffixes solely for comparison/diagnostic purposes.

It must not:

- add a model field such as `is_mosaic`;
- infer mosaic state from image dimensions;
- infer mosaic state from WCS;
- alter archive hierarchy based on mosaic state;
- alter reconstruction grouping based on mosaic state.

### Stack Count Behaviour

F8-04 remains deferred to Stage 8.2d.

Do not change `STACKCNT` semantics or retained-light diagnostics.

## Scope

Stage 8.2c includes:

1. inspect the discovery target-comparison logic;
2. identify the exact code path generating F8-03;
3. add a narrowly scoped structural target normalization helper if useful;
4. normalize `_mosaic` and `_mosaic_sub` only for comparison;
5. preserve original evidence/path values;
6. add focused tests for matching mosaic directory forms;
7. add focused tests proving genuine mismatches still diagnose;
8. add a regression proving ordinary target names containing `mosaic` are not damaged;
9. run full repository tests/static checks;
10. perform read-only real-data qualification against all four explicit mosaic datasets;
11. run focused non-regression checks against representative non-mosaic datasets and Dataset 08.

## Expected Production Area

Primary expected production area:

`src/seestar_toolkit/archive/discovery.py`

A small private helper is acceptable.

Changes outside discovery are permitted only if directly required and must be justified in the completion report.

Do not redesign the discovery data model.

## Regression Test Strategy

### RF8-03A — Mosaic Product Directory

Create generated temporary FITS evidence under:

`Target_mosaic/`

with:

`OBJECT=Target`

Expected:

- no directory/FITS target mismatch diagnostic;
- original directory/path remains unchanged;
- metadata target remains `Target`.

### RF8-03B — Mosaic Subdirectory

Create generated temporary FITS evidence under:

`Target_mosaic_sub/`

with:

`OBJECT=Target`

Expected:

- no false target mismatch diagnostic;
- classification/discovery remains otherwise unchanged.

### RF8-03C — Genuine Mismatch

Create evidence:

directory:

`Target A_mosaic`

FITS:

`OBJECT=Target B`

Expected:

- mismatch diagnostic remains;
- normalization must not suppress a genuine difference.

### RF8-03D — Ordinary Target Containing Mosaic Text

Create a non-structural target name containing the word `mosaic`, for example:

`Mosaic Galaxy`

Expected:

- target remains unchanged;
- no broad string replacement occurs.

If a form ending literally in `_mosaic` could itself be a legitimate astronomical target name, document that this Stage 8 policy intentionally treats the exact Seestar structural suffix as filesystem syntax when it appears in the relevant Seestar directory context.

### F8-01 / F8-02 Non-Regression

Existing equal-time and timestamp diagnostic regression coverage must remain passing.

## Real-Data Qualification

Qualification must remain read-only.

Validate all explicit mosaic datasets:

### Dataset 02

`<private-test-data>/dataset_02_fw846_altaz_unknown_mosaic_single`

Expected:

- one COMPLETE observation;
- 13 lights;
- correct stack;
- target remains `Unknown`;
- F8-02 warnings remain zero;
- F8-03 false mosaic warnings become zero;
- archive plan remains one observation.

### Dataset 05

`<private-test-data>/dataset_05_fw931_altaz_ngc6888_mosaic_single`

Expected:

- one COMPLETE observation;
- 12 lights;
- correct stack;
- F8-03 false mosaic warnings become zero;
- archive plan remains one observation.

### Dataset 07

`<private-test-data>/dataset_07_fw775_eq_ic5070_mosaic_single`

Expected:

- one COMPLETE observation;
- 77 lights;
- correct stack;
- firmware 7.75 EQ behaviour remains intact;
- F8-03 false mosaic warnings become zero;
- archive plan remains one observation.

Dataset 07 is the key proof that diagnostic cleanup does not alter previously correct reconstruction.

### Dataset 09

`<private-test-data>/dataset_09_fw931_eq_ngc281w_mosaic_single`

Expected:

- one COMPLETE observation;
- 12 lights;
- correct stack;
- Stage 8.2a equal-time fix remains intact;
- F8-03 false mosaic warnings become zero;
- archive plan remains one observation.

### Representative Non-Mosaic Checks

At minimum verify:

- Dataset 01 remains correct;
- Dataset 08 remains three COMPLETE observations with 12 / 1 / 135 lights.

A full nine-dataset sweep is welcome if practical but is not required if the focused evidence is sufficient and repository tests provide broad protection.

## Dataset Preservation

Do not:

- modify;
- rename;
- move;
- copy external datasets into the repository;
- execute archive COPY or MOVE.

Record that all real-data qualification was read-only.

## Diagnostics Expected To Remain

After Stage 8.2c:

### F8-04

Dataset 08 Session 03 retained-source versus accepted-stack-count diagnostic remains until Stage 8.2d.

### Genuine Target Mismatches

A real normalized directory/FITS logical target mismatch must continue to produce a diagnostic.

The goal is not to suppress target mismatch diagnostics generally.

## Exclusions

Stage 8.2c must not:

- remediate F8-04;
- alter F8-01 equal-time ordering;
- alter F8-02 timestamp semantics;
- add typed mosaic evidence;
- infer mosaic state from dimensions;
- infer mosaic state from WCS;
- change reconstruction grouping;
- change cadence thresholds;
- change `STACKCNT` semantics;
- change archive hierarchy;
- change observation numbering;
- change +12-hour archive-date logic;
- add target correction/override;
- broaden target normalization beyond recognized structural suffixes;
- copy full real datasets into the repository;
- execute archive COPY/MOVE;
- begin Stage 8.2d;
- include unrelated refactors or cleanup.

## Implementation Guidance

Prefer a small explicit helper with clear suffix semantics.

The helper should be easy to test independently.

Normalization should be used only where directory-derived target identity is compared with FITS target identity.

Do not mutate stored source evidence merely to make the diagnostic disappear.

The original path and directory context should remain available for diagnostics, indexing and future typed mosaic work.

## Validation

Run focused tests first.

Then run:

`python -m pytest`

`ruff check .`

`git diff --check`

If Python files change, run project-standard formatting validation.

Then perform the required read-only real-data qualification.

## Completion Report

Return a complete Stage 8.2c completion report containing:

### Stage 8.2c Result

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

Identify the exact comparison/path generating F8-03.

### Normalization Policy

Explain precisely:

- recognized suffixes;
- where normalization is applied;
- which values remain preserved;
- why genuine mismatches still work.

### Files Changed

List every changed file.

### Tests Added/Modified

Describe each regression.

### Focused Automated Validation

Report focused test results.

### Full Repository Validation

Report:

- pytest;
- Ruff;
- formatting check;
- `git diff --check`.

### Real-Data Qualification

Report Datasets 02, 05, 07 and 09 individually.

Include:

- observation count;
- status;
- light membership;
- stack;
- logical target;
- F8-03 diagnostic count after remediation;
- archive-plan count.

### Representative Non-Mosaic Validation

Report Dataset 01 and Dataset 08 results.

### Deferred Findings

Explicitly confirm F8-04 was not remediated and Stage 8.2d was not started.

### Dataset Preservation

Confirm no real dataset mutation/copy/archive operation occurred.

### Git Diff Summary

Confirm no unrelated changes.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.2c is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `a5fda62` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. The precise F8-03 diagnostic root cause is confirmed.
4. The implementation is scoped to F8-03 only.
5. `_mosaic` is recognized as structural suffix syntax for target comparison.
6. `_mosaic_sub` is recognized as structural source-directory syntax for target comparison.
7. Suffix handling is exact/structural rather than arbitrary substring replacement.
8. Original source paths remain unchanged.
9. Original directory evidence remains available.
10. FITS logical target evidence remains unchanged.
11. Matching `Target_mosaic` versus FITS `Target` no longer warns.
12. Matching `Target_mosaic_sub` versus FITS `Target` no longer warns.
13. A genuine normalized directory/FITS target mismatch still warns.
14. An ordinary target containing the word `mosaic` is not incorrectly rewritten.
15. No typed mosaic field is introduced.
16. Mosaic status is not inferred from dimensions.
17. Mosaic status is not inferred from WCS.
18. Mosaic status is not used to change reconstruction grouping.
19. Focused regression covers `_mosaic`.
20. Focused regression covers `_mosaic_sub`.
21. Focused regression covers a genuine mismatch.
22. Focused regression covers non-structural use of `mosaic` text.
23. Existing F8-01 equal-time regression remains passing.
24. Existing F8-02 timestamp regression remains passing.
25. Dataset 02 remains exactly one observation.
26. Dataset 02 remains COMPLETE.
27. Dataset 02 retains all 13 lights.
28. Dataset 02 uses the correct stack.
29. Dataset 02 target remains legitimate `Unknown`.
30. Dataset 02 F8-02 warnings remain zero.
31. Dataset 02 F8-03 false warnings become zero.
32. Dataset 02 archive plan remains one observation.
33. Dataset 05 remains exactly one observation.
34. Dataset 05 remains COMPLETE.
35. Dataset 05 retains all 12 lights.
36. Dataset 05 uses the correct stack.
37. Dataset 05 F8-03 false warnings become zero.
38. Dataset 05 archive plan remains one observation.
39. Dataset 07 remains exactly one observation.
40. Dataset 07 remains COMPLETE.
41. Dataset 07 retains all 77 lights.
42. Dataset 07 uses the correct stack.
43. Dataset 07 firmware 7.75 behaviour remains intact.
44. Dataset 07 EQ behaviour remains intact.
45. Dataset 07 F8-03 false warnings become zero.
46. Dataset 07 archive plan remains one observation.
47. Dataset 09 remains exactly one observation.
48. Dataset 09 remains COMPLETE.
49. Dataset 09 retains all 12 lights.
50. Dataset 09 uses the correct stack.
51. Dataset 09 F8-03 false warnings become zero.
52. Dataset 09 archive plan remains one observation.
53. Dataset 01 remains correctly reconstructed.
54. Dataset 01 remains free of F8-02 false timestamp warnings.
55. Dataset 08 remains exactly three observations.
56. All three Dataset 08 observations remain COMPLETE.
57. Dataset 08 memberships remain 12, 1 and 135.
58. Dataset 08 stack memberships remain correct.
59. Dataset 08 archive planning remains three observations.
60. Dataset 08 +12-hour archive date remains correct.
61. Dataset 08 F8-04 diagnostic remains.
62. Cross-midnight behaviour remains unchanged.
63. Large-gap stack-backed behaviour remains unchanged.
64. Intermediate-stack boundaries remain unchanged.
65. F8-01 remains fixed for Datasets 02, 05 and 09.
66. F8-02 remains fixed across the previously validated evidence.
67. No observation membership changes are introduced by F8-03 remediation.
68. No observation-count changes are introduced by F8-03 remediation.
69. Legitimate `Unknown` remains supported.
70. AltAz support remains intact.
71. EQ support remains intact.
72. Firmware 7.75, 8.46 and 9.31 compatibility remains intact.
73. RGB stack classification despite `BAYERPAT=GRBG` remains intact.
74. Timestamp precedence remains unchanged.
75. Filename fallback remains unchanged.
76. Cadence/grouping thresholds remain unchanged.
77. `STACKCNT` semantics remain unchanged.
78. No retained-light-count-equals-STACKCNT assumption is introduced.
79. F8-04 is not remediated.
80. No target correction/override is added.
81. Archive hierarchy remains unchanged.
82. Observation numbering remains unchanged.
83. +12-hour archive-date policy remains unchanged.
84. No complete real dataset is copied into the repository.
85. No archive COPY or MOVE operation is executed.
86. Real datasets used for qualification remain unchanged.
87. Full repository pytest passes.
88. Ruff passes.
89. `git diff --check` passes.
90. Formatting validation passes where applicable.
91. Every changed file is identified.
92. No unrelated production refactor or cleanup is included.
93. The completion report clearly distinguishes F8-03 remediation from deferred F8-04.
94. Evidence is sufficient to proceed to Stage 8.2d without reopening F8-03 design.

## Expected Next Stage

After Stage 8.2c is reviewed, committed and documented, proceed to:

**Stage 8.2d — Correct Stack-Count Diagnostic Semantics**

Stage 8.2d will address F8-04 only.
