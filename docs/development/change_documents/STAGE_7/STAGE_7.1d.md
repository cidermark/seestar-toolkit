# STAGE 7.1d — Archive metadata and destination path planning

## Status

**Stage:** 7.1d  
**Stage title:** Archive metadata and destination path planning  
**Starting commit:** `6e8590e` — `Stage 7.1c: reconstruct Seestar observations`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording the preceding Stage 7.1c commit may already be present in the working tree. It is expected and must not be treated as an unexpected dirty-tree condition.

---

## 1. Purpose

Stage 7.1d converts reconstructed logical observations from Stage 7.1c into deterministic, validated archive metadata and destination plans.

This stage is planning only.

It must answer:
- what target name is authoritative for archive placement;
- what logical location name applies;
- what `session_end_date` is;
- what configurable archive hierarchy applies;
- what observation directory name would be used;
- where original lights, Seestar stacks, and TIFF derivatives would ultimately go;
- what metadata must be carried forward to later archive execution and index generation.

It must **not** create directories, copy/move files, generate TIFFs, or modify the filesystem.

The primary boundary is:

> Stage 7.1d decides *where* archive products should go; Stage 7.1e decides *how* files are safely placed there.

---

## 2. Required outcome

After Stage 7.1d, the codebase must expose planning APIs/models that:

1. accept Stage 7.1c reconstruction results;
2. resolve/retain authoritative target metadata for each observation;
3. resolve the logical archive location from explicit/configured inputs;
4. calculate `session_end_date`;
5. normalize target/location path components safely;
6. expand a configurable hierarchy template;
7. assign deterministic archive observation directory names;
8. derive destination paths for lights, Seestar stack products, and future TIFF derivatives;
9. retain exact source metadata separately from normalized logical archive metadata;
10. expose problems/ambiguity without mutating the filesystem;
11. remain independent of argparse and future UI code.

The output becomes the input contract for Stage 7.1e safe archive file operations and Stage 7.1f TIFF orchestration.

---

## 3. Inputs

Stage 7.1d consumes reconstructed observation data from Stage 7.1c.

Conceptually:

```python
reconstruction = reconstruct_seestar_observations(inventory)
plan = plan_seestar_archive(...)
```

Exact API names are illustrative. Codex should follow existing project conventions.

Stage 7.1d must not rescan the source filesystem for discovery or reconstruct observations independently.

---

## 4. Archive metadata model

Planning should introduce the minimum immutable model needed to carry archive decisions forward.

Conceptually this may include:

```text
ArchivePlanningConfig
SavedLocation
ObservationArchiveMetadata
PlannedArchiveObservation
ArchivePlan
ArchivePlanningProblem
```

Exact names are not prescribed.

Each planned observation should retain, as appropriate:
- reference to the reconstructed observation;
- authoritative logical target;
- authoritative logical location;
- exact source GPS metadata where available;
- first light timestamp;
- last light timestamp;
- stack timestamp;
- session end date;
- planned hierarchy components;
- planned observation directory name;
- planned destination directory;
- planned light destination paths;
- planned Seestar stack FITS destination path;
- planned Seestar stack TIFF destination path;
- planned individual-light TIFF destination paths;
- relevant planning diagnostics.

No filesystem mutation occurs.

---

## 5. Session end date

The archive grouping rule fixed in Stage 7.1a is:

> `session_end_date = date(capture_datetime + 12 hours)`

This is archive grouping only.

Examples:

```text
2026-09-01 22:00 + 12h -> 2026-09-02
2026-09-02 01:30 + 12h -> 2026-09-02
2026-09-02 05:00 + 12h -> 2026-09-02
```

The formatted archive token is `YYYYMMDD`, for example `20260902`.

### 5.1 Timestamp source for session grouping

Use the best authoritative observation time already produced/retained by Stage 7.1c.

