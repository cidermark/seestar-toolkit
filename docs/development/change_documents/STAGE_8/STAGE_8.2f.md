# Stage 8.2f — Correct Mosaic Target Semantics in Archive Planning

## Status

PASS — implemented and qualified 2026-09-08; uncommitted.

## Purpose

Remediate the previously hidden Stage 8 defect exposed by the failed Stage 8.2e full regression:

> Stage 8.2c corrected structural `_mosaic` / `_mosaic_sub` target comparison during discovery, but archive planning still emits false mosaic target mismatch diagnostics for Datasets 02, 05, 07 and 09.

This is a narrow propagation/consistency defect.

Reconstruction is correct. Observation membership, stack assignment, archive counts and archive dates must remain unchanged.

The goal is to make archive-planning target comparison use the same logical structural-mosaic semantics already established by Stage 8.2c, without rewriting stored evidence or adding typed mosaic state.

## Starting Commit

Expected starting commit:

`02d92ce` — Stage 8.2d: correct stack-count diagnostic semantics

Stage 8.2e failed validation and must not be treated as a completed/committed stage.

Before implementation begins, record the actual Git `HEAD`.

Permitted pre-existing working-tree changes:

- `docs/CHANGELOG.md` containing the intentionally pending Stage 8.2d entry;
- `docs/change_documents/STAGE_8/STAGE_8.2e.md` containing the failed Stage 8.2e validation report;
- this new `docs/change_documents/STAGE_8/STAGE_8.2f.md`.

Any other pre-existing change must be identified and explained.

## Defect Classification

Finding:

**F8-03A — Archive-planning structural mosaic target diagnostic**

Classification:

`ARCHIVE / DIAGNOSTIC`

Severity:

`Low`

Priority:

`P1 for Stage 8 closure`

Evidence:

- Dataset 02;
- Dataset 05;
- Dataset 07;
- Dataset 09.

This is not a reconstruction defect.

It is a second code path applying target comparison semantics inconsistently with Stage 8.2c.

## Required Behaviour

Archive planning must treat Seestar structural target directory forms consistently with discovery:

- `<target>_mosaic` compares logically as `<target>`;
- `<target>_mosaic_sub` compares logically as `<target>` after existing `_sub` handling;
- normalization applies only to logical comparison;
- original source paths remain unchanged;
- original stored directory evidence remains unchanged;
- FITS `OBJECT` remains unchanged;
- archive target selection remains unchanged unless current architecture already selects from FITS metadata;
- genuine normalized mismatches must still diagnose.

Do not use arbitrary substring replacement.

Do not strip ordinary non-structural text containing `mosaic`.

## Architectural Requirement

Before changing code, identify the exact archive-planning path that reintroduces the false mismatch.

Prefer reuse of the Stage 8.2c comparison semantics rather than duplicating a subtly different normalization rule.

If the Stage 8.2c helper is currently private to discovery and cannot cleanly be reused, make the smallest architectural adjustment needed to provide one authoritative comparison-normalization rule.

Do not redesign the archive or discovery models.

## Non-Regression Requirements

Preserve all Stage 8.2a–8.2d behaviour.

### F8-01

- D02 — 1 COMPLETE / 13 lights
- D05 — 1 COMPLETE / 12 lights
- D09 — 1 COMPLETE / 12 lights
- no trailing LIGHTS_ONLY observations

### F8-02

- false filename/FITS timestamp diagnostics remain zero across the real corpus;
- FITS timestamp authority remains unchanged;
- filename fallback remains unchanged.

### F8-03 Discovery

- discovery-level false mosaic target diagnostics remain zero for D02/D05/D07/D09;
- original stored evidence remains preserved.

### F8-04

Dataset 08 Session 03 remains:

- 135 retained lights;
- `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`;
- no retained-count-vs-STACKCNT warning;
- no false replacement stack metadata warning.

## Focused Regression Strategy

### RF8-03A-1 — Archive Plan for Mosaic Product

Generated or synthetic discovery/reconstruction evidence representing:

- directory `Target_mosaic`;
- FITS `OBJECT=Target`.

Expected:

- archive planning succeeds;
- no false target mismatch problem;
- original source/directory evidence remains unchanged.

### RF8-03A-2 — Archive Plan for Mosaic Subdirectory

Represent:

- directory `Target_mosaic_sub`;
- FITS `OBJECT=Target`.

Expected:

- no false archive-planning target mismatch problem.

### RF8-03A-3 — Genuine Mismatch

Represent:

- directory `Target A_mosaic`;
- FITS `OBJECT=Target B`.

Expected:

- archive planning still exposes a meaningful target mismatch diagnostic/problem.

### RF8-03A-4 — Non-Structural Mosaic Text

Represent:

