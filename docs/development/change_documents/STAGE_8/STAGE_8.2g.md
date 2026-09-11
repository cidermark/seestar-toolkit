# Stage 8.2g — Full Real-Data Remediation Regression

## Status

PASS — validation completed 2026-09-08; uncommitted.

## Purpose

Repeat the full Stage 8 remediation regression from the corrected post-8.2f baseline.

Stage 8.2e previously failed because archive planning still emitted false structural-mosaic target diagnostics. Stage 8.2f corrected that hidden defect.

Stage 8.2g must now prove that the complete remediation set works together across the frozen nine-dataset real-data corpus.

This is a validation stage. A clean PASS should require no production or test-code changes.

## Starting Commit

Expected starting commit:

`491ce26` — Stage 8.2f: correct mosaic target semantics in archive planning

Record the actual Git `HEAD` before validation begins.

Permitted intentional working-tree changes:

- `docs/CHANGELOG.md` containing the pending Stage 8.2f entry;
- this `docs/change_documents/STAGE_8/STAGE_8.2g.md`.

Any other pre-existing change must be identified and explained.

## Remediations Under Combined Validation

Validate all confirmed Stage 8 fixes together:

- F8-01 — equal-time reconstruction ordering;
- F8-02 — filename/FITS timestamp diagnostic semantics;
- F8-03 — discovery structural mosaic target comparison;
- F8-03A — archive-planning structural mosaic target comparison;
- F8-04 — stack-count diagnostic semantics.

## Frozen Real-Data Corpus

Use the existing read-only corpus:

`<private-test-data>/`

Datasets:

1. `dataset_01_fw846_altaz_c27_single`
2. `dataset_02_fw846_altaz_unknown_mosaic_single`
3. `dataset_03_fw846_altaz_ngc6888_single`
4. `dataset_04_fw931_altaz_m27_single`
5. `dataset_05_fw931_altaz_ngc6888_mosaic_single`
6. `dataset_06_fw775_eq_ic1318_single`
7. `dataset_07_fw775_eq_ic5070_mosaic_single`
8. `dataset_08_fw931_eq_m57_three_sessions`
9. `dataset_09_fw931_eq_ngc281w_mosaic_single`

Do not repeat ground-truth discovery. Existing frozen Stage 8 truth is authoritative.

## Frozen Reconstruction Truth

Expected results:

- Dataset 01 — 1 COMPLETE — 18 lights
- Dataset 02 — 1 COMPLETE — 13 lights
- Dataset 03 — 1 COMPLETE — 18 lights
- Dataset 04 — 1 COMPLETE — 12 lights
- Dataset 05 — 1 COMPLETE — 12 lights
- Dataset 06 — 1 COMPLETE — 16 lights
- Dataset 07 — 1 COMPLETE — 77 lights
- Dataset 08 — 3 COMPLETE — 12 / 1 / 135 lights
- Dataset 09 — 1 COMPLETE — 12 lights

Total expected observations:

`11`

All expected stack assignments must remain correct.

No unexpected LIGHTS_ONLY, STACK_ONLY, AMBIGUOUS or UNRESOLVED observations are permitted.

## Frozen Archive-Planning Truth

Expected plan counts:

- Dataset 01 — 1
- Dataset 02 — 1
- Dataset 03 — 1
- Dataset 04 — 1
- Dataset 05 — 1
- Dataset 06 — 1
- Dataset 07 — 1
- Dataset 08 — 3
- Dataset 09 — 1

Total expected planned observations:

`11`

Expected archive dates:

- Dataset 01 — `20260907`
- Dataset 02 — `20260907`
- Dataset 03 — `20260907`
- Dataset 04 — `20260907`
- Dataset 05 — `20260907`
- Dataset 06 — `20260906`
- Dataset 07 — `20260906`
- Dataset 08 — all three `20260907`
- Dataset 09 — `20260907`

No false structural-mosaic planning diagnostics are expected.

## Required Validation

### F8-01

Datasets 02, 05 and 09 must remain corrected.

Confirm:

- compatible equal-time final lights remain attached to their stacks;
- no trailing LIGHTS_ONLY observations;
- later lights are not assigned backward;
- observation membership/count remains frozen.

### F8-02

Across all nine datasets confirm:

- FITS timestamps remain authoritative where available;
- filename timestamps remain fallback evidence;
- false local-time-vs-UTC conflict diagnostics remain zero;
- no timezone inference;
- no network dependency.

### F8-03

Datasets 02, 05, 07 and 09:

- discovery false mosaic target diagnostics remain zero;
- original source paths remain unchanged;
- stored directory evidence remains unchanged;
- FITS target remains unchanged;
- legitimate `Unknown` remains supported.

### F8-03A

Datasets 02, 05, 07 and 09:

- archive-planning false mosaic target diagnostics/problems remain zero;
- archive plan count/date remain frozen;
- genuine target-mismatch protection remains covered by automated tests.

### F8-04

Dataset 08 Session 03 remains:

- 135 retained source lights;
- reported `STACKCNT=106`;
- `TOTALEXP=3180`;
- `EXPTIME=30`;
- no retained-count-vs-STACKCNT diagnostic;
- no false replacement diagnostic;
- source membership remains independent of STACKCNT.

## Behavioural Coverage

Confirm the frozen corpus still validates:

- AltAz;
- EQ;
- firmware 7.75;
- firmware 8.46;
- firmware 9.31;
- single observations;
- multiple observations of same target/night;
- cross-midnight session behaviour;
- large retained-light gaps;
- equal-time light/stack timestamps;
- structural mosaic filesystem naming;
- target `Unknown`;
- RGB stacked FITS containing `BAYERPAT=GRBG`;
- retained source count differing from STACKCNT.

## Diagnostics

The full frozen corpus should have zero diagnostics attributable to:

- F8-01;
- F8-02;
- F8-03;
- F8-03A;
- F8-04.

If anything remains, identify the exact dataset/item and classify it explicitly.

Do not silently suppress or opportunistically fix unrelated findings.

## Automated Validation

Run focused regression tests covering all Stage 8 remediation findings.

Then run:

`python -m pytest`

`ruff check .`

`git diff --check`

Run project-standard formatting validation where applicable.

A clean Stage 8.2g PASS should require no production/test change.

## Dataset Preservation

Qualification must remain read-only.

Capture before/after preservation evidence for all nine datasets, including at minimum:

- file count;
- total bytes;
- content/state fingerprint.

Do not:

- modify;
- rename;
- move;
- delete;
- copy complete datasets into the repository;
- execute archive COPY;
- execute archive MOVE.

## Deferred Features

Remain deferred:

- DF8-01 — typed mosaic evidence;
- DF8-02 — target correction/override.

Do not implement either.

## Scope

Stage 8.2g includes only:

1. record starting repository state;
2. run focused remediation regression tests;
3. run full repository validation;
4. perform full nine-dataset discovery/reconstruction qualification;
5. perform full nine-dataset read-only archive-planning qualification;
6. compare all results with frozen truth;
7. confirm all five remediation findings remain resolved;
8. verify dataset preservation;
9. determine whether Stage 8.2 remediation can be formally closed.

## Exclusions

Do not:

- modify F8-01 through F8-04/F8-03A design;
- add new heuristics;
- alter reconstruction grouping;
- alter cadence thresholds;
- alter timestamp precedence;
- alter filename fallback;
- add timezone inference;
- add typed mosaic state;
- infer mosaic from dimensions/WCS;
- add target override/correction;
- change STACKCNT source-membership semantics;
- change archive hierarchy;
- change observation numbering;
- change +12-hour date policy;
- begin Stage 8 closure implementation;
- include unrelated cleanup/refactoring;
- commit changes.

## Expected Outcome

A clean PASS should establish:

- all repository tests pass;
- all 11 frozen observations match truth;
- all 11 archive plans match truth;
- all expected dates match;
- F8-01 resolved;
- F8-02 resolved;
- F8-03 resolved;
- F8-03A resolved;
- F8-04 resolved;
- no cross-remediation regression;
- no production/test change required;
- external datasets unchanged.

## Completion Report

Return:

- result: PASS / PASS WITH FINDINGS / FAIL;
- starting HEAD and working-tree state;
- Python executable/version/import path;
- focused validation results;
- full pytest/Ruff/format/diff results;
- full nine-dataset reconstruction table;
- full nine-dataset archive-planning table;
- remediation verification for F8-01/F8-02/F8-03/F8-03A/F8-04;
- behavioural coverage;
- dataset preservation evidence;
- deferred-feature confirmation;
- git diff/status summary;
- closure recommendation;
- all closure criteria below individually.

## Closure Criteria