Preferred grouping evidence should normally be:
1. first-light capture time;
2. otherwise stack time for stack-only observations;
3. otherwise another documented authoritative reconstructed time;
4. unresolved if no safe observation time exists.

Do not modify FITS source timestamps.

Do not derive `session_end_date` from filesystem mtime.

---

## 6. Configurable hierarchy

The default archive hierarchy remains:

```text
{target}/{location}/{session_end_date}
```

Alternative user-configurable ordering must be supported, for example:

```text
{location}/{session_end_date}/{target}
```

Stage 7.1d must implement a reusable hierarchy-template contract suitable for future CLI and UI use.

Required supported tokens for Stage 7:
- `{target}`
- `{location}`
- `{session_end_date}`

Unknown/unrecognised tokens must produce a clear planning/configuration error.

The hierarchy template must not permit absolute-path escape or traversal outside the supplied archive root.

---

## 7. Configuration representation

Stage 7.1a preferred TOML for persistent configuration.

Stage 7.1d should implement the **configuration model/contract** needed for planning, but avoid broad user-facing configuration-management work.

At minimum, support configuration data for:
- archive root;
- hierarchy template;
- saved locations;
- saved-location matching radius.

If a small TOML loader/writer is necessary and naturally belongs here, keep it minimal and well tested.

Do not implement interactive configuration UI.

Do not implement Stage 7.1g prompting.

---

## 8. Target resolution

Stage 7.1b/7.1c retain target evidence from FITS metadata and directory/source context.

Stage 7.1d must resolve the logical target used in the archive hierarchy.

### 8.1 Precedence

Use the strongest existing authoritative target evidence.

A reasonable precedence is:
1. trusted FITS target metadata;
2. existing reconstructed/discovery target candidate derived from trusted evidence;
3. directory-derived target evidence;
4. unresolved/unknown.

If the existing Stage 7.1b target contract already defines stronger precedence, reuse it rather than duplicating a second target-resolution policy.

### 8.2 Conflict handling

Conflicting target evidence must remain visible as a planning diagnostic.

Do not silently rewrite one target into another without preserving the conflict.

### 8.3 Unknown target

If no safe target can be resolved, use a clear explicit logical fallback such as `unknown`, or preserve an unresolved state if that better fits current project conventions.

The behavior must be deterministic and documented.

---

## 9. Path-component normalization

Target and location values used as directory components must be normalized safely and deterministically.

Required policy from Stage 7.1a:
- trim leading/trailing whitespace;
- collapse repeated internal whitespace to one;
- preserve ordinary spaces;
- preserve case;
- do not convert spaces to underscores;
- neutralize `/` and other unsafe path characters deterministically;
- prevent `.` and `..`;
- prevent absolute path injection;
- prevent path traversal.

Normalization must not destroy the original logical/source value stored in metadata.

Examples should include:
- `IC 434`
- `Warfield`
- `  IC   434`
- `Target/Name`
- `..`
- `/absolute/path`

The implementation should use one reusable path-component normalizer rather than ad hoc sanitization at each call site.

---

## 10. Location resolution

Stage 7.1a fixed the location precedence as:
1. explicit CLI/user location wins;
2. match FITS GPS to saved configured locations;
3. optional reverse-geocoded suggestion;
4. interactive manual entry;
5. `unknown`.

Stage 7.1d implements only the **non-interactive planning portion** of this policy.

### 10.1 Explicit logical location

Planning API should accept an explicit logical location value.

If supplied, it wins.

### 10.2 Saved-location GPS matching

Where no explicit location is supplied and usable GPS coordinates are available, Stage 7.1d should support matching against configured saved locations.

Each saved location should contain at least:
- name;
- latitude;
- longitude;
- matching radius.

If multiple saved locations match, the nearest match wins.

The result must be deterministic.

### 10.3 Exact GPS preservation

Exact source GPS coordinates must remain separately available from the logical matched location name.

Do not replace precise source metadata with the logical place name.

### 10.4 Reverse geocoding

Do **not** hard-wire any external geocoding provider.

