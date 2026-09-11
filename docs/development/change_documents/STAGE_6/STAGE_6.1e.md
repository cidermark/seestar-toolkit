# Seestar Toolkit — Stage 6.1e

## Integrate and Polish the Single-File `convert` CLI

### Purpose

Stage 6.1e integrates the already validated Stage 6 single-file conversion pipeline into the user-facing command-line interface and defines the supported single-file `convert` command contract.

The underlying image conversion routes are already validated:

- Stage 6.1b — raw Seestar Bayer -> `uint16` RGB TIFF;
- Stage 6.1c — native Seestar RGB -> `uint16` RGB TIFF;
- Stage 6.1d — Siril RGB -> `float32` RGB TIFF.

Stage 6.1e must expose that existing functionality cleanly through the CLI. It must not reimplement image-processing logic in the CLI.

The intended user-facing concept is:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
```

The exact syntax should follow the project's existing CLI conventions where those conventions are already established. Codex must inspect the existing CLI before making changes and preserve compatible behaviour unless this specification explicitly requires otherwise.

---

## Starting Point / Prerequisite Commit

Stage 6.1e starts from:

```text
9458bb7 Stage 6.1d: validate Siril RGB conversion path
```

Stages 1–5 and Stage 6.1a–6.1d are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1d entry as an intentional uncommitted modification. That state is normal and should ordinarily be included in the Stage 6.1e commit.

The authoritative specification for this sub-stage is:

```text
docs/change_documents/STAGE_6/STAGE_6.1e.md
```

---

## Background

Stage 6.1a established the public Python single-file conversion boundary:

```python
convert_fits_to_tiff(input_path, output_path) -> pathlib.Path
```

That operation owns orchestration of the Stage 2–5 subsystems.

The CLI must now act as a thin user-facing adapter around that operation.

The CLI must not duplicate:

- FITS inspection/classification;
- FITS reading;
- Bayer demosaicing;
- RGB layout normalisation;
- TIFF dtype handling;
- TIFF writing;
- overwrite policy.

Those responsibilities remain in their existing subsystems and the Stage 6 conversion operation.

---

## Required Work

### 1. Assess the Existing CLI First

Before changing production code, inspect the current CLI implementation, command structure, entry points, tests, help text, and existing conventions.

Determine:

- whether a `convert` command already exists;
- how arguments/subcommands are currently parsed;
- how success and failure are currently reported;
- what `python -m seestar_toolkit` currently does;
- how the installed console entry point is configured in `pyproject.toml`;
- what CLI tests already exist.

Preserve established project conventions where they are sensible.

Do not replace the CLI framework or perform an unrelated CLI rewrite.

---

### 2. Single-File `convert` Command

Provide or complete a user-facing single-file conversion command whose conceptual form is:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
```

The command must accept:

1. one input FIT/FITS path;
2. one explicit output TIFF path.

The CLI must call the existing:

```python
convert_fits_to_tiff(input_path, output_path)
```

operation.

It must not reproduce conversion logic itself.

The output path is deliberately explicit in Stage 6.1e. Automatic archive-derived output placement belongs to Stage 7.

---

### 3. Supported Input Routes

The CLI must successfully expose all three already validated conversion routes:

```text
raw Seestar Bayer  -> uint16 RGB TIFF
native Seestar RGB -> uint16 RGB TIFF
Siril RGB          -> float32 RGB TIFF
```

Stage 6.1e should validate the CLI boundary using representative existing fixtures.

It is not necessary to repeat every Stage 6.1b–6.1d fixture test through the CLI if representative coverage plus the existing pipeline suites proves the boundary adequately.

At minimum, CLI-level conversion coverage must demonstrate:

- one real raw Seestar Bayer input;
- one real native Seestar RGB input;
- one real Siril RGB input.

Use existing repository fixtures. Do not modify them.

---

### 4. Successful Command Behaviour

On successful conversion, the CLI must:

- create the requested TIFF;
- leave the source FIT/FITS unchanged;
- return a successful process exit status (`0`);
- provide concise, useful confirmation to the user.

The success output should identify the created destination path.

Avoid verbose internal implementation detail.

Do not print Python object representations or debugging information.

---

### 5. Failure Behaviour

Expected user-facing conversion failures must produce:

- a non-zero exit status;
- a concise, understandable error message;
- no Python traceback during normal CLI use.

At minimum validate appropriate CLI behaviour for:

- missing/nonexistent input;
- unsupported or unclassifiable FITS input where an existing fixture/test mechanism is available;
- existing output destination / overwrite refusal.

The CLI must preserve the underlying conversion policy rather than inventing a second overwrite policy.

A failed conversion must not damage an existing destination.

