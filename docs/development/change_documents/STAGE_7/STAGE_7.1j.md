# STAGE 7.1j — Validate and formally close Stage 7

## Status
**Stage:** 7.1j  
**Stage title:** Validate and formally close Stage 7  
**Starting commit:** `ae5abdb` — `Stage 7.1i: validate complete archive workflows`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording Stage 7.1i may already be present in the working tree. It is expected and must be preserved.

---

## 1. Purpose

Stage 7.1j is the formal closure audit for Stage 7 — Archive organisation and file management.

This stage must determine whether Stage 7 can be declared complete.

It is a **closure/audit stage**, not a feature-development stage.

The audit must:
- reconcile the original Stage 7 objectives and architecture against what 7.1a–7.1i delivered;
- verify all public/archive behaviors remain coherent;
- verify all Stage 7 policy decisions are reflected accurately in implementation and documentation;
- rerun the final regression and quality gates;
- identify any unresolved Stage 7 defects or scope gaps;
- update project documentation to mark Stage 7 complete only if the audit passes.

Production-code changes are permitted only if a genuine unresolved Stage 7 defect is discovered during the audit. Any such fix must be minimal, documented, regression-tested, and fully revalidated before closure.

---

## 2. Starting point

Starting commit:

```text
ae5abdb Stage 7.1i: validate complete archive workflows
```

Expected dirty tree before work:

```text
M docs/CHANGELOG.md
```

containing the intentional Stage 7.1i commit record.

No other unexpected modification should be present.

---

## 3. Stage 7 scope to reconcile

Stage 7 delivered archive organisation and file management for Seestar FIT/FITS workflows.

The audit must reconcile the following implemented capabilities:

1. Archive architecture and policy contracts.
2. Seestar input discovery/classification.
3. Observation reconstruction and stack association.
4. Metadata/location/session resolution and destination planning.
5. Safe archive COPY/MOVE/collision operations.
6. TIFF generation integrated with archive execution.
7. Archive CLI, TOML configuration, interaction and strict dry-run.
8. Human-readable target indexes.
9. Complete integrated workflow validation.

Stage 7 does **not** include:
- JPEG deletion or JPEG archival;
- compression;
- reverse geocoding/network lookup;
- config persistence/writing;
- DSLR ingestion;
- Stage 8 broad real-dataset qualification;
- Stage 9 packaging/release.

---

## 4. Original Stage 7 architectural decisions to audit

### 4.1 Terminology
Confirm documentation and implementation remain consistent with:
- Session = observing night/period at a location.
- Observation = one discrete imaging capture/run of one target.
- Light = individual sub-exposure.
- Seestar stack = Seestar-generated stacked product associated with an observation.

### 4.2 Session end date
Confirm:

```text
session_end_date = date(capture_datetime + 12 hours)
```

is preserved solely for archive grouping and source timestamps are never modified.

### 4.3 Configurable hierarchy
Confirm default:

```text
{target}/{location}/{session_end_date}
```

and alternative token orders remain supported through TOML/CLI planning.

### 4.4 Canonical observation layout
Confirm observation-scoped structure remains:

```text
observation_NN/
├── lights/
├── seestar_stacked/
└── tiff/
```

with original light FITS directly under `lights/`, stack FITS plus stack TIFF under `seestar_stacked/`, and light TIFFs under `tiff/`.

### 4.5 Filenames
Confirm:
- source FITS basenames are preserved;
- derivatives use `.tiff`;
- no silent rename policy was introduced.

### 4.6 Target/path normalization
Confirm:
- spaces/case are preserved as intended;
- unsafe/path-traversal characters are neutralised/rejected safely;
- no absolute/traversal escapes are possible.

### 4.7 Location policy
Confirm precedence remains:
1. explicit CLI/user location;
2. saved configured GPS match;
3. interactive manual/accepted suggestion path where applicable;
4. `unknown`.

Confirm non-interactive mode does not prompt and no network/reverse-geocoding dependency was added.

