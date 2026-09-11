# STAGE 7.1f — Integrate TIFF generation and archive orchestration

## Status
**Stage:** 7.1f  
**Stage title:** Integrate TIFF generation and archive orchestration  
**Starting commit:** `7bdc859` — `Stage 7.1e: add safe archive file operations`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording Stage 7.1e may already be present. It is expected.

## 1. Purpose
Stage 7.1f integrates the completed Stage 7 archive pipeline with the established FITS-to-TIFF conversion pipeline.

The integrated library workflow becomes:

```text
Seestar source root
  -> discovery (7.1b)
  -> observation reconstruction (7.1c)
  -> archive planning (7.1d)
  -> safe original FITS execution (7.1e)
  -> TIFF generation into the destinations already planned by 7.1d
```

This stage provides library-level archive orchestration only.

It must not add the user-facing archive CLI, interactive prompting, dry-run UI, reverse geocoding, INDEX.md generation, compression, or DSLR ingestion.

## 2. Required outcome
Expose a coherent orchestration API that can:
1. consume a source root and archive-planning inputs;
2. run the existing discovery/reconstruction/planning pipeline without duplicating it;
3. execute original FITS archive actions through Stage 7.1e;
4. generate TIFF derivatives through the established conversion API;
5. place TIFFs exactly at Stage 7.1d planned TIFF destinations;
6. preserve dtype/shape behavior established in Stages 3–6;
7. avoid TIFF generation when the corresponding original archive operation is unsafe or failed;
8. report original-file and TIFF outcomes separately and clearly;
9. expose partial completion;
10. remain independent of argparse and interaction.

## 3. Reuse requirements
Do not duplicate existing subsystems.

Reuse:
- `discover_seestar_inputs()`
- `reconstruct_seestar_observations()`
- `plan_seestar_archive()`
- `execute_archive_plan()`
- established FITS-to-TIFF conversion, preferably `convert_fits_to_tiff()`.

Do not introduce another FITS reader, demosaicer, RGB normalizer, or TIFF writer.

## 4. Orchestration boundary
A conceptual API is:

```python
result = archive_seestar_session(
    source_root,
    *,
    archive_root,
    hierarchy_template="{target}/{location}/{session_end_date}",
    explicit_location=None,
    saved_locations=(),
    source_action=SourceAction.COPY,
    collision_policy=CollisionPolicy.SKIP_IDENTICAL,
)
```

Exact naming/signature should follow project style.

The orchestration API should expose or retain intermediate discovery, reconstruction, plan, execution, and TIFF results where useful for later CLI reporting.

## 5. Order of operations
The implementation must use a safe deterministic order.

Required principle:
1. discover;
2. reconstruct;
3. plan;
4. execute original FITS archive operation;
5. generate TIFF only for eligible successful/safely-present archived originals.

TIFF generation must not precede planning.

TIFF generation must not cause a failed original FITS archive operation to be reported as fully successful.

## 6. TIFF source choice
TIFF generation should operate from the successfully archived FITS destination where practical, rather than depending on a source that may have been moved/deleted.

This is especially important for `SourceAction.MOVE`.

After a successful MOVE, TIFF generation must still work.

For identical-destination skip cases, TIFF generation may use the verified archived FITS destination.

## 7. TIFF destination contract
Use only the TIFF paths already produced by Stage 7.1d.

Lights:
```text
observation_NN/tiff/<light basename>.tiff
```

Seestar stack:
```text
observation_NN/seestar_stacked/<stack basename>.tiff
```

Do not independently recalculate TIFF names or hierarchy placement.

## 8. TIFF conversion behavior
Use the established conversion contract.

Expected validated output behavior remains:
- raw Bayer Seestar light -> RGB `(H, W, 3)` `uint16`;
- native Seestar RGB -> normalized RGB `uint16`;
- Siril RGB support remains unchanged in the existing converter;
- float32 output behavior remains unchanged where applicable.

Stage 7.1f must not change demosaicing, RGB normalization, or TIFF encoding policy.

## 9. TIFF existing-destination policy
TIFF creation must be non-destructive by default.

Do not silently overwrite an existing TIFF.

Use a clear policy consistent with existing conversion semantics and archive collision safety.

If the existing converter uses exclusive-create behavior, preserve it unless orchestration has explicit, safely tested policy handling.

A pre-existing TIFF should produce a visible skipped/collision/failure outcome, not silent replacement.

