# Stage 4.1a — Define RGB image handling contract

## Purpose

Define and validate the Stage 4 RGB image-handling contract using the real RGB
FITS fixtures already present in the repository.

Stage 4.1a establishes the common internal RGB representation and the expected
behaviour for already-RGB FITS images. It must not yet implement the production
layout-normalisation function; that belongs to Stage 4.1b.

## Background

Stage 2 established reader-level recognition of RGB FITS images using
`FitsImageLayout.RGB`.

Stage 3 established `(height, width, 3)` as the toolkit RGB convention for
demosaiced raw Bayer data.

Stage 4 now needs to define how FITS images that are already RGB should enter
that same downstream representation without demosaicing, rescaling, clipping,
or display-oriented processing.

Reconnaissance of the current real RGB fixtures found that all four are stored
as channels-first FITS RGB arrays:

```text
(3, height, width)
```

The fixtures are:

```text
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

Observed structures:

- Seestar standard stack: `(3, 3840, 2160)`, `uint16`
- Seestar mosaic stack: `(3, 2304, 1296)`, `uint16`
- Siril standard stack: `(3, 1920, 1080)`, `float32`
- Siril mosaic stack: `(3, 5437, 4183)`, `float32`

All four are accepted by the existing FITS reader as `FitsImageLayout.RGB`.

The existing reader preserves the original channels-first array shape and the
NumPy values exposed by Astropy. It does not move the channel axis or perform
image-value normalization.

## Stage 4.1a contract

The Stage 4 RGB handling contract is:

1. Already-RGB FITS image data must not be demosaiced.
2. The toolkit common internal RGB representation is `(height, width, 3)`.
3. Supported Stage 4 RGB FITS input is currently the existing reader-supported
   channels-first layout `(3, height, width)`.
4. Stage 4 layout normalization will move the RGB channel axis from first to
   last.
5. Channel order must remain RGB.
6. Pixel numerical values must remain unchanged by layout normalization.
7. Seestar `uint16` RGB input must remain `uint16`.
8. Siril `float32` RGB input must remain `float32`.
9. Stage 4 must preserve numerical precision and dtype class.
10. Byte order is an implementation detail and is not itself part of the
    public Stage 4 contract, provided dtype precision and numerical values are
    preserved.
11. Stage 4 must not deliberately scale, normalize, quantize, clip, stretch,
    gamma-correct, white-balance, equalize, or otherwise alter image values.
12. Standard and mosaic RGB stacks use the same RGB handling path.
13. No producer-specific processing path is currently justified.
14. Unsupported RGB organizations must be rejected explicitly rather than
    guessed or silently rearranged.
15. Stage 4 must remain independent of TIFF-writing policy.

## Mosaic handling

Reconnaissance established that mosaic status does not require a separate core
RGB-processing path.

The observed Seestar standard and mosaic stacks share channels-first RGB
organization and `uint16` data. The observed Siril standard and mosaic stacks
share channels-first RGB organization and `float32` data.

Differences in dimensions, WCS, plate-solving metadata, stack count, target,
or other capture metadata do not alter the Stage 4 RGB layout contract.

No mosaic-specific RGB conversion logic should be introduced.

## Siril handling

Siril-produced stacked FITS images are a first-class Stage 4 use case.

The observed Siril fixtures are channels-first RGB `float32` images. Their
observed values are within `[0, 1]`, but Stage 4 must not assume that every
floating-point FITS image will use this range.

Stage 4 must preserve floating-point values exactly and leave any
float-to-`uint16` conversion policy to the later TIFF-writing stage.

Do not infer producer solely from `CREATOR` or `PRODUCER`, because observed
Siril outputs retain original ZWO values. `PROGRAM` and processing history
provide stronger provenance evidence, but Stage 4 currently requires no
producer-specific branch.

## Orientation findings

Reconnaissance found orientation-related metadata differences:

- `siril_stacked.fit` contains `ROWORDER=BOTTOM-UP`.
- Its history records a `TOP-DOWN` mirror operation.
- `siril_stacked_mosaic.fit` does not contain the same row-order/mirror
  evidence.
- The Siril mosaic fixture is plate-solved and contains rotated TAN WCS.
- The Seestar stacked files contain WCS information.

These findings are insufficient to define safe pixel-orientation correction.

Stage 4.1a therefore explicitly excludes orientation correction. Do not add
`mirrorx`, row reversal, rotation, WCS-based reprojection, or other orientation
transformations.

The existing Siril `mirrorx_single result` difference remains an open
investigation item.

## Stage 4.1a implementation scope

Stage 4.1a is a contract-and-test stage.

Inspect existing RGB-related FITS tests before adding anything.

Add the smallest focused tests necessary to establish the Stage 4 contract
before Stage 4.1b production implementation.

Do not implement the actual Stage 4.1b layout conversion in this stage.

Tests should establish, as appropriate:

- expected channels-first input layout;
- expected future `(height, width, 3)` output contract;
- RGB channel-order preservation;
- `uint16` preservation requirement;
- `float32` preservation requirement;
- unchanged numerical-value requirement;
- same handling expectation for standard and mosaic RGB files;
- no demosaicing requirement for RGB input;
- rejection expectations for unsupported RGB organizations.

Do not over-test metadata already covered adequately by Stage 2.

## Production-code expectation

No substantive production RGB normalization is expected in Stage 4.1a.

If an extremely small API-contract scaffold is necessary to make tests clear,
keep it minimal and do not implement Stage 4.1b layout conversion.

If the existing architecture allows the contract to be defined without
production changes, prefer no production-code changes.

Do not refactor the FITS reader merely to prepare for Stage 4.

## Test fixtures

Use the existing fixtures:

```text
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