Network reverse-geocoding belongs to later orchestration/UI work.

If no explicit or saved location resolves, use `unknown` for non-interactive planning.

---

## 11. Saved-location distance calculation

GPS matching should use a reasonable geographic distance calculation.

Requirements:
- deterministic;
- unit clearly defined;
- matching radius interpreted consistently;
- nearest matching location wins;
- exact boundary behavior tested;
- invalid latitude/longitude values rejected cleanly.

Do not over-engineer provider-specific geospatial infrastructure.

A small haversine implementation or equivalent is acceptable.

---

## 12. Observation directory naming

The canonical Stage 7 archive structure uses:

```text
observation_01
observation_02
...
```

Stage 7.1d is the stage where final planned observation directory naming becomes valid.

Rules:
- numbering is deterministic within one `{target}/{location}/{session_end_date}` grouping;
- numbering starts at `01`;
- chronological order from reconstruction should drive numbering;
- equal-time ties use the deterministic ordering inherited from Stage 7.1c;
- if more than 99 observations exist, naming must remain unambiguous rather than truncating/colliding.

Always use `observation_01` even when only one observation exists.

Observation numbering is archive planning metadata only; Stage 7.1d still does not create the directory.

---

## 13. Canonical destination structure

For each planned observation:

```text
ARCHIVE_ROOT/
└── <hierarchy base>/
    └── observation_01/
        ├── lights/
        ├── seestar_stacked/
        └── tiff/
```

Default hierarchy base:

```text
{target}/{location}/{session_end_date}
```

The exact order follows the configured hierarchy template.

---

## 14. Planned light destinations

Original individual light FIT/FITS files are planned directly under:

```text
observation_NN/lights/
```

Original filenames must be preserved.

Do not rename original FITS files.

---

## 15. Planned individual-light TIFF destinations

Each light FIT/FITS should have a corresponding planned TIFF derivative under:

```text
observation_NN/tiff/
```

The basename is preserved and extension becomes `.tiff`.

Stage 7.1d plans the path only.

It must not call the TIFF conversion pipeline.

---

## 16. Planned Seestar stack destinations

If the observation has a Seestar stack FIT/FITS:

Original stack FITS destination:

```text
observation_NN/seestar_stacked/<original filename>
```

Corresponding TIFF derivative:

```text
observation_NN/seestar_stacked/<same basename>.tiff
```

Stage 7.1d performs no TIFF generation.

---

## 17. Stack-only and lights-only observations

### 17.1 Stack-only
A stack-only reconstructed observation can still receive a planned observation directory and stack destinations if target/location/date metadata can be resolved safely.

### 17.2 Lights-only
A lights-only reconstructed observation can receive planned light/TIFF destinations where metadata is sufficient.

### 17.3 Ambiguous/unresolved
Ambiguous/unresolved reconstructed observations must not be silently turned into authoritative archive placement if essential target/time grouping is unsafe.

The planning result should retain an explicit problem/status so later CLI/orchestration can require user resolution.

---

## 18. Duplicate/collision boundary

Stage 7.1d may detect or represent that two planned outputs target the same destination path.

However it must not execute collision policy.

Actual filesystem/content comparison and safe action belong to Stage 7.1e.

Stage 7.1d may raise a planning-level collision if two distinct source items within the same in-memory plan deterministically map to the same path.

Do not compute SHA-256 solely for execution policy here unless existing data already contains it and it is necessary to detect an internal planning conflict.

---

## 19. Archive root safety

All planned destinations must remain under the supplied archive root.

Required protections:
- no absolute token expansion;
- no `..` traversal;
- no normalized component may escape the root;
- final resolved/planned paths must be safely rooted.

Tests must explicitly cover malicious/unsafe template/component values.

---

## 20. Plan determinism

Given the same reconstruction result, archive root, hierarchy template, saved-location configuration, and explicit location inputs, the archive plan must be deterministic.

