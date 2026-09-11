# Seestar Toolkit — Stage 6.1g

## Validate Stage 6 Conversion and Batch Workflows

### Purpose

Stage 6.1g performs integrated validation of the completed Stage 6 single-file and batch conversion workflows.

Stage 6 functionality is now substantially implemented. This sub-stage is therefore validation-focused, not a feature-development stage.

It must prove that the Stage 6 components work together coherently through the supported public and CLI boundaries, and identify/fix only genuine Stage 6 defects revealed by that validation.

The workflows under validation are:

```text
Single file:
FIT/FITS -> CLI -> convert_fits_to_tiff()
         -> inspect/classify/read
         -> demosaic or RGB normalize
         -> TIFF write

Batch:
input directory -> batch CLI
                -> discover FIT/FITS files
                -> convert_fits_to_tiff() per file
                -> TIFF outputs
                -> success/failure summary
```

Stage 6.1g must not introduce Stage 7 archive functionality.

---

## Starting Point / Prerequisite Commit

Stage 6.1g starts from:

```text
e6214e1 Stage 6.1f: add batch conversion
```

Stages 1–5 and Stage 6.1a–6.1f are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1f entry as an intentional uncommitted modification. This is normal and should ordinarily be included in the Stage 6.1g commit.

The authoritative specification is:

```text
docs/change_documents/STAGE_6/STAGE_6.1g.md
```

---

## Stage 6 Capabilities to Validate

Stage 6 currently provides:

1. public single-file conversion:
   `convert_fits_to_tiff(input_path, output_path) -> Path`;
2. raw Seestar Bayer conversion to channels-last `uint16` RGB TIFF;
3. native Seestar RGB conversion to channels-last `uint16` RGB TIFF;
4. Siril RGB conversion to channels-last `float32` RGB TIFF;
5. user-facing single-file CLI:
   `seestar-toolkit convert INPUT_FITS OUTPUT_TIFF`;
6. flat-directory batch conversion;
7. user-facing batch CLI:
   `seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR`;
8. case-insensitive `.fit` / `.fits` discovery;
9. deterministic, non-recursive batch processing;
10. continue-on-expected-per-file-error behaviour;
11. existing-destination protection;
12. structured batch results and summaries;
13. source-file preservation.

Stage 6.1g must validate these as an integrated workflow.

---

## Required Work

### 1. Assess Before Changing Production Code

Begin by reviewing the current Stage 6 implementation and tests.

Do not assume production changes are required.

If existing behaviour satisfies the integrated workflow contract, Stage 6.1g may consist primarily of validation tests and documentation.

Production changes are permitted only for concrete Stage 6 defects demonstrated during validation.

Do not refactor merely because this is a validation stage.

---

### 2. Validate Public Single-File Workflow

Validate `convert_fits_to_tiff()` end-to-end with representative real fixtures for all currently supported routes:

- raw Seestar Bayer;
- native Seestar RGB;
- Siril RGB.

Confirm:

- successful conversion;
- correct output existence;
- expected `(H, W, 3)` layout;
- expected dtype family;
- independently reopenable TIFF;
- explicit destination behaviour;
- source preservation.

Reuse authoritative fixtures already established in Stages 6.1b–6.1d.

Avoid duplicating unnecessary low-level pixel tests.

---

### 3. Validate Single-File CLI Workflow

Validate the real supported CLI boundary:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
```

and/or the equivalent supported module entry point.

At minimum confirm:

- successful real conversion;
- exit status `0`;
- useful success message;
- destination creation;
- expected failure status for missing input;
- expected failure status for existing destination;
- no traceback for expected application failures;
- source preservation.

The configured console-script entry point must be exercised.

---

### 4. Validate Batch Workflow End-to-End

Validate:

```text
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

using a temporary flat input directory containing representative real data.

The successful mixed batch must include at least:

- one raw Seestar Bayer file;
- one native Seestar RGB file;
- one Siril RGB file.

