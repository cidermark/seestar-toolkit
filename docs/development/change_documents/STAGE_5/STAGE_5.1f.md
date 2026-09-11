# Stage 5.1f — Validate and close Stage 5

## Purpose

Formally validate and close Stage 5 — TIFF output.

Stage 5.1f is a closure and audit stage only.

It must review the complete Stage 5 implementation, tests, documentation, stage
boundaries, and repository state to confirm that the Stage 5 TIFF-output contract
is complete and internally consistent.

Do not add new TIFF functionality.

## Starting point

Stage 5.1e was completed in commit:

```text
3a940cc — Stage 5.1e: validate integrated TIFF output
```

Stage 5 currently consists of:

```text
5.1a — TIFF writer foundation
5.1b — complete TIFF writer file handling
5.1c — add float32 TIFF output support
5.1d — integrate FITS conversion with TIFF output
5.1e — validate integrated TIFF output
```

Relevant commits are:

```text
b399cd7 — Add TIFF writer foundation
7a58987 — Stage 5.1b: complete TIFF writer file handling
1debcec — Stage 5.1c: Add float32 TIFF output support
54d8c60 — Stage 5.1d: integrate FITS conversion with TIFF output
3a940cc — Stage 5.1e: validate integrated TIFF output
```

Stage 5.1a predates the later standardized commit-message format. Do not rewrite
history solely to rename that commit.

## Stage 5 contract to validate

Stage 5 must establish a reliable TIFF-output layer for supported Seestar Toolkit
image data.

The complete Stage 5 contract is:

### Supported RGB array structure

The TIFF writer accepts normalized RGB arrays shaped:

```text
(H, W, 3)
```

with RGB channel order.

### Supported numeric families

The TIFF writer supports:

```text
uint16
float32
```

including equivalent FITS/NumPy byte-order representations of those numeric
families where sample kind and width remain supported.

Unsupported numeric families remain rejected.

### uint16 TIFF output

`uint16` RGB data is persisted as:

```text
RGB
3 samples per pixel
16 bits per sample
unsigned integer samples
```

Pixel values are preserved exactly.

### float32 TIFF output

`float32` RGB data is persisted as:

```text
RGB
3 samples per pixel
32 bits per sample
IEEE floating-point samples
```

Finite sample values are preserved exactly.

No universal `[0, 1]` range restriction exists.

Finite negative values and finite values greater than `1.0` are valid.

NaN and positive/negative infinity are rejected before successful TIFF output.

### Numerical policy

Stage 5 performs no:

- scaling;
- clipping;
- normalization;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- tone mapping;
- resampling;
- integer quantization;
- float-to-integer conversion.

### File-handling policy

TIFF output:

- accepts explicit `str` or `pathlib.Path` destinations;
- returns the successful destination as a `pathlib.Path`;
- refuses silent overwrite;
- preserves an existing destination when overwrite is refused;
- does not create missing parent directories;
- reports TIFF/filesystem write failures through the established TIFF exception
  hierarchy.

### Integrated FITS-to-TIFF conversion

The public integration operation is:

```python
from seestar_toolkit.conversion import convert_fits_to_tiff
```

The conversion path composes existing subsystems:

```text
FITS inspection / classification
            |
            +-- RAW_LIGHT --> existing demosaic()
            |
            +-- RGB_IMAGE --> existing normalize_rgb_layout()
                                   |
                                   v
                              write_tiff()
```

Raw Bayer FITS must use the existing Bayer demosaicing path.

Already-RGB FITS must bypass Bayer demosaicing and use the existing RGB-layout
normalization path.

Both paths must converge on the same TIFF writer.

### Producer independence

Seestar and Siril already-RGB FITS use the same structural RGB normalization and
TIFF-writing path.

No producer-specific TIFF pixel-processing branch should exist.

### Standard/mosaic independence

Standard and mosaic FITS use the same conversion and TIFF-writing architecture.

No mosaic-specific TIFF pixel-processing branch should exist.

### Orientation

Stage 5 introduces no orientation processing.

No:

- rotation;
- mirroring;
- flipping;
- ROWORDER correction;
- WCS orientation correction;
- reprojection

is part of Stage 5.

## Authoritative real-data evidence

Review the existing Stage 5.1d/5.1e integration tests and confirm the authoritative
real-fixture matrix remains covered:

```text
tests/data/seestar/light.fit
tests/data/seestar/mosaic_1.fit
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

These collectively validate:

- raw Bayer standard;
- raw Bayer mosaic;
- Seestar RGB standard;
- Seestar RGB mosaic;
- Siril RGB standard;
- Siril RGB mosaic.

Do not modify or replace the authoritative fixtures during Stage 5.1f.

The separately planned new Seestar app/firmware comparison files are not part of
Stage 5 closure.

## Independent persisted-TIFF validation

Confirm Stage 5.1e continues to validate the actual TIFF files written to disk by
reopening them independently with `tifffile`.

The persisted TIFF validation should continue to prove:

- RGB photometric interpretation;
- three samples per pixel;
- correct dimensions;
- correct sample width;
- correct sample format;
- correct numeric family;
- exact integer sample preservation;
- exact float32 sample preservation;
- successful handling of real Siril big-endian FITS float32 source data.

Do not replace persisted-file validation with pre-write array-only checks.

## Test-suite review

Review the Stage 5 unit and integration tests for completeness and unnecessary
duplication.

At minimum, confirm coverage for:

- TIFF exception hierarchy;
- invalid image shape;
- unsupported numeric types;
- `uint16` TIFF round-trip;
- `float32` TIFF round-trip;
- finite float values outside `[0,1]`;
- non-finite float rejection;
- FITS byte-order-compatible float32 handling;
- explicit destination paths;
- existing-destination refusal;
- missing-parent behaviour;
- raw Bayer integrated conversion;
- already-RGB integrated conversion;
- standard and mosaic inputs;
- Seestar and Siril sources;
- independent persisted-TIFF validation.

Do not add tests solely to increase test count.

Add or amend a test only if the closure review identifies a genuine missing Stage
5 contract assertion.

## Production-code review

Review the Stage 5 production implementation for scope and architecture.

Confirm that:

- low-level TIFF writing remains in the TIFF subsystem;
- FITS-to-TIFF orchestration remains in the higher-level conversion layer;
- demosaicing logic is not duplicated;
- RGB normalization logic is not duplicated;
- TIFF-writing logic is not duplicated;
- there is no unnecessary producer-specific branch;
- there is no unnecessary mosaic-specific branch;
- no CLI concerns leaked into the conversion/TIFF layers;
- no archive-layout concerns leaked into the conversion/TIFF layers;
- no output-naming policy leaked into the conversion/TIFF layers;
- no image enhancement/display processing leaked into Stage 5.

Do not refactor working code merely for style during Stage 5.1f.

If a genuine Stage 5 defect is found, make the smallest justified correction,
protect it with a regression test, and report it clearly.

## Documentation review

Review the current:

```text
docs/ARCHITECTURE.md
docs/PROJECT_Notes.md
docs/CHANGELOG.md
docs/change_documents/STAGE_5/STAGE_5.1a.md
docs/change_documents/STAGE_5/STAGE_5.1b.md
docs/change_documents/STAGE_5/STAGE_5.1c.md
docs/change_documents/STAGE_5/STAGE_5.1d.md
docs/change_documents/STAGE_5/STAGE_5.1e.md
docs/change_documents/STAGE_5/STAGE_5.1f.md
```

Confirm documentation accurately reflects the final Stage 5 contract.

The documentation should clearly preserve these boundaries:

- TIFF output is linear/unprocessed;
- `uint16` and `float32` are supported;
- float32 is written as 32-bit IEEE floating-point TIFF;
- no implicit float-to-integer conversion occurs;
- no universal `[0,1]` restriction exists;
- raw Bayer and already-RGB paths converge on the shared TIFF writer;
- Stage 5 does not own CLI, batch, archive, naming, orientation, or display
  processing.

Make only narrow documentation corrections required for Stage 5 accuracy.

The pending `docs/CHANGELOG.md` modification containing the Stage 5.1e entry is an
expected working-tree change and should be included in the eventual Stage 5.1f
commit.

## Known issues / deferred work review

Review current known issues and deferred items.

Do not convert future-stage work into a Stage 5 blocker unless Stage 5 itself
cannot satisfy its defined TIFF-output contract.

In particular, the following are not Stage 5 blockers:

- CLI integration;
- batch processing;
- output filename generation;
- archive organization;
- configurable archive hierarchy;
- user-interface work;
- orientation policy;
- TIFF metadata policy;
- optional 8-bit compatibility/export mode;
- planetary capture-format investigation;
- Lunar capture behaviour;
- newly released Seestar app/firmware compatibility comparison.

If any documentation currently describes one of these as a Stage 5 requirement,
correct the documentation boundary rather than implementing it here.

## Explicit exclusions

Do not implement:

- new TIFF formats;
- 8-bit TIFF output;
- compression configuration;
- TIFF metadata policy;
- EXIF copying;
- FITS-header embedding;
- CLI commands or options;
- batch processing;
- recursive directory processing;
- output filename generation;
- archive organization;
- configurable archive hierarchy;
- automatic directory creation;
- overwrite/force options;
- orientation correction;
- image stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- colour enhancement;
- registration;
- plate solving;
- mosaic stitching;
- GUI behaviour.

Do not begin Stage 6.

Do not perform the planned `docs/change_documents` directory cleanup during
Stage 5.1f. That cleanup is a separate post-Stage-5 housekeeping activity to be
performed only after Stage 5 has been formally closed and committed.

## Validation commands

Run an appropriate focused Stage 5 test selection.

Then run:

```bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