1. Actual starting HEAD is recorded and matches `491ce26` or difference is explained.
2. Pending CHANGELOG entry is identified as intentional.
3. No unexpected pre-existing working-tree changes are ignored.
4. No production-code change is made unless a genuine regression requires it.
5. No test-code change is made unless a genuine regression requires it.
6. Focused F8-01 regressions pass.
7. Focused F8-02 regressions pass.
8. Focused F8-03 regressions pass.
9. Focused F8-03A regressions pass.
10. Focused F8-04 regressions pass.
11. Full repository pytest passes.
12. Ruff passes.
13. `git diff --check` passes.
14. Formatting validation passes where applicable.
15. Dataset 01 reconstructs exactly 1 COMPLETE observation.
16. Dataset 01 retains 18 lights.
17. Dataset 02 reconstructs exactly 1 COMPLETE observation.
18. Dataset 02 retains 13 lights.
19. Dataset 03 reconstructs exactly 1 COMPLETE observation.
20. Dataset 03 retains 18 lights.
21. Dataset 04 reconstructs exactly 1 COMPLETE observation.
22. Dataset 04 retains 12 lights.
23. Dataset 05 reconstructs exactly 1 COMPLETE observation.
24. Dataset 05 retains 12 lights.
25. Dataset 06 reconstructs exactly 1 COMPLETE observation.
26. Dataset 06 retains 16 lights.
27. Dataset 07 reconstructs exactly 1 COMPLETE observation.
28. Dataset 07 retains 77 lights.
29. Dataset 08 reconstructs exactly 3 COMPLETE observations.
30. Dataset 08 memberships remain 12 / 1 / 135.
31. Dataset 09 reconstructs exactly 1 COMPLETE observation.
32. Dataset 09 retains 12 lights.
33. Total reconstruction count remains exactly 11.
34. All expected stack assignments remain correct.
35. No unexpected LIGHTS_ONLY observations appear.
36. No unexpected STACK_ONLY observations appear.
37. No unexpected AMBIGUOUS observations appear.
38. No unexpected UNRESOLVED observations appear.
39. F8-01 remains resolved in Dataset 02.
40. F8-01 remains resolved in Dataset 05.
41. F8-01 remains resolved in Dataset 09.
42. F8-02 false timestamp diagnostics are zero across all nine datasets.
43. FITS timestamp authority remains intact.
44. Filename fallback remains intact.
45. No timezone inference is introduced.
46. No network dependency is introduced.
47. Dataset 02 discovery F8-03 diagnostics remain zero.
48. Dataset 05 discovery F8-03 diagnostics remain zero.
49. Dataset 07 discovery F8-03 diagnostics remain zero.
50. Dataset 09 discovery F8-03 diagnostics remain zero.
51. Dataset 02 archive-planning F8-03A diagnostics remain zero.
52. Dataset 05 archive-planning F8-03A diagnostics remain zero.
53. Dataset 07 archive-planning F8-03A diagnostics remain zero.
54. Dataset 09 archive-planning F8-03A diagnostics remain zero.
55. Dataset 02 target remains legitimate `Unknown`.
56. Original source paths remain unchanged.
57. Original stored directory evidence remains unchanged.
58. FITS target evidence remains unchanged.
59. Discovery/planning mosaic comparison semantics remain consistent.
60. No typed mosaic state is introduced.
61. No dimensions-based mosaic inference is introduced.
62. No WCS-based mosaic inference is introduced.
63. Dataset 08 Session 03 retains 135 source lights.
64. Dataset 08 Session 03 STACKCNT remains 106.
65. Dataset 08 Session 03 TOTALEXP remains 3180.
66. Dataset 08 Session 03 EXPTIME remains 30.
67. Dataset 08 Session 03 emits no retained-count-vs-STACKCNT warning.
68. Dataset 08 Session 03 emits no false replacement stack diagnostic.
69. STACKCNT remains independent of source membership.
70. Dataset 08 cross-midnight behaviour remains intact.
71. Dataset 08 large-gap behaviour remains intact.
72. Dataset 08 intermediate-stack boundaries remain intact.
73. Dataset 01 archive plan count is 1.
74. Dataset 02 archive plan count is 1.
75. Dataset 03 archive plan count is 1.
76. Dataset 04 archive plan count is 1.
77. Dataset 05 archive plan count is 1.
78. Dataset 06 archive plan count is 1.
79. Dataset 07 archive plan count is 1.
80. Dataset 08 archive plan count is 3.
81. Dataset 09 archive plan count is 1.
82. Total archive plan count remains exactly 11.
83. Dataset 01 archive date is `20260907`.
84. Dataset 02 archive date is `20260907`.
85. Dataset 03 archive date is `20260907`.
86. Dataset 04 archive date is `20260907`.
87. Dataset 05 archive date is `20260907`.
88. Dataset 06 archive date is `20260906`.
89. Dataset 07 archive date is `20260906`.
90. All Dataset 08 archive dates are `20260907`.
91. Dataset 09 archive date is `20260907`.
92. No archive-planning regression remains.
93. AltAz behaviour remains intact.
94. EQ behaviour remains intact.
95. Firmware 7.75 compatibility remains intact.
96. Firmware 8.46 compatibility remains intact.
97. Firmware 9.31 compatibility remains intact.
98. RGB stacked FITS with `BAYERPAT=GRBG` remain correctly classified.
99. Equal-time light/stack behaviour remains intact.
100. Structural mosaic filesystem naming remains supported.
101. Retained-light count differing from STACKCNT remains supported.
102. DF8-01 remains deferred.
103. DF8-02 remains deferred.
104. Archive hierarchy remains unchanged.
105. Observation numbering remains unchanged.
106. +12-hour archive-date policy remains unchanged.
107. Cadence/grouping thresholds remain unchanged.
108. No complete dataset is copied into the repository.
109. No archive COPY is executed.
110. No archive MOVE is executed.
111. All nine datasets remain unchanged after qualification.
112. Every changed file is identified.
113. No unrelated cleanup/refactor is included.
114. No Stage 8 closure implementation is started.
115. Any unexpected discrepancy is explicitly classified.
116. Evidence is sufficient to formally close Stage 8.2 remediation.
117. Evidence is sufficient to proceed to final Stage 8 closure validation without reopening F8-01/F8-02/F8-03/F8-03A/F8-04.

