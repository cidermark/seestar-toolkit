# Seestar Toolkit — Stage 6.1c

## Validate and Complete the Native Seestar RGB Conversion Path

### Purpose

Stage 6.1c validates and, only where necessary, completes the end-to-end single-file conversion route for already-demosaiced native Seestar RGB FIT/FITS images:

```text
native Seestar RGB FIT/FITS
    -> inspect/classify
    -> read RGB image
    -> normalize RGB layout
    -> write TIFF
```

Stage 6.1a established `convert_fits_to_tiff(input_path, output_path) -> pathlib.Path` as the authoritative single-file conversion-pipeline boundary.

Stage 6.1b proved the real Seestar raw Bayer route.

Stage 6.1c now proves the native Seestar stacked RGB route. As with Stage 6.1b, Codex must assess the existing implementation before making production changes.

The goal is to demonstrate that supported real native Seestar RGB FIT/FITS files pass through the existing pipeline and produce valid linear `uint16` RGB TIFF files.

---

## Starting Point / Prerequisite Commit

Stage 6.1c starts from:

```text
8001815 Stage 6.1b: validate raw Bayer conversion path
```

Stages 1–5, Stage 6.1a, and Stage 6.1b are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1b entry as an intentional uncommitted modification. That state is normal and should ordinarily be included in the Stage 6.1c commit.

The authoritative specification for this sub-stage is:

```text
docs/change_documents/STAGE_6/STAGE_6.1c.md
```

---

## Background

The project already has the required native RGB components:

- Stage 2 FITS inspection/classification;
- Stage 2 FITS image reading;
- Stage 4 RGB layout normalisation;
- Stage 5 TIFF writing;
- Stage 6.1a single-file conversion orchestration.

Stage 4 established that native Seestar stacked FITS images are stored as RGB data in channels-first form and are represented as `uint16`.

The conversion pipeline currently routes `FitsImageClass.RGB_IMAGE` through the existing `normalize_rgb_layout()` implementation and then `write_tiff()`.

Stage 6.1c must validate that route specifically with native Seestar stacked FITS fixtures.

Siril RGB validation is deliberately deferred to Stage 6.1d because Siril uses a different source representation (`float32`).

---

## Required Work

### 1. Assess the Existing Native RGB Route First

Before changing production code, inspect the existing Stage 6.1a conversion pipeline and the relevant Stage 2, 4, and 5 APIs.

Determine whether the current `RGB_IMAGE` route already satisfies the Stage 6.1c contract for native Seestar stacked FITS files.

Do not rewrite, refactor, or duplicate working production code simply to create implementation activity for this sub-stage.

If the route is already correct, Stage 6.1c may consist primarily of real-data integration tests and documentation.

Any production-code change must address a concrete deficiency demonstrated by this specification or its tests.

---

### 2. End-to-End Native Seestar RGB Contract

For a supported native Seestar stacked RGB FIT/FITS file, `convert_fits_to_tiff()` must:

1. accept the source FIT/FITS path and explicit TIFF destination;
2. inspect/classify the source through the existing Stage 2 subsystem;
3. classify it as `FitsImageClass.RGB_IMAGE`;
4. read the source through the existing FITS reader;
5. pass the RGB data to the existing Stage 4 `normalize_rgb_layout()` implementation;
6. normalise channels-first source representation to channels-last RGB;
7. preserve the native `uint16` data type;
8. pass the normalised RGB result directly to the existing Stage 5 TIFF writer;
9. create the explicitly requested TIFF output;
10. return the output `Path` according to the Stage 6.1a contract.

The conversion layer remains orchestration only.

---

### 3. RGB Layout Handling

The pipeline must rely on the existing Stage 4 RGB subsystem for layout normalisation.

The conversion layer must not independently:

- transpose axes;
- move channels;
- reinterpret RGB ordering;
- duplicate Stage 4 shape checks.

For the existing native Seestar stacked fixtures, source data is expected to be channels-first:

```text
(3, H, W)
```

and the TIFF-facing result must be:

```text
(H, W, 3)
```

Stage 6.1c validates integration of that existing behaviour rather than redefining it.

---

### 4. Data-Type and Output Contract

Native Seestar stacked RGB FITS data is expected to produce TIFF image data that is:

```text
(H, W, 3)
uint16
RGB
```

The conversion must remain linear.

Stage 6.1c must not introduce:

- stretching;
- gamma;
- white balance;
- colour correction;
- rescaling;
- clipping;
- 8-bit conversion;
- float conversion;
- unrelated dtype conversion.

The existing Stage 4 and Stage 5 contracts remain authoritative.

---

### 5. Source Preservation

Conversion must not modify, rename, move, or delete the source FIT/FITS file.

Source preservation should be verified using strong evidence consistent with Stage 6.1b, such as:

- source existence;
- file size;
- nanosecond modification time;
- SHA-256 digest.

Stage 7 will own source-file movement/copying and archive organisation.

---

## Required Real-Data Validation

Use the project's existing real native Seestar stacked FITS fixtures.

At minimum validate:

- `stacked.fit`;
- `stacked_mosaic.fit`.

If fixture names or paths differ in the repository, use the equivalent existing native Seestar stacked fixtures and report the exact files used.

For each fixture, confirm at minimum:

- inspection/classification identifies a supported `RGB_IMAGE`;
- source image data has the expected native Seestar RGB representation;
- conversion succeeds through `convert_fits_to_tiff()`;
- the requested TIFF exists;
- the TIFF can be independently reopened using the project's established TIFF test dependency/mechanism;
- output shape is `(H, W, 3)` with source-derived height and width;
- output dtype is `uint16`;
- the source FIT/FITS remains unchanged.