Also inspect:

```bash
git status --short
git diff --stat
git diff
```

to confirm Stage 5.1f changes remain narrow and intentional.

## Stage 5 closure criteria

Stage 5 can be closed only if all of the following are true:

1. Stage 5.1a through Stage 5.1e are already complete.
2. The TIFF writer accepts normalized `(H, W, 3)` RGB arrays.
3. `uint16` RGB TIFF output is supported.
4. `float32` RGB TIFF output is supported.
5. `uint16` output uses 16-bit unsigned integer samples.
6. `float32` output uses 32-bit IEEE floating-point samples.
7. FITS/NumPy byte-order representations of supported numeric families are handled correctly.
8. Exact `uint16` sample preservation is validated.
9. Exact `float32` sample preservation is validated.
10. Finite float32 values outside `[0,1]` remain valid.
11. NaN is rejected.
12. Positive infinity is rejected.
13. Negative infinity is rejected.
14. Unsupported image shapes are rejected.
15. Unsupported numeric families remain rejected.
16. No scaling is introduced.
17. No clipping is introduced.
18. No normalization is introduced.
19. No float-to-integer conversion is introduced.
20. No display-oriented image processing is introduced.
21. Explicit TIFF destination paths are supported.
22. Successful writes return a `pathlib.Path`.
23. Existing TIFF destinations are not silently overwritten.
24. Existing destination contents remain protected on overwrite refusal.
25. Missing parent directories are not automatically created.
26. TIFF/filesystem errors remain represented by the established TIFF exception hierarchy.
27. A higher-level FITS-to-TIFF conversion operation exists.
28. Raw Bayer FITS use existing classification logic.
29. Raw Bayer FITS use the existing demosaicing implementation.
30. Already-RGB FITS bypass Bayer demosaicing.
31. Already-RGB FITS use the existing RGB normalization implementation.
32. Raw and already-RGB paths converge on the same TIFF writer.
33. Seestar and Siril RGB sources use the same structural TIFF-output path.
34. Standard and mosaic sources use the same TIFF-output architecture.
35. No producer-specific TIFF pixel-processing branch exists.
36. No mosaic-specific TIFF pixel-processing branch exists.
37. No orientation transformation is introduced by Stage 5.
38. Raw Bayer standard real fixture is validated end-to-end.
39. Raw Bayer mosaic real fixture is validated end-to-end.
40. Seestar RGB standard real fixture is validated end-to-end.
41. Seestar RGB mosaic real fixture is validated end-to-end.
42. Siril RGB standard real fixture is validated end-to-end.
43. Siril RGB mosaic real fixture is validated end-to-end.
44. Generated TIFF files are independently reopened from disk.
45. Persisted TIFF RGB photometric structure is validated.
46. Persisted TIFF samples-per-pixel is validated.
47. Persisted TIFF sample widths/formats are validated.
48. Persisted TIFF dimensions are validated.
49. Persisted TIFF integer samples are validated exactly.
50. Persisted TIFF float32 samples are validated exactly.
51. Real Siril big-endian FITS float32 data is validated successfully.
52. No new dependency was introduced solely for TIFF validation.
53. TIFF writer responsibilities remain separated from FITS-to-TIFF orchestration.
54. No duplicated demosaicing logic exists in Stage 5.
55. No duplicated RGB-normalization logic exists in Stage 5.
56. No duplicated TIFF-writing logic exists in the conversion layer.
57. No CLI integration is part of Stage 5.
58. No batch-processing behaviour is part of Stage 5.
59. No output filename-generation policy is part of Stage 5.
60. No archive-layout policy is part of Stage 5.
61. No automatic directory-creation policy is part of Stage 5.
62. No 8-bit TIFF behaviour is part of Stage 5.
63. No TIFF metadata policy is required for Stage 5 closure.
64. `docs/ARCHITECTURE.md` accurately reflects the final Stage 5 architecture.
65. `docs/PROJECT_Notes.md` accurately reflects the final Stage 5 contract.
66. Stage 5 change documents accurately describe the implemented boundaries.
67. Deferred work is not incorrectly treated as a Stage 5 blocker.
68. The pending Stage 5.1e CHANGELOG entry is preserved for inclusion in the Stage 5.1f commit.
69. Focused Stage 5 tests pass.
70. Full pytest passes.
71. Ruff passes.
72. Formatting validation passes.
73. `git diff --check` passes.
74. Stage 5.1f introduces no unrelated cleanup or refactoring.
75. No unresolved issue remains that is a genuine Stage 5 blocker.