## Expected Next Step

If Stage 8.2g passes cleanly:

1. formally close Stage 8.2 remediation;
2. commit Stage 8.2g validation documentation;
3. update `docs/CHANGELOG.md` with the Stage 8.2g commit and leave it pending;
4. define the final Stage 8 closure audit using the established Stage workflow.

## Stage 8.2g Completion Report — 2026-09-08

**Result: PASS — all 117 closure criteria satisfied.** The complete remediation set passes combined qualification. All 11 observations and all 11 archive plans match frozen truth; no production or test-code change was required.

### Environment and repository state

- Starting HEAD: `491ce265434425b3e363bbbc390e7c7e1e9d691e` — Stage 8.2f: correct mosaic target semantics in archive planning. Ending HEAD is unchanged.
- Initial working tree: modified `docs/CHANGELOG.md` with the intentional three-line pending Stage 8.2f entry; untracked `docs/change_documents/STAGE_8/STAGE_8.2g.md`. No other initial changes.
- Python executable: `<development-environment>/bin/python`; version 3.13.15; pytest 9.1.1; Ruff 0.16.0.
- Imported package: `<repository-root>/src/seestar_toolkit/__init__.py`.
- Existing frozen Stage 8 truth was used without repeating ground-truth discovery. The earlier Stage 8.2e FAIL and Stage 8.2f remediation report remain unchanged; this is a new validation result from the corrected committed baseline.

### Automated validation

| Check | Result |
|---|---|
| Focused remediation tests | **100 passed in 0.63s** |
| `python -m pytest` | **314 passed in 10.64s** |
| `ruff check .` | PASS |
| Scoped `ruff format --check` | PASS: 27 files already formatted |
| `git diff --check` | PASS |

All commands used the project virtual environment. Focused tests comprise `tests/unit/archive/test_reconstruction.py`, `tests/unit/archive/test_discovery.py`, `tests/unit/archive/test_planning.py`, `tests/integration/test_archive_reconstruction.py`, `tests/integration/test_archive_discovery.py`, and `tests/integration/test_archive_planning.py`. They cover F8-01 equal-time compatibility and later-light rejection, F8-02 FITS authority and filename fallback, F8-03 structural suffix and genuine mismatch handling, F8-03A discovery/planning consistency and target-fallback preservation, and F8-04 retained counts above/below STACKCNT, missing counts and contradictory stack metadata.

Formatting was checked for `src/seestar_toolkit/archive`, `tests/unit/archive`, the three discovery/reconstruction/planning integration files, and the Stage 8.2g document. No Python files changed. The pre-existing broader repository formatting debt documented by Stage 8.2e remains outside this validation’s changed-file scope; no claim is made that repository-wide formatting debt was cleared. No test was added, modified, weakened or skipped.

### Full nine-dataset reconstruction

Dataset IDs refer to the exact frozen directory names listed in the specification above. Stack paths below are relative to their dataset root. Every light and stack is assigned exactly once, with no extra or missing FITS membership. All assigned lights precede or equal their stack time.

