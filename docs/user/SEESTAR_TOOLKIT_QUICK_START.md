# Seestar Toolkit Quick Start

**Version 1.1.0 --- 2026-09-23**

This Quick Start gets you from installation to a **safe first archive** and,
optionally, a FITS-to-TIFF conversion.

It assumes you are comfortable using Terminal and Homebrew. For explanations,
advanced archive options, troubleshooting and the full v1.1.0 support
boundaries, see the [Seestar Toolkit User Guide](SEESTAR_TOOLKIT_USER_GUIDE.md).

> **For your first archive:**
>> keep a backup</br>
>> use `--dry-run`</br>
>> inspect the plan</br>
>> copy first</br>
>> verify the result</br>
>> only consider `move` later</br>

## 1. Check the requirements

Seestar Toolkit v1.1.0 is officially supported on:

- **Seestar S50** captures validated for this release;
- an **Apple-silicon Mac** using a supported macOS version;
- **Python 3.11, 3.12, 3.13 or 3.14**.

Other telescope models, operating systems, computer architectures and Python
versions may work, but are not supported unless specifically listed for this
release.

Solar, Lunar and Planetary video processing and DSLR capture processing are
outside the scope of v1.1.0.

Check Homebrew:

``` bash
/opt/homebrew/bin/brew --version
```

See which Homebrew Python versions are installed:

``` bash
/opt/homebrew/bin/brew list --formula | grep '^python'
```

For example, check Python 3.13:

``` bash
/opt/homebrew/bin/python3.13 --version
```

If you need to install it:

``` bash
/opt/homebrew/bin/brew install python@3.13
```

Do not modify Apple's system Python.

## 2. Create the Toolkit environment

Create the recommended virtual environment:

``` bash
/opt/homebrew/bin/python3.13 -m venv ~/.venvs/seestar-toolkit
```

Activate it:

``` bash
source ~/.venvs/seestar-toolkit/bin/activate
```

Check Python:

``` bash
python --version
```

You create this environment once. In later Terminal sessions, simply activate
it again; you do **not** need to reinstall the Toolkit each time.

## 3. Install Seestar Toolkit

Download the v1.1.0 release package from the project's GitHub Releases page.

The recommended installation file is:

``` text
seestar_toolkit-1.1.0-py3-none-any.whl
```

Seestar Toolkit v1.1.0 is **not distributed through PyPI**.

With the virtual environment active, install the wheel, replacing the example
path with the real downloaded file:

``` bash
python -m pip install \
  "/path/to/downloads/seestar_toolkit-1.1.0-py3-none-any.whl"
```

Check the installation:

``` bash
python -m pip check
seestar-toolkit --version
```

The version command should report:

``` text
seestar-toolkit 1.1.0
```

You can also check the equivalent Python entry point:

``` bash
python -m seestar_toolkit --version
```

Normal use in this guide uses the `seestar-toolkit` command.

## 4. Choose a safe first archive

Start with a **small Seestar observing session that is already backed up**.

You need:

- a **source root** containing the Seestar captures;
- a separate **archive root** where the organised archive will be created.

Archive discovery is shallow: the Toolkit examines the selected source root and
its immediate child directories. It does not recursively search an arbitrary
folder tree.

A typical Seestar work folder can look like:

``` text
My Works/                         <- select this as SOURCE_ROOT
  IC 434/
    Stacked_195_IC 434_10.0s_LP_20260103-225603.fit
  IC 434_sub/
    Light_IC 434_10.0s_LP_20260103-220259_thn.jpg
    Light_IC 434_10.0s_LP_20260103-220259.fit
    Light_IC 434_10.0s_LP_20260103-220259.jpg
```

Select `My Works` itself. JPEGs and thumbnails alongside the FITS captures are
normal; the archive workflow leaves them untouched.

Keep the archive root outside the source tree.

## 5. Preview before writing anything

For the first run, explicitly use **copy** and **dry-run**.

Replace `Home` and both example paths:

``` bash
seestar-toolkit archive --dry-run --source-action copy \
  --collision-policy skip-identical --location "Home" \
  --non-interactive "/path/to/My Works" "/path/to/archive"
```

`--dry-run` previews the proposed archive without writing archive outputs.

Before continuing, check that the preview has the expected:

- captures;
- target;
- location;
- observing night;
- observation grouping;
- archive destination;
- `copy` source action.

If anything looks wrong, stop and investigate while you are still in dry-run.

