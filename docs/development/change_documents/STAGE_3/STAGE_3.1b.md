# Stage 3.1b — Genuine Bayer Interpolation

## Purpose

Replace the Stage 3.1a placeholder Bayer handling with genuine Bayer-to-RGB
interpolation while preserving the public interface and validation behaviour
already established.

Stage 3.1b introduces real demosaicing using OpenCV and verifies that all four
supported Bayer layouts produce correctly ordered RGB output.

## Scope

Stage 3.1b modifies the existing demosaicing implementation so that raw
2-dimensional Bayer data is converted into a genuine 3-dimensional RGB image.

The demosaicing layer continues to receive:

-   A 2-dimensional NumPy Bayer image array.
-   A Bayer pattern supplied explicitly by the caller.

It will return:

-   A 3-dimensional NumPy RGB array.
-   Array shape `(height, width, 3)`.
-   RGB channel order `(R, G, B)`.
-   `uint16` output when supplied with `uint16` Bayer data.

Supported Bayer patterns remain:

-   `RGGB`
-   `GRBG`
-   `GBRG`
-   `BGGR`

Current Seestar S50 raw FITS samples use `GRBG`, but the implementation must
remain pattern-independent.

## Architecture

The demosaicing implementation remains in:

```text
src/seestar_toolkit/imaging/demosaic.py
```

The FITS subsystem remains responsible for reading FITS data and identifying
metadata such as the Bayer pattern.

The imaging subsystem must not inspect FITS headers or infer the Bayer pattern
from FITS metadata.

Stage 3.1b must preserve the separation between FITS handling and image
processing established in Stage 3.1a.

## Implementation Approach

Use OpenCV Bayer conversion through `cv2.cvtColor()`.

The implementation must map each supported Bayer pattern to the correct
OpenCV Bayer-to-RGB conversion constant.

The mapping must be verified by tests rather than assumed from the OpenCV
constant names.

The implementation must return RGB output, not BGR output.

OpenCV 5.0.0 is installed in the current development environment and should be
used for Stage 3.1b validation.

## Dependency Handling

Verify whether OpenCV is already declared as a project dependency in:

```text
pyproject.toml
```

If OpenCV is already declared appropriately, do not change the dependency
configuration.

If OpenCV is not declared, add the appropriate OpenCV dependency required by
the project.

Do not pin the dependency specifically to version `5.0.0` unless the existing
project dependency policy requires exact version pinning.

Any dependency change must be limited to what is required to make OpenCV an
explicit project dependency.

## Files

### Modify

```text
src/seestar_toolkit/imaging/demosaic.py
tests/unit/imaging/test_demosaic.py
```

### Conditionally Modify

```text
pyproject.toml
```

Modify `pyproject.toml` only if OpenCV is not already declared appropriately.

### Create

No new source or test package files are required for Stage 3.1b.

Documentation updates and CHANGELOG handling are performed separately from the
Codex implementation step.

## Public Interface

Preserve the Stage 3.1a public interface:

```python
demosaic(image, bayer_pattern)
```

The function accepts:

-   `image` — a 2-dimensional NumPy Bayer image array.
-   `bayer_pattern` — the Bayer layout associated with that image.

The result must be a NumPy RGB array with shape:

```text
(height, width, 3)
```

The channel order must be:

```text
R, G, B
```

Do not change the function name or established calling convention without a
specific reason discovered during implementation.

## Bayer Pattern Support

The implementation must support:

```text
RGGB
GRBG
GBRG
BGGR
```

Each pattern must map to the correct OpenCV conversion behaviour.

Existing Stage 3.1a validation for unsupported Bayer patterns must continue to
work.

## Image Validation

Existing Stage 3.1a validation must be preserved.

The input image must be 2-dimensional.

Inputs with unsupported dimensionality must continue to raise the existing
clear, testable exception.

The demosaicing layer must not silently reshape or reinterpret unsupported
image layouts.

## Data Type and Linearity

The current Seestar raw FITS samples contain 16-bit integer Bayer data.

Stage 3.1b must preserve:

```text
uint16 input → uint16 output
```

The implementation must not:

-   Convert image data to 8-bit.
-   Normalise image values.
-   Stretch the image.
-   Apply gamma correction.
-   Apply white balance.
-   Apply colour enhancement.
-   Rescale pixel values for display purposes.

The output must remain suitable for later linear astrophotography processing.

## Removal of Placeholder Behaviour

Stage 3.1a used simple channel replication as a placeholder implementation.

