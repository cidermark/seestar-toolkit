# Stage 8.1e — Consolidate and Classify Stage 8.1 Discrepancies

## Status

START

## Purpose

Close the Stage 8.1 real-data validation phase by consolidating all evidence gathered from the nine external real-world Seestar datasets and 11 frozen observations.

Stage 8.1e is an analysis and planning sub-stage.

It must:

- identify distinct root causes;
- distinguish root causes from downstream consequences;
- consolidate repeated findings;
- classify severity and scope;
- define remediation priorities;
- determine appropriate regression-fixture needs;
- define the Stage 8.2x remediation sequence;
- preserve deferred features separately from defects.

Stage 8.1e must not modify production code, tests, reconstruction rules, diagnostics, archive behaviour or data models.

No remediation implementation is permitted.

## Starting Commit

Expected starting commit:

`d845067` — Stage 8.1d: validate Dataset 08 multi-session behavior

Before analysis begins, record the actual Git `HEAD`.

The normal intentionally pending `docs/CHANGELOG.md` Stage 8.1d entry is permitted and must not automatically be treated as unexpected working-tree dirtiness.

The new `STAGE_8.1e.md` document may also be present as an intentional uncommitted documentation change.

## Evidence Base

Use only the completed Stage 8.1 evidence from:

- Dataset 01 — fw846 AltAz C27 single
- Dataset 02 — fw846 AltAz Unknown mosaic single
- Dataset 03 — fw846 AltAz NGC 6888 single
- Dataset 04 — fw931 AltAz M27 single
- Dataset 05 — fw931 AltAz NGC 6888 mosaic single
- Dataset 06 — fw775 EQ IC 1318 single
- Dataset 07 — fw775 EQ IC 5070 mosaic single
- Dataset 08 — fw931 EQ M57 three sessions
- Dataset 09 — fw931 EQ NGC 281W mosaic single

Frozen total:

- nine datasets;
- 11 real observations.

Do not re-run broad exploratory ground-truth characterisation.

Re-running narrowly targeted read-only inspection is permitted only where necessary to resolve an ambiguity in the recorded evidence.

Do not modify external datasets.

## Frozen Stage 8.1 Outcome

Across 11 frozen observations:

- 8 reconstructed correctly;
- 3 reconstructed incorrectly;
- the incorrect observations are in Datasets 02, 05 and 09.

All three incorrect reconstructions share the same observed condition:

- final retained light and stack have exactly equal authoritative FITS timestamps;
- deterministic ordering processes the stack before the equal-timestamp light;
- the stack closes the observation without the final light;
- the final light becomes a separate LIGHTS_ONLY observation;
- archive planning inherits an extra observation.

No non-equal final-light/stack case produced this defect.

Dataset 08 confirms:

- three same-target sessions can remain distinct;
- intermediate stack evidence can provide valid boundaries;
- a local cross-midnight transition does not split an observation;
- a 221.936-second retained-light gap does not split a stack-backed observation;
- 135 retained source lights with `STACKCNT=106` and `TOTALEXP=3180` is valid;
- `STACKCNT == TOTALEXP / EXPTIME` remains internally consistent;
- retained source-light count need not equal `STACKCNT`.

## Known Discrepancy Areas

Stage 8.1e must analyse at least the following.

### A. Equal-Timestamp Reconstruction Defect

Observed in:

- Dataset 02;
- Dataset 05;
- Dataset 09.

Classification:

`RECONSTRUCTION`

Known downstream consequence:

`ARCHIVE`

Questions Stage 8.1e must answer:

- Is this one root defect or multiple defects?
- What exact current ordering assumption is invalid?
- What behaviour should replace it?
- What invariants must remain true?
- What regression fixture(s) are needed?
- What existing tests are likely to require extension?
- What remediation stage should implement it?
- What acceptance criteria should prove the defect fixed without damaging Dataset 08 multi-session behaviour?

Do not implement the fix.

### B. Filename/FITS Timezone Diagnostic

Observed in all nine datasets.

Classification:

`DIAGNOSTIC`

Known evidence:

- filename timestamps represent local time;
- FITS timestamps represent UTC;
- current comparison treats them as naive datetimes;
- approximately one-hour differences therefore trigger conflict diagnostics;
- FITS timestamp precedence remains correct;
- no reconstruction membership failure was caused by these warnings.