Confirm:

- discovery count;
- deterministic processing;
- all expected TIFFs created;
- expected filename mapping;
- independently reopenable TIFFs;
- correct dtype families;
- source preservation;
- final success summary;
- exit status `0`.

---

### 5. Validate Partial-Failure Batch Workflow

Validate a batch containing both:

- at least one valid supported FIT/FITS;
- at least one controlled invalid/unsupported FITS input or equivalent expected application-level failure.

Confirm:

- failing file is identified;
- concise reason is reported;
- no expected-error traceback;
- remaining valid file(s) still convert;
- success/failure counts are correct;
- partial batch returns exit status `1`.

This validation must demonstrate that processing continues after a failure, rather than merely unit-testing the result model.

---

### 6. Validate Existing-Destination Safety in Batch

Validate an actual batch workflow in which one mapped TIFF destination already exists.

Confirm:

- existing TIFF is not overwritten;
- its contents remain unchanged;
- that file is reported as failed;
- other eligible files continue;
- final counts reflect the failure;
- CLI returns status `1`.

---

### 7. Validate No-Match Batch Behaviour

Validate an input directory containing no FIT/FITS files.

Confirm:

- unrelated files are ignored;
- clear no-match message;
- zero discovered/succeeded/failed counts are represented consistently;
- CLI returns status `1`;
- no traceback.

---

### 8. Validate Non-Recursive Boundary

Create or use a controlled input layout containing a FIT/FITS file in a nested subdirectory.

Confirm Stage 6.1f/6.1g batch conversion does not discover or process that nested file.

This is an important Stage 6 -> Stage 7 boundary check.

---

### 9. Validate Case-Insensitive Discovery

Validate `.fit`, `.FIT`, `.fits`, and `.FITS` discovery through the integrated batch workflow where practical.

Do not merely rely on implementation inspection if an inexpensive workflow-level test can prove it.

---

### 10. Validate Source Preservation

Representative workflow tests must demonstrate that source files are not:

- modified;
- renamed;
- moved;
- deleted.

Use the established strong evidence where practical:

- existence;
- size;
- nanosecond mtime;
- SHA-256 digest.

For temporary copied fixtures, also confirm the expected source filename set remains present after batch conversion.

---

### 11. Validate CLI Compatibility

Confirm all current CLI surfaces remain coherent:

```text
seestar-toolkit --version
seestar-toolkit convert --help
seestar-toolkit convert-batch --help
```

Also preserve the established no-command help behaviour.

No command should accidentally shadow or break another command.

---

### 12. Validate Stage Boundaries

Stage 6.1g must explicitly confirm that Stage 6 has not acquired Stage 7 behaviour.

There must be no:

- configurable archive hierarchy;
- `{target}/{location}/{date}` path derivation;
- metadata-derived archive placement;
- moving/copying originals into an archive;
- recursive archive traversal;
- archive collision policy;
- missing-metadata archive policy;
- archive dry-run/rollback.

Flat output-directory creation from Stage 6.1f is not archive organisation.

---

### 13. Defect Handling

If validation discovers a genuine Stage 6 defect:

1. document the defect;
2. make the smallest appropriate fix;
3. add regression coverage;
4. rerun focused and full validation;
5. report the defect and fix explicitly.

If no defects are found, do not manufacture production changes.

Any issue belonging to Stage 7, Stage 8, or Stage 9 must be recorded/deferred rather than implemented.

---

## Required Real Fixtures

Use existing authoritative repository fixtures.

At minimum the integrated validation should exercise equivalents of:

```text
tests/data/seestar/light.fit
tests/data/seestar/stacked.fit or stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
```

Additional existing fixtures may be used where they add useful coverage without turning Stage 6.1g into broad Stage 8 dataset qualification.

Do not add newly captured datasets merely to satisfy Stage 6.1g.

Stage 8 remains responsible for broad real-dataset qualification.

---

## Required Tests

Add or refine focused workflow/integration tests as needed.

