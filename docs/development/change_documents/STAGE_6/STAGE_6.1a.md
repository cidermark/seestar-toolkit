# Seestar Toolkit — Stage 6.1a

## Define Conversion Pipeline Contract

### Purpose

Stage 6.1a defines the architectural and behavioural contract for the Seestar Toolkit conversion pipeline.

Stages 2–5 established the individual subsystems required to convert supported FIT/FITS image data into TIFF output:

- Stage 2 — FITS inspection and classification
- Stage 3 — Bayer demosaicing
- Stage 4 — RGB image handling and normalisation
- Stage 5 — TIFF output

Stage 6 begins integrating those existing capabilities into a user-facing conversion workflow.

This sub-stage must define the conversion pipeline contract and orchestration boundary before later Stage 6 sub-stages implement the individual conversion routes and CLI/batch behaviour.

Stage 6.1a is intentionally architectural and contract-focused. It must not implement later Stage 6 functionality prematurely.

---

## Starting Point / Prerequisites

The required project baseline is:

- Stages 1–5 complete.
- Stage 5 closure commit:
  - `75f5c92 Stage 5.1f: validate and close Stage 5`
- Documentation housekeeping commit:
  - `980a38a DOC-6: reorganize change_documents directory`
- Roadmap documentation update:
  - `b4a6477 DOC-7: add archive organisation stage to roadmap`

`docs/CHANGELOG.md` contains intentional uncommitted documentation entries created after the most recent documentation commits.

That existing modified state is expected and must not be treated as an unexpected dirty-working-tree condition.

The Stage 6 change-document directory must exist as:

```text
docs/change_documents/STAGE_6/
```

This document must be stored as:

```text
docs/change_documents/STAGE_6/STAGE_6.1a.md
```

---

## Stage 6 Context

The current roadmap is:

- Stage 6 — Command-line polish and batch processing
- Stage 7 — Archive organisation and file management
- Stage 8 — Testing with real Seestar datasets
- Stage 9 — Packaging and release

Stage 6 establishes reliable single-file and batch FITS-to-TIFF conversion.

Stage 7 will build on Stage 6 and will own archive hierarchy creation, original/generated file placement, configurable archive layouts, metadata-derived archive paths, collision handling, missing-metadata policy, copy/move behaviour, dry-run behaviour, and batch archive organisation.

Stage 6.1a must preserve this boundary.

---

## Architectural Principle

The conversion pipeline owns orchestration only.

It must coordinate the existing Stage 2–5 components rather than duplicate or reimplement their image-processing or file-writing logic.

Conceptually:

```text
FITS input
   |
   v
read / inspect / classify
   |
   +---- RAW_BAYER ----> demosaic --------+
   |                                      |
   +---- RGB_IMAGE ----> RGB normalise ---+
                                          |
                                          v
                                     RGB image
                                          |
                                          v
                                     TIFF writer
```

Later Stage 6 sub-stages will implement the concrete routes.

Stage 6.1a must define the contract those later implementations will follow.

---

## Required Implementation Contract

### 1. Conversion Pipeline API

Introduce a clearly named conversion-pipeline API or service boundary suitable for later use by:

- the single-file CLI conversion command;
- batch conversion;
- future Stage 7 archive organisation.

The exact module/class/function naming may follow the existing project conventions, but the interface must be simple and explicit.

The API must represent conversion of one supported FIT/FITS input into one TIFF output.

The contract must clearly define:

- input path;
- output path;
- successful return value;
- raised/returned failure behaviour;
- responsibility for orchestration;
- responsibility boundaries between the pipeline and existing subsystems.

No batch API is required in Stage 6.1a.

---

### 2. Supported Classification Routing

The contract must define routing based on the Stage 2 FITS classification results.

At minimum, later pipeline implementation must support:

#### RAW_BAYER

Route through:

1. FITS inspection/classification;
2. extraction/use of the Bayer pattern;
3. Stage 3 demosaicing;
4. Stage 5 TIFF writing.

