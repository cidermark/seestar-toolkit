# Stage 4.1c — Validate real Seestar stacked FITS

## Purpose

Validate the Stage 4 RGB processing path against real Seestar-produced stacked FITS files.

Stage 4.1b implemented the RGB layout-normalization boundary:

```text
(3, height, width) -> (height, width, 3)
```

Stage 4.1c must prove that real Seestar standard and mosaic stacked FITS pass through the existing FITS subsystem and `normalize_rgb_layout()` correctly, without Seestar-specific or mosaic-specific processing.

This is primarily a validation and integration-test stage.

## Authoritative fixtures

Use:

```text
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
```

Do not rename, regenerate, resave, rewrite, or otherwise modify them.

## Established evidence

`stacked.fit`:
- primary HDU
- NumPy shape `(3, 3840, 2160)`
- toolkit dimensions `2160 x 3840`
- `uint16` after Astropy FITS scaling
- `BITPIX=16`, `BSCALE=1`, `BZERO=32768`
- already RGB despite retaining `BAYERPAT=GRBG`
- toolkit classification RGB / `RGB_IMAGE`

`stacked_mosaic.fit`:
- primary HDU
- NumPy shape `(3, 2304, 1296)`
- toolkit dimensions `1296 x 2304`
- `uint16` after Astropy FITS scaling
- `BITPIX=16`, `BSCALE=1`, `BZERO=32768`
- already RGB despite retaining `BAYERPAT=GRBG`
- toolkit classification RGB / `RGB_IMAGE`
- no `MOSAIC` keyword

## Objective

Validate this complete existing handoff:

```text
real Seestar stacked FITS
        ↓
existing FITS reader / inspection
        ↓
channels-first RGB `(3, H, W)` uint16
        ↓
normalize_rgb_layout()
        ↓
channels-last RGB `(H, W, 3)` uint16
```

No new image-processing behaviour should be required.

## Required validation

For both fixtures verify, using existing public APIs where appropriate:

1. FITS is successfully read.
2. Toolkit identifies it as RGB rather than raw Bayer.
3. Classification is `RGB_IMAGE`.
4. Reader returns 3D channels-first data.
5. First axis contains exactly three channels.
6. Source dtype is `uint16`.
7. Expected source dimensions are retained.
8. `normalize_rgb_layout()` accepts the reader output.
9. Output shape is `(H, W, 3)`.
10. Output dtype remains `uint16`.
11. RGB channel order is preserved.
12. Representative numerical pixel values are preserved exactly.
13. No demosaicing is applied.
14. Retained `BAYERPAT=GRBG` does not cause treatment as raw Bayer.
15. Standard and mosaic stacks use the same RGB handling path.
16. No `MOSAIC` keyword or mosaic-specific branch is required.

## Test design

Inspect existing Stage 2 RGB tests and Stage 4.1a/4.1b tests before adding coverage.

Avoid duplicating assertions already strongly protected unless needed to demonstrate the Stage 4.1c end-to-end Seestar handoff.

Prefer one focused parameterized integration test covering both fixtures and using the real production APIs:
- existing FITS reader;
- existing inspection/classification API where needed;
- `normalize_rgb_layout()`.

Do not reproduce normalization logic inside the test.

Make channel mapping explicit at representative coordinates:

```text
source[0, y, x] == normalized[y, x, 0]
source[1, y, x] == normalized[y, x, 1]
source[2, y, x] == normalized[y, x, 2]
```

If the existing Stage 4 integration test already satisfies the criteria, prefer strengthening or clarifying it instead of creating redundant tests. Do not add tests merely to increase test counts.

## Production code

No production-code change is expected.

If validation exposes a genuine defect in Stage 4.1b or the Stage 2 FITS classification path, stop and report it before broadening scope. Do not silently redesign or refactor production code.

Do not modify the FITS reader.

## Important Seestar behaviour

A Seestar stacked FITS can retain `BAYERPAT=GRBG` even though the stored image is already three-channel RGB.

Therefore dimensional/layout classification takes precedence over the mere presence of `BAYERPAT`. Stage 4 must not demosaic these files or allow retained Bayer metadata to trigger a second demosaic operation.

Protect this behaviour where it can be done cleanly through existing APIs.

## Standard versus mosaic

The fixtures differ in dimensions, metadata, stack count, WCS and content, but share the same relevant Stage 4 representation:

```text
(3, H, W), uint16, RGB
```

Do not introduce mosaic detection, mosaic-specific normalization, dimension-specific handling, WCS-specific handling, or object-metadata-specific handling.

## Orientation

Do not implement or infer orientation correction. No mirroring, flipping, rotating, WCS reprojection, or ROWORDER handling belongs in this stage.

## Explicit exclusions

Do not implement:
- TIFF writing;
- float-to-`uint16` conversion;
- Siril-specific processing;
- Bayer demosaicing changes;
- normalization or clipping;
- stretching or gamma;
- white balance or RGB equalisation;
- colour enhancement;
- denoising or sharpening;
- producer-specific processing;
- mosaic-specific processing;
- registration, plate solving, or mosaic stitching;
- orientation correction or mirroring;
- WCS reprojection;
- CLI conversion;
- batch processing;
- archive organisation.

Do not begin Stage 4.1d or Stage 5.

## Fixture preservation

Ensure both real fixtures remain unchanged. If hashes are recorded, include them in the completion report.

## Documentation

Update `docs/PROJECT_Notes.md` only as necessary to record:
- Stage 4.1c validation;
- successful standard-stack normalization;
- successful mosaic-stack normalization;
- retained `BAYERPAT` does not cause RGB stacks to be demosaiced;
- no mosaic-specific Stage 4 path is required.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if Stage 4.1c produces new factual evidence not already represented there.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user will add the Stage 4.1c entry after the commit ID is known.

## Validation

Run focused Stage 4.1c tests, then:

```bash
pytest
ruff check .
git diff --check
```

If Python files change, run the applicable Ruff formatting check. Otherwise report formatting as not applicable.

## Acceptance criteria

Stage 4.1c is complete when:

1. Both Seestar fixtures are validated through the real Stage 4 path.
2. Both are classified RGB / `RGB_IMAGE`.
3. Both enter normalization as `(3, H, W)`.
4. Both normalize to `(H, W, 3)`.
5. Both remain `uint16`.
6. RGB order and representative values are preserved exactly.
7. Retained `BAYERPAT=GRBG` does not cause demosaicing.
8. No mosaic-specific handling is required.
9. No production change is required unless a genuine defect is explicitly discovered.
10. Fixtures remain unchanged.
11. Focused and full tests pass.
12. Ruff passes.
13. Formatting passes or is not applicable.
14. `git diff --check` passes.
15. No Stage 4.1d or Stage 5 work occurs.

## Codex completion report

Report:

1. Whether Stage 4.1c can be closed.
2. Files created or modified.
3. Whether production code changed.
4. Integration-test coverage added or changed.
5. Results for `stacked.fit`.
6. Results for `stacked_mosaic.fit`.
7. Confirmation of retained `BAYERPAT` behaviour.
8. Confirmation no mosaic-specific RGB path is required.
9. Focused test result.
10. Full pytest result.
11. Ruff result.
12. Formatting result/status.
13. `git diff --check` result.
14. Fixture-preservation result.
15. Documentation changes.
16. Remaining blockers/open questions.
17. Current `git status --short`.

Do not commit.

## Stage boundary

Successful completion validates real Seestar-produced RGB stacks through the Stage 4 normalization boundary.

Do not proceed to Stage 4.1d or Stage 5.
