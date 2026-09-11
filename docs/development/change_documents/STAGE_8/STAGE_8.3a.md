# Stage 8.3a — Validate and Close Stage 8

## Status

PASS — Stage 8 formally closed by the 2026-09-08 audit; documentation uncommitted.

## Purpose

Perform the formal closure audit for Stage 8 — Testing with Real Seestar Datasets.

This stage must determine whether Stage 8, as a whole, has achieved its objective and can be formally closed.

Stage 8.3a is an audit/validation/documentation stage. It is not a new implementation or remediation stage.

The audit must consider the complete Stage 8 evidence chain:

- frozen real-data corpus and ground truth;
- Stage 8.1 qualification;
- discrepancy classification;
- Stage 8.2 remediation;
- failed Stage 8.2e regression and the additional defect it exposed;
- Stage 8.2f remediation;
- successful Stage 8.2g replacement regression;
- automated test status;
- dataset preservation;
- deferred features;
- repository/documentation readiness.

## Starting Commit

Expected starting commit:

`a329bd9` — Stage 8.2g: validate full real-data remediation

Record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.2g entry is permitted.

This new `docs/change_documents/STAGE_8/STAGE_8.3a.md` document is also an expected working-tree change.

Any other pre-existing change must be identified and explained.

## Stage 8 Objective

Stage 8 exists to validate the Seestar Toolkit against representative real Seestar capture datasets, establish reliable real-world ground truth, identify discrepancies between implemented behaviour and real Seestar behaviour, remediate confirmed defects, and demonstrate that the resulting discovery/reconstruction/archive-planning pipeline behaves correctly across the frozen qualification corpus.

The closure audit must decide whether that objective has been met.

## Frozen Corpus

Authoritative corpus:

`<private-test-data>/`

Nine datasets:

1. `dataset_01_fw846_altaz_c27_single`
2. `dataset_02_fw846_altaz_unknown_mosaic_single`
3. `dataset_03_fw846_altaz_ngc6888_single`
4. `dataset_04_fw931_altaz_m27_single`
5. `dataset_05_fw931_altaz_ngc6888_mosaic_single`
6. `dataset_06_fw775_eq_ic1318_single`
7. `dataset_07_fw775_eq_ic5070_mosaic_single`
8. `dataset_08_fw931_eq_m57_three_sessions`
9. `dataset_09_fw931_eq_ngc281w_mosaic_single`

Do not repeat ground-truth gathering.

## Frozen Truth

Exactly 11 real observations:

- D01 — 1 COMPLETE / 18 lights
- D02 — 1 COMPLETE / 13 lights
- D03 — 1 COMPLETE / 18 lights
- D04 — 1 COMPLETE / 12 lights
- D05 — 1 COMPLETE / 12 lights
- D06 — 1 COMPLETE / 16 lights
- D07 — 1 COMPLETE / 77 lights
- D08 — 3 COMPLETE / 12, 1, 135 lights
- D09 — 1 COMPLETE / 12 lights

Exactly 11 archive plans:

- one each for D01–D07 and D09;
- three for D08.

Frozen archive dates:

- D01 — 20260907
- D02 — 20260907
- D03 — 20260907
- D04 — 20260907
- D05 — 20260907
- D06 — 20260906
- D07 — 20260906
- D08 — 20260907 for all three
- D09 — 20260907

## Stage 8 Evidence Chain

### Stage 8.1

Audit that Stage 8.1 established and preserved the frozen real-data evidence rather than changing production behaviour prematurely.

Confirm:

- D01 baseline qualification;
- D02–D04 qualification;
- D05–D07/D09 qualification;
- D08 multi-session qualification;
- Stage 8.1e discrepancy consolidation.

### Confirmed Findings

The audit must confirm the final disposition of:

- F8-01 — equal-time reconstruction ordering;
- F8-02 — filename/FITS timestamp diagnostic semantics;
- F8-03 — discovery structural mosaic target comparison;
- F8-03A — archive-planning structural mosaic target comparison;
- F8-04 — stack-count diagnostic semantics.

All must be resolved and protected by regression evidence.

### Failed Stage 8.2e

The audit must explicitly retain Stage 8.2e as valid historical evidence.

Stage 8.2e failed because the first full remediation regression exposed F8-03A in archive planning.

That failure must not be rewritten as a pass or omitted.

Stage 8.2f corrected F8-03A.

Stage 8.2g then provided the successful full replacement regression.

### Deferred Features

Confirm these remain deliberately deferred and are not Stage 8 blockers:

- DF8-01 — typed mosaic evidence;
- DF8-02 — target correction/override.

Do not implement them in Stage 8.3a.

