# Seestar Toolkit — Stage 6.1h

## Validate and Close Stage 6

### Purpose

Stage 6.1h is the formal closure audit for Stage 6 — Command-line polish and batch processing.

Stage 6 functionality has already been implemented and integrated through Stages 6.1a–6.1g. Stage 6.1g completed end-to-end workflow validation without finding a production defect.

Stage 6.1h must therefore:

1. audit the complete Stage 6 implementation against its intended objectives;
2. confirm all Stage 6 sub-stages are complete and coherent;
3. confirm tests, CLI behaviour, documentation, and stage boundaries remain correct;
4. run final validation from the current repository baseline;
5. identify any unresolved Stage 6 blocker;
6. update project documentation to formally mark Stage 6 complete only if all closure requirements pass.

This is a closure stage, not a feature-development stage.

---

## Starting Point / Prerequisite Commit

Stage 6.1h starts from:

```text
8969837 Stage 6.1g: validate Stage 6 conversion and batch workflows
```

The Stage 6.1g `docs/CHANGELOG.md` entry may exist as the normal intentional uncommitted change following that commit.

The authoritative specification for this closure audit is:

```text
docs/change_documents/STAGE_6/STAGE_6.1h.md
```

---

## Stage 6 Objective

Stage 6 must leave Seestar Toolkit with reliable user-facing single-file and flat-directory batch FIT/FITS-to-TIFF conversion.

The completed Stage 6 boundary is:

```text
Single file:
FIT/FITS
  -> CLI or public conversion API
  -> existing Stage 2–5 processing
  -> explicit TIFF destination

Batch:
flat input directory
  -> deterministic non-recursive FIT/FITS discovery
  -> existing single-file conversion pipeline per file
  -> explicit flat output directory
  -> per-file results and final summary
```

Stage 6 does not own archive organisation.

---

## Stage 6 Sub-stage Audit

Confirm the repository and documentation accurately reflect completion of:

### Stage 6.1a — Define conversion pipeline contract

Expected established behaviour:

- `convert_fits_to_tiff(input_path, output_path) -> pathlib.Path`;
- RAW_LIGHT routes through Bayer demosaicing;
- RGB_IMAGE routes through RGB layout normalization;
- both routes use the established TIFF writer;
- UNKNOWN/unsupported conversion fails cleanly;
- established subsystem exceptions propagate appropriately.

Starting implementation commit:

```text
6c1ee7e Stage 6.1a: define conversion pipeline contract
```

### Stage 6.1b — Validate raw Bayer conversion path

Expected established behaviour:

- real Seestar raw Bayer input validated;
- GRBG metadata used through existing inspection/demosaicing path;
- channels-last `uint16` RGB TIFF produced;
- source preservation validated.

Commit:

```text
8001815 Stage 6.1b: validate raw Bayer conversion path
```

### Stage 6.1c — Validate native Seestar RGB conversion path

Expected established behaviour:

- native stacked Seestar RGB FITS validated;
- existing channels-first to channels-last normalization reused;
- `uint16` preserved;
- no duplicate axis/reordering implementation;
- source preservation and overwrite protection validated.

Commit:

```text
98e42b3 Stage 6.1c: validate native Seestar RGB conversion path
```

### Stage 6.1d — Validate Siril RGB conversion path

Expected established behaviour:

- Siril stacked RGB FITS validated;
- existing RGB normalization path reused;
- source big-endian float representation normalized appropriately by the established pipeline;
- output remains native `float32`;
- no Siril-specific conversion branch;
- established finite-float TIFF protections remain authoritative.

Commit:

```text
9458bb7 Stage 6.1d: validate Siril RGB conversion path
```

### Stage 6.1e — Integrate single-file convert CLI

Expected established syntax:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
python -m seestar_toolkit convert INPUT_FITS OUTPUT_TIFF
```

Expected behaviour:

- one explicit input and output;
- delegates to `convert_fits_to_tiff()` exactly once;
- successful conversion status `0`;
- expected application failure status `1`;
- argparse usage status `2`;
- concise user-facing messages;
- no traceback for expected application errors;
- `--version`, help, module entry point, and configured console script remain functional.

Commit:

```text
2fb1614 Stage 6.1e: integrate single-file convert CLI
```

### Stage 6.1f — Add batch conversion

Expected established syntax:

```text
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
python -m seestar_toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