- directory `Mosaic Galaxy`;
- FITS `OBJECT=Mosaic Galaxy`.

Expected:

- name remains unchanged;
- no broad text rewriting.

### RF8-03A-5 — Discovery/Planning Consistency

For equivalent evidence, discovery and archive planning must agree on whether the directory-derived target and FITS target logically match.

## Real-Data Qualification

All qualification must be read-only.

Primary affected datasets:

### Dataset 02

Expected:

- reconstruction: 1 COMPLETE / 13 lights;
- logical target remains legitimate `Unknown`;
- discovery F8-03 diagnostics: 0;
- archive-planning false mosaic diagnostics/problems: 0;
- archive plan count: 1;
- archive date: `20260907`.

### Dataset 05

Expected:

- reconstruction: 1 COMPLETE / 12 lights;
- discovery F8-03 diagnostics: 0;
- archive-planning false mosaic diagnostics/problems: 0;
- archive plan count: 1;
- archive date: `20260907`.

### Dataset 07

Expected:

- reconstruction: 1 COMPLETE / 77 lights;
- firmware 7.75 EQ behaviour intact;
- discovery F8-03 diagnostics: 0;
- archive-planning false mosaic diagnostics/problems: 0;
- archive plan count: 1;
- archive date: `20260906`.

### Dataset 09

Expected:

- reconstruction: 1 COMPLETE / 12 lights;
- F8-01 equal-time fix intact;
- discovery F8-03 diagnostics: 0;
- archive-planning false mosaic diagnostics/problems: 0;
- archive plan count: 1;
- archive date: `20260907`.

Representative non-mosaic protection:

- Dataset 01 remains 1 COMPLETE / 18 lights / one plan dated `20260907`;
- Dataset 08 remains 3 COMPLETE / 12,1,135 / three plans all dated `20260907`.

A full nine-dataset sweep is strongly preferred.

## Dataset Preservation

Do not:

- modify;
- rename;
- move;
- delete;
- copy complete datasets into the repository;
- execute archive COPY;
- execute archive MOVE.

Record before/after preservation evidence.

## Exclusions

Do not:

- change reconstruction grouping;
- change equal-time ordering;
- change timestamp precedence;
- change filename fallback;
- add timezone inference;
- change STACKCNT semantics;
- add typed mosaic state;
- infer mosaic state from dimensions or WCS;
- add target correction/override;
- change archive hierarchy;
- change observation numbering;
- change +12-hour archive-date policy;
- broaden target normalization beyond recognized structural suffix semantics;
- opportunistically remediate unrelated findings;
- begin Stage 8 closure;
- commit changes.

## Validation

Run focused tests first.

Then run:

`python -m pytest`

`ruff check .`

`git diff --check`

Run project-standard formatting validation for changed Python files.

Then run the required real-data qualification.

## Completion Report

Return:

- result: PASS / PASS WITH FINDINGS / FAIL;
- environment and starting HEAD;
- exact root cause and archive-planning code path;
- implementation policy and any shared-helper decision;
- every changed file;
- focused tests;
- full pytest/Ruff/format/diff results;
- D02/D05/D07/D09 results;
- D01/D08 non-regression results;
- preferably the full nine-dataset sweep;
- confirmation that F8-01/F8-02/F8-03 discovery/F8-04 remain fixed;
- dataset preservation evidence;
- git status;
- all closure criteria below individually.

## Closure Criteria

