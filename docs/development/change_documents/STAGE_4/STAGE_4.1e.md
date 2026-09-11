# Stage 4.1e — Define Stage 4 to Stage 5 handoff requirements

## Purpose

Define and protect the handoff contract between Stage 4 RGB processing and the
future Stage 5 TIFF output stage.

Stage 4 has now established and validated a common RGB image representation for:

- Seestar-produced stacked FITS (`uint16`);
- Siril-produced stacked FITS (`float32`);
- standard stacks;
- mosaic stacks.

Stage 4.1e must formalize exactly what Stage 4 guarantees to Stage 5 and exactly
what Stage 5 remains responsible for deciding and implementing.

This is primarily a contract/documentation/test stage.

No TIFF writer or float-to-integer conversion should be implemented here.

## Established Stage 4 output contract

The common Stage 4 RGB representation is:

```text
(height, width, 3)
```

with channel order:

```text
R, G, B
```

Stage 4 guarantees that:

1. The image is already RGB.
2. The channel axis is last.
3. The channel order is R, G, B.
4. Pixel values are preserved exactly from the Stage 4 source path.
5. No stretch has been applied.
6. No gamma correction has been applied.
7. No white balance has been applied.
8. No RGB equalisation has been applied by the toolkit.
9. No clipping has been applied by the toolkit.
10. No TIFF-range scaling has been applied by the toolkit.
11. No orientation correction has been applied by the toolkit.
12. No producer-specific output representation is used.
13. No mosaic-specific output representation is used.

## Supported Stage 4 handoff data types

### Seestar RGB path

Real Seestar stacked FITS have been validated as:

```text
(height, width, 3), uint16
```

Stage 4 must hand these values to Stage 5 without conversion.

There must be no unnecessary float conversion, rescaling, clipping, or
normalization before Stage 5.

### Siril RGB path

Real Siril stacked FITS have been validated as:

```text
(height, width, 3), float32
```

Stage 4 must hand these values to Stage 5 as `float32`, preserving numerical
values exactly.

The currently validated Siril fixtures happen to contain values within `[0, 1]`,
but this is observed fixture evidence only.

Stage 4 must not define or enforce a universal `[0, 1]` float range.

## Stage 5 responsibilities

Stage 5 will be responsible for deciding and implementing TIFF output behaviour.

Stage 5 must explicitly define:

1. TIFF sample type and bit depth.
2. How Stage 4 `uint16` RGB data maps to TIFF samples.
3. How Stage 4 `float32` RGB data maps to the chosen TIFF representation.
4. Whether float TIFF output is supported or whether Siril `float32` must be
   converted to integer TIFF.
5. If float-to-`uint16` conversion is required:
   - the scaling policy;
   - expected input range;
   - treatment of values below the supported range;
   - treatment of values above the supported range;
   - clipping policy;
   - rounding policy;
   - NaN handling;
   - positive/negative infinity handling.
6. Whether metadata is written to TIFF and, if so, which metadata.
7. TIFF photometric/channel conventions.
8. File-writing ownership and overwrite behaviour.
9. Any validation required before writing.

These decisions must not be silently embedded in Stage 4.

## Linear-data requirement

The project goal is to preserve a linear RGB processing path into TIFF output.

Accordingly, Stage 4 must not perform:

- display stretching;
- nonlinear tone mapping;
- gamma encoding;
- artistic colour enhancement;
- contrast enhancement;
- sharpening;
- denoising.

Stage 5 must also distinguish between a required numeric representation
conversion and a nonlinear display transformation.

If Stage 5 converts a floating-point linear image to an integer linear TIFF,
that conversion must be explicitly specified and tested as a numeric mapping,
not treated as an implicit stretch.

## Dtype and numeric-value contract

The Stage 4 -> Stage 5 boundary must make the following distinction explicit:

```text
Seestar stacked RGB:
    dtype: uint16
    values: already integer image samples
    Stage 4 action: preserve exactly

Siril stacked RGB:
    dtype: float32
    values: linear floating-point image samples
    Stage 4 action: preserve exactly
```

Stage 4 does not attempt to force these two source classes into one common
numeric dtype.

The common representation is structural:

```text
(H, W, 3), RGB
```

not necessarily a common numeric dtype.

## Validation expectations for Stage 4.1e

Stage 4.1e should inspect current tests and documentation and add only the
smallest coverage necessary to protect the handoff contract.

Suitable tests may verify that the existing Stage 4 production path returns:

- channels-last `(H, W, 3)`;
- `uint16` for representative Seestar RGB;
- `float32` for representative Siril RGB;
- unchanged representative pixel values;
- no automatic coercion to a common dtype.

Do not duplicate all Stage 4.1c/4.1d fixture assertions if those tests already
strongly protect the behavior.

If the handoff contract can be protected by a small focused unit or integration
test plus documentation, prefer that.

Do not add tests merely to increase test counts.

## Production code

No production-code change is expected.

If the current Stage 4 code already satisfies the contract, do not add a wrapper
or abstraction merely for Stage 4.1e.

