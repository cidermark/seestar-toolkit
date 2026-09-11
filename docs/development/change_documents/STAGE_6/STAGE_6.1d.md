# Seestar Toolkit — Stage 6.1d

## Validate and Complete the Siril RGB Conversion Path

### Purpose

Stage 6.1d validates and, only where necessary, completes the end-to-end single-file conversion route for Siril-produced RGB FIT/FITS images.

The route under test is:

```text
Siril RGB FIT/FITS
    -> inspect/classify
    -> read RGB image
    -> normalize RGB layout
    -> write TIFF
```

Stage 6.1a established `convert_fits_to_tiff(input_path, output_path) -> pathlib.Path` as the authoritative single-file conversion-pipeline boundary.

Stage 6.1b validated the raw Seestar Bayer route.

Stage 6.1c validated the native Seestar stacked RGB route.

Stage 6.1d now validates the Siril RGB route, whose source representation differs materially from native Seestar RGB because Siril files are expected to contain `float32` RGB data.

As in Stages 6.1b and 6.1c, Codex must assess the existing implementation before making production changes.

---

## Starting Point / Prerequisite Commit

Stage 6.1d starts from:

```text
98e42b3 Stage 6.1c: validate native Seestar RGB conversion path
```

Stages 1–5 and Stage 6.1a–6.1c are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1c entry as an intentional uncommitted modification. That state is normal and should ordinarily be included in the Stage 6.1d commit.

The authoritative specification for this sub-stage is:

```text
docs/change_documents/STAGE_6/STAGE_6.1d.md
```

---

## Background

The project already contains all expected Siril RGB support components:

- Stage 2 FITS inspection/classification;
- Stage 2 FITS image reading;
- Stage 4 RGB layout normalisation;
- Stage 5 TIFF writing with `float32` support;
- Stage 6.1a single-file conversion orchestration.

Stage 4 established that the existing Siril fixtures are:

- RGB;
- channels-first;
- `float32`;
- observed in the approximate numeric range `[0, 1]`.

Stage 5 established that valid finite `float32` RGB arrays are accepted for TIFF output.

The current `FitsImageClass.RGB_IMAGE` route is therefore expected to support Siril inputs without a separate conversion branch.

Stage 6.1d must validate that assumption with real fixtures.

---

## Required Work

### 1. Assess Existing Siril RGB Support First

Before changing production code, inspect the existing Stage 6.1a conversion pipeline and the relevant Stage 2, 4, and 5 APIs.

Determine whether the current `RGB_IMAGE` path already satisfies the Stage 6.1d contract for Siril-generated FIT/FITS images.

Do not add a Siril-specific conversion branch unless a demonstrated technical requirement makes one necessary.

Do not rewrite or duplicate existing Stage 4/5 logic merely to create implementation work.

If the route is already correct, Stage 6.1d may consist primarily of real-data integration tests and documentation.

---

### 2. End-to-End Siril RGB Contract

For a supported Siril RGB FIT/FITS file, `convert_fits_to_tiff()` must:

1. accept the source FIT/FITS path and explicit TIFF destination;
2. inspect/classify through the existing Stage 2 subsystem;
3. classify the image as `FitsImageClass.RGB_IMAGE`;
4. read the source through the existing FITS reader;
5. preserve the supported Siril `float32` source data type;
6. pass the RGB image to the existing Stage 4 `normalize_rgb_layout()` implementation;
7. normalise channels-first source representation to channels-last RGB;
8. preserve valid finite `float32` image values without introducing scaling or conversion;
9. pass the normalized RGB result directly to the existing Stage 5 TIFF writer;
10. create the explicitly requested TIFF output;
11. return the output `Path` according to the Stage 6.1a contract.

The conversion layer remains orchestration only.

---

### 3. Siril RGB Layout Handling

The pipeline must rely entirely on the existing Stage 4 RGB subsystem for layout normalisation.

The conversion layer must not independently:

- transpose axes;
- move channels;
- reinterpret channel order;
- add Siril-specific axis logic;
- duplicate Stage 4 validation.

For the existing Siril fixtures, source image data is expected to be:

```text
(3, H, W)
float32
```

The TIFF-facing result must be:

```text
(H, W, 3)
float32
```

---

### 4. Float32 Preservation

