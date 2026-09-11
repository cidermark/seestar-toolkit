# Stage 3.1d — Mosaic-session raw FITS validation

## Purpose

Validate that raw FITS files captured during Seestar mosaic sessions follow the
same existing Bayer demosaicing path as ordinary raw Seestar light frames,
across representative Seestar header generations.

Stage 3.1d is a validation and regression-testing stage. It should not introduce
mosaic-specific image-processing behaviour.

## Background

Stage 3.1c validated the end-to-end path from a real Seestar raw Bayer FITS
fixture through the existing FITS reader and inspection layer into
`demosaic(image, bayer_pattern)`.

Before Stage 3.1d, six additional raw FITS files known to have been captured
during independent Seestar mosaic sessions were inspected read-only.

All six:

- are 2-dimensional raw Bayer FITS images;
- have shape `(1920, 1080)`;
- use NumPy dtype `uint16`;
- are classified as `FitsImageLayout.RAW_BAYER`;
- are classified as `FitsImageClass.RAW_LIGHT`;
- expose normalized Bayer pattern `GRBG`;
- demosaic successfully through the existing public APIs;
- produce `(1920, 1080, 3)` `uint16` RGB output containing image data.

The reconnaissance also established that none of these six known mosaic-session
raw FITS files contains a `MOSAIC` keyword.

Therefore Stage 3.1d must not attempt to identify or prove mosaic-session origin
from a `MOSAIC` FITS header field.

## Representative fixtures

Use the following three reconnaissance samples as the permanent Stage 3.1d
regression subset:

- `mosaic_1.fit`
  - `FILTER=IRCUT`
  - `PROGRAM=5.34`
  - represents the distinct filter variant.

- `mosaic_4.fit`
  - `FILTER=LP`
  - `PROGRAM=7.32`
  - newer header variant;
  - uniquely includes `DATE-EXP` and `BIAS` among the reconnaissance set.

- `mosaic_6.fit`
  - `FILTER=LP`
  - `PROGRAM=3.31`
  - legacy header variant;
  - generic `TELESCOP=Seestar S50`;
  - lacks `EQMODE` and `WIDECAM`.

These three files provide useful header diversity while avoiding permanent
storage of six structurally redundant FITS fixtures.

## Fixture handling

The selected source files currently reside outside the repository under:

`../mosaic_images/`

For permanent automated regression testing, copy only the three selected files
into the repository's existing Seestar test-data area, following the current
fixture naming and directory conventions.

Do not alter the FITS contents.

Before and after copying, verify that each repository fixture is byte-for-byte
identical to its source file, preferably using SHA-256.

Do not add `mosaic_2.fit`, `mosaic_3.fit`, or `mosaic_5.fit` unless a concrete
test-coverage reason is discovered during implementation.

## Architecture

Preserve the existing responsibility boundary.

The FITS subsystem is responsible for:

- reading the FITS image;
- determining image layout;
- classifying the image;
- extracting and normalizing Bayer metadata.

The imaging subsystem is responsible for:

- accepting a 2-dimensional Bayer array;
- accepting an explicit Bayer pattern;
- producing linear RGB image data.

The demosaicing layer must not:

- open FITS files;
- inspect FITS headers;
- infer mosaic-session status;
- contain special handling for mosaic-session captures.

## Integration-test strategy

Add Stage 3.1d integration coverage using the three selected real
mosaic-session fixtures.

Prefer a parameterized integration test if that fits the existing test
structure cleanly.

Use the existing public FITS and imaging APIs. Do not mock the FITS reader,
inspector, or demosaicer.

For each selected fixture:

1. Read the image through the existing FITS subsystem.
2. Confirm `FitsImageLayout.RAW_BAYER`.
3. Confirm `FitsImageClass.RAW_LIGHT`.
4. Confirm the source image is 2-dimensional.
5. Obtain the Bayer pattern through the existing metadata/inspection path.
6. Confirm the normalized Bayer pattern is `GRBG`.
7. Pass the source image and inspected Bayer pattern directly to
   `demosaic(image, bayer_pattern)`.