## Required Closure Audit

### Repository Validation

Run:

`python -m pytest`

`ruff check .`

`git diff --check`

Run applicable formatting validation.

No production/test change is expected.

### Stage Documentation Audit

Inspect the Stage 8 authoritative change documents and confirm the development history is internally consistent.

At minimum review:

- Stage 8.1a through Stage 8.1e;
- Stage 8.2a through Stage 8.2g;
- this Stage 8.3a document.

Confirm:

- failed Stage 8.2e is clearly represented as failed;
- Stage 8.2f records the discovered F8-03A remediation;
- Stage 8.2g records the successful replacement regression;
- no finding is left accidentally unclassified;
- deferred features remain clearly deferred.

### Project Documentation

Review the current project documentation that records roadmap/status/architecture/history.

Update documentation only where necessary to accurately record Stage 8 completion.

Expected likely documentation targets include:

- `docs/PROJECT_Notes.md`;
- `docs/ARCHITECTURE.md` only if Stage 8 established architecture facts not already represented;
- `docs/CHANGELOG.md` as required by the established commit workflow.

Do not make speculative architecture changes.

Do not rewrite unrelated historical material.

### Real-Data Closure Evidence

Stage 8.2g already performed the authoritative full nine-dataset regression.

Do not unnecessarily repeat expensive ground-truth analysis.

The closure audit may run a concise/read-only qualification check if useful, but must primarily audit the existing Stage 8.2g evidence.

If real-data qualification is rerun, it must remain read-only and preserve all datasets.

### Dataset Preservation

Confirm Stage 8 evidence records preservation of all 1,020 files in the frozen corpus.

No Stage 8 closure operation may modify/copy/move/delete the external corpus.

### Behavioural Coverage

Confirm Stage 8 validated:

- firmware 7.75;
- firmware 8.46;
- firmware 9.31;
- AltAz;
- EQ;
- single observations;
- multiple same-target observations;
- cross-midnight behaviour;
- large retained-light gaps;
- equal-time light/stack timestamps;
- structural mosaic naming;
- legitimate target `Unknown`;
- RGB stacked FITS containing BAYERPAT;
- retained source-light count differing from STACKCNT.

### Final Stage 8 State

At closure, the audit must be able to state:

- nine real datasets qualified;
- 11 observations qualified;
- 11 archive plans qualified;
- all confirmed Stage 8 findings resolved;
- successful full post-remediation regression exists;
- 314+ automated tests pass;
- frozen external corpus remained unchanged;
- no archive COPY/MOVE was required for qualification;
- deferred features are explicitly recorded;
- repository/project documentation accurately marks Stage 8 complete;
- no known Stage 8 defect remains open.

## Scope

Stage 8.3a includes:

1. audit Stage 8 evidence and history;
2. verify starting repository state;
3. run final automated repository validation;
4. audit Stage 8 change documents;
5. audit confirmed finding disposition;
6. audit deferred feature disposition;
7. verify Stage 8.2g provides successful full real-data closure evidence;
8. verify dataset preservation evidence;
9. update project documentation necessary to mark Stage 8 complete;
10. produce a formal Stage 8 closure recommendation.

## Exclusions

Do not:

- introduce new production functionality;
- introduce new reconstruction heuristics;
- change discovery semantics;
- change archive-planning semantics;
- alter cadence/grouping;
- alter timestamp precedence;
- alter STACKCNT semantics;
- implement typed mosaic evidence;
- implement target correction/override;
- change archive hierarchy;
- execute archive COPY/MOVE;
- copy the full corpus into the repository;
- begin the next development stage;
- perform unrelated cleanup/refactoring;
- commit changes.

If a genuine Stage 8 defect is discovered, STOP closure and report it rather than opportunistically fixing it.

## Completion Report

Return:

- final result: PASS / FAIL;
- starting HEAD and repository state;
- files reviewed;
- files changed;
- automated validation results;
- Stage 8 evidence-chain audit;
- confirmed finding disposition;
- deferred feature disposition;
- real-data qualification summary;
- dataset-preservation summary;
- documentation updates;
- final Stage 8 closure recommendation;
- all closure criteria below individually.

## Closure Criteria