1. Starting HEAD is recorded and matches `02d92ce` or any difference is explained.
2. Failed Stage 8.2e documentation is distinguished from production changes.
3. Pending CHANGELOG entry is correctly treated as intentional.
4. Exact archive-planning code path producing false mosaic diagnostics is identified.
5. The defect is confirmed as separate from reconstruction.
6. Implementation is scoped to archive-planning F8-03 semantics only.
7. `_mosaic` is treated structurally for archive target comparison.
8. `_mosaic_sub` is treated structurally for archive target comparison.
9. Normalization uses suffix semantics, not broad substring replacement.
10. Original source paths remain unchanged.
11. Original stored directory evidence remains unchanged.
12. FITS `OBJECT` remains unchanged.
13. Archive target selection semantics remain otherwise unchanged.
14. Genuine normalized target mismatches still diagnose.
15. Ordinary non-structural `mosaic` text remains unchanged.
16. Discovery and archive planning use consistent logical comparison semantics.
17. Stage 8.2c discovery-level behaviour remains intact.
18. No typed mosaic field is introduced.
19. No dimension-based mosaic inference is introduced.
20. No WCS-based mosaic inference is introduced.
21. Focused archive `_mosaic` regression passes.
22. Focused archive `_mosaic_sub` regression passes.
23. Focused genuine-mismatch regression passes.
24. Focused non-structural mosaic-text regression passes.
25. Discovery/planning consistency regression passes.
26. F8-01 regressions remain passing.
27. F8-02 regressions remain passing.
28. F8-03 discovery regressions remain passing.
29. F8-04 regressions remain passing.
30. Dataset 02 remains one COMPLETE observation.
31. Dataset 02 retains 13 lights.
32. Dataset 02 target remains `Unknown`.
33. Dataset 02 discovery F8-03 diagnostics remain zero.
34. Dataset 02 archive-planning false mosaic diagnostics become zero.
35. Dataset 02 archive plan count remains 1.
36. Dataset 02 archive date remains `20260907`.
37. Dataset 05 remains one COMPLETE observation.
38. Dataset 05 retains 12 lights.
39. Dataset 05 discovery F8-03 diagnostics remain zero.
40. Dataset 05 archive-planning false mosaic diagnostics become zero.
41. Dataset 05 archive plan count remains 1.
42. Dataset 05 archive date remains `20260907`.
43. Dataset 07 remains one COMPLETE observation.
44. Dataset 07 retains 77 lights.
45. Dataset 07 firmware 7.75 behaviour remains intact.
46. Dataset 07 EQ behaviour remains intact.
47. Dataset 07 discovery F8-03 diagnostics remain zero.
48. Dataset 07 archive-planning false mosaic diagnostics become zero.
49. Dataset 07 archive plan count remains 1.
50. Dataset 07 archive date remains `20260906`.
51. Dataset 09 remains one COMPLETE observation.
52. Dataset 09 retains 12 lights.
53. Dataset 09 F8-01 equal-time behaviour remains fixed.
54. Dataset 09 discovery F8-03 diagnostics remain zero.
55. Dataset 09 archive-planning false mosaic diagnostics become zero.
56. Dataset 09 archive plan count remains 1.
57. Dataset 09 archive date remains `20260907`.
58. Dataset 01 remains 1 COMPLETE / 18 lights.
59. Dataset 01 archive plan remains 1 dated `20260907`.
60. Dataset 08 remains exactly 3 COMPLETE observations.
61. Dataset 08 memberships remain 12 / 1 / 135.
62. Dataset 08 archive planning remains 3 observations.
63. Dataset 08 archive dates remain `20260907`.
64. Dataset 08 Session 03 retains 135 lights.
65. Dataset 08 STACKCNT remains 106.
66. Dataset 08 TOTALEXP remains 3180.
67. Dataset 08 EXPTIME remains 30.
68. Dataset 08 emits no F8-04 false diagnostic.
69. F8-02 remains zero across qualified datasets.
70. No observation membership changes are introduced.
71. No observation-count changes are introduced.
72. Timestamp precedence remains unchanged.
73. Filename fallback remains unchanged.
74. Equal-time semantic ordering remains unchanged.
75. STACKCNT remains independent of source membership.
76. Cadence/grouping thresholds remain unchanged.
77. Archive hierarchy remains unchanged.
78. Observation numbering remains unchanged.
79. +12-hour archive-date policy remains unchanged.
80. DF8-01 typed mosaic evidence remains deferred.
81. DF8-02 target correction/override remains deferred.
82. No complete external dataset is copied into the repository.
83. No archive COPY is executed.
84. No archive MOVE is executed.
85. Qualified datasets remain unchanged.
86. Full repository pytest passes.
87. Ruff passes.
88. `git diff --check` passes.
89. Formatting validation passes for changed Python files.
90. Every changed file is identified.
91. No unrelated refactor or cleanup is included.
92. No Stage 8 closure implementation is started.
93. Completion report explicitly records that Stage 8.2e failed because of this hidden planning defect.
94. Evidence is sufficient to rerun the full remediation regression after this fix.
95. No commit is created.

## Next Step

If Stage 8.2f passes and is approved/committed, perform a fresh full real-data regression equivalent to the failed Stage 8.2e before Stage 8 remediation is closed.

## Stage 8.2f Completion Report — 2026-09-08

**Result: PASS — all 95 closure criteria satisfied.** F8-03A is corrected. This is Stage 8.2f implementation and qualification only; the replacement full-regression stage and Stage 8 closure have not begun. No commit was created.

### Environment and starting state

- Starting and ending HEAD: `02d92ce1e9b905889b3498d1266d2644a1e2d05b` — Stage 8.2d: correct stack-count diagnostic semantics.
- Python executable: `<development-environment>/bin/python`; version 3.13.15. pytest 9.1.1; Ruff 0.16.0.
- Package import path: `<repository-root>/src/seestar_toolkit/__init__.py`.
- Initial working tree: intentional modified `docs/CHANGELOG.md`, untracked failed Stage 8.2e report, and untracked Stage 8.2f specification. No unexpected initial production or test changes.
- SHA-256 checks confirm the pending CHANGELOG and failed Stage 8.2e document are byte-for-byte unchanged by Stage 8.2f. **Stage 8.2e remains FAIL**, because its regression exposed the hidden planning defect; it is not a completed remediation commit.

