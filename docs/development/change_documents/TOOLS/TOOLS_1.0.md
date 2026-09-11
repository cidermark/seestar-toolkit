# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

|-----------------|---------------------------------------------|
| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Stage**       | Tools-1                                     |
| **Title**       | Refresh FITS Inspection Utility             |
| **Document**    | TOOLS_1.0.md.                               |
| **Version**     | **1.0**                                     |
| **Base Commit** | dd77745                                     |
| **Status**      | 🟢 Complete                                  |
| **Date**        | 2026-08-25                                  |
|-----------------|---------------------------------------------|

---

## Revision History

|---------|------------|----------------|
| Version | Date       | Description    |
|---------|------------|----------------|
| 1.0     | 2026-08-25 | Initial issue. |

================================================================================
## STAGE OVERVIEW
================================================================================

### Objective

Correct the stale FitsInspection attribute names used by tools/inspect_fits.py.

---

### Base Evidence

Real Seestar reference files established the following layouts:

|----------------|-------------------|-----------|
| File Type      | NumPy Shape       | Layout    |
|----------------|-------------------|-----------|
| Light          | `(1920, 1080)`    | Raw Bayer |
| EQ             | `(1920, 1080)`    | Raw Bayer |
| Stacked        | `(3, 3840, 2160)` | RGB       |
|----------------|-------------------|-----------|

---

### Files Modified

✔ `tools/inspect_fits.py`

---

### Files NOT Modified

No Production modules are changed

---

### Expected Outcome

- Correct the exposure labelling.
- Correct the capture labelling.

---

### Expected Validation
```text
ruff check .
```

Expected:
```text
All checks passed!
```

```text
pytest
```

Expected:
```text
All tests passed.
```

================================================================================
# STEP 1
================================================================================

## CHANGE 1

### Locate

```python
print_field("Exposure", metadata.exposure)
```

### Replace

```python
print_field("Exposure", metadata.exposure_seconds)
```

---

## CHANGE 2

### Locate

```python
print_field("Captured", metadata.capture_time)
```

### Replace the entire block with

```python
print_field("Captured", metadata.captured_at)
```


### File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] File saved

================================================================================
# STEP 3
================================================================================

## VALIDATION

### Run Ruff
```bash
ruff check .
```

Expected:
```text
All checks passed!
```

If Ruff reports only safe formatting/import-order issues, use:
```bash
ruff check . --fix
```

and then rerun:
```bash
ruff check .
```

---

### Run Unit Tests
```bash
pytest
```

Expected:
```text
All tests passed.
```

---

### Real Seestar Verification

After the automated tests pass, run:
```bash
python tools/inspect_fits.py tests/data/seestar/light.fit
python tools/inspect_fits.py tests/data/seestar/eq.fit
python tools/inspect_fits.py tests/data/seestar/stacked.fit
```

================================================================================
## COMPLETION CHECKLIST
================================================================================

### Validation

- [X] All file changes applied
- [X] `ruff check .` passes
- [X] `pytest` passes
- [X] `light.fit` successfully read by toolkit
- [X] `eq.fit` successfully read by toolkit
- [X] `stacked.fit` successfully read by toolkit
- [X] `git diff` reviewed
- [X] Change document updated to Complete

---

## Commit

### Commit ID

```text
1a1f209
```

### Commit Message

```text
Stage 2.2b.2: Support RGB FITS images in the reader
```

---

## Notes

```text

```
