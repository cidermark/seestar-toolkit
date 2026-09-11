# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

|-----------------|---------------------------------------------|
| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Stage**       | 2.2b.2                                      |
| **Title**       | Support RGB FITS Images in the FITS Reader  |
| **Document**    | STAGE 2.2b.2.md                             |
| **Version**     | **1.0**                                     |
| **Base Commit** | bacfe07                                     |
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

Extend `read_fits_image()` so that the FITS reader supports both Seestar image
layouts identified during Stage 2.2a½:

- 2-dimensional raw Bayer FITS images.
- 3-dimensional RGB FITS images stored as `(3, height, width)`.

The existing behaviour for 2-dimensional FITS images must remain unchanged.

RGB support is deliberately limited to the layout observed in real Seestar
stacked FITS files. Other 3-dimensional layouts are not accepted at this stage.

---

### Base Evidence

Real Seestar reference files established the following layouts:

|----------------|-------------------|-----------|
| File Type      | NumPy Shape       | Layout    |
|----------------|-------------------|-----------|
| Light          | `(1920, 1080)`    | Raw Bayer |
| Mosaic light   | `(1920, 1080)`    | Raw Bayer |
| Stacked        | `(3, 3840, 2160)` | RGB       |
| Stacked mosaic | `(3, 2304, 1296)` | RGB       |
|----------------|-------------------|-----------|

---

### Files Modified

✔ `src/seestar_toolkit/fits/reader.py`
✔ `tests/unit/fits/test_reader.py`

---

### Files NOT Modified

✘ `src/seestar_toolkit/fits/models.py`
✘ `src/seestar_toolkit/fits/inspector.py`
✘ `src/seestar_toolkit/fits/__init__.py`
✘ `src/seestar_toolkit/fits/exceptions.py`
✘ `tests/unit/fits/test_models.py`
✘ `tools/inspect_fits.py`
✘ `tools/astropy_hdu_viewer.py`

---

### Expected Outcome

- Preserve support for existing 2-dimensional raw Bayer FITS images.
- Recognise `(3, height, width)` FITS arrays as `FitsImageLayout.RGB`.
- Populate the correct logical image width and height for RGB images.
- Preserve the complete original NumPy shape in `FitsImageData.shape`.
- Preserve the correct dimensionality in `FitsImageData.ndim`.
- Continue rejecting unsupported FITS array layouts.
- Finish the stage with Ruff clean and all tests passing.

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

## FILE CHANGES

### File

`src/seestar_toolkit/fits/reader.py`

### Reason

The current reader accepts only arrays where `ndim == 2`.

Real Seestar stacked FITS files use a 3-dimensional channels-first RGB layout:

```text
(3, height, width)
```

The reader must recognise both supported layouts and populate
`FitsImageData.layout`, `width`, `height`, `shape`, and `ndim` correctly.

---

## CHANGE 1

### Locate the function docstring at the start of

```python
def read_fits_image(path: Path) -> FitsImageData:
```

It currently describes reading the first **two-dimensional** image and says that
`MissingImageDataError` is raised when no two-dimensional image data exists.

### Replace the complete function docstring with

```python
"""Read the first supported image from a FITS file.

The HDUs are inspected in order. The first HDU containing either a
two-dimensional image or a three-dimensional channels-first RGB image
is returned.

Args:
    path: Path to the FITS file.

Returns:
    The image data and associated FITS metadata.

Raises:
    InvalidFitsFileError: If the file cannot be opened as a FITS file.
    MissingImageDataError: If the FITS file contains no supported image data.
"""
```

---

## CHANGE 2

### Locate this block inside `read_fits_image()`

```python
data = np.asarray(hdu.data)

if data.ndim != 2:
    continue

image_data = data.copy()
height, width = image_data.shape
```

### Replace the entire block with

```python
data = np.asarray(hdu.data)

if data.ndim == 2:
    layout = FitsImageLayout.RAW_BAYER
    height, width = data.shape
elif data.ndim == 3 and data.shape[0] == 3:
    layout = FitsImageLayout.RGB
    _, height, width = data.shape
else:
    continue

image_data = data.copy()
```

### Important

Do not accept a generic 3-dimensional array.

For Stage 2.2b.2, an RGB FITS image is supported **only** when:

```python
data.ndim == 3 and data.shape[0] == 3
```

This matches the real Seestar stacked FITS files analysed in Stage 2.2a½.

---

## CHANGE 3

### Locate the `FitsImageData` constructor in the same function

It currently contains:

```python
layout=FitsImageLayout.RAW_BAYER,
```

### Replace that single line with

```python
layout=layout,
```

Do not change the existing:

```python
shape=image_data.shape,
ndim=image_data.ndim,
```

or any other constructor arguments.

---

## CHANGE 4

### Locate all instances of `contains no two-dimensional image data`

### Replace with

```python
    contains no supported image data
```

---

### File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] CHANGE 3 applied
- [X] CHANGE 4 applied
- [X] File saved

