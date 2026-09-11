# STAGE 7.1b — Implement Seestar input discovery and classification

## Status

**Stage:** 7.1b  
**Stage title:** Implement Seestar input discovery and classification  
**Starting commit:** `22c588a` — `Stage 7.1a: define archive architecture and policies`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording the preceding Stage 7.1a commit may already be present in the working tree. It is expected and must not be treated as an unexpected dirty-tree condition.

---

## 1. Purpose

Stage 7.1b implements the first production-code portion of Stage 7.

Given a Seestar parent work directory, normally `My Works`, the Toolkit must discover relevant files in the known shallow Seestar source structure and return a deterministic, typed inventory that later Stage 7 code can consume.

The central boundary is:

> Stage 7.1b discovers and classifies source files. It does not reconstruct observations.

Observation reconstruction, light-to-stack association, stack-boundary handling, and intentional observation merging belong to Stage 7.1c.

Stage 7.1b must be read and implemented in conjunction with the Stage 7 architecture and policy contract established by `STAGE_7.1a.md`, `docs/ARCHITECTURE.md`, and `docs/PROJECT_Notes.md`.

---

## 2. Required outcome

After Stage 7.1b, the codebase must expose a clear archive-discovery API capable of:

1. accepting a Seestar work-root path;
2. validating the root sufficiently for safe discovery;
3. scanning the supported shallow Seestar source structure;
4. identifying candidate source files;
5. classifying candidates into Stage 7 discovery categories;
6. retaining source path and useful discovery/context evidence;
7. reporting malformed/unreadable/unsupported candidates safely;
8. returning results in deterministic order;
9. performing no filesystem mutation;
10. making no observation-grouping decisions.

The resulting inventory is the input contract for Stage 7.1c.

---

## 3. Input-root contract

### 3.1 Normal root

The normal input is the Seestar parent work directory:

```text
My Works/
```

Representative structure:

```text
My Works/
├── IC 434/
│   ├── Stacked_195_IC 434_10.0s_LP_20260103-225603_thn.jpg
│   ├── Stacked_195_IC 434_10.0s_LP_20260103-225603.fit
│   └── Stacked_195_IC 434_10.0s_LP_20260103-225603.jpg
└── IC 434_sub/
    ├── Light_IC 434_10.0s_LP_20260103-220259_thn.jpg
    ├── Light_IC 434_10.0s_LP_20260103-220259.fit
    ├── Light_IC 434_10.0s_LP_20260103-220259.jpg
    └── ...
```

The Seestar may reuse the same target/product and target-sub directories across multiple dates and observations.

Therefore directory membership is discovery context only and must never be treated as proof that all contained files form one observation.

### 3.2 Supported traversal

Stage 7.1b may deliberately understand the known shallow Seestar structure beneath the supplied work root.

This is Stage 7 archive discovery and is independent of the completed Stage 6 batch-conversion contract.

Stage 7.1b must not alter `convert-batch`, make it recursive, or reuse archive discovery to silently change its semantics.

### 3.3 Root validation

The discovery API must reject an input root that does not exist or is not a directory with a clear domain-appropriate error.

An existing empty directory is valid input and should produce an empty inventory rather than an exception merely because no supported source files exist.

The API must accept normal project path conventions (`str` and/or `Path`) consistently with existing project style.

---

## 4. Discovery classifications

The discovery layer must distinguish at least the following conceptual categories:

```text
LIGHT_FITS
SEESTAR_STACK_FITS
SEESTAR_JPEG
THUMBNAIL_JPEG
UNKNOWN
```

Names may follow existing project enum/model naming conventions, but their meanings must remain explicit.

### 4.1 `LIGHT_FITS`

An individual astronomical light sub-exposure suitable for later observation reconstruction.

### 4.2 `SEESTAR_STACK_FITS`

A Seestar-generated stacked FIT/FITS product.

This classification is particularly important because Stage 7.1c will use recognised Seestar stack files as primary observation-end markers.

Stage 7.1b must classify them but must not yet associate lights with them.

### 4.3 `SEESTAR_JPEG`

A normal Seestar-generated JPEG associated with a capture/product.

Stage 7.1a defines the safe default archive JPEG policy as `ignore`; Stage 7.1b only identifies the file type and does not apply destructive policy.

### 4.4 `THUMBNAIL_JPEG`

A Seestar thumbnail JPEG, normally evidenced by the `_thn.jpg` naming convention.

