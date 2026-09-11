# Seestar Toolkit — Stage 6.1f

## Add Batch Conversion

### Purpose

Stage 6.1f adds directory-level batch conversion on top of the already validated single-file conversion pipeline and CLI.

The intended user workflow is:

```text
directory of FIT/FITS captures
        -> discover supported files
        -> convert each through convert_fits_to_tiff()
        -> write TIFFs to an explicit output directory
        -> report successes and failures
```

This is the first stage intended to support converting a whole directory of Seestar Light captures in one operation.

Stage 6.1f is **batch conversion only**.

It must not implement Stage 7 archive organisation, metadata-derived directory hierarchies, source movement/copying, archive collision policy, or configurable `{target}/{location}/{date}` placement.

---

## Starting Point / Prerequisite Commit

Stage 6.1f starts from:

```text
2fb1614 Stage 6.1e: integrate single-file convert CLI
```

Stages 1–5 and Stage 6.1a–6.1e are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1e entry as an intentional uncommitted modification. That state is normal and should ordinarily be included in the Stage 6.1f commit.

The authoritative specification for this sub-stage is:

```text
docs/change_documents/STAGE_6/STAGE_6.1f.md
```

---

## Background

The project already has a validated public single-file conversion operation:

```python
convert_fits_to_tiff(input_path, output_path) -> pathlib.Path
```

and a validated single-file CLI:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
```

The supported data routes are already proven:

- raw Seestar Bayer -> `uint16` RGB TIFF;
- native Seestar RGB -> `uint16` RGB TIFF;
- Siril RGB -> `float32` RGB TIFF.

Stage 6.1f must build batch behaviour **around** that existing operation rather than duplicate conversion logic.

---

## Required Work

### 1. Assess Existing Batch/CLI Structure First

Before changing production code, inspect:

- current CLI structure;
- current conversion module;
- existing filesystem/path helpers;
- existing test conventions;
- whether any unused or placeholder multi-file/batch code remains from earlier CLI work.

Do not introduce a new framework or unrelated command architecture.

If a previous placeholder batch concept exists, either complete it or replace it minimally in line with this specification.

---

### 2. Batch Conversion Public Behaviour

Provide a batch conversion operation and CLI entry point that converts files from one input directory into one explicit output directory.

The user-facing CLI should conceptually be:

```text
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

If the existing CLI naming conventions strongly favour a nested syntax such as:

```text
seestar-toolkit convert --batch ...
```

Codex may retain that only if it is clearly simpler and consistent with the existing parser structure.

The final syntax must be reported explicitly.

The preferred syntax for this stage is:

```text
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

---

### 3. Input Directory Contract

The batch command must:

- accept one explicit input directory;
- reject a missing path;
- reject a path that exists but is not a directory;
- scan only that directory for Stage 6.1f unless a clearly established project convention requires otherwise.

Stage 6.1f must **not recurse into subdirectories**.

Recursive archive/tree traversal belongs to later workflow design and must not be added casually here.

---

### 4. FIT/FITS Discovery

Discover regular files in the input directory whose filename extension is supported for FITS input.

At minimum support case-insensitively:

```text
.fit
.fits
```

Examples that must be discoverable:

```text
light_001.fit
light_002.FIT
stacked.fits
STACKED.FITS
```

Ignore unrelated files such as:

```text
README.txt
preview.jpg
notes.md
```

Do not treat ignored non-FITS files as conversion failures.

Symlink behaviour should follow normal `Path`/filesystem semantics unless the repository already has an explicit policy. Do not add a broad symlink-management subsystem.

---

### 5. Deterministic Processing Order

Discovered FIT/FITS files must be processed in a deterministic order.

Use a stable filename/path ordering so:

- tests are repeatable;
- user-visible output is predictable;
- batch summaries are easy to interpret.

Document the chosen ordering.

Case-sensitive vs case-insensitive sort policy may follow standard Python/path semantics unless a project convention already exists.

---

### 6. Output Directory Contract

The command accepts one explicit output directory.

For Stage 6.1f:

- the output directory must represent a flat batch destination;
- no metadata-derived subdirectories are created;
- no target/location/date layout is introduced.

If the output directory does not exist, Stage 6.1f may create that single explicitly requested directory if this is consistent with the repository's CLI ergonomics.

Do **not** recursively create a wider archive hierarchy derived from metadata.

If parent creation behaviour is introduced, it must be deliberate, tested, and documented.

---

### 7. Output Filename Mapping

Each input FIT/FITS file must map deterministically to one TIFF filename in the explicit output directory.

Default mapping:

```text
light_001.fit   -> light_001.tiff
light_002.fits  -> light_002.tiff
LIGHT_003.FIT   -> LIGHT_003.tiff
```

The source basename stem must be preserved.

Use `.tiff` as the batch output extension unless the project's established TIFF naming convention clearly requires `.tif`.

Do not derive names from FITS metadata in Stage 6.1f.

Do not rename source files.

---

### 8. Reuse the Single-File Conversion Pipeline

Every discovered FIT/FITS file must be converted by calling the existing:

```python
convert_fits_to_tiff(input_path, output_path)
```

operation.

Batch code must not duplicate:

- FITS inspection;
- classification;
- FITS reading;
- Bayer demosaicing;
- RGB normalisation;
- TIFF dtype logic;
- TIFF writing.

The batch layer owns orchestration across multiple files only.

---

### 9. Mixed Supported Input Types

A single batch may contain any mixture of currently supported FITS image types:

- raw Seestar Bayer;
- native Seestar RGB;
- Siril RGB.

Each file must route independently through the existing single-file pipeline.

Do not impose a same-type-only batch restriction unless a demonstrated technical limitation requires it.

---

### 10. Per-File Failure Handling

A batch must not abort automatically on the first expected per-file conversion failure.

For expected user/data failures:

- record/report the failed file;
- report a concise reason;
- continue processing remaining discovered FIT/FITS files.

Expected failure examples include:

- unreadable/invalid FITS;
- unsupported/unclassifiable FITS;
- existing output destination;
- other known application-level conversion errors.

Unexpected programming/system failures should not be swallowed by a blanket `except Exception`.

Catch only the established application/user-facing exception boundary.

---

### 11. Existing Destination Behaviour

Existing Stage 5 overwrite protection remains authoritative.

For an input whose mapped TIFF destination already exists:

- the existing TIFF must not be overwritten;
- that file must be reported as failed/skipped according to the batch result model;
- remaining files must continue processing;
- destination contents must remain unchanged.

Do not add an overwrite flag in Stage 6.1f unless this specification is explicitly amended.

---

### 12. Empty / No-Match Directory Behaviour

If the input directory exists but contains no `.fit` or `.fits` files:

- do not treat unrelated files as errors;
- return a clear user-facing message that no FIT/FITS files were found;
- return a non-zero status because no conversion work was performed.

Recommended exit status:

```text
1
```

If an existing CLI convention strongly indicates another non-zero application error code, preserve the convention and report it.

---

### 13. Batch Result Model

The production batch layer should provide a structured result rather than requiring the CLI to infer success/failure by parsing strings.

A suitable contract would record at minimum:

- discovered count;
- succeeded inputs/outputs or success count;
- failed inputs/reasons or failure count.

The exact type may be a dataclass or another small existing-project-appropriate model.

Do not over-engineer the result structure.

The result must let the CLI produce a final summary without duplicating orchestration logic.

---

### 14. Batch Exit Status Contract

Recommended CLI exit statuses:

```text
0 = all discovered FIT/FITS files converted successfully
1 = one or more application-level failures, or no FIT/FITS files found
2 = argparse / invocation usage error
```

A partially successful batch therefore returns `1`.

This allows automation/scripts to detect that the batch needs attention while still preserving successful outputs.

If the project already has a conflicting established application status convention, use the smallest compatible alternative and report it.

---

### 15. User-Facing Progress and Summary

The batch CLI must provide useful but concise output.

At minimum the final result must communicate:

- number discovered;
- number converted successfully;
- number failed.

For failures, identify the source filename/path and concise reason.

Successful per-file output may be printed if it remains readable, but the final summary is required.

Avoid tracebacks for expected per-file data/application failures.

Example conceptual output:

```text
Created TIFF: output/light_001.tiff
Created TIFF: output/light_002.tiff
Failed: bad.fit — unsupported FITS image type