| Dataset | Observations/status | Light membership | Assigned stack(s) | Logical target | Observation diagnostics |
|---|---|---|---|---|---|
| D01 | 1 COMPLETE | 18 | `C 27/Stacked_18_C 27_10.0s_IRCUT_20260906-210540.fit` | C 27 | 0 |
| D02 | 1 COMPLETE | 13 | `Unknown_mosaic/Stacked_13_mosaic_Unknown_10.0s_IRCUT_20260906-211429.fit` | Unknown | 0 |
| D03 | 1 COMPLETE | 18 | `NGC 6888/Stacked_18_NGC 6888_10.0s_LP_20260906-212307.fit` | NGC 6888 | 0 |
| D04 | 1 COMPLETE | 12 | `M 27/Stacked_12_M 27_10.0s_LP_20260906-221431.fit` | M 27 | 0 |
| D05 | 1 COMPLETE | 12 | `NGC 6888_mosaic/Stacked_12_mosaic_NGC 6888_10.0s_LP_20260906-221937.fit` | NGC 6888 | 0 |
| D06 | 1 COMPLETE | 16 | `IC 1318/Stacked_16_IC 1318_10.0s_LP_20260905-214129.fit` | IC 1318 | 0 |
| D07 | 1 COMPLETE | 77 | `IC 5070_mosaic/Stacked_77_mosaic_IC 5070_10.0s_LP_20260905-220832.fit` | IC 5070 | 0 |
| D08 | 3 COMPLETE | 12 / 1 / 135 | `M 57/Stacked_12_M 57_10.0s_LP_20260906-224631.fit`<br>`M 57/Stacked_1_M 57_10.0s_LP_20260906-225738.fit`<br>`M 57/Stacked_106_M 57_30.0s_LP_20260907-002846.fit` | M 57 | 0 |
| D09 | 1 COMPLETE | 12 | `NGC 281W_mosaic/Stacked_12_mosaic_NGC 281W_10.0s_LP_20260906-225304.fit` | NGC 281W | 0 |

**Total: 11 COMPLETE observations, 326 lights, 11 assigned stacks.** No LIGHTS_ONLY, STACK_ONLY, AMBIGUOUS or UNRESOLVED observations occur. Exact serialized observation records, including every member path, stack assignment, selected times, compatibility target, stack inspection metadata and diagnostic list, match the preserved Stage 8.2f qualification evidence.

### Full nine-dataset read-only archive planning

Called `plan_seestar_archive` directly for each reconstruction with nominal root `/tmp/stage82g_uncreated_archive`. That root was never created. No execution API, conversion or dataset-copy operation was invoked for qualification. No explicit or saved location was supplied, so the existing location fallback remains `unknown`.

| Dataset | Plan count | Archive date(s) | Planning metadata diagnostics | Blocking planning problems |
|---|---|---|---|---|
| D01 | 1 | 20260907 | 0 | 0 |
| D02 | 1 | 20260907 | 0 | 0 |
| D03 | 1 | 20260907 | 0 | 0 |
| D04 | 1 | 20260907 | 0 | 0 |
| D05 | 1 | 20260907 | 0 | 0 |
| D06 | 1 | 20260906 | 0 | 0 |
| D07 | 1 | 20260906 | 0 | 0 |
| D08 | 3 | 20260907 / 20260907 / 20260907 | 0 | 0 |
| D09 | 1 | 20260907 | 0 | 0 |

**Total: 11 plans.** All specified dates match. Default hierarchy remains `{target}/{location}/{session_end_date}`. Single-observation datasets use `observation_01`; D08 uses `observation_01`, `observation_02`, `observation_03` in chronological order. Counts, targets, dates, names and destination suffixes exactly match Stage 8.2f evidence; only the nominal validation root differs.

### Combined remediation verification

**F8-01 — PASS.** D02/D05/D09 remain 1 COMPLETE with 13/12/12 lights and no trailing LIGHTS_ONLY observation. Equal-time final-light/stack timestamps remain `2026-09-06 20:14:08.453031`, `2026-09-06 21:19:09.055769`, and `2026-09-06 21:52:36.968517`, respectively. Corpus assertions verify no later-light back-assignment; focused negative and deterministic-order regressions pass.

**F8-02 — PASS.** False filename/FITS timestamp diagnostics are zero across all nine datasets and every diagnostic layer. Every discovered FITS item with FITS timestamp evidence selects that evidence. Filename fallback and FITS authority tests pass. No timezone inference, network dependency or timestamp-policy change was introduced.

**F8-03 — PASS.** D02/D05/D07/D09 have zero discovery structural mosaic target conflicts. Inventory evidence is identical before and after planning, including source paths, directory target and FITS metadata. D02 retains legitimate target `Unknown`. Automated evidence-preservation tests pass.

**F8-03A — PASS.** D02/D05/D07/D09 have zero archive-planning structural mosaic target diagnostics and zero blocking planning problems. All expected plans/dates remain frozen. Discovery and planning still share `target_comparison.py::directory_target_for_comparison`; genuine normalized mismatch, ordinary mosaic text, mixed-case suffix and directory-only target-fallback tests pass. No target rewriting was used.

**F8-04 — PASS.** D08 Session 03 retains 135 lights with reported count 106. Direct read-only FITS header checks confirm `STACKCNT=106`, `TOTALEXP=3180.0`, `EXPTIME=30.0`; `3180/30=106`. There is no retained-count warning or replacement stack diagnostic. All 11 stacks satisfy the metadata exposure/count relationship. Source membership remains independent of STACKCNT.

No cross-remediation regression or additional defect was found.

### Behavioural coverage

