# STAGE 7.1c — Observation reconstruction and stack association

## Status

**Stage:** 7.1c  
**Stage title:** Observation reconstruction and stack association  
**Starting commit:** `610db0d` — `Stage 7.1b: add Seestar input discovery`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording the preceding Stage 7.1b commit may already be present in the working tree. It is expected and must not be treated as an unexpected dirty-tree condition.

---

## 1. Purpose

Stage 7.1c takes the deterministic inventory produced by Stage 7.1b and reconstructs logical Seestar observations.

The Seestar source layout does not create one directory per observation. Multiple capture runs for the same target may coexist in the same product and `_sub` directories across one or more nights.

Therefore Stage 7.1c must infer observation boundaries from discovered file evidence.

The primary architecture rule is:

> A recognised Seestar stacked FITS is the primary end-of-observation marker.

Stage 7.1c must implement that rule conservatively, deterministically, and without filesystem mutation.

---

## 2. Required outcome

After Stage 7.1c, the codebase must expose a reconstruction API that:

1. accepts the Stage 7.1b discovery inventory;
2. selects discovered light and Seestar stack candidates;
3. derives/retains reliable capture-time evidence;
4. orders compatible candidates chronologically;
5. treats each recognised Seestar stack as an observation boundary;
6. associates compatible preceding unassigned lights with that stack;
7. preserves stack-count metadata only as supporting evidence;
8. represents missing-stack, orphan, timestamp, and compatibility ambiguity explicitly;
9. supports the intentional observation-merge behaviour established in Stage 7.1a;
10. returns logical reconstruction results without assigning archive destination paths;
11. performs no filesystem mutation.

The reconstruction output becomes the input contract for Stage 7.1d.

---

## 3. Input contract

The input is the typed inventory returned by the Stage 7.1b archive discovery API, currently exposed conceptually as:

```python
inventory = discover_seestar_inputs(root)
```

Stage 7.1c must consume the discovery model rather than rescan the source tree independently.

It must not introduce a second filesystem discovery path.

Unknown/JPEG candidates are not observation source frames and should not be treated as light or stack boundaries.

---

## 4. Observation terminology

An **observation** is one logical imaging capture/run of one target.

A reconstructed observation should contain, at minimum:

- one or more associated light candidates where available;
- zero or one associated recognised Seestar stack;
- first-light timestamp where available;
- last-light timestamp where available;
- stack timestamp where available;
- compatibility metadata/evidence used for association;
- reconstruction status/diagnostics sufficient to expose ambiguity.

A stack-only case may exist and must remain visible.

A lights-only case may exist and must remain visible.

---

## 5. Primary stack-boundary rule

For a compatible chronological sequence:

```text
light
light
light
stack
```

the stack closes the observation.

For:

```text
light
light
stack A
light
light
stack B
```

two observations are reconstructed.

Normative rule:

> Each recognised Seestar stacked FITS closes one observation consisting of compatible preceding lights that have not already been assigned to an earlier stack.

Stage 7.1c must not look ahead and assign post-stack lights backwards to an already-closed observation.

---

## 6. Intentional observation merging

The Stage 7.1a merge behaviour becomes operational here.

If intermediate recognised stack files are absent/ineligible and only the final stack remains discovered:

```text
capture A lights
capture B lights
capture C lights
final stack
```

then all compatible preceding unassigned lights may reconstruct as one logical observation ending at that final stack.

If intermediate recognised stack files are present:

```text
capture A lights
stack A
capture B lights
stack B
```

they create separate observation boundaries.

Important:

- no source files are modified;
- compatibility rules still apply;
- a missing intermediate stack must not cause incompatible lights to be merged;
- user-facing documentation must eventually explain that stack eligibility controls grouping boundaries.

Stage 7.1c implements the reconstruction consequence only. It does not implement an exclude/ignore CLI mechanism.

---

## 7. Timestamp evidence

### 7.1 Need for explicit timestamp handling

Reconstruction must not depend on lexical filename ordering alone.

Capture-time evidence may come from:

- FITS metadata already exposed through `FitsInspection`;
- Seestar filename timestamp evidence;
- other existing inspection metadata if already available.

Codex must first inspect the current Stage 2/7.1b models to determine exactly which timestamp fields are available.

### 7.2 Authority and conflict policy

Where both FITS metadata and filename timestamp are available:

