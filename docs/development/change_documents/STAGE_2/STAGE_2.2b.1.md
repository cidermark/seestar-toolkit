# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

| Field           | Value                                        |
|-----------------|----------------------------------------------|
| **Stage**       | 2.2b.1                                       |
| **Title**       | Extend FITS Image Model for Multiple Layouts |
| **Document**    | STAGE 2.2b.1.md                              |
| **Version**     | **1.1**                                      |
| **Base Commit** | e746bbe                                      |
| **Status**      | 🟢 Complete                                  |
| **Date**        | 2026-08-03                                   |

---

## Revision History

| Version | Date       | Description                                                  |
|---------|------------|--------------------------------------------------------------|
| 1.0     | 2026-08-03 | Initial issue                                                |
| 1.1     | 2026-08-03 | Clarified target classes, target tests and change locations. |
| 1.2     | 2026-08-04 | Expanded stage to include reader.py updates so the project   |
|         |            | finishes with a passing test suite.                          |


================================================================================
## STAGE OVERVIEW
================================================================================

### Objective

### Objective

Extend the FITS data model and FITS reader so that the toolkit can distinguish
between raw Bayer acquisition images and processed RGB images while maintaining
full compatibility with existing functionality.

- Raw Bayer acquisition FITS images.
- Processed RGB FITS images.

This stage modifies **only the FITS data model**.

There are **no behavioural changes**.

---

### Files Modified

✔ `src/seestar_toolkit/fits/models.py`
✔ `src/seestar_toolkit/fits/__init__.py`
✔ `tests/unit/fits/test_models.py`
✔ `src/seestar_toolkit/fits/reader.py`

---

### Files NOT Modified

✘ `src/seestar_toolkit/fits/inspector.py`
✘ `src/seestar_toolkit/fits/exceptions.py`
✘ `tools/inspect_fits.py`
✘ `tools/astropy_hdu_viewer.py`

---

### Expected Outcome
- Introduce an explicit distinction between raw Bayer and RGB FITS images.
- Extend `FitsImageData` to describe image layout.
- Update the FITS reader to populate the extended data model.
- Maintain existing toolkit functionality and public API.
- Complete the stage with a clean `ruff` check and all tests passing.

---

### Expected Validation
```text
ruff check .
```

Expected:
```
All checks passed.
```

```text
pytest
```

Expected:
```
All tests passed.

Stage 2.2b.2 updates the reader.
```

================================================================================
# STEP 1
================================================================================
## FILE CHANGES
================================================================================

## File

`src/seestar_toolkit/fits/models.py`

## Reason

Introduce an explicit image layout so that all future code can determine
whether a FITS image represents raw Bayer data or processed RGB data
without inspecting the NumPy array.

---

## CHANGE 1

### Locate

```python
from dataclasses import dataclass
from pathlib import Path
```

### Replace with

```python
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
```

---

## CHANGE 2

### Locate the dataclass

```python
@dataclass(slots=True)
class FitsImageData:
```

### Insert immediately BEFORE this class

```python
class FitsImageLayout(Enum):
    """Semantic layout of image data stored in a FITS file."""

    RAW_BAYER = auto()
    RGB = auto()
```

> **Important**
>
> There are two dataclasses in this file.
>
> **Modify ONLY**
>
> `FitsImageData`
>
> **Do NOT modify**
>
> `FitsInspection`

---

## CHANGE 3

### Locate the field definitions inside **FitsImageData**.
The first field currently is:

```python
path: Path
```

### Replace the beginning of the field definitions with:

```python
layout: FitsImageLayout
shape: tuple[int, ...]

path: Path
hdu_index: int

width: int
height: int

ndim: int

dtype: np.dtype
bit_depth: int

header: Header
data: np.ndarray
```

> Do **not** modify:
>
> - class declaration
> - docstring
> - methods
> - properties

## File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] CHANGE 3 applied
- [X] File saved

================================================================================
# STEP 2
================================================================================
## FILE CHANGES
================================================================================