Tests should avoid brittle exact-pixel assertions unless an existing Stage 4 contract makes them useful.

Stage 4 already validates RGB normalisation correctness. Stage 6.1c validates end-to-end integration of that subsystem.

---

## Required Tests

Add focused integration tests appropriate to the existing test structure.

Tests must cover at least:

1. real `stacked.fit` conversion through the public pipeline boundary;
2. real `stacked_mosaic.fit` conversion through the public pipeline boundary;
3. `RGB_IMAGE` classification;
4. source channels-first RGB representation where applicable;
5. output existence;
6. output channels-last `(H, W, 3)` layout;
7. `uint16` preservation;
8. independent TIFF reopening;
9. source-file preservation;
10. existing destination overwrite protection where relevant.

Existing Stage 6.1a unit tests may continue to provide isolated proof that `normalize_rgb_layout()` output is handed directly to `write_tiff()`.

Do not duplicate Stage 4's detailed normalisation tests.

---

## Files / Components Expected to Be Affected

Expected changes should remain small.

Likely files include:

- Stage 6 native-Seestar-RGB integration tests;
- `src/seestar_toolkit/conversion.py` only if a concrete deficiency is demonstrated;
- `docs/PROJECT_Notes.md` or architecture documentation only where required;
- `docs/change_documents/STAGE_6/STAGE_6.1c.md`;
- the intentionally modified `docs/CHANGELOG.md` in the eventual commit.

Existing FITS fixtures must remain unchanged.

Avoid unrelated refactoring.

---

## Documentation Requirements

Update documentation only where needed to record that the native Seestar stacked RGB route has been validated end-to-end through the public single-file pipeline.

Documentation must not imply that:

- Siril RGB validation is complete;
- CLI polish is complete;
- batch processing is complete;
- Stage 7 archive organisation is complete;
- broad Stage 8 dataset qualification is complete.

---

## Explicit Exclusions / Deferred Work

Stage 6.1c must not implement:

- raw Bayer work already completed in Stage 6.1b except where required to prevent regression;
- Siril RGB conversion validation — Stage 6.1d;
- CLI `convert` integration/polish — Stage 6.1e;
- batch conversion — Stage 6.1f;
- complete Stage 6 workflow validation — Stage 6.1g;
- Stage 6 closure — Stage 6.1h;
- archive directory creation;
- configurable archive hierarchy;
- movement/copying of original files;
- archive collision policy;
- archive missing-metadata behaviour;
- archive dry-run behaviour;
- Stage 7 functionality;
- broad Stage 8 real-dataset qualification;
- image enhancement;
- 8-bit output;
- packaging/release work.

If excluded work appears necessary, report it rather than implementing it.

---

## Validation Commands

Run at minimum:

```bash
pytest <relevant Stage 6.1c test files>
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

Stage 6.1c may be closed only when all of the following are satisfied:

1. The existing RGB_IMAGE production route has been assessed before unnecessary production changes are made.
2. `convert_fits_to_tiff()` remains the public single-file conversion boundary.
3. Real native Seestar `stacked.fit` converts successfully through that boundary.
4. Real native Seestar `stacked_mosaic.fit` converts successfully through that boundary.
5. Both real fixtures are classified through the existing Stage 2 subsystem as `FitsImageClass.RGB_IMAGE`.
6. The route uses the existing Stage 2 FITS reader.
7. Native Seestar source RGB layout is validated as expected for the existing fixtures.
8. RGB conversion uses the existing Stage 4 `normalize_rgb_layout()` implementation.
9. The conversion layer does not duplicate RGB axis/channel normalisation logic.
10. The normalised result is passed to the existing Stage 5 TIFF writer without new image transformation.
11. TIFF outputs exist at the explicitly requested destinations.
12. TIFF outputs can be independently reopened successfully.
13. TIFF outputs have `(H, W, 3)` channels-last RGB layout with source-derived dimensions.
14. TIFF output data type is `uint16`.
15. Conversion remains linear and introduces no stretching, gamma, white balance, colour correction, rescaling, clipping, float conversion, or 8-bit conversion.
16. Source FIT/FITS files remain present and unchanged.
17. Existing TIFF destination overwrite protection remains intact.
18. Stage 6.1c focused integration tests pass.
19. The complete project test suite passes.
20. Ruff passes.
21. Formatting validation for changed source/test files passes.
22. `git diff --check` passes.
23. Documentation accurately records native Seestar RGB-route completion where required.
24. Siril RGB remains explicitly deferred to Stage 6.1d.
25. No CLI batch, archive, Stage 7, Stage 8, or release work has crept into this sub-stage.
26. No unrelated refactoring or behavioural changes have been introduced.
27. Codex provides the required completion report and identifies deviations, assumptions, and blockers.

Every closure criterion must be reviewed individually before Stage 6.1c is approved for commit.

---

## Required Codex Completion Report

When complete, report:

- files changed;
- whether production conversion code required modification and why;
- implementation/integration summary;
- exact real native Seestar FITS fixtures used;
- source and output shapes/dtypes observed;
- tests added or changed;
- validation commands and results;
- closure criteria 1–27, individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers or unresolved issues.

Do not commit any changes.

---

## Stage Boundary / What Comes Next

Successful Stage 6.1c completion proves the native Seestar stacked RGB route end-to-end.

The next planned sub-stage is:

```text
Stage 6.1d — validate the Siril RGB conversion path
```

Stage 6.1d will specifically address the existing Siril `float32` RGB FITS representation and corresponding TIFF output path.

CLI polish remains Stage 6.1e.

Batch conversion remains Stage 6.1f.

Archive organisation remains Stage 7.