### 4.8 Source action
Confirm:
- COPY remains default;
- MOVE remains explicit and copy-verify-delete;
- source deletion occurs only after safe destination establishment.

### 4.9 Collision policy
Confirm default remains safe:
- identical → skip where applicable;
- differing content → collision/error unless explicit overwrite;
- no silent overwrite.

### 4.10 JPEG policy
Confirm JPEGs remain untouched/ignored by default.

### 4.11 Compression
Confirm no compression behavior is implemented.

### 4.12 Dry-run
Confirm dry-run shares discovery/reconstruction/location/planning paths but makes zero filesystem/config mutation.

### 4.13 Indexes
Confirm:
- `INDEX.md` remains derived/regenerable;
- existing index Markdown is not authoritative input;
- actual telescope identifier is preferred;
- historical/incremental observations are preserved;
- index placement follows the concrete target directory in the configured hierarchy.

### 4.14 Future DSLR compatibility
Confirm Stage 7 did not implement DSLR ingestion while keeping architecture reasonably source-neutral where already designed.

---

## 5. Public API audit

Review the public archive API surface exposed from `seestar_toolkit.archive`.

Confirm that the current API is coherent and intentional, including the established areas:

- discovery;
- reconstruction;
- planning;
- execution;
- orchestration;
- configuration;
- indexing.

Check that:
- immutable models remain appropriate;
- exception types remain scoped;
- no accidental internal helper has been unnecessarily exported;
- no public symbol introduced during Stage 7 is obviously inconsistent with project naming conventions.

Do not redesign the public API during closure unless an actual defect exists.

---

## 6. CLI audit

Audit:

```text
seestar-toolkit archive SOURCE_ROOT ARCHIVE_ROOT [options]
```

with established options:

```text
--dry-run
--location LOCATION
--hierarchy HIERARCHY
--source-action {copy,move}
--collision-policy {skip-identical,error,overwrite}
--non-interactive
--config PATH
```

Confirm:
- help text remains accurate;
- exit codes remain 0/1/2 as established;
- dry-run reporting is clear;
- index reporting is present;
- config precedence is documented accurately;
- no hidden Stage 7 option exists without documentation.

Also confirm Stage 6 commands remain untouched:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

and `convert-batch` remains flat/non-recursive.

---

## 7. Configuration audit

Audit default config path:

```text
~/.config/seestar-toolkit/config.toml
```

and schema:

```toml
[archive]
hierarchy = "{target}/{location}/{session_end_date}"
source_action = "copy"
collision_policy = "skip-identical"

[[locations]]
name = "Warfield"
latitude = 51.4
longitude = -0.7
radius_m = 500
```

Confirm:
- CLI > TOML > built-in precedence;
- missing default config allowed;
- explicit missing config errors cleanly;
- malformed TOML errors cleanly;
- invalid saved locations rejected;
- unknown keys ignored for forward compatibility;
- no config writing/persistence is implemented.

---

## 8. Integrated workflow audit

Re-run or rely on existing tests plus focused final checks to confirm all established workflows remain green:

- normal COPY;
- explicit MOVE;
- strict dry-run;
- identical rerun;
- differing-content collision;
- explicit overwrite;
- partial failure;
- empty source;
- malformed FITS;
- lights-only;
- stack-only;
- multiple observations;
- incremental archive;
- multiple sessions;
- alternative hierarchy;
- saved location;
- explicit location override;
- non-interactive unknown fallback;
- index creation/update/unchanged/failure behavior.

No new behavior should be added merely to expand matrix coverage beyond Stage 7.1i unless a genuine uncovered contract gap is found.

---

## 9. Incremental observation fix audit

Stage 7.1i introduced a narrow reconciliation fix so later archive invocations can allocate new observation numbers without merging into historical observation directories.