Do not invent TIFF content hashing unless necessary for a coherent minimal policy.

## 10. TIFF failure behavior
If TIFF conversion fails:
- original archived FITS must remain valid;
- source must not be restored/deleted merely because TIFF failed;
- failure must be reported explicitly;
- later independent TIFF operations may continue if that is the chosen orchestration policy.

Recommended: continue independent items and return partial completion.

## 11. MOVE + TIFF failure
For explicit MOVE:
- successful original archive move remains successful even if TIFF generation later fails;
- source must not be recreated or silently restored;
- orchestration result must clearly distinguish archived-original success from derivative failure.

## 12. Eligibility mapping
TIFF generation must map each executable `PlannedFile` to its corresponding Stage 7.1e execution result.

Eligible examples:
- `COPIED`
- `MOVED`
- `SKIPPED_IDENTICAL` where archived destination has been verified identical.

Ineligible examples:
- `COLLISION`
- `FAILED`
- `PARTIAL` unless the destination is explicitly verified safe and the policy documents why it is eligible.

Use conservative eligibility.

## 13. Result model
Introduce minimal immutable orchestration/TIFF result models.

Conceptually:
```text
ArchiveTiffOutcome
ArchiveTiffResult
SeestarArchiveResult
```

Per-TIFF result should retain:
- archived FITS input path;
- planned TIFF destination;
- outcome;
- diagnostic/error.

Overall result should retain or expose:
- discovery result;
- reconstruction result;
- archive plan;
- Stage 7.1e execution result;
- TIFF results;
- overall complete/partial/failed state.

Do not hide original-file failures behind TIFF success.

## 14. Status semantics
Define deterministic aggregate status.

A fully COMPLETE result requires all required original archive operations and all eligible TIFF conversions to succeed or satisfy an explicitly safe already-present policy.

Any mixture of success and failure should be PARTIAL.

A wholly unusable workflow should be FAILED.

Exact enum reuse/new type should follow existing architecture.

## 15. Planning problems
Observations that Stage 7.1d cannot safely plan must remain visible.

Orchestration must not override planning ambiguity.

No prompting is allowed in 7.1f.

Later Stage 7.1g CLI interaction may resolve user-input cases.

## 16. Empty/no-input behavior
Handle empty discovery/reconstruction/plan results deterministically.

Do not create archive directories merely because orchestration was invoked.

Return an explicit meaningful result rather than crashing.

## 17. Source action and collision policy
Pass Stage 7.1e source-action and collision-policy inputs through unchanged.

Do not redefine copy/move safety.

Do not duplicate collision hashing.

## 18. Filesystem safety
All original-file filesystem safety remains owned by Stage 7.1e.

TIFF generation must:
- use planned destinations;
- not escape archive root;
- not follow a forged TIFF destination outside the validated plan/root;
- create only TIFF parent directories required for eligible conversions.

Defensively validate TIFF destination containment if needed.

## 19. No rollback of successful originals
Do not implement broad transactional rollback.

If original FITS archival succeeds and TIFF conversion fails, retain the archived FITS.

Report partial completion.

## 20. No JPEG handling
JPEG and thumbnail policy remains `ignore`.

Do not convert, move, copy, or delete JPEGs.

## 21. No INDEX.md
Do not generate target `INDEX.md`.

Stage 7.1h owns index generation.

Retain metadata needed later.

## 22. No archive CLI
Do not add argparse commands/options.

Stage 7.1g owns archive CLI, interaction, and dry-run.

## 23. No dry-run
Do not implement user-facing dry-run behavior in 7.1f.

The orchestration architecture should remain compatible with later dry-run using the same planning path.

## 24. No reverse geocoding
Do not call external services.

No network dependency.

## 25. No compression
Do not gzip/zip/tgz original FITS.

## 26. Future DSLR
Keep orchestration naming/models reasonably extensible, but implement Seestar only.

No EXIF/Canon/DSLR ingestion.

