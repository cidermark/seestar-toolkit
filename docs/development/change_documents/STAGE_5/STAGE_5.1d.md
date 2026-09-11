# Stage 5.1d — Integrate processed RGB output with TIFF writing

## Purpose

Connect the existing validated image-processing paths to the Stage 5 TIFF writer
so that normalized RGB image data can be handed directly to TIFF output through a
single higher-level conversion operation.

Stage 5.1a through Stage 5.1c established the TIFF subsystem itself.

Stage 5.1d must integrate that writer with the existing FITS/Bayer/RGB processing
components without introducing CLI, batch, archive, or user-interface behaviour.

## Starting point

Stage 5.1c was completed in commit:

```text
1debcec — Stage 5.1c: Add float32 TIFF output support
```

The existing TIFF writer supports:

```text
(H, W, 3), uint16
(H, W, 3), float32
```

with:

- RGB channel order;
- exact value preservation;
- no scaling or image processing;
- safe destination handling;
- no silent overwrite;
- no automatic directory creation;
- rejection of non-finite float32 samples.

Stage 4 already established the normalized RGB handoff contract:

```text
(H, W, 3), RGB, linear image data
```

with source dtype preserved.

## Stage 5.1d objective

Create the smallest appropriate higher-level conversion/output operation that:

1. accepts an already-inspected or otherwise supported FITS input;
2. routes raw Bayer data through the existing Bayer demosaicing path;
3. routes already-RGB FITS through the existing RGB normalization path;
4. hands the resulting normalized RGB image directly to `write_tiff()`;
5. produces a TIFF using the existing Stage 5 numeric/file-writing policies.

Do not duplicate image-processing logic inside the TIFF subsystem.

The integration layer must orchestrate existing components rather than
re-implementing them.

## Architectural boundary

The Stage 5.1d integration operation should live outside the low-level TIFF
writer package unless the existing architecture strongly indicates otherwise.

Inspect the existing repository structure and documented architecture before
choosing the exact module/function name.

Prefer a small conversion/service layer that composes the existing:

- FITS inspection/reading;
- image classification;
- Bayer demosaicing;
- RGB normalization;
- TIFF writing.

Do not introduce a large pipeline framework, class hierarchy, plugin system, or
new abstraction layer solely for Stage 5.1d.

## Input routing

The integration path must use existing image classification/inspection behaviour.

### Raw Bayer FITS

Supported raw Bayer FITS must:

1. be recognized using existing classification logic;
2. use the existing Bayer pattern metadata;
3. be demosaiced using the existing Stage 3 implementation;
4. produce normalized:

```text
(H, W, 3), uint16
```

RGB data;
5. pass that result directly to the TIFF writer.

Do not introduce a second Bayer interpolation implementation.

### Already-RGB FITS

Supported already-RGB FITS must:

1. be recognized as RGB using existing Stage 2/Stage 4 behaviour;
2. bypass Bayer demosaicing;
3. use the existing Stage 4 RGB normalization path;
4. preserve source dtype;
5. pass normalized RGB data directly to the TIFF writer.

Validated Seestar RGB stacks therefore remain:

```text
(H, W, 3), uint16
```

Validated Siril RGB stacks therefore remain:

```text
(H, W, 3), float32
```

## Producer independence

The higher-level integration must not add producer-specific pixel-processing
branches.

Seestar and Siril already-RGB FITS must use the same structural RGB normalization
path.

Producer metadata may be inspected as part of existing classification, but must
not cause different RGB pixel-processing behaviour unless existing project logic
already requires it.

## Standard and mosaic independence

Standard and mosaic FITS must use the same pixel-processing and TIFF-writing
paths.

Do not add mosaic-specific conversion logic.

The integration should rely on existing image classification/layout handling
rather than explicit mosaic branching.

## Numerical preservation

The integration layer must not alter the established Stage 3, Stage 4, or Stage 5
numeric contracts.

It must perform no:

- scaling;
- normalization;
- clipping;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- tone mapping;
- resampling;
- integer quantization;
- float-to-integer conversion.

