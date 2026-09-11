# Stage 4.1f — Validate and close Stage 4

## Purpose

Perform the final validation and documentation review for Stage 4 — RGB FITS
processing/handling — and determine whether Stage 4 can be formally closed.

This is a validation/closure stage.

No new image-processing functionality is expected.

Do not begin Stage 5.

## Stage 4 scope being closed

Stage 4 established a common internal RGB handling path for already-RGB FITS
images.

The completed sub-stages are:

- Stage 4.1a — Define RGB image handling contract.
- Stage 4.1b — Implement RGB layout normalization.
- Stage 4.1c — Validate real Seestar stacked FITS.
- Stage 4.1d — Validate real Siril stacked FITS, standard and mosaic.
- Stage 4.1e — Define the Stage 4 to Stage 5 handoff requirements.

Stage 4.1f must review the combined result rather than introduce another
processing feature.

## Required final Stage 4 contract

Confirm that the implementation, tests, and documentation collectively establish
the following.

### RGB recognition

Already-RGB FITS images are recognized from their supported image layout and are
not sent through Bayer demosaicing.

A retained `BAYERPAT` keyword in an already-RGB Seestar stack must not cause the
image to be treated as raw Bayer data.

### Supported FITS RGB layout

The currently supported FITS RGB layout is channels-first:

```text
(3, height, width)
```

The Stage 4 normalization operation converts this to:

```text
(height, width, 3)
```

### Internal channel order

The normalized representation is:

```text
R, G, B
```

No channel reordering is introduced.

### Numerical preservation

Stage 4 preserves source numerical values.

It must not perform:

- scaling;
- clipping;
- normalization;
- stretching;
- gamma correction;
- white balance;
- RGB equalisation;
- tone mapping;
- integer quantization.

### Dtype preservation

Validated Seestar stacked FITS are handed forward as:

```text
(H, W, 3), uint16
```

Validated Siril stacked FITS are handed forward as:

```text
(H, W, 3), float32
```

Stage 4 does not impose one common numeric dtype.

### Float range

The validated Siril fixtures happen to contain floating-point values in `[0,1]`.

Confirm that this remains fixture-specific evidence and has not become a
universal Stage 4 input or output assumption.

### Standard and mosaic handling

Confirm that standard and mosaic RGB stacks use the same Stage 4 pixel-processing
path.

No mosaic-specific RGB normalization or conversion should exist.

### Producer independence

Confirm that Seestar and Siril RGB stacks use the same structural normalization
contract.

There should be no producer-specific RGB pixel-processing branch.

Producer metadata may be retained or inspected elsewhere, but must not alter the
Stage 4 RGB pixel representation.

### Orientation

Confirm that Stage 4 performs no:

- mirroring;
- flipping;
- rotation;
- ROWORDER interpretation;
- WCS orientation correction;
- reprojection.

The previously observed Siril standard-stack `mirrorx_single result` / history
difference remains an evidence question rather than a Stage 4 processing rule.

Orientation must remain deferred unless the existing evidence now proves a
specific required behavior. Do not infer one simply to close Stage 4.

### Stage 5 boundary

Confirm that Stage 4 hands Stage 5:

```text
(H, W, 3), RGB, linear image data
```

while preserving the Stage 4 source dtype and numerical values.

Confirm that Stage 5 owns TIFF-specific decisions, including:

- TIFF sample type;
- TIFF bit depth;
- direct `uint16` output mapping;
- handling of `float32`;
- whether floating-point TIFF is supported;
- any float-to-integer range/scaling policy;
- clipping;
- rounding;
- below-range and above-range handling;
- NaN and infinity handling;
- TIFF photometric/channel conventions;
- TIFF metadata policy;
- validation and overwrite/file-writing behavior.

No Stage 5 numeric policy should have leaked into Stage 4.

## Real-data validation matrix

Confirm that Stage 4 remains validated against all four authoritative RGB
fixtures:

```text
tests/data/seestar/stacked.fit
tests/data/seestar/stacked_mosaic.fit
tests/data/reference/siril_stacked.fit
tests/data/reference/siril_stacked_mosaic.fit
```

The final review should confirm coverage for:

| Producer | Capture/stack type | Expected dtype |
|---|---|---|
| Seestar | Standard | uint16 |
| Seestar | Mosaic | uint16 |
| Siril | Standard | float32 |
| Siril | Mosaic | float32 |

Do not modify or replace these fixtures.

If practical, verify that the fixture files remain unchanged. Existing known
hash assertions/checks may be reused rather than adding redundant mechanisms.

## Test review

Review the complete Stage 4 test coverage, including:

- RGB handling contract tests;
- RGB layout normalization unit tests;
- Seestar stacked FITS integration coverage;
- Siril stacked FITS integration coverage.

Confirm that tests protect the important behavior without excessive duplication.

Do not add tests simply to increase the test count.

Add or modify a test only if the closure review identifies a genuine uncovered
Stage 4 requirement.

If no coverage gap exists, leave tests unchanged.

## Production-code review

Review the Stage 4 production implementation, especially the RGB normalization
path.

Confirm that it remains minimal and appropriately scoped.

No production-code change is expected.

Do not refactor working Stage 4 code merely for closure.

