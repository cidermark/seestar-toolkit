# Seestar FITS Header Reference

## Purpose

This document records FITS image layouts and header keywords observed in
Seestar-generated FITS files. It is the authoritative observed-data
reference for the Seestar Toolkit project.

## Important

Raw capture FITS and processed stacked FITS use different image layouts:

-   Raw captures: 2-dimensional Bayer arrays.
-   Stacked images: 3-dimensional channels-first RGB arrays.

Toolkit representations:

-   `FitsImageLayout.RAW_BAYER`
-   `FitsImageLayout.RGB`

## Public header sanitisation

The nine active real-image fixtures now contain synthetic site coordinates,
serial-bearing device names and timestamps. Their pixels and processing
characteristics are unchanged. Header examples and observed-capture sections
below record historical observations, not current public-fixture private
metadata. See [the fixture privacy review](../../tests/data/PRIVACY_REVIEW.md).

## Active fixture provenance

Stage 9.1d preflight replaced the real Siril mosaic with a 5,760-byte
synthetic Siril-style FITS. The active dimensions below describe that
replacement. Historical observations elsewhere describe the original real
`(3, 5437, 4183)` mosaic; those records remain unchanged.
See [test-data documentation](../../tests/data/README.md#synthetic-siril-mosaic)
for generation, metadata and contract details. The replacement is generated
by Astropy and contains no original capture metadata.

## Files Analysed

  ----------------------------------------------------------------------------------------
  File                   Capture Type                           Notes
  ---------------------- -------------------------------------- --------------------------
  `light.fit`            Raw light                              IC 434; LP; 10s; GRBG
  `mosaic.fit`           Raw mosaic light                       NGC 6992; LP; 10s; GRBG
  `eq.fit`               Raw light captured in equitorial mode  IC 434; LP; 10s; GRBG
  `stacked.fit`          Seestar stacked image                  Linear RGB; channels-first
  `stacked_mosaic.fit`   Seestar stacked mosaic                 Linear RGB; channels-first
  `siril_stacked.fit`    Siril reference stack                  Linear RGB; float32
  `siril_stacked_mosaic.fit` Synthetic Siril-style mosaic       Linear RGB; float32
  ----------------------------------------------------------------------------------------

Firmware values have not yet been recorded reliably. The observed `PROGRAM` 
keyword must not be assumed to be the Seestar firmware version without verification.

## HDU Analysis Reference

  ---------------------------------------------------------------------------------------------
  File                   Array Dimensions    NumPy Shape         Data Type    Interpretation
  ---------------------- ------------------- ------------------- ------------ -----------------
  `light.fit`            2D                  `(1920, 1080)`      `uint16`     Raw Bayer frame
  `mosaic.fit`           2D                  `(1920, 1080)`      `uint16`     Raw Bayer frame
  `eq.fit`               2D                  `(1920, 1080)`      `uint16`     Raw Bayer frame
  `stacked.fit`          3D                  `(3, 3840, 2160)`   `uint16`     RGB linear image
  `stacked_mosaic.fit`   3D                  `(3, 2304, 1296)`   `uint16`     RGB linear image
  `siril_stacked.fit`    3D                  `(3, 1920, 1080)`   `float32`    RGB linear image
  `siril_stacked_mosaic.fit` 3D              `(3, 17, 11)`   `float32`    RGB linear image
  ---------------------------------------------------------------------------------------------

Channels-first RGB shape is `(channels, height, width)`.

Therefore:

-   `stacked.fit` → width 2160, height 3840.
-   `stacked_mosaic.fit` → width 1296, height 2304.
-   `siril_stacked.fit` → width 1080, height 1920.
-   `siril_stacked_mosaic.fit` → width 11, height 17 (synthetic replacement).

## Raw Seestar Header Keyword Reference

  ---------------------------------------------------------------------------------------
  Keyword      Example Value                  Description / Current Interpretation
  ------------ ------------------------------ -------------------------------------------
  `APERTURE`   `5.0`                          Telescope aperture value
  `BAYERPAT`   `GRBG`                         Bayer colour filter pattern
  `BIAS`       `471`                          Exact semantics not yet confirmed
  `BITPIX`     `16`                           FITS storage bit depth
  `BSCALE`     `1`                            FITS data scaling
  `BZERO`      `32768`                        FITS unsigned-integer offset
  `CCD-TEMP`   `17.125`                       Sensor temperature
  `CCDXBIN`    `1`                            X binning
  `CCDYBIN`    `1`                            Y binning
  `CREATOR`    `ZWO Seestar S50`              Creating application/device
  `DATE-EXP`   `2026-01-03T22:02:50.610018`   Exposure end timestamp
  `DATE-OBS`   `2026-01-03T22:02:39.686812`   Observation/capture timestamp
  `DEC`        `-2.448889`                    Declination
  `EQMODE`     `0` or `1`                     Tracking mode: 0 = Alt-Az, 1 = Equatorial
  `EXPOSURE`   `10.0`                         Individual exposure duration
  `EXPTIME`    `10.0`                         Appears to duplicate individual exposure duration
  `EXTEND`     `True`                         Standard FITS extension flag
  `FILTER`     `LP`                           Selected filter
  `FOCALLEN`   `250.0`                        Focal length
  `FOCUSPOS`   `1537`                         Focus position
  `GAIN`       `80`                           Camera gain
  `IMAGETYP`   `Light`                        Image type
  `INSTRUME`   `Seestar S50`                  Instrument
  `NAXIS`      `2`                            Number of image axes for raw captures
  `NAXIS1`     `1080`                         FITS first-axis size
  `NAXIS2`     `1920`                         FITS second-axis size
  `OBJECT`     `IC 434`                       Target/object name
  `PRODUCER`   `ZWO`                          Producer
  `PROGRAM`    `6.45` / `8.46`                Meaning requires verification
  `RA`         `85.595835`                    Right ascension as stored by Seestar
  `SIMPLE`     `True`                         Standard FITS conformance flag
  `SITELAT`    `51.428`                       Capture site latitude
  `SITELONG`   `-0.753306`                    Capture site longitude
  `TELESCOP`   `S50_b90071df`                 Telescope/device identifier
  `TOTALEXP`   `10.0`                         Total exposure value
  `WIDECAM`    `0`                            Wide-camera indicator; purpose unconfirmed
  `XBINNING`   `1`                            X binning
  `XORGSUBF`   `0`                            X subframe origin
  `XPIXSZ`     `2.90000009536743`             X pixel size
  `YBINNING`   `1`                            Y binning
  `YORGSUBF`   `0`                            Y subframe origin
  `YPIXSZ`     `2.90000009536743`             Y pixel size
  ---------------------------------------------------------------------------------------

Standard FITS `COMMENT` records were also present.

## Observed Raw Capture Examples

### `light.fit`

-   Object: IC 434
-   Exposure: 10.0 s
-   Gain: 80
-   Bayer: GRBG
-   Filter: LP
-   Telescope: `S50_b90071df`
-   Instrument: Seestar S50
-   `EQMODE`: 0
-   `TOTALEXP`: 10.0
-   Shape: `(1920, 1080)`

### `mosaic.fit`

-   Object: NGC 6992
-   Exposure: 10.0 s
-   Gain: 80
-   Bayer: GRBG
-   Filter: LP
-   Telescope: `S50_99643794`
-   Instrument: Seestar S50
-   `EQMODE`: 0
-   `TOTALEXP`: 10.0
-   Shape: `(1920, 1080)`

The raw mosaic has the same array dimensions and Bayer layout as the
standard raw light. Mosaic classification must not be inferred merely
from raw image dimensions.

## Metadata Interpretation Notes

### Exposure

`EXPOSURE` and `EXPTIME` have so far been observed with identical values
and are currently treated as duplicate representations of individual
exposure duration.

`TOTALEXP` is intended to represent total exposure. Where valid stacked
metadata provides both values, a frame count may be derivable as
`TOTALEXP / EXPOSURE`.

### Bayer Pattern

Observed raw Seestar S50 captures use `GRBG`. The toolkit should
continue reading `BAYERPAT` rather than assume every future file
necessarily uses the same pattern.

Observed Seestar stacked RGB FITS may also retain `IMAGETYP=Light` and
`BAYERPAT=GRBG`. These header values do not by themselves identify raw
Bayer image data; the actual FITS array layout must also be considered.

### RGB Layout

Observed Seestar stacked FITS files use `(3, height, width)`. Stage
2.2b.2 added reader support specifically for this layout. Generic
3-dimensional arrays are not automatically treated as RGB.

Observed Seestar standard and mosaic stacks use channels-first `uint16` RGB.
Observed Siril standard and mosaic stacks use channels-first `float32` RGB.
The current reader preserves these shapes, dtype precision and numerical
values; it does not move the channel axis.

Stage 4 defines `(height, width, 3)` as the common toolkit RGB representation.
Stage 4 layout normalization moves the channel axis while preserving RGB
channel order, values and dtype precision. The observed Siril values are within
`[0, 1]`, but this is not a universal range requirement for floating-point RGB
FITS data. Standard and mosaic stacks require no separate core RGB path.

Orientation metadata differed between the original real Siril fixtures. The standard stack
contains `ROWORDER=BOTTOM-UP` and mirror-related processing history, while the
mosaic stack contains plate-solved rotational WCS without equivalent mirror
evidence. These findings do not establish a safe orientation correction, so
orientation changes remain outside the Stage 4 RGB handling contract. The active
synthetic mosaic retains absent `ROWORDER` and invented rotated TAN WCS;
exact pixel checks enforce unchanged orientation, without claiming real plate solving.

### Mosaic Identification

The analysed raw standard and mosaic lights have the same shape. Mosaic
status therefore cannot be inferred from raw image dimensions.

Six additional raw FITS files known to originate from independent Seestar
mosaic sessions were inspected. All six were 2-dimensional `(1920, 1080)`
`uint16` Bayer frames using normalized `GRBG`, and all demosaiced successfully
through the same processing path as ordinary raw lights.

None of those six files contained a `MOSAIC` keyword. Mosaic-session origin
therefore cannot currently be inferred reliably from that header field and
requires external capture/session context or other explicit evidence.

A Seestar mosaic capture session can result from expanding the capture frame
beyond the normal field of view, rotating the capture frame, or both. The
observed raw subframes themselves remain ordinary raw Bayer light frames.

### Tracking Mode

`EQMODE` has been observed with value `0`. A known equatorial capture is
still required before assigning definitive meanings to all values.

### Firmware / Program Version

Observed `PROGRAM` values include `6.45` and `8.46`. These have not been
verified as firmware versions.

## Unknown / Partially Understood Keywords

  Keyword     Example          Investigation
  ----------- ---------------- ----------------------------------------------
  `BIAS`      `471`            Confirm exact Seestar meaning
  `PROGRAM`   `6.45`, `8.46`   Confirm meaning
  `WIDECAM`   `0`              Confirm purpose; may reflect shared codebase

## Capture-Mode Notes

-   Solar video and timelapse have been observed to create MP4 output
    rather than individual FITS files.
-   Lunar output is believed to behave similarly but requires
    confirmation.
-   Planetary capture output remains to be investigated.
-   Mosaic-session raw subframes have been observed to retain the same
    2-dimensional `uint16` `GRBG` Bayer layout as standard raw lights.
-   Reference Siril preprocessing scripts use the same debayer operation for
    standard and mosaic-session Seestar lights. Mosaic-specific behaviour
    appears later in the workflow during plate solving/registration rather
    than during Bayer conversion.
-   The reviewed Siril scripts perform normalization and RGB equalisation
    during stacking, not during debayering.

## Further Investigation

-   Add a verified equatorial FITS sample.
-   Record and compare complete headers from Seestar stacked FITS files.
-   Verify `PROGRAM`, `EQMODE`, `BIAS` and `WIDECAM`.
-   Confirm Lunar and planetary output formats.
-   Record firmware information separately when verified.
-   Investigate why the standard Siril Seestar preprocessing script applies
    `mirrorx_single result` while the mosaic preprocessing script does not.
