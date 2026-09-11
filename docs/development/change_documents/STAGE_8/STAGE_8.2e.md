# Stage 8.2e — Full Real-Data Remediation Regression

## Status

FAIL — validation completed 2026-09-08; remaining F8-03 archive-planning diagnostics block closure.

## Purpose

Validate the complete Stage 8 remediation set against the frozen nine-dataset real-data corpus after all four confirmed Stage 8.1 findings have been corrected.

Stage 8.2e is a regression-validation stage.

It must not introduce new remediation unless the validation discovers a genuine regression or previously hidden defect.

Confirmed remediations now present:

- F8-01 — equal-time reconstruction ordering — fixed in Stage 8.2a;
- F8-02 — filename/FITS timestamp diagnostic semantics — fixed in Stage 8.2b;
- F8-03 — structural mosaic suffix target comparison — fixed in Stage 8.2c;
- F8-04 — stack-count diagnostic semantics — fixed in Stage 8.2d.

The goal is to prove that all four fixes coexist correctly across the full frozen corpus and that no cross-remediation regression has been introduced.

## Starting Commit

Expected starting commit:

`02d92ce` — Stage 8.2d: correct stack-count diagnostic semantics

Before validation begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.2d entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.2e.md` document may also be present as an intentional uncommitted documentation change.

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

Do not repeat ground-truth discovery. The Stage 8 frozen evidence is authoritative.

## Frozen Expected Observation Truth

Exactly **11 observations** must be reconstructed.

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

All expected stacks must remain correctly assigned.

No extra LIGHTS_ONLY, STACK_ONLY, AMBIGUOUS or UNRESOLVED observations are expected in the frozen corpus.

## Required Validation

Stage 8.2e must validate all of the following together.

### F8-01 — Equal-Time Reconstruction Ordering

Datasets 02, 05 and 09 must remain corrected.

Expected:

- Dataset 02: one COMPLETE observation with 13 lights;
- Dataset 05: one COMPLETE observation with 12 lights;
- Dataset 09: one COMPLETE observation with 12 lights;
- no trailing LIGHTS_ONLY observation;
- equal-time compatible final light remains associated with its stack;
- no later-light back-assignment regression.

### F8-02 — Filename/FITS Timestamp Diagnostic Semantics

Across all nine datasets:

- authoritative FITS timestamps remain selected where present;
- filename timestamps remain fallback evidence;
- false local-wall-clock versus FITS-UTC conflict diagnostics remain zero;
- no timezone inference is introduced;
- no network dependency is introduced.

### F8-03 — Mosaic Target Comparison

Datasets 02, 05, 07 and 09:

- structural `_mosaic` / `_mosaic_sub` comparison diagnostics remain zero;
- original paths and stored evidence remain unchanged;
- legitimate target `Unknown` in Dataset 02 remains supported;
- no typed mosaic field is required;
- mosaic state must not affect reconstruction.

### F8-04 — Stack-Count Diagnostic Semantics

Dataset 08 Session 03:

- retains all 135 source lights;
- reported `STACKCNT` remains 106;
- `TOTALEXP` remains 3180;
- `EXPTIME` remains 30;
- no retained-count-versus-STACKCNT warning;
- no false replacement diagnostic;
- reconstruction membership remains independent of STACKCNT.

The valid metadata relationship remains:

`STACKCNT == TOTALEXP / EXPTIME`

where all required values are present.

## Archive-Planning Validation

Run read-only archive planning for every dataset.

Expected:

- one planned observation for each single-observation dataset;
- three planned observations for Dataset 08;
- total planned observations across corpus: 11;
- no planning problems caused by Stage 8.2 remediations.

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

If existing frozen Stage 8 evidence records a different archive date for any dataset, report the discrepancy before changing anything.

Do not alter the +12-hour astronomical-night/archive-date rule.

## Behavioural Coverage

Confirm the corpus still exercises and passes:

- AltAz captures;
- EQ captures;
- firmware 7.75;
- firmware 8.46;
- firmware 9.31;
- single observations;
- multiple observations of the same target in one night;
- cross-midnight observations;
- large retained-light gaps;
- equal light/stack timestamps;
- explicit mosaic directory naming;
- target `Unknown`;
- RGB stacked FITS that still contain `BAYERPAT=GRBG`;
- source-light counts that differ from STACKCNT.

## Diagnostics

The full corpus should contain no remaining diagnostics attributable to F8-01, F8-02, F8-03 or F8-04.

If any diagnostic remains:

1. identify the exact dataset and item;
2. classify whether it is:
   - expected informational evidence;
   - a deferred feature;
   - a regression;
   - a newly discovered defect;
3. do not silently suppress it;
4. do not remediate it in Stage 8.2e unless required to correct a genuine Stage 8 regression and clearly justified.

## Deferred Features

The following remain out of scope:

### DF8-01 — Typed Mosaic Evidence

Do not add typed mosaic state.

### DF8-02 — Target Correction / Override

Do not add target-name correction, interactive override, or archive-target rewriting.

Both must remain deferred.

## Automated Validation

Run:

`python -m pytest`

`ruff check .`

`git diff --check`

Run project-standard formatting validation for any files changed during Stage 8.2e.

No production-code changes are expected in a clean PASS.

If no production code changes are required, that itself is useful validation evidence.

## Read-Only Corpus Qualification

The nine external datasets must remain unchanged.

Before and after qualification, capture preservation evidence sufficient to demonstrate no mutation.

At minimum include:

- file count;
- total bytes;
- content or state fingerprint.

Do not:

- modify;
- rename;
- move;
- delete;
- copy complete datasets into the repository;
- execute archive COPY;
- execute archive MOVE.

Archive planning must remain read-only.

## Scope

Stage 8.2e includes:

1. record starting repository state;
2. run focused Stage 8 remediation regression tests;
3. run full automated validation;
4. run full nine-dataset discovery/reconstruction sweep;
5. run read-only archive planning for all nine datasets;
6. compare results with frozen expected truth;
7. verify all four remediation findings remain resolved;
8. verify no new cross-remediation regression;
9. verify external datasets are unchanged;
10. report any unexpected finding without opportunistic unrelated fixes;
11. establish whether Stage 8 remediation can be closed.

## Exclusions

Do not:

- change F8-01 design;
- change F8-02 design;
- change F8-03 design;
- change F8-04 design;
- add new reconstruction heuristics;
- alter cadence thresholds;
- alter timestamp precedence;
- alter filename fallback;
- add timezone inference;
- add typed mosaic metadata;
- add target correction/override;
- change STACKCNT membership semantics;
- change archive hierarchy;
- change observation numbering;
- change +12-hour archive-date logic;
- copy complete datasets into the repository;
- execute archive COPY/MOVE;
- begin Stage 8 closure work beyond reporting readiness;
- include unrelated cleanup or refactoring.

## Expected Outcome

A clean PASS should demonstrate:

- all 304+ repository tests pass;
- all 11 frozen observations reconstruct correctly;
- all archive plans match expected counts and dates;
- F8-01 remains resolved;
- F8-02 remains resolved;
- F8-03 remains resolved;
- F8-04 remains resolved;
- no new diagnostics or regressions are introduced;
- no production change is required;
- external datasets remain unchanged.

## Completion Report

Return a complete Stage 8.2e completion report containing:

### Stage 8.2e Result

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

### Automated Validation

Report:

- focused remediation tests;
- full pytest;
- Ruff;
- formatting;
- `git diff --check`.

### Full Corpus Reconstruction

Provide a table for all nine datasets with:

- observation count;
- status;
- light membership;
- assigned stack;
- logical target;
- remaining diagnostic count.

### Archive Planning

Provide a table for all nine datasets with:

- plan count;
- archive date(s);
- planning problems.

### Remediation Verification

Report F8-01, F8-02, F8-03 and F8-04 separately.

### Behavioural Coverage

Confirm firmware, mount mode, mosaic, Unknown, cross-midnight, large-gap and equal-time cases remain correct.

### Deferred Features

Confirm DF8-01 and DF8-02 remain deferred.

### Dataset Preservation

Provide before/after preservation evidence.

### Git Diff Summary

List every changed file.

A clean validation PASS should ideally change only:

- `docs/CHANGELOG.md` as pre-existing pending documentation;
- `docs/change_documents/STAGE_8/STAGE_8.2e.md`.

If anything else changes, explain why.

### Closure Recommendation

State whether the evidence is sufficient to close Stage 8.2 remediation and proceed to Stage 8 closure validation.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.2e is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `02d92ce` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. No production-code change is made unless a genuine regression requires it.
4. Focused F8-01 regression coverage passes.
5. Focused F8-02 regression coverage passes.
6. Focused F8-03 regression coverage passes.
7. Focused F8-04 regression coverage passes.
8. Full repository pytest passes.
9. Ruff passes.
10. `git diff --check` passes.
11. Formatting validation passes where applicable.
12. Dataset 01 reconstructs exactly one COMPLETE observation.
13. Dataset 01 retains 18 lights.
14. Dataset 02 reconstructs exactly one COMPLETE observation.
15. Dataset 02 retains 13 lights.
16. Dataset 03 reconstructs exactly one COMPLETE observation.
17. Dataset 03 retains 18 lights.
18. Dataset 04 reconstructs exactly one COMPLETE observation.
19. Dataset 04 retains 12 lights.
20. Dataset 05 reconstructs exactly one COMPLETE observation.
21. Dataset 05 retains 12 lights.
22. Dataset 06 reconstructs exactly one COMPLETE observation.
23. Dataset 06 retains 16 lights.
24. Dataset 07 reconstructs exactly one COMPLETE observation.
25. Dataset 07 retains 77 lights.
26. Dataset 08 reconstructs exactly three COMPLETE observations.
27. Dataset 08 memberships remain 12, 1 and 135.
28. Dataset 09 reconstructs exactly one COMPLETE observation.
29. Dataset 09 retains 12 lights.
30. Total frozen observation count remains exactly 11.
31. All expected stack assignments remain correct.
32. No extra LIGHTS_ONLY observation appears in Dataset 02.
33. No extra LIGHTS_ONLY observation appears in Dataset 05.
34. No extra LIGHTS_ONLY observation appears in Dataset 09.
35. F8-01 remains resolved in Dataset 02.
36. F8-01 remains resolved in Dataset 05.
37. F8-01 remains resolved in Dataset 09.
38. F8-02 false timestamp diagnostics remain zero across all nine datasets.
39. FITS timestamp authority remains intact.
40. Filename timestamp fallback remains intact.
41. No timezone inference is introduced.
42. No network dependency is introduced.
43. F8-03 false mosaic target diagnostics remain zero in Dataset 02.
44. F8-03 false mosaic target diagnostics remain zero in Dataset 05.
45. F8-03 false mosaic target diagnostics remain zero in Dataset 07.
46. F8-03 false mosaic target diagnostics remain zero in Dataset 09.
47. Dataset 02 legitimate target `Unknown` remains intact.
48. Original source paths/evidence remain unchanged by F8-03 behaviour.
49. No typed mosaic state is introduced.
50. Dataset 08 Session 03 retains all 135 source lights.
51. Dataset 08 Session 03 reported STACKCNT remains 106.
52. Dataset 08 Session 03 TOTALEXP remains 3180.
53. Dataset 08 Session 03 EXPTIME remains 30.
54. Dataset 08 Session 03 emits no retained-count-vs-STACKCNT warning.
55. Dataset 08 Session 03 emits no false replacement stack-count diagnostic.
56. STACKCNT remains independent of source-light membership.
57. Dataset 08 cross-midnight behaviour remains intact.
58. Dataset 08 large-gap stack-backed behaviour remains intact.
59. Dataset 08 intermediate stack boundaries remain intact.
60. Dataset 01 archive plan count is 1.
61. Dataset 02 archive plan count is 1.
62. Dataset 03 archive plan count is 1.
63. Dataset 04 archive plan count is 1.
64. Dataset 05 archive plan count is 1.
65. Dataset 06 archive plan count is 1.
66. Dataset 07 archive plan count is 1.
67. Dataset 08 archive plan count is 3.
68. Dataset 09 archive plan count is 1.
69. Total archive plan count is 11.
70. Dataset 01 archive date is 20260907.
71. Dataset 02 archive date is 20260907.
72. Dataset 03 archive date is 20260907.
73. Dataset 04 archive date is 20260907.
74. Dataset 05 archive date is 20260907.
75. Dataset 06 archive date is 20260906.
76. Dataset 07 archive date is 20260906.
77. All Dataset 08 archive dates are 20260907.
78. Dataset 09 archive date is 20260907.
79. No planning regression attributable to Stage 8.2 fixes is present.
80. AltAz behaviour remains intact.
81. EQ behaviour remains intact.
82. Firmware 7.75 compatibility remains intact.
83. Firmware 8.46 compatibility remains intact.
84. Firmware 9.31 compatibility remains intact.
85. RGB stacked FITS with `BAYERPAT=GRBG` remain correctly classified.
86. Equal-time light/stack behaviour remains intact.
87. Explicit mosaic filesystem naming remains supported.
88. Retained-light-count differing from STACKCNT remains supported.
89. DF8-01 typed mosaic evidence remains deferred.
90. DF8-02 target correction/override remains deferred.
91. Archive hierarchy remains unchanged.
92. Observation numbering remains unchanged.
93. +12-hour archive-date policy remains unchanged.
94. Cadence/grouping thresholds remain unchanged.
95. No complete external dataset is copied into the repository.
96. No archive COPY operation is executed.
97. No archive MOVE operation is executed.
98. All nine datasets remain unchanged after qualification.
99. Every changed file is identified.
100. No unrelated refactor or cleanup is included.
101. No Stage 8.3 or later-stage implementation is started.
102. Completion report distinguishes confirmed remediations from deferred features.
103. Any unexpected diagnostic or discrepancy is explicitly classified rather than silently ignored.
104. Evidence is sufficient to determine whether Stage 8.2 remediation can be formally closed.
105. Evidence is sufficient to proceed to Stage 8 closure validation without reopening F8-01 through F8-04 design.

## Expected Next Step

If Stage 8.2e passes cleanly, formally close Stage 8.2 remediation.

Then define the final Stage 8 closure/validation step using the established project workflow before Stage 8 itself is closed.

## Stage 8.2e Completion Report — 2026-09-08

**Result: FAIL.** Qualification is finished, but remediation is not ready for closure. All 11 observations and all archive counts/dates match frozen truth. Four false structural mosaic target diagnostics remain in archive-plan metadata (D02/D05/D07/D09). No production or test changes were made.

### Environment and starting state

- Starting and ending HEAD: `02d92ce1e9b905889b3498d1266d2644a1e2d05b` — Stage 8.2d: correct stack-count diagnostic semantics.
- Initial tree: modified `docs/CHANGELOG.md` (the intentional two-line Stage 8.2d entry) and untracked `docs/change_documents/STAGE_8/STAGE_8.2e.md`. No unexpected changes.
- Python: `<development-environment>/bin/python`, 3.13.15; pytest 9.1.1; Ruff 0.16.0.
- Imported package: `<repository-root>/src/seestar_toolkit/__init__.py`.
- Used the specified frozen corpus and expectations; no ground-truth discovery was repeated. Dataset IDs below refer to the exact dataset directory names listed above.

### Automated validation

| Check | Result |
|---|---|
| Focused discovery/reconstruction unit and integration tests | 48 passed in 0.68s |
| `python -m pytest` | 304 passed in 11.26s |
| `ruff check .` | PASS |
| `ruff format --check` for archive source/tests, discovery/reconstruction integration tests and this document | PASS: 25 files already formatted |
| Broader `ruff format --check .` | FAIL: 16 pre-existing files would be reformatted; 119 already formatted |
| `git diff --check` | PASS |

Commands used the project virtual environment executables. Focused files: `tests/unit/archive/test_reconstruction.py`, `tests/unit/archive/test_discovery.py`, `tests/integration/test_archive_reconstruction.py`, `tests/integration/test_archive_discovery.py`. These cover equal-time compatibility/order and later-light rejection, FITS authority and filename fallback, comparison-only mosaic suffix handling and genuine mismatches, retained counts above/below STACKCNT, missing STACKCNT and contradictory stack metadata. No tests were added, changed, weakened or skipped.

The broad formatting failure is pre-existing repository formatting debt, not a remediation regression. All 16 files are unchanged from HEAD; no unrelated formatting was applied:

- `docs/change_documents/STAGE_2/STAGE_2.2b.1.md`
- `docs/change_documents/STAGE_2/STAGE_2.2b.2.md`
- `docs/change_documents/STAGE_2/STAGE_2.2c.md`
- `docs/change_documents/STAGE_2/STAGE_2.2d.md`
- `src/seestar_toolkit/fits/exceptions.py`
- `src/seestar_toolkit/fits/inspector.py`
- `src/seestar_toolkit/fits/models.py`
- `src/seestar_toolkit/fits/reader.py`
- `src/seestar_toolkit/models.py`
- `tests/unit/fits/test_exceptions.py`
- `tests/unit/fits/test_inspection_models.py`
- `tests/unit/fits/test_inspector.py`
- `tests/unit/fits/test_models.py`
- `tests/unit/fits/test_reader.py`
- `tools/astropy_hdu_viewer.py`
- `tools/inspect_fits.py`

### Full corpus reconstruction

Diagnostic columns count discovery item problems / reconstruction observation problems / archive metadata diagnostics separately. Each discovery problem is the expected excluded `.DS_Store` item, classified below. Stack paths are relative to their dataset root.

| Dataset | Observations/status | Lights | Assigned stack(s) | Logical target | Diagnostics D/R/A |
|---|---|---|---|---|---|
| D01 | 1 COMPLETE | 18 | `C 27/Stacked_18_C 27_10.0s_IRCUT_20260906-210540.fit` | C 27 | 1/0/0 |
| D02 | 1 COMPLETE | 13 | `Unknown_mosaic/Stacked_13_mosaic_Unknown_10.0s_IRCUT_20260906-211429.fit` | Unknown | 1/0/1 |
| D03 | 1 COMPLETE | 18 | `NGC 6888/Stacked_18_NGC 6888_10.0s_LP_20260906-212307.fit` | NGC 6888 | 1/0/0 |
| D04 | 1 COMPLETE | 12 | `M 27/Stacked_12_M 27_10.0s_LP_20260906-221431.fit` | M 27 | 1/0/0 |
| D05 | 1 COMPLETE | 12 | `NGC 6888_mosaic/Stacked_12_mosaic_NGC 6888_10.0s_LP_20260906-221937.fit` | NGC 6888 | 1/0/1 |
| D06 | 1 COMPLETE | 16 | `IC 1318/Stacked_16_IC 1318_10.0s_LP_20260905-214129.fit` | IC 1318 | 1/0/0 |
| D07 | 1 COMPLETE | 77 | `IC 5070_mosaic/Stacked_77_mosaic_IC 5070_10.0s_LP_20260905-220832.fit` | IC 5070 | 1/0/1 |
| D08 | 3 COMPLETE | 12 / 1 / 135 | `M 57/Stacked_12_M 57_10.0s_LP_20260906-224631.fit`<br>`M 57/Stacked_1_M 57_10.0s_LP_20260906-225738.fit`<br>`M 57/Stacked_106_M 57_30.0s_LP_20260907-002846.fit` | M 57 | 1/0/0 |
| D09 | 1 COMPLETE | 12 | `NGC 281W_mosaic/Stacked_12_mosaic_NGC 281W_10.0s_LP_20260906-225304.fit` | NGC 281W | 1/0/1 |

Exactly 326 lights and 11 stacks are assigned once each, without duplicate membership or unassigned FITS lights/stacks. All assigned lights precede or equal their stack timestamp. There are no LIGHTS_ONLY, STACK_ONLY, AMBIGUOUS or UNRESOLVED observations.

### Read-only archive planning

Called `plan_seestar_archive` directly on every reconstruction, using `/tmp/stage82e_uncreated_archive` as a nominal root. No archive directory was created. No explicit location or saved-location mapping was supplied, so the existing `unknown` location fallback applies. Default hierarchy remains `{target}/{location}/{session_end_date}`.

| Dataset | Plans | Dates | Blocking planning problems | Metadata diagnostics |
|---|---|---|---|---|
| D01 | 1 | 20260907 | 0 | 0 |
| D02 | 1 | 20260907 | 0 | 1 |
| D03 | 1 | 20260907 | 0 | 0 |
| D04 | 1 | 20260907 | 0 | 0 |
| D05 | 1 | 20260907 | 0 | 1 |
| D06 | 1 | 20260906 | 0 | 0 |
| D07 | 1 | 20260906 | 0 | 1 |
| D08 | 3 | 20260907 / 20260907 / 20260907 | 0 | 0 |
| D09 | 1 | 20260907 | 0 | 1 |

Total: 11 plans. Single datasets use `observation_01`; D08 uses `observation_01`, `observation_02`, `observation_03` in chronological order. All specified dates match; no contradictory archive date was found in the consulted frozen Stage 8 documents. The +12-hour policy is unchanged. A zero blocking-problem count does not mean zero metadata diagnostics.

### Remediation verification and findings

**F8-01 — PASS.** D02/D05/D09 retain 13/12/12 lights in one COMPLETE observation each. Last-light and stack authoritative timestamps are equal, respectively `2026-09-06 20:14:08.453031`, `2026-09-06 21:19:09.055769`, and `2026-09-06 21:52:36.968517`. No trailing LIGHTS_ONLY observation or later-light back-assignment exists. Focused negative and deterministic-order tests pass.

**F8-02 — PASS.** No false FITS/filename conflict diagnostic occurs at discovery, reconstruction or planning. Every discovered FITS item with authoritative FITS time selects that time. Filename fallback and authority tests pass. No timestamp precedence changes, timezone inference or network dependency were introduced.

**F8-03 — FAIL at archive planning; PASS at discovery/reconstruction.** Original paths and directory/FITS target evidence remain preserved; `Unknown` is intact. However, `src/seestar_toolkit/archive/planning.py::_resolve_target` compares stored directory evidence directly with the FITS target, without the structural suffix comparison normalization used by discovery. Exact affected planned items and messages:

- D02, `/tmp/stage82e_uncreated_archive/Unknown/unknown/20260907/observation_01` (assigned stack: `Unknown_mosaic/Stacked_13_mosaic_Unknown_10.0s_IRCUT_20260906-211429.fit`): `FITS target 'Unknown' conflicts with directory evidence ('Unknown_mosaic',)`.
- D05, `/tmp/stage82e_uncreated_archive/NGC 6888/unknown/20260907/observation_01` (assigned stack: `NGC 6888_mosaic/Stacked_12_mosaic_NGC 6888_10.0s_LP_20260906-221937.fit`): `FITS target 'NGC 6888' conflicts with directory evidence ('NGC 6888_mosaic',)`.
- D07, `/tmp/stage82e_uncreated_archive/IC 5070/unknown/20260906/observation_01` (assigned stack: `IC 5070_mosaic/Stacked_77_mosaic_IC 5070_10.0s_LP_20260905-220832.fit`): `FITS target 'IC 5070' conflicts with directory evidence ('IC 5070_mosaic',)`.
- D09, `/tmp/stage82e_uncreated_archive/NGC 281W/unknown/20260907/observation_01` (assigned stack: `NGC 281W_mosaic/Stacked_12_mosaic_NGC 281W_10.0s_LP_20260906-225304.fit`): `FITS target 'NGC 281W' conflicts with directory evidence ('NGC 281W_mosaic',)`.

Classification: **newly discovered, previously hidden defect in the remaining F8-03 diagnostic path**, not expected informational evidence and not DF8-01/DF8-02. The planning module last changed at `7c1086f` (Stage 7.1d), before the four remediation commits. No evidence indicates a newly introduced cross-remediation regression; Stage 8.2c corrected discovery but left this independent comparison path unchanged. All four plans still have correct targets, counts, dates and destinations. The zero-warning requirement nevertheless fails. No diagnostic was suppressed and no opportunistic fix was made.

**F8-04 — PASS.** Direct read-only FITS header inspection confirms D08 Session 03 `STACKCNT=106`, `TOTALEXP=3180.0`, `EXPTIME=30.0`; `3180/30=106`. Reconstruction retains all 135 lights and emits no retained-count or replacement stack diagnostic. All 11 stacks satisfy the metadata relationship; STACKCNT is independent of source-light membership.

**Other diagnostics:** each dataset has exactly one discovery item at `<dataset>/.DS_Store` with `Unsupported source-file extension: <none>`. These nine items are expected informational evidence for unsupported filesystem metadata, excluded from reconstruction, with no effect on planning. This identifies the exact item in every dataset; no other discovery problems or observation problems remain.

### Behavioural coverage and preserved boundaries

- AltAz: D01–D05; EQ: D06–D09. Stack metadata confirms firmware 8.46 in D01–D03, 9.31 in D04/D05/D08/D09, and 7.75 in D06/D07.
- All 11 stacked FITS classify as RGB_IMAGE while retaining `BAYERPAT=GRBG`.
- Single observations, explicit mosaic paths, target `Unknown`, equal-time boundaries and retained-count/STACKCNT differences retain correct membership. The archive mosaic diagnostic exception is reported above.
- D08 remains three separate COMPLETE observations with 12 / 1 / 135 lights. Its intermediate stacks preserve session boundaries. Session 03 maximum retained-light gap is 221.936137 seconds and is still supported by its stack.
- D08 Session 03 selected FITS times span `2026-09-06 21:58:56.320616` to `2026-09-06 23:27:40.288955`, with stack time `2026-09-06 23:28:11.246013`. Frozen cross-midnight filename evidence remains visible in the stack name ending `20260907-002846.fit`; selected FITS times stay on September 6. No timezone inference or filename-driven date override was performed. All three archive dates are `20260907`.
- No production changes: cadence/grouping thresholds, semantic ordering, archive hierarchy, numbering and +12-hour date rule are unchanged.
- DF8-01 typed mosaic evidence and DF8-02 target correction/override remain deferred. Neither is required to classify the planning defect; neither was implemented.

### Dataset preservation

Before/after manifests matched exactly. Each sorted manifest row records relative path, mode/type, size, mtime_ns, ctime_ns and (for files) full-content SHA-256. Directory state is included; access times are excluded because reads can update them. The fingerprints below are SHA-256 of compact JSON for the applicable sorted rows. Counts, bytes and fingerprints are identical before and after.

| Dataset | Files before/after | Bytes before/after | State/content fingerprint before = after |
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

Nine dataset subtotal: 1,020 files, 2,061,243,868 bytes. Entire root includes three additional existing metadata files. No external dataset was modified, renamed, moved, deleted or copied. No external archive COPY/MOVE was executed. The full pytest suite exercises execution using its own temporary fixtures, not this external corpus.

### Git diff and validation artifacts

- `docs/CHANGELOG.md`: pre-existing two-line Stage 8.2d entry, preserved without editing.
- `docs/change_documents/STAGE_8/STAGE_8.2e.md`: existing untracked specification; status updated and this completion report appended. The authoritative requirements and all original closure criteria are retained.
- No production-code or test-code files changed. No commit, staging, branch change, cleanup or Stage 8 closure implementation occurred.
- Temporary evidence outside the repository: `/tmp/stage82e_validate.py`, `/tmp/stage82e_report.py`, `/tmp/stage82e_format.txt`, and `/tmp/stage82e_evidence/{before.json,after.json,results.json,preservation.json}`. These contain scripts, metadata and membership/path records, not dataset copies.

### Closure recommendation

Do not formally close Stage 8.2 remediation or proceed to final Stage 8 closure validation yet. The four remaining archive-planning diagnostics violate the specified F8-03 acceptance criteria. Record and authorize a narrowly scoped follow-up for that comparison path using the existing comparison-only design, then rerun qualification. No design change, typed mosaic state or target override is indicated by this evidence. Broad formatting debt is separate and does not justify unrelated cleanup here.

### Individual closure-criterion results

100 PASS; 5 FAIL (43–46 and 105). Criterion 11 applies to files changed during this stage; its PASS does not conceal the broader pre-existing formatting failure. Criterion 79 distinguishes a previously hidden planning defect from a newly introduced regression. Criterion 104 passes because the evidence establishes that closure is not yet justified.

| # | Result | Criterion and evidence |
|---|---|---|
| 1 | PASS | Actual starting Git HEAD is recorded and matches expected commit `02d92ce` or any difference is explained. |
| 2 | PASS | Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes. |
| 3 | PASS | No production-code change is made unless a genuine regression requires it. |
| 4 | PASS | Focused F8-01 regression coverage passes. |
| 5 | PASS | Focused F8-02 regression coverage passes. |
| 6 | PASS | Focused F8-03 regression coverage passes. |
| 7 | PASS | Focused F8-04 regression coverage passes. |
| 8 | PASS | Full repository pytest passes. |
| 9 | PASS | Ruff passes. |
| 10 | PASS | `git diff --check` passes. |
| 11 | PASS | Formatting validation passes where applicable. Scoped formatting passes; broad repository formatting has 16 unchanged failures. |
| 12 | PASS | Dataset 01 reconstructs exactly one COMPLETE observation. |
| 13 | PASS | Dataset 01 retains 18 lights. |
| 14 | PASS | Dataset 02 reconstructs exactly one COMPLETE observation. |
| 15 | PASS | Dataset 02 retains 13 lights. |
| 16 | PASS | Dataset 03 reconstructs exactly one COMPLETE observation. |
| 17 | PASS | Dataset 03 retains 18 lights. |
| 18 | PASS | Dataset 04 reconstructs exactly one COMPLETE observation. |
| 19 | PASS | Dataset 04 retains 12 lights. |
| 20 | PASS | Dataset 05 reconstructs exactly one COMPLETE observation. |
| 21 | PASS | Dataset 05 retains 12 lights. |
| 22 | PASS | Dataset 06 reconstructs exactly one COMPLETE observation. |
| 23 | PASS | Dataset 06 retains 16 lights. |
| 24 | PASS | Dataset 07 reconstructs exactly one COMPLETE observation. |
| 25 | PASS | Dataset 07 retains 77 lights. |
| 26 | PASS | Dataset 08 reconstructs exactly three COMPLETE observations. |
| 27 | PASS | Dataset 08 memberships remain 12, 1 and 135. |
| 28 | PASS | Dataset 09 reconstructs exactly one COMPLETE observation. |
| 29 | PASS | Dataset 09 retains 12 lights. |
| 30 | PASS | Total frozen observation count remains exactly 11. |
| 31 | PASS | All expected stack assignments remain correct. |
| 32 | PASS | No extra LIGHTS_ONLY observation appears in Dataset 02. |
| 33 | PASS | No extra LIGHTS_ONLY observation appears in Dataset 05. |
| 34 | PASS | No extra LIGHTS_ONLY observation appears in Dataset 09. |
| 35 | PASS | F8-01 remains resolved in Dataset 02. |
| 36 | PASS | F8-01 remains resolved in Dataset 05. |
| 37 | PASS | F8-01 remains resolved in Dataset 09. |
| 38 | PASS | F8-02 false timestamp diagnostics remain zero across all nine datasets. |
| 39 | PASS | FITS timestamp authority remains intact. |
| 40 | PASS | Filename timestamp fallback remains intact. |
| 41 | PASS | No timezone inference is introduced. |
| 42 | PASS | No network dependency is introduced. |
| 43 | FAIL | F8-03 false mosaic target diagnostics remain zero in Dataset 02. Discovery/reconstruction: zero; archive metadata: one false structural target warning. |
| 44 | FAIL | F8-03 false mosaic target diagnostics remain zero in Dataset 05. Discovery/reconstruction: zero; archive metadata: one false structural target warning. |
| 45 | FAIL | F8-03 false mosaic target diagnostics remain zero in Dataset 07. Discovery/reconstruction: zero; archive metadata: one false structural target warning. |
| 46 | FAIL | F8-03 false mosaic target diagnostics remain zero in Dataset 09. Discovery/reconstruction: zero; archive metadata: one false structural target warning. |
| 47 | PASS | Dataset 02 legitimate target `Unknown` remains intact. |
| 48 | PASS | Original source paths/evidence remain unchanged by F8-03 behaviour. |
| 49 | PASS | No typed mosaic state is introduced. |
| 50 | PASS | Dataset 08 Session 03 retains all 135 source lights. |
| 51 | PASS | Dataset 08 Session 03 reported STACKCNT remains 106. |
| 52 | PASS | Dataset 08 Session 03 TOTALEXP remains 3180. |
| 53 | PASS | Dataset 08 Session 03 EXPTIME remains 30. |
| 54 | PASS | Dataset 08 Session 03 emits no retained-count-vs-STACKCNT warning. |
| 55 | PASS | Dataset 08 Session 03 emits no false replacement stack-count diagnostic. |
| 56 | PASS | STACKCNT remains independent of source-light membership. |
| 57 | PASS | Dataset 08 cross-midnight behaviour remains intact. |
| 58 | PASS | Dataset 08 large-gap stack-backed behaviour remains intact. |
| 59 | PASS | Dataset 08 intermediate stack boundaries remain intact. |
| 60 | PASS | Dataset 01 archive plan count is 1. |
| 61 | PASS | Dataset 02 archive plan count is 1. |
| 62 | PASS | Dataset 03 archive plan count is 1. |
| 63 | PASS | Dataset 04 archive plan count is 1. |
| 64 | PASS | Dataset 05 archive plan count is 1. |
| 65 | PASS | Dataset 06 archive plan count is 1. |
| 66 | PASS | Dataset 07 archive plan count is 1. |
| 67 | PASS | Dataset 08 archive plan count is 3. |
| 68 | PASS | Dataset 09 archive plan count is 1. |
| 69 | PASS | Total archive plan count is 11. |
| 70 | PASS | Dataset 01 archive date is 20260907. |
| 71 | PASS | Dataset 02 archive date is 20260907. |
| 72 | PASS | Dataset 03 archive date is 20260907. |
| 73 | PASS | Dataset 04 archive date is 20260907. |
| 74 | PASS | Dataset 05 archive date is 20260907. |
| 75 | PASS | Dataset 06 archive date is 20260906. |
| 76 | PASS | Dataset 07 archive date is 20260906. |
| 77 | PASS | All Dataset 08 archive dates are 20260907. |
| 78 | PASS | Dataset 09 archive date is 20260907. |
| 79 | PASS | No planning regression attributable to Stage 8.2 fixes is present. No newly introduced regression; a pre-existing F8-03 planning defect remains and is explicitly reported. |
| 80 | PASS | AltAz behaviour remains intact. |
| 81 | PASS | EQ behaviour remains intact. |
| 82 | PASS | Firmware 7.75 compatibility remains intact. |
| 83 | PASS | Firmware 8.46 compatibility remains intact. |
| 84 | PASS | Firmware 9.31 compatibility remains intact. |
| 85 | PASS | RGB stacked FITS with `BAYERPAT=GRBG` remain correctly classified. |
| 86 | PASS | Equal-time light/stack behaviour remains intact. |
| 87 | PASS | Explicit mosaic filesystem naming remains supported. |
| 88 | PASS | Retained-light-count differing from STACKCNT remains supported. |
| 89 | PASS | DF8-01 typed mosaic evidence remains deferred. |
| 90 | PASS | DF8-02 target correction/override remains deferred. |
| 91 | PASS | Archive hierarchy remains unchanged. |
| 92 | PASS | Observation numbering remains unchanged. |
| 93 | PASS | +12-hour archive-date policy remains unchanged. |
| 94 | PASS | Cadence/grouping thresholds remain unchanged. |
| 95 | PASS | No complete external dataset is copied into the repository. |
| 96 | PASS | No archive COPY operation is executed. External qualification used planning only; repository tests use temporary execution fixtures. |
| 97 | PASS | No archive MOVE operation is executed. External qualification used planning only; repository tests use temporary execution fixtures. |
| 98 | PASS | All nine datasets remain unchanged after qualification. Before/after state and content manifests are identical. |
| 99 | PASS | Every changed file is identified. |
| 100 | PASS | No unrelated refactor or cleanup is included. |
| 101 | PASS | No Stage 8.3 or later-stage implementation is started. |
| 102 | PASS | Completion report distinguishes confirmed remediations from deferred features. |
| 103 | PASS | Any unexpected diagnostic or discrepancy is explicitly classified rather than silently ignored. Four false planning diagnostics, nine .DS_Store exclusions and broad formatting debt are classified above. |
| 104 | PASS | Evidence is sufficient to determine whether Stage 8.2 remediation can be formally closed. Evidence supports a definite decision: do not close yet. |
| 105 | FAIL | Evidence is sufficient to proceed to Stage 8 closure validation without reopening F8-01 through F8-04 design. Closure validation is blocked by the remaining F8-03 planning path; existing design need not change. |
