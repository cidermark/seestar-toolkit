# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

|-----------------|---------------------------------------------|
| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Stage**       | 2.2d.                                       |  
| **Title**       | Add Reliable FITS Image Classification      |
| **Document**    | STAGE 2.2d.md.                              |
| **Version**     | **1.0**                                     |
| **Base Commit** | 3efd84f                                     |
| **Status**      | 🟢 Complete.                                |
| **Date**        | 2026-08-26                                  |
|-----------------|---------------------------------------------|

## Revision History

  Version   Date         Description
  --------- ------------ ----------------
  1.0       2026-08-26   Initial issue.

================================================================================
## STAGE OVERVIEW
================================================================================

### Objective

Add a small, explicit classification layer on top of the existing FITS
reader and inspection metadata.

Classification must use only evidence available from the FITS file
itself.

This stage must NOT:

-   infer mosaic status from image dimensions;
-   infer session type from folder names;
-   assume `PROGRAM` is a firmware version;
-   infer capture modes that are not supported by observed FITS
    evidence.

### Reliable Classification Rules

  Classification   Required Evidence
  ---------------- -------------------------------------------------------
  `RAW_LIGHT`      `FitsImageLayout.RAW_BAYER` and `IMAGETYP == "Light"`
  `RGB_IMAGE`      `FitsImageLayout.RGB`
  `UNKNOWN`        Anything else

`RGB_IMAGE` is deliberately generic. Although the observed Seestar RGB
FITS files are stacked products, the FITS layout alone does not prove
how the RGB image was created.

Mosaic status remains outside this classifier.

### Files Modified

-   `src/seestar_toolkit/fits/models.py`
-   `src/seestar_toolkit/fits/inspector.py`
-   `src/seestar_toolkit/fits/__init__.py`
-   `tests/unit/fits/test_inspection_models.py`
-   `tests/unit/fits/test_inspector.py`

### Files NOT Modified

-   `src/seestar_toolkit/fits/reader.py`
-   `src/seestar_toolkit/fits/exceptions.py`
-   `tools/inspect_fits.py`

### Expected Outcome

-   Add strongly typed `FitsImageClass`.
-   Add `image_class` to `FitsInspection`.
-   Classify known raw Seestar lights as `RAW_LIGHT`.
-   Classify supported RGB FITS images as `RGB_IMAGE`.
-   Return `UNKNOWN` when evidence is insufficient.
-   Preserve all existing reader and metadata behaviour.
-   Ruff clean and all tests passing.

================================================================================
# STEP 1
================================================================================

## File: `src/seestar_toolkit/fits/models.py`

### CHANGE 1

Locate:

``` python
class FitsImageLayout(Enum):
```

Insert immediately AFTER the complete `FitsImageLayout` enum:

``` python
class FitsImageClass(Enum):
    """High-level classification derived from reliable FITS evidence."""

    RAW_LIGHT = auto()
    RGB_IMAGE = auto()
    UNKNOWN = auto()
```

### CHANGE 2

Locate `class FitsInspection:`.

Insert immediately after:

``` python
image_type: str | None
```

Add:

CHECK!!!!!!!

``` python
image_class: FitsImageClass
```

================================================================================
# STEP 2
================================================================================

## File: `src/seestar_toolkit/fits/inspector.py`

### CHANGE 1

Locate the import from `.models`.

Add `FitsImageClass` and `FitsImageLayout` to that import if they are
not already present.

### CHANGE 2

Locate the start of `inspect_fits()` after the image has been read and
its header obtained.

Before constructing `FitsInspection`, add:

``` python
image_type = _read_text(header, "IMAGETYP")
image_class = _classify_image(
    layout=image.layout,
    image_type=image_type,
)
```

### CHANGE 3

Inside `FitsInspection(` locate:

``` python
image_type=_read_text(header, "IMAGETYP"),
```

Replace with:

``` python
image_type=image_type,
image_class=image_class,
```

### CHANGE 4

Insert this helper before the existing header-reading helper functions:

``` python
def _classify_image(
    *,
    layout: FitsImageLayout,
    image_type: str | None,
) -> FitsImageClass:
    if layout is FitsImageLayout.RGB:
        return FitsImageClass.RGB_IMAGE

    if (
        layout is FitsImageLayout.RAW_BAYER
        and image_type is not None
        and image_type.casefold() == "light"
    ):
        return FitsImageClass.RAW_LIGHT

    return FitsImageClass.UNKNOWN
```

================================================================================
# STEP 3
================================================================================

## File: `src/seestar_toolkit/fits/__init__.py`

### CHANGE 1

Locate the import from `.models`.

Add:

``` python
FitsImageClass
```

### CHANGE 2

Locate `__all__`.

Add:

``` python
"FitsImageClass",
```

================================================================================
# STEP 4
================================================================================

## File: `tests/unit/fits/test_inspection_models.py`

### CHANGE 1

Locate the import from `seestar_toolkit.fits`.

Add:

``` python
FitsImageClass
```

### CHANGE 2

For every direct `FitsInspection(` construction, add:

``` python
image_class=FitsImageClass.RAW_LIGHT,
```

immediately after `image_type=...`.

If a construction deliberately represents an unknown image, use:

``` python
image_class=FitsImageClass.UNKNOWN,
```

### CHANGE 3

In the normal construction/value test add:

``` python
assert inspection.image_class is FitsImageClass.RAW_LIGHT
```

================================================================================
# STEP 5
================================================================================

## File: `tests/unit/fits/test_inspector.py`

### CHANGE 1

Locate the import from `seestar_toolkit.fits`.

Add:

``` python
FitsImageClass
```

### CHANGE 2

In `test_inspect_fits_extracts_metadata(...)` add:

``` python
assert result.image_class is FitsImageClass.RAW_LIGHT
```

### CHANGE 3

Add:

``` python
def test_inspect_fits_classifies_rgb_image(tmp_path: Path) -> None:
    image_path = tmp_path / "rgb.fit"
    data = np.zeros((3, 10, 20), dtype=np.uint16)

    fits.writeto(image_path, data)

    result = inspect_fits(image_path)

    assert result.image_class is FitsImageClass.RGB_IMAGE
```

### CHANGE 4

Add:

``` python
def test_inspect_fits_classifies_unknown_raw_image(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "unknown.fit"
    data = np.zeros((10, 20), dtype=np.uint16)

    fits.writeto(image_path, data)

    result = inspect_fits(image_path)

    assert result.image_class is FitsImageClass.UNKNOWN
```

### CHANGE 5

In the missing-optional-metadata test, add:

``` python
assert result.image_class is FitsImageClass.UNKNOWN
```

================================================================================
# STEP 6
================================================================================

## VALIDATION

Run:

``` bash
ruff check .
pytest
```

Then verify:

``` bash
python tools/inspect_fits.py tests/data/seestar/light.fit
python tools/inspect_fits.py tests/data/seestar/eq.fit
python tools/inspect_fits.py tests/data/seestar/stacked.fit
python tools/inspect_fits.py tests/data/seestar/stacked_mosaic.fit
```

Expected API classifications:

  File                   Expected Classification
  ---------------------- -------------------------
  `light.fit`            `RAW_LIGHT`
  `eq.fit`               `RAW_LIGHT`
  `stacked.fit`          `RGB_IMAGE`
  `stacked_mosaic.fit`   `RGB_IMAGE`

Do not classify either mosaic sample as a special mosaic class in this
stage.

================================================================================
\## COMPLETION CHECKLIST
================================================================================

-   [X] All file changes applied
-   [X] `ruff check .` passes
-   [X] `pytest` passes
-   [X] Real reference files inspect successfully
-   [ ] `git diff` reviewed
-   [ ] Change document updated to Complete

## Commit

Suggested commit message:

``` text
Stage 2.2d: Add reliable FITS image classification
```

================================================================================
\## NEXT STAGE
================================================================================

After Stage 2.2d is complete, review Stage 2 against its original
objectives.

If no material FITS-inspection/classification gaps remain, Stage 2.2e
should be a validation/closure stage rather than another feature stage.