Questions Stage 8.1e must answer:

- What is the invalid diagnostic assumption?
- Should the comparison become timezone-aware, timezone-tolerant, or otherwise context-sensitive?
- What real invariant should a conflict diagnostic actually protect?
- What test evidence is required?
- What remediation stage should own this work?

Do not implement the fix.

### C. Mosaic Directory/FITS Target Diagnostic

Observed in all explicitly validated mosaic datasets:

- Dataset 02;
- Dataset 05;
- Dataset 07;
- Dataset 09.

Classification:

`DIAGNOSTIC`

Known evidence:

- filesystem target includes `_mosaic`;
- FITS target does not;
- current discovery emits directory/FITS target disagreement warnings;
- this warning does not independently cause reconstruction failure;
- Dataset 07 proves successful reconstruction despite the warning.

Questions Stage 8.1e must answer:

- Is `_mosaic` a structural filesystem suffix rather than part of logical target identity?
- Where should normalization occur, if at all?
- What diagnostics should remain valid after normalization?
- What tests/fixtures are required?
- Should typed mosaic evidence be part of the defect remediation or remain a separate deferred feature?

Do not implement changes.

### D. STACKCNT Versus Retained-Light Diagnostic Semantics

Established most clearly by Dataset 08 Session 03.

Classification:

`DIAGNOSTIC`

Known frozen evidence:

- EXPTIME = 30;
- STACKCNT = 106;
- TOTALEXP = 3180;
- retained source-light FITS = 135;
- membership is correct;
- current Toolkit emits a mismatch diagnostic;
- `STACKCNT == TOTALEXP / EXPTIME` is internally consistent.

Questions Stage 8.1e must answer:

- What does `STACKCNT` appear to represent?
- Which equality assumptions are invalid?
- Which consistency checks remain useful?
- Should retained-source count ever be compared directly with `STACKCNT`?
- What regression case is needed?
- What remediation stage should own this diagnostic change?

Do not implement changes.

## Deferred Feature Areas

The following must remain explicitly separate from confirmed defects unless Stage 8.1 evidence demonstrates otherwise.

### Typed Mosaic Evidence

Potential future representation of explicit Seestar mosaic filesystem context.

Current status:

`DEFERRED FEATURE`

Do not promote it into required remediation merely because mosaic diagnostic cleanup may touch related normalization.

### Target Correction / Override

Future user-facing ability to correct or override target labels such as legitimate `Unknown` or reframed targets.

Current status:

`DEFERRED FEATURE`

Do not implement or schedule as a blocking Stage 8 remediation requirement unless there is direct evidence that current archive correctness depends on it.

## Required Consolidation Table

Produce a root-cause consolidation table with at least:

| Finding ID | Root cause | Evidence datasets | Classification | Material impact | Downstream effects | Proposed remediation stage | Regression fixture needed |
|------------|------------|-------------------|----------------|-----------------|--------------------|----------------------------|---------------------------|

Use stable finding IDs:

- `F8-01`, `F8-02`, ...

Repeated observations of the same underlying cause must be consolidated under one finding.

## Severity and Priority

For each root finding assign:

### Severity

Use:

- Critical
- High
- Medium
- Low
- Informational

Base severity on actual Toolkit correctness impact, not warning volume.

### Remediation Priority

Use:

- P1 — fix before further Stage 8 progression;
- P2 — fix during Stage 8 before closure;
- P3 — desirable but can be deferred beyond Stage 8;
- Deferred Feature — explicitly outside defect remediation.

Explain every assignment.

## Regression Fixture Strategy

Stage 8.1e must decide what minimal permanent fixtures are needed.

Constraints:

- do not copy complete real datasets into the repository;
- fixtures should be as small as practical;
- fixtures must preserve the exact metadata/timestamp relationship needed to reproduce the defect;
- fixture selection must be evidence-driven.

At minimum consider whether permanent fixtures are needed for:

1. equal final-light/stack timestamp ordering;
2. timezone diagnostic behaviour;
3. `_mosaic` target normalization/diagnostic behaviour;
4. retained-source count differing from `STACKCNT`;
5. Dataset 08-style multi-session protection against regression.