Expected behaviour:

- explicit flat input and output directories;
- `.fit` and `.fits` discovery, case-insensitive;
- regular top-level files only;
- non-recursive;
- deterministic processing;
- source stem -> `.tiff`;
- every file delegates to `convert_fits_to_tiff()`;
- mixed raw Seestar/native Seestar RGB/Siril RGB supported;
- expected per-file failures recorded while later files continue;
- existing destinations protected;
- structured batch result;
- clear final summary;
- status `0` for complete success;
- status `1` for partial/application failure or no matches;
- argparse status `2`;
- no archive behaviour.

Commit:

```text
e6214e1 Stage 6.1f: add batch conversion
```

### Stage 6.1g — Validate Stage 6 conversion and batch workflows

Expected established result:

- integrated real-data validation passed;
- all three conversion routes passed;
- configured console script passed;
- successful mixed batch passed;
- partial-failure continuation passed;
- existing-destination safety passed;
- no-match behaviour passed;
- case-insensitive and non-recursive discovery passed;
- strong source preservation passed;
- Stage 7 boundary passed;
- no production defect was found.

Commit:

```text
8969837 Stage 6.1g: validate Stage 6 conversion and batch workflows
```

---

## Required Closure Work

### 1. Audit, Do Not Rebuild

Review the current repository before making changes.

Do not reimplement or redesign Stage 6.

Production code changes are permitted only if the closure audit exposes a concrete Stage 6 defect that prevents closure.

If a defect is found:

1. document it;
2. make the smallest appropriate fix;
3. add regression coverage;
4. rerun all relevant validation;
5. report it explicitly.

Do not introduce improvements merely because they are desirable.

---

### 2. Confirm Stage 6 Public API Contract

Confirm the current public single-file conversion path remains:

```python
convert_fits_to_tiff(input_path, output_path) -> pathlib.Path
```

Confirm it remains a thin orchestrator over established Stage 2–5 functionality and does not duplicate image-processing policy.

Confirm all supported Stage 6 routes remain:

- raw Seestar Bayer -> RGB `uint16` TIFF;
- native Seestar RGB -> RGB `uint16` TIFF;
- Siril RGB -> RGB `float32` TIFF.

---

### 3. Confirm Single-File CLI Contract

Confirm current syntax and behaviour:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
```

Verify:

- help;
- representative successful real conversion;
- output creation;
- exit `0`;
- expected application failure exit `1`;
- argparse usage exit `2`;
- existing-destination refusal;
- no traceback for expected application failures.

---

### 4. Confirm Batch CLI Contract

Confirm current syntax and behaviour:

```text
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

Verify:

- help;
- explicit input/output directories;
- non-recursive discovery;
- case-insensitive `.fit` / `.fits`;
- deterministic ordering;
- stem -> `.tiff`;
- mixed supported input types;
- expected-failure continuation;
- existing-destination protection;
- no-match behaviour;
- correct summaries;
- exit `0` complete success;
- exit `1` partial/application/no-match failure;
- argparse usage exit `2`.

---

### 5. Confirm Real-Data Coverage

Confirm existing tests continue to validate representative authoritative fixtures for:

```text
tests/data/seestar/light.fit
tests/data/seestar/stacked.fit
tests/data/reference/siril_stacked.fit
```

Equivalent already-authoritative variants are acceptable where existing tests use them.

Do not expand into broad Stage 8 dataset qualification.

---

### 6. Confirm Source Preservation

Confirm Stage 6 workflow coverage demonstrates that source FITS files are not:

- modified;
- renamed;
- moved;
- deleted.

Retain the established strong preservation evidence based on existence, size, nanosecond mtime, and SHA-256 where currently used.

Authoritative fixtures themselves must remain unchanged.

---

### 7. Confirm CLI Compatibility

Validate:

```text
seestar-toolkit --version
seestar-toolkit convert --help
seestar-toolkit convert-batch --help
```

