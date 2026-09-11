# STAGE 7.1e — Safe archive file operations

## Status

**Stage:** 7.1e  
**Stage title:** Safe archive file operations  
**Starting commit:** `7c1086f` — `Stage 7.1d: plan archive destinations`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording the preceding Stage 7.1d commit may already be present in the working tree. It is expected and must not be treated as an unexpected dirty-tree condition.

---

## 1. Purpose

Stage 7.1e implements the filesystem execution layer for already-planned archive file operations.

Stage 7.1d decides *where* files should go.

Stage 7.1e decides *how* original source files are safely copied or moved into those planned destinations.

This stage must provide:

- safe directory creation for planned archive destinations;
- safe copy execution;
- optional explicit move execution;
- collision detection;
- identical-content handling;
- protection against silent overwrite;
- rollback/partial-failure awareness;
- deterministic execution results;
- filesystem mutation only for approved source-file archive actions.

This stage must **not** generate TIFF files, build INDEX.md, implement archive CLI prompting, perform reverse geocoding, or implement full archive orchestration.

---

## 2. Required outcome

After Stage 7.1e, the codebase must expose an execution API that:

1. consumes an ArchivePlan from Stage 7.1d;
2. validates planned filesystem operations before mutation;
3. creates required archive directories safely;
4. copies original source FITS files by default;
5. supports move only as an explicit opt-in action;
6. compares existing destination files reliably when collisions occur;
7. supports deterministic collision policy decisions;
8. never silently overwrites different content;
9. removes a source during move only after destination success is established;
10. reports per-file success, skip, collision, and failure results;
11. preserves Stage 7.1d planning semantics;
12. performs no TIFF generation.

---

## 3. Inputs

The execution layer consumes Stage 7.1d planning output.

Conceptually:

```python
plan = plan_seestar_archive(...)
result = execute_archive_plan(plan, ...)
```

Exact API names are illustrative.

Stage 7.1e must not:

- rediscover source files;
- reconstruct observations;
- recalculate archive hierarchy decisions independently.

It may validate that planned source/destination paths are still safe and usable at execution time.

---

## 4. Source action policy

Stage 7.1a fixed the safe default source action as:

```text
copy
```

Stage 7.1e must support at least:

- COPY
- MOVE

Move must be explicit/opt-in.

There must be no implicit default move.

Compression remains deferred.

---

## 5. Copy semantics

For a planned source FITS file:

1. validate source exists and is a regular file;
2. validate destination remains under the planned archive root;
3. create required parent directories safely;
4. detect destination collision before writing;
5. write/copy safely;
6. verify successful completion sufficiently before reporting success.

Use standard-library file-copy primitives unless there is a strong existing project convention otherwise.

Preserve original file content exactly.

Preserving metadata such as mtime is acceptable where supported by the chosen copy primitive, but source content integrity is more important than metadata preservation.

---

## 6. Move semantics

Move is explicit.

Safety rule:

> The source must not be removed until destination success is established.

Implementation may use copy-then-delete semantics rather than blind rename if that provides safer cross-filesystem behavior.

Requirements:

- destination content must be successfully established first;
- source deletion happens only after destination success;
- if destination write fails, source remains untouched;
- if source deletion fails after successful copy, result must clearly report partial completion;
- no silent data loss.

Cross-filesystem behavior must be safe.

---

## 7. Collision policy

Stage 7.1a defined conceptual choices:

- Skip
- Overwrite
- Cancel

Stage 7.1e must implement a clear typed collision policy suitable for later CLI use.

At minimum support:

- SKIP_IDENTICAL / SKIP
- OVERWRITE
- CANCEL / ERROR

Exact enum names may follow project style.

Default policy must be safe and non-destructive.

Recommended default:

```text
skip identical content, error/cancel on different content
```

Do not silently overwrite.

---

## 8. Content identity

File identity must use reliable content comparison.

Use SHA-256 or an equivalently strong whole-file comparison.

Do not rely only on:

- filename;
- file size;
- mtime;
- path.

An implementation may use a size pre-check before hashing as an optimization, but final identity must be content-based.

Hashing must be deterministic and streamed rather than loading large FITS files entirely into memory.

---

## 9. Existing destination — identical content

If destination exists and content is identical:

Safe/default behavior:

- report as skipped/already present;
- do not rewrite unnecessarily;
- do not delete source under COPY;
- under MOVE, source may be removed only if policy explicitly defines identical destination as successfully archived and tests prove the behavior is safe.

If MOVE + identical destination removes source, this must be explicit, documented, and tested.

Otherwise, safest behavior is to retain source and report skipped.

Codex should choose one coherent policy and document it.

---

## 10. Existing destination — different content

If destination exists with the same planned path but different content:

- never silently overwrite;
- default behavior must fail/cancel that file operation safely;
- OVERWRITE may be supported only when explicitly selected;
- overwrite must not delete the existing file until replacement success is secured.

If atomic replacement is practical, prefer it.

If not, use a clearly safe staged replacement strategy.

---

## 11. Temporary/staged writes

To avoid partially written destination files, use a safe staged-write approach where appropriate.

For example:

```text
destination.tmp-<unique>
```

then atomically replace/rename into final destination after successful copy.

Requirements:

- temporary files are created in the destination filesystem where practical;
- temporary files are cleaned up after failure;
- no stale partial file is mistaken for success;
- temporary names must not collide deterministically.

Do not over-engineer journaling.

---

## 12. Directory creation

Stage 7.1e is the first Stage allowed to create planned archive directories.

Requirements:

- create only directories required by the approved ArchivePlan;
- use safe parent creation;
- existing correct directories are acceptable;
- existing non-directory path conflicts are errors;
- no source-directory mutation;
- no unrelated archive directories.

Do not pre-create directories for unresolved/unplanned observations.

---

## 13. Archive-root safety revalidation

Even though Stage 7.1d already validated paths, execution must defensively verify:

- destination paths remain under archive root;
- no traversal/escape is possible;
- symlink behavior does not allow an unsafe escape.

Execution should not blindly trust a maliciously forged ArchivePlan object.

A reasonable real-path/symlink safety strategy should be implemented and tested.

Do not follow destination symlinks outside the archive root.

---

## 14. Source safety

Source paths must be validated before mutation.

At minimum:

- source exists;
- source is a regular file;
- source is not the same path as destination;
- source and destination identity are not confused via symlinks/hardlinks where practical;
- move deletion is limited strictly to the intended source file.

Do not recursively remove directories.

---

## 15. Planned file scope

Stage 7.1d plans both:

- original FITS destinations;
- future TIFF derivative destinations.

Stage 7.1e must execute **only original source-file archive operations**.

It must not attempt to materialize planned TIFF derivative destinations.

This distinction must be explicit in the model/API/tests.

Stage 7.1f will integrate TIFF generation.

---

## 16. Which source files are executable

Executable original files include:

- individual light FIT/FITS source files;
- Seestar stacked FIT/FITS source files.

Do not execute:

- TIFF derivative plans;
- JPEG/thumbnail items;
- INDEX.md;
- future DSLR assets.

---

## 17. Execution result model

Introduce the minimum immutable result model needed for later orchestration.

Conceptually:

```text
ArchiveExecutionStatus
ArchiveFileExecutionResult
ArchiveExecutionResult
```

Per-file result should retain, where useful:

- source path;
- destination path;
- requested action;
- effective outcome;
- collision state;
- source hash and destination hash where calculated;
- bytes processed;
- diagnostic/error information.

Overall result should summarize:

- success count;
- skipped count;
- failed count;
- moved count;
- copied count;
- whether execution completed fully or partially.

Exact names should follow project style.

---

## 18. Partial failure

One file failure must not cause silent loss of information about previous successful operations.

The API should have a clear policy:

- either stop immediately on first hard failure and report completed prior operations;
- or continue independent operations and return a partial-success result.

