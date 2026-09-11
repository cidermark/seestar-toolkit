# Seestar Toolkit

# Change Document

================================================================================
## DOCUMENT CONTROL
================================================================================

|-----------------|---------------------------------------------|
| Field           | Value                                       |
|-----------------|---------------------------------------------|
| **Stage**       | 2.2c.                                       |  
| **Title**       | Expand FITS Inspection Metadata.            |
| **Document**    | STAGE 2.2c.md.                              |
| **Version**     | **1.0**                                     |
| **Base Commit** | 616bc87                                     |
| **Status**      | 🟢 Complete                                  |
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

Expand `FitsInspection` so the toolkit exposes additional useful
metadata confirmed in real Seestar FITS files.

This stage is limited to direct metadata extraction and normalisation.
It does not add image-processing behaviour or speculative capture
classification.

### Metadata Added

  FITS Keyword   FitsInspection field       Type
  -------------- -------------------------- -------------------
  IMAGETYP       `image_type`               `str | None`
  TOTALEXP       `total_exposure_seconds`   `float | None`
  DATE-EXP       `exposure_ended_at`        `datetime | None`
  RA             `ra_degrees`               `float | None`
  DEC            `dec_degrees`              `float | None`
  SITELAT        `site_latitude`            `float | None`
  SITELONG       `site_longitude`           `float | None`
  EQMODE         `eq_mode`                  `int | None`
  CCD-TEMP       `ccd_temperature`          `float | None`
  FOCUSPOS       `focus_position`           `int | None`
  APERTURE       `aperture`                 `float | None`
  FOCALLEN       `focal_length`             `float | None`
  CREATOR        `creator`                  `str | None`
  PRODUCER       `producer`                 `str | None`
  PROGRAM        `program`                  `str | None`
  WIDECAM        `wide_camera`              `int | None`

`PROGRAM` is deliberately stored as text because its exact meaning
remains unverified.

`EQMODE` is stored as the raw integer. Real captures establish
`0 = Alt-Az` and `1 = Equatorial`.

### Files Modified

-   `src/seestar_toolkit/fits/models.py`
-   `src/seestar_toolkit/fits/inspector.py`
-   `tests/unit/fits/test_inspection_models.py`
-   `tests/unit/fits/test_inspector.py`

### Files NOT Modified

-   `src/seestar_toolkit/fits/reader.py`
-   `src/seestar_toolkit/fits/__init__.py`
-   `src/seestar_toolkit/fits/exceptions.py`

### Expected Outcome

-   Existing inspection metadata remains unchanged.
-   Additional confirmed Seestar metadata is exposed.
-   Missing optional metadata produces `None`.
-   Invalid optional numeric/date values produce `None`.
-   `PROGRAM` is preserved without assigning an unverified meaning.
-   Ruff clean and all tests passing.

================================================================================
# STEP 1
================================================================================

## File: `src/seestar_toolkit/fits/models.py`

### CHANGE 1

Locate `class FitsInspection:` and its existing final field:

``` python
captured_at: datetime | None
```

Insert immediately AFTER:

``` python
image_type: str | None
total_exposure_seconds: float | None
exposure_ended_at: datetime | None
ra_degrees: float | None
dec_degrees: float | None
site_latitude: float | None
site_longitude: float | None
eq_mode: int | None
ccd_temperature: float | None
focus_position: int | None
aperture: float | None
focal_length: float | None
creator: str | None
producer: str | None
program: str | None
wide_camera: int | None
```

Do not alter existing fields.

================================================================================
# STEP 2
================================================================================

## File: `src/seestar_toolkit/fits/inspector.py`

### CHANGE 1

Locate the existing `FitsInspection(` constructor inside
`inspect_fits()`.

After:

``` python
captured_at=_read_datetime(header, "DATE-OBS"),
```

Insert:

``` python
image_type=_read_text(header, "IMAGETYP"),
total_exposure_seconds=_read_float(header, "TOTALEXP"),
exposure_ended_at=_read_datetime(header, "DATE-EXP"),
ra_degrees=_read_float(header, "RA"),
dec_degrees=_read_float(header, "DEC"),
site_latitude=_read_float(header, "SITELAT"),
site_longitude=_read_float(header, "SITELONG"),
eq_mode=_read_int(header, "EQMODE"),
ccd_temperature=_read_float(header, "CCD-TEMP"),
focus_position=_read_int(header, "FOCUSPOS"),
aperture=_read_float(header, "APERTURE"),
focal_length=_read_float(header, "FOCALLEN"),
creator=_read_text(header, "CREATOR"),
producer=_read_text(header, "PRODUCER"),
program=_read_text(header, "PROGRAM"),
wide_camera=_read_int(header, "WIDECAM"),
```

### CHANGE 2

Locate the complete `_read_float()` helper.

Insert immediately AFTER it:

``` python
def _read_int(header: Header, key: str) -> int | None:
    value = header.get(key)

    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None
```

================================================================================
# STEP 3
================================================================================

## File: `tests/unit/fits/test_inspection_models.py`

### CHANGE 1

For every direct `FitsInspection(` construction, add these arguments
after `captured_at=...`:

``` python
image_type="Light",
total_exposure_seconds=10.0,
exposure_ended_at=datetime(2026, 7, 16, 2, 11, 47),
ra_degrees=314.0,
dec_degrees=31.5,
site_latitude=51.428,
site_longitude=-0.753,
eq_mode=0,
ccd_temperature=20.0,
focus_position=1500,
aperture=5.0,
focal_length=250.0,
creator="ZWO Seestar S50",
producer="ZWO",
program="8.46",
wide_camera=0,
```

### CHANGE 2

In the creation/value test add:

``` python
assert inspection.image_type == "Light"
assert inspection.total_exposure_seconds == 10.0
assert inspection.eq_mode == 0
assert inspection.focus_position == 1500
assert inspection.program == "8.46"
assert inspection.wide_camera == 0
```

Do not remove existing assertions.

================================================================================
# STEP 4
================================================================================

## File: `tests/unit/fits/test_inspector.py`

### CHANGE 1

In `test_inspect_fits_extracts_metadata`, add these header values:

``` python
header["IMAGETYP"] = "Light"
header["TOTALEXP"] = 120.0
header["DATE-EXP"] = "2026-07-16T02:11:47Z"
header["RA"] = 314.374995
header["DEC"] = 31.583889
header["SITELAT"] = 51.428
header["SITELONG"] = -0.753501
header["EQMODE"] = 1
header["CCD-TEMP"] = 17.5
header["FOCUSPOS"] = 1636
header["APERTURE"] = 5.0
header["FOCALLEN"] = 250.0
header["CREATOR"] = "ZWO Seestar S50"
header["PRODUCER"] = "ZWO"
header["PROGRAM"] = "8.46"
header["WIDECAM"] = 0
```

### CHANGE 2

Add these result assertions:

``` python
assert result.image_type == "Light"
assert result.total_exposure_seconds == 120.0
assert result.exposure_ended_at == datetime(
    2026, 7, 16, 2, 11, 47, tzinfo=timezone.utc
)
assert result.ra_degrees == 314.374995
assert result.dec_degrees == 31.583889
assert result.site_latitude == 51.428
assert result.site_longitude == -0.753501
assert result.eq_mode == 1
assert result.ccd_temperature == 17.5
assert result.focus_position == 1636
assert result.aperture == 5.0
assert result.focal_length == 250.0
assert result.creator == "ZWO Seestar S50"
assert result.producer == "ZWO"
assert result.program == "8.46"
assert result.wide_camera == 0
```

If the file currently imports only `datetime`, change:

``` python
from datetime import datetime
```

to:

``` python
from datetime import datetime, timezone
```

### CHANGE 3

In `test_inspect_fits_handles_missing_optional_metadata`, add:

``` python
assert result.image_type is None
assert result.total_exposure_seconds is None
assert result.exposure_ended_at is None
assert result.ra_degrees is None
assert result.dec_degrees is None
assert result.site_latitude is None
assert result.site_longitude is None
assert result.eq_mode is None
assert result.ccd_temperature is None
assert result.focus_position is None
assert result.aperture is None
assert result.focal_length is None
assert result.creator is None
assert result.producer is None
assert result.program is None
assert result.wide_camera is None
```

### CHANGE 4

In `test_inspect_fits_handles_invalid_optional_values`, add:

``` python
header["TOTALEXP"] = "not-a-number"
header["DATE-EXP"] = "not-a-date"
header["RA"] = "unknown"
header["DEC"] = "unknown"
header["SITELAT"] = "unknown"
header["SITELONG"] = "unknown"
header["EQMODE"] = "unknown"
header["CCD-TEMP"] = "unknown"
header["FOCUSPOS"] = "unknown"
header["APERTURE"] = "unknown"
header["FOCALLEN"] = "unknown"
header["WIDECAM"] = "unknown"
```

Add assertions:

``` python
assert result.total_exposure_seconds is None
assert result.exposure_ended_at is None
assert result.ra_degrees is None
assert result.dec_degrees is None
assert result.site_latitude is None
assert result.site_longitude is None
assert result.eq_mode is None
assert result.ccd_temperature is None
assert result.focus_position is None
assert result.aperture is None
assert result.focal_length is None
assert result.wide_camera is None
```

================================================================================
# STEP 5
================================================================================

## VALIDATION

Run:

``` bash
ruff check .
pytest
```

Then:

``` bash
python tools/inspect_fits.py tests/data/seestar/light.fit
python tools/inspect_fits.py tests/data/seestar/eq.fit
python tools/inspect_fits.py tests/data/seestar/stacked.fit
```

The developer tool does not need to display every new field in this
stage. These runs confirm that the expanded inspection model has not
broken known real FITS layouts.

================================================================================
## COMPLETION CHECKLIST
================================================================================

-   [X] All file changes applied
-   [X] `ruff check .` passes
-   [X] `pytest` passes
-   [X] `light.fit` inspection succeeds
-   [X] `eq.fit` inspection succeeds
-   [X] `stacked.fit` inspection succeeds
-   [X] `git diff` reviewed
-   [X] Change document updated to Complete

## Commit

Suggested commit message:

``` text
Stage 2.2c: Expand FITS inspection metadata
```

================================================================================
\## NEXT STAGE
================================================================================

After validation, define Stage 2.2d around reliable FITS/image
classification.

Derived values such as stack frame count are intentionally deferred
until the underlying metadata model has been validated against the real
Seestar samples.