The validation suite must cover at least:

1. public pipeline raw Seestar workflow;
2. public pipeline native Seestar RGB workflow;
3. public pipeline Siril RGB workflow;
4. real single-file CLI success;
5. single-file CLI missing-input failure;
6. single-file CLI existing-destination refusal;
7. successful mixed real-data batch;
8. partial-failure batch continues;
9. existing-destination batch continues;
10. no-match batch;
11. non-recursive batch boundary;
12. case-insensitive batch discovery;
13. deterministic batch behaviour;
14. source preservation;
15. correct TIFF reopening/layout/dtype family;
16. CLI exit-status contracts;
17. traceback-free expected failures;
18. CLI version/help compatibility;
19. configured console-script entry point;
20. Stage 7 archive behaviour remains absent.

Prefer a focused Stage 6 workflow-validation test file rather than duplicating all earlier unit/integration suites.

---

## Documentation Requirements

Update `docs/PROJECT_Notes.md` and/or other relevant documentation only where necessary to record the Stage 6.1g validation result.

Documentation must not mark Stage 6 itself complete yet.

Formal Stage 6 closure belongs exclusively to Stage 6.1h.

If defects are found and fixed, document them accurately.

If no defects are found, record that the existing Stage 6 implementation passed integrated workflow validation.

---

## Expected Files / Scope

Likely changes:

- focused Stage 6 workflow integration tests;
- `docs/PROJECT_Notes.md`;
- this authoritative change document;
- existing intentional `docs/CHANGELOG.md` change.

Production files should remain unchanged unless validation demonstrates a real defect.

Do not modify Stage 2–5 processing code without a concrete regression/defect requiring it.

Existing FITS fixtures must remain unchanged.

---

## Explicit Exclusions

Stage 6.1g must not implement:

- new conversion features;
- new image formats;
- new demosaicing behaviour;
- new RGB normalization policy;
- new TIFF dtype policy;
- recursive batch conversion;
- archive organisation;
- configurable archive layout;
- source archive copy/move;
- archive collision handling;
- missing metadata archive policy;
- archive dry-run/rollback;
- overwrite/force mode;
- concurrency/parallel processing;
- file watching;
- broad Stage 8 dataset qualification;
- packaging/release work;
- Stage 6 formal closure.

Stage 6 formal closure is Stage 6.1h.

---

## Validation Commands

Run at minimum:

```bash
pytest <Stage 6.1g workflow-validation tests>
pytest
ruff check .
```

Run the established formatting check for changed Python source/test files.

Also run:

```bash
git diff --check
```

Exercise the configured `seestar-toolkit` console entry point for representative single-file and batch workflows.

Codex must not commit.

---

## Closure Criteria

Stage 6.1g may close only when all criteria below are satisfied:

1. Existing Stage 6 implementation was assessed before production changes.
2. No unnecessary production changes were introduced.
3. Public raw Seestar conversion works end-to-end.
4. Public native Seestar RGB conversion works end-to-end.
5. Public Siril RGB conversion works end-to-end.
6. Public conversion outputs reopen successfully.
7. Public conversion outputs retain expected `(H, W, 3)` layout.
8. Raw/native Seestar output dtype remains `uint16`.
9. Siril output dtype remains `float32`.
10. Explicit destination behaviour remains correct.
11. Single-file CLI succeeds on representative real input.
12. Single-file CLI success returns `0`.
13. Single-file CLI creates the requested destination.
14. Single-file CLI reports useful success output.
15. Missing single-file input returns expected non-zero status.
16. Existing single-file destination is refused.
17. Existing single-file destination remains unchanged.
18. Expected single-file failures emit no traceback.
19. Mixed real-data batch discovers all expected top-level FIT/FITS files.
20. Mixed batch converts raw Seestar input.
21. Mixed batch converts native Seestar RGB input.
22. Mixed batch converts Siril RGB input.
23. Mixed batch produces expected `.tiff` filename mapping.
24. Mixed batch TIFF outputs reopen successfully.
25. Mixed batch dtype families remain correct.
26. Full-success batch returns status `0`.
27. Full-success batch summary counts are correct.
28. Partial-failure batch identifies the failing input.
29. Partial-failure batch reports a concise reason.
30. Partial-failure batch continues to later valid input.
31. Partial-failure batch counts are correct.
32. Partial-failure batch returns status `1`.
33. Existing-destination batch does not overwrite destination.
34. Existing-destination batch preserves destination contents.
35. Existing-destination batch continues processing other files.
36. Existing-destination batch returns status `1`.
37. No-match batch clearly reports no FIT/FITS files.
38. No-match batch returns status `1`.
39. No-match batch emits no traceback.
40. Batch scanning remains non-recursive.
41. Nested FIT/FITS input is not processed.
42. `.fit`, `.FIT`, `.fits`, and `.FITS` discovery is validated.
43. Batch processing remains deterministic.
44. Representative source FITS remain present after conversion.
45. Representative source size remains unchanged.
46. Representative source nanosecond mtime remains unchanged.
47. Representative source SHA-256 remains unchanged.
48. Source files are not renamed/moved/deleted.
49. `seestar-toolkit --version` remains functional.
50. `convert --help` remains functional.
51. `convert-batch --help` remains functional.
52. Established no-command help behaviour remains functional.
53. Configured console-script entry point is exercised successfully.
54. CLI commands do not conflict or shadow one another.
55. Batch conversion remains a thin orchestrator over `convert_fits_to_tiff()`.
56. Stage 2–5 image-processing logic is not duplicated.
57. No Stage 7 archive hierarchy behaviour has been introduced.
58. No metadata-derived archive placement has been introduced.
59. No source archive copy/move behaviour has been introduced.
60. No recursive archive traversal has been introduced.
61. Any genuine Stage 6 defect found is documented and minimally fixed with regression coverage.
62. Issues outside Stage 6 scope are deferred rather than implemented.
63. Focused Stage 6.1g workflow tests pass.
64. Complete project test suite passes.
65. Ruff passes.
66. Formatting validation passes.
67. `git diff --check` passes.
68. Existing authoritative FITS fixtures remain unchanged.
69. Documentation accurately records Stage 6.1g validation.
70. Documentation does not prematurely mark Stage 6 complete.
71. Stage 6 formal closure remains deferred to Stage 6.1h.
72. Broad real-dataset qualification remains deferred to Stage 8.
73. Packaging/release remains deferred to Stage 9.
74. No unrelated refactoring or behavioural change is introduced.
75. Codex reports files changed, validation evidence, defects/fixes, deviations, assumptions, blockers, and criteria 1–75 individually.

Every criterion must be reviewed before Stage 6.1g is approved for commit.

---

## Required Codex Completion Report

Report:

- files changed;
- production files changed, if any, and the demonstrated defect requiring each change;
- integrated workflow validation design;
- exact real fixtures exercised;
- single-file public API results;
- single-file CLI results and exit statuses;
- successful mixed-batch results;
- partial-failure results;
- existing-destination results;
- no-match results;
- non-recursive/case-insensitive discovery evidence;
- source-preservation evidence;
- console-entry-point validation;
- Stage 7 boundary validation;
- defects found and fixes made, or explicitly `none`;
- tests added/changed;
- validation commands/results;
- closure criteria 1–75 individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers/unresolved issues.

Do not commit changes.

---

## Stage Boundary / Next Step

Successful Stage 6.1g completion means the implemented Stage 6 conversion and batch workflows have passed integrated validation.

It does **not** itself close Stage 6.

The next and final Stage 6 sub-stage is:

```text
Stage 6.1h — validate and close Stage 6
```

Stage 6.1h will perform the formal Stage 6 closure audit against the overall Stage 6 objectives, documentation, tests, boundaries, and outstanding issues before Stage 7 begins.