It must remain distinguishable from the full-size Seestar JPEG.

### 4.5 `UNKNOWN`

A discovered item that does not safely classify as one of the supported categories.

Unknown files must not be silently promoted to valid astronomical source data.

---

## 5. FIT/FITS extension handling

The project supports FIT/FITS input.

Discovery must handle supported FITS extensions consistently with existing project conventions, including case handling where appropriate.

Do not introduce an extension rule that contradicts the existing FITS/conversion subsystem.

---

## 6. Classification evidence

### 6.1 Principle

Classification must not depend solely on exact Seestar filenames.

Firmware or app changes may alter naming conventions.

The intended evidence model is:

```text
FITS inspection/classification
        +
directory context
        +
filename evidence
        ->
discovery classification
```

### 6.2 FITS evidence

For FIT/FITS candidates, reuse the existing Stage 2 FITS reader/inspection/classification subsystem wherever practical.

Do not introduce a second independent FITS parser or duplicate established image classification logic.

Existing FITS metadata/image classification should provide authoritative or strong evidence where it can do so.

### 6.3 Filename evidence

Current known filename evidence includes patterns such as:

```text
Light_*.fit
Stacked_*.fit
*_thn.jpg
*.jpg
```

These patterns are useful evidence but are not a substitute for FITS inspection when stronger evidence is available.

### 6.4 Directory context

Known directory context includes patterns such as:

```text
<target>/
<target>_sub/
```

The product directory and sub directory may help infer candidate role and target context.

Directory naming is supporting context rather than proof of observation membership.

### 6.5 Conflicting evidence

If filename, directory context, and FITS inspection materially disagree, Stage 7.1b must not silently invent certainty.

The discovery result should either:

- classify using a clearly documented evidence precedence when the stronger evidence is sufficient; or
- preserve/report the ambiguity/error in a form later code can handle safely.

Codex should prefer a small explicit model over hidden heuristics.

---

## 7. Discovery item model

Stage 7.1b should introduce the minimum clear model required to represent one discovered source item.

The exact Python names and module placement should follow the existing package architecture, but a discovered item should retain at least:

- source path;
- discovery classification;
- source-directory context;
- candidate target/context name where determinable;
- sufficient FITS inspection/classification evidence or reference data for later stages;
- discovery problem/error information when a candidate could not be safely inspected/classified.

Do not overload the discovery item with Stage 7.1c+ decisions such as:

- observation number;
- associated stack;
- session end date;
- logical archive location;
- destination archive path;
- copy/move decision;
- generated TIFF destination.

Those belong to later stages.

### 7.1 Target context

It is acceptable for discovery to retain a target candidate derived from the source directory and/or FITS metadata.

Where multiple sources disagree, do not silently rewrite authoritative metadata merely to match the directory name.

The precise normalised archive target belongs to Stage 7.1d.

### 7.2 Timestamps

If existing FITS inspection naturally exposes capture timestamps needed by later code, discovery may retain that evidence.

Stage 7.1b must not use timestamps to group observations.

---

## 8. Discovery result model

The public/internal API should return a deterministic inventory rather than exposing an unordered filesystem traversal.

The result may be a sequence of discovery items or a small result object containing items and diagnostics, according to existing project style.

The API should make it straightforward for Stage 7.1c to obtain all discovered light and stack candidates without rescanning the filesystem.

---

## 9. Deterministic ordering

Given the same unchanged input tree, discovery output order must be deterministic.

Do not rely on raw filesystem iteration order.

A stable path-based ordering is acceptable for Stage 7.1b.

Chronological observation ordering is not required here and belongs to Stage 7.1c.

Tests must prove deterministic output independently of filesystem enumeration order where practical.

---

## 10. JPEG handling boundary

Stage 7.1b classifies JPEGs but does not archive, copy, delete, or ignore them operationally.

The Stage 7.1a policy remains:

```text
default JPEG policy = ignore
```

`ignore` means later archive execution leaves the source JPEG untouched.

Do not delete JPEGs during discovery.

---

## 11. Malformed, unreadable and unsupported candidates

Discovery must be robust against individual problematic files.

Examples include:

- malformed FIT/FITS;
- unreadable FIT/FITS;
- unsupported FITS image content;
- misleading FITS filename;
- unrelated file;
- unsupported extension.

A single bad candidate should not normally crash discovery of the entire work root.

The problem should be represented or reported clearly enough that later CLI/orchestration can explain it.