| Behaviour | Evidence/result |
|---|---|
| AltAz | D01–D05 pass; stack EQMODE=0 |
| EQ | D06–D09 pass; stack EQMODE=1 |
| Firmware 7.75 | D06/D07 stack metadata and complete reconstructions pass |
| Firmware 8.46 | D01–D03 pass |
| Firmware 9.31 | D04/D05/D08/D09 pass |
| Single observations | All datasets other than D08 retain one COMPLETE |
| Same target/night, multiple observations | D08 retains three M 57 observations and intermediate-stack boundaries |
| Cross-midnight evidence | D08 Session 03 retains filename ending `20260907-002846.fit`; selected FITS stack time remains `2026-09-06 23:28:11.246013` |
| Large retained-light gaps | D08 Session 03 retains its 221.936137-second maximum gap and all 135 lights |
| Equal-time light/stack | D02/D05/D09 final-light equality is asserted |
| Structural mosaic naming and Unknown | D02/D05/D07/D09 preserve source names; D02 target remains Unknown |
| RGB with BAYERPAT=GRBG | All 11 stacks remain classified RGB_IMAGE with GRBG evidence retained |
| Retained count differs from STACKCNT | D08 Session 03 remains 135 versus 106 without a false warning |

Cross-midnight refers to the frozen filename/session evidence, not an inferred timezone conversion: D08 Session 03 selected FITS light times remain `2026-09-06 21:58:56.320616` through `2026-09-06 23:27:40.288955`. All three archive dates remain `20260907` under the unchanged +12-hour rule.

### Diagnostics and deferred features

Zero diagnostics attributable to F8-01/F8-02/F8-03/F8-03A/F8-04 remain. There is one existing discovery diagnostic per dataset (nine total), at the exact item `<dataset>/.DS_Store`: `Unsupported source-file extension: <none>`. These are **expected informational filesystem-metadata exclusions**, not remediation defects. They do not become observations or planning problems. No other discovery problem remains.

DF8-01 typed mosaic evidence and DF8-02 target correction/override remain deferred. No typed mosaic state, dimension/WCS inference, override, new grouping heuristic, cadence change or unrelated cleanup was implemented.

### Dataset preservation

Before/after manifests match exactly for all nine datasets and the full corpus root. Sorted manifest rows record relative path, type/mode, byte size, mtime_ns, ctime_ns and a full-content SHA-256 for each file; directory state is included. Access times are excluded because reads can affect them. Each table fingerprint is SHA-256 of the compact sorted JSON manifest for that dataset.

| Dataset | Files before / after | Bytes before / after | State/content fingerprint before = after |
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

Dataset subtotal: **1,020 files, 2,061,243,868 bytes**, unchanged. The entire-root count includes three additional existing metadata files. No source was modified, renamed, moved, deleted or copied. No archive COPY/MOVE was executed against the corpus. The full pytest suite separately exercises execution behavior on its own temporary fixtures.

### Git diff/status and artifacts

| State | File | Explanation |
|---|---|---|
| M, pre-existing | `docs/CHANGELOG.md` | Intentional pending Stage 8.2f entry, preserved byte-for-byte |
| ?? | `docs/change_documents/STAGE_8/STAGE_8.2g.md` | Existing untracked specification, status updated and this report appended |

These are the only working-tree changes. No production or test-code changes were made. Prior Stage 8.2e and Stage 8.2f documents are byte-for-byte unchanged. No staging, commit, branch change or closure implementation occurred.

Temporary artifacts outside the repository: `/tmp/stage82g_preexisting.json`, `/tmp/stage82g_validate.py`, `/tmp/stage82g_report.py`, `/tmp/stage82g_qualification.txt`, and `/tmp/stage82g_evidence/{before.json,after.json,results.json,preservation.json}`. They contain validation scripts, logs, metadata and membership paths, not dataset copies.

### Closure recommendation

The evidence is sufficient to formally close Stage 8.2 remediation and proceed to a separately defined final Stage 8 closure validation without reopening any of the five remediation designs. This report records readiness only: Stage 8 closure work has not begun, no formal closure implementation was performed, and no commit was created. The historical Stage 8.2e FAIL remains intact.

### Individual closure criteria

**117 / 117 PASS.**

