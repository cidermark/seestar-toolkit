# Changelog

## [1.1.0] - Unreleased

### Added

- Reconstruction of supported Seestar captures into target, location,
  observing-night and observation archive structures, with dry-run, copy/move,
  collision handling and target indexes.
- Single-file and non-recursive batch conversion of supported FIT/FITS images to
  linear RGB TIFF.
- Read-only archive configuration and local saved-location matching.

### Supported

- Validated Seestar S50 raw Bayer, native RGB stacked and mosaic FIT/FITS inputs,
  plus tested Siril RGB conversion inputs.
- Apple-silicon Macs within the validated macOS release envelope, using Python
  3.11, 3.12, 3.13 or 3.14.

### Known limitations

- Other Seestar models may work but are not officially supported without
  sufficient v1.1.0 validation.
- Solar, Lunar and Planetary video processing, DSLR capture processing, Intel
  Macs, Windows and Linux are outside the validated v1.1.0 scope.
- Archive and batch operations can partially succeed; keep backups, preview
  archive plans and verify results.

See the [Quick Start](docs/user/SEESTAR_TOOLKIT_QUICK_START.md) and
[User Guide](docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md) for installation, safety,
privacy and complete support boundaries.
