# STAGE 7.1h — Generate human-readable target indexes

## Status
**Stage:** 7.1h  
**Stage title:** Generate human-readable target indexes  
**Starting commit:** `f8f07e5` — `Stage 7.1g: add archive CLI and dry-run`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording Stage 7.1g may already be present. It is expected and must be preserved.

## 1. Purpose
Stage 7.1h adds the derived, human-readable target-level `INDEX.md` files defined by the Stage 7 architecture.

Each target archive directory may contain:

```text
{target}/INDEX.md
```

The index is a convenience view of archived observations. It is **derived and regenerable**, not authoritative metadata.

This stage must integrate index generation with successful archive execution while preserving all Stage 7.1a–7.1g safety and CLI behavior.

## 2. Canonical placement
For the default hierarchy:

```text
ARCHIVE_ROOT/
└── {target}/
    ├── INDEX.md
    └── {location}/
        └── {session_end_date}/
            └── observation_NN/
```

`INDEX.md` belongs at the target directory level.

The hierarchy template is configurable, so index placement must be derived from the archive plan's target component rather than assuming target is always the first hierarchy segment.

For alternative hierarchy:

```text
{location}/{session_end_date}/{target}
```

the index belongs at:

```text
ARCHIVE_ROOT/{location}/{session_end_date}/{target}/INDEX.md
```

for that target directory represented by the concrete plan.

Do not hard-code `ARCHIVE_ROOT / target`.

## 3. Index scope
An index describes archived observations represented by the archive.

It should be generated only from successfully established archive content and structured Stage 7 metadata.

Do not scan FITS headers again merely to build the index.

Do not use filesystem mtimes as observation metadata.

## 4. Representative format
Use a readable Markdown structure similar to:

```markdown
# IC 434

## Warfield — 2026-01-04

### Observation 01

- Telescope: S50_99643794
- First light: 2026-01-03 22:02:59
- Last light: 2026-01-03 22:56:01
- Exposure: 10.0 s
- Filter: LP
- Light subs: 201
- Seestar stack: Stacked_195_IC 434_10.0s_LP_20260103-225603.fit
- Seestar stack count: 195
- Capture mode: Alt-Az
- GPS: ...
```

Exact punctuation may follow project style, but output must be stable, readable, deterministic, and tested.

## 5. Telescope identifier
Use the actual Seestar telescope identifier when available, e.g.:

```text
S50_99643794
```

Do not substitute a generic model string such as `ZWO Seestar S50`.

If the identifier is unavailable:

```text
unknown
```

Use existing retained FITS/discovery/planning metadata. Do not re-read FITS solely for the index.

## 6. Required observation fields
Where available, include:
- telescope identifier;
- first light timestamp;
- last light timestamp;
- exposure;
- filter;
- number of archived light subs;
- Seestar stack filename;
- reported Seestar stack count;
- capture/tracking mode;
- GPS coordinates.

Use `unknown` or an equally clear stable representation when optional metadata is unavailable.

Do not invent values.

## 7. Target/location/session grouping
Index entries should group observations in a human-friendly deterministic order.

Recommended:
1. target title;
2. location + session end date;
3. observation number.

If the concrete configurable hierarchy creates separate physical target directories for different location/session groups, each physical target directory's `INDEX.md` should describe the observations represented beneath/at that target directory rather than trying to create one global cross-tree target index.

Index semantics must follow actual planned target directory placement.

## 8. Observation numbering
Use the observation identifier/number already established by Stage 7.1d planning.

Do not independently renumber observations.

## 9. Archived light count
Report the count of successfully established archived light FITS represented by the observation.

Do not blindly report discovery count if some original light archive operations failed.

A `SKIPPED_IDENTICAL` original counts as successfully established.

A failed/colliding original does not count as newly/safely established for the current operation unless the existing execution semantics explicitly establish it as safe.

## 10. Stack reporting
If the Seestar stack was successfully archived or verified identical, report its original filename.

If no stack is associated:

```text
Seestar stack: none
```

Reported stack count remains metadata parsed from the Seestar stack filename and must not be treated as the number of light files.

## 11. Capture mode
Use retained metadata such as `eq_mode` / tracking mode.

Render a stable human-readable form, e.g. `Alt-Az`, `Equatorial`, or `unknown`, based on existing values.

Do not infer capture mode from filenames.

## 12. GPS
Use retained source GPS coordinates.

A stable representation is sufficient, e.g.:

```text
GPS: 51.123456, -0.123456
```

If unavailable:

```text
GPS: unknown
```

Do not reverse geocode.

## 13. Timestamp formatting
Render observation timestamps in a stable human-readable form.

Recommended:

```text
YYYY-MM-DD HH:MM:SS
```

Do not alter authoritative datetime semantics.

If timezone information is retained, do not silently misrepresent it as local time. Use a documented stable representation.

## 14. Exposure formatting
Use stable concise formatting, e.g.:

```text
10.0 s
```

Do not derive exposure from filename when structured metadata is already retained.

## 15. Deterministic generation
For identical structured input, generated Markdown must be byte-for-byte deterministic.

Do not include:
- generation timestamp;
- current time;
- random IDs;
- environment-dependent absolute source paths.

End the file consistently with a newline.

## 16. Regenerable model
INDEX.md is derived.

It must be safe to regenerate from current archive-operation metadata.

Do not make INDEX.md the source of truth for future archive decisions.

Do not parse existing INDEX.md to reconstruct observations.

## 17. Existing index handling
Index updates must not leave a partially written file.

Use safe staged/atomic replacement where practical:
1. render complete Markdown in memory;
2. write to a same-directory temporary file;
3. flush/fsync where consistent with project safety;
4. atomically replace `INDEX.md`.

If generation fails before replacement, preserve the previous index.

## 18. Reruns
Rerunning an identical successful archive should produce the same index content.

Do not duplicate observation sections merely because the archive command was rerun.

The implementation must be idempotent at the Markdown content level.

## 19. Existing archive history
A critical requirement: updating an index must not erase earlier observation entries merely because the current archive invocation contains only a newer observation.

Because INDEX.md is derived but archive operations may occur incrementally, design a safe way to represent all known archived observations for the physical target directory.

Preferred architecture:
- generate from structured observation metadata available from the current archive tree/plan where possible;
- if full historical structured metadata is not persisted elsewhere, use a narrowly scoped deterministic archive-tree reconstruction strategy based on archive layout and existing retained artifacts;
- do **not** treat an existing INDEX.md as authoritative input.

Codex must inspect the existing Stage 7 models and choose the smallest safe solution.

If complete historical regeneration cannot be done without re-reading archived FITS, it is acceptable for the index generator to inspect archived FITS through the established Stage 2 inspection API. This is the one permitted exception to the general "do not re-read FITS solely for the index" preference, and only when necessary to preserve historical entries.

Do not duplicate FITS parsing.

## 20. Incremental archive requirement
Example:
- run 1 archives observation_01;
- run 2 later archives observation_02 into the same physical target/location/session grouping.

After run 2, INDEX.md must contain both observation_01 and observation_02.

It must not contain duplicate observation_01 entries.

## 21. Multiple sessions
If the physical target directory encompasses multiple sessions, include all represented sessions in deterministic date/location order.

If configurable hierarchy physically separates target directories by session/location, each index covers its own physical subtree.

## 22. Integration point
Index generation occurs only after archive original/TIFF execution has completed sufficiently to know what content was safely established.

Recommended:

```text
prepare
-> execute originals
-> generate TIFFs
-> generate/update indexes
-> aggregate result
```

A TIFF failure does not necessarily prevent an observation from appearing in the index if its original FITS content is safely archived.

The index describes archived observations, not only derivative success.

## 23. Failure behavior
Index-generation failure:
- must not roll back successfully archived FITS;
- must not roll back TIFFs;
- must be visible in the overall result;
- should make an otherwise successful operation PARTIAL.