Confirm established no-command help behaviour and configured console-script wiring.

Where practical also confirm:

```text
python -m seestar_toolkit --version
```

No Stage 6 command should conflict with another.

---

### 8. Confirm Stage 6 -> Stage 7 Boundary

Stage 6 closure requires explicit confirmation that archive organisation remains deferred.

Stage 6 must not implement:

- configurable archive hierarchy;
- `{target}/{location}/{date}` path derivation;
- alternative archive layouts such as `{location}/{date}/{target}`;
- metadata-derived archive placement;
- source-file archive copy/move;
- archive-root configuration;
- archive collision policy;
- missing-metadata archive policy;
- archive dry-run/rollback;
- recursive archive organisation.

The flat explicitly requested output directory used by batch conversion is Stage 6 behaviour and is not an archive hierarchy.

Stage 7 owns archive organisation and file management.

---

### 9. Confirm Later-Stage Boundaries

Confirm:

- broad real-world dataset qualification remains Stage 8;
- packaging and release remain Stage 9.

Do not pull those responsibilities into Stage 6 closure.

---

### 10. Documentation Closure

Review at least:

```text
README.md
docs/ARCHITECTURE.md
docs/PROJECT_Notes.md
docs/CHANGELOG.md
docs/change_documents/STAGE_6/
```

Ensure they are mutually coherent regarding Stage 6 behaviour.

`PROJECT_Notes.md` must be updated to mark Stage 6 complete only after closure validation passes.

The documentation should accurately record:

- Stage 6 purpose;
- completed single-file conversion;
- completed batch conversion;
- supported Stage 6 conversion families;
- final CLI syntax;
- non-recursive flat-directory batch scope;
- exit/failure behaviour at an appropriate level;
- Stage 7 archive boundary;
- Stage 8 qualification boundary;
- Stage 9 packaging/release boundary;
- Stage 6.1h closure status.

Do not invent future implementation details.

---

### 11. Change-document Audit

Confirm Stage 6 authoritative change documents are present and coherent for:

```text
STAGE_6.1a.md
STAGE_6.1b.md
STAGE_6.1c.md
STAGE_6.1d.md
STAGE_6.1e.md
STAGE_6.1f.md
STAGE_6.1g.md
STAGE_6.1h.md
```

Report missing or inconsistent documents as blockers unless safely correctable as documentation-only closure work.

---

### 12. Final Validation

Run at minimum:

```bash
pytest
ruff check .
git diff --check
```

Run formatting validation for changed Python files, if any.

Exercise the configured console entry point directly for representative Stage 6 behaviour.

At minimum validate:

```text
seestar-toolkit --version
seestar-toolkit convert --help
seestar-toolkit convert-batch --help
```

Perform at least one representative real single-file conversion and one representative real mixed batch conversion through the configured entry point, using temporary destinations.

Do not modify authoritative fixture files.

---

## Expected Changes

Stage 6.1h should normally require only documentation changes, including:

- `docs/PROJECT_Notes.md`;
- this authoritative change document;
- possibly README/ARCHITECTURE only if the audit identifies an actual documentation inconsistency;
- the normal pending `docs/CHANGELOG.md` update from Stage 6.1g.

Production Python code and tests should normally remain unchanged because Stage 6.1g already completed integrated validation successfully.

Do not create closure-only tests merely to increase test counts if existing tests already prove the required contracts.

---

## Explicit Exclusions

Do not implement:

- new conversion functionality;
- recursive batch processing;
- archive hierarchy;
- configurable archive layouts;
- source archive movement/copying;
- archive metadata policy;
- overwrite/force options;
- concurrency;
- file watching;
- new FITS classification;
- new demosaicing;
- new RGB normalization;
- new TIFF policy;
- broad Stage 8 qualification;
- packaging/release;
- unrelated refactoring.

---

## Closure Criteria

Stage 6 may be formally closed only if all criteria below are satisfied.

### Stage history and implementation