No reliance on ambient current working directory, locale-dependent sorting, filesystem enumeration order, or network services.

---

## 21. INDEX.md boundary

Stage 7.1d may retain metadata that Stage 7.1h will later use to generate target-level `INDEX.md`.

It must not generate or write `INDEX.md`.

Useful retained values may include target, location, session end date, telescope identifier, first/last light, exposure, filter, light count, stack filename, stack count, capture mode, and exact GPS.

---

## 22. Telescope identifier

Where available in existing FITS/reconstruction metadata, preserve the actual Seestar telescope identifier such as `S50_99643794`.

Do not replace it with generic `ZWO Seestar S50`.

If unavailable, preserve `unknown` or equivalent explicit absence.

---

## 23. JPEG policy boundary

Stage 7.1d must not attach, relocate, or delete JPEG/thumbnail items.

Default JPEG source behavior remains `ignore`.

Deletion is not permitted.

---

## 24. Future DSLR boundary

The archive planning model should remain source-format-neutral where practical.

However Stage 7.1d must not implement DSLR ingestion, EXIF reading, or DSLR-specific path logic.

---

## 25. API direction

Codex should extend the existing `seestar_toolkit.archive` package coherently.

A conceptual API shape is:

```python
plan = plan_seestar_archive(
    reconstruction,
    archive_root=...,
    hierarchy_template="{target}/{location}/{session_end_date}",
    explicit_location=...,
    saved_locations=...,
)
```

Exact names/signatures are illustrative.

The API must be independent of argparse, independently unit-testable, deterministic, read-only, and suitable for Stage 7.1e execution.

---

## 26. Error model

Reuse the project's existing exception architecture.

Introduce only the minimum archive-planning-specific exception(s) required.

Distinguish:
- invalid planning configuration;
- invalid archive root/template values;
- observation-level unresolved metadata;
- internal planning destination collision.

Do not mask programming errors with broad catch-all handling.

---

## 27. Tests

Stage 7.1d requires focused automated tests.

At minimum cover:
1. default hierarchy expansion;
2. alternative hierarchy ordering;
3. supported hierarchy tokens;
4. unknown hierarchy token rejection;
5. target path normalization;
6. location path normalization;
7. repeated whitespace collapse;
8. preservation of ordinary spaces and case;
9. slash/unsafe-character neutralization;
10. `.` and `..` protection;
11. absolute path/traversal protection;
12. final planned path remains beneath archive root;
13. `session_end_date` before midnight;
14. `session_end_date` after midnight;
15. `session_end_date` around the +12-hour grouping boundary;
16. no filesystem mtime used for session grouping;
17. explicit location wins;
18. saved GPS location match;
19. nearest overlapping saved-location match wins;
20. exact radius boundary behavior;
21. no match -> `unknown`;
22. exact GPS retained separately from logical location;
23. invalid saved-location coordinates rejected;
24. one observation -> `observation_01`;
25. multiple observations -> deterministic numbering;
26. numbering remains unambiguous above 99;
27. original light FITS filenames preserved;
28. light TIFF derivative changes only extension to `.tiff`;
29. stack FITS planned under `seestar_stacked/`;
30. stack TIFF planned beside stack FITS;
31. lights-only observation planning;
32. stack-only observation planning;
33. ambiguous/unresolved essential metadata not silently treated as authoritative;
34. two distinct planned sources mapping to same destination are detected;
35. no copy/move/delete occurs;
36. no TIFF generation occurs;
37. no directory creation occurs;
38. no `INDEX.md` generation occurs;
39. Stage 7.1c reconstruction tests remain green;
40. Stage 7.1b discovery tests remain green;
41. Stage 2–6 tests remain green.

Synthetic reconstruction models are preferred for focused planning tests.

Use real fixtures only where useful to verify metadata handoff, without expanding into Stage 8 broad qualification.

---

## 28. Documentation updates

Codex must update documentation as needed to record the Stage 7.1d implementation accurately.