Do not create a TIFF-facing API prematurely unless the existing architecture
clearly requires a minimal boundary object and the need is demonstrated by a
real current gap.

If a genuine gap is discovered, report it before broadening scope.

## Orientation

Orientation remains outside the Stage 4 handoff contract.

Stage 4 hands Stage 5 the RGB pixels in the currently validated toolkit
orientation.

Do not introduce:
- mirroring;
- flipping;
- rotation;
- WCS-based correction;
- ROWORDER handling;
- reprojection.

If orientation later becomes a TIFF-output requirement, it must be separately
specified using evidence rather than inferred here.

## Producer and mosaic independence

The Stage 4 -> Stage 5 handoff must not require Stage 5 to know whether the RGB
array originated from:

- Seestar standard stacking;
- Seestar mosaic stacking;
- Siril standard stacking;
- Siril mosaic stacking.

Stage 5 may need source metadata for output metadata decisions, but the RGB
pixel-processing contract itself must not branch on producer or mosaic status.

## Explicit exclusions

Do not implement:

- TIFF writing;
- TIFF metadata writing;
- float-to-`uint16` conversion;
- float-range normalization;
- clipping;
- NaN/Inf handling implementation;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- denoising;
- sharpening;
- orientation correction;
- mirroring;
- WCS reprojection;
- registration;
- plate solving;
- mosaic stitching;
- producer-specific image processing;
- mosaic-specific image processing;
- CLI conversion;
- batch processing;
- archive organisation.

Do not begin Stage 5.

## Documentation

Update `docs/PROJECT_Notes.md` as necessary to record the finalized Stage 4 ->
Stage 5 handoff contract.

The documentation should clearly state:

- common structural RGB representation `(H, W, 3)`;
- RGB channel order;
- Seestar `uint16` preservation;
- Siril `float32` preservation;
- exact numerical-value preservation;
- no common numeric dtype is imposed by Stage 4;
- observed Siril `[0,1]` values are not a universal contract;
- Stage 5 owns any required float-to-TIFF numeric mapping;
- Stage 5 must explicitly define clipping/range/NaN/Inf/rounding policy if
  integer conversion is required;
- orientation remains deferred;
- producer and mosaic origin do not change the pixel handoff contract.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if Stage 4.1e produces new factual
FITS evidence. Contract clarification alone belongs in project/architecture
documentation rather than the FITS reference.

If `docs/ARCHITECTURE.md` contains the appropriate processing-boundary section,
update it only if doing so materially clarifies the Stage 4 -> Stage 5
responsibility boundary. Keep changes minimal.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user will
add the Stage 4.1e CHANGELOG entry after the commit ID is known.

## Validation commands

Run any focused Stage 4.1e tests.

Then run:

```bash
pytest
ruff check .
git diff --check
```

If Python files are changed, run the applicable Ruff formatting check.

If no Python files are changed, report formatting as not applicable.

## Acceptance criteria

Stage 4.1e is complete when:

1. The Stage 4 -> Stage 5 handoff contract is explicit.
2. Stage 4 output is defined structurally as `(H, W, 3)` RGB.
3. RGB channel order is explicitly R, G, B.
4. Seestar `uint16` handoff is preserved exactly.
5. Siril `float32` handoff is preserved exactly.
6. Stage 4 does not impose a common numeric dtype.
7. Numerical values are preserved through Stage 4.
8. No universal `[0,1]` float assumption is introduced.
9. Stage 5 responsibility for float-to-TIFF mapping is explicit.
10. Any future clipping/range/NaN/Inf/rounding decisions are explicitly assigned
    to Stage 5.
11. Orientation remains outside Stage 4.
12. Producer and mosaic origin do not alter the RGB pixel handoff contract.
13. No TIFF-writing behavior is implemented.
14. No production-code change is required unless a genuine current gap is
    explicitly identified.
15. Focused tests, if added, pass.
16. Full pytest passes.
17. Ruff passes.
18. Formatting checks pass or are correctly reported not applicable.
19. `git diff --check` passes.
20. No Stage 5 work is performed.

## Codex completion report

At completion, report:

1. Whether Stage 4.1e can be closed.
2. Files created or modified.
3. Whether any production code changed.
4. The finalized Stage 4 -> Stage 5 handoff contract.
5. Seestar handoff dtype/value policy.
6. Siril handoff dtype/value policy.
7. Confirmation that no common numeric dtype is imposed.
8. Confirmation that no universal `[0,1]` rule is imposed.
9. Stage 5 responsibilities identified.
10. Orientation status.
11. Producer/mosaic-independence status.
12. Tests added or changed.
13. Focused test result, if applicable.
14. Full pytest result.
15. Ruff result.
16. Formatting result or not-applicable status.
17. `git diff --check` result.
18. Documentation changes.
19. Any remaining Stage 4.1e blockers or open questions.
20. Current `git status --short`.

Do not commit changes.

## Stage boundary

Successful completion of Stage 4.1e defines the final RGB data contract that
Stage 5 TIFF output will consume.

Do not begin Stage 4.1f validation/closure or Stage 5 during this stage.