## 27. Tests
Add focused tests covering at minimum:
1. full synthetic discovery -> reconstruction -> planning -> copy -> TIFF workflow;
2. raw Bayer light TIFF generation through established converter;
3. native Seestar RGB stack TIFF generation through established converter;
4. TIFF destinations exactly match Stage 7.1d plan;
5. no independent TIFF path recalculation;
6. COPY source remains;
7. MOVE source removed after successful archive operation;
8. TIFF generation still succeeds after MOVE;
9. identical archived FITS skip can still generate missing TIFF;
10. failed original archive copy does not generate TIFF;
11. original collision does not generate TIFF;
12. TIFF failure preserves archived FITS;
13. TIFF failure after MOVE does not restore source;
14. independent TIFF conversions continue after one expected failure;
15. partial result accurately reports mixed outcomes;
16. full success reports complete;
17. wholly failed workflow reports failed;
18. planning ambiguity remains visible and unexecuted;
19. empty source behavior;
20. pre-existing TIFF is not silently overwritten;
21. light TIFF lands under `tiff/`;
22. stack TIFF lands under `seestar_stacked/`;
23. JPEGs untouched;
24. no INDEX.md generation;
25. no compression;
26. no network/geocoder;
27. orchestration independent of argparse;
28. Stage 7.1e execution tests remain green;
29. Stage 7.1d planning tests remain green;
30. Stage 7.1c reconstruction tests remain green;
31. Stage 7.1b discovery tests remain green;
32. Stage 5/6 conversion tests remain green;
33. full Stage 2–6 suite remains green.

Use temporary filesystem fixtures for orchestration tests. Real FITS fixtures may be used selectively for converter integration.

## 28. Documentation
Update as needed:
- preserve `docs/change_documents/STAGE_7/STAGE_7.1f.md` as authoritative;
- update `docs/PROJECT_Notes.md`;
- update `docs/ARCHITECTURE.md`;
- preserve expected pending `docs/CHANGELOG.md` entry for `7bdc859`.

Do not mark Stage 7.1f complete before Stage-chat review.

## 29. Explicit exclusions
Do not implement:
- archive CLI;
- interactive prompts;
- dry-run CLI/orchestration;
- reverse-geocoding providers;
- INDEX.md generation;
- JPEG archive operations;
- compression;
- DSLR ingestion;
- new demosaic algorithms;
- new RGB normalization;
- new TIFF encoding policy;
- Stage 8 broad qualification;
- Stage 9 packaging/release.

## 30. Validation
Run at least:
```text
pytest
ruff check .
git diff --check
```

Run formatting validation for changed Python files.

Explicitly confirm:
- Stage 7.1e execution tests remain green;
- Stage 7.1d planning tests remain green;
- Stage 7.1c reconstruction tests remain green;
- Stage 7.1b discovery tests remain green;
- Stage 5/6 TIFF/conversion tests remain green;
- Stage 6 `convert` unchanged;
- Stage 6 `convert-batch` remains flat/non-recursive;
- no archive CLI;
- no INDEX.md;
- Stage 7.1g not started.

