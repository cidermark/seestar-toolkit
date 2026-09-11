# STAGE 7.1i — Validate complete Stage 7 workflows

## Status
**Stage:** 7.1i  
**Stage title:** Validate complete Stage 7 workflows  
**Starting commit:** `c3052d5` — `Stage 7.1h: add target archive indexes`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording Stage 7.1h may already be present in the working tree. It is expected and must be preserved.

---

## 1. Purpose

Stage 7.1i validates the complete Stage 7 archive workflow as an integrated system.

This is primarily a **validation and defect-correction stage**, not a feature-development stage.

The workflow under validation is:

```text
Seestar source tree
→ discovery
→ observation reconstruction
→ metadata/location resolution
→ archive planning
→ original FITS execution
→ TIFF generation
→ target INDEX.md generation
→ CLI reporting / exit status
```

The goal is to prove that the Stage 7 implementation works coherently end-to-end across representative workflows and failure modes before the formal Stage 7 closure audit in Stage 7.1j.

---

## 2. Starting point

Starting commit:

```text
c3052d5 Stage 7.1h: add target archive indexes
```

Expected dirty tree before work:

```text
M docs/CHANGELOG.md
```

containing the intentional Stage 7.1h commit record.

No other unexpected modification should be present.

---

## 3. Stage character

Do not add new archive features.

Stage 7.1i may:
- add integration/system tests;
- add representative synthetic or copied test fixtures if necessary;
- add validation helpers used only to exercise existing contracts;
- correct genuine defects exposed by integrated testing;
- update documentation to record validated behavior.

Stage 7.1i must not broaden the Stage 7 product scope.

If a defect requires a production-code fix, keep it narrowly scoped to restoring the already-agreed Stage 7 contract.

---

## 4. Complete workflow to validate

Validate the complete public CLI workflow:

```text
seestar-toolkit archive SOURCE_ROOT ARCHIVE_ROOT [options]
```

including:

- discovery of supported FIT/FITS inputs;
- classification of raw lights and Seestar stack FITS;
- observation reconstruction;
- target/date/location resolution;
- observation numbering;
- archive destination planning;
- safe COPY behavior;
- explicit MOVE behavior;
- collision handling;
- TIFF conversion;
- generated INDEX.md;
- dry-run;
- configuration loading;
- interactive/non-interactive location behavior where testable;
- output summaries;
- exit codes;
- idempotent reruns.

---

## 5. Representative validation matrix

At minimum, cover these integrated scenarios.

### A. Normal COPY workflow
A source tree containing:
- one or more raw Seestar light FITS;
- one Seestar stacked RGB FITS;
- related JPEG/thumbnail files.

Validate:
- light FITS copied to `lights/`;
- light TIFFs created under `tiff/`;
- stack FITS copied to `seestar_stacked/`;
- stack TIFF created beside stack FITS;
- JPEGs untouched;
- INDEX.md generated;
- source FITS preserved;
- exit code 0.

### B. MOVE workflow
Validate:
- archived FITS established first;
- source FITS removed only through established Stage 7.1e semantics;
- TIFF conversion reads archived FITS;
- INDEX.md generated;
- no source restoration after successful move;
- exit code 0 on complete success.

### C. Dry-run
Validate:
- same discovery/reconstruction/location/planning path;
- no archive root creation;
- no copies;
- no moves;
- no source deletion;
- no TIFF generation;
- no INDEX.md;
- no temporary files;
- no config writes;
- plan/index paths reported;
- source hashes/mtimes unchanged.

### D. Idempotent rerun
Run identical COPY archive twice.

Validate:
- originals become `SKIPPED_IDENTICAL` on rerun where appropriate;
- existing TIFF behavior follows established collision contract;
- index does not duplicate observations;
- archived FITS remain byte-identical;
- no corruption;
- deterministic status/diagnostics.

Because Stage 7.1f deliberately treats existing TIFF as a collision rather than hashing it as identical, do not redefine that policy here. Validate the current contract and expected aggregate result.

### E. Differing-content collision
Create same planned FITS destination with different content.