- FITS metadata should be treated as the preferred evidence when it is clearly the capture time;
- filename timestamp remains useful corroborating evidence;
- material disagreement must remain visible as a diagnostic/problem;
- Stage 7.1c must not silently choose one value without documenting the precedence.

If the existing `FitsInspection` does not yet expose a suitable capture timestamp, Stage 7.1c may add the minimum metadata extraction needed through the existing FITS subsystem rather than creating a parallel FITS parser.

### 7.3 Material disagreement

The implementation should define a small, documented threshold for what constitutes timestamp disagreement versus expected representation/rounding differences.

Do not overfit the threshold to a single fixture.

### 7.4 Missing timestamp

A light or stack lacking usable time evidence must not disappear.

It should become an unresolved/orphan/ambiguous reconstruction item as appropriate.

---

## 8. Compatibility rules

A preceding light must not be assigned to a stack merely because its timestamp is earlier.

Compatibility should use available evidence such as:

- target identity/evidence;
- exposure time;
- filter;
- relevant capture mode or image characteristics;
- other stable FITS metadata already available.

The compatibility model should be explicit and testable.

### 8.1 Target evidence

Where target metadata and directory target evidence conflict, Stage 7.1c should prefer the stronger established evidence while preserving/reporting conflicts.

Do not perform Stage 7.1d filesystem normalisation here.

### 8.2 Exposure/filter

Exposure and filter differences are strong reasons not to merge data into one observation unless architecture evidence shows otherwise.

### 8.3 Conservative rule

If compatibility cannot be established safely, do not silently associate the file.

Ambiguity is preferable to incorrect grouping.

---

## 9. Stack count policy

A Seestar stack filename may encode a count:

```text
Stacked_195_...
```

This is supporting evidence only.

It must never be used to take exactly the preceding N light files.

Reason:

- Seestar may reject some captured subs;
- source light count can therefore exceed stack count;
- the count reflects accepted stack members, not necessarily all captured source lights belonging to the observation.

The reconstruction model may retain/report:

- discovered light count;
- Seestar-reported stack count;
- any mismatch diagnostic.

A mismatch alone must not invalidate an otherwise coherent observation.

---

## 10. Missing-stack fallback

A source tree may contain compatible lights with no recognised Seestar stack.

Stage 7.1c must preserve these.

It may use conservative temporal/cadence analysis to suggest or construct a provisional lights-only observation when evidence is strong.

However:

- ambiguous gaps must remain visible;
- no interactive prompting belongs here;
- later Stage 7.1g may ask the user to resolve ambiguity;
- non-interactive orchestration later must be able to fail/report safely rather than silently guess.

The reconstruction model must therefore support an explicit status such as complete / lights-only / stack-only / ambiguous / unresolved, or an equivalent small design consistent with project style.

---

## 11. Orphan and edge cases

Stage 7.1c must handle at least:

### 11.1 Stack with no compatible preceding lights

The stack remains visible as a stack-only/orphan reconstruction result or diagnostic.

### 11.2 Lights after the final stack

They must not be assigned backwards to the final stack.

They remain lights-only/unresolved until a later boundary or fallback rule applies.

### 11.3 Incompatible lights before a stack

They must not be consumed by that stack.

They remain available for another compatible boundary or as unresolved/lights-only data.

### 11.4 Multiple stacks with no intervening lights

Both stack candidates remain visible. Do not silently collapse them.

### 11.5 Missing/malformed timestamps

Affected items remain visible and diagnostic.

### 11.6 Malformed discovery items

Per-file discovery problems created by Stage 7.1b must not be reinterpreted as valid observation members.

---

## 12. Determinism

Given the same discovery inventory, reconstruction output must be deterministic.

Do not rely on incidental list/set/dict ordering where the semantic ordering is chronological.

For equal timestamps, define a deterministic tie-breaker such as root-relative source path.

Tests must demonstrate stable behaviour.

---

## 13. Reconstruction model

Stage 7.1c should introduce the minimum clear immutable model required for logical reconstruction.

Conceptually it may include:

```text
ReconstructedObservation
ObservationReconstructionResult
ObservationStatus
ObservationProblem / diagnostic
```

Exact names should follow project conventions.

A reconstructed observation should not contain:

- final `observation_01` archive directory name;
- archive root;
- logical location;
- `session_end_date` destination path;
- copy/move decision;
- TIFF destination path;
- index-output path.

Those belong to Stage 7.1d+.

---

## 14. Observation numbering boundary

Stage 7.1c may return observations in deterministic chronological order.