## 6. Create the archive by copying

When the preview looks correct, run the same command with only `--dry-run`
removed:

``` bash
seestar-toolkit archive --source-action copy \
  --collision-policy skip-identical --location "Home" \
  --non-interactive "/path/to/My Works" "/path/to/archive"
```

The default archive hierarchy keeps a stack TIFF companion beside its stack FITS:

``` text
Target/
└── Location/
    └── Observing night/
        └── observation_01/
            ├── lights/
            └── seestar_stacked/
```

The Toolkit may create additional observation directories when the captures
represent separate observations. A human-readable target index is also
maintained.

Because this example uses `copy`, the source FITS files remain in their original
location.

## 7. Verify the archive

Before doing anything to your source collection, inspect both the source and the
new archive.

Confirm that:

1.  the original source captures are still present;
2.  the expected target, location and observing-night directories exist;
3.  the expected observation directories and files are present;
4.  the stack TIFF companion and target index are where expected;
5.  the command did not report unresolved observations, collisions or failures.

Do **not** delete your originals simply because the command completed.

The full User Guide explains observing-night dates, observation reconstruction,
custom hierarchy order, collisions, re-running an archive and the additional
risks of `--source-action move`.

## 8. Let the Toolkit resolve a saved location

Using `--location "Home"` is simple for a first run, but you do not have to
supply a location every time.

The default configuration file is:

``` text
~/.config/seestar-toolkit/config.toml
```

For example:

``` toml
[[locations]]
name = "Home"
latitude = 51.0000
longitude = -1.0000
radius_m = 100.0
```

The coordinates above are illustrative only.

When supported captures contain usable coordinates, the Toolkit can compare
them locally with saved locations. It does not use an online geocoder.

Use a dry run to confirm the resolved location. For example:

``` text
M 42/Home/20260915/...
```

is resolved, while:

``` text
M 42/unknown/20260915/...
```

means the location was not resolved to a saved or supplied label.

An explicit `--location "Home"` takes precedence over automatic matching.

Configuration is **read-only in v1.1.0**. The Toolkit does not add or update
saved locations itself.

## 9. Convert a FITS image to TIFF

Conversion is optional. You do not need to convert FITS files before using the
archive.

Convert one supported FITS image:

``` bash
seestar-toolkit convert \
  "/path/to/input.fit" \
  "/path/to/output.tiff"
```

Batch-convert the supported FITS files directly inside one directory:

``` bash
seestar-toolkit convert-batch \
  "/path/to/fits" \
  "/path/to/tiff"
```

Batch conversion is non-recursive.

The Toolkit creates **linear RGB TIFF** data. It does not automatically stretch
the image or alter brightness, contrast or colour, so an astronomical TIFF can
initially look very dark.

Standalone `convert` and `convert-batch` outputs are not automatically added to
an existing Toolkit archive. If you want a standalone TIFF inside an archived
observation, choose or create the appropriate `tiff/` directory yourself.

Keep the original FITS file.

## 10. Useful commands

Show the main help:

``` bash
seestar-toolkit --help
```

Show command-specific help:

``` bash
seestar-toolkit archive --help
seestar-toolkit convert --help
seestar-toolkit convert-batch --help
```

Check the installed version:

``` bash
seestar-toolkit --version
```

The principal exit codes are:

``` text
0    success
1    operational or processing failure
2    command-line usage error
```

A batch or archive failure does not mean that every earlier successful action
has automatically been rolled back. Inspect the source and destination before
retrying.

## 11. When you have finished

Leave the virtual environment:

``` bash
deactivate
```

Your Toolkit installation remains in:

``` text
~/.venvs/seestar-toolkit/
```

Activate it again next time:

``` bash
source ~/.venvs/seestar-toolkit/bin/activate
```

## Next: the full User Guide

This Quick Start deliberately leaves out many details.

Read the [Seestar Toolkit User Guide](SEESTAR_TOOLKIT_USER_GUIDE.md) before using `move`, changing collision
policies, customising the archive hierarchy, troubleshooting partial operations,
or working through storage, permissions and privacy questions.

In particular, remember:

**Back up → Dry-run → Inspect → Copy → Verify**

Your original FITS captures remain valuable source data. Keep an independent
backup and verify your archive before deciding whether to remove source files.

Before sharing FITS files, configuration, archive indexes or diagnostics, review
them for private location, device and capture metadata.