If any criterion fails, do not declare Stage 5 complete. Report the blocker and
the smallest appropriate next action.

## Codex completion report

At completion, report:

1. Whether Stage 5.1f can be closed.
2. Whether Stage 5 can be closed.
3. Files created.
4. Files modified.
5. Whether production code changed and why.
6. Whether tests changed and why.
7. TIFF writer contract review.
8. `uint16` output review.
9. `float32` output review.
10. Byte-order compatibility review.
11. Non-finite float rejection review.
12. Numerical-preservation review.
13. File-handling review.
14. FITS-to-TIFF integration review.
15. Raw Bayer routing review.
16. Already-RGB routing review.
17. Standard/mosaic independence review.
18. Producer-independence review.
19. Orientation review.
20. Authoritative six-fixture validation status.
21. Independent persisted-TIFF validation status.
22. Test-suite coverage review.
23. Production architecture review.
24. `docs/ARCHITECTURE.md` review.
25. `docs/PROJECT_Notes.md` review.
26. Stage 5 change-document review.
27. CHANGELOG status.
28. Deferred-work / known-issues review.
29. Confirmation that no CLI, batch, naming, archive, orientation, 8-bit, metadata-policy, or Stage 6 work was added.
30. Confirmation that the planned `docs/change_documents` cleanup was not performed.
31. Focused Stage 5 test result.
32. Full pytest result.
33. Ruff result.
34. Formatting result.
35. `git diff --check` result.
36. `git diff --stat` summary.
37. Any genuine Stage 5 blockers.
38. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 5.1f can be closed.**

and:

**Stage 5 can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 5.1f formally closes Stage 5 — TIFF output.

After the Stage 5.1f changes are reviewed and committed, repository/documentation
housekeeping may be performed as a separate activity.

In particular, the planned cleanup of:

```text
docs/change_documents/
```

must occur after Stage 5 closure rather than being mixed into the Stage 5.1f
closure commit.

Stage 6 must not begin during Stage 5.1f.
