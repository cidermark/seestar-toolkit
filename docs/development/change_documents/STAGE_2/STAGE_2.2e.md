# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

|-----------------|---------------------------------------------|
| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Stage**       | 2.2e                                        |  
| **Title**       | Stage 2 Validation and Closure.             |
| **Document**    | STAGE 2.2e.md                               |
| **Version**     | **1.0**                                     |
| **Base Commit** | 9271283                                     |
| **Status**      | 🟢 Complete                                  |
| **Date**        | 2026-08-26                                  |
|-----------------|---------------------------------------------|

## Revision History

| Version | Date       | Description.   |
|---------|------------|----------------|
| 1.0     | 2026-08-26 | Initial issue. |

================================================================================
## STAGE OVERVIEW
================================================================================

### Objective

Validate the completed Stage 2 FITS inspection and classification subsystem
against both the automated test suite and the real Seestar FITS reference files.

This is a closure stage.

No production-code changes are planned unless validation exposes a genuine defect.

### Baseline

At the start of Stage 2.2e:

- `ruff check .` passes.
- `pytest` passes with 32 tests.
- Current HEAD is `9271283` — Stage 2.2d.
- `docs/CHANGELOG.md` contains an uncommitted documentation update.

### Stage 2 Capabilities to Validate

- FITS file opening and validation.
- 2-dimensional raw Bayer image support.
- 3-dimensional channels-first RGB image support.
- Unsupported image-layout rejection.
- Image dimensions, shape, dimensionality, datatype and bit depth.
- Bayer-pattern extraction.
- Core and expanded metadata extraction.
- Missing optional metadata handling.
- Invalid optional metadata handling.
- `EQMODE` metadata handling.
- Reliable high-level image classification:
  - `RAW_LIGHT`
  - `RGB_IMAGE`
  - `UNKNOWN`

### Real Reference Files

Validate:

- `tests/data/seestar/light.fit`
- `tests/data/seestar/eq.fit`
- `tests/data/seestar/mosaic.fit`
- `tests/data/seestar/stacked.fit`
- `tests/data/seestar/stacked_mosaic.fit`

================================================================================
# STEP 1
================================================================================

## Automated Validation

Run:

```bash
ruff check .
pytest
```

Expected:

```text
All checks passed!
32 passed
```

================================================================================
# STEP 2
================================================================================

## Real FITS Classification Validation

Run:

```bash
python - <<'PY'
from pathlib import Path

from seestar_toolkit.fits import inspect_fits

files = [
    "light.fit",
    "eq.fit",
    "mosaic.fit",
    "stacked.fit",
    "stacked_mosaic.fit",
]

root = Path("tests/data/seestar")

for name in files:
    result = inspect_fits(root / name)

    print(
        f"{name:20} "
        f"class={result.image_class.name:10} "
        f"type={result.image_type!s:8} "
        f"bayer={result.bayer_pattern!s:5} "
        f"eqmode={result.eq_mode!s:4} "
        f"size={result.width}x{result.height} "
        f"dtype={result.dtype}"
    )
PY
```

### Expected Classification

| File | Expected Class |
|------|----------------|
| `light.fit` | `RAW_LIGHT` |
| `eq.fit` | `RAW_LIGHT` |
| `mosaic.fit` | `RAW_LIGHT` |
| `stacked.fit` | `RGB_IMAGE` |
| `stacked_mosaic.fit` | `RGB_IMAGE` |

Expected tracking-mode evidence:

- normal Alt-Az samples: `EQMODE = 0`
- `eq.fit`: `EQMODE = 1`

Do not expect a special mosaic classification.

================================================================================
# STEP 3
================================================================================

## Stage 2 Objective Review

Confirm that Stage 2 now provides:

- Strongly typed FITS image models.
- Strongly typed inspection metadata.
- Raw Bayer and RGB image-layout recognition.
- Reliable image classification.
- Extraction of useful Seestar FITS metadata.
- Graceful handling of missing and invalid optional metadata.
- Real-data validation against representative Seestar FITS files.
- Developer inspection tools for future FITS investigation.

### Intentionally Deferred

The following are outside Stage 2 closure:

- Bayer demosaicing.
- RGB image processing.
- TIFF writing.
- Session/folder-level mosaic classification.
- Archive organisation.
- Derived stack-frame count.
- Firm interpretation of unverified `PROGRAM`, `BIAS` and `WIDECAM` semantics.
- Lunar and planetary capture-format investigation.

================================================================================
# STEP 4
================================================================================

## Documentation Closure

Update:

- `docs/PROJECT_Notes.md`
  - Mark Stage 2 complete.
  - Set Stage 3 as the current focus.
- `docs/CHANGELOG.md`
  - Ensure Stage 2.2d is recorded.
  - Add Stage 2.2e closure entry after the commit is created.
- `docs/change_documents/STAGE_2/STAGE_2.2e.md`
  - Mark status Complete.
  - Complete the checklist.
  - Record the final commit ID.

`ARCHITECTURE.md` and `SEESTAR_FITS_REFERENCE.md` only need changes if Stage 2
validation reveals something not already documented.

================================================================================
## COMPLETION CHECKLIST
================================================================================

- [X] Ruff passes
- [X] All pytest tests pass
- [X] `light.fit` validates as `RAW_LIGHT`
- [X] `eq.fit` validates as `RAW_LIGHT`
- [X] `mosaic.fit` validates as `RAW_LIGHT`
- [X] `stacked.fit` validates as `RGB_IMAGE`
- [X] `stacked_mosaic.fit` validates as `RGB_IMAGE`
- [X] `EQMODE = 0` / `1` evidence remains consistent
- [X] Stage 2 objectives reviewed
- [X] Deferred work recorded
- [X] `PROJECT_Notes.md` marks Stage 2 complete
- [X] `CHANGELOG.md` updated
- [X] `git diff` reviewed
- [ ] Working tree clean after commit

## Commit

Suggested commit message:

```text
Stage 2.2e: Validate and close Stage 2
```

================================================================================
## NEXT STAGE
================================================================================

Stage 3 — Bayer Demosaicing