However, root-level failures such as nonexistent/non-directory input are API-level errors and should fail the discovery request clearly.

Do not suppress unexpected programming errors under a broad catch-all that makes defects invisible.

---

## 12. Mosaic compatibility

The exact real Seestar mosaic source-directory naming convention is not yet confirmed.

A likely convention such as:

```text
<target>_mosaic_sub
```

must not be hard-coded as authoritative merely from memory.

Stage 7.1b should be structured so an additional recognised source-directory convention can be added without redesigning the discovery API/model.

Existing real mosaic FITS fixtures may be used to validate that FITS inspection/classification remains compatible with mosaic-produced files.

Do not turn this stage into broad mosaic dataset qualification.

---

## 13. No observation reconstruction

This boundary must be explicit in both implementation and tests.

Stage 7.1b must not:

- assign `observation_01`, `observation_02`, etc.;
- associate a light with a particular stack;
- use stack timestamps as grouping boundaries;
- use temporal gaps to split observations;
- use stack counts to select preceding lights;
- implement intentional observation merging;
- resolve missing-stack grouping.

Those responsibilities begin in Stage 7.1c.

A source tree containing multiple stack candidates should therefore return multiple classified stack items, not multiple reconstructed observation objects.

---

## 14. No filesystem mutation

Discovery is read-only.

Stage 7.1b must not:

- create archive directories;
- copy source files;
- move source files;
- rename source files;
- delete source files;
- generate TIFF files;
- generate `INDEX.md`;
- modify source metadata.

Tests should confirm the source tree is unchanged by discovery where practical.

---

## 15. Proposed API direction

Codex should first inspect existing project module/API conventions and choose names consistent with them.

A conceptual shape is:

```python
inventory = discover_seestar_inputs(root)
```

with a deterministic sequence/result containing typed discovery items.

This name is illustrative, not mandatory.

Prefer a narrow, testable API over coupling discovery directly to argparse/CLI output.

The discovery layer must be callable independently of the future Stage 7.1g archive CLI.

---

## 16. Error model

Use the project's existing exception architecture where suitable.

If a Stage 7 archive/discovery-specific exception hierarchy is needed, introduce only the minimum foundation required for 7.1b.

Errors should distinguish root/request failure from per-file discovery problems where practical.

Do not prematurely define a large exception taxonomy for later Stage 7 stages.

---

## 17. Tests

Stage 7.1b requires focused automated tests.

At minimum, cover:

1. valid work-root discovery;
2. `LIGHT_FITS` classification;
3. `SEESTAR_STACK_FITS` classification;
4. full-size `SEESTAR_JPEG` classification;
5. `THUMBNAIL_JPEG` classification;
6. unknown/unrelated file handling;
7. deterministic result ordering;
8. existing empty directory returns empty inventory;
9. nonexistent root fails clearly;
10. file path supplied as root fails clearly;
11. malformed/unreadable FITS candidate is reported safely without losing other valid discoveries;
12. supported FIT/FITS extension handling;
13. target/product versus `_sub` directory context is retained appropriately;
14. multiple stack files remain separate discovery items and are not converted into observations;
15. discovery performs no filesystem mutation;
16. Stage 6 conversion/batch behaviour remains unchanged.

Use synthetic fixtures for structural/discovery cases where sufficient.

Use existing real FITS fixtures where they add meaningful confidence and do not broaden this stage into Stage 8 qualification.

Do not create tests for Stage 7.1c algorithms.

---

## 18. Documentation updates

Codex must update documentation as required to record Stage 7.1b implementation accurately.

At minimum:

- preserve `docs/change_documents/STAGE_7/STAGE_7.1b.md` as the authoritative change document;
- update `docs/PROJECT_Notes.md` with Stage 7.1b current focus/progress as appropriate;
- update `docs/ARCHITECTURE.md` only where actual discovery API/module design needs to be recorded;
- update other documentation only when needed for consistency.

Do not mark Stage 7.1b complete before Stage-chat review.

The existing uncommitted `docs/CHANGELOG.md` entry for commit `22c588a` is expected and should be preserved. Do not invent the Stage 7.1b commit ID before the user commits.

---

## 19. Explicit exclusions

Stage 7.1b must not implement:

- observation reconstruction;
- stack-to-light association;
- intentional observation merge execution;
- missing-stack grouping;
- `session_end_date` calculation for archive placement;
- logical location resolution;
- saved-location matching;
- reverse geocoding;
- archive path construction;
- target/location filesystem normalisation implementation beyond anything minimally needed for discovery context;
- copy/move/delete;
- compression;
- duplicate/collision execution;
- TIFF generation/orchestration;
- archive dry-run;
- archive CLI;
- `INDEX.md` generation;
- DSLR ingestion;
- Stage 8 broad real-dataset qualification;
- Stage 9 packaging/release work.

---

## 20. Validation requirements

Codex must run at least:

```text
pytest
ruff check .
git diff --check
```

Run the repository's appropriate formatting check for changed Python files.

If repository-wide formatting has known pre-existing differences, report them accurately rather than modifying unrelated historical files.

Confirm explicitly that Stage 6 source/API/CLI semantics were not altered.

---

## 21. Closure criteria

Stage 7.1b is ready for Stage-chat review only when all of the following are satisfied:

1. A clear Stage 7 Seestar discovery API exists.
2. The API accepts the intended `My Works`-style parent root.
3. Nonexistent roots fail with a clear domain-appropriate error.
4. Non-directory roots fail with a clear domain-appropriate error.
5. Existing empty roots return an empty deterministic inventory.
6. Discovery understands only the required shallow Stage 7 Seestar input scope and does not alter Stage 6 batch semantics.
7. A typed discovery-item model exists.
8. Discovery distinguishes individual light FIT/FITS files.
9. Discovery distinguishes Seestar stacked FIT/FITS files.
10. Discovery distinguishes full-size Seestar JPEGs.
11. Discovery distinguishes Seestar thumbnail JPEGs.
12. Unknown/unrelated candidates are handled safely.
13. FIT/FITS candidate classification reuses existing Stage 2 inspection/classification logic where practical.
14. No second independent FITS parser/classification subsystem has been introduced.
15. Filename evidence is not the sole authority for FITS classification.
16. Directory context is treated as supporting evidence rather than observation membership.
17. Target/source-directory context needed by later stages is retained where determinable.
18. Conflicting evidence is handled by explicit precedence or preserved/reported ambiguity rather than silent guessing.
19. Malformed/unreadable FITS candidates do not normally prevent discovery of other valid candidates.
20. Per-file discovery problems remain visible to later callers.
21. Discovery results are deterministic for an unchanged input tree.
22. Discovery does not depend on raw filesystem iteration order.
23. Multiple stack candidates remain individual discovery items.
24. No observation numbers are assigned.
25. No light-to-stack association occurs.
26. No stack-boundary grouping occurs.
27. No stack-count grouping occurs.
28. No intentional observation-merge execution occurs.
29. No missing-stack observation reconstruction occurs.
30. Discovery performs no filesystem mutation.
31. JPEG files are not deleted or otherwise mutated.
32. No TIFF files are generated.
33. No archive destination directories or paths are operationally created.
34. The unconfirmed mosaic-directory convention is not hard-coded as authoritative.
35. The design permits later addition of confirmed mosaic source-directory conventions without redesigning the discovery model.
36. The discovery API is independent of argparse/future archive CLI presentation.
37. Stage 6 `convert` behaviour remains unchanged.
38. Stage 6 `convert-batch` remains flat and non-recursive.
39. DSLR ingestion has not been implemented.
40. Broad real-dataset qualification remains Stage 8.
41. Packaging/release remains Stage 9.
42. Focused Stage 7.1b tests cover the required discovery/classification behaviours.
43. Existing Stage 2–6 tests remain green.
44. The full test suite passes.
45. Ruff lint passes.
46. Formatting validation for changed Python files passes.
47. `git diff --check` passes.
48. Project documentation accurately records the Stage 7.1b implementation without prematurely marking it complete.
49. The expected uncommitted Stage 7.1a `docs/CHANGELOG.md` entry is preserved appropriately.
50. Codex has made no Git commit.
51. Stage 7.1c has not been started.

---

## 22. Codex completion report

Codex must return a concise completion report containing:

1. files changed;
2. production API/model/module summary;
3. test additions and what they prove;
4. validation commands and exact results;
5. explicit confirmation of closure criteria 1–51, or identification of any criterion not satisfied;
6. assumptions, uncertainties, and any contradictions discovered;
7. current `git status --short`;
8. confirmation that no Git commit was made;
9. confirmation that Stage 7.1c was not started.

Do **not** commit the changes.

The Stage chat will review the report against all closure criteria before Stage 7.1b can be marked COMPLETE and before a Git commit message is issued.