Whichever is chosen must be deterministic and documented.

Recommended for batch-like archive execution:

> continue independent file operations, collect failures, and return an explicit partial result.

Do not hide partial completion behind a generic success boolean.

---

## 19. Idempotency

Re-running the same COPY plan against an already successfully copied archive should be safe.

Expected behavior:

- identical destinations are recognized;
- no duplicate content is created;
- no destructive overwrite occurs by default;
- result reports already-present/skipped items.

Tests must verify safe rerun behavior.

---

## 20. MOVE idempotency boundary

After a successful MOVE, the source no longer exists.

Re-running the same stale plan should report source missing clearly rather than pretending success.

Future orchestration may regenerate a fresh plan.

Do not silently reinterpret missing source as success unless the destination is verified identical and policy explicitly supports that behavior.

---

## 21. Overwrite safety

If explicit overwrite is supported:

- destination replacement must be staged safely;
- failed replacement must not destroy the previous valid destination;
- source removal under MOVE happens only after replacement succeeds;
- overwrite behavior must be thoroughly tested.

If robust overwrite cannot be implemented cleanly in this stage, Codex may implement ERROR/CANCEL and SKIP safely and leave overwrite as an explicit unsupported policy error, provided this is clearly documented and Stage-chat can review it.

However, the collision-policy model should remain extensible.

---

## 22. Hashing API

A small reusable internal/public helper for SHA-256 is acceptable.

Requirements:

- streamed reads;
- deterministic digest;
- binary mode;
- meaningful errors;
- no whole-file memory load.

Do not expose hashing as a broader end-user CLI feature.

---

## 23. Filesystem abstraction boundary

Do not introduce a large virtual filesystem framework.

Use Python pathlib/shutil/os primitives coherently.

Small test seams/helpers are acceptable.

Keep implementation understandable and auditable.

---

## 24. Error model

Extend archive exceptions minimally.

Potential categories:

- ArchiveExecutionError
- ArchiveSourceError
- ArchiveDestinationError
- ArchiveCollisionError
- ArchiveMoveError

Exact design should fit current exceptions architecture.

Do not broadly catch all exceptions and convert programming bugs into file-operation failures.

Catch expected filesystem exceptions narrowly.

---

## 25. Dry-run boundary

Stage 7.1a requires a future dry-run mode.

However Stage 7.1e does **not** implement archive dry-run CLI/orchestration.

The execution API may be structured so dry-run can later reuse planning without mutation, but no fake execution mode is required here.

Stage 7.1g owns user-facing dry-run.

---

## 26. TIFF boundary

Stage 7.1e must not call:

```text
convert_fits_to_tiff()
```

or any equivalent TIFF writer/conversion code.

Stage 7.1f will integrate TIFF generation after original archive file execution semantics are proven safe.

---

## 27. Compression boundary

Do not implement:

- gzip;
- zip;
- tgz;
- source compression;
- compressed archive replacement.

Compression remains deferred pending representative FITS measurements and later design.

---

## 28. Documentation updates

Codex must update documentation as required.

At minimum:

- preserve `docs/change_documents/STAGE_7/STAGE_7.1e.md` as the authoritative specification;
- update `docs/PROJECT_Notes.md` with Stage 7.1e current focus/progress;
- update `docs/ARCHITECTURE.md` with execution/collision/source-action contracts;
- preserve the intentional pending `docs/CHANGELOG.md` entry for commit `7c1086f`.

Do not mark Stage 7.1e complete before Stage-chat review.

---

## 29. Tests

Stage 7.1e requires focused automated tests.

At minimum cover:

1. COPY is the safe default source action;
2. valid planned source file copies successfully;
3. required destination parents are created;
4. source remains after COPY;
5. copied content is byte-identical;
6. MOVE must be explicit;
7. successful MOVE establishes destination before removing source;
8. successful MOVE removes source only after success;
9. failed destination write during MOVE leaves source;
10. source-delete failure after move-copy is reported as partial failure;
11. missing source is reported clearly;
12. non-regular source path is rejected;
13. source equal to destination is rejected;
14. existing identical destination is detected using content;
15. identical-content rerun is safe/idempotent;
16. same size but different content is not treated as identical;
17. same filename/path with different content never silently overwrites by default;
18. explicit collision policy behavior is deterministic;
19. explicit overwrite, if implemented, preserves safety;
20. cancellation/error collision leaves both source and destination unchanged;
21. SHA-256 hashing is streamed;
22. planned destination remains under archive root;
23. forged/traversal destination outside root is rejected;
24. destination symlink escape is rejected;
25. existing non-directory parent path is rejected;
26. temporary/staged files are cleaned after failure;
27. no partial destination remains after failed copy;
28. light FITS planned files are executable;
29. stack FITS planned files are executable;
30. planned TIFF derivatives are not executed;
31. JPEGs are not executed;
32. no TIFF conversion occurs;
33. no INDEX.md generation occurs;
34. no compression occurs;
35. multiple independent operations can return explicit partial completion;
36. execution results retain useful per-file outcomes;
37. repeat COPY plan against identical archive is safe;
38. stale MOVE plan with missing source is visible;
39. Stage 7.1d planning tests remain green;
40. Stage 7.1c reconstruction tests remain green;
41. Stage 7.1b discovery tests remain green;
42. Stage 2–6 tests remain green.

Use temporary directories/files for filesystem tests.

Do not use real user paths.

---

## 30. Validation requirements

Codex must run at least:

```text
pytest
ruff check .
git diff --check
```

Run formatting validation for changed Python files.

Explicitly confirm:

- Stage 7.1d planning API/tests remain green;
- Stage 7.1c reconstruction API/tests remain green;
- Stage 7.1b discovery API/tests remain green;
- Stage 6 `convert` remains unchanged;
- Stage 6 `convert-batch` remains flat and non-recursive;
- no TIFF generation occurs;
- no archive CLI was implemented;
- Stage 7.1f was not started.

---

## 31. Closure criteria

Stage 7.1e is ready for Stage-chat review only when all criteria below are satisfied.

