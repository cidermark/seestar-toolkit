# Stage 5.1e — Validate integrated TIFF output

## Purpose

Independently validate the TIFF files produced by the integrated FITS-to-TIFF
conversion path established in Stage 5.1d.

Stage 5.1e is primarily a validation and hardening stage.

It must prove that TIFF files produced from each supported FITS family are
structurally correct, numerically faithful to the established processing-path
output, and readable independently of the toolkit's own writer.

Do not add new image-processing features.

## Starting point

Stage 5.1d was completed in commit:

```text
54d8c60 — Stage 5.1d: integrate FITS conversion with TIFF output
```

The public integrated conversion API is:

```python
from seestar_toolkit.conversion import convert_fits_to_tiff
```

Conceptually, the established conversion path is:

```text
FITS inspection / classification
            |
            +-- RAW_LIGHT --> existing demosaic()
            |
            +-- RGB_IMAGE --> existing normalize_rgb_layout()
                                   |
                                   v
                              write_tiff()
```

The Stage 5 TIFF writer supports the established sample families:

```text
(H, W, 3), uint16
(H, W, 3), float32
```

including FITS byte-order representations of those numeric sample types where
applicable.

No scaling, clipping, normalization, stretching, gamma, white balance,
equalisation, quantization, orientation processing, or other display-oriented
transformation is part of the conversion contract.

## Stage 5.1e objective

Validate the complete conversion output using real authoritative FITS fixtures.

The validation must demonstrate that generated TIFF files:

1. can be opened by an independent TIFF reader;
2. are RGB images with three samples per pixel;
3. have the expected dimensions;
4. retain the expected numeric sample type;
5. retain the expected TIFF sample depth;
6. retain the expected TIFF sample format;
7. preserve pixel/sample values from the established processing path;
8. work for raw Bayer and already-RGB FITS;
9. work for standard and mosaic captures;
10. work for both Seestar and Siril RGB sources.

The tests must validate the file that was actually written to disk rather than
only inspecting arrays immediately before `write_tiff()`.

## Independent validation boundary

Use `tifffile` directly in validation tests to reopen and inspect generated TIFF
files.

Do not validate TIFF output through a toolkit helper that simply mirrors or
wraps the production writer.

The purpose is to inspect the persisted TIFF independently from the production
conversion path.

Where TIFF tags are inspected, read them from the generated TIFF itself.

## Authoritative real-data matrix

Validate the existing authoritative fixtures, using the actual repository paths
if a filename differs slightly:

```text
tests/data/seestar/light.fit
tests/data/seestar/mosaic_1.fit
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

This provides the following validation matrix:

| Source | Input family | Capture family | Expected TIFF samples |
|---|---|---|---|
| Seestar | Raw Bayer | Standard | RGB uint16 |
| Seestar | Raw Bayer | Mosaic | RGB uint16 |
| Seestar | Already RGB | Standard | RGB uint16 |
| Seestar | Already RGB | Mosaic | RGB uint16 |
| Siril | Already RGB | Standard | RGB float32 |
| Siril | Already RGB | Mosaic | RGB float32 |

Do not modify, regenerate, or replace these authoritative FITS fixtures.

The separately planned new Seestar app/firmware comparison samples are outside
Stage 5.1e.

## Structural TIFF validation

For each generated TIFF, validate as applicable:

- file exists;
- file can be reopened by `tifffile`;
- image shape is `(H, W, 3)`;
- photometric interpretation is RGB;
- samples per pixel is 3;
- bits per sample is correct;
- sample format is correct for the numeric family;
- array dtype represents the expected numeric family;
- dimensions match the normalized processing-path output.

Expected numeric TIFF families are:

### uint16 path

```text
3 samples per pixel
16 bits per sample
unsigned integer samples
```

### float32 path

```text
3 samples per pixel
32 bits per sample
IEEE floating-point samples
```

Do not require a particular TIFF compression mode unless the existing writer
contract already specifies one.

Do not introduce new metadata requirements.

## Numerical validation

For every authoritative fixture, independently establish the expected RGB array
using the already-validated pre-TIFF processing components:

### Raw Bayer

Expected data must be obtained using the existing:

- FITS inspection/classification;
- FITS image reader;
- Bayer metadata;
- `demosaic()` implementation.

### Already-RGB

Expected data must be obtained using the existing:

- FITS inspection/classification;
- FITS image reader;
- `normalize_rgb_layout()` implementation.

Then:

1. run `convert_fits_to_tiff()` to create the actual TIFF;
2. reopen that TIFF independently using `tifffile`;
3. compare the persisted TIFF samples against the expected RGB array.

For integer data, require exact equality.

For float32 data, prefer exact equality if the TIFF round-trip is demonstrably
exact. Do not introduce tolerances merely to make a failing test pass.

If exact float32 preservation fails, stop and report the observed difference
before changing the numerical contract.

## Byte-order validation

Stage 5.1d exposed the fact that real Siril FITS arrays may be represented as
big-endian float32 (`>f4`).

Stage 5.1e must explicitly confirm that TIFF files generated from the real Siril
fixtures retain the same numeric sample values after persistence and independent
reopening.

The TIFF reader may return native-endian arrays. Byte-order representation itself
does not need to remain identical after TIFF persistence.

The requirement is preservation of:

- numeric values;
- floating-point sample width;
- floating-point sample format.

Do not require TIFF byte order to match FITS byte order.

## Standard versus mosaic validation

Validate both standard and mosaic fixtures.

The test design should demonstrate that no mosaic-specific TIFF behaviour exists.

Mosaic inputs may have different dimensions, but they must use the same
conversion and validation rules as standard inputs.

Do not add explicit production branches for mosaic data.

## Producer independence

Validate both Seestar and Siril already-RGB sources.

The tests must confirm that both converge on the same TIFF-writing contract,
with source dtype/sample family preserved.

Do not add producer-specific TIFF behaviour.

## Orientation

Stage 5.1e must not introduce orientation correction.

Validation should confirm that the TIFF samples correspond directly to the
existing normalized RGB processing output.

Do not perform or require:

- rotation;
- mirroring;
- flipping;
- ROWORDER correction;
- WCS orientation correction;
- reprojection.

## File-handling regression validation

Retain the existing Stage 5 file-handling guarantees.

Review existing tests and add coverage only if necessary to ensure integrated
conversion still preserves:

- explicit output destination;
- no silent overwrite;
- existing destination remains unchanged;
- missing parent directories are not created;
- failed conversion does not report a successful TIFF path.

Do not duplicate already-sufficient tests solely to increase test count.

## Compatibility smoke check

If practical with installed project dependencies, perform a simple independent
smoke check that the generated TIFF files can be opened outside the conversion
function using `tifffile`.

Do not add Pillow, OpenCV, imageio, external command-line programs, or other new
dependencies solely for Stage 5.1e.

`tifffile` is the authoritative TIFF validation library for this stage.

## Production-code changes

Stage 5.1e should require no production-code changes if the Stage 5.1d output is
already correct.

Prefer validation-only changes.

If validation reveals a genuine defect:

1. identify the exact failed contract;
2. make the smallest justified production correction;
3. add a regression test;
4. document the correction in the completion report.

Do not refactor working production code as part of validation.

## Test organization

Prefer integration tests for real FITS-to-TIFF validation.

Extend the existing Stage 5.1d integration test module if that remains clear and
maintainable, or create a narrowly named Stage 5 TIFF validation integration test
module if separation improves clarity.

Avoid duplicating low-level TIFF writer unit tests.

## Documentation

The authoritative Stage 5.1e specification is:

```text
docs/change_documents/STAGE_5/STAGE_5.1e.md
```

Update `docs/PROJECT_Notes.md` and/or `docs/ARCHITECTURE.md` only if Stage 5.1e
establishes or corrects a documented contract.

Do not make documentation changes merely to restate test implementation details.

Preserve the normal project CHANGELOG workflow.

The pending `docs/CHANGELOG.md` update containing the Stage 5.1d entry is an
expected working-tree change and should be included in the eventual Stage 5.1e
commit. It must not be treated as contamination or discarded.

## Explicit exclusions

Do not implement:

- CLI integration;
- command-line options;
- batch conversion;
- recursive directory processing;
- output filename generation;
- archive organization;
- configurable archive hierarchy;
- automatic directory creation;
- overwrite/force options;
- 8-bit TIFF output;
- compression configuration;
- TIFF metadata policy;
- EXIF copying;
- FITS-header embedding;
- image stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- float-to-integer conversion;
- orientation correction;
- mirroring;
- rotation;
- WCS reprojection;
- registration;
- plate solving;
- mosaic stitching;
- GUI behaviour.

Do not begin Stage 5.1f.

## Validation commands

Run the focused Stage 5.1e integration validation.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

## Stage 5.1e closure criteria

Stage 5.1e can be closed only if all of the following are true:

1. All six authoritative real FITS fixtures are validated through the integrated conversion path.
2. Generated TIFF files are reopened independently using `tifffile`.
3. Raw Bayer standard output is validated.
4. Raw Bayer mosaic output is validated.
5. Seestar RGB standard output is validated.
6. Seestar RGB mosaic output is validated.
7. Siril RGB standard output is validated.
8. Siril RGB mosaic output is validated.
9. Every generated TIFF has `(H, W, 3)` RGB structure.
10. Every generated TIFF reports three samples per pixel.
11. `uint16` outputs use 16-bit unsigned integer samples.
12. `float32` outputs use 32-bit IEEE floating-point samples.
13. Raw Bayer TIFF dimensions match the existing demosaic output.
14. Already-RGB TIFF dimensions match the existing RGB normalization output.
15. Raw Bayer TIFF sample values exactly match the existing demosaic output.
16. Seestar RGB TIFF sample values exactly match the existing normalization output.
17. Siril float32 TIFF sample values are preserved exactly unless a genuine TIFF limitation is demonstrated and reported.
18. Real Siril big-endian float32 FITS data is successfully persisted and independently reopened with values preserved.
19. TIFF byte order is not incorrectly required to match FITS byte order.
20. No scaling is introduced.
21. No clipping is introduced.
22. No normalization is introduced.
23. No float-to-integer conversion is introduced.
24. No display-oriented image processing is introduced.
25. No orientation transformation is introduced.
26. Standard and mosaic inputs use the same TIFF contract.
27. Seestar and Siril RGB inputs use the same TIFF-writing contract.
28. No producer-specific TIFF processing is added.
29. Existing destination protection remains valid.
30. Missing parent directories remain uncreated.
31. No new runtime dependency is added solely for validation.
32. No output naming/archive policy is introduced.
33. No CLI integration is introduced.
34. No 8-bit TIFF behaviour is introduced.
35. Any production-code change is limited to a genuine validation-discovered defect and protected by regression coverage.
36. Focused Stage 5.1e validation tests pass.
37. Full pytest passes.
38. Ruff passes.
39. Formatting validation passes.
40. `git diff --check` passes.
41. Documentation remains accurate.
42. No unresolved issue remains that is a genuine Stage 5.1e blocker.

If any criterion fails, do not declare Stage 5.1e complete. Report the blocker
and the smallest appropriate next action.

## Codex completion report

At completion, report:

1. Whether Stage 5.1e can be closed.
2. Files created.
3. Files modified.
4. Whether any production code changed and why.
5. Test organization and changes.
6. Authoritative real-fixture matrix result.
7. Raw Bayer standard validation result.
8. Raw Bayer mosaic validation result.
9. Seestar RGB standard validation result.
10. Seestar RGB mosaic validation result.
11. Siril RGB standard validation result.
12. Siril RGB mosaic validation result.
13. Independent TIFF reopen result.
14. RGB photometric result.
15. Samples-per-pixel result.
16. uint16 bit-depth/sample-format result.
17. float32 bit-depth/sample-format result.
18. Dimension-preservation result.
19. Integer sample-preservation result.
20. Float32 sample-preservation result.
21. Siril big-endian FITS validation result.
22. Standard/mosaic independence result.
23. Producer-independence result.
24. Numerical-preservation result.
25. Orientation result.
26. File-handling regression status.
27. Confirmation that no new validation-only dependency was added.
28. Confirmation that no CLI, archive, naming, 8-bit, or metadata-policy work was added.
29. Focused Stage 5.1e test result.
30. Full pytest result.
31. Ruff result.
32. Formatting result.
33. `git diff --check` result.
34. Documentation changes.
35. Any blockers or open questions for Stage 5.1f.
36. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 5.1e can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 5.1e establishes that the integrated FITS-to-TIFF
path produces structurally correct and numerically faithful TIFF files for the
currently supported authoritative Seestar and Siril FITS families.

Stage 5.1f may then define the next Stage 5 boundary or perform Stage 5 closure
work, but it must not be started during Stage 5.1e.