1. Actual starting HEAD is recorded and matches `a329bd9` or difference is explained.
2. Pending Stage 8.2g CHANGELOG entry is recognized as intentional.
3. No unexpected pre-existing working-tree change is ignored.
4. Stage 8.1a evidence is present and consistent.
5. Stage 8.1b evidence is present and consistent.
6. Stage 8.1c evidence is present and consistent.
7. Stage 8.1d evidence is present and consistent.
8. Stage 8.1e evidence is present and consistent.
9. Stage 8.2a evidence is present and consistent.
10. Stage 8.2b evidence is present and consistent.
11. Stage 8.2c evidence is present and consistent.
12. Stage 8.2d evidence is present and consistent.
13. Failed Stage 8.2e evidence is present.
14. Stage 8.2e remains explicitly recorded as FAIL.
15. Stage 8.2f evidence is present and consistent.
16. Stage 8.2f records F8-03A remediation.
17. Stage 8.2g evidence is present and consistent.
18. Stage 8.2g records the successful replacement full regression.
19. F8-01 is recorded as resolved.
20. F8-01 regression evidence exists.
21. F8-02 is recorded as resolved.
22. F8-02 regression evidence exists.
23. F8-03 is recorded as resolved.
24. F8-03 regression evidence exists.
25. F8-03A is recorded as resolved.
26. F8-03A regression evidence exists.
27. F8-04 is recorded as resolved.
28. F8-04 regression evidence exists.
29. No confirmed Stage 8 finding remains unresolved.
30. DF8-01 remains explicitly deferred.
31. DF8-02 remains explicitly deferred.
32. Deferred features are not incorrectly classified as closure blockers.
33. Frozen corpus contains nine qualification datasets.
34. Frozen truth remains exactly 11 observations.
35. Frozen archive truth remains exactly 11 plans.
36. D01 frozen membership remains 18.
37. D02 frozen membership remains 13.
38. D03 frozen membership remains 18.
39. D04 frozen membership remains 12.
40. D05 frozen membership remains 12.
41. D06 frozen membership remains 16.
42. D07 frozen membership remains 77.
43. D08 frozen memberships remain 12 / 1 / 135.
44. D09 frozen membership remains 12.
45. D01 archive date remains 20260907.
46. D02 archive date remains 20260907.
47. D03 archive date remains 20260907.
48. D04 archive date remains 20260907.
49. D05 archive date remains 20260907.
50. D06 archive date remains 20260906.
51. D07 archive date remains 20260906.
52. All three D08 archive dates remain 20260907.
53. D09 archive date remains 20260907.
54. Stage 8.2g reports zero diagnostics attributable to F8-01.
55. Stage 8.2g reports zero diagnostics attributable to F8-02.
56. Stage 8.2g reports zero diagnostics attributable to F8-03.
57. Stage 8.2g reports zero diagnostics attributable to F8-03A.
58. Stage 8.2g reports zero diagnostics attributable to F8-04.
59. Firmware 7.75 real-data coverage is confirmed.
60. Firmware 8.46 real-data coverage is confirmed.
61. Firmware 9.31 real-data coverage is confirmed.
62. AltAz coverage is confirmed.
63. EQ coverage is confirmed.
64. Single-observation coverage is confirmed.
65. Multi-observation same-target coverage is confirmed.
66. Cross-midnight coverage is confirmed.
67. Large retained-light-gap coverage is confirmed.
68. Equal-time light/stack coverage is confirmed.
69. Structural mosaic naming coverage is confirmed.
70. Legitimate `Unknown` target coverage is confirmed.
71. RGB stacked FITS containing BAYERPAT coverage is confirmed.
72. Retained-light-count versus STACKCNT divergence coverage is confirmed.
73. Full repository pytest passes.
74. Full test count is at least the 314-test Stage 8.2g baseline.
75. Ruff passes.
76. `git diff --check` passes.
77. Applicable formatting validation passes.
78. No production-code change is required for Stage 8 closure.
79. No test-code change is required for Stage 8 closure.
80. Stage 8 evidence confirms all 1,020 frozen dataset files remained unchanged.
81. No archive COPY operation was required during Stage 8 qualification.
82. No archive MOVE operation was required during Stage 8 qualification.
83. No complete frozen dataset is added to the repository.
84. Project roadmap/status documentation is reviewed for Stage 8 completion.
85. `docs/PROJECT_Notes.md` accurately records Stage 8 completion after any required update.
86. `docs/ARCHITECTURE.md` is reviewed for Stage 8-derived architecture facts.
87. ARCHITECTURE is changed only if necessary.
88. `docs/CHANGELOG.md` preserves established pending-entry workflow.
89. Failed Stage 8.2e history is not erased or rewritten.
90. Stage 8.2f and Stage 8.2g history clearly explains recovery from 8.2e failure.
91. Stage 8 ground truth is not regenerated or silently changed.
92. No new real-data heuristic is introduced during closure.
93. No deferred feature is implemented during closure.
94. No unrelated cleanup/refactor is included.
95. No next-stage implementation is started.
96. Every file changed during Stage 8.3a is identified.
97. Every documentation change is justified by Stage 8 closure.
98. Repository remains in a state suitable for a closure commit.
99. No known Stage 8 defect remains open.
100. Stage 8 objective is demonstrably satisfied.
101. Evidence supports formal closure of Stage 8.
102. Completion report explicitly states whether Stage 8 can close.
103. Completion report lists any remaining deferred/non-blocking work.
104. Completion report identifies the next project stage only as future work and does not begin it.
105. No commit is created by Codex.

