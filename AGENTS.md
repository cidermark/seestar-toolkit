# Seestar Toolkit — Codex Instructions

## Project Overview

Seestar Toolkit is a Python application for processing image data produced by the ZWO Seestar S50 smart telescope.

The project is being developed incrementally in clearly defined stages.

The initial processing pipeline is intended to:

1. Read Seestar FIT/FITS files.
2. Inspect and classify FITS image data and metadata.
3. Demosaic raw Bayer image data.
4. Preserve linear 16-bit RGB image data.
5. Produce output suitable for later astrophotography processing.
6. Eventually organise imaging sessions into a configurable archive structure.

Do not assume functionality beyond what is documented or already implemented.

---

## Project Documentation

Before making significant changes, consult the relevant documentation under `docs/development/`.

The main project documents are:

### `docs/development/PROJECT_Notes.md`

Contains:

- development stages;
- completed work;
- planned work;
- implementation notes;
- important project decisions.

Use this document to understand where the project currently is in its development plan.

### `docs/development/ARCHITECTURE.md`

Defines the intended architecture and component responsibilities.

Architectural changes should be consistent with this document.

Do not introduce a new architectural approach simply because it is convenient for the current task.

### `docs/development/CHANGELOG.md`

Records completed changes to the project.

Do not use the changelog as the primary source for future requirements.

### Development Environment Documentation

Additional development environment instructions may exist under `docs/development/`.

Use these when environment setup or development commands need to be understood.

---

## Development Approach

Development is deliberately incremental.

Work on **one explicitly requested development stage or sub-stage at a time**.

Do not implement functionality belonging to later stages unless explicitly requested.

For example, if asked to implement Stage 3.1a:

- implement Stage 3.1a only;
- do not anticipate and implement Stage 3.1b or Stage 3.2;
- do not perform unrelated refactoring.

Small, reviewable changes are preferred over large changes.

---

## Tests First

The project follows a test-first approach where practical.

For new behaviour:

1. Understand the existing implementation and tests.
2. Add or modify tests describing the required behaviour.
3. Implement the smallest change required to satisfy those tests.
4. Run the complete test suite.
5. Run Ruff checks.

Existing passing tests must continue to pass.

Do not weaken, delete or bypass existing tests merely to make a new implementation pass.

---

## Required Validation

Before reporting a coding task as complete, run:

```bash
pytest
```

and:

```bash
ruff check .
```

Report:

- files created;
- files modified;
- tests added or changed;
- pytest result;
- Ruff result;
- any remaining issues or assumptions.

If tests or Ruff fail, report the failure rather than describing the task as complete.

---

## Python Environment

The development environment uses Python 3.13.

Avoid introducing dependencies or language features that conflict with the Python version specified by the project configuration.

Check `pyproject.toml` before adding dependencies or changing tooling configuration.

Do not add a new dependency when the required functionality can reasonably be implemented using dependencies already present in the project.

---

## Source Layout

Application code is under:

```text
src/seestar_toolkit/
```

Tests are under:

```text
tests/
```

FITS-related functionality currently lives under:

```text
src/seestar_toolkit/fits/
```

with corresponding unit tests under:

```text
tests/unit/fits/
```

Follow the existing project structure and naming conventions.

---

## Image Processing Principles

Image-processing changes must preserve the scientific usefulness of the source data.

Unless a development stage explicitly requires otherwise:

- preserve linear image data;
- preserve 16-bit precision where applicable;
- do not stretch image data;
- do not apply automatic brightness adjustments;
- do not apply automatic contrast adjustments;
- do not apply colour correction;
- do not apply white balance;
- do not clip or normalise pixel values unnecessarily.

Processing stages should have clearly separated responsibilities.

For example, Bayer demosaicing should convert Bayer sensor data into RGB data. It should not also perform image stretching or output-file creation unless explicitly required by the relevant development stage.

---

## Seestar FITS Data

The project must support FIT/FITS data produced by the ZWO Seestar S50.

Known raw Seestar data may use a Bayer pattern such as:

```text
GRBG
```

Do not assume that every FITS file is raw Bayer data.

The FITS inspection subsystem should be used where appropriate to determine the characteristics of an input image.

Real Seestar FITS samples used by the test suite are located under the project's test-data structure.

Do not modify real test FITS files.

---

## Archive Layout

Future archive organisation must not hard-code a single directory hierarchy.

The archive hierarchy is intended to be configurable.

A possible layout is:

```text
{target}/{location}/{date}
```

but alternatives such as:

```text
{location}/{date}/{target}
```

must remain possible.

Consult `docs/development/ARCHITECTURE.md` for the current architectural definition before implementing archive organisation.

Do not implement archive functionality unless the requested development stage requires it.

---

## Scope Control

Before editing code:

1. Inspect the relevant existing source.
2. Inspect the corresponding tests.
3. Check the relevant project documentation.
4. Determine the smallest set of files that need changing.

Avoid:

- unrelated refactoring;
- formatting unrelated files;
- renaming existing interfaces without need;
- speculative features;
- premature optimisation;
- adding dependencies without justification.

If the requested change conflicts with the documented architecture or existing requirements, stop and report the conflict rather than silently changing the design.

---

## Git

Do not create commits unless explicitly instructed to do so.

Do not amend existing commits.

Do not push changes.

Do not change branches unless explicitly instructed.

Before beginning work, inspect the working tree with:

```bash
git status
```

### Expected CHANGELOG modification

`docs/development/CHANGELOG.md` is normally expected to have an uncommitted modification.

The project workflow is:

1. A development change is committed.
2. The commit ID and commit message are then recorded in `docs/development/CHANGELOG.md`.
3. This leaves `docs/development/CHANGELOG.md` intentionally modified while the next development task is performed.
4. The CHANGELOG update is included with a subsequent appropriate commit.

Therefore:

- do not treat a modified `docs/development/CHANGELOG.md` as an unexpected dirty-working-tree condition;
- do not revert or discard its existing changes;
- preserve existing CHANGELOG changes when performing development work;
- only modify `docs/development/CHANGELOG.md` when explicitly instructed or when the requested development step specifically requires it.

Other existing uncommitted changes may belong to the user.

Do not overwrite, revert, stage or otherwise modify unrelated existing changes.

When work is complete, report the files changed so they can be reviewed before committing.

---

## Documentation

Do not update project documentation automatically unless:

- the requested development step requires it; or
- explicitly instructed.

When documentation changes appear necessary but are outside the requested scope, report the recommended changes instead of making them.

---

## Working With the User

The user retains control over architectural and development decisions.

When requirements are ambiguous and the choice would materially affect the design, explain the issue and request a decision rather than making a large assumption.

Small implementation details that clearly follow existing project conventions may be resolved without asking.

Prefer clear, maintainable implementations over clever or unnecessarily complex solutions.

---

## Current Development Context

The FITS inspection engine was completed and validated at the end of Stage 2.

Stage 2 closed with commit:

```text
3f67cfc — Stage 2.2e: Validate and close Stage 2
```

The next planned development area is:

```text
Stage 3 — Bayer Demosaicing
```

Consult `docs/development/PROJECT_Notes.md` for the authoritative current development status before starting work.

This section is informational only. If the repository history or project documentation shows that development has progressed beyond this point, follow the newer project state rather than this note.