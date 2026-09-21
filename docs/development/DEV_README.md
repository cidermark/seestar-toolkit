# Seestar Toolkit

Seestar Toolkit is a Python command-line utility for converting supported
FIT/FITS images into linear RGB TIFF files for later processing.

## Version

Current development version: **1.1.0**

## Supported input

- Raw Bayer FIT/FITS images using `BAYERPAT`, including `GRBG`
- Native Seestar RGB FIT/FITS images
- Supported Siril RGB FIT/FITS images

## Output

- Linear 16-bit unsigned-integer RGB TIFF for Seestar `uint16` input
- Linear 32-bit floating-point RGB TIFF for supported Siril `float32` input

## Development installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Commands

```bash
seestar-toolkit --version
seestar-toolkit --help
seestar-toolkit convert input.fit output.tiff
seestar-toolkit convert-batch input-directory output-directory
seestar-toolkit archive --dry-run --source-action copy --collision-policy skip-identical --non-interactive source-root /absolute/archive-root
seestar-toolkit archive --source-action copy --collision-policy skip-identical --location "Example Site" source-root /absolute/archive-root
python -m seestar_toolkit --version
python -m seestar_toolkit convert input.fit output.tiff
python -m seestar_toolkit convert-batch input-directory output-directory
python -m seestar_toolkit archive --dry-run --source-action copy --collision-policy skip-identical source-root /absolute/archive-root
```

Single-file conversion uses one explicit output path. Batch conversion scans
one input directory non-recursively for `.fit` and `.fits` files
case-insensitively, processes them in filename order, and writes
`source-stem.tiff` into one explicit flat output directory. The batch output
directory is created if absent, but its parent must exist. Existing
destinations are never overwritten.

Batch conversion continues after expected per-file failures and prints a final
discovered/converted/failed summary. Its exit status is `0` only when every
discovered file converts, `1` for partial failure or no matching files, and `2`
for command-usage errors.

This batch command performs conversion only and remains flat and
non-recursive. The separate `archive SOURCE_ROOT ARCHIVE_ROOT` command uses
shallow Seestar-aware discovery: files in the selected source root and its
immediate child directories only. It supports `--dry-run`, `--location`,
`--hierarchy`, `--source-action {copy,move}`, `--collision-policy
{skip-identical,error,overwrite}`, `--non-interactive`, and `--config PATH`.
COPY and non-destructive identical-file skipping are the defaults.

Archive settings are read from `~/.config/seestar-toolkit/config.toml` when it
exists; an explicit `--config` path takes its place. CLI values override TOML,
which overrides built-in defaults. The loader is read-only and ignores unknown
keys for forward compatibility:

```toml
[archive]
hierarchy = "{target}/{location}/{session_end_date}"
source_action = "copy"
collision_policy = "skip-identical"

[[locations]]
name = "Example Site"
latitude = 0.0
longitude = 0.0
radius_m = 100
```

Dry-run performs the same discovery, observation reconstruction, location
resolution and destination planning as execution, then stops before any
filesystem mutation. Archive exit status is `0` for complete success and `1`
for expected operational, partial or failed outcomes; argparse usage errors
remain `2`.

Real archive runs also create or update a derived `INDEX.md` in each concrete
target directory. Its placement follows the configured hierarchy, and it lists
the archived observations and retained capture metadata. Indexes are
regenerable convenience views, not authoritative archive metadata. Dry-run
reports their planned paths but does not create index or temporary files.

## Tests

```bash
pytest
ruff check .
```