Validate default `skip-identical` policy:
- no overwrite;
- source retained;
- collision visible;
- dependent TIFF ineligible;
- aggregate result non-success as established;
- unrelated operations continue where allowed.

### F. Explicit overwrite
Validate `--collision-policy overwrite`:
- differing destination replaced only via existing safe verified path;
- TIFF/index behavior remains coherent afterward;
- no blind overwrite logic introduced.

### G. Partial failure
Induce an expected original or TIFF failure.

Validate:
- successfully completed originals remain;
- successful TIFFs remain;
- successful indexes remain where applicable;
- independent work continues;
- aggregate status is PARTIAL when useful work exists;
- CLI exit code 1.

### H. Empty source root
Validate the exact existing no-op contract:
- library result COMPLETE;
- archive CLI exit code according to Stage 7.1g established mapping;
- no archive root created unless existing behavior explicitly does so;
- no index.

### I. Malformed FITS
Validate:
- expected FITS error is surfaced cleanly;
- no broad programming exception swallowing;
- no invalid output created;
- exit code 1.

### J. Lights-only observation
Validate coherent lights-only reconstruction/planning/archive/index behavior.

Do not invent a stack.

### K. Stack-only observation
Validate stack-only behavior if supported by existing contracts.

Do not invent lights.

### L. Multiple observations
Validate two or more reconstructed observations under the same target/session:
- stable observation numbering;
- correct directory separation;
- correct TIFF placement;
- one coherent index containing all observations.

### M. Incremental archive
Archive observation 01, then later archive observation 02 into same applicable target tree.

Validate:
- observation 01 preserved;
- observation 02 added;
- index contains both;
- no duplicate observation sections.

### N. Multiple sessions
Validate one target across more than one session end date.

Index ordering must remain deterministic and historical content must remain intact.

### O. Alternative hierarchy
Use:

```text
{location}/{session_end_date}/{target}
```

Validate:
- archive paths correct;
- index placed at the concrete target directory;
- no hard-coded default hierarchy assumptions leak through.

### P. Saved location config
Validate configuration-provided saved GPS location resolution through the real CLI path.

### Q. Explicit location override
Validate `--location` takes precedence over saved GPS match.

### R. Non-interactive fallback
Validate unmatched GPS → `unknown` without prompt.

---

## 6. Real fixture usage

Use existing authoritative Seestar fixtures where practical, including:

```text
tests/data/seestar/light.fit
tests/data/seestar/stacked.fit
```

and any other existing Stage 2/4 fixtures that are appropriate.

Do not modify authoritative fixture files.

When a test needs multiple observations, collisions, malformed files, alternative metadata or multiple dates, prefer:
- temporary copies of authoritative fixtures;
- genuine synthetic Astropy FITS created in the test;
- small controlled fixtures generated specifically for the test.

Do not fabricate non-FITS byte files and call them valid FITS.

---

## 7. Source-tree realism

Where practical, build temporary source trees resembling Seestar `My Works`, for example:

```text
My Works/
├── IC 434/
│   ├── Stacked_...fit
│   ├── Stacked_...jpg
│   └── Stacked_..._thn.jpg
└── IC 434_sub/
    ├── Light_...fit
    ├── Light_...jpg
    └── Light_..._thn.jpg
```

Do not require exact production JPEG naming for archive correctness beyond established discovery behavior.

---

## 8. Output file verification

For successful workflows, reopen outputs and verify.

### FITS
At minimum:
- archived FITS bytes match source for COPY;
- archived FITS bytes match original source content for MOVE before source deletion;
- whole-file identity where expected.

### TIFF
Use established TIFF readers/tests to verify:
- file exists;
- expected shape;
- expected dtype;
- raw Bayer light yields RGB uint16;
- native Seestar RGB stack yields RGB uint16;
- Siril float32 path remains unaffected through Stage 5/6 regression tests.

Do not add new TIFF policy.

### INDEX.md
Verify:
- correct path;
- correct target/location/session headings;
- correct observation entries;
- telescope identifier;
- light count;
- stack filename/count;
- deterministic rerun behavior.