Audit specifically that:
- identical reruns continue to map to the existing observation;
- differing-content collisions remain tied to the existing planned destination;
- genuinely new source sets receive the next observation number;
- TIFF-only remnants do not reserve an observation;
- symlinked observation/frame directories are not trusted;
- reconciliation remains read-only;
- no directory/file mutation happens during preparation.

This fix must be explicitly documented as part of final Stage 7 behavior.

---

## 10. Documentation audit

Audit:
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/PROJECT_Notes.md`
- `docs/CHANGELOG.md`
- all `docs/change_documents/STAGE_7/STAGE_7.1a.md` through `STAGE_7.1j.md`

Ensure documentation:
- reflects the actual final Stage 7 CLI/options;
- accurately describes archive layout;
- accurately describes source-action/collision behavior;
- accurately describes dry-run;
- accurately describes config/location handling;
- accurately describes index behavior;
- records the Stage 7.1i incremental-observation correction;
- contains no stale statement implying Stage 7 functionality that was deferred;
- does not claim Stage 8 qualification or Stage 9 release work is complete.

If the audit passes:
- update `docs/PROJECT_Notes.md` to mark Stage 7 complete;
- replace any “Stage 7 Current Focus” wording with a Stage 7 summary/closure status as appropriate;
- record the successful 7.1j closure audit;
- preserve Stage 8 and Stage 9 roadmap entries.

Do not invent future Stage details not already planned.

---

## 11. Changelog handling

Preserve the pending Stage 7.1i commit record in `docs/CHANGELOG.md`.

During Stage 7.1j, update the changelog only as required by the project’s normal stage-documentation conventions.

Do not insert a 7.1j commit ID before the user has actually committed Stage 7.1j.

---

## 12. Final quality gates

Run at minimum:

```text
pytest
ruff check .
git diff --check
```

Run formatting validation on changed Python files, if any.

Also run a focused Stage 7 regression matrix.

If no production code changes are made, the final full suite still must pass from the starting codebase.

Report exact counts and timings.

---

## 13. Real command smoke checks

Where practical, confirm:

```text
seestar-toolkit archive --help
python -m seestar_toolkit archive --help
seestar-toolkit convert --help
seestar-toolkit convert-batch --help
```

Use a real archive dry-run or COPY smoke check with existing fixtures if useful to corroborate test results.

Do not mutate repository fixtures.

---

## 14. Closure decision

At the end of Stage 7.1j, Codex must explicitly conclude one of:

### PASS
Stage 7 can be formally closed.

or

### FAIL
Stage 7 cannot be closed, with each blocking defect/gap listed precisely.

Do not mark Stage 7 complete merely because tests pass; the architecture/documentation reconciliation must also pass.

---

## 15. Production defect policy

If an unresolved Stage 7 defect is discovered:
1. do not declare closure;
2. document the violated Stage 7 contract;
3. implement the smallest correction;
4. add focused regression coverage;
5. rerun the complete final audit;
6. only then declare PASS if all criteria are met.

If the defect is substantial enough to constitute new feature work, Stage 7.1j must FAIL rather than silently expanding scope.

---

## 16. Explicit exclusions

Do not implement:
- JPEG deletion/archive;
- compression;
- reverse geocoding;
- config persistence;
- DSLR ingestion;
- new archive modes;
- new hierarchy tokens;
- new TIFF formats;
- Stage 8 real-dataset qualification;
- Stage 9 packaging/release.

Do not start Stage 8 work.

---

## 17. Closure criteria

1. Audit starts from commit ae5abdb.
2. Pending Stage 7.1i CHANGELOG entry is preserved.
3. Unexpected dirty-tree changes are absent or explained.
4. Stage 7.1a architecture decisions are reconciled.
5. Stage 7.1b discovery behavior is reconciled.
6. Stage 7.1c reconstruction behavior is reconciled.
7. Stage 7.1d planning behavior is reconciled.
8. Stage 7.1e execution behavior is reconciled.
9. Stage 7.1f TIFF orchestration is reconciled.
10. Stage 7.1g CLI/config/dry-run behavior is reconciled.
11. Stage 7.1h index behavior is reconciled.
12. Stage 7.1i validation and incremental fix are reconciled.
13. Session terminology is documented consistently.
14. Observation terminology is documented consistently.
15. Light terminology is documented consistently.
16. Seestar stack terminology is documented consistently.
17. session_end_date +12h rule remains implemented.
18. Source FITS timestamps are not modified.
19. Default hierarchy remains `{target}/{location}/{session_end_date}`.
20. Alternative hierarchy token orders remain supported.
21. Hierarchy requires exactly supported tokens as established.
22. Observation directories remain mandatory.
23. Observation numbering remains deterministic.
24. Incremental new observations receive new numbers.
25. Identical reruns retain established observation number.
26. Differing-content collision retains established destination semantics.
27. TIFF-only remnants do not reserve observation numbers.
28. Incremental reconciliation is read-only.
29. Incremental reconciliation does not follow unsafe symlinks.
30. Light FITS remain under `lights/`.
31. Light TIFFs remain under `tiff/`.
32. Stack FITS remain under `seestar_stacked/`.
33. Stack TIFF remains beside stack FITS.
34. Original FITS basenames are preserved.
35. TIFF derivatives use `.tiff`.
36. No silent rename policy exists.
37. Archive component normalization remains safe.
38. Traversal/absolute path escapes remain prevented.
39. Symlink escape protections remain in place.
40. Explicit location remains highest precedence.
41. Saved GPS location matching remains supported.
42. Non-interactive unmatched location falls back safely.
43. Non-interactive mode does not prompt.
44. No reverse geocoding dependency exists.
45. Default source action remains COPY.
46. MOVE remains explicit.
47. MOVE remains copy-verify-delete.
48. Source deletion occurs only after destination establishment.
49. Default collision policy remains safe.
50. Identical original destinations can be skipped safely.
51. Different-content originals are not silently overwritten.
52. Explicit overwrite remains opt-in.
53. JPEGs remain untouched by default.
54. Compression is not implemented.
55. Config persistence is not implemented.
56. DSLR ingestion is not implemented.
57. Dry-run shares preparation logic.
58. Dry-run performs zero filesystem mutation.
59. Dry-run performs zero config mutation.
60. Dry-run reports planned destinations.
61. Dry-run reports planned index path.
62. INDEX.md remains derived/regenerable.
63. Existing INDEX.md is not authoritative metadata.
64. Historical indexes preserve prior observations.
65. Index placement follows concrete target hierarchy position.
66. Actual telescope identifier is preferred.
67. Missing telescope identifier renders clearly.
68. Index writes remain safe/atomic.
69. Index failure cannot falsely produce COMPLETE.
70. Public discovery API remains coherent.
71. Public reconstruction API remains coherent.
72. Public planning API remains coherent.
73. Public execution API remains coherent.
74. Public orchestration API remains coherent.
75. Public configuration API remains coherent.
76. Public indexing API remains coherent.
77. Public exception model remains coherent.
78. No obviously accidental public export remains.
79. Archive CLI command exists and help is accurate.
80. `--dry-run` remains supported.
81. `--location` remains supported.
82. `--hierarchy` remains supported.
83. `--source-action` remains supported.
84. `--collision-policy` remains supported.
85. `--non-interactive` remains supported.
86. `--config` remains supported.
87. CLI exit code 0 remains complete success.
88. CLI exit code 1 remains expected operational/partial failure.
89. CLI exit code 2 remains usage error.
90. Empty source behavior remains the established complete no-op.
91. Default config path remains documented.
92. CLI > TOML > built-in precedence remains documented/implemented.
93. Missing default config remains allowed.
94. Explicit missing config remains an error.
95. Malformed TOML remains an error.
96. Invalid saved locations remain rejected.
97. Unknown config keys remain tolerated.
98. No config write occurs.
99. Normal COPY integration remains green.
100. MOVE integration remains green.
101. Dry-run integration remains green.
102. Identical rerun integration remains green.
103. Different-content collision integration remains green.
104. Explicit overwrite integration remains green.
105. Partial failure integration remains green.
106. Empty-source integration remains green.
107. Malformed-FITS integration remains green.
108. Lights-only integration remains green.
109. Stack-only integration remains green.
110. Multiple-observation integration remains green.
111. Incremental archive integration remains green.
112. Multiple-session integration remains green.
113. Alternative hierarchy integration remains green.
114. Saved-location integration remains green.
115. Explicit-location override remains green.
116. Non-interactive fallback remains green.
117. Index outcome integration remains green.
118. Raw light TIFF path remains green.
119. Native Seestar RGB TIFF path remains green.
120. Siril float32 TIFF regression remains green.
121. Stage 6 `convert` remains unchanged.
122. Stage 6 `convert-batch` remains unchanged.
123. `convert-batch` remains flat/non-recursive.
124. Stage 6 CLI exit behavior remains unchanged.
125. README archive documentation matches implementation.
126. ARCHITECTURE archive documentation matches implementation.
127. PROJECT_Notes Stage 7 status matches implementation.
128. Stage 7.1a change document remains present.
129. Stage 7.1b change document remains present.
130. Stage 7.1c change document remains present.
131. Stage 7.1d change document remains present.
132. Stage 7.1e change document remains present.
133. Stage 7.1f change document remains present.
134. Stage 7.1g change document remains present.
135. Stage 7.1h change document remains present.
136. Stage 7.1i change document remains present.
137. Stage 7.1j change document remains present.
138. Stage 7.1i incremental fix is documented.
139. No stale documentation claims deferred JPEG behavior is implemented.
140. No stale documentation claims compression is implemented.
141. No stale documentation claims reverse geocoding is implemented.
142. No stale documentation claims config persistence is implemented.
143. No stale documentation claims DSLR ingestion is implemented.
144. Stage 8 remains future qualification work.
145. Stage 9 remains future packaging/release work.
146. Focused Stage 7 regression suite passes.
147. Full pytest suite passes.
148. Ruff passes.
149. Formatting validation passes where applicable.
150. git diff --check passes.
151. Console archive help smoke check passes.
152. Module archive help smoke check passes.
153. Stage 6 command help smoke checks pass.
154. No repository fixture is mutated.
155. No network access is introduced.
156. No new dependency is introduced unless strictly required by a defect fix.
157. No new archive feature is introduced.
158. Any production defect discovered is documented.
159. Any defect correction is narrowly scoped.
160. Any defect correction has regression coverage.
161. Full audit is rerun after any defect correction.
162. PROJECT_Notes is updated to Stage 7 complete only if audit passes.
163. Stage 7 closure summary records successful 7.1j audit.
164. Stage 8 and Stage 9 roadmap entries are retained.
165. Stage 7 is not marked complete if any blocking defect remains.
166. Codex explicitly declares PASS or FAIL.
167. If PASS, Codex explicitly states Stage 7 can be closed.
168. If FAIL, Codex lists every blocker.
169. Stage 8 work is not started.
170. Stage 9 work is not started.
171. No Git commit is made by Codex.

---

## 18. Codex completion report

Return:

1. files changed;
2. starting-tree verification;
3. Stage 7 architecture reconciliation summary;
4. public API audit;
5. CLI/config audit;
6. integrated workflow audit;
7. incremental observation-fix audit;
8. documentation audit;
9. any defects found and corrections;
10. focused regression result;
11. full test-suite result;
12. Ruff/format/git diff results;
13. command smoke-check results;
14. explicit confirmation of closure criteria 1–171 or exceptions;
15. final PASS/FAIL decision;
16. if PASS, explicit statement: `Stage 7 can be formally closed.`;
17. assumptions/open points;
18. current `git status --short`;
19. confirmation no Git commit was made;
20. confirmation Stage 8 and Stage 9 were not started.

Do not commit.

The Stage chat will review the closure audit before approving the final Stage 7 commit.