## 31. Closure criteria
1. Public Seestar archive orchestration API exists.
2. It composes existing Stage 7.1b–7.1e APIs rather than duplicating them.
3. Discovery remains delegated to `discover_seestar_inputs()`.
4. Reconstruction remains delegated to `reconstruct_seestar_observations()`.
5. Planning remains delegated to `plan_seestar_archive()`.
6. Original FITS execution remains delegated to `execute_archive_plan()`.
7. TIFF generation reuses established FITS-to-TIFF conversion.
8. No duplicate FITS reader is added.
9. No duplicate demosaicer is added.
10. No duplicate RGB normalizer is added.
11. No duplicate TIFF writer is added.
12. Orchestration is independent of argparse.
13. COPY remains default source action.
14. MOVE remains explicit.
15. Collision policy passes through Stage 7.1e.
16. Discovery occurs before reconstruction.
17. Reconstruction occurs before planning.
18. Planning occurs before filesystem execution.
19. Original FITS execution occurs before corresponding TIFF generation.
20. TIFF generation uses Stage 7.1d planned destinations.
21. TIFF paths are not independently recalculated.
22. Light TIFFs target `observation_NN/tiff/`.
23. Stack TIFFs target `observation_NN/seestar_stacked/`.
24. Original FITS filenames remain unchanged.
25. TIFF derivative basename/extension policy remains unchanged.
26. TIFF conversion uses archived FITS destination where practical.
27. Successful MOVE still permits TIFF generation.
28. COPY preserves source.
29. MOVE source deletion remains governed solely by Stage 7.1e.
30. TIFF failure does not undo successful original archival.
31. TIFF failure after MOVE does not restore source.
32. Failed original archival prevents corresponding TIFF generation.
33. Original collision prevents corresponding TIFF generation unless Stage 7.1e verified archived content as identical.
34. `SKIPPED_IDENTICAL` can support TIFF generation from verified archive FITS.
35. Eligibility mapping from execution result to TIFF generation is explicit.
36. Eligibility is conservative.
37. Pre-existing TIFF is not silently overwritten.
38. TIFF collision/existence outcome is visible.
39. TIFF conversion errors are visible.
40. TIFF failure preserves archived FITS.
41. Independent TIFF operations can continue after an expected conversion failure.
42. No broad rollback deletes successful originals.
43. Typed per-TIFF result exists.
44. Overall orchestration result exists.
45. Result retains/exposes discovery outcome.
46. Result retains/exposes reconstruction outcome.
47. Result retains/exposes archive plan.
48. Result retains/exposes Stage 7.1e execution outcome.
49. Result retains/exposes TIFF outcomes.
50. TIFF result identifies archived FITS input.
51. TIFF result identifies planned TIFF destination.
52. TIFF result identifies outcome.
53. TIFF result exposes diagnostics.
54. Aggregate COMPLETE semantics are deterministic.
55. Aggregate PARTIAL semantics are deterministic.
56. Aggregate FAILED semantics are deterministic.
57. Original archive failure cannot be hidden by TIFF success.
58. TIFF failure prevents false COMPLETE.
59. Planning problems remain visible.
60. Orchestration does not silently resolve ambiguous observations.
61. No interactive prompt is added.
62. Empty/no-input behavior is deterministic.
63. Empty workflow does not create archive directories unnecessarily.
64. TIFF parent directories are created only for eligible conversions.
65. TIFF destination containment is safe.
66. Forged TIFF destination escape is not executed.
67. JPEGs are not copied.
68. JPEGs are not moved.
69. JPEGs are not deleted.
70. JPEGs are not converted.
71. INDEX.md is not generated.
72. Compression is not performed.
73. Reverse geocoding is not performed.
74. No network service is required.
75. DSLR ingestion is not implemented.
76. Existing raw Bayer conversion behavior remains unchanged.
77. Existing native Seestar RGB conversion behavior remains unchanged.
78. Existing Siril RGB conversion behavior remains unchanged.
79. Existing uint16 TIFF behavior remains unchanged.
80. Existing float32 TIFF behavior remains unchanged.
81. Stage 7.1e execution semantics remain unchanged.
82. Stage 7.1d planning semantics remain unchanged.
83. Stage 7.1c reconstruction semantics remain unchanged.
84. Stage 7.1b discovery semantics remain unchanged.
85. Focused orchestration tests cover full COPY workflow.
86. Focused tests cover MOVE + TIFF.
87. Focused tests cover identical archived FITS + missing TIFF.
88. Focused tests cover failed original archival.
89. Focused tests cover TIFF failure.
90. Focused tests cover partial completion.
91. Focused tests cover TIFF destination placement.
92. Focused tests cover existing TIFF safety.
93. Focused tests prove JPEG exclusion.
94. Focused tests prove INDEX exclusion.
95. Stage 7.1e tests pass.
96. Stage 7.1d tests pass.
97. Stage 7.1c tests pass.
98. Stage 7.1b tests pass.
99. Stage 5/6 conversion tests pass.
100. Existing Stage 2–6 tests pass.
101. Full test suite passes.
102. Ruff lint passes.
103. Formatting validation passes.
104. `git diff --check` passes.
105. Stage 6 `convert` remains unchanged.
106. Stage 6 `convert-batch` remains flat and non-recursive.
107. No archive CLI is implemented.
108. No dry-run UI/orchestration is implemented.
109. Broad real-dataset qualification remains Stage 8.
110. Packaging/release remains Stage 9.
111. Documentation accurately records Stage 7.1f without premature closure.
112. Expected pending CHANGELOG entry for Stage 7.1e is preserved.
113. Codex makes no Git commit.
114. Stage 7.1g is not started.

## 32. Codex completion report
Return:
1. files changed;
2. public orchestration API/models;
3. exact composed pipeline;
4. TIFF source/destination policy;
5. COPY/MOVE integration behavior;
6. TIFF eligibility mapping;
7. TIFF collision/failure policy;
8. aggregate result/status semantics;
9. tests added;
10. validation commands and exact results;
11. explicit confirmation of criteria 1–114 or exceptions;
12. assumptions/open points;
13. `git status --short`;
14. confirmation no commit;
15. confirmation Stage 7.1g not started.

Do not commit. Stage chat will audit before closure.