1. Stage 6.1a is complete and its conversion pipeline contract remains valid.
2. Stage 6.1b is complete and raw Seestar conversion remains validated.
3. Stage 6.1c is complete and native Seestar RGB conversion remains validated.
4. Stage 6.1d is complete and Siril RGB conversion remains validated.
5. Stage 6.1e is complete and single-file CLI remains validated.
6. Stage 6.1f is complete and batch conversion remains validated.
7. Stage 6.1g is complete and integrated Stage 6 validation remains valid.
8. Stage 6.1a–6.1g commits are accurately represented in project documentation.
9. No unresolved blocker from a prior Stage 6 sub-stage remains.

### Public conversion contract

10. `convert_fits_to_tiff(input_path, output_path)` remains the single-file conversion API.
11. It returns the requested output as a `pathlib.Path`.
12. Raw Seestar Bayer inputs route through established demosaicing.
13. Native Seestar RGB inputs route through established RGB normalization.
14. Siril RGB inputs route through established RGB normalization.
15. Raw Seestar output remains channels-last RGB `uint16`.
16. Native Seestar RGB output remains channels-last RGB `uint16`.
17. Siril RGB output remains channels-last RGB `float32`.
18. TIFF output remains independently reopenable.
19. Existing TIFF destinations remain protected from overwrite.
20. Stage 2–5 processing logic is not duplicated in Stage 6 orchestration.

### Single-file CLI

21. `seestar-toolkit convert INPUT_FITS OUTPUT_TIFF` remains the supported single-file syntax.
22. Single-file command help succeeds.
23. Representative real single-file conversion succeeds.
24. Successful single-file conversion returns status `0`.
25. Requested TIFF destination is created.
26. Expected application failure returns status `1`.
27. Argparse usage errors return status `2`.
28. Existing destination is refused.
29. Expected application failures do not emit tracebacks.
30. Single-file CLI delegates through the established conversion pipeline.

### Batch CLI

31. `seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR` remains the supported batch syntax.
32. Batch command help succeeds.
33. Batch uses one explicit input directory.
34. Batch uses one explicit flat output directory.
35. `.fit` files are discovered.
36. `.fits` files are discovered.
37. FIT/FITS extension matching remains case-insensitive.
38. Unrelated non-FITS files are ignored.
39. Batch scanning remains non-recursive.
40. Nested FIT/FITS files are not processed.
41. Batch processing remains deterministic.
42. Output naming remains source stem -> `.tiff`.
43. Batch delegates each discovered file to `convert_fits_to_tiff()`.
44. Mixed raw Seestar/native Seestar RGB/Siril RGB batches remain supported.
45. Expected per-file failure does not abort later eligible files.
46. Batch result/reporting retains discovered, succeeded/converted, and failed counts.
47. Failed inputs remain identifiable with concise reasons.
48. Existing output destinations remain protected.
49. Existing output destination contents remain unchanged.
50. No-match input produces a clear failure.
51. Full-success batch returns status `0`.
52. Partial/application-failure batch returns status `1`.
53. No-match batch returns status `1`.
54. Batch argparse usage errors return status `2`.
55. Expected batch failures do not emit tracebacks.
56. Batch final summary remains coherent.

### Real-data and preservation validation

57. Representative real raw Seestar fixture coverage remains present.
58. Representative real native Seestar RGB fixture coverage remains present.
59. Representative real Siril RGB fixture coverage remains present.
60. Representative mixed real-data batch coverage remains present.
61. Representative outputs are independently reopened by tests/validation.
62. Expected output layouts and dtype families are validated.
63. Source FITS files remain present after conversion.
64. Source FITS sizes remain unchanged.
65. Source FITS nanosecond mtimes remain unchanged where strong preservation checks are used.
66. Source FITS SHA-256 digests remain unchanged where strong preservation checks are used.
67. Source FITS are not renamed, moved, or deleted.
68. Authoritative repository FITS fixtures remain unchanged.

### CLI compatibility

69. Configured `seestar-toolkit` console entry point remains wired and executable.
70. `seestar-toolkit --version` succeeds.
71. Version output remains `1.1.0` for the current development release.
72. `convert --help` succeeds.
73. `convert-batch --help` succeeds.
74. Established no-command help behaviour remains functional.
75. Module entry point remains functional.
76. Stage 6 commands do not conflict or shadow one another.