8. Confirm demosaicing succeeds.
9. Confirm output shape is `(height, width, 3)`, deriving `height` and `width`
   from the source array rather than hard-coding them.
10. Confirm the output has three RGB channels.
11. Confirm `uint16` input remains `uint16` output.
12. Confirm the output contains non-empty image data.

Do not use brittle exact astronomical pixel-value assertions. Stage 3.1b
already provides deterministic interpolation and RGB-channel-order tests.

## Header-variant coverage

The purpose of using three fixtures is to demonstrate that differences in
non-demosaicing metadata do not require special Bayer-processing behaviour.

The Stage 3.1d test does not need to assert every differing header field.
However, it should retain enough fixture identity or parameter description to
make clear that the three representative header generations are deliberately
covered.

Do not add production branching based on:

- `PROGRAM`;
- `FILTER`;
- `TELESCOP`;
- `DATE-EXP`;
- `BIAS`;
- `EQMODE`;
- `WIDECAM`;
- mosaic-session origin.

None of those differences was found to alter the current demosaicing contract.

## Linearity and data preservation

The required image path remains:

`raw uint16 Bayer FITS → uint16 RGB`

Do not:

- convert to 8-bit;
- normalize;
- rescale for display;
- stretch;
- apply gamma;
- apply white balance;
- enhance colour;
- denoise;
- sharpen.

## Production-code changes

No production-code changes are expected.

Stage 3.1c and the six-file reconnaissance demonstrated that the existing public
FITS and imaging APIs already compose correctly.

If Stage 3.1d unexpectedly exposes a genuine production defect:

- make the smallest appropriate fix;
- explain why the fix is required;
- add focused regression coverage;
- do not broaden the scope of the stage.

Do not introduce a new abstraction solely to support these integration tests.

## Explicit exclusions

Stage 3.1d does not implement:

- mosaic detection or classification;
- mosaic stitching;
- mosaic-specific demosaicing;
- TIFF output;
- CLI conversion;
- batch processing;
- directory processing;
- RGB FITS processing;
- stacked FITS processing;
- stretching;
- gamma correction;
- white balance;
- colour enhancement;
- denoising;
- sharpening;
- alternative demosaicing algorithms;
- archive organisation.

## Acceptance criteria

Stage 3.1d is complete when:

1. The three selected real mosaic-session FITS fixtures are present in the
   repository test-data area.
2. Their copied contents are verified unchanged from the external source files.
3. All three are read using the existing FITS subsystem.
4. All three are confirmed as raw Bayer / raw-light data.
5. All three expose `GRBG` through the existing metadata path.
6. No manual Bayer-pattern override is used.
7. All three are passed through the existing public `demosaic()` interface.
8. All three produce `(height, width, 3)` RGB arrays.
9. All three preserve `uint16`.
10. All three produce non-empty image data.
11. No mosaic-specific production processing is introduced.
12. No unnecessary production abstraction is introduced.
13. Existing tests continue to pass.
14. Ruff checks pass.
15. Applicable formatting checks pass.
16. `git diff --check` passes.

## Validation

Run the focused Stage 3.1d integration coverage separately.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting check for files changed during this stage.

Do not modify unrelated files merely to clean up pre-existing formatting.

## Codex completion report

When implementation is complete, report:

1. Files created or modified.
2. Exact source fixtures copied.
3. Destination paths for permanent fixtures.
4. SHA-256 or equivalent verification that copied FITS files match their
   external sources.
5. Existing FITS APIs used.
6. Bayer pattern obtained for each fixture.
7. Whether any production-code changes were required.
8. Integration-test structure and coverage summary.
9. Focused Stage 3.1d test result.
10. Full pytest result.
11. Ruff result.
12. Formatting-check result.
13. `git diff --check` result.
14. Any assumptions, warnings, or issues.
15. `git status --short`.

Do not commit changes.

## Stage boundary

Stage 3.1d demonstrates that representative raw FITS files originating from
Seestar mosaic sessions, including legacy and newer header variants, require no
special demosaicing behaviour and pass through the same existing raw
Bayer-to-linear-RGB path.

It does not add new image-processing functionality.
