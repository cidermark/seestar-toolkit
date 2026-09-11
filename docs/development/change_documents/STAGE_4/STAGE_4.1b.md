# Stage 4.1b — Implement RGB layout normalization

## Purpose

Implement the Stage 4 RGB layout-normalization function defined by the
Stage 4.1a contract.

The function must convert supported channels-first RGB image data:

```text
(3, height, width)
```

into the toolkit common RGB representation:

```text
(height, width, 3)
```

while preserving RGB channel order, numerical values, dtype class, and precision.

## Background

Stage 4.1a established the RGB handling contract using real Seestar and Siril
stacked FITS fixtures.

The validated fixture set includes:

```text
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

Observed input types:

- Seestar standard and mosaic stacks: channels-first `uint16`
- Siril standard and mosaic stacks: channels-first `float32`

Stage 4.1a also established that:

- standard and mosaic RGB FITS use one common handling path;
- no producer-specific processing is required;
- orientation correction is outside the Stage 4 RGB layout contract;
- TIFF conversion and float-to-`uint16` mapping belong to Stage 5.

## Stage 4.1b objective

Add a small, explicit RGB layout-normalization API in the imaging layer.

The exact public function name should follow the existing project naming style.
A suggested name is:

```python
normalize_rgb_layout(image)
```

If the existing imaging API structure strongly suggests a clearer name, use it,
but keep the function narrowly focused on layout normalization.

The function contract is:

1. Accept a NumPy RGB array in channels-first form:
   `(3, height, width)`.
2. Return a NumPy RGB array in channels-last form:
   `(height, width, 3)`.
3. Preserve RGB channel ordering exactly.
4. Preserve all numerical values exactly.
5. Preserve `uint16` as `uint16`.
6. Preserve `float32` as `float32`.
7. Preserve dtype precision/class for other supported numeric inputs unless the
   implementation inherently requires a value-preserving native-endian view or
   copy.
8. Do not rescale values.
9. Do not normalize values.
10. Do not clip values.
11. Do not alter orientation.
12. Do not demosaic input.
13. Do not inspect FITS metadata.
14. Do not branch by producer.
15. Do not branch by mosaic status.

## Input validation

Reject unsupported array organizations explicitly.

At minimum, reject:

- non-3-dimensional input;
- 3-dimensional input where the first axis is not exactly length 3.

Do not attempt to guess channels-last input.

If `(height, width, 3)` is passed to this function, it must be rejected rather
than silently returned unchanged or rearranged.

This function represents the specific conversion boundary from FITS
channels-first RGB data into toolkit channels-last RGB data.

## Implementation guidance

Prefer the simplest NumPy operation that clearly moves the RGB channel axis
from index 0 to index 2.

The implementation must not introduce OpenCV or other image-processing
operations for this conversion unless already necessary.

The result may be a view or a copy unless existing project conventions require
one specifically. Do not add unnecessary copying solely for ownership
semantics unless a test or existing design contract requires it.

Do not change the FITS reader in this stage.

The reader should continue returning FITS data in its observed FITS/NumPy
layout. Stage 4.1b introduces the explicit downstream normalization step.

## Tests

Extend the Stage 4 contract tests or add focused unit tests for the production
normalization function.

Tests must protect:

1. `(3, H, W)` becomes `(H, W, 3)`.
2. Channel 0 remains red.
3. Channel 1 remains green.
4. Channel 2 remains blue.
5. Numerical values are unchanged.
6. `uint16` is preserved.
7. `float32` is preserved.
8. Non-3-dimensional inputs are rejected.
9. Three-dimensional inputs whose first axis is not length 3 are rejected.
10. Channels-last `(H, W, 3)` input is rejected explicitly.

Use deterministic synthetic arrays for exact channel/value assertions.

Also add or update integration coverage using the existing real fixtures so
that at minimum one Seestar `uint16` RGB FITS and one Siril `float32` RGB FITS
are read through the existing FITS subsystem and then passed through the new
normalization function.

If the existing Stage 4.1a integration contract test can be evolved cleanly to
exercise the production function without duplicating coverage, prefer that.

Do not unnecessarily load every very large fixture in multiple tests.

## Real-fixture expectations

For real fixture coverage:

- Seestar RGB data must remain `uint16`.
- Siril RGB data must remain `float32`.
- Input shape remains `(3, H, W)` before normalization.
- Output shape becomes `(H, W, 3)`.
- Representative pixel values must be identical before and after axis
  movement.
- No demosaicing occurs.

Standard and mosaic stacks remain covered by the Stage 4.1a contract. Stage
4.1b does not need redundant full integration tests for all four fixtures if
the contract is already protected and focused production tests cover the new
function.

## Production files

The implementation should live in the existing imaging package, not in the
FITS reader.

Likely locations include:

```text
src/seestar_toolkit/imaging/
```

Follow the existing package structure and public-export conventions.

Do not create a new subsystem unless genuinely necessary.

## Explicit exclusions

Stage 4.1b must not implement:

- TIFF writing;
- float-to-`uint16` conversion;
- image-value normalization;
- clipping;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- denoising;
- sharpening;
- Bayer demosaicing changes;
- FITS reader refactoring;
- producer detection;
- mosaic detection;
- mosaic stitching;
- registration;
- plate solving;
- orientation correction;
- mirroring;
- WCS reprojection;
- CLI conversion;
- batch processing;
- archive organisation.

## Documentation

Update `docs/PROJECT_Notes.md` only as necessary to record:

- Stage 4.1b implementation;
- the new RGB layout-normalization function;
- channels-first `(3, H, W)` to channels-last `(H, W, 3)` conversion;
- preservation of RGB order, values, `uint16`, and `float32`;
- no producer- or mosaic-specific branch;
- orientation and TIFF conversion remain deferred.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if implementation evidence
materially changes or clarifies the existing reference.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user
will add the Stage 4.1b CHANGELOG entry after the commit ID is known.

## Validation commands

Run focused Stage 4.1b tests.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting check for changed Python files.

## Acceptance criteria

Stage 4.1b is complete when:

1. A small explicit RGB layout-normalization production API exists.
2. `(3, H, W)` input converts to `(H, W, 3)`.
3. RGB channel order is preserved.
4. Numerical values are preserved exactly.
5. `uint16` is preserved.
6. `float32` is preserved.
7. Unsupported dimensionality is rejected.
8. Unsupported first-axis lengths are rejected.
9. Channels-last input is rejected rather than guessed.
10. At least one real Seestar RGB FITS is validated through the production
    normalization function.
11. At least one real Siril RGB FITS is validated through the production
    normalization function.
12. No FITS-reader refactor is introduced.
13. No producer-specific branch is introduced.
14. No mosaic-specific branch is introduced.
15. No orientation correction is introduced.
16. No TIFF conversion behaviour is introduced.
17. Focused tests pass.
18. Full pytest passes.
19. Ruff passes.
20. Formatting checks pass.
21. `git diff --check` passes.

## Codex completion report

At completion, report:

1. Whether Stage 4.1b can be closed.
2. Public API added.
3. Files created or modified.
4. Production implementation summary.
5. Input-validation behaviour.
6. Unit tests added or changed.
7. Integration tests added or changed.
8. Stage 4.1b-focused test result.
9. Full pytest result.
10. Ruff result.
11. Formatting result.
12. `git diff --check` result.
13. Documentation changes.
14. Any remaining Stage 4.1b blockers or open questions.
15. Current `git status --short`.

Do not commit changes.

## Stage boundary

Successful completion of Stage 4.1b implements the RGB layout-normalization
boundary.

Do not begin Stage 4.1c or Stage 5 work during this stage.