Do not add broad `except Exception` handling merely to suppress programming defects unless that is already an intentional project-wide CLI convention. Catch only the appropriate expected application/user-facing exception boundary.

Unexpected programming errors should remain diagnosable during development.

---

### 6. Input and Output Path Handling

The command must support normal filesystem paths accepted by the existing conversion API.

Paths containing spaces should work naturally through standard shell quoting.

Do not add archive path interpretation.

Do not infer target/location/date directories.

Do not create Stage 7 archive hierarchy.

Parent-directory behaviour must remain consistent with the existing Stage 5 TIFF writer contract. Do not silently introduce unrelated recursive directory creation unless that behaviour is already established and explicitly required by the current APIs.

---

### 7. Help and Usage

The CLI must provide useful help for the `convert` command.

Help should make clear:

- that the command converts one FIT/FITS image to one TIFF;
- the required input argument;
- the required output argument.

Where appropriate, identify that supported data currently includes raw Seestar Bayer, native Seestar RGB, and supported Siril RGB FITS.

Do not overload help with internal implementation detail.

Normal help requests must exit successfully.

Invalid invocation, such as missing required arguments, must fail with the CLI framework's appropriate non-zero usage exit code and useful usage/help information.

---

### 8. Existing CLI Behaviour

Existing unrelated CLI functionality must continue to work.

At minimum preserve and regression-test existing behaviour that is already part of the project, including the version command/option and existing inspection functionality if present.

Do not remove, rename, or materially alter unrelated commands merely to accommodate `convert`.

If existing syntax differs from the conceptual syntax in this document, prefer the smallest compatible evolution and report it.

---

### 9. Entry-Point Consistency

The user-facing command should behave consistently through the project's supported invocation mechanisms.

Inspect the existing project configuration and validate the mechanisms that are actually supported, such as:

```text
seestar-toolkit ...
python -m seestar_toolkit ...
```

Do not create a new packaging scheme.

If both mechanisms are currently supported, the `convert` command must be reachable through both.

Tests may invoke the CLI in-process where appropriate, but at least one validation should exercise the real configured entry-point path sufficiently to detect broken CLI wiring.

---

### 10. Source and Destination Safety

The Stage 6.1e CLI must retain the safety guarantees established by earlier stages:

- source FITS is not modified, moved, renamed, or deleted;
- existing TIFF destinations are not overwritten;
- failed conversion does not corrupt an existing destination.

Strong source hashing does not need to be repeated for every CLI fixture if the Stage 6.1b–6.1d integration tests remain authoritative, but CLI tests should include sufficient evidence that the command does not introduce file-management side effects.

Stage 7 owns file movement/copying and archive organisation.

---

## Required Tests

Add or update focused CLI tests consistent with the repository's existing test organisation.

Tests must cover at least:

1. `convert` help succeeds and documents required arguments;
2. real raw Seestar Bayer conversion through the CLI;
3. real native Seestar RGB conversion through the CLI;
4. real Siril RGB conversion through the CLI;
5. successful command returns exit status `0`;
6. successful command creates the explicitly requested destination;
7. success output identifies the destination;
8. missing/nonexistent input produces non-zero status and useful error text;
9. existing destination produces non-zero status;
10. existing destination contents remain unchanged after overwrite refusal;
11. expected user-facing conversion failures do not emit a traceback;
12. missing required arguments produce appropriate usage failure;
13. existing version behaviour remains working;
14. existing unrelated CLI command behaviour remains working where applicable;
15. supported project entry-point invocation remains wired correctly.

Do not duplicate detailed image-data assertions already owned by Stages 6.1b–6.1d unless needed to prove the CLI called the correct pipeline.

---

## Files / Components Expected to Be Affected

Likely files include:

- existing CLI implementation, probably under `src/seestar_toolkit/`;
- CLI tests;
- documentation where necessary;
- `docs/PROJECT_Notes.md`;
- `docs/change_documents/STAGE_6/STAGE_6.1e.md`;
- the intentionally modified `docs/CHANGELOG.md` as part of the eventual commit.

`pyproject.toml` should change only if a concrete entry-point deficiency is found.

The Stage 2–5 image-processing implementations should not require modification.

`src/seestar_toolkit/conversion.py` should change only if a genuine public-boundary deficiency is discovered.

Existing FITS fixtures must remain unchanged.

Avoid unrelated refactoring.

---

## Documentation Requirements

Update project documentation where necessary to record the supported single-file CLI conversion workflow.

Documentation should show the actual final syntax, for example:

```text
seestar-toolkit convert input.fit output.tiff
```

Use the syntax actually implemented by the repository.

Documentation must not claim batch conversion is complete.

Documentation must not claim archive placement is complete.

Do not document Stage 7 behaviour as though it already exists.

---

