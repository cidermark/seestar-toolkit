# Stage 3.1e — Validate and close Stage 3

## Purpose

Perform final validation of the Stage 3 Bayer demosaicing implementation and,
if the established contract is fully satisfied, close Stage 3.

Stage 3.1e is primarily a validation and closure stage. It must not introduce
new image-processing functionality merely to create additional work for
Stage 3.

## Stage 3 contract

Stage 3 converts raw 2-dimensional Bayer image data into linear RGB image data.

The established public interface is:

`demosaic(image, bayer_pattern)`

The demosaicing layer:

- accepts a 2-dimensional NumPy Bayer image array;
- receives the Bayer pattern explicitly from its caller;
- supports `RGGB`, `GRBG`, `GBRG`, and `BGGR`;
- performs genuine Bayer interpolation;
- returns RGB data in `(height, width, 3)` form;
- preserves `uint16` image data for Seestar raw inputs;
- remains independent of FITS parsing and FITS metadata access.

## Completed Stage 3 work

### Stage 3.1a

Established the imaging package and public demosaicing interface, validation,
supported Bayer-pattern contract, RGB output shape, and `uint16` preservation.

### Stage 3.1b

Replaced the temporary placeholder with genuine OpenCV Bayer interpolation.

Deterministic synthetic tests verify:

- all four supported Bayer patterns;
- correct conversion mappings;
- genuine interpolation;
- RGB channel ordering;
- protection against accidental RGB/BGR reversal;
- `uint16` preservation.

### Stage 3.1c

Validated the real Seestar raw FITS-to-RGB integration path.

A real Seestar raw Bayer FITS fixture is:

- read through the existing FITS subsystem;
- classified as raw Bayer/raw light;
- inspected for its normalized Bayer pattern;
- passed directly into the public demosaicing API;
- converted to `(height, width, 3)` `uint16` RGB data.

No production integration abstraction was required.

### Stage 3.1d

Validated representative raw FITS files originating from Seestar mosaic
sessions across legacy, intermediate, and newer header variants.

The selected fixtures all use the same existing Bayer-processing path and
require no mosaic-specific demosaicing behaviour.

Stage 3.1d completed with 48 tests passing and Ruff clean.

## Additional reference findings

Review of Seestar Siril preprocessing scripts supports the Stage 3 architecture:

- standard and mosaic-session Seestar lights use the same debayer operation;
- mosaic-specific behaviour appears later during registration/plate solving;
- normalization and RGB equalisation occur later during stacking rather than
  during debayering.

Known Seestar mosaic-session raw FITS samples may contain no `MOSAIC` keyword.
Mosaic-session origin is therefore not part of the Stage 3 demosaicing
contract.

The difference whereby the reviewed standard Siril preprocessing script applies
`mirrorx_single result` while the mosaic script does not remains an open
investigation item. It must not be folded into Stage 3 without separate
evidence that it is a demosaicing responsibility.

## Validation objectives

Review the current Stage 3 implementation and tests against the established
contract.

Confirm that:

1. The public `demosaic(image, bayer_pattern)` interface remains stable.
2. Input validation rejects non-2-dimensional image arrays.
3. Unsupported Bayer patterns are rejected.
4. `RGGB` is supported.
5. `GRBG` is supported.
6. `GBRG` is supported.
7. `BGGR` is supported.
8. Genuine Bayer interpolation is performed.
9. RGB channel ordering is correct.
10. Output shape is `(height, width, 3)`.
11. Seestar `uint16` input remains `uint16` output.
12. Real Seestar raw Bayer FITS integration is covered.
13. Bayer pattern for real FITS data is obtained through the existing FITS
    inspection/metadata path rather than manually overridden.
14. Representative mosaic-session raw FITS/header variants are covered.
15. Mosaic-session frames require no mosaic-specific demosaicing logic.
16. The demosaicing module does not read FITS files or inspect FITS headers.
17. No display-oriented processing has entered the Stage 3 path.

## Test review

Inspect the existing Stage 3 unit and integration tests before changing
anything.

Determine whether the existing tests already provide sufficient regression
coverage for every Stage 3 contract item.

Do not add tests solely to increase the test count.

If a genuine Stage 3 contract gap is found:

- add the smallest focused test needed;
- make a production-code change only if the test exposes a genuine defect;
- explain the gap and the fix clearly.

If no gap exists, no source or test changes are required.

## Production-code expectation

No production-code changes are expected.

The existing implementation has already passed synthetic Bayer-pattern tests,
real Seestar raw FITS integration, and multiple mosaic-session/header variants.

Do not refactor working code during this closure stage unless a concrete
correctness problem is discovered.

## Explicit exclusions

Stage 3.1e must not implement:

- TIFF writing;
- CLI conversion;
- batch processing;
- directory processing;
- RGB FITS processing;
- stacked FITS processing;
- mosaic detection;
- mosaic stitching;
- registration;
- plate solving;
- image orientation correction;
- `mirrorx` behaviour;
- normalization;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- denoising;
- sharpening;
- alternative demosaicing algorithms;
- archive organisation.

Those concerns belong to later stages or separate investigation.

## Documentation review

Check that the current Stage 3 documentation is consistent with the
implementation and test evidence.

In particular, review:

- `docs/PROJECT_Notes.md`
- `docs/SEESTAR_FITS_REFERENCE.md`
- Stage 3 change documents

Do not rewrite documentation unnecessarily.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The
CHANGELOG entry for the Stage 3.1e commit will be added by the user after the
commit ID is known.

If a documentation inconsistency materially prevents Stage 3 closure, report it
and make only the smallest necessary correction.

## Validation commands

Run the Stage 3-focused unit and integration tests separately as appropriate.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting check for files changed during Stage 3.1e.
If no Python files are changed, report that formatting was not applicable
rather than changing files unnecessarily.

Do not modify unrelated files to clean up pre-existing issues.

## Acceptance criteria

Stage 3.1e can close Stage 3 when:

1. Every Stage 3 contract item has existing or newly added regression coverage.
2. All four standard Bayer patterns are validated.
3. RGB channel ordering is validated.
4. Input validation remains correct.
5. Linear `uint16` preservation is validated.
6. Real Seestar raw FITS integration is validated.
7. Representative mosaic-session raw FITS integration is validated.
8. No mosaic-specific demosaicing behaviour is required.
9. FITS handling remains separate from demosaicing.
10. No later-stage image-processing behaviour has leaked into Stage 3.
11. No unresolved correctness issue remains within Stage 3 scope.
12. Full pytest passes.
13. Ruff passes.
14. Applicable formatting checks pass.
15. `git diff --check` passes.

If any acceptance criterion is not satisfied, do not declare Stage 3 complete.
Report the specific blocker.

## Codex completion report

When validation is complete, report:

1. Whether Stage 3 can be closed.
2. Stage 3 contract review, item by item.
3. Any coverage gaps found.
4. Files created or modified during Stage 3.1e.
5. Whether any production-code changes were required.
6. Whether any new tests were required and why.
7. Stage 3-focused test result.
8. Full pytest result.
9. Ruff result.
10. Formatting-check result or not-applicable status.
11. `git diff --check` result.
12. Documentation consistency result.
13. Any remaining Stage 3 warnings or blockers.
14. Current `git status --short`.

Do not commit changes.

## Stage boundary

Successful completion of Stage 3.1e closes Stage 3 — Bayer demosaicing.

The next roadmap stage is Stage 4 — RGB FITS processing/handling.

Stage 3.1e must not begin Stage 4 work.