## File

`tests/unit/fits/test_models.py`

## Reason

Update all tests that construct a `FitsImageData` object.

---

## CHANGE 1

### Locate

```python
from seestar_toolkit.fits import FitsImageData
```

### Replace with

```python
from seestar_toolkit.fits import (
    FitsImageData,
    FitsImageLayout,
)
```

---

## CHANGE 2

Insert immediately before the first test in the file.

```python
def test_fits_image_layout_enum() -> None:
    """Verify supported FITS image layouts."""

    assert FitsImageLayout.RAW_BAYER.name == "RAW_BAYER"
    assert FitsImageLayout.RGB.name == "RGB"
```

---

## CHANGE 3

There are currently **two** tests that construct a `FitsImageData`
instance.

Update **both** tests.

### Test 1

```python
def test_fits_image_data_creation():
```

Add these constructor arguments:

```python
layout=FitsImageLayout.RAW_BAYER,
shape=(1920, 1080),
ndim=2,
```

Immediately after the existing assertions add:

```python
assert image.layout is FitsImageLayout.RAW_BAYER
assert image.shape == (1920, 1080)
assert image.ndim == 2
```

---

### Test 2

```python
def test_fits_image_data_is_immutable():
```

Also add:

```python
layout=FitsImageLayout.RAW_BAYER,
shape=(1920, 1080),
ndim=2,
```

to the constructor.

**Do not add any new assertions.**

The purpose of this test remains unchanged.

## File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] CHANGE 3 applied
- [X] File saved

================================================================================
# STEP 3
================================================================================
## FILE CHANGES
================================================================================

## File
src/seestar_toolkit/fits/__init__.py

## Reason
FitsImageLayout now exists inside models.py, but the package’s public interface (seestar_toolkit.fits) 
doesn’t export it.

---

## CHANGE 1

### Locate 1
```python
from .models import
```

### Add
add 'FitsImageLayout' to the list og imports.

## CHANGE 2

### Locate 2
```python
__all__ = [
```

### Add
```python
"FitsImageLayout",
```

## File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] File saved

================================================================================
# STEP 4
================================================================================
## FILE CHANGES
================================================================================

## File

`src/seestar_toolkit/fits/reader.py`

## Reason

Introduce an explicit image layout so that all future code can determine
whether a FITS image represents raw Bayer data or processed RGB data
without inspecting the NumPy array.

---

## CHANGE 1

### Locate

```python
from .models import FitsImageData
```

### Replace with

```python
from .models import FitsImageData, FitsImageLayout
```

---

## CHANGE 2

### Locate the dataclass

```text
Locate the return FitsImageData( statement.
```
It will look something like :
```python
return FitsImageData(
    path=source_path,
    hdu_index=hdu_index,
    width=width,
    height=height,
    dtype=image_data.dtype,
    bit_depth=image_data.dtype.itemsize * 8,
    header=hdu.header.copy(),
    data=image_data,
)
```
### Replace with

```python
return FitsImageData(
    layout=FitsImageLayout.RAW_BAYER,
    shape=image_data.shape,
    path=source_path,
    hdu_index=hdu_index,
    width=width,
    height=height,
    ndim=image_data.ndim,
    dtype=image_data.dtype,
    bit_depth=image_data.dtype.itemsize * 8,
    header=hdu.header.copy(),
    data=image_data,
)
```

---

## File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] File saved

================================================================================
## COMPLETION CHECKLIST
================================================================================

## Validation

- [X] `ruff check .`
- [X] `pytest`
- [X] `git diff` reviewed

---

## Commit

Commit ID

```text
bacfe07
```

Commit Message

```text
Stage 2.2b.1: Extend FITS image model for multiple layouts
```

---

## Notes

```
```

================================================================================
## NEXT STAGE
================================================================================

**Stage 2.2b.2**

Update the FITS reader to populate the new data model while preserving
existing raw Bayer FITS behaviour.