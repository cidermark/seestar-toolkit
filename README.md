# Seestar Toolkit

**Version 1.1.0 - Unreleased**

Seestar Toolkit was developed to make a growing collection of Seestar captures
easier to preserve, understand and use. It reconstructs related captures into
observations and organises them into a predictable archive by target, observing
location and observing night.

The archive workflow keeps you in control: back up the source, preview the plan
with `--dry-run`, inspect every proposed path, then copy before considering a
move. A typical result is:

```text
Target/
|-- INDEX.md
`-- Location/
    `-- 20260915/
        `-- observation_01/
            |-- lights/
            `-- seestar_stacked/
```

Individual light FITS files remain in `lights/` without automatic TIFF
conversion. When a Seestar-created stacked FITS is present, its required TIFF
companion is generated beside it in `seestar_stacked/`.

The Toolkit can also convert supported FIT/FITS images into linear RGB TIFFs,
one file at a time or as a non-recursive batch. Conversion complements archive
organisation; it is not required to use the archive.

## Supported environment and captures

For v1.1.0, **supported** means tested and validated for this release:

- Seestar S50 captures within the validated FIT/FITS input scope, including
  supported raw Bayer lights, native RGB stacked images and mosaics;
- Apple-silicon Macs using a macOS version within the release's tested and
  Apple-supported platform envelope; and
- Python 3.11, 3.12, 3.13 or 3.14.

Other Seestar models may work, but they have not received enough validation for
v1.1.0 to call them officially supported. Unsupported does not mean known not to
work. Intel Macs, Windows and Linux are outside the validated v1.1.0 platform
scope. Solar, Lunar and Planetary video processing and DSLR capture processing
are also outside this release.

## Install and start

Release packages will be available from
[GitHub Releases](https://github.com/cidermark/seestar-toolkit/releases) when
v1.1.0 is published. The wheel is the recommended installation format; the
Toolkit is not distributed through PyPI for v1.1.0.

Follow the [Quick Start](docs/user/SEESTAR_TOOLKIT_QUICK_START.md) for the
supported Python, virtual environment, installation and first archive steps.
The [User Guide](docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md) is the authoritative
reference for supported inputs, archive behaviour, conversion, configuration,
storage, privacy, troubleshooting and uninstalling.

A safe first archive begins with an explicit preview:

```bash
seestar-toolkit archive --dry-run --source-action copy \
  --collision-policy skip-identical --location "Home" \
  --non-interactive "/path/to/My Works" "/absolute/path/to/archive"
```

After inspecting the plan, repeat the command without `--dry-run` to copy.

## Safety and privacy

Keep an independent backup and verify the archive before removing source files.
Archive and batch operations can partially succeed and do not provide
whole-workflow rollback.

FITS files, configuration, archive indexes and diagnostics can contain observing
coordinates, timestamps, device identifiers and other private metadata. Review
them before sharing. The audited v1.1.0 Toolkit runtime has no telemetry,
analytics, update checking or online geocoder; mounted network storage still
uses the network as normal filesystem storage.

## Contributing and release history

Bug reports, enhancement suggestions and carefully reviewed representative data
from other Seestar models can help. See [Contributing](CONTRIBUTING.md) and the
[public changelog](CHANGELOG.md).

Seestar Toolkit is licensed under the [MIT License](LICENSE).
