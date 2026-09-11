# Stage 8.2a — Correct Equal-Time Reconstruction Ordering

## Status

START

## Purpose

Remediate confirmed Stage 8 finding **F8-01**:

> When a compatible final light and its stack have exactly the same authoritative FITS timestamp, current deterministic ordering may process the stack first because path ordering is used as the tie-breaker. The stack then closes the observation before the final light is seen, and the final light becomes a separate LIGHTS_ONLY observation.

This defect is confirmed in:

- Dataset 02;
- Dataset 05;
- Dataset 09.

Stage 8.2a must correct this reconstruction behaviour while preserving all known-good Stage 8.1 behaviour.

This is the first Stage 8 remediation sub-stage.

## Starting Commit

Expected starting commit:

`e1a00f2` — Stage 8.1e: consolidate Stage 8.1 discrepancies

Before implementation begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.1e entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.2a.md` document may also be present as an intentional uncommitted documentation change.

## Authoritative Finding

### F8-01 — Equal-Time Reconstruction Ordering

Classification:

`RECONSTRUCTION`

Severity:

`High`

Priority:

`P1`

Observed behaviour:

- selected FITS timestamp is authoritative;
- light and stack can legitimately share exactly the same selected timestamp;
- current ordering is effectively based on selected timestamp plus path;
- product-directory stack paths may sort before `_sub` light paths;
- stack therefore closes the observation before the equal-time final light is processed;
- the final light becomes a separate `LIGHTS_ONLY` observation;
- archive planning inherits an extra observation;
- associated-light count becomes one lower than the actual source-light membership;
- secondary stack-count and missing-stack diagnostics may appear.

Confirmed affected datasets:

- Dataset 02;
- Dataset 05;
- Dataset 09.

No non-equal final-light/stack case produced this defect during Stage 8.1 validation.

## Required Behaviour

The fix must preserve authoritative timestamp ordering while adding semantic handling for exact timestamp ties.

At an equal selected timestamp:

1. compatible light evidence that belongs to a stack must be considered before that stack closes the observation;
2. incompatible equal-time lights must not be consumed by that stack;
3. path ordering may remain a deterministic secondary mechanism, but must not decide light-versus-stack semantic precedence;
4. separate equal-time stacks must remain deterministic;
5. genuinely later lights must not be assigned backward to an earlier stack;
6. already-correct non-equal ordering must remain unchanged.

The implementation should be as narrow as practical.

Do not redesign reconstruction beyond what F8-01 requires.

## Non-Regression Requirements

Stage 8.2a must protect all known-correct Stage 8.1 behaviour.

### Single-Observation Datasets

Datasets 01, 03, 04, 06 and 07 must remain correctly reconstructed.

### Dataset 08 Multi-Session Behaviour

All three Dataset 08 observations must remain distinct and COMPLETE.

Specifically preserve:

- observation 1: 12 lights plus its stack;
- observation 2: 1 light plus its stack;
- observation 3: 135 lights plus its stack;
- intermediate stacks remain valid observation boundaries;
- shared target/filter/EQ/telescope metadata must not cause observation merging;
- the cross-midnight observation remains intact;
- the 221.936-second retained-light gap remains valid within the stack-closed observation;
- Session 03 retains all 135 source lights despite `STACKCNT=106`.

### Timestamp Behaviour

Preserve:

- FITS timestamps remain authoritative;
- filename timestamps remain fallback evidence;
- existing timestamp-conflict diagnostic semantics remain unchanged during Stage 8.2a.

F8-02 belongs to Stage 8.2b.

### Mosaic Behaviour

Do not modify:

- `_mosaic` target comparison;
- directory/FITS target diagnostics;
- typed mosaic representation.

F8-03 belongs to Stage 8.2c.

### Stack Count Behaviour

Do not modify:

- current `STACKCNT` diagnostic semantics;
- `STACKCNT` interpretation;
- associated-light mismatch diagnostics except where they naturally disappear because membership is now correct.

F8-04 belongs to Stage 8.2d.

### Archive Behaviour

Do not change archive planning rules directly.

Archive planning should improve only as a downstream consequence of corrected reconstruction.

Preserve:

- +12-hour astronomical-night/archive-date rule;
- observation numbering;
- target/location/GPS behaviour;
- read-only planning semantics.

### Other Established Behaviour

Preserve:

- legitimate target `Unknown`;
- AltAz and EQ compatibility;
- firmware 7.75, 8.46 and 9.31;
- RGB stack classification even where `BAYERPAT=GRBG`;
- no assumption that retained-light count equals `STACKCNT`;
- no calendar-date-only observation splitting.

## Scope

Stage 8.2a includes:

1. inspect current reconstruction ordering implementation;
2. identify the precise equal-time ordering point responsible for F8-01;
3. add focused automated regression coverage;
4. implement the smallest production change that provides semantic light-before-stack treatment for valid equal-time ties;
5. preserve deterministic behaviour;
6. verify incompatible equal-time light handling;
7. verify later-light non-backward-assignment;
8. verify multi-stack determinism if the implementation path could affect it;
9. verify Dataset 08-style multi-session behaviour using compact regression coverage;
10. run full repository quality gates;
11. run read-only real-data qualification against Datasets 02, 05 and 09 after unit/integration tests pass;
12. run a focused read-only non-regression check against Dataset 08.

## Expected Production Area

Primary expected implementation area:

`src/seestar_toolkit/archive/reconstruction.py`

Changes outside this area are permitted only if directly required by the narrow fix and must be justified in the completion report.

Do not alter unrelated modules opportunistically.

## Regression Test Strategy

### RF8-01 — Equal-Time Ordering

Add a minimal regression scenario containing:

- at least one earlier compatible light;
- one final compatible light;
- one stack;
- final compatible light and stack sharing exactly the same authoritative selected timestamp;
- path names/order that reproduce the prior stack-before-light lexical ordering.

Expected result:

- one COMPLETE observation;
- all compatible lights associated;
- no trailing LIGHTS_ONLY observation;
- stack assigned correctly.

### Incompatible Equal-Time Light

Add a case with an equal-time light that is incompatible with the stack by one established compatibility dimension, such as:

- target;
- exposure;
- filter;
- EQ mode.

Expected result:

- incompatible light is not consumed by the stack;
- compatible light membership remains correct;
- deterministic output remains stable.

### Later-Light Protection

Add coverage proving that a genuinely later light is not pulled backward into an earlier stack merely because semantic ordering changed.

### Multiple Equal-Time Stack Determinism

If the implementation can affect multiple equal-time stacks, add focused coverage demonstrating deterministic and correct behaviour.

If existing architecture makes this impossible or irrelevant, document why.

### RF8-05 — Compact Multi-Session Protection

Add a compact synthetic reconstruction scenario representing the important Dataset 08 properties:

- multiple stacks;
- repeated compatible metadata;
- clear session boundaries;
- at least one later session;
- no accidental merge caused by tie-ordering changes.

This does not need to reproduce every Dataset 08 file.

It should protect the reconstruction invariant that intermediate stacks remain observation boundaries.

### FITS Integration Coverage

Where practical, add a generated temporary Astropy FITS integration test that exercises discovery-to-reconstruction behaviour for an equal-time light/stack case.

Do not commit a large binary dataset.

Generated temporary FITS is preferred.

## Real-Data Qualification

After automated tests pass, perform read-only qualification using:

### Dataset 02

`<private-test-data>/dataset_02_fw846_altaz_unknown_mosaic_single`

Expected after fix:

- exactly 1 observation;
- status COMPLETE;
- all 13 retained lights associated;
- correct stack;
- no extra LIGHTS_ONLY observation;
- archive planning produces one observation.

Do not remediate its timestamp or mosaic diagnostics during this stage.

### Dataset 05

`<private-test-data>/dataset_05_fw931_altaz_ngc6888_mosaic_single`

Expected after fix:

- exactly 1 observation;
- status COMPLETE;
- all 12 retained lights associated;
- correct stack;
- no extra LIGHTS_ONLY observation;
- archive planning produces one observation.

Do not remediate its timestamp or mosaic diagnostics during this stage.

### Dataset 09

`<private-test-data>/dataset_09_fw931_eq_ngc281w_mosaic_single`

Expected after fix:

- exactly 1 observation;
- status COMPLETE;
- all 12 retained lights associated;
- correct stack;
- no extra LIGHTS_ONLY observation;
- archive planning produces one observation.

Do not remediate its timestamp or mosaic diagnostics during this stage.

### Dataset 08 Focused Non-Regression

`<private-test-data>/dataset_08_fw931_eq_m57_three_sessions`

Expected:

- exactly 3 observations;
- all COMPLETE;
- light membership 12, 1 and 135;
- correct stacks;
- no merge/split regression;
- archive planning remains 3 observations;
- +12-hour archive date remains correct.

Do not repeat full Stage 8.1d characterisation unless required to investigate a regression.

## Dataset Preservation

Any real-data qualification must remain read-only.

For Datasets 02, 05, 09 and 08:

- do not modify;
- do not rename;
- do not move;
- do not copy into the repository;
- do not execute archive COPY or MOVE.

Use preservation manifests before/after if the qualification procedure writes or traverses in a way where verification is useful.

At minimum state explicitly that no dataset mutation occurred.

## Diagnostics Expected To Remain

After F8-01 is fixed, these findings are still expected until later stages:

### F8-02

Local filename versus UTC FITS timestamp conflict diagnostics.

### F8-03

`_mosaic` directory/FITS target disagreement diagnostics on mosaic datasets.

### F8-04

Dataset 08 Session 03 retained-source versus `STACKCNT` diagnostic.

Their continued presence is not a Stage 8.2a failure.

A stack-count/missing-stack warning that existed only because F8-01 mis-associated the final light should disappear naturally once membership is corrected.

## Exclusions

Stage 8.2a must not:

- remediate F8-02;
- remediate F8-03;
- remediate F8-04;
- change timestamp precedence;
- change filename/FITS timezone interpretation;
- change timestamp-conflict thresholds;
- change cadence thresholds;
- change missing-stack fallback grouping;
- change `STACKCNT` semantics;
- introduce retained-light count equality with `STACKCNT`;
- add typed mosaic metadata;
- add target correction/override;
- alter archive hierarchy;
- alter +12-hour archive-date logic;
- redesign session terminology;
- copy complete real datasets into the repository;
- create large permanent FITS fixtures;
- execute archive COPY/MOVE;
- begin Stage 8.2b;
- make unrelated cleanup/refactors.

## Implementation Guidance

Prefer an explicit semantic ordering rule over path-name tricks.

Avoid solving the defect by special-casing known filenames or directories.

The solution should operate on discovered/reconstructed item semantics.

The implementation should remain deterministic.

If equal-time grouping is introduced, its ordering and compatibility rules must be explicit and testable.

## Validation

Run focused tests first.

Then run:

`python -m pytest`

`ruff check .`

`git diff --check`

If Python files are changed, run the project-standard formatting validation if applicable.

Perform the required read-only real-data qualification after automated tests pass.

## Completion Report

Return a complete Stage 8.2a report containing:

### Stage 8.2a Result

Use:

- PASS;
- PASS WITH FINDINGS;
- FAIL.

### Environment

Record:

- HEAD;
- working-tree state;
- Python executable/version;
- import path.

### Root Cause Confirmation

Describe the exact code path and ordering behaviour responsible for F8-01.

### Files Changed

List every source/test/documentation file changed.

### Tests Added/Modified

Describe:

- equal-time regression coverage;
- incompatible equal-time light coverage;
- later-light protection;
- multi-stack determinism coverage or justification;
- Dataset 08-style compact multi-session coverage;
- FITS integration coverage if added.

### Implementation

Describe the production change precisely.

### Focused Automated Validation

Report focused test results.

### Full Repository Validation

Report:

- pytest;
- Ruff;
- `git diff --check`;
- formatting validation where applicable.

### Real-Data Qualification

Report Datasets 02, 05 and 09 individually.

For each record:

- observation count;
- status;
- light membership;
- stack;
- equal-timestamp relationship;
- archive-plan observation count;
- whether expected unrelated diagnostics remain.

### Dataset 08 Non-Regression

Record:

- three COMPLETE observations;
- 12/1/135 light membership;
- stack membership;
- archive-plan count;
- +12-hour archive date;
- any regression.

### Deferred Findings

Explicitly confirm that F8-02, F8-03 and F8-04 were not remediated.

### Dataset Preservation

Confirm real datasets remained unchanged.

### Git Diff Summary

Summarise production/test changes and confirm no unrelated changes.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.2a is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `e1a00f2` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. The precise F8-01 ordering root cause is confirmed in current code.
4. The implementation remains narrowly scoped to F8-01.
5. FITS timestamps remain authoritative.
6. Equal-time compatible light evidence is considered before the stack closes its observation.
7. Path lexical ordering no longer determines semantic light-versus-stack precedence.
8. Incompatible equal-time lights are not consumed by the stack.
9. Genuinely later lights are not assigned backward to an earlier stack.
10. Reconstruction remains deterministic.
11. Multiple equal-time stack behaviour is tested or explicitly shown not to require additional coverage.
12. A focused automated regression reproduces the former equal-time failure.
13. That regression now produces one COMPLETE observation with full compatible membership.
14. No trailing LIGHTS_ONLY observation remains in the regression case.
15. An incompatible equal-time light regression is covered.
16. Later-light non-backward-assignment is covered.
17. Compact Dataset 08-style multi-session protection is covered.
18. Intermediate stack boundaries remain protected by tests.
19. Generated temporary FITS integration coverage is added where practical or omission is justified.
20. Dataset 02 reconstructs as exactly one observation.
21. Dataset 02 status is COMPLETE.
22. Dataset 02 contains all 13 retained lights.
23. Dataset 02 uses the correct stack.
24. Dataset 02 no longer produces the extra LIGHTS_ONLY observation.
25. Dataset 02 archive planning produces one observation.
26. Dataset 05 reconstructs as exactly one observation.
27. Dataset 05 status is COMPLETE.
28. Dataset 05 contains all 12 retained lights.
29. Dataset 05 uses the correct stack.
30. Dataset 05 no longer produces the extra LIGHTS_ONLY observation.
31. Dataset 05 archive planning produces one observation.
32. Dataset 09 reconstructs as exactly one observation.
33. Dataset 09 status is COMPLETE.
34. Dataset 09 contains all 12 retained lights.
35. Dataset 09 uses the correct stack.
36. Dataset 09 no longer produces the extra LIGHTS_ONLY observation.
37. Dataset 09 archive planning produces one observation.
38. Dataset 08 still reconstructs as exactly three observations.
39. All three Dataset 08 observations remain COMPLETE.
40. Dataset 08 light memberships remain 12, 1 and 135.
41. Dataset 08 stack memberships remain correct.
42. Dataset 08 observations are neither merged nor split.
43. Dataset 08 archive planning remains three observations.
44. Dataset 08 +12-hour archive date remains correct.
45. Dataset 08 Session 03 retains all 135 source lights.
46. Large-gap stack-backed behaviour remains unchanged.
47. Cross-midnight behaviour remains unchanged.
48. Intermediate-stack session separation remains unchanged.
49. Legitimate `Unknown` target behaviour remains unchanged.
50. AltAz and EQ compatibility remain unchanged.
51. Firmware 7.75, 8.46 and 9.31 compatibility remains unchanged.
52. RGB stack classification despite `BAYERPAT=GRBG` remains unchanged.
53. Timestamp diagnostic semantics F8-02 are not remediated.
54. Mosaic diagnostic semantics F8-03 are not remediated.
55. Stack-count diagnostic semantics F8-04 are not remediated.
56. Timestamp precedence is not changed.
57. Timestamp-conflict threshold is not changed.
58. Cadence/grouping thresholds are not changed.
59. `STACKCNT` interpretation is not changed.
60. No retained-light-count-equals-STACKCNT assumption is introduced.
61. No typed mosaic field is added.
62. No target correction/override capability is added.
63. Archive hierarchy and +12-hour date policy are not changed.
64. No complete real dataset is copied into the repository.
65. No archive COPY or MOVE operation is executed.
66. Real datasets used for qualification remain unchanged.
67. Full repository pytest passes.
68. Ruff passes.
69. `git diff --check` passes.
70. Formatting validation passes where applicable.
71. Every changed file is identified.
72. No unrelated production refactor or cleanup is included.
73. The completion report explicitly distinguishes F8-01 remediation from still-deferred F8-02/F8-03/F8-04.
74. Evidence is sufficient to proceed to Stage 8.2b without reopening F8-01 design.

## Expected Next Stage

After Stage 8.2a is reviewed, committed and documented, proceed to:

**Stage 8.2b — Correct Filename/FITS Diagnostic Semantics**

Stage 8.2b will address F8-02 only.
