# Stage 3.1a — Bayer Demosaicing Foundation

## Purpose

Establish the package structure, public interface, validation behaviour and
unit-test foundation for Bayer demosaicing.

This stage defines the contract for converting a raw 2-dimensional Bayer
image into a 3-dimensional RGB image.

The actual Bayer interpolation algorithm is **not** implemented as part of
Stage 3.1a.

## Scope

Stage 3.1a introduces a new image-processing package that is independent of
the FITS subsystem.

The demosaicing layer will receive:

-   A 2-dimensional NumPy array containing raw Bayer image data.
-   A Bayer pattern supplied explicitly by the caller.

It will return:

-   A 3-dimensional NumPy RGB array.
-   Array shape `(height, width, 3)`.
-   `uint16` image data when supplied with `uint16` Bayer data.

The interface must support the four standard Bayer patterns:

-   `RGGB`
-   `GRBG`
-   `GBRG`
-   `BGGR`

Current Seestar S50 raw FITS samples use `GRBG`, but the demosaicing layer
must not be restricted specifically to that pattern.

## Architecture

Image-processing functionality will be kept separate from FITS reading and
metadata inspection.

The new package will be:

```text
src/seestar_toolkit/imaging/
```

The initial public demosaicing implementation will reside in:

```text
src/seestar_toolkit/imaging/demosaic.py
```

The FITS subsystem remains responsible for reading FITS data and identifying
metadata such as the Bayer pattern.

The imaging subsystem must not independently inspect FITS headers or infer
the Bayer pattern from FITS metadata.

## Files

### Create

```text
src/seestar_toolkit/imaging/__init__.py
src/seestar_toolkit/imaging/demosaic.py
tests/unit/imaging/__init__.py
tests/unit/imaging/test_demosaic.py
```

### Modify

No existing source or test files should require modification for Stage 3.1a.

Documentation updates and CHANGELOG handling are performed separately from
the Codex implementation step.

## Public Interface

Stage 3.1a establishes a public function conceptually equivalent to:

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

The RGB channel order is:

```text
R, G, B
```

## Input Validation

The demosaicing interface must reject unsupported input rather than silently
guessing how it should be interpreted.

### Bayer Pattern

The following Bayer patterns are valid:

```text
RGGB
GRBG
GBRG
BGGR
```

Any other Bayer pattern must raise an appropriate exception.

The implementation should use a clear exception type and error message that
can be tested reliably.

### Image Dimensionality

The input Bayer image must be 2-dimensional.

Inputs with any other dimensionality must raise an appropriate exception.

The demosaicing layer must not silently reshape or reinterpret unsupported
image layouts.

## Data Type

The current Seestar raw FITS samples contain 16-bit integer Bayer data.

Stage 3.1a therefore establishes that:

```text
uint16 input → uint16 output
```

No conversion to 8-bit image data is permitted.

No normalisation or scaling of pixel values is required by this stage.

## Stage 3.1a Placeholder Behaviour

Stage 3.1a establishes the demosaicing interface but does not implement the
real Bayer interpolation algorithm.

A minimal placeholder RGB result may therefore be used to satisfy the
interface and structural tests.

The placeholder must not be treated as scientifically or visually correct
demosaicing.

Actual Bayer interpolation and pixel-value validation belong to a subsequent
Stage 3 implementation step.

## Unit Tests

Create:

```text
tests/unit/imaging/test_demosaic.py
```

Tests must establish that:

-   `demosaic()` can be imported from
    `seestar_toolkit.imaging.demosaic`.
-   A valid 2-dimensional Bayer array is accepted.
-   `RGGB` is accepted.
-   `GRBG` is accepted.
-   `GBRG` is accepted.
-   `BGGR` is accepted.
-   An unsupported Bayer pattern is rejected.
-   Non-2-dimensional input is rejected.
-   Output shape is `(height, width, 3)`.
-   `uint16` input produces `uint16` output.

Tests must not attempt to validate Bayer interpolation accuracy during
Stage 3.1a.

## Explicit Exclusions

Stage 3.1a does **not** implement or test:

-   Real Bayer interpolation.
-   Demosaicing quality.
-   Individual RGB pixel-value correctness.
-   FITS integration.
-   FITS header processing.
-   Automatic Bayer-pattern detection.
-   Image stretching.
-   Gamma correction.
-   White balance.
-   Colour correction or enhancement.
-   TIFF writing.
-   CLI integration.
-   Batch processing.

These behaviours belong to later development stages.

## Acceptance Criteria

Stage 3.1a is complete when:

1.  The `seestar_toolkit.imaging` package exists.
2.  The public `demosaic()` interface exists.
3.  All four supported Bayer patterns are accepted.
4.  Unsupported Bayer patterns are rejected.
5.  Non-2-dimensional image data is rejected.
6.  Valid input produces an RGB array with shape `(height, width, 3)`.
7.  `uint16` data is preserved through the interface.
8.  Unit tests covering the Stage 3.1a contract pass.
9.  The complete existing test suite continues to pass.
10. Ruff reports no new linting or formatting problems.

## Validation

Codex must run the project's normal validation commands after implementation.

At minimum:

```bash
pytest
ruff check .
```

If the project currently uses an additional Ruff formatting check, that
existing validation should also be run.

The Codex result returned for review should include:

-   Files created or modified.
-   Summary of the implementation.
-   Test results.
-   Ruff results.
-   Any assumptions or issues encountered.

## Stage Boundary

Completion of Stage 3.1a establishes only the demosaicing foundation.

The next Stage 3 step will implement and test actual Bayer-to-RGB
interpolation while preserving the linear 16-bit processing requirements.