The normalized RGB array handed to `write_tiff()` must be the direct output of the
appropriate existing processing path.

## Orientation

Stage 5.1d must not introduce orientation processing.

Do not perform:

- mirroring;
- flipping;
- rotation;
- ROWORDER interpretation;
- WCS-based orientation correction;
- reprojection.

Orientation remains outside this stage unless an existing component already has
documented behaviour that must simply be preserved.

## Destination-path handling

Reuse the Stage 5.1b TIFF writer behaviour.

The integration layer may accept an explicit destination path and pass it through
to `write_tiff()`.

It must not:

- generate filenames;
- infer output directories;
- create missing directories;
- overwrite existing files;
- implement archive hierarchy;
- add overwrite/force options.

If a higher-level function accepts both input and output paths, the output path
must remain explicit.

## Error handling

Reuse existing subsystem exceptions where practical.

Do not hide useful toolkit-level exceptions behind a generic catch-all error.

The integration layer should preserve clear failure boundaries for:

- unsupported or invalid FITS input;
- unsupported image classification;
- invalid Bayer metadata;
- RGB normalization failure;
- TIFF image validation failure;
- TIFF/filesystem write failure.

Introduce a new conversion-level exception only if the existing architecture
clearly requires one.

Do not build an unnecessary exception hierarchy.

## Public API

Inspect existing project conventions before choosing the exact public API.

The intended shape is a simple higher-level operation conceptually similar to:

```text
convert_fits_to_tiff(input_path, output_path)
```

The exact function/module name should follow existing repository naming and
architecture.

A successful operation should return the final TIFF destination as a:

```text
pathlib.Path
```

unless an established project convention strongly suggests otherwise.

Do not introduce CLI parsing in Stage 5.1d.

## Tests

Add focused tests that verify integration rather than re-testing every low-level
implementation detail.

Coverage should include, as appropriate:

1. Raw Bayer FITS is routed through existing demosaicing and written as TIFF.
2. Already-RGB Seestar FITS bypasses Bayer demosaicing and is normalized/written.
3. Already-RGB Siril FITS bypasses Bayer demosaicing and is normalized/written.
4. Resulting raw-Bayer TIFF is `(H,W,3)` RGB `uint16`.
5. Resulting Seestar RGB TIFF is `(H,W,3)` RGB `uint16`.
6. Resulting Siril RGB TIFF is `(H,W,3)` RGB `float32`.
7. Pixel/sample values match the corresponding existing processing-path output.
8. Standard and mosaic inputs use the same conversion architecture.
9. Existing destination refusal still works through the integrated path.
10. Missing parent directories are still not created.
11. Unsupported/invalid input fails without creating a TIFF.
12. The integration does not perform orientation changes.
13. No producer-specific RGB processing branch is introduced.

Prefer using existing authoritative test fixtures.

Do not create synthetic duplicates where existing real fixtures already provide
appropriate coverage.

## Real-data validation

Where practical, validate Stage 5.1d against the existing authoritative fixtures:

```text
tests/data/seestar/light.fit
tests/data/seestar/mosaic_1.fit
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

Use the actual fixture paths present in the repository if names differ slightly.

Do not modify or replace authoritative fixtures.

The new firmware comparison samples being gathered separately are not part of
Stage 5.1d unless the user explicitly adds them to the stage.

## Production-code scope

Modify only the minimum files required to introduce the conversion/output
integration.

Expected areas may include:

```text
src/seestar_toolkit/
tests/unit/
tests/integration/
```

Choose locations based on the existing repository organization.

Do not refactor the FITS, Bayer, RGB, or TIFF subsystems unless integration
reveals a genuine defect.

If a genuine defect is found, make only the smallest justified correction and
report it clearly.

## Documentation

The authoritative Stage 5.1d specification is:

```text
docs/change_documents/STAGE_5/STAGE_5.1d.md
```

Update `docs/PROJECT_Notes.md` and/or `docs/ARCHITECTURE.md` only if needed to
record the new integration boundary accurately.

Documentation should make clear that:

- raw Bayer FITS use the existing demosaicing path;
- already-RGB FITS use the existing normalization path;
- both paths converge on the same TIFF writer;
- numeric values remain linear and unprocessed;
- CLI, batch, and archive behaviour remain future work.

Preserve the normal project CHANGELOG workflow.

## Explicit exclusions

Do not implement:

- CLI commands;
- command-line arguments;
- batch conversion;
- recursive directory processing;
- output filename generation;
- archive organisation;
- configurable archive hierarchy;
- automatic directory creation;
- overwrite/force options;
- 8-bit TIFF output;
- image stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- orientation correction;
- mirroring;
- rotation;
- WCS reprojection;
- registration;
- plate solving;
- mosaic stitching;
- metadata embedding beyond existing TIFF writer behaviour;
- GUI behaviour.

Do not begin Stage 5.1e.

## Validation commands

Run an appropriate focused integration test selection.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

## Stage 5.1d closure criteria

Stage 5.1d can be closed only if all of the following are true:

1. A higher-level FITS-to-TIFF conversion/output operation exists.
2. Raw Bayer FITS uses existing classification logic.
3. Raw Bayer FITS uses existing Stage 3 demosaicing.
4. Already-RGB FITS bypasses Bayer demosaicing.
5. Already-RGB FITS uses existing Stage 4 normalization.
6. Raw Bayer output reaches TIFF as `(H,W,3)` `uint16`.
7. Seestar RGB output reaches TIFF as `(H,W,3)` `uint16`.
8. Siril RGB output reaches TIFF as `(H,W,3)` `float32`.
9. The existing Stage 5 TIFF writer is used rather than duplicated.
10. No numeric scaling or conversion is introduced.
11. No float-to-integer conversion is introduced.
12. No image enhancement or display processing is introduced.
13. Standard and mosaic inputs use the same conversion architecture.
14. Seestar and Siril RGB inputs use the same structural RGB path.
15. No producer-specific RGB pixel-processing branch is added.
16. No mosaic-specific pixel-processing branch is added.
17. Orientation remains unchanged/deferred.
18. Existing destination overwrite protection remains effective.
19. Missing parent directories remain uncreated.
20. Invalid/unsupported input does not produce a misleading successful TIFF.
21. A successful integrated conversion returns the final TIFF path.
22. No output filename-generation policy is introduced.
23. No archive policy is introduced.
24. No CLI integration is introduced.
25. No 8-bit TIFF behaviour is introduced.
26. Focused integration tests pass.
27. Full pytest passes.
28. Ruff passes.
29. Formatting validation passes.
30. `git diff --check` passes.
31. Documentation accurately reflects the new integration boundary where needed.
32. No unresolved issue remains that is a genuine Stage 5.1d blocker.

If any criterion fails, do not declare Stage 5.1d complete. Report the blocker
and the smallest appropriate next action.

## Codex completion report

At completion, report:

1. Whether Stage 5.1d can be closed.
2. Files created or modified.
3. Public conversion API established.
4. Production-code changes.
5. Test changes.
6. Raw Bayer routing status.
7. Bayer demosaicing reuse status.
8. Already-RGB routing status.
9. RGB normalization reuse status.
10. Seestar `uint16` TIFF integration status.
11. Siril `float32` TIFF integration status.
12. Standard/mosaic independence status.
13. Producer-independence status.
14. Numerical-preservation status.
15. Orientation status.
16. Destination-path/file-handling status.
17. Error-handling status.
18. Confirmation that no CLI integration was added.
19. Confirmation that no output naming/archive logic was added.
20. Confirmation that no 8-bit output was added.
21. Real-fixture validation status.
22. Focused integration test result.
23. Full pytest result.
24. Ruff result.
25. Formatting result.
26. `git diff --check` result.
27. Documentation changes.
28. Any blockers or open questions for Stage 5.1e.
29. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 5.1d can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 5.1d establishes a complete internal conversion
path from supported FITS input to TIFF output.

Stage 5.1e may then validate produced TIFF files independently and/or define the
next output-facing boundary, but must not be started during Stage 5.1d.