## Explicit Exclusions / Deferred Work

Stage 6.1e must not implement:

- new demosaicing behaviour;
- new RGB normalisation behaviour;
- new TIFF dtype policy;
- image enhancement;
- automatic output naming beyond what is strictly necessary for the explicit-output command;
- directory batch conversion;
- recursive directory scanning;
- wildcard/glob batch orchestration;
- batch summaries;
- continue-on-error batch policy;
- Stage 6.1f batch conversion;
- Stage 6.1g workflow validation;
- Stage 6.1h Stage 6 closure;
- archive directory creation;
- configurable archive hierarchy;
- source-file movement/copying;
- archive collision handling;
- archive missing-metadata behaviour;
- archive dry-run behaviour;
- Stage 7 functionality;
- broad Stage 8 dataset qualification;
- packaging/release work from Stage 9.

If excluded work appears necessary, report it rather than implementing it.

---

## Validation Commands

Run at minimum:

```bash
pytest <relevant Stage 6.1e CLI test files>
pytest
ruff check .
```

Run the repository's established formatting check for all changed Python source/test files.

Also run:

```bash
git diff --check
```

Exercise the actual supported CLI invocation manually or through an appropriate subprocess test sufficiently to confirm entry-point wiring.

Codex must not commit changes.

---

## Closure Criteria

Stage 6.1e may be closed only when all of the following are satisfied:

1. The existing CLI implementation and conventions were assessed before changes.
2. The project exposes a single-file `convert` command.
3. The command accepts one input FIT/FITS path.
4. The command accepts one explicit output TIFF path.
5. The CLI delegates conversion to `convert_fits_to_tiff()` rather than duplicating conversion logic.
6. A real raw Seestar Bayer fixture converts successfully through the CLI.
7. A real native Seestar RGB fixture converts successfully through the CLI.
8. A real Siril RGB fixture converts successfully through the CLI.
9. Successful conversion returns exit status `0`.
10. Successful conversion creates the explicitly requested TIFF destination.
11. Successful conversion provides concise confirmation identifying the destination.
12. Source FITS files are not modified/moved/renamed/deleted by the CLI.
13. Existing destination overwrite refusal remains enforced.
14. Existing destination contents remain unchanged after overwrite refusal.
15. Missing/nonexistent input produces a non-zero exit status.
16. Missing/nonexistent input produces useful user-facing error text.
17. Expected user-facing conversion failures do not emit Python tracebacks.
18. Unsupported/unclassifiable input receives appropriate CLI failure behaviour where an existing fixture/test mechanism permits validation.
19. Missing required command arguments produce appropriate non-zero usage behaviour.
20. `convert` help succeeds and clearly documents its required input and output arguments.
21. Paths are passed through the established filesystem/conversion APIs without archive-specific interpretation.
22. Existing version CLI behaviour remains working.
23. Existing unrelated CLI command behaviour remains working where applicable.
24. Supported configured entry-point invocation remains correctly wired.
25. No Stage 2–5 image-processing logic is duplicated in the CLI.
26. No unnecessary production conversion changes are introduced.
27. Focused Stage 6.1e CLI tests pass.
28. The complete project test suite passes.
29. Ruff passes.
30. Formatting validation for changed Python source/test files passes.
31. `git diff --check` passes.
32. Documentation accurately records the final single-file `convert` syntax where required.
33. Documentation does not imply batch conversion is complete.
34. Batch conversion remains deferred to Stage 6.1f.
35. Archive organisation and file movement remain deferred to Stage 7.
36. Broad real-dataset qualification remains deferred to Stage 8.
37. Packaging/release work remains deferred to Stage 9.
38. No unrelated refactoring or behavioural changes have been introduced.
39. Codex provides the required completion report and identifies deviations, assumptions, and blockers.

Every closure criterion must be reviewed individually before Stage 6.1e is approved for commit.

---

## Required Codex Completion Report

When complete, report:

- files changed;
- existing CLI structure/conventions found;
- final `convert` syntax;
- whether `pyproject.toml`, conversion code, or image-processing code required changes and why;
- implementation summary;
- exact real FITS fixtures exercised through the CLI;
- CLI success/failure behaviour and exit codes;
- tests added or changed;
- actual entry-point validation performed;
- validation commands and results;
- closure criteria 1–39, individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers or unresolved issues.

Do not commit any changes.

---

## Stage Boundary / What Comes Next

Successful Stage 6.1e completion establishes the supported user-facing single-file conversion workflow.

The next planned sub-stage is:

```text
Stage 6.1f — add batch conversion
```

Stage 6.1f will build on the single-file conversion operation and CLI behaviour established here.

Archive organisation remains Stage 7 and must remain separate from Stage 6 batch conversion.