1. A clear archive-execution API exists.
2. The API consumes Stage 7.1d ArchivePlan output.
3. The API does not rediscover source files.
4. The API does not reconstruct observations.
5. The API does not independently recalculate hierarchy placement.
6. A typed source-action model exists.
7. COPY is the safe/default action.
8. MOVE requires explicit selection.
9. Compression is not a source action.
10. Required archive parent directories can be created safely.
11. Existing valid directories are handled safely.
12. Existing non-directory parent conflicts are errors.
13. Only directories required by executable planned files are created.
14. Unresolved/unplanned observations do not cause directory creation.
15. Source existence is validated.
16. Source must be a regular file.
17. Source equal to destination is rejected.
18. Source mutation is limited to explicit MOVE deletion.
19. COPY preserves the source.
20. COPY establishes byte-identical destination content.
21. MOVE establishes destination before source removal.
22. Failed MOVE destination creation leaves source untouched.
23. Source deletion occurs only after successful destination establishment.
24. Source-deletion failure is surfaced explicitly.
25. Cross-filesystem move behavior is safe.
26. A typed collision-policy model exists.
27. Default collision behavior is non-destructive.
28. Existing destination identity uses reliable content comparison.
29. SHA-256 or equivalent whole-file identity is used.
30. Hashing does not rely only on name/size/mtime.
31. Hashing is streamed rather than whole-file loaded.
32. Existing identical destination is recognized.
33. Identical destination can be safely skipped/reported.
34. Re-running an already-completed COPY plan is safe.
35. Same-size different-content files are not treated as identical.
36. Existing different-content destination is never silently overwritten.
37. Default different-content collision fails/cancels safely.
38. Explicit overwrite, if supported, must be opt-in.
39. Failed overwrite must preserve the previous valid destination.
40. Collision cancellation/error leaves source unchanged.
41. Collision cancellation/error leaves destination unchanged.
42. Temporary/staged writes are used where needed to prevent partial destinations.
43. Failed writes do not leave a false-success final destination.
44. Temporary files are cleaned after expected failures.
45. Planned destination paths are revalidated against archive root.
46. Forged plans cannot escape archive root via traversal.
47. Destination symlink escape outside archive root is prevented.
48. Execution does not blindly trust a malicious ArchivePlan.
49. Original light FITS planned files are executable.
50. Original stack FITS planned files are executable.
51. Planned light TIFF derivative files are not executed.
52. Planned stack TIFF derivative files are not executed.
53. JPEGs are not executed.
54. INDEX.md is not generated.
55. No TIFF conversion function is called.
56. No compression is performed.
57. A typed per-file execution result exists.
58. An overall execution result exists.
59. Per-file results identify source and destination.
60. Per-file results identify requested action.
61. Per-file results identify effective outcome.
62. Collision/skipped states are visible.
63. Failure diagnostics are visible.
64. Overall results distinguish full success from partial completion.
65. Multiple independent operations can preserve completed successes while reporting later failures.
66. Partial failures are not hidden behind generic success.
67. MOVE completed-count reporting is accurate.
68. COPY completed-count reporting is accurate.
69. Skip reporting is accurate.
70. Failure reporting is accurate.
71. Execution result behavior is deterministic.
72. Stale MOVE plans with missing source do not silently succeed.
73. No recursive directory deletion occurs.
74. No unrelated files are modified.
75. No source directory is modified except explicit source-file removal under MOVE.
76. No filesystem mutation happens for planned TIFF derivative paths.
77. No reverse geocoding is introduced.
78. No network services are used.
79. No archive CLI is implemented.
80. No interactive prompting is implemented.
81. Dry-run CLI/orchestration is not implemented.
82. Execution API design remains suitable for future dry-run/orchestration reuse.
83. Stage 7.1d planning semantics remain unchanged.
84. Stage 7.1d planning tests remain green.
85. Stage 7.1c reconstruction tests remain green.
86. Stage 7.1b discovery tests remain green.
87. Existing Stage 2–6 tests remain green.
88. Focused Stage 7.1e tests cover COPY safety.
89. Focused tests cover MOVE safety.
90. Focused tests cover identical-content collisions.
91. Focused tests cover different-content collisions.
92. Focused tests cover path/symlink safety.
93. Focused tests cover partial failure.
94. Focused tests prove TIFF derivatives are not executed.
95. Full test suite passes.
96. Ruff lint passes.
97. Formatting validation for changed Python files passes.
98. `git diff --check` passes.
99. Stage 6 `convert` remains unchanged.
100. Stage 6 `convert-batch` remains flat and non-recursive.
101. Broad real-dataset qualification remains Stage 8.
102. Packaging/release remains Stage 9.
103. Documentation records Stage 7.1e accurately without prematurely marking it complete.
104. Expected pending `docs/CHANGELOG.md` entry for Stage 7.1d is preserved.
105. Codex makes no Git commit.
106. Stage 7.1f is not started.

---

## 32. Codex completion report

Codex must return a concise completion report containing:

1. files changed;
2. public execution API/model summary;
3. implemented COPY rule;
4. implemented MOVE rule;
5. implemented collision/content-identity rule;
6. implemented path/symlink safety rule;
7. implemented partial-failure/result model;
8. exact boundary proving TIFF derivative plans are not executed;
9. test additions and what they prove;
10. validation commands and exact results;
11. explicit confirmation of closure criteria 1–106, or identification of any criterion not satisfied;
12. assumptions, uncertainties, and contradictions discovered;
13. current `git status --short`;
14. confirmation that no Git commit was made;
15. confirmation that Stage 7.1f was not started.

Do **not** commit the changes.

The Stage chat will audit the completion report against all closure criteria before Stage 7.1e can be marked COMPLETE and before a Git commit message is issued.