| # | Result | Criterion and supporting evidence |
|---|---|---|
| 1 | PASS | Actual starting HEAD is recorded and matches `491ce26` or difference is explained. See starting state, preserved hashes and final two-file Git status. |
| 2 | PASS | Pending CHANGELOG entry is identified as intentional. See starting state, preserved hashes and final two-file Git status. |
| 3 | PASS | No unexpected pre-existing working-tree changes are ignored. See starting state, preserved hashes and final two-file Git status. |
| 4 | PASS | No production-code change is made unless a genuine regression requires it. See starting state, preserved hashes and final two-file Git status. |
| 5 | PASS | No test-code change is made unless a genuine regression requires it. See starting state, preserved hashes and final two-file Git status. |
| 6 | PASS | Focused F8-01 regressions pass. All 100 focused remediation tests pass. |
| 7 | PASS | Focused F8-02 regressions pass. All 100 focused remediation tests pass. |
| 8 | PASS | Focused F8-03 regressions pass. All 100 focused remediation tests pass. |
| 9 | PASS | Focused F8-03A regressions pass. All 100 focused remediation tests pass. |
| 10 | PASS | Focused F8-04 regressions pass. All 100 focused remediation tests pass. |
| 11 | PASS | Full repository pytest passes. 314 tests pass. |
| 12 | PASS | Ruff passes. Ruff check passes. |
| 13 | PASS | `git diff --check` passes. Whitespace/diff check passes. |
| 14 | PASS | Formatting validation passes where applicable. 27 scoped files pass formatting; no Python files changed. |
| 15 | PASS | Dataset 01 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 16 | PASS | Dataset 01 retains 18 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 17 | PASS | Dataset 02 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 18 | PASS | Dataset 02 retains 13 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 19 | PASS | Dataset 03 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 20 | PASS | Dataset 03 retains 18 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 21 | PASS | Dataset 04 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 22 | PASS | Dataset 04 retains 12 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 23 | PASS | Dataset 05 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 24 | PASS | Dataset 05 retains 12 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 25 | PASS | Dataset 06 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 26 | PASS | Dataset 06 retains 16 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 27 | PASS | Dataset 07 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 28 | PASS | Dataset 07 retains 77 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 29 | PASS | Dataset 08 reconstructs exactly 3 COMPLETE observations. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 30 | PASS | Dataset 08 memberships remain 12 / 1 / 135. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 31 | PASS | Dataset 09 reconstructs exactly 1 COMPLETE observation. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 32 | PASS | Dataset 09 retains 12 lights. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 33 | PASS | Total reconstruction count remains exactly 11. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 34 | PASS | All expected stack assignments remain correct. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 35 | PASS | No unexpected LIGHTS_ONLY observations appear. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 36 | PASS | No unexpected STACK_ONLY observations appear. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 37 | PASS | No unexpected AMBIGUOUS observations appear. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 38 | PASS | No unexpected UNRESOLVED observations appear. See nine-dataset reconstruction table and exact membership/stack comparison. |
| 39 | PASS | F8-01 remains resolved in Dataset 02. Equal-time attachment and no backward assignment asserted in the corpus sweep. |
| 40 | PASS | F8-01 remains resolved in Dataset 05. Equal-time attachment and no backward assignment asserted in the corpus sweep. |
| 41 | PASS | F8-01 remains resolved in Dataset 09. Equal-time attachment and no backward assignment asserted in the corpus sweep. |
| 42 | PASS | F8-02 false timestamp diagnostics are zero across all nine datasets. FITS authority assertions and authority/fallback regressions pass; no code changes. |
| 43 | PASS | FITS timestamp authority remains intact. FITS authority assertions and authority/fallback regressions pass; no code changes. |
| 44 | PASS | Filename fallback remains intact. FITS authority assertions and authority/fallback regressions pass; no code changes. |
| 45 | PASS | No timezone inference is introduced. FITS authority assertions and authority/fallback regressions pass; no code changes. |
| 46 | PASS | No network dependency is introduced. FITS authority assertions and authority/fallback regressions pass; no code changes. |
| 47 | PASS | Dataset 02 discovery F8-03 diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 48 | PASS | Dataset 05 discovery F8-03 diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 49 | PASS | Dataset 07 discovery F8-03 diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 50 | PASS | Dataset 09 discovery F8-03 diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 51 | PASS | Dataset 02 archive-planning F8-03A diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 52 | PASS | Dataset 05 archive-planning F8-03A diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 53 | PASS | Dataset 07 archive-planning F8-03A diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 54 | PASS | Dataset 09 archive-planning F8-03A diagnostics remain zero. Affected datasets have zero target conflicts at discovery and planning. |
| 55 | PASS | Dataset 02 target remains legitimate `Unknown`. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 56 | PASS | Original source paths remain unchanged. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 57 | PASS | Original stored directory evidence remains unchanged. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 58 | PASS | FITS target evidence remains unchanged. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 59 | PASS | Discovery/planning mosaic comparison semantics remain consistent. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 60 | PASS | No typed mosaic state is introduced. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 61 | PASS | No dimensions-based mosaic inference is introduced. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 62 | PASS | No WCS-based mosaic inference is introduced. Inventory preservation assertions and shared-comparison tests pass; no model or policy changes. |
| 63 | PASS | Dataset 08 Session 03 retains 135 source lights. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 64 | PASS | Dataset 08 Session 03 STACKCNT remains 106. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 65 | PASS | Dataset 08 Session 03 TOTALEXP remains 3180. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 66 | PASS | Dataset 08 Session 03 EXPTIME remains 30. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 67 | PASS | Dataset 08 Session 03 emits no retained-count-vs-STACKCNT warning. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 68 | PASS | Dataset 08 Session 03 emits no false replacement stack diagnostic. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 69 | PASS | STACKCNT remains independent of source membership. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 70 | PASS | Dataset 08 cross-midnight behaviour remains intact. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 71 | PASS | Dataset 08 large-gap behaviour remains intact. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 72 | PASS | Dataset 08 intermediate-stack boundaries remain intact. See D08 metadata and behavioural coverage: 12/1/135 lights, final header 106/3180/30. |
| 73 | PASS | Dataset 01 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 74 | PASS | Dataset 02 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 75 | PASS | Dataset 03 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 76 | PASS | Dataset 04 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 77 | PASS | Dataset 05 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 78 | PASS | Dataset 06 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 79 | PASS | Dataset 07 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 80 | PASS | Dataset 08 archive plan count is 3. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 81 | PASS | Dataset 09 archive plan count is 1. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 82 | PASS | Total archive plan count remains exactly 11. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 83 | PASS | Dataset 01 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 84 | PASS | Dataset 02 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 85 | PASS | Dataset 03 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 86 | PASS | Dataset 04 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 87 | PASS | Dataset 05 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 88 | PASS | Dataset 06 archive date is `20260906`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 89 | PASS | Dataset 07 archive date is `20260906`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 90 | PASS | All Dataset 08 archive dates are `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 91 | PASS | Dataset 09 archive date is `20260907`. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 92 | PASS | No archive-planning regression remains. See nine-dataset archive table: 11 exact plans, expected dates, zero planning diagnostics/problems. |
| 93 | PASS | AltAz behaviour remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 94 | PASS | EQ behaviour remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 95 | PASS | Firmware 7.75 compatibility remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 96 | PASS | Firmware 8.46 compatibility remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 97 | PASS | Firmware 9.31 compatibility remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 98 | PASS | RGB stacked FITS with `BAYERPAT=GRBG` remain correctly classified. See firmware/mount/image classification and behavioural coverage table. |
| 99 | PASS | Equal-time light/stack behaviour remains intact. See firmware/mount/image classification and behavioural coverage table. |
| 100 | PASS | Structural mosaic filesystem naming remains supported. See firmware/mount/image classification and behavioural coverage table. |
| 101 | PASS | Retained-light count differing from STACKCNT remains supported. See firmware/mount/image classification and behavioural coverage table. |
| 102 | PASS | DF8-01 remains deferred. No production code changed; deferred features and existing policies are preserved. |
| 103 | PASS | DF8-02 remains deferred. No production code changed; deferred features and existing policies are preserved. |
| 104 | PASS | Archive hierarchy remains unchanged. No production code changed; deferred features and existing policies are preserved. |
| 105 | PASS | Observation numbering remains unchanged. No production code changed; deferred features and existing policies are preserved. |
| 106 | PASS | +12-hour archive-date policy remains unchanged. No production code changed; deferred features and existing policies are preserved. |
| 107 | PASS | Cadence/grouping thresholds remain unchanged. No production code changed; deferred features and existing policies are preserved. |
| 108 | PASS | No complete dataset is copied into the repository. Read-only qualification; before/after state and full-content fingerprints match. |
| 109 | PASS | No archive COPY is executed. Read-only qualification; before/after state and full-content fingerprints match. |
| 110 | PASS | No archive MOVE is executed. Read-only qualification; before/after state and full-content fingerprints match. |
| 111 | PASS | All nine datasets remain unchanged after qualification. Read-only qualification; before/after state and full-content fingerprints match. |
| 112 | PASS | Every changed file is identified. See complete Git status, diagnostics classification and scope statement. |
| 113 | PASS | No unrelated cleanup/refactor is included. See complete Git status, diagnostics classification and scope statement. |
| 114 | PASS | No Stage 8 closure implementation is started. See complete Git status, diagnostics classification and scope statement. |
| 115 | PASS | Any unexpected discrepancy is explicitly classified. See complete Git status, diagnostics classification and scope statement. |
| 116 | PASS | Evidence is sufficient to formally close Stage 8.2 remediation. All combined acceptance evidence passes; readiness is recorded without starting closure work. |
| 117 | PASS | Evidence is sufficient to proceed to final Stage 8 closure validation without reopening F8-01/F8-02/F8-03/F8-03A/F8-04. All combined acceptance evidence passes; readiness is recorded without starting closure work. |