### Stage boundaries

77. Stage 6 contains no configurable archive hierarchy implementation.
78. Stage 6 contains no `{target}/{location}/{date}` archive path derivation.
79. Stage 6 contains no alternative metadata-derived archive layout implementation.
80. Stage 6 does not move/copy source FITS into an archive.
81. Stage 6 contains no archive-root configuration implementation.
82. Stage 6 contains no archive collision/missing-metadata/dry-run/rollback policy.
83. Stage 6 batch behaviour remains flat and non-recursive.
84. Archive organisation and file management remain explicitly assigned to Stage 7.
85. Broad real-dataset qualification remains assigned to Stage 8.
86. Packaging and release remain assigned to Stage 9.

### Documentation and change control

87. README accurately describes current Stage 6 user-facing behaviour.
88. ARCHITECTURE accurately describes current Stage 6 architecture and Stage 7 boundary.
89. PROJECT_Notes accurately records Stage 6 implementation and validation status.
90. PROJECT_Notes marks Stage 6 complete only after this closure audit passes.
91. CHANGELOG history is coherent with the established commit workflow.
92. Stage 6.1a authoritative change document is present.
93. Stage 6.1b authoritative change document is present.
94. Stage 6.1c authoritative change document is present.
95. Stage 6.1d authoritative change document is present.
96. Stage 6.1e authoritative change document is present.
97. Stage 6.1f authoritative change document is present.
98. Stage 6.1g authoritative change document is present.
99. Stage 6.1h authoritative change document is present.
100. Stage 6 change documents are mutually coherent enough for closure.
101. No documentation prematurely claims Stage 7, Stage 8, or Stage 9 completion.

### Final quality gate

102. No unnecessary production-code change is introduced during closure.
103. Any genuine closure-blocking Stage 6 defect found is minimally fixed and regression-tested.
104. No unrelated refactoring or behavioural change is introduced.
105. Full project test suite passes.
106. Ruff passes.
107. Formatting validation passes for changed Python files, if any.
108. `git diff --check` passes.
109. Configured console entry point is exercised directly during closure.
110. Representative real single-file conversion passes through the configured entry point.
111. Representative real mixed batch conversion passes through the configured entry point.
112. Closure validation does not modify authoritative FITS fixtures.
113. No unresolved Stage 6 blocker remains.
114. Stage 6 can be formally declared complete.
115. Codex provides the complete closure report required below.

All 115 criteria must be reviewed before the Stage 6.1h commit is approved.

---

## Required Codex Closure Report

Report:

1. files changed;
2. production files changed, if any, and the concrete closure-blocking defect requiring each;
3. Stage 6.1a–6.1g audit result;
4. current public conversion API contract;
5. current single-file CLI syntax and behaviour;
6. current batch CLI syntax and behaviour;
7. exact authoritative real fixtures confirmed;
8. source-preservation evidence;
9. configured console-entry-point validation;
10. representative real single-file closure run;
11. representative real mixed-batch closure run;
12. CLI version/help/module-entry validation;
13. Stage 6 -> Stage 7 boundary audit;
14. Stage 8 and Stage 9 boundary audit;
15. documentation audit;
16. Stage 6 change-document audit;
17. defects found and fixes made, or explicitly `none`;
18. full validation commands and results;
19. whether authoritative fixtures changed;
20. closure criteria 1–115 individually marked satisfied/not satisfied;
21. deviations;
22. assumptions;
23. blockers/unresolved issues;
24. explicit conclusion whether Stage 6.1h and Stage 6 may close.

Do not commit changes.

---

## Completion Boundary

If every closure criterion passes, Stage 6.1h may be approved and Stage 6 formally declared complete.

The next development stage is:

```text
Stage 7 — Archive organisation and file management
```

Stage 7 will own archive placement and configurable directory hierarchy, including the planned default:

```text
{target}/{location}/{date}
```

and permitted alternative hierarchy preferences.

Do not begin Stage 7 implementation as part of Stage 6.1h.