### Root cause and implementation policy

**F8-03A: ARCHIVE / DIAGNOSTIC; Low severity; P1 for Stage 8 closure.** The path is `plan_seestar_archive` → `_observation_candidate` → `_resolve_target` in `src/seestar_toolkit/archive/planning.py`. `_resolve_target` compared `directory.casefold()` directly with the authoritative FITS target. Thus retained directory evidence such as `Unknown_mosaic` still triggered a false conflict after discovery had correctly accepted it. Reconstruction was already correct.

Moved the existing Stage 8.2c suffix rule unchanged into `src/seestar_toolkit/archive/target_comparison.py::directory_target_for_comparison`. Both discovery and planning now call that one rule when comparing directory and FITS target evidence. This small shared module avoids coupling planning to a private discovery implementation and avoids a duplicate rule. It adds no model or exported package API.

The rule removes exactly one terminal, case-insensitive `_mosaic` suffix for comparison. Discovery still performs its existing `_sub` handling first, so a `Target_mosaic_sub` source directory retains `Target_mosaic` as directory target evidence and compares as `Target`. No arbitrary substring replacement, dimension/WCS inference, typed mosaic field or target override was introduced.

Only the diagnostic comparison uses the result. Original paths, stored directory target, FITS OBJECT and archive target precedence are preserved. Genuine mismatches still include the original conflicting evidence in diagnostics. Directory-only target fallback remains `Target_mosaic`; it is not rewritten to `Target`. Cadence/grouping, equal-time ordering, timestamp selection, filename fallback, STACKCNT handling and archive placement rules were not edited.

### Focused regression evidence

Ten new test cases: nine generated-FITS integration parameter cases and one directory-fallback unit test. The integration cases exercise discovery → reconstruction → planning, assert agreement between discovery and planning diagnostics, preserve source bytes/path/evidence, and verify no archive filesystem creation. Single-item cases legitimately retain existing LIGHTS_ONLY/STACK_ONLY informational diagnostics; the tests distinguish these from target conflicts.

| Required coverage | Cases and result |
|---|---|
| RF8-03A-1 `_mosaic` product | `Target_mosaic` / `Target` passes; `Unknown_mosaic` / `Unknown` also passes |
| RF8-03A-2 `_mosaic_sub` | `Target_mosaic_sub` / `Target` and mixed-case `Target_MOSAIC_SUB` / `target` pass |
| RF8-03A-3 genuine mismatch | `Target A_mosaic` and `Target A_mosaic_sub` versus `Target B` retain meaningful conflict diagnostics |
| RF8-03A-4 ordinary mosaic text | `Mosaic Galaxy` is unchanged; `Target_mosaic_field` is unchanged and still conflicts with `Target_field` |
| RF8-03A-5 consistency | Every generated case asserts equivalent discovery/planning match decisions |
| Target-selection protection | Missing FITS/compatibility target retains directory fallback `Target_mosaic` |

Before the production fix, the focused new/existing planning run produced **4 failed / 48 passed**: the four matching structural suffix cases failed on false planning conflicts. After the fix, all focused tests pass. During test construction, assertions were adjusted to retain expected single-item observation diagnostics rather than require an empty diagnostic tuple; no application warning was suppressed.

### Automated validation

| Check | Result |
|---|---|
| Focused remediation/discovery/planning tests | **100 passed in 0.78s** |
| `python -m pytest` | **314 passed in 11.35s** |
| `ruff check .` | PASS |
| `ruff format --check` on all five changed/new Python files | PASS: 5 files already formatted |
| `git diff --check` | PASS |

Focused files: `tests/integration/test_archive_planning.py`, `tests/unit/archive/test_planning.py`, `tests/unit/archive/test_reconstruction.py`, `tests/unit/archive/test_discovery.py`, `tests/integration/test_archive_reconstruction.py`, `tests/integration/test_archive_discovery.py`. Existing F8-01/F8-02/F8-03/F8-04 regressions all pass. Tests were run using the project virtual environment. No existing test was weakened, deleted or skipped. The pre-existing broad formatting debt recorded by failed Stage 8.2e remains untouched; Stage 8.2f requires formatting checks for changed Python files, all of which pass.

### Stage 8.2f real-data qualification

Read-only discovery/reconstruction/planning covered all nine datasets at `<private-test-data>/`. Frozen truth was reused. The nominal root `/tmp/stage82f_uncreated_archive` was passed to `plan_seestar_archive`; it was never created. No execution API was invoked for the corpus. Location remains the default `unknown` because no location configuration was supplied.