Batch complete: 3 discovered, 2 converted, 1 failed
```

Exact wording may follow project conventions.

---

### 16. Source Preservation

Batch conversion must never:

- modify source FIT/FITS content;
- rename source FIT/FITS files;
- move source FIT/FITS files;
- delete source FIT/FITS files.

Existing Stage 6.1b–6.1e source-preservation tests remain authoritative for the single-file pipeline.

Stage 6.1f integration tests must include sufficient evidence that batch orchestration itself introduces no source-file movement or destructive side effects.

For representative fixtures, preservation should use the established strong checks where practical:

- existence;
- size;
- nanosecond mtime;
- SHA-256 digest.

---

## Required Real-Data Validation

Create focused integration coverage using temporary input/output directories populated from existing authoritative fixtures.

At minimum validate a successful batch containing representative copies of:

- one raw Seestar Bayer fixture, e.g. `light.fit`;
- one native Seestar RGB fixture, e.g. `stacked.fit` or `stacked_mosaic.fit`;
- one Siril RGB fixture, e.g. `siril_stacked.fit`.

The originals under `tests/data/` must remain unchanged.

Copy fixtures into a temporary batch input directory where necessary so batch tests do not write beside authoritative test data.

Validate that:

- all three are discovered;
- all three convert;
- expected `.tiff` names appear in the output directory;
- output files reopen successfully;
- dtype families remain correct through the existing pipeline;
- source files remain unchanged.

Also validate a mixed-result batch containing at least:

- one valid FIT/FITS file;
- one invalid/unclassifiable FITS file or equivalent controlled failure.

Confirm that:

- the valid file still converts;
- the invalid file is reported;
- the batch continues;
- final status indicates partial failure.

---

## Required Tests

Add focused unit/integration tests consistent with the existing repository structure.

Tests must cover at least:

1. batch operation discovers `.fit`;
2. batch operation discovers `.fits`;
3. extension matching is case-insensitive;
4. unrelated non-FITS files are ignored;
5. discovery/processing order is deterministic;
6. explicit input directory is required;
7. missing input directory fails cleanly;
8. non-directory input fails cleanly;
9. explicit output directory is required;
10. output directory behaviour is defined and tested;
11. output names preserve stems and use the chosen TIFF extension;
12. batch delegates each file to `convert_fits_to_tiff()`;
13. batch does not duplicate conversion logic;
14. real raw Seestar fixture converts in batch;
15. real native Seestar RGB fixture converts in batch;
16. real Siril RGB fixture converts in batch;
17. mixed supported image types work in one batch;
18. expected per-file failure does not stop later files;
19. partial success records/report counts correctly;
20. existing output refuses overwrite;
21. existing output contents remain unchanged;
22. no-match directory returns clear failure state;
23. source files remain unchanged;
24. successful full batch returns CLI status `0`;
25. partial-failure batch returns CLI status `1`;
26. no-match batch returns CLI status `1`;
27. usage errors remain argparse status `2`;
28. expected batch failures emit no traceback;
29. final summary reports discovered/succeeded/failed counts;
30. `convert-batch --help` (or final equivalent) documents required arguments;
31. existing single-file `convert` remains working;
32. existing `--version` remains working;
33. configured entry-point invocation remains correctly wired.

Avoid duplicating detailed pixel correctness tests already owned by Stages 6.1b–6.1e.

---

## Files / Components Expected to Be Affected

Likely changes include:

- a small batch conversion module or extension to `conversion.py`;
- a small batch result model if needed;
- `src/seestar_toolkit/cli.py`;
- unit tests for batch orchestration/CLI;
- integration tests for real batch conversion;
- `README.md`;
- `docs/ARCHITECTURE.md`;
- `docs/PROJECT_Notes.md`;
- `docs/change_documents/STAGE_6/STAGE_6.1f.md`;
- the intentionally modified `docs/CHANGELOG.md` as part of the eventual commit.

`pyproject.toml` should not require change unless a concrete CLI wiring deficiency is found.

Stage 2–5 image-processing code should not require change.

Existing authoritative fixtures must remain unchanged.

Avoid unrelated refactoring.

---

## Documentation Requirements

Update documentation where needed to record:

- the final batch CLI syntax;
- that it processes one flat input directory;
- supported `.fit` / `.fits` discovery;
- explicit output directory;
- deterministic stem -> `.tiff` naming;
- continuation after expected per-file failures;
- summary/exit-status behaviour.

Documentation must state clearly that:

- Stage 6.1f is batch conversion only;
- input scanning is non-recursive;
- archive hierarchy/configuration is not implemented here;
- Stage 7 owns archive organisation and file movement.

Do not imply broad Stage 8 dataset qualification is complete.

---

## Explicit Exclusions / Deferred Work

Stage 6.1f must not implement:

- recursive directory traversal;
- recursive archive scanning;
- metadata-derived output hierarchy;
- configurable `{target}/{location}/{date}` layout;
- alternate archive hierarchy preferences;
- source file copy/move into archive;
- archive root configuration;
- archive collision policy;
- missing metadata archive policy;
- archive dry-run;
- archive rollback;
- Stage 7 functionality;
- broad Stage 8 dataset qualification;
- packaging/release work;
- overwrite mode/force flag;
- parallel/multiprocess conversion;
- file watching;
- background processing;
- automatic deletion of source files;
- image enhancement;
- new demosaicing/RGB/TIFF policies.

Do not introduce recursive conversion simply because a directory API makes it easy.

If any excluded capability appears necessary, report it rather than implementing it.

---

## Validation Commands

Run at minimum:

```bash
pytest <relevant Stage 6.1f unit/integration test files>
pytest
ruff check .
```

Run the repository's established formatting check for all changed Python source/test files.

Also run:

```bash
git diff --check
```

Exercise the actual supported batch CLI invocation manually or through subprocess testing.

At least one validation must use the project's configured console-script entry point if practical, in addition to in-process or `python -m` testing.

Codex must not commit changes.

---

## Closure Criteria

Stage 6.1f may be closed only when all of the following are satisfied:

1. Existing CLI/conversion/filesystem structure was assessed before implementation.
2. A batch conversion operation exists as a thin orchestrator over `convert_fits_to_tiff()`.
3. A user-facing batch CLI command exists.
4. Final batch CLI syntax is documented and reported.
5. Batch accepts one explicit input directory.
6. Batch accepts one explicit output directory.
7. Missing input directory fails cleanly.
8. Non-directory input fails cleanly.
9. `.fit` files are discovered.
10. `.fits` files are discovered.
11. FIT/FITS extension matching is case-insensitive.
12. Unrelated non-FITS files are ignored.
13. Input scanning is non-recursive.
14. Processing order is deterministic.
15. Output filenames preserve source stems.
16. Output files use the documented TIFF extension.
17. No metadata-derived archive naming is introduced.
18. Batch delegates each conversion to `convert_fits_to_tiff()`.
19. No Stage 2–5 image-processing logic is duplicated.
20. Mixed raw Seestar, native Seestar RGB, and Siril RGB inputs can be processed in one batch.
21. Real raw Seestar data converts successfully through batch.
22. Real native Seestar RGB data converts successfully through batch.
23. Real Siril RGB data converts successfully through batch.
24. Expected per-file conversion failure does not abort remaining files.
25. Batch result records/report success and failure counts.
26. Failed file and concise reason are identifiable.
27. Existing output destinations remain protected from overwrite.
28. Existing destination content remains unchanged after refusal.
29. No-match input directory produces clear user-facing failure.
30. Full-success batch CLI exits `0`.
31. Partial-failure batch CLI exits `1`.
32. No-match batch CLI exits non-zero, expected `1`.
33. CLI usage errors retain argparse status `2`.
34. Expected batch application failures do not emit Python tracebacks.
35. Final CLI summary reports discovered/succeeded/failed counts.
36. Batch help succeeds and documents required input/output directories.
37. Source FIT/FITS files are not modified, moved, renamed, or deleted.
38. Representative source preservation is validated with strong evidence.
39. Existing single-file `convert` remains functional.
40. Existing `--version` remains functional.
41. Supported configured CLI entry point remains wired correctly.
42. Focused Stage 6.1f tests pass.
43. Complete project test suite passes.
44. Ruff passes.
45. Formatting validation for changed Python source/test files passes.
46. `git diff --check` passes.
47. Documentation accurately records batch syntax and behaviour.
48. Documentation explicitly states non-recursive Stage 6.1f scope.
49. Archive hierarchy/configuration/file movement remains deferred to Stage 7.
50. Broad real-dataset qualification remains deferred to Stage 8.
51. Packaging/release remains deferred to Stage 9.
52. No overwrite/force mode, parallel processing, file watching, or unrelated scope creep is introduced.
53. No unrelated refactoring or behavioural changes are introduced.
54. Codex provides the required completion report and identifies deviations, assumptions, and blockers.

Every closure criterion must be reviewed individually before Stage 6.1f is approved for commit.

---

## Required Codex Completion Report

When complete, report:

- files changed;
- existing batch-related/CLI structure found;
- final batch CLI syntax;
- batch operation/result-model design;
- input discovery and ordering policy;
- output directory and filename policy;
- per-file error/continue policy;
- batch exit-status policy;
- exact real fixtures exercised;
- full-success and partial-failure evidence;
- source-preservation evidence;
- whether conversion/image-processing/pyproject code required changes and why;
- tests added/changed;
- actual entry-point validation performed;
- validation commands/results;
- closure criteria 1–54 individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers/unresolved issues.

Do not commit any changes.

---

## Stage Boundary / What Comes Next

Successful Stage 6.1f completion establishes:

- reliable single-file CLI conversion;
- reliable flat-directory batch conversion;
- continuation/reporting for expected per-file failures.

The next planned sub-stage is:

```text
Stage 6.1g — validate Stage 6 conversion and batch workflows
```

Stage 6.1g is validation/integration work, not an excuse to introduce Stage 7 behaviour.

Stage 7 remains responsible for archive organisation, configurable directory hierarchy, source/generated file placement, collisions, missing metadata, copy/move policy, and archive dry-run behaviour.