Do not create fixtures during Stage 8.1e.

For each proposed fixture, specify:

- purpose;
- minimal files required;
- metadata characteristics that must be retained;
- which remediation stage will create it;
- whether synthetic/unit data is sufficient or real trimmed FITS are required.

## Remediation Sequencing

Stage 8.1e must define the Stage 8.2x implementation sequence.

Prefer independent, reviewable sub-stages.

The plan should explicitly state dependencies and recommended order.

A likely structure may include separate remediation stages for:

- reconstruction ordering;
- timestamp diagnostics;
- mosaic target diagnostics;
- stack-count diagnostics;
- final real-data regression.

Do not assume this exact structure if evidence supports a better decomposition.

Each proposed Stage 8.2x sub-stage must include:

- purpose;
- finding IDs addressed;
- expected production areas;
- expected tests/fixtures;
- key non-regression constraints;
- closure criteria summary.

Do not write implementation code.

## Non-Regression Constraints

The remediation plan must explicitly protect all known correct behaviour, including:

- Datasets 01, 03, 04, 06 and 07 remain correctly reconstructed;
- all three Dataset 08 observations remain separate and COMPLETE;
- Dataset 08 Session 03 retains all 135 source lights;
- intermediate stacks remain valid session boundaries;
- cross-midnight observations are not split solely by calendar date;
- large gaps within stack-backed observations are not incorrectly split;
- FITS timestamps remain authoritative;
- `Unknown` remains a legitimate target;
- EQ and AltAz compatibility remain supported;
- firmware 7.75, 8.46 and 9.31 remain compatible;
- `BAYERPAT=GRBG` on RGB stacks must not cause raw-Bayer misclassification;
- archive planning continues to use the +12-hour astronomical-night rule;
- no assumption that retained source-light count must equal `STACKCNT` is introduced.

## Scope

Stage 8.1e includes:

- review of all Stage 8.1 evidence;
- consolidation of repeated findings;
- root-cause classification;
- severity;
- remediation priority;
- fixture strategy;
- Stage 8.2x sequencing;
- explicit non-regression constraints;
- documentation of deferred features.

## Exclusions

Stage 8.1e must not:

- modify production code;
- modify tests;
- create fixtures;
- change reconstruction ordering;
- change timestamp handling;
- change diagnostic thresholds;
- alter mosaic normalization;
- alter stack-count interpretation;
- change archive/session behaviour;
- implement target override;
- copy full datasets into the repository;
- execute archive COPY or MOVE;
- start a Stage 8.2 implementation;
- commit anything.

## Repository Validation

Because Stage 8.1e is documentation/analysis only, no source/test changes are expected.

At the end run:

`python -m pytest`

`ruff check .`

`git diff --check`

Record the results.

## Completion Report

Return a complete Stage 8.1e report containing:

### Stage 8.1e Result

Use:

- PASS;
- PASS WITH FINDINGS;
- FAIL — consolidation incomplete.

### Environment

Record:

- HEAD;
- working-tree state;
- Python executable/version;
- package import path.

### Evidence Summary

Summarise the nine datasets / 11 observations.

### Root-Cause Consolidation Table

Use stable `F8-*` IDs.

### Finding Details

For every root finding include:

- description;
- supporting datasets;
- classification;
- root cause;
- severity;
- remediation priority;
- downstream consequences;
- non-regression constraints;
- proposed fixture;
- proposed remediation stage.

### Deferred Features

Keep deferred features separate from defects.

### Regression Fixture Plan

Specify all recommended minimal fixtures.

### Stage 8.2x Remediation Plan

Define the implementation sequence with dependencies and closure intent.

### Final Non-Regression Matrix

Map each remediation finding against known-good Stage 8.1 behaviours that must remain protected.

### Repository Validation

Record pytest, Ruff and `git diff --check`.

### Files Changed

Identify every file changed during Stage 8.1e.

No production/test changes are expected.

### Closure Criteria

Report every criterion below individually.

## Closure Criteria

Stage 8.1e is complete only when all of the following are satisfied:

1. Actual starting Git HEAD is recorded and matches expected commit `d845067` or any difference is explained.
2. Intentional pending CHANGELOG/documentation changes are distinguished from unexpected working-tree changes.
3. Evidence from all nine datasets / 11 frozen observations is represented.
4. The three incorrect reconstructions are identified as Datasets 02, 05 and 09.
5. Equal-timestamp reconstruction failures are consolidated under a single root finding unless evidence proves otherwise.
6. Downstream archive consequences of the equal-timestamp defect are distinguished from the root reconstruction defect.
7. Timestamp diagnostic recurrence across all nine datasets is consolidated under one root finding.
8. Mosaic directory-target warnings across Datasets 02, 05, 07 and 09 are consolidated under one root finding.
9. Dataset 08 Session 03 count-warning semantics are consolidated under one root finding.
10. No unsupported additional defect category is invented.
11. Every root finding has a stable `F8-*` identifier.
12. Every root finding has an established Stage 8 classification.
13. Every root finding has an explicit severity.
14. Every root finding has an explicit remediation priority.
15. Severity is based on correctness impact rather than diagnostic volume.
16. Repeated symptoms are separated from root causes.
17. Known downstream consequences are documented.
18. The equal-timestamp finding includes the evidence that all equal cases failed and no non-equal case did.
19. The timestamp finding preserves FITS timestamps as authoritative.
20. The mosaic finding preserves evidence that Dataset 07 reconstructs correctly.
21. The stack-count finding preserves the valid 135 retained / 106 accepted / 3180-second evidence.
22. No assumption that retained-light count must equal `STACKCNT` is introduced.
23. `STACKCNT == TOTALEXP / EXPTIME` evidence is preserved.
24. Typed mosaic representation remains separated as a deferred feature unless direct evidence requires otherwise.
25. Target correction/override remains separated as a deferred feature.
26. A minimal regression-fixture strategy is defined.
27. Equal-timestamp regression coverage is explicitly planned.
28. Timestamp-diagnostic regression coverage is explicitly planned.
29. Mosaic-diagnostic regression coverage is explicitly planned.
30. Retained-source versus accepted-count regression coverage is explicitly planned.
31. Dataset 08 multi-session protection is included in regression planning.
32. Full real datasets are not proposed as permanent repository fixtures.
33. Each fixture proposal identifies purpose and minimal evidence required.
34. Each fixture proposal identifies the owning remediation stage.
35. Synthetic versus real trimmed-fixture suitability is considered.
36. A Stage 8.2x remediation sequence is defined.
37. Each proposed Stage 8.2x sub-stage identifies the finding IDs it addresses.
38. Dependencies between Stage 8.2x sub-stages are recorded.
39. Reconstruction correctness is prioritized ahead of purely diagnostic cleanup unless evidence supports another order.
40. A final all-dataset real-data regression stage is planned.
41. Non-regression constraints cover Datasets 01, 03, 04, 06 and 07.
42. Non-regression constraints protect all three Dataset 08 observations.
43. Non-regression constraints protect Dataset 08 Session 03 membership of 135 retained lights.
44. Non-regression constraints protect cross-midnight behaviour.
45. Non-regression constraints protect large-gap stack-backed observations.
46. Non-regression constraints protect intermediate-stack session separation.
47. Non-regression constraints protect legitimate `Unknown`.
48. Non-regression constraints protect EQ and AltAz behaviour.
49. Non-regression constraints protect firmware 7.75, 8.46 and 9.31.
50. Non-regression constraints protect RGB-stack classification despite `BAYERPAT=GRBG`.
51. Non-regression constraints protect the +12-hour archive-date rule.
52. No production code is changed.
53. No tests are changed.
54. No fixtures are created.
55. No remediation is implemented.
56. No full dataset is copied into the repository.
57. No archive COPY or MOVE operation is executed.
58. No Stage 8.2 implementation is started.
59. Full repository pytest passes.
60. Ruff passes.
61. `git diff --check` passes.
62. All files changed during Stage 8.1e are identified.
63. The final consolidation is sufficiently precise to launch Stage 8.2a without reopening broad Stage 8.1 evidence gathering.

## Expected Next Stage

After Stage 8.1e closure, begin the first Stage 8.2 remediation sub-stage according to the consolidation result.

The first implementation stage should address the highest-priority confirmed defect while preserving the non-regression constraints defined here.
