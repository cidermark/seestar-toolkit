# Stage 5.1c — Define float32 TIFF output policy

## Purpose

Define and implement the Stage 5 policy for writing normalized RGB `float32`
image data to TIFF.

Stage 4 established that validated Siril RGB FITS are handed to Stage 5 as:

```text
(height, width, 3), float32
```

Stage 5.1a and Stage 5.1b established a safe, exact `uint16` RGB TIFF writer.

Stage 5.1c must now define how `float32` RGB image data is represented in TIFF
without introducing pipeline or CLI integration.

## Starting point

Stage 5.1b was completed in commit:

```text
b323eeb — Complete TIFF writer file handling
```

The existing public API is:

```text
write_tiff(image, path)
```

The current writer:

- accepts `(height, width, 3)` RGB NumPy arrays;
- requires `numpy.uint16`;
- writes 16-bit-per-channel RGB TIFF;
- preserves `uint16` values exactly;
- performs no scaling or image processing;
- accepts `str` and `pathlib.Path` destinations;
- refuses to overwrite existing files;
- does not create missing parent directories;
- returns the final destination as a `pathlib.Path`;
- wraps practical TIFF/filesystem failures in `TiffWriteError`.

Do not weaken or redesign this working `uint16` contract.

## Stage 5.1c design objective

Stage 5 must support the normalized `float32` RGB data produced by Stage 4 for
validated Siril stacked FITS.

The preferred policy for Stage 5.1c is:

```text
float32 input -> 32-bit floating-point RGB TIFF
```

The writer must preserve the supplied floating-point sample values directly.

Do not convert `float32` input to `uint16` during Stage 5.1c.

Do not impose a universal `[0,1]` range requirement merely because the currently
validated Siril fixtures happen to contain values in that range.

## Supported input contracts

After Stage 5.1c, the TIFF writer must support both:

```text
(H, W, 3), uint16
```

and:

```text
(H, W, 3), float32
```

Both represent:

```text
R, G, B
```

channel order.

Unsupported layouts must remain rejected.

Unsupported dtypes must remain rejected unless explicitly included in this stage.

In particular, Stage 5.1c does not add support for:

- `uint8`;
- `int16`;
- `uint32`;
- `float64`;
- other integer or floating-point dtypes.

## uint16 TIFF behaviour

Existing `uint16` behaviour must remain unchanged.

A `uint16` input must continue to produce:

```text
RGB TIFF
3 samples per pixel
16 bits per sample
```

with exact pixel-value preservation.

No regression in Stage 5.1a or Stage 5.1b behaviour is acceptable.

## float32 TIFF behaviour

A `float32` input must produce an RGB TIFF with:

```text
3 samples per pixel
32 bits per sample
IEEE floating-point sample format
RGB photometric interpretation
```

The TIFF must preserve the input floating-point samples directly.

No normalization, scaling, clipping, rounding, quantization, or integer
conversion may occur.

A TIFF written from `float32` input and read back must preserve values according
to exact `float32` representation where supported by the TIFF library.

## Float value range

Do not impose a `[0,1]` restriction.

Stage 4 established only that the currently validated Siril fixtures happen to
contain values in `[0,1]`.

That is fixture evidence, not a universal Stage 4 or Stage 5 rule.

Stage 5.1c must therefore permit finite `float32` RGB values outside `[0,1]`.

Tests should include representative:

- values below `0.0`;
- values between `0.0` and `1.0`;
- values above `1.0`.

These values must be written without clipping or rescaling.

## NaN and infinity policy

Stage 5.1c must explicitly define behaviour for non-finite floating-point values.

Preferred policy:

- reject `NaN`;
- reject positive infinity;
- reject negative infinity.

These values should raise `InvalidTiffImageError`.

The writer should not silently replace, clamp, normalize, or otherwise transform
non-finite values.

This keeps TIFF output deterministic while avoiding undefined downstream
behaviour.

Do not add configurable NaN/Inf replacement policy during this stage.

## TIFF metadata/sample-format validation

Tests must verify the resulting `float32` TIFF structure using `tifffile` or an
equivalent existing test dependency.

Confirm at least:

```text
photometric: RGB
samples per pixel: 3
bits per sample: 32
sample format: IEEE floating point
```

Use the TIFF library's actual exposed metadata representation rather than relying
on assumptions about raw numeric tag values.

## Exception behaviour

Continue using the existing TIFF exception hierarchy:

```text
TiffError
InvalidTiffImageError
TiffWriteError
```

Invalid image shape, unsupported dtype, and rejected non-finite float data must
raise `InvalidTiffImageError`.

Filesystem and underlying TIFF-output failures must remain exposed through
`TiffWriteError`.

Do not introduce new exception classes unless a genuine need is demonstrated.

## File-handling contract remains unchanged

Stage 5.1b behaviour must remain intact.

The writer must continue to:

- accept `str` and `pathlib.Path`;
- return the final destination as a `pathlib.Path`;
- refuse to overwrite an existing destination;
- leave an existing destination unchanged;
- avoid automatic parent-directory creation;
- wrap practical filesystem failures in `TiffWriteError`;
- perform image validation before creating the destination where practical.

Do not add overwrite or directory-creation options.

## Tests

Add focused tests for the new `float32` contract.

Coverage should include, as appropriate:

1. `float32` RGB input is accepted.
2. `float32` data round-trips without scaling or quantization.
3. Resulting TIFF uses RGB photometric interpretation.
4. Resulting TIFF has three samples per pixel.
5. Resulting TIFF has 32 bits per sample.
6. Resulting TIFF uses IEEE floating-point sample format.
7. Finite values below `0.0` are preserved.
8. Finite values above `1.0` are preserved.
9. `NaN` is rejected.
10. Positive infinity is rejected.
11. Negative infinity is rejected.
12. Rejected non-finite input does not create an output file.
13. Existing `uint16` exact round-trip behaviour remains intact.
14. Existing Stage 5.1b path/file-handling tests remain intact.
15. Unsupported dtypes such as `float64` remain rejected.

Do not add duplicate tests where existing coverage already protects the same
requirement.

## Production-code scope

Modify only the TIFF subsystem as required.

Expected files are primarily:

```text
src/seestar_toolkit/tiff/writer.py
tests/unit/tiff/test_writer.py
```

Other TIFF subsystem files may be modified only if genuinely required.

Keep the implementation minimal.

Do not introduce a separate float TIFF writer unless the existing architecture
clearly benefits from it. Prefer one public `write_tiff(image, path)` operation
that dispatches safely according to supported dtype.

## Documentation

The authoritative Stage 5.1c specification is:

```text
docs/change_documents/STAGE_5/STAGE_5.1c.md
```

Update architecture/project documentation only if Stage 5.1c establishes a
numeric/output policy that is not already accurately documented.

If documentation is changed, keep it narrowly scoped to:

- supported TIFF sample types;
- `uint16` direct preservation;
- `float32` direct floating-point TIFF output;
- no implicit float-to-integer conversion;
- rejection of non-finite float samples.

Do not make broad unrelated documentation changes.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user will
add the Stage 5.1c CHANGELOG entry after the commit ID is known.

## Explicit exclusions

Do not implement:

- CLI integration;
- conversion-pipeline integration;
- output filename generation;
- archive organisation;
- configurable archive hierarchy;
- automatic directory creation;
- overwrite/force options;
- 8-bit TIFF output;
- float-to-`uint16` conversion;
- float normalization to `[0,1]`;
- float scaling to integer range;
- clipping;
- rounding/quantization policy;
- NaN/Inf replacement;
- image stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- TIFF metadata embedding beyond what `tifffile` requires for correct sample
  representation;
- orientation correction;
- registration;
- plate solving;
- mosaic stitching;
- batch conversion.

Do not begin Stage 5.1d.

## Validation commands

Run an appropriate focused TIFF test selection.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

## Stage 5.1c closure criteria

Stage 5.1c can be closed only if all of the following are true:

1. Existing `uint16` TIFF behaviour remains unchanged.
2. `(H,W,3)` `float32` RGB input is supported.
3. `float32` TIFF output uses RGB photometric interpretation.
4. `float32` TIFF output has three samples per pixel.
5. `float32` TIFF output has 32 bits per sample.
6. `float32` TIFF output uses IEEE floating-point sample format.
7. Finite `float32` values are preserved without scaling.
8. Finite negative values are not clipped.
9. Finite values above `1.0` are not clipped.
10. No universal `[0,1]` input rule is imposed.
11. No float-to-integer conversion is introduced.
12. `NaN` is rejected.
13. Positive infinity is rejected.
14. Negative infinity is rejected.
15. Rejected non-finite input does not create an output file.
16. Unsupported dtypes remain rejected.
17. Existing Stage 5.1b path/file-handling behaviour remains intact.
18. No CLI or pipeline integration has been introduced.
19. No 8-bit TIFF behaviour has been introduced.
20. No image-processing behaviour has been introduced.
21. Focused TIFF tests pass.
22. Full pytest passes.
23. Ruff passes.
24. Formatting validation passes.
25. `git diff --check` passes.
26. Documentation accurately reflects the established numeric policy where
    applicable.
27. No unresolved issue remains that is a genuine Stage 5.1c blocker.

If any criterion fails, do not declare Stage 5.1c complete. Report the blocker
and the smallest appropriate next action.

## Codex completion report

At completion, report:

1. Whether Stage 5.1c can be closed.
2. Files created or modified.
3. Production-code changes.
4. Test changes.
5. Final supported input dtypes.
6. Final `uint16` TIFF behaviour.
7. Final `float32` TIFF behaviour.
8. Final float-range policy.
9. Final NaN policy.
10. Final positive-infinity policy.
11. Final negative-infinity policy.
12. Final TIFF photometric/sample structure for `float32`.
13. Confirmation that no float-to-integer conversion occurs.
14. Confirmation that Stage 5.1b file-handling behaviour remains unchanged.
15. Confirmation that no CLI or pipeline integration was added.
16. Confirmation that no 8-bit output was added.
17. Focused TIFF test result.
18. Full pytest result.
19. Ruff result.
20. Formatting result.
21. `git diff --check` result.
22. Documentation changes.
23. Any blockers or open questions for Stage 5.1d.
24. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 5.1c can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 5.1c establishes the TIFF sample-type policy for
both normalized Stage 4 RGB numeric representations:

```text
uint16  -> 16-bit integer RGB TIFF
float32 -> 32-bit floating-point RGB TIFF
```

Both paths preserve source sample values without implicit scaling or
quantization.

Stage 5.1d may then address higher-level output integration and naming/path
policy, but must not be started during Stage 5.1c.