Do not rename, regenerate, resave, or alter them.

## Explicit exclusions

Stage 4.1a must not implement:

- RGB axis-normalization production logic;
- Bayer demosaicing;
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
- registration;
- plate solving;
- mosaic stitching;
- orientation correction;
- mirroring;
- WCS reprojection;
- CLI conversion;
- batch processing;
- archive organisation.

## Stage 5 boundary

Stage 4 must retain enough information for Stage 5 to make explicit, testable
TIFF conversion decisions.

Stage 5 will eventually need to account for source dtype, numerical value
range, FITS scaling already applied by Astropy, finite/non-finite floating
values, values outside the destination range, explicit float-to-`uint16`
mapping policy, avoidance of accidental clipping, RGB channel-axis
normalization, memory requirements for large images, and any separately
justified orientation behaviour.

Stage 4.1a must not design or implement that conversion policy.

## Documentation

Update `docs/PROJECT_Notes.md` only as necessary to record:

- Stage 4 has started;
- Stage 4.1a defines the RGB handling contract;
- `(height, width, 3)` is the common toolkit RGB representation;
- Seestar `uint16` and Siril `float32` RGB FITS are both supported Stage 4
  use cases;
- standard and mosaic stacks use the same RGB handling contract;
- orientation correction remains outside Stage 4 pending separate evidence.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if reconnaissance findings are
not already captured accurately.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user
will add the Stage 4.1a CHANGELOG entry after the commit ID is known.

## Validation commands

Run Stage 4.1a-focused tests, then:

```bash
pytest
ruff check .
git diff --check
```

If Python files are changed, run the applicable Ruff formatting check. If no
Python files are changed, report formatting as not applicable.

## Acceptance criteria

Stage 4.1a is complete when:

1. The common RGB representation is explicitly defined as
   `(height, width, 3)`.
2. Existing supported RGB FITS input is explicitly defined as
   `(3, height, width)`.
3. Required channel-axis normalization is specified.
4. RGB channel-order preservation is specified.
5. Pixel-value preservation is specified.
6. Seestar `uint16` preservation is specified.
7. Siril `float32` preservation is specified.
8. Byte order is treated as an implementation detail unless it affects
   numerical fidelity.
9. Standard and mosaic stacks share one handling contract.
10. No producer-specific RGB-processing branch is introduced.
11. Unsupported RGB organizations have an explicit rejection policy.
12. Orientation correction remains outside scope.
13. TIFF conversion remains outside scope.
14. Focused Stage 4.1a contract tests pass.
15. Full pytest passes.
16. Ruff passes.
17. Applicable formatting checks pass.
18. `git diff --check` passes.
19. No fixture is modified.

## Codex completion report

At completion, report:

1. Stage 4.1a contract implemented/documented.
2. Files created or modified.
3. Production-code changes, if any, with justification.
4. New tests added and what contract requirement each protects.
5. Stage 4.1a-focused test result.
6. Full pytest result.
7. Ruff result.
8. Formatting result or not-applicable status.
9. `git diff --check` result.
10. Fixture-preservation result.
11. Documentation changes.
12. Any remaining Stage 4.1a blockers or open questions.
13. Current `git status --short`.

Do not commit changes.

## Stage boundary

Successful completion of Stage 4.1a establishes the RGB image-handling
contract.

Stage 4.1b will implement actual RGB layout normalization from
`(3, height, width)` to `(height, width, 3)`.

Do not begin Stage 4.1b during this stage.