Expected image representation after demosaicing:

```text
(H, W, 3) uint16
```

#### RGB_IMAGE

Route through:

1. FITS inspection/classification;
2. Stage 4 RGB normalisation;
3. Stage 5 TIFF writing.

The existing RGB subsystem remains responsible for preserving supported source data types and normalising channel order/layout.

The pipeline must not perform its own RGB axis conversion or numeric conversion.

---

### 3. Unsupported Classification Behaviour

The pipeline contract must explicitly define how unsupported or unconvertible classifications are handled.

Unsupported classifications must fail clearly rather than silently selecting an arbitrary conversion route.

Failure behaviour must use the project's established exception/error conventions where practical.

Stage 6.1a may add a conversion-specific exception type if required by the existing architecture, but must not introduce an unnecessarily large exception hierarchy.

---

### 4. Existing Subsystem Reuse

The pipeline must reuse the authoritative Stage 2–5 APIs.

It must not duplicate:

- FITS reading logic;
- FITS classification logic;
- Bayer-pattern interpretation already owned by the relevant subsystem;
- demosaicing algorithms;
- RGB channels-first/channels-last normalisation;
- image dtype conversion;
- TIFF encoding;
- TIFF overwrite-protection behaviour.

The pipeline may prepare arguments and select which subsystem to call.

---

### 5. Path Responsibilities

The Stage 6.1a contract must treat input and output as explicit paths.

The pipeline may validate or normalise path-like inputs where consistent with existing APIs.

It must not:

- derive archive directories;
- derive target/location/date paths;
- move or copy original FITS files;
- create Stage 7 archive structures;
- invent batch output-directory policy.

Single-file output naming defaults belong to the later CLI-integration sub-stage unless a minimal internal contract is strictly required now.

---

### 6. Data Preservation

The pipeline contract must preserve the data model established in Stages 3–5.

No new image transformation is permitted.

In particular, the pipeline must not add:

- stretching;
- white balance;
- colour correction;
- gamma adjustment;
- rescaling;
- clipping;
- 8-bit conversion;
- arbitrary dtype conversion.

The purpose of the pipeline is orchestration, not image enhancement.

---

## Files / Components Expected to Be Affected

The exact implementation should follow the current repository structure, but Stage 6.1a is expected to affect only a small set of components such as:

- a new or existing conversion/orchestration module under `src/seestar_toolkit/`;
- focused unit tests for the pipeline contract;
- `docs/change_documents/STAGE_6/STAGE_6.1a.md`;
- documentation only where necessary to record the new architectural boundary;
- the existing intentionally modified `docs/CHANGELOG.md` may be included in the eventual Stage 6.1a commit.

Codex must avoid unrelated refactoring.

---

## Required Tests

Stage 6.1a tests must focus on the conversion-pipeline contract and orchestration boundary.

Tests should use mocks, stubs, or minimal synthetic data where appropriate.

At minimum, tests must verify:

1. the conversion API accepts the required input/output path contract;
2. RAW_BAYER classification selects the Bayer/demosaic route;
3. RGB_IMAGE classification selects the RGB-normalisation route;
4. the selected route passes its result to the TIFF writer;
5. unsupported classification fails explicitly;
6. Stage 2–5 subsystem functions are reused rather than replicated;
7. exceptions from underlying conversion components are not silently swallowed;
8. the API has predictable successful return behaviour.

Tests must avoid making Stage 6.1a into full real-data integration testing.

---

## Real-Data Validation

No new real-Seestar-data validation is required for Stage 6.1a.

Real-data conversion is intentionally deferred to later Stage 6 sub-stages.

Existing real-data fixtures must not be modified unnecessarily.

---

## Documentation Requirements

Stage 6.1a must ensure the project documentation reflects the new conversion-pipeline architectural boundary where required.

Documentation must make clear that:

- the pipeline orchestrates existing FITS, demosaic, RGB, and TIFF subsystems;
- Stage 6 will later add CLI and batch conversion;
- archive organisation remains Stage 7 work.

Do not duplicate large sections of existing project documentation if a concise architectural update is sufficient.

---

## Explicit Exclusions / Deferred Work

Stage 6.1a must not implement:

- complete raw Bayer end-to-end conversion;
- complete Seestar RGB end-to-end conversion;
- complete Siril RGB end-to-end conversion;
- CLI `convert` command integration or polish;
- batch conversion;
- recursive directory traversal;
- batch summaries;
- archive directory creation;
- `{target}/{location}/{date}` or any other archive hierarchy;
- metadata-derived archive placement;
- movement or copying of original files;
- archive collision handling;
- archive dry-run behaviour;
- Stage 7 functionality;
- Stage 8 real-dataset validation work;
- image enhancement;
- 8-bit TIFF output;
- packaging/release changes.

If any excluded capability appears necessary, Codex must report it as a blocker or recommendation rather than implementing it.

---

## Validation Commands

Codex must run, at minimum:

```bash
pytest <relevant Stage 6.1a test files>
pytest
ruff check .
```

If formatting tools are already part of the repository's normal validation workflow, run the appropriate existing check as well.

Do not introduce new tooling solely for this sub-stage.

---

## Closure Criteria

Stage 6.1a may be closed only when all of the following are satisfied:

1. A clear single-file conversion-pipeline API/service boundary exists.
2. The API contract explicitly represents one FIT/FITS input and one TIFF output.
3. RAW_BAYER routing is defined and selects the existing Bayer/demosaic path.
4. RGB_IMAGE routing is defined and selects the existing RGB-normalisation path.
5. The pipeline hands the routed RGB result to the existing TIFF writer.
6. Unsupported classifications fail explicitly and predictably.
7. The pipeline does not duplicate Stage 2 FITS inspection/classification logic.
8. The pipeline does not duplicate Stage 3 demosaicing logic.
9. The pipeline does not duplicate Stage 4 RGB-normalisation logic.
10. The pipeline does not duplicate Stage 5 TIFF-writing logic.
11. Existing subsystem exceptions are not silently swallowed.
12. Successful return behaviour is defined and tested.
13. No new image enhancement, scaling, stretching, colour processing, or dtype-conversion behaviour has been introduced.
14. Unit tests cover both supported routing branches and unsupported classification behaviour.
15. Stage 6.1a tests pass.
16. The complete project test suite passes.
17. Ruff passes.
18. Documentation accurately records the pipeline/orchestration boundary where required.
19. Stage 7 archive-organisation responsibilities remain explicitly outside this sub-stage.
20. No later Stage 6 implementation work has been pulled into Stage 6.1a.
21. No unrelated refactoring or behavioural changes have been introduced.
22. Codex provides the required completion report and identifies any deviations, assumptions, or blockers.

Every criterion must be reviewed individually before Stage 6.1a is approved for commit.

---

## Required Codex Completion Report

When implementation is complete, Codex must report:

- files changed;
- implementation summary;
- tests added or changed;
- validation commands run and their results;
- each closure criterion, numbered 1–22, with a clear satisfied/not-satisfied status;
- any deviations from this specification;
- any assumptions made;
- any blockers or unresolved issues.

Codex must not commit any changes.

---

## Stage Boundary / What Comes Next

Successful completion of Stage 6.1a establishes the conversion-pipeline contract only.

The planned subsequent Stage 6 work is:

- Stage 6.1b — implement raw Bayer conversion path;
- Stage 6.1c — implement Seestar RGB conversion path;
- Stage 6.1d — implement Siril RGB conversion path;
- Stage 6.1e — integrate and polish single-file `convert` CLI;
- Stage 6.1f — add batch conversion;
- Stage 6.1g — validate Stage 6 conversion and batch workflows;
- Stage 6.1h — validate and close Stage 6.

Stage 7 archive organisation must not begin as part of Stage 6.1a.