At minimum:
- preserve `docs/change_documents/STAGE_7/STAGE_7.1d.md` as the authoritative specification;
- update `docs/PROJECT_Notes.md` with Stage 7.1d current focus/progress;
- update `docs/ARCHITECTURE.md` with the implemented planning/configuration contracts;
- preserve the intentional pending `docs/CHANGELOG.md` entry for commit `6e8590e`.

Do not mark Stage 7.1d complete before Stage-chat review.

---

## 29. Explicit exclusions

Stage 7.1d must not implement:
- filesystem directory creation;
- copy;
- move;
- delete;
- rename;
- compression;
- SHA-256 duplicate execution policy;
- overwrite/skip/cancel execution;
- TIFF generation;
- integrated archive orchestration;
- dry-run execution;
- archive CLI;
- interactive location prompts;
- reverse-geocoder provider calls;
- `INDEX.md` generation;
- DSLR ingestion;
- Stage 8 broad qualification;
- Stage 9 packaging/release.

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
- Stage 7.1c reconstruction API/tests remain green;
- Stage 7.1b discovery API/tests remain green;
- Stage 6 `convert` behavior is unchanged;
- Stage 6 `convert-batch` remains flat and non-recursive;
- no filesystem mutation occurs;
- no TIFF generation occurs;
- Stage 7.1e was not started.

---

## 31. Closure criteria

Stage 7.1d is ready for Stage-chat review only when all criteria below are satisfied.

