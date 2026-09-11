# Seestar Toolkit — Stage 6.1b

## Validate and Complete the Raw Bayer Conversion Path

### Purpose

Stage 6.1b validates and, only where necessary, completes the first supported end-to-end single-file conversion route:

```text
raw Seestar FIT/FITS
    -> inspect/classify
    -> read image
    -> obtain Bayer pattern
    -> demosaic
    -> write TIFF
```

Stage 6.1a established `convert_fits_to_tiff(input_path, output_path) -> pathlib.Path` as the authoritative single-file conversion-pipeline boundary.

The raw-light orchestration already exists. Stage 6.1b must therefore begin by assessing that existing implementation rather than assuming new production code is required.

The goal is to prove that supported real Seestar raw Bayer FIT/FITS files pass correctly through the established pipeline and produce valid linear 16-bit RGB TIFF files.

---

## Starting Point / Prerequisite Commit

Stage 6.1b starts from:

```text
6c1ee7e Stage 6.1a: define conversion pipeline contract
```

Stages 1–5 and Stage 6.1a are complete.

`docs/CHANGELOG.md` is expected to contain the subsequently added Stage 6.1a entry as an intentional uncommitted modification. That state is normal and should ordinarily be included in the Stage 6.1b commit.

The authoritative specification for this sub-stage is:

```text
docs/change_documents/STAGE_6/STAGE_6.1b.md
```

---

## Background

The project already has the required raw-image components:

- Stage 2 FITS inspection/classification;
- Stage 2 FITS image reading;
- Stage 3 Bayer demosaicing;
- Stage 5 TIFF writing;
- Stage 6.1a single-file conversion orchestration.

The established model distinguishes:

- `FitsImageLayout.RAW_BAYER` — the low-level Bayer image layout;
- `FitsImageClass.RAW_LIGHT` — the supported high-level classification used by the conversion pipeline.

Stage 6.1b must preserve that distinction.

The existing conversion pipeline currently routes `FitsImageClass.RAW_LIGHT` through `demosaic()` and then `write_tiff()`.

---

## Required Work

### 1. Assess the Existing Raw Route First

Before changing production code, inspect the existing Stage 6.1a pipeline and relevant Stage 2, 3, and 5 APIs.

Determine whether the existing RAW_LIGHT route already satisfies the complete Stage 6.1b contract.

Do not rewrite, refactor, or duplicate working code simply because this roadmap step is labelled "implement raw Bayer conversion path."

If the production route is already correct, Stage 6.1b may consist primarily of stronger integration/real-data tests and documentation.

Any production-code change must address a concrete deficiency demonstrated by the Stage 6.1b requirements or tests.

---

### 2. End-to-End Raw Conversion Contract

For a supported raw Seestar light, the established `convert_fits_to_tiff()` pipeline must:

1. accept the FIT/FITS source path and explicit TIFF destination path;
2. inspect/classify the FITS file using the existing Stage 2 subsystem;
3. classify the supported raw light as `FitsImageClass.RAW_LIGHT`;
4. read the source image using the existing FITS reader;
5. obtain/use the Bayer pattern reported by the existing inspection metadata;
6. invoke the existing Stage 3 `demosaic()` implementation;
7. produce an `(H, W, 3)` `uint16` RGB array from the raw Bayer image;
8. pass that array unchanged to the existing Stage 5 TIFF writer;
9. create the requested TIFF output;
10. return the output `Path` according to the Stage 6.1a contract.

The conversion layer must remain orchestration only.

---

### 3. Bayer Pattern Handling

The pipeline must use the Bayer pattern obtained through the existing FITS inspection/metadata model.

For the existing real Seestar raw fixtures this is expected to be `GRBG`.

Do not:

- hard-code `GRBG` into the conversion pipeline;
- independently parse FITS headers inside the conversion layer;
- add a second Bayer-pattern interpretation mechanism.

Missing or unsupported Bayer-pattern behaviour must remain consistent with the established Stage 2/3 contracts and must fail explicitly rather than silently selecting a pattern.

---

### 4. Output Data Contract

A successfully converted raw Seestar light must produce a TIFF whose image data is:

```text
(H, W, 3)
uint16
RGB
```

The conversion must remain linear.

Stage 6.1b must not introduce:

- stretching;
- gamma;
- white balance;
- colour correction;
- rescaling;
- clipping;
- 8-bit conversion;
- unrelated dtype conversion.

The TIFF writer remains authoritative for TIFF encoding and destination-file protection.

---

### 5. Source Preservation

Conversion must not modify, rename, move, or delete the source FIT/FITS file.

Stage 7 will own original-file placement and archive-management behaviour.

Stage 6.1b may create only the explicitly requested TIFF output and normal temporary test artefacts managed by the test framework.

---

## Required Real-Data Validation

Stage 6.1b must use the project's existing real Seestar raw FITS fixtures.

At minimum validate:

- `light.fit`;
- at least one existing mosaic-session raw-light fixture, preferably one of:
  - `mosaic_1.fit`
  - `mosaic_4.fit`
  - `mosaic_6.fit`

If fixture paths/names differ in the current repository, use the equivalent existing files and report the exact fixtures used.

For each real-data conversion validated, confirm at minimum:

- source inspection produces the expected supported raw-light classification;
- the Bayer pattern is obtained from metadata rather than hard-coded;
- conversion succeeds through `convert_fits_to_tiff()`;
- the output TIFF exists;
- the TIFF can be reopened using the project's established TIFF-reading test dependency/mechanism;
- output shape is `(H, W, 3)` with dimensions corresponding to the source image;
- output dtype is `uint16`;
- the source FIT/FITS remains present and unchanged by the conversion operation.