================================================================================
# STEP 2
================================================================================

## FILE CHANGES

### File

`tests/unit/fits/test_reader.py`

### Reason

Extend reader tests to verify the new RGB FITS behaviour and confirm that
unsupported image layouts are still rejected.

---

## CHANGE 1

### Locate the existing import from `seestar_toolkit.fits`

Add `FitsImageLayout` to that import.

For example, if the current import is:

```python
from seestar_toolkit.fits import (
    InvalidFitsFileError,
    MissingImageDataError,
    read_fits_image,
)
```

### Replace with

```python
from seestar_toolkit.fits import (
    FitsImageLayout,
    InvalidFitsFileError,
    MissingImageDataError,
    read_fits_image,
)
```

---

## CHANGE 2

### Locate

```python
def test_read_fits_image_reads_primary_hdu(tmp_path: Path) -> None:
```

### Add these assertions to the existing assertions in that test

```python
assert result.layout is FitsImageLayout.RAW_BAYER
assert result.shape == (3, 4)
assert result.ndim == 2
```

The existing test creates:

```python
np.arange(12, dtype=np.uint16).reshape(3, 4)
```

so the expected shape is `(3, 4)`.

Do not change the existing assertions.

---

## CHANGE 3

### Insert a new test immediately AFTER

```python
def test_read_fits_image_reads_primary_hdu(...)
```

and before the next existing test.

### Insert

```python
def test_read_fits_image_reads_rgb_primary_hdu(tmp_path: Path) -> None:
    image_path = tmp_path / "rgb.fit"
    expected_data = np.arange(
        3 * 4 * 5,
        dtype=np.uint16,
    ).reshape(3, 4, 5)

    fits.writeto(image_path, expected_data)

    result = read_fits_image(image_path)

    assert result.path == image_path
    assert result.hdu_index == 0
    assert result.layout is FitsImageLayout.RGB
    assert result.shape == (3, 4, 5)
    assert result.ndim == 3
    assert result.width == 5
    assert result.height == 4
    assert result.dtype == np.dtype(np.uint16)
    assert result.bit_depth == 16
    np.testing.assert_array_equal(result.data, expected_data)
```

---

## CHANGE 4

### Locate the existing test

```python
def test_read_fits_image_rejects_file_without_image_data(
```

or the existing test that checks `MissingImageDataError`.

Any assertion matching the previous exception text:

```text
contains no two-dimensional image data
```

must be updated to:

```text
contains no supported image data
```

Do this for **every** test in `test_reader.py` that checks the old
`MissingImageDataError` message.

---

## CHANGE 5

### Add the following new test near the existing unsupported/non-2D tests

```python
def test_read_fits_image_rejects_unsupported_3d_data(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "unsupported-3d.fit"

    fits.writeto(
        image_path,
        np.zeros((4, 10, 20), dtype=np.uint16),
    )

    with pytest.raises(
        MissingImageDataError,
        match="contains no supported image data",
    ):
        read_fits_image(image_path)
```

### Reason

This verifies that merely being 3-dimensional is not enough.

Only a channels-first 3-plane RGB array is accepted during this stage.

---

### File Completion Checklist

- [X] CHANGE 1 applied
- [X] CHANGE 2 applied
- [X] CHANGE 3 applied
- [X] CHANGE 4 applied
- [X] CHANGE 5 applied
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

The exact test count may increase from the previous stage because this stage
adds new reader tests.

---

### Real Seestar Verification

After the automated tests pass, run:

```bash
python tools/inspect_fits.py tests/data/seestar/stacked.fit
```

and:

```bash
python tools/inspect_fits.py tests/data/seestar/stacked_mosaic.fit
```

Expected high-level results:

```text
stacked.fit
layout      : RGB
shape       : (3, 3840, 2160)
width       : 2160
height      : 3840
ndim        : 3
```

```text
stacked_mosaic.fit
layout      : RGB
shape       : (3, 2304, 1296)
width       : 1296
height      : 2304
ndim        : 3
```

If `tools/inspect_fits.py` does not currently print `layout`, `shape`, or `ndim`,
do **not** modify the tool during this stage. Successful completion without the
previous `MissingImageDataError` is sufficient evidence that the toolkit reader
now accepts the files.

================================================================================
## COMPLETION CHECKLIST
================================================================================

### Validation

- [X] All file changes applied
- [X] `ruff check .` passes
- [X] `pytest` passes
- [X] `stacked.fit` successfully read by toolkit
- [X] `stacked_mosaic.fit` successfully read by toolkit
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

================================================================================
## NEXT STAGE
================================================================================

The next Stage 2 task should build on the now-generalised FITS reader and
continue image inspection/classification using the explicit
`FitsImageLayout.RAW_BAYER` and `FitsImageLayout.RGB` values.

The exact next-stage scope should be confirmed after Stage 2.2b.2 validation
against the real Seestar reference files.