| Dataset | COMPLETE observations | Lights | Logical target | Plans | Archive date(s) | Discovery false mosaic / planning diagnostics / blocking problems |
|---|---|---|---|---|---|---|
| D01 | 1 | 18 | C 27 | 1 | 20260907 | 0 / 0 / 0 |
| D02 | 1 | 13 | Unknown | 1 | 20260907 | 0 / 0 / 0 |
| D03 | 1 | 18 | NGC 6888 | 1 | 20260907 | 0 / 0 / 0 |
| D04 | 1 | 12 | M 27 | 1 | 20260907 | 0 / 0 / 0 |
| D05 | 1 | 12 | NGC 6888 | 1 | 20260907 | 0 / 0 / 0 |
| D06 | 1 | 16 | IC 1318 | 1 | 20260906 | 0 / 0 / 0 |
| D07 | 1 | 77 | IC 5070 | 1 | 20260906 | 0 / 0 / 0 |
| D08 | 3 | 12 / 1 / 135 | M 57 | 3 | 20260907 / 20260907 / 20260907 | 0 / 0 / 0 |
| D09 | 1 | 12 | NGC 281W | 1 | 20260907 | 0 / 0 / 0 |

Total: **11 COMPLETE observations, 326 retained lights, 11 assigned stacks and 11 plans**. No extra LIGHTS_ONLY, STACK_ONLY, AMBIGUOUS or UNRESOLVED observations appear. Exact serialized observation membership, assigned-stack paths, compatibility targets, times, stack inspection metadata and reconstruction problems match the saved Stage 8.2e baseline for all nine datasets. Every planned count, target, date, name and destination suffix also matches; only the four erroneous planning diagnostics disappeared.

Assigned stacks, with paths relative to the corresponding dataset root:

| Dataset | Stack assignment in observation order |
|---|---|
| D01 | `C 27/Stacked_18_C 27_10.0s_IRCUT_20260906-210540.fit` |
| D02 | `Unknown_mosaic/Stacked_13_mosaic_Unknown_10.0s_IRCUT_20260906-211429.fit` |
| D03 | `NGC 6888/Stacked_18_NGC 6888_10.0s_LP_20260906-212307.fit` |
| D04 | `M 27/Stacked_12_M 27_10.0s_LP_20260906-221431.fit` |
| D05 | `NGC 6888_mosaic/Stacked_12_mosaic_NGC 6888_10.0s_LP_20260906-221937.fit` |
| D06 | `IC 1318/Stacked_16_IC 1318_10.0s_LP_20260905-214129.fit` |
| D07 | `IC 5070_mosaic/Stacked_77_mosaic_IC 5070_10.0s_LP_20260905-220832.fit` |
| D08 | `M 57/Stacked_12_M 57_10.0s_LP_20260906-224631.fit`<br>`M 57/Stacked_1_M 57_10.0s_LP_20260906-225738.fit`<br>`M 57/Stacked_106_M 57_30.0s_LP_20260907-002846.fit` |
| D09 | `NGC 281W_mosaic/Stacked_12_mosaic_NGC 281W_10.0s_LP_20260906-225304.fit` |

### Non-regression findings

- **F8-01:** D02/D05/D09 remain single COMPLETE observations with 13/12/12 lights, no trailing observation and unchanged equal-time final-light/stack timestamps. Existing later-light and incompatible-light protection tests pass.
- **F8-02:** zero false filename/FITS timestamp diagnostics across all nine datasets. Every qualified item with FITS timestamp evidence still selects that timestamp. Existing FITS authority and filename fallback tests pass; no timezone or network behavior changed.
- **F8-03 discovery:** false structural mosaic diagnostics remain zero in D02/D05/D07/D09. `Unknown` remains a legitimate target. Generated cases verify original source paths, directory evidence and FITS OBJECT are retained.
- **F8-03A planning:** the four former structural directory/FITS conflict diagnostics are now zero; genuine normalized mismatches remain diagnosed by focused tests. No archive target rewrite was used to achieve this result.
- **F8-04:** D08 Session 03 retains 135 lights. Direct read-only FITS header checks confirm `STACKCNT=106`, `TOTALEXP=3180.0`, `EXPTIME=30.0`, and `3180/30=106`. No retained-count or replacement stack warning remains. All 11 stack headers satisfy their exposure/count relationship.
- **D01 protection:** one COMPLETE / 18 lights, one plan dated `20260907`.
- **D07 protection:** firmware `7.75`, `EQMODE=1`, one COMPLETE / 77 lights, one plan dated `20260906`.
- **D08 protection:** three COMPLETE / 12, 1, 135 lights, unchanged intermediate stack boundaries, three plans dated `20260907`, numbered `observation_01`–`observation_03`. Session 03 retains its 221.936137-second maximum light gap and frozen cross-midnight filename evidence.
- All AltAz/EQ firmware cases and RGB stacks retaining `BAYERPAT=GRBG` are unchanged. Archive hierarchy, observation numbering, +12-hour dates and target-selection precedence remain unchanged. DF8-01 and DF8-02 remain deferred.