Stage 6.1d must specifically prove preservation of the Siril `float32` data path.

The pipeline must not:

- convert `float32` to `uint16`;
- quantize to 16-bit integer;
- rescale values;
- normalize values to a different numeric range;
- clip valid values;
- apply gamma;
- stretch;
- change colour balance.

The existing Stage 5 TIFF writer contract for finite `float32` arrays remains authoritative.

If the real Siril fixture contains valid values outside the previously observed `[0, 1]` range, Stage 6.1d should report the observation rather than introduce implicit clipping or scaling.

---

### 5. Invalid Float Behaviour

Detailed TIFF-writer rejection of NaN and Inf is already owned by Stage 5.

Stage 6.1d does not need to duplicate every invalid-float test.

However, the conversion pipeline must not catch, hide, or transform an underlying Stage 5 failure for invalid `float32` output.

Existing Stage 6.1a exception-propagation tests may provide sufficient proof unless a Siril-specific integration gap is found.

---

### 6. Source Preservation

Conversion must not modify, rename, move, or delete the source Siril FIT/FITS file.

Source preservation should be checked using evidence consistent with Stages 6.1b and 6.1c:

- file existence;
- file size;
- nanosecond modification time;
- SHA-256 digest.

Stage 7 owns source-file movement/copying and archive organisation.

---

## Required Real-Data Validation

Use the project's existing Siril RGB FITS fixtures.

At minimum validate:

- `siril_stacked.fit`;
- `siril_stacked_mosaic.fit`.

If exact names or paths differ in the repository, use the equivalent existing Siril fixtures and report their exact paths.

For each fixture, confirm at minimum:

- inspection/classification identifies `FitsImageClass.RGB_IMAGE`;
- source image layout is RGB/channels-first as expected;
- source dtype is `float32`;
- conversion succeeds through `convert_fits_to_tiff()`;
- output TIFF exists;
- output TIFF can be independently reopened using the project's established TIFF test mechanism;
- output shape is `(H, W, 3)` with source-derived dimensions;
- output dtype remains `float32`;
- representative numeric values/range are preserved sufficiently to demonstrate that no implicit scaling or integer conversion occurred;
- source FIT/FITS remains unchanged.

Do not require exact whole-image byte equality between FITS image data and TIFF reopening unless the TIFF library/format path guarantees it and such an assertion is stable.

A small set of representative pixel/value comparisons or array comparison may be used if appropriate and practical.

---

## Required Tests

Add focused integration tests consistent with the existing test structure.

Tests must cover at least:

1. real `siril_stacked.fit` conversion through the public pipeline boundary;
2. real `siril_stacked_mosaic.fit` conversion through the public pipeline boundary;
3. `RGB_IMAGE` classification;
4. source channels-first RGB representation;
5. source `float32` dtype;
6. output existence;
7. output channels-last `(H, W, 3)` layout;
8. output `float32` dtype;
9. independent TIFF reopening;
10. sufficient value/range preservation evidence to show no implicit integer conversion or scaling;
11. source-file preservation;
12. existing destination overwrite protection where relevant.

Existing Stage 4 tests remain authoritative for detailed RGB normalisation logic.

Existing Stage 5 tests remain authoritative for detailed float32 TIFF writer validation.

Do not duplicate those lower-level suites unnecessarily.

---

## Files / Components Expected to Be Affected

Expected changes should remain small.

Likely files include:

- Stage 6 Siril RGB integration tests;
- `src/seestar_toolkit/conversion.py` only if a concrete deficiency is demonstrated;
- documentation only where necessary;
- `docs/change_documents/STAGE_6/STAGE_6.1d.md`;
- the intentionally modified `docs/CHANGELOG.md` as part of the eventual commit.

Existing FITS fixtures must remain unchanged.

Avoid unrelated refactoring.

---

## Documentation Requirements

Update project documentation only where needed to record that the Siril `float32` RGB route has been validated end-to-end through the public single-file pipeline.

Documentation should distinguish clearly between:

- native Seestar RGB `uint16`;
- Siril RGB `float32`.

Do not imply that CLI polish, batch processing, archive organisation, Stage 8 real-dataset qualification, or release work is complete.

---

## Explicit Exclusions / Deferred Work

Stage 6.1d must not implement:

- raw Bayer work already completed in Stage 6.1b;
- native Seestar RGB work already completed in Stage 6.1c except regression protection;
- CLI `convert` integration/polish — Stage 6.1e;
- batch conversion — Stage 6.1f;
- complete Stage 6 workflow validation — Stage 6.1g;
- Stage 6 closure — Stage 6.1h;
- archive directory creation;
- configurable archive hierarchy;
- source-file movement/copying;
- archive collision handling;
- archive missing-metadata behaviour;
- archive dry-run behaviour;
- Stage 7 functionality;
- broad Stage 8 dataset qualification;
- image enhancement;
- 8-bit conversion;
- arbitrary float-to-integer conversion;
- packaging/release work.

If excluded work appears necessary, report it rather than implementing it.

---

## Validation Commands

Run at minimum:

```bash
pytest <relevant Stage 6.1d test files>
pytest
ruff check .
```

Run the repository's established formatting check for changed source/test files.

Also run:

```bash
git diff --check
```

Codex must not commit changes.

---

## Closure Criteria

Stage 6.1d may be closed only when all of the following are satisfied:

1. The existing `RGB_IMAGE` route has been assessed for Siril support before unnecessary production changes are made.
2. `convert_fits_to_tiff()` remains the public single-file conversion boundary.
3. Real `siril_stacked.fit` converts successfully through that boundary.
4. Real `siril_stacked_mosaic.fit` converts successfully through that boundary.
5. Both fixtures are classified through the existing Stage 2 subsystem as `FitsImageClass.RGB_IMAGE`.
6. Both fixtures are read using the existing Stage 2 FITS reader.
7. Siril source RGB layout is validated as channels-first for the existing fixtures.
8. Siril source dtype is validated as `float32`.
9. The route uses the existing Stage 4 `normalize_rgb_layout()` implementation.
10. The conversion layer does not duplicate or add Siril-specific RGB axis/channel manipulation.
11. The normalized array is passed to the existing Stage 5 TIFF writer without new image transformation.
12. TIFF outputs exist at the explicitly requested destinations.
13. TIFF outputs can be independently reopened successfully.
14. TIFF outputs have `(H, W, 3)` channels-last RGB layout with source-derived dimensions.
15. TIFF output dtype remains `float32`.
16. Validation demonstrates that no implicit float-to-integer conversion has occurred.
17. Validation demonstrates that no implicit scaling, stretching, clipping, gamma, white balance, or colour correction has occurred.
18. Existing Stage 5 invalid-float protections remain intact and are not bypassed or hidden by the conversion pipeline.
19. Source Siril FIT/FITS files remain present and unchanged.
20. Existing TIFF destination overwrite protection remains intact.
21. Stage 6.1d focused integration tests pass.
22. The complete project test suite passes.
23. Ruff passes.
24. Formatting validation for changed source/test files passes.
25. `git diff --check` passes.
26. Documentation accurately records Siril `float32` RGB-route completion where required.
27. CLI integration/polish remains deferred to Stage 6.1e.
28. No batch, archive, Stage 7, Stage 8, or release work has crept into this sub-stage.
29. No unnecessary Siril-specific production branch has been introduced if the generic `RGB_IMAGE` route already suffices.
30. No unrelated refactoring or behavioural changes have been introduced.
31. Codex provides the required completion report and identifies deviations, assumptions, and blockers.

Every closure criterion must be reviewed individually before Stage 6.1d is approved for commit.

---

## Required Codex Completion Report

When complete, report:

- files changed;
- whether production conversion code required modification and why;
- implementation/integration summary;
- exact Siril FITS fixtures used;
- source and output shapes/dtypes observed;
- observed representative source/output value ranges or other value-preservation evidence;
- tests added or changed;
- validation commands and results;
- closure criteria 1–31, individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers or unresolved issues.

Do not commit any changes.

---

## Stage Boundary / What Comes Next

Successful Stage 6.1d completion proves all currently supported single-file image-data routes:

- raw Seestar Bayer;
- native Seestar RGB;
- Siril RGB.

The next planned sub-stage is:

```text
Stage 6.1e — integrate and polish the single-file convert CLI
```

Batch conversion remains Stage 6.1f.

Archive organisation remains Stage 7.

Broader qualification with additional real Seestar datasets remains Stage 8.
