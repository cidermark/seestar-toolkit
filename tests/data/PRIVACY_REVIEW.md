# Stage 9.1d FITS fixture privacy review

All nine real-data fixtures are **SAFE AFTER SANITISATION** in the working
tree. Header-only sanitisation was sufficient; no synthetic image replacement
was necessary. The approved 5,760-byte synthetic Siril mosaic is unchanged.
This is a FITS-fixture review, not clearance of the entire repository or index.

## Inventory and remediation

The fields listed below were replaced, not merely hidden. All file sizes are
unchanged. Every changed card has the comment `Synthetic public fixture value`.

| Fixture | Classification | Sensitive fields replaced | Resulting bytes |
| --- | --- | --- | ---: |
| `tests/data/reference/siril_stacked.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE`, `DATE-OBS`, `EXPSTART`, `EXPEND` | 24,888,960 |
| `tests/data/seestar/eq.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 4,152,960 |
| `tests/data/seestar/light.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 4,152,960 |
| `tests/data/seestar/mosaic.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 4,152,960 |
| `tests/data/seestar/mosaic_1.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS` | 4,152,960 |
| `tests/data/seestar/mosaic_4.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 4,152,960 |
| `tests/data/seestar/mosaic_6.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `DATE-OBS` | 4,152,960 |
| `tests/data/seestar/stacked.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 49,775,040 |
| `tests/data/seestar/stacked_mosaic.fit` | SAFE AFTER SANITISATION | `SITELAT`, `SITELONG`, `TELESCOP`, `DATE-OBS`, `DATE-EXP` | 17,925,120 |

Site coordinates are now `(0.0, 0.0)`, explicitly synthetic rather than an
observing location. Serial-bearing telescope values became `S50_00000001`
or `S50_00000002`, preserving the standard/mosaic device distinction and
valid device-name syntax. The legacy `mosaic_6.fit` already used the generic
`Seestar S50` model name, which was retained.

Present ISO dates now use 2000-01-01, 00:00:00 for raw/Siril images and
01:00:00 for native stacks; present exposure-end dates are 11 seconds later.
This retains timestamp parsing and light-before-stack association without
retaining original dates or time-of-day. Siril creation date and Julian
`EXPSTART`/`EXPEND` were also replaced: 2451544.5 and
2451544.5 + 1760/86400. These are fixture values, not capture evidence.

## Complete metadata and pixel review

All HDUs, header values and card comments were inspected. Each file contains
one primary image HDU. No observer/user fields, personal paths, emails or
other personal text were found. FITS standard citation COMMENT cards and
Siril's stacking and `TOP-DOWN mirror` HISTORY are non-identifying and retained.
Generic `INSTRUME`, `CREATOR`, `PRODUCER` and software `PROGRAM` identify
product models/versions, not people or individual devices.

Astronomical `OBJECT`, RA/DEC and native-stack TAN-SIP WCS describe celestial
fields, not terrestrial GPS locations; these were retained. Exposure durations,
stack counts, gain, focus, temperature, pixel size, binning and other technical
settings were inspected and retained as non-identifying image characteristics.

Contrast-enhanced previews of all nine arrays showed star/nebula fields and
sensor noise, with no visible people, terrestrial landmarks or embedded
personal labels (preview filenames were added by the review script only).
Astronomical target identity remains inferable from real pixels. Sensor noise
can also permit correlation with another copy of an image; this review does
not claim anonymity against image matching. No pixel redaction is warranted
for these astronomical regression fixtures.

## Preservation and test dependencies

Only selected 80-byte header cards were replaced in place. Header lengths,
all other cards and the complete data region were byte-identical before and
after sanitisation. Header padding was blank and data padding zero; no extra
HDUs or trailing private payload were present. FITS verification passed.
Raw Bayer patterns, uint16 scaling, float32 precision, shapes, EQMODE,
software-version variation, RGB layout, linear values, WCS and Siril
ROWORDER/mirror history remain intact.

All dependent modules below are under `tests/integration/`:

- `siril_stacked.fit`: `test_batch_conversion.py`, `test_cli_conversion.py`, `test_fits_to_tiff_conversion.py`, `test_rgb_handling_contract.py`, `test_siril_rgb_conversion.py`, `test_stage6_workflows.py`
- `eq.fit`: No current automated test dependency; retained reference fixture.
- `light.fit`: `test_archive_discovery.py`, `test_archive_orchestration.py`, `test_archive_reconstruction.py`, `test_batch_conversion.py`, `test_cli_conversion.py`, `test_fits_to_tiff_conversion.py`, `test_raw_conversion.py`, `test_seestar_demosaic.py`, `test_stage6_workflows.py`
- `mosaic.fit`: No current automated test dependency; retained reference fixture.
- `mosaic_1.fit`: `test_fits_to_tiff_conversion.py`, `test_mosaic_session_demosaic.py`, `test_raw_conversion.py`
- `mosaic_4.fit`: `test_mosaic_session_demosaic.py`
- `mosaic_6.fit`: `test_mosaic_session_demosaic.py`
- `stacked.fit`: `test_archive_discovery.py`, `test_archive_orchestration.py`, `test_archive_reconstruction.py`, `test_batch_conversion.py`, `test_fits_to_tiff_conversion.py`, `test_rgb_handling_contract.py`, `test_seestar_rgb_conversion.py`, `test_stage6_workflows.py`
- `stacked_mosaic.fit`: `test_cli_conversion.py`, `test_fits_to_tiff_conversion.py`, `test_rgb_handling_contract.py`, `test_seestar_rgb_conversion.py`

The only test change in this sanitisation step is
`test_real_seestar_copy_cli_reopens_tiffs_and_verifies_index` in
`test_archive_orchestration.py`: the exact index assertion now expects
`S50_00000001` instead of the real serial. It still verifies telescope metadata
propagation. No tests, assertions or processing paths were removed or bypassed.

Pixel-region SHA-256 values (identical before and after):

| Fixture | Pixel SHA-256 |
| --- | --- |
| `siril_stacked.fit` | `cb51b67c1985f1b1a9693ca7f4b3b7e2c6f945a63cdc050f5ea8521ee279953f` |
| `eq.fit` | `6018596eda99a7592aa6a49546bb6f1eadeab2568e9a0d8932f787f54588525d` |
| `light.fit` | `549ff7320f7f88362597527cecf8e3f8178a6f4100a2d3e8ef1eaf8d7b31df1c` |
| `mosaic.fit` | `a7366dfdda9818f34690f5a7a7e369ae5f83032ab7187429aa195cf59892922c` |
| `mosaic_1.fit` | `d208a6ad509914be51ff2f977297efad9e3e8dbb89041f984d42d197fb67be05` |
| `mosaic_4.fit` | `97d7d07fcb43eac414e2ca7894d8dd55e910342e998251d07cc9d443d40c5d86` |
| `mosaic_6.fit` | `3d37af8237e8f94d5820555597eef115563a75551d364115db046901b5eb0ec5` |
| `stacked.fit` | `f732117994f4bacfcfb0953d150522cfc87a4d141dbba00a64b9a5fcb116d191` |
| `stacked_mosaic.fit` | `749a0fd5905ffb939c9424bd20467ae567487156c97061acd49e013d985377d5` |

## Validation and Git boundary

- Complete suite: 323 passed in 11.72 seconds (Python 3.13.15).
- `ruff check .`: passed.
- Applicable `ruff format --check`: 32 Python files passed, retaining the
  established archive/CLI scope plus the prior mosaic-remediation files.
- `git diff --check`: passed; changed Markdown reviewed for layout and links.
- All nine sanitised headers reopened and verified against replacement values.
- No production code changes; no coverage reduction.

The reviewed working-tree FITS files are suitable for future public publication
under the astronomical-image privacy assessment above. The index was not
updated: it still contains unsanitised real fixtures and the original
272,923,200-byte Siril mosaic. Therefore the current staged snapshot is NOT
cleared for a public commit. Stage the reviewed replacements in the subsequent
Git preparation step before creating clean history. No commit, push, history
rewrite or CI implementation was performed. This report does not clear other
repository documents, historical records or previously staged content.