Independent target indexes may continue if one target index fails.

## 24. Result models
Add minimal immutable result models, conceptually:

```text
ArchiveIndexOutcome
ArchiveIndexResult
```

Useful outcomes may include:
- CREATED
- UPDATED
- UNCHANGED
- FAILED

Exact names may follow project conventions.

Each result should identify:
- target/index path;
- outcome;
- diagnostic/error.

Extend `SeestarArchiveResult` to expose index results.

Do not overload TIFF result types.

## 25. Aggregate status
Index failure must prevent false COMPLETE.

A successful or unchanged index should permit COMPLETE if all other required work is complete.

If original/TIFF work succeeds but an index fails, overall result should be PARTIAL.

## 26. CLI integration
The existing `archive` command should generate/update indexes during real execution.

Dry-run must **not** write INDEX.md.

Dry-run should report the index path(s) that would be generated/updated.

Do not add a separate required user command just to build indexes.

A separate internal/library regeneration helper is acceptable.

## 27. Dry-run
Dry-run remains zero mutation.

It may show:

```text
Index: .../INDEX.md
```

but must not:
- create it;
- update it;
- create temp index files.

Existing Stage 7.1g zero-mutation tests must remain green.

## 28. Index path safety
Index paths must remain within the archive root and within the concrete target directory represented by the plan.

Reject forged/traversal/symlink escape.

Do not follow an unsafe index symlink outside the archive root.

## 29. Markdown safety
Target/location values may contain Markdown-significant characters.

Render them predictably without allowing malformed headings/structure.

Use a small Markdown escaping helper if necessary.

Do not add a Markdown templating dependency.

## 30. No configuration persistence
Stage 7.1h does not add config writing.

## 31. No JPEG changes
JPEGs remain untouched.

## 32. No compression
No compression.

## 33. No reverse geocoding
No network/reverse-geocoder.

## 34. No DSLR ingestion
No DSLR work.

## 35. Tests
Add focused tests covering at minimum:
1. single target/single observation index creation;
2. exact target-level index placement under default hierarchy;
3. correct index placement when target token is not first;
4. actual telescope ID rendering;
5. unknown telescope fallback;
6. first/last light rendering;
7. exposure rendering;
8. filter rendering;
9. successful archived light count;
10. stack filename rendering;
11. no-stack rendering;
12. reported stack count rendering;
13. capture mode rendering;
14. GPS rendering;
15. unknown optional fields;
16. deterministic ordering;
17. deterministic byte output;
18. rerun unchanged result;
19. incremental second observation preserves first;
20. no duplicate sections on rerun;
21. multiple sessions;
22. multiple target directories;
23. failed original light excluded from archived-light count;
24. SKIPPED_IDENTICAL light counted;
25. failed stack not reported as safely archived;
26. TIFF failure does not erase archived observation from index;
27. index failure produces PARTIAL;
28. one index failure does not prevent independent index update;
29. existing index preserved on failed atomic replacement;
30. index path containment;
31. symlink escape rejection;
32. Markdown-significant target/location values handled;
33. dry-run reports planned index;
34. dry-run writes no index;
35. real CLI archive creates index;
36. real CLI rerun does not duplicate entries;
37. JPEGs untouched;
38. no config write;
39. no compression;
40. no network;
41. Stage 7.1g CLI/dry-run tests remain green;
42. Stage 7.1f orchestration tests remain green;
43. Stage 7.1e execution tests remain green;
44. Stage 7.1d planning tests remain green;
45. Stage 7.1c reconstruction tests remain green;
46. Stage 7.1b discovery tests remain green;
47. Stage 5/6 tests remain green;
48. full suite remains green.

## 36. Documentation
Update as required:
- `docs/ARCHITECTURE.md`;
- `docs/PROJECT_Notes.md`;
- README archive documentation if appropriate;
- preserve authoritative `docs/change_documents/STAGE_7/STAGE_7.1h.md`;
- preserve pending `docs/CHANGELOG.md` entry for `f8f07e5`.

