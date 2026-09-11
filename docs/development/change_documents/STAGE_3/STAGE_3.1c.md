# Stage 3.1c — Real Seestar FITS Integration

## Purpose

Validate the end-to-end path from a real Seestar raw Bayer FITS file to a
demosaiced linear RGB image.

Stage 3.1c connects the FITS reading and metadata-inspection behaviour
established in Stage 2 with the Bayer demosaicing behaviour established in
Stages 3.1a and 3.1b.

The purpose of this stage is integration and validation. It does not introduce
TIFF output or display-oriented image processing.

## Scope

Stage 3.1c will use an existing real Seestar raw Bayer FITS test file.

The integration path must:

1.  Read the FITS image using the existing FITS subsystem.
2.  Confirm that the image is classified as raw Bayer data.
3.  Obtain the Bayer pattern using the existing FITS metadata/inspection
    behaviour.
4.  Supply the raw 2-dimensional image array and Bayer pattern to
    `demosaic(image, bayer_pattern)`.
5.  Verify that the result is a 3-dimensional RGB image.
6.  Verify output shape `(height, width, 3)`.
7.  Verify `uint16` output for the existing Seestar `uint16` sample.
8.  Verify that the operation does not modify the source FITS file.

The current real Seestar raw samples are expected to use Bayer pattern
`GRBG`.

## Architecture

Stage 3.1c must preserve the existing separation of responsibilities.

### FITS subsystem

The FITS subsystem remains responsible for:

-   Reading FITS image data.
-   Classifying the FITS image layout.
-   Reading FITS metadata.
-   Identifying the Bayer pattern.

### Imaging subsystem

The imaging subsystem remains responsible for:

-   Accepting a 2-dimensional Bayer image array.
-   Accepting an explicitly supplied Bayer pattern.
-   Performing Bayer-to-RGB interpolation.
-   Returning a linear RGB NumPy array.

The demosaicing module must not begin reading FITS files or inspecting FITS
headers.

## Integration Strategy

Prefer an integration test that composes the existing public FITS APIs with
the existing public demosaicing API.

Do not add a new production abstraction merely to make the integration test
convenient unless the current public APIs genuinely cannot express the
required workflow.

If a small production integration point is genuinely required, Codex must
explain why before making broader architectural changes.

## Test Data

Use an existing real Seestar raw Bayer FITS file already stored under the
project's test-data structure.

Prefer an existing standard raw light sample rather than adding a new large
binary test file.

Do not duplicate an existing FITS fixture.

The selected test file must be a raw 2-dimensional Bayer image and must expose
a Bayer pattern through the existing metadata-inspection path.

## Files

### Create or Modify

The primary expected change is an integration test under:

```text
tests/integration/
```

Use the existing integration-test structure and naming conventions in the
repository.

Codex should inspect the existing test layout before choosing the exact
filename.

### Modify only if genuinely required

Existing production files may be modified only if the current public FITS and
imaging APIs cannot be composed to perform the required integration.

Likely production areas, if required, would be limited to:

```text
src/seestar_toolkit/fits/
src/seestar_toolkit/imaging/
```

Do not modify production code merely to create a convenience wrapper.

### Do not modify

Stage 3.1c should not require changes to:

```text
src/seestar_toolkit/cli.py
```

TIFF-writing code must not be introduced.

Documentation updates and CHANGELOG handling are performed separately from the
Codex implementation step.

## Integration Test Requirements

The integration test must exercise the real path rather than mocking the FITS
reader, inspector or demosaicer.

For the selected real Seestar raw FITS sample, verify:

-   The file can be read through the existing FITS subsystem.
-   The image is identified as raw Bayer data.
-   The raw image array is 2-dimensional.
-   The Bayer pattern is obtained through the existing metadata/inspection
    behaviour.
-   The observed Bayer pattern is `GRBG`, if that is what the selected existing
    fixture contains.
-   The image array and Bayer pattern can be passed directly to `demosaic()`.
-   The result is a NumPy array.
-   The result has shape `(height, width, 3)`, derived from the source image
    dimensions rather than hard-coded unnecessarily.
-   The result has dtype `uint16` for the existing Seestar `uint16` fixture.
-   The RGB result contains three channels.
-   Demosaicing completes without modifying the source file.

