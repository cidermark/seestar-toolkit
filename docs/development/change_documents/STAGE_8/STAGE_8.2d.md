# Stage 8.2d — Correct Stack-Count Diagnostic Semantics

## Status

START

## Purpose

Remediate confirmed Stage 8 finding **F8-04**:

> The Toolkit currently treats `STACKCNT` as though it should equal the number of retained source-light FITS files reconstructed into an observation.

Stage 8 real-data evidence shows that assumption is invalid.

Dataset 08 Session 03 contains:

- 135 retained 30-second light FITS files;
- `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`.

The internally consistent stack relationship is:

`STACKCNT == TOTALEXP / EXPTIME == 106`

while the number of retained source-light files is 135.

Stage 8.2d must correct the diagnostic semantics without changing reconstruction membership.

This is a metadata/diagnostic remediation stage only.

## Starting Commit

Expected starting commit:

`25587ef` — Stage 8.2c: normalize mosaic target comparison

Before implementation begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.2c entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.2d.md` document may also be present as an intentional uncommitted documentation change.

## Authoritative Finding

### F8-04 — Retained-Light Count vs STACKCNT Diagnostic

Classification:

`DIAGNOSTIC`

Severity:

`Low`

Priority:

`P2`

Primary evidence:

Dataset 08, Session 03.

Observed values:

- retained source lights: 135;
- stack filename count: 106;
- FITS `STACKCNT`: 106;
- FITS `TOTALEXP`: 3180 seconds;
- exposure: 30 seconds.

Confirmed Stage 8 evidence:

`3180 / 30 = 106`

Therefore `STACKCNT` is consistent with accepted/integrated stack exposures, not necessarily with the number of retained source FITS files present in the capture directory.

The existing warning that assumes `retained_light_count == STACKCNT` is therefore semantically invalid.

## Required Behaviour

### Retained Source Count

The Toolkit must continue to count all compatible retained source-light FITS files reconstructed into an observation.

Dataset 08 Session 03 must remain:

`135 retained lights`

Do not truncate or select exactly `STACKCNT` lights.

### STACKCNT

Preserve `STACKCNT` as stack metadata.

Do not redefine it as the retained source-file count.

Where current metadata exposes a reported stack count, that value should remain available.

### TOTALEXP / EXPTIME Relationship

Where all required values are present and valid, a useful internal consistency relationship may be checked:

`STACKCNT == TOTALEXP / EXPTIME`

Use a numerically appropriate comparison.

Do not manufacture values when metadata is missing.

Do not require this diagnostic if the current model lacks one or more values.

### Diagnostic Semantics

Remove or replace diagnostics that claim a mismatch solely because:

`retained source-light count != STACKCNT`

A difference between those values is not inherently erroneous.

If the Toolkit retains a diagnostic involving stack count, it must describe a genuinely meaningful inconsistency, such as contradictory stack metadata.

### Reconstruction Independence

`STACKCNT` must never be used to choose exactly N source lights for an observation.

Observation reconstruction remains driven by timestamp/order/compatibility/stack boundaries under the existing architecture.

## Non-Regression Requirements

### Stage 8.2a

Preserve:

- semantic light-before-stack equal-time ordering;
- Dataset 02: 1 COMPLETE / 13 lights;
- Dataset 05: 1 COMPLETE / 12 lights;
- Dataset 09: 1 COMPLETE / 12 lights.

### Stage 8.2b

Preserve:

- FITS timestamp authority;
- filename fallback;
- zero false F8-02 warnings across characterised datasets.

### Stage 8.2c

Preserve:

- structural `_mosaic` comparison normalization;
- zero false F8-03 warnings on Datasets 02, 05, 07 and 09;
- original path/evidence preservation.

### Dataset 08

Preserve exactly:

Observation 1:
- COMPLETE;
- 12 lights;
- first stack.

Observation 2:
- COMPLETE;
- 1 light;
- second stack.

Observation 3:
- COMPLETE;
- 135 retained lights;
- third stack;
- `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`.

Also preserve:

- cross-midnight continuity;
- large retained-light gap;
- intermediate stack boundaries;
- archive planning as three observations;
- archive date `20260907`.

## Scope

Stage 8.2d includes:

1. inspect where retained-light count and reported stack count are compared;
2. identify the exact code path producing F8-04;
3. remove the invalid retained-count-equals-STACKCNT assumption;
4. preserve reported stack-count metadata;
5. add or refine a meaningful stack metadata consistency diagnostic where appropriate;
6. add focused tests;
7. ensure reconstruction never truncates membership to STACKCNT;
8. run full repository validation;
9. perform real-data qualification, especially Dataset 08;
10. verify prior Stage 8 fixes remain intact.

## Expected Production Area

Likely implementation area:

`src/seestar_toolkit/archive/reconstruction.py`

or whichever module currently owns the stack-count mismatch diagnostic.

Changes elsewhere are allowed only if directly required and must be justified.

Do not redesign the observation model unless strictly necessary for the narrow diagnostic correction.

## Regression Test Strategy

### RF8-04A — Retained Count Greater Than STACKCNT

Synthetic observation evidence:

- 135 compatible retained lights;
- stack metadata `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`.

Expected:

- one COMPLETE observation;
- all 135 retained lights remain;
- stack count remains 106;
- no warning solely because 135 != 106.

### RF8-04B — Internal Stack Metadata Consistency

Where practical, test:

- `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`.

Expected:

- no stack metadata inconsistency diagnostic.

### RF8-04C — Internal Stack Metadata Contradiction

Where practical, create contradictory metadata, for example:

- `STACKCNT=106`;
- `TOTALEXP=3000`;
- `EXPTIME=30`.

Expected:

- a meaningful diagnostic remains or is introduced if current architecture supports it;
- reconstruction membership remains unaffected.

If implementing this diagnostic would broaden scope unnecessarily, document why the correct Stage 8.2d fix is simply removal of the invalid retained-count comparison.

### RF8-04D — Retained Count Less Than STACKCNT

Create a synthetic case where retained source-light count is less than reported `STACKCNT`.

Expected:

- do not fabricate missing lights;
- do not consume unrelated lights;
- do not force equality;
- no warning solely from retained-count inequality unless another independent inconsistency exists.

### RF8-04E — No STACKCNT

Where stack-count metadata is absent:

- reconstruction must continue according to existing rules;
- no new requirement for STACKCNT may be introduced.

### Prior-Stage Protection

Existing F8-01, F8-02 and F8-03 tests must remain passing.

## Real-Data Qualification

All qualification must remain read-only.

### Dataset 08 — Primary Qualification

Path:

`<private-test-data>/dataset_08_fw931_eq_m57_three_sessions`

Expected:

- exactly three observations;
- all COMPLETE;
- memberships remain 12 / 1 / 135;
- correct stacks remain assigned;
- Session 03 retains all 135 lights;
- Session 03 reported stack count remains 106;
- Session 03 `TOTALEXP` remains 3180;
- Session 03 exposure remains 30 seconds;
- former F8-04 retained-vs-STACKCNT diagnostic becomes zero;
- no new false diagnostic replaces it;
- F8-02 remains zero;
- archive planning remains exactly three observations;
- all archive dates remain `20260907`.

### Dataset 02

Expected:

- 1 COMPLETE;
- 13 lights;
- F8-01 remains fixed;
- F8-02 remains zero;
- F8-03 remains zero.

### Dataset 05

Expected:

- 1 COMPLETE;
- 12 lights;
- F8-01 remains fixed;
- F8-02 remains zero;
- F8-03 remains zero.

### Dataset 07

Expected:

- 1 COMPLETE;
- 77 lights;
- firmware 7.75 EQ behaviour intact;
- F8-03 remains zero.

### Dataset 09

Expected:

- 1 COMPLETE;
- 12 lights;
- F8-01 remains fixed;
- F8-03 remains zero.

### Optional Full Nine-Dataset Sweep

A full nine-dataset diagnostic/reconstruction sweep is strongly preferred if practical.

Expected:

- all 11 frozen observations still correct;
- F8-01 remains fixed;
- F8-02 remains zero;
- F8-03 remains zero on mosaic datasets;
- F8-04 becomes zero;
- no new regression diagnostics introduced by Stage 8.2d.

## Dataset Preservation

Do not:

- modify;
- rename;
- move;
- copy complete datasets into the repository;
- execute archive COPY or MOVE.

Record preservation evidence.

## Diagnostics Expected After Stage 8.2d

After this stage, all four confirmed Stage 8.1 remediation findings should be resolved:

- F8-01 — resolved;
- F8-02 — resolved;
- F8-03 — resolved;
- F8-04 — resolved.

Deferred features remain deferred:

- DF8-01 typed mosaic evidence;
- DF8-02 target correction/override.

Do not implement either deferred feature.

## Exclusions

Stage 8.2d must not:

- change F8-01 ordering logic;
- change F8-02 timestamp semantics;
- change F8-03 mosaic comparison semantics;
- use STACKCNT to select source-light membership;
- truncate retained lights;
- fabricate missing lights;
- alter cadence/grouping thresholds;
- alter timestamp precedence;
- alter filename fallback;
- add typed mosaic metadata;
- add target correction/override;
- change archive hierarchy;
- change observation numbering;
- change +12-hour archive date;
- copy full datasets into the repository;
- execute archive COPY/MOVE;
- begin Stage 8.2e;
- include unrelated refactors or cleanup.

## Implementation Guidance

The important semantic separation is:

- **retained source-light count** = number of compatible source FITS files retained and reconstructed into the observation;
- **STACKCNT** = stack metadata describing accepted/integrated exposures;
- **TOTALEXP / EXPTIME** = useful check on stack metadata where valid.

These values may legitimately differ.

Do not collapse them into one concept.

If a diagnostic remains, phrase it according to the actual metadata relationship being checked.

## Validation

Run focused tests first.

Then:

`python -m pytest`

`ruff check .`

`git diff --check`

Run project-standard formatting validation for changed Python files.

Then perform the required read-only real-data qualification.

## Completion Report

Return a complete Stage 8.2d completion report containing:

### Stage 8.2d Result

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

Identify the exact invalid retained-count/STACKCNT comparison.

### Semantic Policy

Explain:

- retained source count semantics;
- STACKCNT semantics;
- TOTALEXP/EXPTIME relationship;
- what diagnostic was removed/replaced;
- why reconstruction remains independent.

### Files Changed

List every changed file.

### Tests Added/Modified

Describe focused regressions.

### Focused Validation

Report focused tests.

### Full Validation

Report:

- pytest;
- Ruff;
- formatting;
- `git diff --check`.

### Real-Data Qualification

Report Dataset 08 in detail.

Also report representative prior-fix datasets 02, 05, 07 and 09.

If a full nine-dataset sweep is performed, report it.

### Deferred Features

Confirm DF8-01 and DF8-02 remain deferred.

### Dataset Preservation

Confirm read-only qualification.

### Git Diff Summary

Confirm no unrelated changes.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.2d is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `25587ef` or difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. The exact F8-04 root cause is confirmed.
4. The implementation is scoped to F8-04 only.
5. Retained source-light count remains a distinct concept.
6. `STACKCNT` remains a distinct stack metadata concept.
7. `STACKCNT` is not redefined as retained source-file count.
8. Reconstruction does not use STACKCNT to select exactly N lights.
9. Retained lights are not truncated to STACKCNT.
10. Missing source lights are not fabricated to satisfy STACKCNT.
11. The invalid retained-count-equals-STACKCNT diagnostic is removed or replaced.
12. A difference between retained count and STACKCNT alone is no longer diagnosed as erroneous.
13. `TOTALEXP / EXPTIME` is recognized as relevant stack metadata evidence where valid.
14. No value is manufactured when required stack metadata is missing.
15. Numerically appropriate comparison is used if stack metadata consistency is checked.
16. A synthetic retained-count-greater-than-STACKCNT case is covered.
17. That case retains all source lights.
18. That case retains reported STACKCNT independently.
19. That case no longer emits the invalid mismatch diagnostic.
20. A consistent STACKCNT/TOTALEXP/EXPTIME case is covered or existing coverage is identified.
21. A contradictory stack metadata case is tested or omission is explicitly justified.
22. A retained-count-less-than-STACKCNT case is covered.
23. That case does not fabricate or consume unrelated lights.
24. Absence of STACKCNT remains supported.
25. F8-01 regressions remain passing.
26. F8-02 regressions remain passing.
27. F8-03 regressions remain passing.
28. Dataset 08 remains exactly three observations.
29. All three Dataset 08 observations remain COMPLETE.
30. Dataset 08 memberships remain 12, 1 and 135.
31. Dataset 08 correct stack assignments remain unchanged.
32. Dataset 08 Session 03 retains all 135 lights.
33. Dataset 08 Session 03 reported STACKCNT remains 106.
34. Dataset 08 Session 03 TOTALEXP remains 3180 seconds.
35. Dataset 08 Session 03 exposure remains 30 seconds.
36. Dataset 08 former F8-04 retained/count diagnostic becomes zero.
37. No new false Dataset 08 stack-count diagnostic replaces F8-04.
38. Dataset 08 F8-02 remains zero.
39. Dataset 08 cross-midnight behaviour remains intact.
40. Dataset 08 large-gap stack-backed behaviour remains intact.
41. Dataset 08 intermediate-stack boundaries remain intact.
42. Dataset 08 archive planning remains exactly three observations.
43. Dataset 08 archive dates remain 20260907.
44. Dataset 02 remains one COMPLETE observation.
45. Dataset 02 retains all 13 lights.
46. Dataset 02 F8-01 remains fixed.
47. Dataset 02 F8-02 remains zero.
48. Dataset 02 F8-03 remains zero.
49. Dataset 05 remains one COMPLETE observation.
50. Dataset 05 retains all 12 lights.
51. Dataset 05 F8-01 remains fixed.
52. Dataset 05 F8-02 remains zero.
53. Dataset 05 F8-03 remains zero.
54. Dataset 07 remains one COMPLETE observation.
55. Dataset 07 retains all 77 lights.
56. Dataset 07 firmware 7.75 behaviour remains intact.
57. Dataset 07 EQ behaviour remains intact.
58. Dataset 07 F8-03 remains zero.
59. Dataset 09 remains one COMPLETE observation.
60. Dataset 09 retains all 12 lights.
61. Dataset 09 F8-01 remains fixed.
62. Dataset 09 F8-02 remains zero.
63. Dataset 09 F8-03 remains zero.
64. No observation membership changes are introduced by F8-04 remediation.
65. No observation-count changes are introduced by F8-04 remediation.
66. Timestamp precedence remains unchanged.
67. Filename fallback remains unchanged.
68. Equal-time semantic ordering remains unchanged.
69. Mosaic comparison normalization remains unchanged.
70. Cadence/grouping thresholds remain unchanged.
71. Archive hierarchy remains unchanged.
72. Observation numbering remains unchanged.
73. +12-hour archive-date policy remains unchanged.
74. Legitimate `Unknown` remains supported.
75. AltAz support remains intact.
76. EQ support remains intact.
77. Firmware 7.75, 8.46 and 9.31 compatibility remains intact.
78. RGB stack classification despite `BAYERPAT=GRBG` remains intact.
79. DF8-01 typed mosaic evidence remains deferred.
80. DF8-02 target correction/override remains deferred.
81. No complete real dataset is copied into the repository.
82. No archive COPY or MOVE operation is executed.
83. Real datasets used for qualification remain unchanged.
84. Full repository pytest passes.
85. Ruff passes.
86. `git diff --check` passes.
87. Formatting validation passes where applicable.
88. Every changed file is identified.
89. No unrelated production refactor or cleanup is included.
90. Completion report clearly distinguishes F8-04 remediation from deferred features.
91. A full nine-dataset sweep is performed, or omission is explicitly justified.
92. Evidence is sufficient to proceed to Stage 8.2e without reopening F8-04 design.

## Expected Next Stage

After Stage 8.2d is reviewed, committed and documented, proceed to:

**Stage 8.2e — Full Real-Data Remediation Regression**

Stage 8.2e will validate all four Stage 8 remediation findings together across the frozen real-data corpus.