1. A clear archive-planning API exists.
2. The API consumes Stage 7.1c reconstruction output.
3. The API does not independently rescan source discovery directories.
4. A typed immutable archive-planning model exists.
5. The plan retains reference/evidence from the reconstructed observation.
6. Logical target metadata is resolved deterministically.
7. Stronger existing FITS/reconstruction target evidence is preferred over weaker directory evidence.
8. Target conflicts remain visible diagnostically.
9. Unknown/unresolved target handling is explicit and deterministic.
10. Exact source metadata remains separate from normalized archive path components.
11. `session_end_date` uses the `capture_datetime + 12 hours` rule.
12. `session_end_date` is formatted consistently for hierarchy expansion.
13. Filesystem mtime is not used for session grouping.
14. First-light time is preferred for normal observations where available.
15. Stack time can support stack-only observation grouping.
16. Missing safe observation time remains visible rather than guessed.
17. Default hierarchy `{target}/{location}/{session_end_date}` is supported.
18. Alternative token ordering is supported.
19. `{target}`, `{location}`, and `{session_end_date}` are supported tokens.
20. Unknown hierarchy tokens produce a clear configuration/planning error.
21. Hierarchy expansion cannot produce an absolute escape from archive root.
22. Hierarchy expansion cannot traverse outside archive root.
23. Target normalization trims outer whitespace.
24. Target normalization collapses repeated internal whitespace.
25. Target normalization preserves ordinary spaces.
26. Target normalization preserves case.
27. Target normalization does not convert spaces to underscores.
28. Unsafe `/` or equivalent path separators are neutralized deterministically.
29. `.` and `..` are neutralized/rejected safely.
30. Absolute path injection is prevented.
31. Location normalization follows the same safe path-component contract.
32. Original logical target/location values remain available separately.
33. Explicit logical location input wins.
34. GPS matching against saved configured locations is supported.
35. Each saved location has name, latitude, longitude, and radius.
36. Nearest matching location wins when match radii overlap.
37. Saved-location matching is deterministic.
38. Exact GPS remains preserved separately from logical location.
39. Invalid saved-location coordinates/radii are rejected cleanly.
40. No reverse-geocoding provider is hard-wired.
41. No network access is required for planning.
42. No resolved location falls back silently to a guessed place.
43. Non-interactive no-match location becomes `unknown` or equivalent explicit fallback.
44. One observation receives planned directory name `observation_01`.
45. Multiple observations are numbered deterministically.
46. Observation numbering is scoped to one target/location/session grouping.
47. Numbering remains unambiguous above 99 observations.
48. Final archive observation directory naming is introduced here, not earlier reconstruction.
49. Planned `lights/` directory exists in the model/path plan.
50. Planned `seestar_stacked/` directory exists in the model/path plan.
51. Planned `tiff/` directory exists in the model/path plan.
52. Original light FITS filenames are preserved in planned destinations.
53. Light TIFF derivative preserves basename and uses `.tiff`.
54. Original stack FITS filename is preserved under `seestar_stacked/`.
55. Stack TIFF derivative is planned beside the stack FITS with `.tiff`.
56. Stage 7.1d plans TIFF destinations but does not generate TIFFs.
57. Lights-only reconstructed observations can be represented in the plan.
58. Stack-only reconstructed observations can be represented in the plan.
59. Ambiguous/unresolved essential metadata does not silently become authoritative placement.
60. Planning diagnostics/problems are exposed to callers.
61. Distinct in-memory sources that map to the same planned destination are detected as a planning conflict.
62. Filesystem content collision execution remains deferred to Stage 7.1e.
63. No SHA-256 overwrite/skip/cancel execution policy is implemented here.
64. All planned destinations remain beneath the archive root.
65. The plan is deterministic for identical inputs/configuration.
66. The plan does not depend on current working directory.
67. The plan does not depend on filesystem iteration order.
68. The plan does not depend on network services.
69. Telescope identifier is preserved where already available.
70. Missing telescope identifier remains explicit rather than replaced with a generic device name.
71. Metadata needed later for `INDEX.md` can be retained.
72. `INDEX.md` is not generated.
73. JPEGs are not deleted.
74. JPEG archive placement is not introduced unexpectedly.
75. DSLR ingestion is not implemented.
76. The planning API is independent of argparse.
77. No interactive prompting is implemented.
78. No filesystem directories are created.
79. No files are copied.
80. No files are moved.
81. No files are deleted.
82. No files are renamed.
83. No compression is performed.
84. Stage 7.1c reconstruction tests remain green.
85. Stage 7.1b discovery tests remain green.
86. Existing Stage 2–6 tests remain green.
87. Focused Stage 7.1d tests cover hierarchy/path safety.
88. Focused tests cover session-date grouping.
89. Focused tests cover location resolution.
90. Focused tests cover observation numbering.
91. Focused tests cover planned FITS/TIFF destinations.
92. Focused tests cover unresolved/conflict cases.
93. Full test suite passes.
94. Ruff lint passes.
95. Formatting validation for changed Python files passes.
96. `git diff --check` passes.
97. Stage 6 `convert` remains unchanged.
98. Stage 6 `convert-batch` remains flat and non-recursive.
99. Broad real-dataset qualification remains Stage 8.
100. Packaging/release remains Stage 9.
101. Documentation records Stage 7.1d accurately without prematurely marking it complete.
102. Expected pending `docs/CHANGELOG.md` entry for Stage 7.1c is preserved.
103. Codex makes no Git commit.
104. Stage 7.1e is not started.

---

## 32. Codex completion report

Codex must return a concise completion report containing:
1. files changed;
2. production API/model/configuration summary;
3. implemented target-resolution rule;
4. implemented session-end-date rule;
5. implemented hierarchy/path-normalization rule;
6. implemented location-resolution and GPS-matching rule;
7. implemented observation-numbering rule;
8. planned source/TIFF destination behavior;
9. test additions and what they prove;
10. validation commands and exact results;
11. explicit confirmation of closure criteria 1–104, or identification of any criterion not satisfied;
12. assumptions, uncertainties, and contradictions discovered;
13. current `git status --short`;
14. confirmation that no Git commit was made;
15. confirmation that Stage 7.1e was not started.

Do **not** commit the changes.

The Stage chat will audit the completion report against all closure criteria before Stage 7.1d can be marked COMPLETE and before a Git commit message is issued.