Stage 3.1b must remove that placeholder behaviour and replace it with genuine
Bayer interpolation.

The implementation must not retain channel replication as a fallback for valid
supported Bayer input.

## Unit Tests

Update:

```text
tests/unit/imaging/test_demosaic.py
```

Preserve the existing Stage 3.1a contract tests unless a test must be adapted
because genuine interpolation changes only the expected pixel values.

Add deterministic tests that verify the actual Bayer-to-RGB behaviour.

Tests must cover:

-   Genuine interpolation rather than channel replication.
-   `RGGB` mapping.
-   `GRBG` mapping.
-   `GBRG` mapping.
-   `BGGR` mapping.
-   Correct RGB channel ordering.
-   `(height, width, 3)` output shape.
-   `uint16` preservation.
-   Existing unsupported Bayer-pattern validation.
-   Existing non-2-dimensional input validation.

## Synthetic Test Data

Use small deterministic synthetic Bayer arrays for the new interpolation
tests.

The tests should be designed so that the expected red, green and blue
orientation is unambiguous.

Prefer synthetic data with clearly separated channel values so that an
incorrect Bayer mapping or accidental BGR/RGB reversal will cause the test to
fail reliably.

Tests must not depend on visual inspection.

Tests must not require real FITS files during Stage 3.1b.

Because interpolation modifies neighbouring pixel values, tests should avoid
fragile assumptions about edge pixels where possible. Validate representative
interior pixels or regions where the expected channel behaviour is
deterministic.

## OpenCV Mapping Verification

OpenCV Bayer conversion constant names can be easy to misinterpret when RGB
and BGR output conventions are involved.

Codex must therefore verify the actual behaviour of the selected conversion
constants against the synthetic tests.

Do not select constants solely from their names without validating the
resulting channel order.

The tests should protect against future accidental changes to the mapping.

## Explicit Exclusions

Stage 3.1b does **not** implement or test:

-   FITS-to-demosaicer integration.
-   FITS header processing.
-   Automatic Bayer-pattern detection.
-   Real Seestar FITS validation.
-   TIFF writing.
-   Image stretching.
-   Gamma correction.
-   White balance.
-   Colour correction or enhancement.
-   Noise reduction.
-   Sharpening.
-   CLI integration.
-   Batch processing.
-   Alternative demosaicing algorithms.
-   Demosaicing quality comparisons.

These behaviours belong to later development stages.

## Acceptance Criteria

Stage 3.1b is complete when:

1.  The Stage 3.1a placeholder channel replication has been removed.
2.  `demosaic()` performs genuine Bayer interpolation using OpenCV.
3.  `RGGB` is correctly converted to RGB.
4.  `GRBG` is correctly converted to RGB.
5.  `GBRG` is correctly converted to RGB.
6.  `BGGR` is correctly converted to RGB.
7.  Output channel order is verified as `(R, G, B)`.
8.  Output shape remains `(height, width, 3)`.
9.  `uint16` input produces `uint16` output.
10. Existing input-validation behaviour remains intact.
11. Synthetic tests reliably detect incorrect Bayer mapping.
12. Synthetic tests reliably detect RGB/BGR channel reversal.
13. OpenCV is declared appropriately as a project dependency.
14. All Stage 3.1b tests pass.
15. The complete existing test suite continues to pass.
16. `ruff check .` reports no new problems.
17. Stage 3.1b files pass the repository's applicable Ruff formatting check.

## Validation

Codex must run the project's normal validation commands after implementation.

At minimum:

```bash
pytest
ruff check .
```

Run the applicable Ruff formatting validation for the files changed in
Stage 3.1b.

If the repository-wide formatting check continues to report pre-existing
formatting problems outside this stage, do not modify unrelated files merely
to make that check pass. Report the existing condition clearly.

The Codex result returned for review should include:

1.  Files created or modified.
2.  Whether `pyproject.toml` required modification.
3.  The OpenCV Bayer conversion mapping used for all four patterns.
4.  A concise summary of the implementation.
5.  Full pytest result summary.
6.  Focused Stage 3.1b test result summary.
7.  Ruff result summary.
8.  Formatting-check result.
9.  Any assumptions, warnings or issues encountered.
10. Current `git status --short`.

## Stage Boundary

Completion of Stage 3.1b establishes genuine Bayer-to-RGB interpolation in
isolation from FITS handling.

Real Seestar FITS integration and validation remain outside this stage and
should be introduced in a subsequent Stage 3 step.