---

## 9. Source preservation

COPY validation must prove source files remain unchanged.

MOVE validation must prove:
- intended source FITS removed only after successful destination establishment;
- unrelated source files remain;
- JPEGs remain untouched.

Dry-run must prove all sources remain unchanged.

---

## 10. Collision and safety validation

Exercise:
- identical destination;
- different-content destination;
- overwrite policy;
- source/destination same-file defense if feasible at integration level;
- path containment/symlink protections through existing focused tests.

Stage 7.1i does not need to duplicate every Stage 7.1e unit test, but the regression suite must remain green.

---

## 11. Configuration validation

Exercise real config loading with temporary TOML.

At minimum:
- hierarchy from config;
- source action from config;
- collision policy from config;
- saved location from config;
- CLI overrides config;
- missing default config remains allowed.

Do not implement config writing.

---

## 12. CLI validation

Validate both:

```text
python -m seestar_toolkit ...
```

and the configured console entry point where practical:

```text
seestar-toolkit ...
```

At minimum validate:
- `archive --help`;
- real dry-run;
- real COPY;
- at least one expected failure path;
- exit codes;
- summaries.

Preserve:
- `convert`;
- `convert-batch`.

---

## 13. Exit-code validation

Confirm:

```text
0 = complete success
1 = expected archive/planning/config/partial/failure result
2 = argparse usage error
```

Confirm the established empty-source mapping explicitly.

Do not change Stage 6 exit behavior.

---

## 14. Stage 6 preservation

Explicitly verify:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

remain compatible.

`convert-batch` must remain flat and non-recursive.

No Stage 7 validation fix may alter Stage 6 semantics unless a pre-existing regression is discovered and explicitly documented.

---

## 15. Stage 7 policy preservation

Validation must confirm the following remain true:

- default hierarchy `{target}/{location}/{session_end_date}`;
- session end date = date(capture_datetime + 12 hours);
- observation directories always numbered;
- original FITS filenames preserved;
- derivative extension `.tiff`;
- default source action COPY;
- MOVE explicit;
- JPEG default untouched;
- no compression;
- no reverse geocoding;
- no DSLR ingestion;
- no automatic config persistence;
- INDEX.md derived/regenerable;
- actual telescope ID when available;
- dry-run zero mutation.

---

## 16. Defect handling

If integrated validation exposes a defect:
1. record the failing scenario;
2. identify which established Stage 7 contract is violated;
3. make the smallest production change required;
4. add a regression test;
5. rerun the complete validation matrix;
6. document the defect and correction in the Codex report.

Do not use a validation failure as an opportunity to add new behavior.

If no defect is found, production changes may be unnecessary.

---

## 17. Documentation

Update:
- `docs/PROJECT_Notes.md` to record Stage 7.1i validation status/results;
- `docs/ARCHITECTURE.md` only if a genuine integration clarification is needed;
- README only if validation reveals existing CLI documentation is inaccurate.

Preserve:
- `docs/change_documents/STAGE_7/STAGE_7.1i.md`;
- pending `docs/CHANGELOG.md` entry for `c3052d5`.

Do not mark Stage 7 complete.

Do not perform Stage 7.1j closure work.

---

## 18. Explicit exclusions

Do not implement:
- new archive features;
- new source formats;
- DSLR ingestion;
- JPEG deletion/archive;
- compression;
- reverse geocoding;
- configuration persistence;
- new index fields beyond established Stage 7.1h contract unless required to correct a defect;
- packaging/release;
- Stage 8 broad real-dataset qualification;
- Stage 7 formal closure.

---

## 19. Validation commands

Run at minimum:

```text
pytest
ruff check .
git diff --check
```

Run formatting checks on changed Python files.

Also run useful focused matrices, for example:
- Stage 7 archive unit/integration tests;
- Stage 5/6 conversion regression tests;
- CLI tests.

Report exact counts and timings.

---

## 20. Closure criteria