It must not make final archive naming decisions such as:

```text
observation_01
observation_02
```

Those names belong to Stage 7.1d destination planning.

If an internal zero/one-based sequence index is useful for deterministic result handling, it must not be presented as the final archive directory contract.

---

## 15. No archive metadata/path planning

Stage 7.1c does not own:

- `session_end_date`;
- logical location resolution;
- target path-component normalisation;
- hierarchy token expansion;
- archive destination path;
- collision policy execution.

Do not start Stage 7.1d work.

---

## 16. No filesystem mutation

Stage 7.1c is read-only.

It must not:

- create directories;
- copy files;
- move files;
- delete files;
- rename files;
- generate TIFFs;
- generate `INDEX.md`;
- update source metadata.

---

## 17. API direction

Codex should inspect Stage 7.1b module/model conventions and extend them coherently.

A conceptual shape is:

```python
result = reconstruct_seestar_observations(inventory)
```

This name is illustrative, not mandatory.

The API must be:

- independent of argparse;
- independently testable;
- deterministic;
- suitable for later Stage 7.1d path planning.

Do not couple reconstruction to future CLI prompts.

---

## 18. Tests

Stage 7.1c requires focused automated tests.

At minimum, cover:

1. one light sequence plus one stack -> one observation;
2. multiple stack boundaries -> multiple observations;
3. lights before first recognised stack associate correctly;
4. lights after a stack do not associate backwards;
5. intentional merge behaviour with intermediate stacks absent;
6. presence of intermediate stacks prevents merge across those boundaries;
7. incompatible target evidence prevents association;
8. incompatible exposure prevents association;
9. incompatible filter prevents association;
10. stack count is not used as exact light-selection count;
11. discovered-light count may exceed Seestar stack count without invalidating grouping;
12. stack with no compatible lights remains visible;
13. lights with no stack remain visible;
14. missing-stack fallback is conservative;
15. ambiguous lights-only grouping is represented explicitly;
16. malformed/missing timestamps remain visible;
17. timestamp evidence is chronological and not filename-lexical only;
18. materially conflicting FITS/filename timestamps are reported;
19. equal timestamp tie-breaking is deterministic;
20. multiple stacks with no intervening lights remain distinct;
21. discovery `UNKNOWN` / JPEG items do not become observation members;
22. no archive path or observation-directory naming fields are introduced;
23. no filesystem mutation occurs;
24. Stage 7.1b discovery behaviour remains green;
25. Stage 2–6 tests remain green.

Use synthetic discovery inventories for algorithmic tests where appropriate.

Use existing real Seestar fixtures when useful to verify timestamp/metadata extraction, but do not turn this stage into broad Stage 8 qualification.

---

## 19. Documentation updates

Codex must update documentation as required to record the Stage 7.1c implementation accurately.

At minimum:

- preserve `docs/change_documents/STAGE_7/STAGE_7.1c.md` as the authoritative change document;
- update `docs/PROJECT_Notes.md` with Stage 7.1c current focus/progress;
- update `docs/ARCHITECTURE.md` where reconstruction API/model and timestamp authority need to be recorded;
- update user-facing documentation only if necessary to preserve the intentional merge contract clearly.

Do not mark Stage 7.1c complete before Stage-chat review.

Preserve the expected uncommitted `docs/CHANGELOG.md` entry for commit `610db0d`.

---

## 20. Explicit exclusions

Stage 7.1c must not implement:

- archive path construction;
- `session_end_date` destination planning;
- logical location resolution;
- saved-location matching;
- reverse geocoding;
- path-component sanitisation for archive destinations;
- copy/move/delete;
- compression;
- duplicate/collision execution;
- TIFF generation/orchestration;
- archive dry-run;
- archive CLI;
- `INDEX.md` generation;
- DSLR ingestion;
- broad Stage 8 real-dataset qualification;
- Stage 9 packaging/release work.

---

## 21. Validation requirements

Codex must run at least:

```text
pytest
ruff check .
git diff --check
```

Run formatting validation for changed Python files.

Explicitly confirm:

- Stage 7.1b discovery API/tests remain green;
- Stage 6 convert/convert-batch behaviour remains unchanged;
- no filesystem mutation is introduced;
- no Stage 7.1d work was started.

---

## 22. Closure criteria

Stage 7.1c is ready for Stage-chat review only when all of the following are satisfied:

1. A clear observation-reconstruction API exists.
2. The API consumes the Stage 7.1b discovery inventory rather than rescanning the filesystem.
3. The API identifies discovered light candidates for reconstruction.
4. The API identifies recognised Seestar stack candidates for boundaries.
5. JPEG and UNKNOWN discovery items are excluded from observation membership.
6. Reconstruction uses explicit capture-time evidence rather than filename lexical ordering alone.
7. Existing FITS timestamp evidence is reused where available.
8. No parallel independent FITS parser is introduced.
9. FITS/filename timestamp precedence is documented.
10. Material timestamp conflicts are visible as diagnostics/problems.
11. Missing timestamp evidence does not cause silent data loss.
12. Reconstruction output is deterministic.
13. Equal-time cases have a deterministic tie-breaker.
14. A recognised Seestar stacked FITS closes an observation.
15. Compatible preceding unassigned lights associate with that stack.
16. Post-stack lights are not assigned backwards to an already-closed observation.
17. Multiple recognised stacks reconstruct multiple logical observations.
18. Multiple stacks with no intervening lights remain separately visible.
19. Compatibility checks use target evidence where available.
20. Compatibility checks use exposure evidence where available.
21. Compatibility checks use filter evidence where available.
22. Other stable capture metadata may support compatibility without hidden heuristics.
23. Incompatible lights are not silently consumed by a stack.
24. Uncertain compatibility remains visible rather than guessed.
25. Stack count is not used as an exact preceding-light selector.
26. Discovered light count may exceed Seestar stack count without automatically invalidating the observation.
27. Stack count may be retained as supporting metadata/diagnostic evidence.
28. Intentional observation merging works when intermediate recognised stacks are absent and compatible lights precede the final stack.
29. Intermediate recognised stacks prevent merging across those boundaries.
30. Intentional merge execution does not modify source files.
31. Missing-stack lights remain visible.
32. Conservative missing-stack fallback exists where evidence is strong enough.
33. Ambiguous missing-stack grouping is represented explicitly.
34. No interactive prompting is implemented.
35. Stack-only/orphan stack cases remain visible.
36. Lights after the final stack remain visible.
37. Malformed/unusable timestamp cases remain visible.
38. Stage 7.1b per-file discovery problems are not treated as valid observation members.
39. Reconstruction returns logical observations/diagnostics suitable for Stage 7.1d.
40. Final archive directory names such as `observation_01` are not assigned here.
41. `session_end_date` destination planning is not implemented.
42. Logical location resolution is not implemented.
43. Archive hierarchy/path construction is not implemented.
44. Copy/move/delete is not implemented.
45. TIFF generation is not implemented.
46. Archive dry-run is not implemented.
47. Archive CLI is not implemented.
48. `INDEX.md` generation is not implemented.
49. DSLR ingestion is not implemented.
50. Reconstruction performs no filesystem mutation.
51. Focused Stage 7.1c tests cover primary stack-boundary behaviour.
52. Focused tests cover intentional merge behaviour.
53. Focused tests cover incompatibility and orphan/ambiguous cases.
54. Focused tests cover timestamp conflict/missing-time behaviour.
55. Stage 7.1b discovery tests remain green.
56. Existing Stage 2–6 tests remain green.
57. The full test suite passes.
58. Ruff lint passes.
59. Formatting validation for changed Python files passes.
60. `git diff --check` passes.
61. Stage 6 `convert` behaviour remains unchanged.
62. Stage 6 `convert-batch` remains flat and non-recursive.
63. Broad real-dataset qualification remains Stage 8.
64. Packaging/release remains Stage 9.
65. Documentation accurately records Stage 7.1c without prematurely marking it complete.
66. The expected uncommitted Stage 7.1b `docs/CHANGELOG.md` entry is preserved.
67. Codex has made no Git commit.
68. Stage 7.1d has not been started.

---

## 23. Codex completion report

Codex must return a concise completion report containing:

1. files changed;
2. production API/model/module summary;
3. the implemented timestamp authority/conflict rule;
4. the implemented compatibility rule;
5. test additions and what they prove;
6. validation commands and exact results;
7. explicit confirmation of closure criteria 1–68, or identification of any criterion not satisfied;
8. assumptions, uncertainties, and any contradictions discovered;
9. current `git status --short`;
10. confirmation that no Git commit was made;
11. confirmation that Stage 7.1d was not started.

Do **not** commit the changes.

The Stage chat will review the completion report against all closure criteria before Stage 7.1c can be marked COMPLETE and before a Git commit message is issued.