## Image-Content Validation

Stage 3.1b already provides deterministic unit tests for exact Bayer mapping,
RGB ordering and interpolation behaviour.

Stage 3.1c therefore does not need to prove the OpenCV interpolation algorithm
again using exact real-image pixel values.

The real FITS integration test should nevertheless include a modest sanity
check that the output contains image data and is not an empty or structurally
invalid result.

Avoid brittle assertions based on specific astronomical pixel values unless
there is a clear reason to require them.

Do not judge image quality by visual inspection as part of the automated test.

## Data Type and Linearity

The integration path must preserve the Stage 3 requirements:

```text
raw uint16 Bayer FITS data → uint16 RGB image data
```

Do not:

-   Convert to 8-bit.
-   Normalise.
-   Stretch.
-   Apply gamma correction.
-   Apply white balance.
-   Apply colour enhancement.
-   Apply display scaling.

No processing should be introduced solely to make the image look better.

## Source File Preservation

The integration test must operate read-only with respect to the source FITS
fixture.

It must not rewrite, update or otherwise alter the original FITS file.

If practical within the existing test style, verify source-file preservation
without introducing unnecessary complexity.

## Existing Tests

All Stage 1, Stage 2, Stage 3.1a and Stage 3.1b tests must continue to pass.

Stage 3.1c must not weaken or remove existing unit-test coverage.

If the real FITS integration exposes a genuine defect in an existing API,
fix the smallest appropriate production area and add focused regression
coverage.

## Explicit Exclusions

Stage 3.1c does **not** implement or test:

-   TIFF writing.
-   CLI conversion commands.
-   Batch processing.
-   Directory processing.
-   Image stretching.
-   Gamma correction.
-   White balance.
-   Colour correction or enhancement.
-   Noise reduction.
-   Sharpening.
-   Alternative demosaicing algorithms.
-   Visual image-quality assessment.
-   RGB FITS processing.
-   Stacked FITS processing.
-   Mosaic-specific processing behaviour.
-   Archive organisation.

These behaviours belong to later stages.

## Acceptance Criteria

Stage 3.1c is complete when:

1.  A real existing Seestar raw Bayer FITS fixture is used by an integration
    test.
2.  The FITS file is read through the existing FITS subsystem.
3.  The image is confirmed as raw Bayer data.
4.  The Bayer pattern is obtained through the existing FITS metadata path.
5.  The raw image and Bayer pattern are passed to the existing `demosaic()`
    interface.
6.  Demosaicing succeeds without a manual Bayer-pattern override in the test
    workflow.
7.  The resulting image has shape `(height, width, 3)`.
8.  The resulting image is RGB and contains three channels.
9.  `uint16` source data produces `uint16` RGB output.
10. The result passes a basic non-empty image-data sanity check.
11. The source FITS fixture is not modified.
12. No unnecessary production abstraction is introduced.
13. All existing tests continue to pass.
14. `ruff check .` reports no new problems.
15. Stage 3.1c files pass the applicable Ruff formatting check.

## Validation

Codex must run the project's normal validation commands after implementation.

At minimum:

```bash
pytest
ruff check .
```

Also run the applicable Ruff formatting check for files changed in Stage 3.1c.

Run the Stage 3.1c integration test separately as well so its result is clearly
reported.

If repository-wide formatting validation reports only known pre-existing
formatting problems outside this stage, do not modify unrelated files.

## Codex Report

When finished, Codex must report:

1.  Files created or modified.
2.  The real Seestar FITS fixture used.
3.  The existing FITS APIs used to read and inspect it.
4.  The Bayer pattern obtained from the fixture.
5.  Whether any production code changes were required.
6.  A concise summary of the integration test.
7.  Focused Stage 3.1c integration-test result.
8.  Full pytest result summary.
9.  Ruff result summary.
10. Formatting-check result.
11. Any assumptions, warnings or issues encountered.
12. Current `git status --short`.

Do not commit any changes.

## Stage Boundary

Completion of Stage 3.1c demonstrates that the existing FITS subsystem and
Bayer demosaicing subsystem work together correctly on real Seestar raw FITS
data.

It does not yet establish TIFF export, CLI conversion workflow or processing
of already-RGB FITS images.