1. Complete Stage 7 workflow is exercised end-to-end.
2. Validation starts from commit c3052d5.
3. Pending Stage 7.1h CHANGELOG entry is preserved.
4. No new archive feature is introduced.
5. Normal COPY workflow is validated.
6. Raw light FITS archive destination is validated.
7. Raw light TIFF generation is validated.
8. Stack FITS archive destination is validated.
9. Stack TIFF generation is validated.
10. INDEX.md generation is validated.
11. JPEGs are proven untouched in normal workflow.
12. COPY source FITS are proven preserved.
13. Normal complete COPY returns exit 0.
14. MOVE workflow is validated.
15. MOVE establishes archived FITS before source deletion.
16. MOVE TIFF generation reads archived FITS.
17. MOVE index generation succeeds.
18. Intended moved FITS source is removed on complete success.
19. Unrelated source files remain after MOVE.
20. MOVE complete success returns exit 0.
21. Dry-run uses discovery.
22. Dry-run uses reconstruction.
23. Dry-run uses location resolution.
24. Dry-run uses planning.
25. Dry-run reports planned archive work.
26. Dry-run reports planned index path.
27. Dry-run does not create archive root.
28. Dry-run does not create directories.
29. Dry-run does not copy FITS.
30. Dry-run does not move FITS.
31. Dry-run does not delete FITS.
32. Dry-run does not create TIFFs.
33. Dry-run does not create INDEX.md.
34. Dry-run creates no staging/temp files.
35. Dry-run does not write config.
36. Dry-run preserves source hashes.
37. Dry-run preserves source mtimes where reliably testable.
38. Identical rerun workflow is validated.
39. Identical FITS rerun follows SKIPPED_IDENTICAL policy.
40. Identical rerun does not corrupt archived FITS.
41. Rerun does not duplicate index observations.
42. Existing TIFF rerun follows established TIFF collision policy.
43. Rerun aggregate status is deterministic and documented.
44. Different-content FITS collision is validated.
45. Different-content collision does not overwrite under default policy.
46. Collision leaves source intact.
47. Collision is visible in result/CLI.
48. Dependent TIFF is not falsely generated from failed/colliding original.
49. Unrelated eligible work may continue.
50. Explicit overwrite workflow is validated.
51. Overwrite uses existing safe execution path.
52. No blind overwrite implementation is added.
53. Post-overwrite TIFF/index behavior is coherent.
54. Partial failure workflow is validated.
55. Successful FITS remain after later failure.
56. Successful TIFFs remain after later failure.
57. Successful indexes remain after unrelated failure where applicable.
58. Independent work continues after expected failure where established.
59. Useful progress plus failure maps to PARTIAL.
60. Partial CLI result returns exit 1.
61. Empty source workflow is validated.
62. Empty source library status matches existing COMPLETE contract.
63. Empty source CLI exit mapping matches Stage 7.1g contract.
64. Empty source creates no unintended archive/index content.
65. Malformed FITS workflow is validated.
66. Malformed FITS produces expected diagnostic.
67. Malformed FITS creates no invalid derivative output.
68. Malformed FITS maps to exit 1.
69. Unexpected programming errors are not broadly swallowed.
70. Lights-only workflow is validated.
71. Lights-only archive does not invent a stack.
72. Lights-only index state is coherent.
73. Stack-only workflow is validated where supported.
74. Stack-only archive does not invent lights.
75. Stack-only index state is coherent.
76. Multiple observations are validated.
77. Observation numbering is stable.
78. Observation directories are separated correctly.
79. TIFF placement is correct for each observation.
80. Index contains all validated observations.
81. Incremental archive workflow is validated.
82. Earlier observation remains after later archive.
83. Later observation is added.
84. Incremental index contains both.
85. Incremental index contains no duplicate observation.
86. Multiple sessions are validated.
87. Session ordering is deterministic.
88. Historical index content remains intact.
89. Alternative hierarchy is validated.
90. Alternative hierarchy archive paths are correct.
91. Alternative hierarchy target index placement is correct.
92. No default-hierarchy hard-coding is exposed.
93. Saved-location config is validated through CLI.
94. Saved GPS match resolves expected location.
95. Explicit --location override is validated.
96. Explicit location wins over saved match.
97. Non-interactive unmatched location fallback is validated.
98. Non-interactive fallback is `unknown`.
99. Non-interactive mode does not prompt.
100. Config hierarchy value is exercised.
101. Config source action value is exercised.
102. Config collision policy value is exercised.
103. CLI-over-config precedence is exercised.
104. Missing default config remains allowed.
105. Archived FITS byte identity is validated for COPY.
106. MOVE destination content identity is validated.
107. Raw light TIFF shape/dtype are validated.
108. Native stack TIFF shape/dtype are validated.
109. Existing Stage 5 Siril float32 behavior remains green.
110. INDEX.md path is validated.
111. INDEX target heading is validated.
112. INDEX location/session heading is validated.
113. INDEX observation heading is validated.
114. INDEX telescope ID is validated.
115. INDEX light count is validated.
116. INDEX stack filename/count are validated.
117. INDEX rerun determinism is validated.
118. Source action default remains COPY.
119. MOVE remains explicit.
120. Default hierarchy remains unchanged.
121. Session-end-date +12h rule remains unchanged.
122. Observation directories remain mandatory.
123. Original FITS filenames remain preserved.
124. TIFF derivatives use `.tiff`.
125. JPEG policy remains untouched/ignore.
126. Compression remains absent.
127. Reverse geocoding remains absent.
128. DSLR ingestion remains absent.
129. Config persistence remains absent.
130. INDEX remains derived/regenerable.
131. Actual telescope ID remains preferred.
132. Stage 7.1g dry-run zero-mutation tests pass.
133. Stage 7.1h index tests pass.
134. Stage 7.1f orchestration tests pass.
135. Stage 7.1e execution tests pass.
136. Stage 7.1d planning tests pass.
137. Stage 7.1c reconstruction tests pass.
138. Stage 7.1b discovery tests pass.
139. Stage 5/6 conversion tests pass.
140. Stage 5/6 CLI tests pass.
141. `convert` remains unchanged.
142. `convert-batch` remains flat/non-recursive.
143. Console `archive --help` is validated.
144. Module `archive --help` is validated.
145. Real console dry-run is exercised where practical.
146. Real console COPY is exercised where practical.
147. At least one real expected failure CLI path is exercised.
148. Exit code 0 behavior is confirmed.
149. Exit code 1 behavior is confirmed.
150. Exit code 2 usage behavior is confirmed.
151. Full Stage 7 focused regression matrix passes.
152. Full test suite passes.
153. Ruff lint passes.
154. Formatting validation passes.
155. `git diff --check` passes.
156. Any discovered defect is documented.
157. Any defect fix is narrowly scoped.
158. Every defect fix has regression coverage.
159. Complete validation is rerun after any defect fix.
160. Documentation records Stage 7.1i validation accurately.
161. Pending CHANGELOG entry for Stage 7.1h is preserved.
162. Stage 7 is not prematurely marked complete.
163. Stage 7.1j is not started.
164. Stage 8 qualification is not started.
165. Stage 9 packaging/release is not started.
166. No Git commit is made by Codex.

---

## 21. Codex completion report

Return a concise completion report containing:

1. files changed;
2. validation matrix executed;
3. exact real/synthetic fixtures used;
4. COPY validation results;
5. MOVE validation results;
6. dry-run zero-mutation proof;
7. rerun/collision/overwrite validation;
8. partial/error/empty/malformed validation;
9. lights-only/stack-only/multiple-observation/session validation;
10. alternative hierarchy/config/location validation;
11. TIFF/index output verification;
12. Stage 6 preservation results;
13. any defects discovered and exact fixes;
14. test suites and exact counts/timings;
15. Ruff/format/git diff results;
16. explicit confirmation of closure criteria 1–166 or any unsatisfied criteria;
17. assumptions/open points;
18. current `git status --short`;
19. confirmation no Git commit was made;
20. confirmation Stage 7.1j was not started.

Do not commit.

The Stage chat will audit the completion report against all closure criteria before Stage 7.1i may be marked COMPLETE.