Remaining corpus discovery diagnostics: exactly one `<dataset>/.DS_Store` per dataset (D01–D09), each `Unsupported source-file extension: <none>`. These are expected informational exclusions, not F8-03A or new defects; observation and planning diagnostics are zero.

The temporary qualification harness initially compared in-memory tuples/datetimes with JSON baseline lists/strings, producing a harness-only assertion mismatch. Both sides were then compared in the same serialized representation and the qualification rerun successfully. No production change was made in response; no reconstruction difference was found.

### Dataset preservation

Before and after manifests match exactly. Sorted entries contain relative path, file type/mode, size, mtime_ns, ctime_ns, and full-content SHA-256 for each file; directory state is also included. Access time is excluded because reads may affect it. The displayed fingerprint is SHA-256 of each dataset’s compact sorted JSON manifest.

| Dataset | Files before / after | Bytes before / after | Fingerprint before = after |
|---|---|---|---|
| D01 | 58 / 58 | 140096760 / 140096760 | `108aaf3103168a854fa410b06fff6048d57580c2bb32a613ccff2a37d771586c` |
| D02 | 43 / 43 | 92584424 / 92584424 | `6365ddb2dba5ef8ab1bc003dbe56f631d37782fb77750d9ac78102b6593ab106` |
| D03 | 58 / 58 | 140069691 / 140069691 | `ddca8d8912b40160eada506744a2a507f6fb9635ebfb5e4b4370e5f0fa547fdd` |
| D04 | 40 / 40 | 110684347 / 110684347 | `a8a9d1c6f17632bce14e5aed4fb3e852d7640ea9dc5436fbf8f21272208d25e0` |
| D05 | 40 / 40 | 71751294 / 71751294 | `c667622867c2e4c280ce28f740b78d3d848f1b21e8a2b68634e33f6992099b61` |
| D06 | 52 / 52 | 130415139 / 130415139 | `2643921a2469f6569026849346227bb4bf5e16969ce89bc0c99a3bbf3f24bc29` |
| D07 | 235 / 235 | 414333201 / 414333201 | `feb64ed1aca39b39fad1b7fb054b0b34b30cccd4d78d4bc0537eb6e04811cf90` |
| D08 | 454 / 454 | 880703483 / 880703483 | `7ea235a43ff3deec3e2b0ec463c9bac1367013e080b4bb8cbccf1101cd32fcd0` |
| D09 | 40 / 40 | 80605529 / 80605529 | `8c259ccc5236f3d73eb1a42d9ccf4a75ee794d1d194e9429437793b63c380846` |
| Entire corpus root | 1023 / 1023 | 2061255012 / 2061255012 | `c2b51858f3e87e7c1652d6d1c3e9ad943a5f112c5ca915280dd10baba2fbbf89` |

Dataset subtotal: **1,020 files / 2,061,243,868 bytes**, unchanged. Entire-root totals include three existing metadata files outside the dataset directories. No dataset was modified, moved, renamed, deleted or copied. No archive COPY/MOVE was executed against the corpus. The required full pytest suite separately exercises execution APIs using temporary test fixtures.

### Changed files and final Git status

| Git state | File | Change |
|---|---|---|
| M (pre-existing) | `docs/CHANGELOG.md` | Pending Stage 8.2d entry, unchanged by this work |
| ?? (pre-existing) | `docs/change_documents/STAGE_8/STAGE_8.2e.md` | Failed regression report, unchanged by this work |
| ?? | `docs/change_documents/STAGE_8/STAGE_8.2f.md` | Original specification retained; status and this report added |
| M | `src/seestar_toolkit/archive/discovery.py` | Use the extracted authoritative comparison helper |
| M | `src/seestar_toolkit/archive/planning.py` | Apply the same helper only to directory/FITS diagnostic comparison |
| ?? | `src/seestar_toolkit/archive/target_comparison.py` | Shared existing terminal-suffix rule |
| M | `tests/unit/archive/test_planning.py` | One fallback-preservation regression |
| ?? | `tests/integration/test_archive_planning.py` | Nine generated-FITS comparison/consistency regressions |

No other repository file changed. No commit, branch change, staging, unrelated cleanup or later-stage implementation occurred. Temporary artifacts outside the repository: `/tmp/stage82f_preexisting.json`, `/tmp/stage82f_red.txt`, `/tmp/stage82f_validate.py`, `/tmp/stage82f_report.py`, `/tmp/stage82f_qualification.txt`, and `/tmp/stage82f_evidence/{before.json,after.json,results.json,preservation.json}`. They contain validation scripts, logs, metadata and membership paths, not dataset copies.