## Expected Next Step

If all closure criteria pass:

1. formally close Stage 8;
2. approve the Stage 8.3a closure commit;
3. update `docs/CHANGELOG.md` with the Stage 8.3a commit ID and leave it pending;
4. begin the next project stage only in a new, separately defined Stage chat/workflow.

## Stage 8.3a Formal Closure Report — 2026-09-08

**Final result: PASS. Stage 8 can formally close and is marked complete in the project roadmap. All 105 closure criteria pass.** No known Stage 8 defect remains open. This is an evidence audit, final repository validation and documentation update; no production or test behavior changed.

### Starting state and environment

- Starting and ending HEAD: `a329bd9e325dafd96fc2befdbdb62986ba4291cd` — Stage 8.2g: validate full real-data remediation.
- Initial Git status: modified `docs/CHANGELOG.md` (intentional two-line pending Stage 8.2g entry) and untracked `docs/change_documents/STAGE_8/STAGE_8.3a.md`. No other pre-existing changes.
- Python executable `<development-environment>/bin/python`, version 3.13.15; pytest 9.1.1; Ruff 0.16.0.
- Imported package `<repository-root>/src/seestar_toolkit/__init__.py`.

### Files and history reviewed

Reviewed the authoritative Stage 8.3a specification in full; Stage 8.1a–8.1e and Stage 8.2a–8.2g change documents for frozen evidence, requirements, finding disposition and outcomes; the Stage 8.0 context/status; `docs/PROJECT_Notes.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, repository `AGENTS.md`, project tooling configuration, commit history and changed-file history. The existing archive reconstruction, discovery, planning and shared target-comparison implementation and regression coverage corroborate the established semantics.

The primary final real-data source is the committed [Stage 8.2g report](STAGE_8.2g.md), not a newly gathered corpus. No external dataset was read, rescanned, copied or otherwise operated on during this closure audit.

### Stage 8 evidence chain

| Stage / committed evidence | Audit result |
|---|---|
| 8.1a — `5800b47` | D01 baseline protocol and frozen single observation established; subsequent evidence carries forward the 18-light baseline |
| 8.1b — `330d69a` | D02–D04 qualified; D02 equal-time split and recurring timestamp/mosaic diagnostics carried into 8.1c |
| 8.1c — `d5e7f92` | D05–D07/D09 qualified; D05/D09 share D02 ordering defect, while D06/D07 protect older firmware/EQ behavior |
| 8.1d — `d845067` | D08 three-observation evidence: 12/1/135 lights, intermediate-stack boundaries, cross-midnight evidence, large gap, count divergence |
| 8.1e — `e1a00f2` | Consolidates 8 correctly reconstructed and 3 incorrectly reconstructed frozen observations; separates four root findings and deferred features |
| 8.2a — `65872ec` | F8-01 semantic equal-time ordering correction with regression protection |
| 8.2b — `a5fda62` | F8-02 invalid filename/FITS conflict comparison removed while authority/fallback remain intact |
| 8.2c — `25587ef` | F8-03 discovery comparison-only structural suffix correction |
| 8.2d — `02d92ce` | F8-04 retained-count warning corrected; source membership unchanged |
| 8.2e — historical FAIL, report included in `491ce26` | First combined regression retained 11 correct observations/plans but exposed four false mosaic planning diagnostics; failure remains explicit |
| 8.2f — `491ce26` | F8-03A corrected through one shared comparison rule; focused tests demonstrate failure before and success after correction |
| 8.2g — `a329bd9` | Successful replacement full regression: 117/117 criteria, 100 focused tests and 314 full tests pass; all nine datasets and preservation evidence match |

Git confirms that Stage 8.1 made no production or test changes (`git diff db4db43 e1a00f2 -- src tests` is empty). The remediation commits then change the expected narrow code/test paths. Stage 8.2g changes only validation documentation and the pending CHANGELOG entry. There is no invented successful Stage 8.2e remediation commit.

**Historical-document classification:** 8.1a–8.2d retain original `START` headings and instruction-style content rather than appended completion reports. Their completion/progression is corroborated by the commit chain, successor documents carrying forward observed evidence, remediation diffs/tests, and the final 8.2g report. They are not treated as standalone completed-result reports. Likewise, the word “uncommitted” in the 8.2f/8.2g report status describes report-authoring time; Git now records those reports at the commits above. These are non-blocking archival status conventions, explicitly distinguished from current state. No historical document was rewritten to manufacture an outcome.

### Final finding disposition

| Finding | Final disposition | Regression evidence |
|---|---|---|
| F8-01 | RESOLVED by 8.2a | Equal-time compatible/incompatible, later-light rejection and deterministic stack-order tests; 8.2g D02/D05/D09 retain 13/12/12 |
| F8-02 | RESOLVED by 8.2b | FITS-authority and filename-fallback unit/integration tests; 8.2g false timestamp diagnostics zero across all nine |
| F8-03 | RESOLVED by 8.2c | Structural suffix, preserved evidence, ordinary mosaic text and genuine mismatch discovery tests; D02/D05/D07/D09 zero false discovery conflicts |
| F8-03A | RESOLVED by 8.2f | Generated-FITS discovery/planning consistency, genuine mismatch and fallback-preservation tests; same four datasets zero false planning conflicts in 8.2g |
| F8-04 | RESOLVED by 8.2d | Greater/less/missing reported count and contradictory stack metadata tests; D08 Session 03 retains 135 with 106/3180/30 and no false diagnostic |

The current full pytest run includes all of these regressions. Stage 8.2g explicitly reports zero diagnostics attributable to each finding and no cross-remediation regression. No design is reopened.

### Deferred and non-blocking work

- **DF8-01 — typed mosaic evidence:** deliberately deferred; comparison-only suffix handling is sufficient for the qualified archive behavior. No typed state or dimension/WCS inference was added.
- **DF8-02 — target correction/override:** deliberately deferred; legitimate `Unknown` and existing target precedence are supported without an override.
- Nine recorded `.DS_Store` discovery exclusions (one at each dataset root) are expected informational metadata exclusions, not open defects; they do not create observations or plans.
- Broader pre-existing formatting debt recorded by 8.2e remains outside applicable changed-file formatting checks. No unrelated formatting cleanup was performed.

Neither deferred feature blocks Stage 8. Earlier-stage deferred work remains outside this audit. Stage 9 — Packaging and release is future work only, to be separately defined; it has not begun.

### Frozen real-data closure evidence

The following is audited from Stage 8.2g. No ground truth was regenerated or silently changed.

| Dataset | COMPLETE observations | Retained lights | Plans | Archive date(s) |
|---|---|---|---|---|
| D01 | 1 | 18 | 1 | 20260907 |
| D02 | 1 | 13 | 1 | 20260907 |
| D03 | 1 | 18 | 1 | 20260907 |
| D04 | 1 | 12 | 1 | 20260907 |
| D05 | 1 | 12 | 1 | 20260907 |
| D06 | 1 | 16 | 1 | 20260906 |
| D07 | 1 | 77 | 1 | 20260906 |
| D08 | 3 | 12 / 1 / 135 | 3 | 20260907 / 20260907 / 20260907 |
| D09 | 1 | 12 | 1 | 20260907 |

**Totals: 9 datasets, 11 COMPLETE observations, 326 retained lights, 11 correctly assigned stacks, 11 archive plans.** Stage 8.2g records exact once-only membership, no unexpected LIGHTS_ONLY/STACK_ONLY/AMBIGUOUS/UNRESOLVED observations, frozen stack assignments, expected dates and zero observation/planning diagnostics.

D08 Session 03 remains 135 retained lights with `STACKCNT=106`, `TOTALEXP=3180`, `EXPTIME=30`. Its metadata relationship is `3180/30=106`; the source-light count is intentionally independent.

### Behavioural coverage audit

| Behaviour | Authoritative 8.2g evidence |
|---|---|
| Firmware 7.75 | D06/D07 |
| Firmware 8.46 | D01–D03 |
| Firmware 9.31 | D04/D05/D08/D09 |
| AltAz / EQ | D01–D05 EQMODE=0; D06–D09 EQMODE=1 |
| Single observations | D01–D07 and D09 |
| Multiple same-target observations | D08 three M 57 observations with separate intermediate stacks |
| Cross-midnight | D08 frozen filename/session evidence crosses midnight; FITS times remain authoritative, no timezone inferred |
| Large retained-light gap | D08 Session 03 maximum gap 221.936137 seconds remains stack-backed |
| Equal-time light/stack | D02/D05/D09 final light equals stack time and remains attached |
| Structural mosaic naming | D02/D05/D07/D09, discovery and planning agree |
| Legitimate Unknown | D02 retains Unknown |
| RGB stack with BAYERPAT | All 11 stacks remain RGB_IMAGE with GRBG evidence |
| Retained-light/count divergence | D08 Session 03 retains 135 versus STACKCNT 106 |

### Dataset-preservation audit

Stage 8.2g records before/after relative-path, mode/type, size, mtime_ns, ctime_ns and full-content SHA-256 manifests with exact equality. Access times are excluded because reads can affect them. The table below reproduces the authoritative recorded preservation evidence, not a new filesystem measurement.

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

No Stage 8.3a operation touched the external corpus. Qualification needed no external archive COPY/MOVE; repository execution tests use their own temporary fixtures, which is distinct from executing a corpus archive operation. No complete frozen dataset was added to the repository.

### Final repository validation

| Check | Result |
|---|---|
| `python -m pytest` | **314 passed in 11.52s**; equals the 314-test Stage 8.2g baseline |
| `ruff check .` | PASS |
| Archive source/unit/integration formatting | PASS: 26 files already formatted |
| Formatting of changed closure documentation | PASS |
| `git diff --check` | PASS |

No production or test-code change was required. Applicable formatting covers the archive package, archive unit tests, discovery/reconstruction/planning integration tests, and edited closure documents. It does not assert that unrelated historical repository formatting debt has been removed.

### Documentation updates and final file list

| File | Change and justification |
|---|---|
| `docs/PROJECT_Notes.md` | Mark Stage 8 complete; add closure/evidence summary, failure/recovery history, resolved findings, deferred non-blockers and future-only Stage 9 |
| `docs/ARCHITECTURE.md` | Correct stale pre-Stage-8 timestamp conflict and equal-time descriptions; record shared comparison-only mosaic semantics and retained-count independence already implemented and qualified |
| `docs/change_documents/STAGE_8/STAGE_8.3a.md` | Preserve authoritative specification; update status and append this complete 105-criterion closure report |
| `docs/CHANGELOG.md` | Pre-existing intentional pending 8.2g entry, preserved byte-for-byte; no new entry or fabricated closure commit ID |

The architecture edit is necessary because the old text still promised a two-second filename/FITS conflict warning and path-only equal-time ordering, and did not represent shared structural comparison. It documents existing code, not new architecture or behavior. Historical Stage 7 progress sections in project notes remain historical; the new Stage 8 section makes the superseding behavior explicit.

Final Git status consists only of the three modified tracked documents (`PROJECT_Notes.md`, `ARCHITECTURE.md`, pending `CHANGELOG.md`) and the untracked Stage 8.3a document. All earlier Stage 8 documents and the pending CHANGELOG are hash-checked unchanged. No other file changed. Temporary audit artifacts outside the repository: `/tmp/stage83a_preserved_docs.json` and `/tmp/stage83a_report.py`; neither contains external datasets.

### Formal closure decision

**Stage 8 can formally close. Stage 8 is complete.** Its objective is satisfied: representative frozen real-data evidence was established, discrepancies were classified, all confirmed defects were remediated, the failed regression exposed and preserved an additional defect, and the successful replacement regression plus current repository validation establish the final result. No known Stage 8 defect remains open.

The repository is suitable for review and a closure documentation commit. No commit was created, no files were staged, no branch was changed, and no next-stage implementation was started. After the user’s closure commit, the established workflow is to record its real ID in CHANGELOG and leave that entry pending. DF8-01/DF8-02 remain future non-blocking work; Stage 9 requires a separate workflow.

### Individual closure criteria

**105 / 105 PASS.**

| # | Result | Criterion and supporting evidence |
|---|---|---|
| 1 | PASS | Actual starting HEAD is recorded and matches `a329bd9` or difference is explained. Starting HEAD and two intentional initial changes verified. |
| 2 | PASS | Pending Stage 8.2g CHANGELOG entry is recognized as intentional. Starting HEAD and two intentional initial changes verified. |
| 3 | PASS | No unexpected pre-existing working-tree change is ignored. Starting HEAD and two intentional initial changes verified. |
| 4 | PASS | Stage 8.1a evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 5 | PASS | Stage 8.1b evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 6 | PASS | Stage 8.1c evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 7 | PASS | Stage 8.1d evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 8 | PASS | Stage 8.1e evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 9 | PASS | Stage 8.2a evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 10 | PASS | Stage 8.2b evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 11 | PASS | Stage 8.2c evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 12 | PASS | Stage 8.2d evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 13 | PASS | Failed Stage 8.2e evidence is present. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 14 | PASS | Stage 8.2e remains explicitly recorded as FAIL. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 15 | PASS | Stage 8.2f evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 16 | PASS | Stage 8.2f records F8-03A remediation. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 17 | PASS | Stage 8.2g evidence is present and consistent. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 18 | PASS | Stage 8.2g records the successful replacement full regression. See stage-by-stage evidence/commit table and explicit historical-status classification. |
| 19 | PASS | F8-01 is recorded as resolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 20 | PASS | F8-01 regression evidence exists. See resolved-finding table, existing regression coverage and current passing suite. |
| 21 | PASS | F8-02 is recorded as resolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 22 | PASS | F8-02 regression evidence exists. See resolved-finding table, existing regression coverage and current passing suite. |
| 23 | PASS | F8-03 is recorded as resolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 24 | PASS | F8-03 regression evidence exists. See resolved-finding table, existing regression coverage and current passing suite. |
| 25 | PASS | F8-03A is recorded as resolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 26 | PASS | F8-03A regression evidence exists. See resolved-finding table, existing regression coverage and current passing suite. |
| 27 | PASS | F8-04 is recorded as resolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 28 | PASS | F8-04 regression evidence exists. See resolved-finding table, existing regression coverage and current passing suite. |
| 29 | PASS | No confirmed Stage 8 finding remains unresolved. See resolved-finding table, existing regression coverage and current passing suite. |
| 30 | PASS | DF8-01 remains explicitly deferred. DF8-01/DF8-02 are explicitly deferred and non-blocking. |
| 31 | PASS | DF8-02 remains explicitly deferred. DF8-01/DF8-02 are explicitly deferred and non-blocking. |
| 32 | PASS | Deferred features are not incorrectly classified as closure blockers. DF8-01/DF8-02 are explicitly deferred and non-blocking. |
| 33 | PASS | Frozen corpus contains nine qualification datasets. See frozen-truth table audited from committed Stage 8.2g. |
| 34 | PASS | Frozen truth remains exactly 11 observations. See frozen-truth table audited from committed Stage 8.2g. |
| 35 | PASS | Frozen archive truth remains exactly 11 plans. See frozen-truth table audited from committed Stage 8.2g. |
| 36 | PASS | D01 frozen membership remains 18. See frozen-truth table audited from committed Stage 8.2g. |
| 37 | PASS | D02 frozen membership remains 13. See frozen-truth table audited from committed Stage 8.2g. |
| 38 | PASS | D03 frozen membership remains 18. See frozen-truth table audited from committed Stage 8.2g. |
| 39 | PASS | D04 frozen membership remains 12. See frozen-truth table audited from committed Stage 8.2g. |
| 40 | PASS | D05 frozen membership remains 12. See frozen-truth table audited from committed Stage 8.2g. |
| 41 | PASS | D06 frozen membership remains 16. See frozen-truth table audited from committed Stage 8.2g. |
| 42 | PASS | D07 frozen membership remains 77. See frozen-truth table audited from committed Stage 8.2g. |
| 43 | PASS | D08 frozen memberships remain 12 / 1 / 135. See frozen-truth table audited from committed Stage 8.2g. |
| 44 | PASS | D09 frozen membership remains 12. See frozen-truth table audited from committed Stage 8.2g. |
| 45 | PASS | D01 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 46 | PASS | D02 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 47 | PASS | D03 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 48 | PASS | D04 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 49 | PASS | D05 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 50 | PASS | D06 archive date remains 20260906. See frozen-truth table audited from committed Stage 8.2g. |
| 51 | PASS | D07 archive date remains 20260906. See frozen-truth table audited from committed Stage 8.2g. |
| 52 | PASS | All three D08 archive dates remain 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 53 | PASS | D09 archive date remains 20260907. See frozen-truth table audited from committed Stage 8.2g. |
| 54 | PASS | Stage 8.2g reports zero diagnostics attributable to F8-01. Stage 8.2g explicitly records zero diagnostics for this finding. |
| 55 | PASS | Stage 8.2g reports zero diagnostics attributable to F8-02. Stage 8.2g explicitly records zero diagnostics for this finding. |
| 56 | PASS | Stage 8.2g reports zero diagnostics attributable to F8-03. Stage 8.2g explicitly records zero diagnostics for this finding. |
| 57 | PASS | Stage 8.2g reports zero diagnostics attributable to F8-03A. Stage 8.2g explicitly records zero diagnostics for this finding. |
| 58 | PASS | Stage 8.2g reports zero diagnostics attributable to F8-04. Stage 8.2g explicitly records zero diagnostics for this finding. |
| 59 | PASS | Firmware 7.75 real-data coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 60 | PASS | Firmware 8.46 real-data coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 61 | PASS | Firmware 9.31 real-data coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 62 | PASS | AltAz coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 63 | PASS | EQ coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 64 | PASS | Single-observation coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 65 | PASS | Multi-observation same-target coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 66 | PASS | Cross-midnight coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 67 | PASS | Large retained-light-gap coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 68 | PASS | Equal-time light/stack coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 69 | PASS | Structural mosaic naming coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 70 | PASS | Legitimate `Unknown` target coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 71 | PASS | RGB stacked FITS containing BAYERPAT coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 72 | PASS | Retained-light-count versus STACKCNT divergence coverage is confirmed. See behavioural coverage matrix audited from Stage 8.2g. |
| 73 | PASS | Full repository pytest passes. 314 tests passed in the final run. |
| 74 | PASS | Full test count is at least the 314-test Stage 8.2g baseline. 314 tests passed in the final run. |
| 75 | PASS | Ruff passes. ruff check . passed. |
| 76 | PASS | `git diff --check` passes. git diff --check passed. |
| 77 | PASS | Applicable formatting validation passes. Archive scope and edited documentation pass formatting. |
| 78 | PASS | No production-code change is required for Stage 8 closure. No source or test changes. |
| 79 | PASS | No test-code change is required for Stage 8 closure. No source or test changes. |
| 80 | PASS | Stage 8 evidence confirms all 1,020 frozen dataset files remained unchanged. Audited 8.2g manifests and read-only qualification record; no external corpus operation in closure. |
| 81 | PASS | No archive COPY operation was required during Stage 8 qualification. Audited 8.2g manifests and read-only qualification record; no external corpus operation in closure. |
| 82 | PASS | No archive MOVE operation was required during Stage 8 qualification. Audited 8.2g manifests and read-only qualification record; no external corpus operation in closure. |
| 83 | PASS | No complete frozen dataset is added to the repository. Audited 8.2g manifests and read-only qualification record; no external corpus operation in closure. |
| 84 | PASS | Project roadmap/status documentation is reviewed for Stage 8 completion. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 85 | PASS | `docs/PROJECT_Notes.md` accurately records Stage 8 completion after any required update. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 86 | PASS | `docs/ARCHITECTURE.md` is reviewed for Stage 8-derived architecture facts. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 87 | PASS | ARCHITECTURE is changed only if necessary. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 88 | PASS | `docs/CHANGELOG.md` preserves established pending-entry workflow. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 89 | PASS | Failed Stage 8.2e history is not erased or rewritten. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 90 | PASS | Stage 8.2f and Stage 8.2g history clearly explains recovery from 8.2e failure. See justified documentation updates, preserved history and unchanged pending CHANGELOG. |
| 91 | PASS | Stage 8 ground truth is not regenerated or silently changed. Documentation-only scope; complete final file list and exclusions checked. |
| 92 | PASS | No new real-data heuristic is introduced during closure. Documentation-only scope; complete final file list and exclusions checked. |
| 93 | PASS | No deferred feature is implemented during closure. Documentation-only scope; complete final file list and exclusions checked. |
| 94 | PASS | No unrelated cleanup/refactor is included. Documentation-only scope; complete final file list and exclusions checked. |
| 95 | PASS | No next-stage implementation is started. Documentation-only scope; complete final file list and exclusions checked. |
| 96 | PASS | Every file changed during Stage 8.3a is identified. Documentation-only scope; complete final file list and exclusions checked. |
| 97 | PASS | Every documentation change is justified by Stage 8 closure. Documentation-only scope; complete final file list and exclusions checked. |
| 98 | PASS | Repository remains in a state suitable for a closure commit. All validation passes; only reviewable closure documentation and the permitted pending entry differ. |
| 99 | PASS | No known Stage 8 defect remains open. All findings resolved; final evidence establishes Stage 8 completion. |
| 100 | PASS | Stage 8 objective is demonstrably satisfied. All findings resolved; final evidence establishes Stage 8 completion. |
| 101 | PASS | Evidence supports formal closure of Stage 8. All findings resolved; final evidence establishes Stage 8 completion. |
| 102 | PASS | Completion report explicitly states whether Stage 8 can close. All findings resolved; final evidence establishes Stage 8 completion. |
| 103 | PASS | Completion report lists any remaining deferred/non-blocking work. Deferred features and future-only Stage 9 are explicitly listed. |
| 104 | PASS | Completion report identifies the next project stage only as future work and does not begin it. Deferred features and future-only Stage 9 are explicitly listed. |
| 105 | PASS | No commit is created by Codex. HEAD unchanged; no commit or staging operation performed. |
