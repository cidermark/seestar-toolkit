# Stage 5.1a --- Add TIFF writer foundation

## Purpose

Establish the TIFF output subsystem and define the public contract for
writing processed Seestar Toolkit image data as a TIFF.

This is the first implementation stage of Stage 5 --- TIFF output.

Stage 4 is complete.

## Starting point

Stage 4 --- RGB FITS processing/handling --- was completed in commit:

``` text
2b62892
```

Stage 4 hands Stage 5 linear RGB image data in the normalized layout:

``` text
(height, width, 3)
```

Stage 5 now owns TIFF-specific output behaviour.

## Required TIFF writer contract

Provide a public TIFF-writing operation:

``` text
write_tiff(image, path)
```

The writer must accept RGB NumPy image data with:

``` text
shape: (height, width, 3)
dtype: numpy.uint16
```

The resulting file must be a standards-compliant RGB TIFF containing:

``` text
3 samples per pixel
16 bits per sample
RGB photometric interpretation
```

## Numerical preservation

The TIFF writer must preserve the supplied `uint16` pixel values
exactly.

It must not perform:

-   scaling;
-   normalization;
-   clipping;
-   stretching;
-   gamma correction;
-   white balance;
-   RGB equalisation;
-   tone mapping;
-   resampling;
-   implicit dtype conversion.

An image written to TIFF and read back must contain the same pixel
values as the input image.

## Input validation

Reject unsupported image layouts.

This includes:

-   2D arrays;
-   channels-first arrays;
-   single-channel arrays;
-   four-channel arrays;
-   any other layout not matching `(height, width, 3)`.

Reject unsupported dtypes rather than silently converting them.

This includes at least:

-   `uint8`;
-   `int16`;
-   `uint32`;
-   `float32`.

## TIFF exception hierarchy

Provide TIFF-specific toolkit exceptions.

The subsystem must provide:

``` text
TiffError
InvalidTiffImageError
TiffWriteError
```

`TiffError` is the TIFF subsystem base exception.

Invalid image data must raise `InvalidTiffImageError`.

TIFF/file-writing failures must be exposed as `TiffWriteError` rather
than leaking arbitrary underlying library exceptions.

The hierarchy should follow the existing Seestar Toolkit exception
conventions.

## Package structure

Stage 5.1a establishes a dedicated TIFF subsystem:

``` text
src/seestar_toolkit/tiff/
    __init__.py
    exceptions.py
    writer.py
```

The public writer must be exported from:

``` text
seestar_toolkit.tiff
```

Tests belong under:

``` text
tests/unit/tiff/
```

## Explicit exclusions

Do not implement:

-   CLI integration;
-   conversion-pipeline integration;
-   output filename generation;
-   archive organisation;
-   automatic output-directory creation;
-   overwrite policy;
-   TIFF metadata embedding;
-   8-bit TIFF output;
-   float-to-`uint16` conversion;
-   float scaling policy;
-   image stretching;
-   gamma correction;
-   white balance;
-   colour enhancement;
-   orientation correction;
-   batch conversion.

These belong to later Stage 5 work or future development.

## Validation requirements

Tests must verify:

1.  `uint16` RGB images can be written and read back with identical
    pixel values.
2.  TIFF photometric interpretation is RGB.
3.  TIFF output contains three samples per pixel.
4.  TIFF output contains sixteen bits per sample.
5.  Unsupported array layouts are rejected.
6.  Unsupported dtypes are rejected.
7.  TIFF output failures are wrapped in the TIFF exception hierarchy.
8.  TIFF exception inheritance follows project conventions.

Run:

``` bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

## Stage 5.1a closure criteria

Stage 5.1a can be closed only if:

1.  A dedicated TIFF subsystem exists.
2.  `write_tiff(image, path)` is publicly available.
3.  `(H,W,3)` `uint16` RGB input is supported.
4.  Unsupported shapes are rejected.
5.  Unsupported dtypes are rejected.
6.  TIFF output is RGB.
7.  TIFF output contains three samples per pixel.
8.  TIFF output contains sixteen bits per sample.
9.  Pixel values survive an exact TIFF round-trip.
10. No image processing or numerical transformation occurs.
11. TIFF-specific exceptions are established.
12. TIFF writing failures are appropriately wrapped.
13. Focused TIFF tests pass.
14. Full pytest passes.
15. Ruff passes.
16. Formatting validation passes.
17. `git diff --check` passes.
18. No later Stage 5 functionality has been introduced unnecessarily.

## Completion result

Stage 5.1a was successfully completed.

The following files were created:

``` text
src/seestar_toolkit/tiff/__init__.py
src/seestar_toolkit/tiff/exceptions.py
src/seestar_toolkit/tiff/writer.py
tests/unit/tiff/__init__.py
tests/unit/tiff/test_exceptions.py
tests/unit/tiff/test_writer.py
```

Validation results:

``` text
Focused TIFF tests: 11 passed
Full pytest:         69 passed
Ruff:                All checks passed
Formatting:          6 files already formatted
git diff --check:    passed
```

Stage 5.1a was committed as:

``` text
b399cd7 — Add TIFF writer foundation
```

## Stage boundary

Successful completion of Stage 5.1a establishes the basic linear 16-bit
RGB TIFF writer.

Stage 5.1b continues Stage 5 by defining the remaining low-level TIFF
destination-path and file-writing behaviour.