### Readiness

Evidence supports approval/review of Stage 8.2f and a subsequent fresh full remediation regression after the requested workflow’s approval/commit step. This qualification does not retroactively change failed Stage 8.2e, close Stage 8.2, or begin the replacement full-regression stage. No remaining F8-03A defect was found.

### Individual closure criteria

**95 / 95 PASS.** Each criterion is evaluated below.

| # | Result | Criterion and evidence |
|---|---|---|
| 1 | PASS | Starting HEAD is recorded and matches `02d92ce` or any difference is explained. See environment, preserved document hashes and final Git status. |
| 2 | PASS | Failed Stage 8.2e documentation is distinguished from production changes. See environment, preserved document hashes and final Git status. |
| 3 | PASS | Pending CHANGELOG entry is correctly treated as intentional. See environment, preserved document hashes and final Git status. |
| 4 | PASS | Exact archive-planning code path producing false mosaic diagnostics is identified. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 5 | PASS | The defect is confirmed as separate from reconstruction. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 6 | PASS | Implementation is scoped to archive-planning F8-03 semantics only. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 7 | PASS | `_mosaic` is treated structurally for archive target comparison. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 8 | PASS | `_mosaic_sub` is treated structurally for archive target comparison. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 9 | PASS | Normalization uses suffix semantics, not broad substring replacement. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 10 | PASS | Original source paths remain unchanged. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 11 | PASS | Original stored directory evidence remains unchanged. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 12 | PASS | FITS `OBJECT` remains unchanged. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 13 | PASS | Archive target selection semantics remain otherwise unchanged. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 14 | PASS | Genuine normalized target mismatches still diagnose. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 15 | PASS | Ordinary non-structural `mosaic` text remains unchanged. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 16 | PASS | Discovery and archive planning use consistent logical comparison semantics. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 17 | PASS | Stage 8.2c discovery-level behaviour remains intact. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 18 | PASS | No typed mosaic field is introduced. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 19 | PASS | No dimension-based mosaic inference is introduced. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 20 | PASS | No WCS-based mosaic inference is introduced. See root cause/shared-helper policy and generated-FITS preservation assertions. |
| 21 | PASS | Focused archive `_mosaic` regression passes. See 100 passing focused tests and the RF8-03A coverage table. |
| 22 | PASS | Focused archive `_mosaic_sub` regression passes. See 100 passing focused tests and the RF8-03A coverage table. |
| 23 | PASS | Focused genuine-mismatch regression passes. See 100 passing focused tests and the RF8-03A coverage table. |
| 24 | PASS | Focused non-structural mosaic-text regression passes. See 100 passing focused tests and the RF8-03A coverage table. |
| 25 | PASS | Discovery/planning consistency regression passes. See 100 passing focused tests and the RF8-03A coverage table. |
| 26 | PASS | F8-01 regressions remain passing. See 100 passing focused tests and the RF8-03A coverage table. |
| 27 | PASS | F8-02 regressions remain passing. See 100 passing focused tests and the RF8-03A coverage table. |
| 28 | PASS | F8-03 discovery regressions remain passing. See 100 passing focused tests and the RF8-03A coverage table. |
| 29 | PASS | F8-04 regressions remain passing. See 100 passing focused tests and the RF8-03A coverage table. |
| 30 | PASS | Dataset 02 remains one COMPLETE observation. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 31 | PASS | Dataset 02 retains 13 lights. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 32 | PASS | Dataset 02 target remains `Unknown`. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 33 | PASS | Dataset 02 discovery F8-03 diagnostics remain zero. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 34 | PASS | Dataset 02 archive-planning false mosaic diagnostics become zero. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 35 | PASS | Dataset 02 archive plan count remains 1. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 36 | PASS | Dataset 02 archive date remains `20260907`. D02: 1 COMPLETE / 13 / Unknown / 1 plan / 20260907; zero false diagnostics. |
| 37 | PASS | Dataset 05 remains one COMPLETE observation. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 38 | PASS | Dataset 05 retains 12 lights. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 39 | PASS | Dataset 05 discovery F8-03 diagnostics remain zero. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 40 | PASS | Dataset 05 archive-planning false mosaic diagnostics become zero. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 41 | PASS | Dataset 05 archive plan count remains 1. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 42 | PASS | Dataset 05 archive date remains `20260907`. D05: 1 COMPLETE / 12 / 1 plan / 20260907; zero false diagnostics. |
| 43 | PASS | Dataset 07 remains one COMPLETE observation. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 44 | PASS | Dataset 07 retains 77 lights. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 45 | PASS | Dataset 07 firmware 7.75 behaviour remains intact. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 46 | PASS | Dataset 07 EQ behaviour remains intact. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 47 | PASS | Dataset 07 discovery F8-03 diagnostics remain zero. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 48 | PASS | Dataset 07 archive-planning false mosaic diagnostics become zero. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 49 | PASS | Dataset 07 archive plan count remains 1. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 50 | PASS | Dataset 07 archive date remains `20260906`. D07: 1 COMPLETE / 77 / firmware 7.75 / EQMODE=1 / 1 plan / 20260906; zero false diagnostics. |
| 51 | PASS | Dataset 09 remains one COMPLETE observation. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 52 | PASS | Dataset 09 retains 12 lights. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 53 | PASS | Dataset 09 F8-01 equal-time behaviour remains fixed. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 54 | PASS | Dataset 09 discovery F8-03 diagnostics remain zero. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 55 | PASS | Dataset 09 archive-planning false mosaic diagnostics become zero. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 56 | PASS | Dataset 09 archive plan count remains 1. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 57 | PASS | Dataset 09 archive date remains `20260907`. D09: 1 COMPLETE / 12 / unchanged equal-time boundary / 1 plan / 20260907; zero false diagnostics. |
| 58 | PASS | Dataset 01 remains 1 COMPLETE / 18 lights. D01: 1 COMPLETE / 18 / 1 plan / 20260907. |
| 59 | PASS | Dataset 01 archive plan remains 1 dated `20260907`. D01: 1 COMPLETE / 18 / 1 plan / 20260907. |
| 60 | PASS | Dataset 08 remains exactly 3 COMPLETE observations. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 61 | PASS | Dataset 08 memberships remain 12 / 1 / 135. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 62 | PASS | Dataset 08 archive planning remains 3 observations. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 63 | PASS | Dataset 08 archive dates remain `20260907`. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 64 | PASS | Dataset 08 Session 03 retains 135 lights. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 65 | PASS | Dataset 08 STACKCNT remains 106. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 66 | PASS | Dataset 08 TOTALEXP remains 3180. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 67 | PASS | Dataset 08 EXPTIME remains 30. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 68 | PASS | Dataset 08 emits no F8-04 false diagnostic. D08: 3 COMPLETE / 12,1,135 / 3 plans dated 20260907; Session 03 header 106/3180/30; zero diagnostics. |
| 69 | PASS | F8-02 remains zero across qualified datasets. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 70 | PASS | No observation membership changes are introduced. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 71 | PASS | No observation-count changes are introduced. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 72 | PASS | Timestamp precedence remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 73 | PASS | Filename fallback remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 74 | PASS | Equal-time semantic ordering remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 75 | PASS | STACKCNT remains independent of source membership. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 76 | PASS | Cadence/grouping thresholds remain unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 77 | PASS | Archive hierarchy remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 78 | PASS | Observation numbering remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 79 | PASS | +12-hour archive-date policy remains unchanged. Exact baseline observation/placement comparison passes; protected production code is unchanged. |
| 80 | PASS | DF8-01 typed mosaic evidence remains deferred. Both deferred features remain unimplemented. |
| 81 | PASS | DF8-02 target correction/override remains deferred. Both deferred features remain unimplemented. |
| 82 | PASS | No complete external dataset is copied into the repository. Read-only planning; before/after state and full-content manifests match. |
| 83 | PASS | No archive COPY is executed. Read-only planning; before/after state and full-content manifests match. |
| 84 | PASS | No archive MOVE is executed. Read-only planning; before/after state and full-content manifests match. |
| 85 | PASS | Qualified datasets remain unchanged. Read-only planning; before/after state and full-content manifests match. |
| 86 | PASS | Full repository pytest passes. 314 tests passed. |
| 87 | PASS | Ruff passes. ruff check . passed. |
| 88 | PASS | `git diff --check` passes. git diff --check passed. |
| 89 | PASS | Formatting validation passes for changed Python files. All five changed/new Python files pass Ruff formatting. |
| 90 | PASS | Every changed file is identified. See complete file list and scoped diff; no later stage started. |
| 91 | PASS | No unrelated refactor or cleanup is included. See complete file list and scoped diff; no later stage started. |
| 92 | PASS | No Stage 8 closure implementation is started. See complete file list and scoped diff; no later stage started. |
| 93 | PASS | Completion report explicitly records that Stage 8.2e failed because of this hidden planning defect. See environment, preserved document hashes and final Git status. |
| 94 | PASS | Evidence is sufficient to rerun the full remediation regression after this fix. The fix is qualified and ready for the separately authorized replacement regression. |
| 95 | PASS | No commit is created. See environment, preserved document hashes and final Git status. |
