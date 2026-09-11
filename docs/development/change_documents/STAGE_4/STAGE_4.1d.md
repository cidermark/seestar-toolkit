# Stage 4.1d — Validate Siril stacked FITS

## Purpose

Validate the Stage 4 RGB processing path against real Siril-produced stacked FITS files.

Stage 4.1b implemented the common RGB layout-normalization boundary:

```text
(3, height, width) -> (height, width, 3)
```

Stage 4.1c then validated real Seestar standard and mosaic stacked FITS through that path.

Stage 4.1d must now prove that real Siril standard and mosaic stacked FITS also pass through the existing FITS reader and the same RGB normalization function correctly, without Siril-specific or mosaic-specific processing.

This is primarily a validation and integration-test stage.

## Authoritative real fixtures

Use the existing real Siril fixtures:

```text
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

Do not rename, regenerate, resave, rewrite, or otherwise modify these files.

## Established reconnaissance evidence

### `siril_stacked.fit`

- primary HDU
- NumPy shape `(3, 1920, 1080)`
- toolkit dimensions `1080 x 1920`
- big-endian `float32`
- `BITPIX=-32`
- `BSCALE=1.0`
- `BZERO=0.0`
- observed numerical range within `[0, 1]`
- toolkit classification RGB / `RGB_IMAGE`
- no `BAYERPAT`
- `PROGRAM=Siril 1.4.0-beta3`
- `ROWORDER=BOTTOM-UP`
- history includes normalized/equalized stacking and a TOP-DOWN mirror

### `siril_stacked_mosaic.fit`

- primary HDU
- NumPy shape `(3, 5437, 4183)`
- toolkit dimensions `4183 x 5437`
- big-endian `float32`
- `BITPIX=-32`
- `BSCALE=1.0`
- `BZERO=0.0`
- observed numerical range within `[0, 1]`
- toolkit classification RGB / `RGB_IMAGE`
- no `BAYERPAT`
- `PROGRAM=Siril 1.4.4`
- plate-solved TAN WCS
- no equivalent ROWORDER/mirror-history evidence
- no `MOSAIC` keyword

The observed `[0, 1]` range is fixture evidence only. It must not become a universal Stage 4 rule for all floating-point FITS.

## Stage 4.1d objective

Validate the existing Siril RGB handoff:

```text
real Siril stacked FITS
        ↓
existing FITS reader / inspection
        ↓
channels-first RGB `(3, H, W)` float32
        ↓
normalize_rgb_layout()
        ↓