Tests should avoid brittle assertions on exact demosaiced pixel values unless an existing established test contract makes such assertions appropriate.

Stage 3 already validates demosaicing correctness; Stage 6.1b validates integration of that subsystem into the complete raw conversion route.

---

## Required Tests

Add focused integration tests appropriate to the existing test layout.

Tests must cover at least:

1. real `light.fit` conversion through the public pipeline boundary;
2. real mosaic-session raw FITS conversion through the public pipeline boundary;
3. correct output existence;
4. correct output dimensions/channel layout;
5. `uint16` TIFF output;
6. source-file preservation;
7. use of metadata-derived Bayer information, either directly demonstrated by the real-data route or supported by the Stage 6.1a orchestration tests;
8. preservation of existing destination overwrite-protection behaviour where relevant to the raw end-to-end route.

Do not duplicate Stage 3's detailed demosaic algorithm tests.

Do not turn Stage 6.1b into broad Stage 8 dataset validation.

---

## Files / Components Expected to Be Affected

Expected changes should remain small.

Likely files include:

- Stage 6 conversion/integration tests;
- `src/seestar_toolkit/conversion.py` only if a concrete deficiency is found;
- documentation where necessary;
- `docs/change_documents/STAGE_6/STAGE_6.1b.md`;
- the intentionally modified `docs/CHANGELOG.md` as part of the eventual commit.

Existing FITS fixtures should not be modified.

Avoid unrelated refactoring.

---

## Documentation Requirements

Update project/architecture documentation only where Stage 6.1b establishes information not already recorded.

Documentation should make clear that the raw Seestar conversion route has now been validated end-to-end through the public single-file pipeline.

Do not prematurely describe the Seestar stacked RGB, Siril RGB, CLI batch, or Stage 7 archive routes as complete.

---

## Explicit Exclusions / Deferred Work

Stage 6.1b must not implement:

- Seestar stacked RGB conversion validation — Stage 6.1c;
- Siril RGB conversion validation — Stage 6.1d;
- CLI `convert` integration/polish — Stage 6.1e;
- batch conversion — Stage 6.1f;
- complete Stage 6 workflow validation — Stage 6.1g;
- Stage 6 closure — Stage 6.1h;
- archive directory creation;
- configurable `{target}/{location}/{date}` archive hierarchy;
- moving/copying source FITS into archives;
- archive collision handling;
- archive missing-metadata policy;
- archive dry-run behaviour;
- Stage 7 functionality;
- broad real-dataset qualification belonging to Stage 8;
- image enhancement;
- 8-bit TIFF output;
- packaging/release work.

If an excluded capability appears necessary, report it rather than implementing it.

---

## Validation Commands

Run at minimum:

```bash
pytest <relevant Stage 6.1b test files>
pytest
ruff check .
```

Also run the repository's established formatting check for files changed in this sub-stage.

Run:

```bash
git diff --check
```

No changes may be committed by Codex.

---

## Closure Criteria

Stage 6.1b may be closed only when all of the following are satisfied:

1. The existing RAW_LIGHT conversion implementation has been assessed before unnecessary production changes are made.
2. `convert_fits_to_tiff()` remains the public single-file conversion boundary.
3. A real Seestar `light.fit` fixture converts successfully through that boundary.
4. At least one real mosaic-session raw-light fixture converts successfully through that boundary.
5. Real raw fixtures are classified using the existing Stage 2 classification subsystem.
6. RAW_LIGHT conversion uses the existing Stage 2 FITS reader.
7. Bayer pattern information is obtained from existing FITS inspection metadata and is not hard-coded in the conversion layer.
8. RAW_LIGHT conversion uses the existing Stage 3 `demosaic()` implementation.
9. The demosaiced result is passed to the existing Stage 5 TIFF writer without new image transformation.
10. The resulting TIFF exists at the explicitly requested destination.
11. The resulting TIFF can be reopened successfully.
12. The resulting TIFF has `(H, W, 3)` RGB channel layout with dimensions corresponding to the source.
13. The resulting TIFF data type is `uint16`.
14. The conversion remains linear and introduces no stretching, gamma, white balance, colour correction, rescaling, clipping, or 8-bit conversion.
15. Source FIT/FITS files remain present and are not modified, renamed, moved, or deleted by conversion.
16. Existing TIFF destination overwrite protection remains intact.
17. Stage 6.1b integration tests pass.
18. The complete project test suite passes.
19. Ruff passes.
20. Formatting validation for changed source/test files passes.
21. `git diff --check` passes.
22. Documentation accurately records raw-route completion where required.
23. No Seestar RGB, Siril RGB, CLI batch, archive, Stage 7, Stage 8, or release work has crept into this sub-stage.
24. No unrelated refactoring or behavioural changes have been introduced.
25. Codex provides the required completion report and identifies any deviations, assumptions, or blockers.

Every closure criterion must be reviewed individually before Stage 6.1b is approved for commit.

---

## Required Codex Completion Report

When complete, report:

- files changed;
- whether production conversion code required modification and why;
- implementation/integration summary;
- exact real FITS fixtures used;
- tests added or changed;
- validation commands and results;
- closure criteria 1–25, individually marked satisfied/not satisfied;
- deviations;
- assumptions;
- blockers or unresolved issues.

Do not commit any changes.

---

## Stage Boundary / What Comes Next

Successful Stage 6.1b completion proves the raw Seestar Bayer route end-to-end.

The next planned sub-stage is:

```text
Stage 6.1c — implement/validate the Seestar RGB conversion path
```

Stage 6.1c will address already-demosaiced native Seestar RGB FITS input.

Siril RGB remains Stage 6.1d.

Batch conversion remains Stage 6.1f.

Archive organisation remains Stage 7.