If a genuine defect or missing Stage 4 requirement is discovered, report it and
make only the smallest justified correction within Stage 4 scope.

Do not solve Stage 5 concerns in Stage 4 production code.

## Documentation review

Review at least:

```text
docs/PROJECT_Notes.md
docs/ARCHITECTURE.md
docs/SEESTAR_FITS_REFERENCE.md
docs/change_documents/STAGE_4/STAGE_4.1a.md
docs/change_documents/STAGE_4/STAGE_4.1b.md
docs/change_documents/STAGE_4/STAGE_4.1c.md
docs/change_documents/STAGE_4/STAGE_4.1d.md
docs/change_documents/STAGE_4/STAGE_4.1e.md
```

Update `docs/PROJECT_Notes.md` to mark Stage 4 complete only if every Stage 4
acceptance criterion passes.

Ensure documentation does not still describe completed Stage 4 work as future,
planned, pending, or in progress.

Ensure the next development focus is Stage 5 — TIFF output.

Update `docs/ARCHITECTURE.md` only if the closure review finds a genuine
inconsistency or missing boundary clarification.

Update `docs/SEESTAR_FITS_REFERENCE.md` only if the review reveals a factual
error or genuinely new FITS evidence. Do not add architectural policy to the
FITS reference.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The user will
add the Stage 4.1f CHANGELOG entry after the commit ID is known.

## Explicit exclusions

Do not implement:

- TIFF writing;
- TIFF metadata output;
- float-to-`uint16` conversion;
- float scaling or normalization;
- clipping policy;
- NaN/Inf conversion policy;
- gamma correction;
- stretching;
- white balance;
- RGB equalisation;
- colour enhancement;
- orientation correction;
- mirroring;
- rotation;
- WCS reprojection;
- registration;
- plate solving;
- mosaic stitching;
- CLI conversion;
- batch conversion;
- archive organisation.

Do not begin Stage 5.

## Validation commands

Run an appropriate focused Stage 4 test selection covering the Stage 4 contract,
normalization, Seestar integration, and Siril integration.

Then run:

```bash
pytest
ruff check .
git diff --check
```

If Python files are changed, run the applicable Ruff formatting check.

If no Python files are changed, report formatting as not applicable.

## Stage 4 closure criteria

Stage 4 can be closed only if all of the following are true:

1. Already-RGB FITS are correctly distinguished from raw Bayer images.
2. Retained `BAYERPAT` metadata does not cause already-RGB Seestar stacks to be
   demosaiced.
3. Supported channels-first `(3,H,W)` RGB FITS are normalized to `(H,W,3)`.
4. Normalized channel order is R, G, B.
5. Numerical values are preserved.
6. Seestar RGB `uint16` is preserved.
7. Siril RGB `float32` is preserved.
8. Stage 4 imposes no common numeric dtype.
9. Stage 4 imposes no universal `[0,1]` float rule.
10. No scaling, clipping, stretching, gamma, white balance, RGB equalisation, or
    quantization occurs.
11. Standard and mosaic stacks use the same RGB processing path.
12. Seestar and Siril use the same structural RGB normalization contract.
13. No producer-specific pixel-processing branch exists.
14. No mosaic-specific pixel-processing branch exists.
15. Orientation remains unchanged/deferred.
16. The four authoritative real RGB fixtures are covered.
17. The Stage 4 -> Stage 5 handoff is explicit.
18. TIFF-specific numeric/file-format policy remains assigned to Stage 5.
19. No Stage 5 implementation has leaked into Stage 4.
20. Stage 4 tests adequately protect the contract.
21. Full pytest passes.
22. Ruff passes.
23. Formatting passes or is correctly reported not applicable.
24. `git diff --check` passes.
25. Documentation accurately records Stage 4 as complete and Stage 5 as the next
    development focus.
26. No unresolved issue remains that is a genuine Stage 4 blocker.

If any criterion fails, do not declare Stage 4 complete. Report the blocker and
the smallest appropriate next action.

## Codex completion report

At completion, report:

1. Whether Stage 4.1f can be closed.
2. Whether Stage 4 as a whole can be closed.
3. Files created or modified.
4. Whether production code changed.
5. Whether tests changed.
6. Final RGB recognition/classification status.
7. Final layout-normalization status.
8. Final RGB channel-order status.
9. Final numerical-preservation status.
10. Final Seestar dtype status.
11. Final Siril dtype status.
12. Float-range policy status.
13. Standard/mosaic independence status.
14. Producer-independence status.
15. Orientation status and any remaining orientation question.
16. Stage 4 -> Stage 5 handoff status.
17. Confirmation that no Stage 5 TIFF behavior was implemented.
18. Real-fixture validation status for all four authoritative fixtures.
19. Focused Stage 4 test result.
20. Full pytest result.
21. Ruff result.
22. Formatting result or not-applicable status.
23. `git diff --check` result.
24. Documentation changes.
25. Any remaining blockers or open questions.
26. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 4.1f can be closed.**

and:

**Stage 4 can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 4.1f formally closes Stage 4 — RGB FITS
processing/handling.

Stage 5 — TIFF output — is the next development stage, but must not be started
during Stage 4.1f.