channels-last RGB `(H, W, 3)` float32
```

No new image-processing behaviour should be required.

## Required validation

For both real Siril fixtures, verify as appropriate through existing public APIs:

1. The FITS file is successfully read.
2. The toolkit identifies the image as RGB.
3. The image classification is `RGB_IMAGE`.
4. The reader returns a three-dimensional channels-first array.
5. The first axis contains exactly three RGB channels.
6. The source dtype remains `float32`.
7. The expected source dimensions are retained.
8. `normalize_rgb_layout()` accepts the reader output.
9. The normalized shape is `(H, W, 3)`.
10. The normalized dtype remains `float32`.
11. RGB channel ordering is preserved.
12. Representative numerical values are preserved exactly.
13. No value normalization, scaling, clipping, or quantization occurs.
14. No float-to-`uint16` conversion occurs.
15. No Siril-specific processing branch is required.
16. Standard and mosaic Siril stacks use the same RGB handling path.
17. No `MOSAIC` keyword or mosaic-specific branch is required.

## Test design

Inspect the existing Stage 4 integration coverage before adding or changing tests.

Stage 4.1a/4.1b already exercised the Siril fixtures as part of the general RGB contract. Stage 4.1d should add value by explicitly validating the **real Siril stacked-FITS workflow as a coherent integration path**, just as Stage 4.1c did for Seestar.

Prefer strengthening or reorganizing the existing integration test rather than creating redundant tests or loading the very large Siril mosaic fixture repeatedly.

A focused parameterized Siril integration test may cover:

```text
siril_stacked.fit
siril_stacked_mosaic.fit
```

Use the real production APIs:
- existing FITS reader;
- existing inspection/classification API where needed;
- `normalize_rgb_layout()`.

Do not reproduce production normalization logic in the test.

For representative value preservation, make channel mapping explicit:

```text
source[0, y, x] == normalized[y, x, 0]
source[1, y, x] == normalized[y, x, 1]
source[2, y, x] == normalized[y, x, 2]
```

Use coordinates valid for each fixture.

Do not add tests solely to increase test counts.

## Float handling contract

Stage 4 must preserve Siril floating-point data as floating-point data.

For these fixtures:
- `float32` must remain `float32`;
- numerical values must remain unchanged;
- no clipping to `[0, 1]`;
- no assumption that `[0, 1]` is universally valid;
- no conversion to integer;
- no rescaling to TIFF range.

Any float-to-`uint16` policy belongs to Stage 5.

Byte order is not a public Stage 4 contract. Preserve numerical values and dtype precision/class; do not add endianness-specific API behavior unless a genuine defect is discovered.

## Producer metadata

Siril-generated FITS may retain:

```text
CREATOR=ZWO Seestar S50
PRODUCER=ZWO
```

from the source data while identifying the processing application through `PROGRAM` and history.

Stage 4.1d must not introduce producer-specific branching based on these metadata fields.

The RGB path is determined by image structure/classification, not by attempting to infer producer-specific processing rules.

## Standard versus mosaic

The standard and mosaic Siril fixtures differ substantially in dimensions, WCS, metadata and processing history, but share the same relevant Stage 4 representation:

```text
(3, H, W), float32, RGB
```

Do not introduce:
- mosaic detection;
- mosaic-specific RGB normalization;
- special handling based on dimensions;
- special handling based on plate solving;
- special handling based on WCS;
- special handling based on PROGRAM version;
- special handling based on object metadata.

## Orientation

Orientation remains explicitly outside this stage.

Relevant evidence is intentionally inconsistent:
- standard Siril stack has `ROWORDER=BOTTOM-UP`;
- its history records a TOP-DOWN mirror;
- mosaic Siril stack lacks equivalent mirror evidence;
- mosaic stack is plate solved with rotated TAN WCS.

This evidence does not establish a safe universal orientation rule.

Do not implement:
- mirroring;
- flipping;
- rotation;
- ROWORDER interpretation;
- WCS-based orientation correction;
- reprojection.

Record orientation as deferred if documentation requires it.

## Production code

No production-code change is expected.

If validation exposes a genuine defect in the FITS reader, inspector, or `normalize_rgb_layout()`, stop and report it before broadening scope.

Do not silently redesign, refactor, normalize, cast, or clip production data.

## Explicit exclusions

Do not implement:

- TIFF writing;
- float-to-`uint16` conversion;
- value normalization;
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
- producer detection logic;
- Siril-specific processing;
- mosaic-specific processing;
- registration;
- plate solving;
- mosaic stitching;
- orientation correction;
- mirroring;
- WCS reprojection;
- CLI conversion;
- batch processing;
- archive organisation.

Do not begin Stage 4.1e or Stage 5.

## Fixture preservation

Before and after work, ensure both Siril fixtures remain unchanged.

If hashes are calculated, include them in the completion report.

Tracked test-data files must remain unmodified.

## Documentation

Update `docs/PROJECT_Notes.md` only as necessary to record:

- Stage 4.1d validation;
- successful real Siril standard-stack normalization;
- successful real Siril mosaic-stack normalization;
- preservation of `float32`;
- preservation of numerical values;
- no Siril-specific RGB path required;
- no mosaic-specific RGB path required;
- observed `[0, 1]` range remains fixture evidence rather than a universal rule;
- orientation remains deferred.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if Stage 4.1d produces new factual evidence not already represented.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user will add the Stage 4.1d CHANGELOG entry after the commit ID is known.

## Validation commands

Run the focused Stage 4.1d integration tests.

Then run:

```bash
pytest
ruff check .
git diff --check
```

If Python files are changed, run the applicable Ruff formatting check.

If no Python files are changed, report formatting as not applicable.

## Acceptance criteria

Stage 4.1d is complete when:

1. `siril_stacked.fit` is validated through the real Stage 4 RGB path.
2. `siril_stacked_mosaic.fit` is validated through the same path.
3. Both are classified as RGB / `RGB_IMAGE`.
4. Both enter normalization as `(3, H, W)`.
5. Both normalize to `(H, W, 3)`.
6. Both remain `float32`.
7. RGB channel order is preserved.
8. Representative numerical values are preserved exactly.
9. No value normalization, clipping, quantization, or integer conversion occurs.
10. No universal `[0, 1]` assumption is introduced.
11. No Siril-specific handling is required.
12. No mosaic-specific handling is required.
13. No orientation correction is introduced.
14. No production-code change is required unless a genuine existing defect is explicitly discovered.
15. Real fixtures remain unchanged.
16. Focused tests pass.
17. Full pytest passes.
18. Ruff passes.
19. Formatting checks pass or are correctly reported not applicable.
20. `git diff --check` passes.
21. No Stage 4.1e or Stage 5 work is performed.

## Codex completion report

At completion, report:

1. Whether Stage 4.1d can be closed.
2. Files created or modified.
3. Whether any production code changed.
4. Integration-test coverage added or changed.
5. Results for `siril_stacked.fit`.
6. Results for `siril_stacked_mosaic.fit`.
7. Float32 preservation result.
8. Numerical-value preservation result.
9. Confirmation no universal `[0, 1]` rule was introduced.
10. Confirmation no Siril-specific RGB path is required.
11. Confirmation no mosaic-specific RGB path is required.
12. Orientation status.
13. Stage 4.1d-focused test result.
14. Full pytest result.
15. Ruff result.
16. Formatting result or not-applicable status.
17. `git diff --check` result.
18. Fixture-preservation result.
19. Documentation changes.
20. Any remaining Stage 4.1d blockers or open questions.
21. Current `git status --short`.

Do not commit changes.

## Stage boundary

Successful completion of Stage 4.1d validates real Siril-produced RGB stacks through the same Stage 4 normalization boundary already proven for Seestar RGB stacks.

Do not proceed to Stage 4.1e or Stage 5 during this stage.