Do not mark 7.1h complete before Stage-chat review.

## 37. Explicit exclusions
Do not implement:
- Stage 7.1i broad workflow validation;
- Stage 7.1j closure;
- reverse geocoding;
- JPEG deletion/archive;
- compression;
- DSLR ingestion;
- new FITS parser;
- new TIFF behavior;
- configuration persistence;
- Stage 8 qualification;
- Stage 9 packaging/release.

## 38. Validation
Run at least:

```text
pytest
ruff check .
git diff --check
```

Run formatting validation on changed Python files.

Explicitly confirm:
- Stage 7.1g CLI and zero-mutation dry-run tests remain green;
- Stage 7.1f orchestration tests remain green;
- Stage 7.1e execution tests remain green;
- Stage 7.1d planning tests remain green;
- Stage 7.1c reconstruction tests remain green;
- Stage 7.1b discovery tests remain green;
- Stage 5/6 conversion/CLI tests remain green;
- `convert` unchanged;
- `convert-batch` remains flat/non-recursive;
- no JPEG changes;
- no compression;
- no network;
- Stage 7.1i not started.

## 39. Closure criteria
1. Target-level INDEX.md generation exists.
2. INDEX.md is treated as derived/regenerable.
3. INDEX.md is not authoritative input.
4. Existing INDEX.md is not parsed as authoritative observation metadata.
5. Index placement follows the concrete target directory in the configured hierarchy.
6. Default hierarchy index placement is correct.
7. Alternative hierarchy with target not first is correct.
8. Index path is not hard-coded as archive_root/target.
9. Index uses planned/structured archive metadata.
10. No duplicate FITS parser is added.
11. Established FITS inspection is reused if historical reconstruction requires FITS reads.
12. Telescope identifier uses actual retained identifier when available.
13. Generic model string is not substituted for missing telescope ID.
14. Missing telescope ID renders unknown.
15. First light is rendered when available.
16. Last light is rendered when available.
17. Exposure is rendered when available.
18. Filter is rendered when available.
19. Archived light count is rendered.
20. Archived light count reflects safely established originals.
21. SKIPPED_IDENTICAL light counts as established.
22. Failed/colliding light is not falsely counted.
23. Stack filename is rendered only when safely established.
24. No-stack state is explicit.
25. Reported stack count remains distinct from light count.
26. Capture/tracking mode is rendered.
27. Capture mode is not inferred from filename.
28. GPS is rendered when available.
29. Missing GPS is explicit.
30. Reverse geocoding is not used.
31. Timestamp formatting is stable.
32. Timestamp timezone semantics are not silently falsified.
33. Exposure formatting is stable.
34. Output ordering is deterministic.
35. Output is byte-deterministic for identical input.
36. Output contains no generation timestamp.
37. Output contains no random/environment-dependent content.
38. Output ends consistently with newline.
39. Observation numbering comes from Stage 7.1d.
40. Index generator does not independently renumber observations.
41. Target heading is human readable.
42. Location/session grouping is human readable.
43. Observation headings are human readable.
44. Markdown-significant metadata is handled predictably.
45. No Markdown templating dependency is introduced.
46. Index is generated only after archive execution establishes safe content.
47. TIFF failure does not automatically exclude safely archived observation.
48. Index generation does not roll back FITS.
49. Index generation does not roll back TIFFs.
50. Index failure is visible.
51. Index failure prevents false COMPLETE.
52. Index failure produces PARTIAL when other useful work succeeded.
53. Independent index operations may continue after one failure.
54. Typed index result exists.
55. Index result identifies path.
56. Index result identifies outcome.
57. Index result exposes diagnostic/error.
58. Aggregate archive result exposes index results.
59. CREATED or equivalent outcome exists.
60. UPDATED or equivalent outcome exists.
61. UNCHANGED or equivalent outcome exists.
62. FAILED or equivalent outcome exists.
63. Index writes use complete rendered content.
64. Index update avoids partial final files.
65. Previous index is preserved if replacement fails.
66. Rerunning identical archive yields identical index content.
67. Rerun does not duplicate observation sections.
68. Incremental archive preserves earlier observation entries.
69. Incremental archive adds the new observation.
70. Multiple sessions are represented deterministically where physically in scope.
71. Multiple target directories get independent indexes.
72. Index scope follows physical target directory placement.
73. Historical observations are not erased by a later partial invocation.
74. Historical regeneration does not rely on INDEX.md as source of truth.
75. Any historical FITS inspection uses existing Stage 2 API.
76. Filesystem mtime is not used as observation metadata.
77. CLI real archive generates/updates index.
78. No separate mandatory index command is required.
79. Dry-run reports intended index path(s).
80. Dry-run does not create INDEX.md.
81. Dry-run does not update INDEX.md.
82. Dry-run creates no index temp files.
83. Stage 7.1g zero-mutation dry-run remains valid.
84. Index path is contained within archive root.
85. Traversal escape is rejected.
86. Unsafe symlink escape is rejected.
87. JPEGs remain untouched.
88. Configuration is not written.
89. Compression is not implemented.
90. No network service is added.
91. DSLR ingestion is not added.
92. Stage 7.1g CLI semantics remain unchanged except index reporting/generation.
93. Stage 7.1f orchestration semantics remain compatible.
94. Stage 7.1e execution safety remains unchanged.
95. Stage 7.1d planning remains unchanged.
96. Stage 7.1c reconstruction remains unchanged.
97. Stage 7.1b discovery remains unchanged.
98. Existing TIFF conversion behavior remains unchanged.
99. Existing Stage 6 convert remains unchanged.
100. Existing Stage 6 convert-batch remains flat/non-recursive.
101. Focused index creation test exists.
102. Focused default placement test exists.
103. Focused alternative hierarchy placement test exists.
104. Focused telescope ID test exists.
105. Focused unknown metadata test exists.
106. Focused archived-light-count test exists.
107. Focused stack reporting test exists.
108. Focused deterministic output test exists.
109. Focused unchanged rerun test exists.
110. Focused incremental preservation test exists.
111. Focused duplicate-prevention test exists.
112. Focused multiple-session/target test exists.
113. Focused TIFF-failure/index test exists.
114. Focused index-failure partial-status test exists.
115. Focused atomic-preservation test exists.
116. Focused path/symlink safety test exists.
117. Focused Markdown escaping test exists.
118. Focused dry-run no-index-write test exists.
119. Focused real CLI index-generation test exists.
120. Stage 7.1g tests pass.
121. Stage 7.1f tests pass.
122. Stage 7.1e tests pass.
123. Stage 7.1d tests pass.
124. Stage 7.1c tests pass.
125. Stage 7.1b tests pass.
126. Stage 5/6 tests pass.
127. Full test suite passes.
128. Ruff lint passes.
129. Formatting validation passes.
130. git diff --check passes.
131. Documentation accurately records pending Stage 7.1h.
132. Pending CHANGELOG entry for Stage 7.1g is preserved.
133. No Stage 7.1i work is started.
134. Broad qualification remains Stage 8.
135. Packaging/release remains Stage 9.
136. Codex makes no Git commit.

## 40. Codex completion report
Return:
1. files changed;
2. public index APIs/models;
3. exact index placement logic for default and alternative hierarchies;
4. source of index metadata, including historical/incremental reconstruction;
5. Markdown format and metadata rendering;
6. archived-light/stack eligibility rules;
7. atomic write/rerun behavior;
8. orchestration/CLI integration;
9. index failure and aggregate-status behavior;
10. dry-run behavior;
11. tests added;
12. validation commands and exact results;
13. explicit confirmation of criteria 1–136 or exceptions;
14. assumptions/open points;
15. `git status --short`;
16. confirmation no commit;
17. confirmation Stage 7.1i not started.

Do not commit. Stage chat will audit before closure.
