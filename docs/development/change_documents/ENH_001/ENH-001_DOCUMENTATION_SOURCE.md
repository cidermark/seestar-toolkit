# Development — ENH-001 (unreleased)

Standalone source material for human editorial review, prepared against
`9899524` on `enh/ENH-001-config-management`. This describes the implemented
ENH-001a/ENH-001b commands, not functionality in the published v1.1.0 release.
It is not an integrated User Guide, Quick Start or closure report.

Examples use deliberately illustrative coordinates and quoted placeholder paths.
Replace them with your own values before use. Examples are alternatives, not a
script to run in sequence. Commands marked **save** or **remove** change saved
configuration when validation and any required authorisation succeed.

## Purpose, file location and precedence

ENH-001 provides explicit inspection and management of archive preferences and
observing locations. The default TOML file is:

```text
~/.config/seestar-toolkit/config.toml
```

The path is under the current user's home directory; `XDG_CONFIG_HOME` does not
select another location. Use `--config PATH` to select an existing alternative
file for that invocation. It replaces the default-file selection rather than
merging two files.

Archive preference precedence remains **CLI override > saved configuration >
built-in default**. An archive invocation's overrides are temporary. Ordinary
`config show` displays values without invocation-specific overrides; it does not
predict a separate archive command's complete choices. Unknown TOML entries are
retained but are not effective managed preferences.

A typical document has `[archive]` preferences and repeated `[[locations]]`
entries with `name`, `latitude`, `longitude` and `radius_m`. There are no built-in
observing sites. **The 100 m radius default applies only when creating a new
location.** Existing entries must have a radius; an omitted field is not repaired
by silently assigning 100 m.

## Inspect configuration — no saving

```bash
seestar-toolkit config show
seestar-toolkit config show --saved
seestar-toolkit config show --defaults
seestar-toolkit config show --config "/path/to/existing/config.toml"
```

| Form | Display and behaviour |
|---|---|
| `config show` | Selected path/existence status, one effective value per archive preference with `[saved]` or `[default]`, and saved locations. A saved value keeps its saved label even when equal to the default. |
| `config show --saved` | Raw saved entries, including locations, unknown keys and comments; it does not invent absent defaults. Readable invalid entries are accompanied by diagnostics. |
| `config show --defaults` | Built-in preferences and notice that there are no built-in sites. Does not read the saved file, even if damaged or inaccessible. Cannot be combined with `--config`. |
| `config show --extract FILE` | FITS site coordinates and all containing saved locations, as described below. Does not save or update a location. |

Without the default file, ordinary inspection shows defaults/no saved locations
and creates nothing. Invalid known scalar values are normally marked
`[saved; INVALID]`, with diagnostics and a failing status rather than successful
fallback values. See the hierarchy-brace exception under discrepancies below.

## Archive preferences — save or remove

| Setting | Accepted value | Built-in default |
|---|---|---|
| `archive.hierarchy` | Each of `{target}`, `{location}`, `{session_end_date}` exactly once, as separate relative path components, in any order | `{target}/{location}/{session_end_date}` |
| `archive.source_action` | `copy`, `move` | `copy` |
| `archive.collision_policy` | `skip-identical`, `error`, `overwrite` | `skip-identical` |

**Save:** scalar replacement needs no confirmation question.

```bash
seestar-toolkit config set archive.source_action copy
seestar-toolkit config set archive.collision_policy skip-identical
seestar-toolkit config set archive.hierarchy '{location}/{target}/{session_end_date}'
```

**Remove:** unset deletes the saved preference so its built-in default applies.

```bash
seestar-toolkit config unset archive.source_action
```

A save reports previous/new state after writing succeeds. An absent-key unset is
a no-op. Setting an already equivalent saved value also avoids rewriting. Setting
a missing preference to its default explicitly saves it, so its label becomes
saved. Policy values are case-insensitive in saved configuration and `config set`,
but surrounding spaces are not accepted. Newly written policy values are
normalised to lowercase; an equivalent existing spelling need not be rewritten.

Only the three listed preferences are supported. Source/destination paths,
`--dry-run`, prompting flags, explicit archive location and the configuration-file
selector cannot be saved as scalar preferences. `move` and collision policies
retain their existing archive-execution meanings; setting them does not itself
run an archive operation.

## Create a location — save

Manual creation requires both coordinates. These numbers illustrate syntax only:

```bash
seestar-toolkit config set --location "Example Site" --latitude 10.0 --longitude 20.0
seestar-toolkit config set --location "Example Site" --latitude 10.0 --longitude 20.0 --radius-m 75.5
```

Alternatively, use the observing-site coordinates from one FITS file:

```bash
seestar-toolkit config set --location "Example Site" --extract "/path/to/capture.fit"
```

A new location receives `radius_m = 100.0` unless `--radius-m` is supplied.
Creation requires no separate confirmation. If the name instead identifies an
existing entry, existing-location update rules apply. These operations must pass
name, coordinate, overlap and complete-document validation before writing.

## Inspect FITS GPS and saved matches — no saving

```bash
seestar-toolkit config show --extract "/path/to/capture.fit"
seestar-toolkit config show --extract "/path/to/capture.fit" --config "/path/to/existing/config.toml"
```

Output identifies the selected configuration, FITS file and site coordinates.
Every containing saved location is listed with its name, latitude, longitude,
radius in metres and distance in metres. Output distinguishes no saved locations,
no matching locations, one match and multiple matches. Legacy conflicts produce
warnings. Invalid configuration prevents successful match reporting.

Matches use the archive's Haversine distance calculation and inclusive boundary
(`distance <= radius + 1e-9` metres). Results are ordered by distance, then
case-folded name, then original name. Ordinary archive selection still chooses
the nearest containing location using those tie-breaks; inspection lists them
all without changing archive selection.

Extraction reads headers across FITS HDUs without accessing image/table arrays;
the input does not need a TIFF-convertible image type. Only `SITELAT` and
`SITELONG` supply site coordinates. Numeric degree values, including numeric
strings, are interpreted; target `RA`/`DEC` are never substitutes.

Headers with neither site card are ignored. Every header with either card must
have a complete, finite, in-range pair. Identical repeated numeric values are
accepted. Conflicting duplicate cards, disagreement between HDUs, incomplete
pairs and invalid evidence fail; values are not averaged or combined across
headers. Missing/unreadable/malformed evidence also fails. There is no dataset
scan, sexagesimal conversion, geocoding or alternative-keyword guessing.

## Update, rename and remove locations

**Save:** existing locations retain unspecified coordinates, radius and unknown
fields. Latitude-only, longitude-only or radius-only changes are supported:

```bash
seestar-toolkit config set --location "Example Site" --latitude 10.001
seestar-toolkit config set --location "Example Site" --longitude 20.001
seestar-toolkit config set --location "Example Site" --radius-m 80
```

FITS extraction replaces both coordinates, retaining the existing radius unless
explicitly changed. `--extract` cannot be combined with either manual coordinate.

Before a changed existing entry is saved, the CLI displays `Old:` and `Proposed:`
values and asks:

```text
Update config / Skip [Skip]:
```

Enter `Update config` (also `update` or `u`) to save, or `Skip`/`s` to cancel.
Answers are case-insensitive. Blank input defaults to Skip; end-of-input also
skips. Skip succeeds without changing configuration bytes or modification time.

Without a terminal on standard input, replacement requires explicit `--update`:

```bash
seestar-toolkit config set --location "Example Site" --extract "/path/to/capture.fit" --update
```

`--update` is location-only, requires an existing named entry and never bypasses
validation. A valid no-op does not prompt or rewrite, including unattended use.
Validation still occurs first: resubmitting an unchanged legacy entry can fail
if it does not satisfy the strict edit rules.

Rename alone or combine rename with coordinate/radius changes:

```bash
seestar-toolkit config set --location "Example Site" --rename "Example Observatory"
seestar-toolkit config set --location "Example Site" --rename "Example Observatory" --latitude 10.002 --radius-m 60 --update
```

Rename requires an existing entry. Combined changes validate together and use
one question and one save. A different existing entry occupying the proposed
name is a conflict, not a replacement target. **Rename changes saved
configuration only; it does not rename archive directories or regenerate indexes.**

**Remove:** delete a uniquely identified complete location without another
confirmation:

```bash
seestar-toolkit config unset --location "Example Site"
```

An absent name is a successful no-op, provided the proposed configuration is
otherwise valid. Ambiguous legacy names cannot be removed through this command.

## Names, coordinates and circles

Lookup trims outer spaces and uses Unicode case-folding. New and explicitly
renamed names are trimmed while internal spacing/capitalisation are retained.
An ordinary coordinate/radius edit preserves an untouched legacy name's spelling.
Blank names and standalone `.`/`..` names are rejected for creation/edits.

Directory names use existing archive cleaning, including whitespace normalisation
and unsafe-character replacement. Different logical names must not collide after
that cleaning, compared without regard to case: for example, `A/B` and `a-b`
conflict. A case-only rename of the same unique entry is allowed. Multiple legacy
entries sharing the requested trimmed/case-folded identity require manual
file disambiguation; the CLI never silently chooses one.

Coordinates must be finite numbers: latitude in `[-90, 90]`, longitude in
`[-180, 180]`. Booleans are not coordinates or radii. New/edited radii must be
strictly positive; decimal metres are supported.

A new or edited circle must not touch or overlap another saved circle. The edited
entry is excluded from comparison with itself. Rejection occurs when centre
distance is at most the sum of the two radii plus `1e-9` metres. Diagnostics name
both sites and show distance/radii. Rename-only edits must also satisfy these
rules. There is no overlap override question or force flag.

## Legacy compatibility, invalid files and repair

Legacy zero-radius, duplicate-name and overlapping locations remain loadable for
archive use if they meet existing required-field/type/range rules. Configuration
inspection warns about these conflicts without failing solely for them. Archive
nearest-match selection, tie-breaking and inclusive boundaries remain unchanged.
The shared distance calculation clamps its intermediate for antipodal rounding.

Unrelated legacy conflicts do not prevent scalar changes, a valid separate
location edit or removal. The location being edited must satisfy the new rules;
for example, renaming a zero-radius entry also requires correcting its radius.

Readable invalid TOML values can normally be inspected with diagnostics and
repaired by setting/unsetting the affected preference, editing the affected
location, or removing a uniquely identified invalid location. The entire proposed
document must then pass existing schema and hierarchy validation. Another
unrelated existing-schema failure blocks saving; these commands are not a batch
repair language. Broken TOML syntax and ambiguous names require manual repair.
See the unmatched-brace limitation below before promising universal repair.

| Configuration condition | Behaviour |
|---|---|
| Missing default file | Inspect/defaults work without creating anything. A successful set can create the default directory/file. Unset/no-op creates nothing. |
| Missing explicit `--config` path | Error, including on set; no file is created at a possibly mistyped path. |
| Malformed or unreadable TOML | Error; no silent default fallback. `show --defaults` remains independent of the file. |
| Readable invalid known values | Normally inspectable with diagnostics and status 1; edits require a fully valid proposed document. |
| Broken symlink, link loop or non-file path | Error rather than a missing-default fallback. |
| Unknown keys/sections | Preserved, ignored by runtime configuration resolution. |

A valid explicit archive hierarchy can still override an invalid saved hierarchy
string. This does not generalise to invalid saved types/policies, which still
fail loading even when an archive override is supplied.

## File selection, preservation and writes

Place `--config` after the `show`, `set` or `unset` verb, for example:

```bash
seestar-toolkit config set archive.source_action copy --config "/path/to/existing/config.toml"
seestar-toolkit config unset --location "Example Site" --config "/path/to/existing/config.toml"
```

Configuration commands show the selected path and, when different, its resolved
destination. Symlink writes replace the target file and preserve the link.
Existing target permission bits are retained; new default configuration files
use owner-only access (0600).

Edits preserve unrelated values, unknown entries, comments and unaffected
locations. Edited whitespace need not remain byte-identical. Removing a location
deletes its fields and their inline comments; standalone notes are retained but
may move. No-ops and Skip do not rewrite or change modification time.

Validated changes are written to a sibling temporary file and atomically replace
the resolved destination. The writer checks content, file metadata and link target
for changes since reading, including after a prompt. A detected concurrent change
stops the save and requests retry. Temporary files are cleaned on failure and
success is reported only after replacement. This is lightweight accidental-edit
protection, not locking or a guarantee against every race; it does not introduce
ownership/ACL management.

## Compact syntax and options reference

`PREF` is one of the three archive setting names above. Brackets indicate optional
syntax and are not typed. `PATH` must name an existing configuration file.

```text
config show [--config PATH]
config show --saved [--config PATH]
config show --defaults
config show --extract FILE [--config PATH]
config set PREF VALUE [--config PATH]
config unset PREF [--config PATH]
config set --location NAME [CHANGE FIELDS] [--update] [--config PATH]
config unset --location NAME [--config PATH]
```

Prefix each form with `seestar-toolkit`. Location CHANGE FIELDS are
`--latitude NUMBER`, `--longitude NUMBER`, `--extract FILE`, `--radius-m NUMBER`
and `--rename NEW_NAME`; at least one is required.

| Combination | Supported or rejected |
|---|---|
| New location + both manual coordinates, or FITS extraction | Supported; optional radius, no creation confirmation. |
| Existing location + one/both manual coordinates or radius only | Supported; unspecified fields retained. |
| Rename + radius + either manual coordinates or extraction | Supported for an existing entry, with one validation/save. |
| `--update` + existing location change | Supported, including extraction/rename; suppresses the question. |
| Extraction + either manual coordinate | Rejected argument combination. |
| Two of `show --saved`, `--defaults`, `--extract` | Rejected argument combination. |
| `show --defaults --config PATH` | Rejected argument combination. |
| Scalar and location forms mixed; location flags on scalar commands | Rejected argument combination. |
| `set --location NAME` without a change; scalar set without a value | Rejected argument combination. |
| `--update`/coordinate/rename flags on unset; mutation flags on show | Rejected arguments. |
| New location with partial coordinates; missing rename/update target | Operational validation error; nothing saved. |

## Exit behaviour and common errors

Normal output goes to standard output; warnings/errors go to standard error.

| Status | Meaning |
|---|---|
| 0 | Successful inspection/save/removal, explicit Skip, or valid no-op. Legacy warnings alone do not make inspection fail. |
| 1 | Handled configuration, extraction, validation, write or unattended-authorisation error; readable invalid inspection also fails. |
| 2 | Argument parsing/usage error, including unsupported preferences or mixed forms. |

These are the handled CLI categories; the source-level exception below must not
be presented as an ordinary diagnostic guarantee.

Common remedies: check an explicit path exists; use both coordinates for creation;
supply the missing existing radius explicitly; inspect raw saved entries before
repairing; disambiguate duplicate legacy names manually; choose a distinct name
or non-overlapping valid circle; supply `--update` only for an intended existing
replacement; use a FITS file with consistent site cards; retry after reviewing an
external configuration edit. There is no force option to bypass validation.

## Important unchanged behaviour and limits

Only explicit configuration commands persist settings. Archive-location prompt
answers remain temporary. Saving/renaming a location does not reorganise archived
files. Help/version and conversion remain independent of saved configuration.
Strict configuration GPS extraction does not change archive FITS inspection or
multi-file GPS reconciliation. The observing-night rule remains
`date(capture_datetime + 12 hours)`; ENH-002 is not implemented here.

There is no `config location` subcommand, top-level `config --extract` shorthand,
`--save-config`, reset-all, GUI or configuration-profile system. Output is
human-readable; no JSON interface is advertised. No release/version change is
implied by this material.

## Suggested topics to integrate into the User Guide

- Configuration location, precedence, explicit-file selection and the three
  inspect-only views.
- Preference/default table and scalar save/unset examples.
- Location creation, partial edits, FITS inspection versus FITS-derived saving,
  prompts/unattended updates, rename and removal.
- Name/circle rules, legacy compatibility, invalid-file repair and exit codes.
- Preservation/write guarantees and limits; unchanged archive semantics.
- Incorporate confirmed discrepancy outcomes before making universal error or
  repair claims. Keep unreleased status clear until release metadata is agreed.

## Smaller selection suitable for the Quick Start

- Locate the default file and run `config show` / `config show --defaults`.
- Save one common preference, such as `archive.source_action copy`.
- Inspect a capture with `config show --extract "/path/to/capture.fit"`.
- Create a named location from that file; explain the new-location-only 100 m
  default and optional radius.
- Briefly explain Update config / Skip and unattended `--update`, with a link to
  detailed validation/repair guidance. Mention that rename does not move archives.

## Implementation/specification discrepancies and editorial questions

**Source-level gap: unmatched hierarchy braces.** Specification sections 4, 5,
8 and 10 require actionable invalid-value diagnostics and targeted repair.
`planning._template_tokens()` calls `string.Formatter().parse()` directly.
An unmatched brace (for example the string `{target`) raises `ValueError`, while
configuration validation wrappers catch `ArchivePlanningConfigurationError`
and/or `ArchiveConfigError`, and `_run_config()` catches `ArchiveConfigError` and
`FitsError`. This path can therefore escape as an uncaught exception instead of
normal invalid inspection/status handling. Scalar repair first inspects existing
values, so even replacing that saved hierarchy may encounter the exception.
This finding is from source inspection, not a newly executed reproduction; no
production change was made. Confirm and resolve separately before promising that
all readable invalid hierarchy strings can be inspected/repaired normally.

**Resolution — 2026-10-01.** The finding was reproduced and fixed by `2425ccf`.
Malformed opening and closing braces now enter the established handled
configuration-validation path, while valid explicit archive hierarchy overrides
retain precedence. See the
[hierarchy validation fix report](ENH-001_HIERARCHY_FIX_REPORT.md). The original
finding above is retained as the source-review context that led to the fix.

**No-op clarification, not a demonstrated contradiction:** valid unchanged
location edits return before the prompt, but strict validation precedes no-op
recognition. Unchanged invalid legacy entries can still fail. This material
states the implemented ordering rather than promising unconditional no-op success.

**Minor help wording:** the general unset help says a saved preference is removed
so its default applies. The `--location` help correctly describes removal of an
entry; locations have no built-in default entry. Use the distinction in editorial
text. No help/code changes are part of this step.

Guide integration, release/document version wording, PDF/checksum regeneration
and final closure validation remain pending. Neither ENH-001c nor ENH-001 is
marked complete by this source material.

## Repository sources and existing test evidence

Paths below are relative to the repository root. Tests were read as existing
behavioural evidence, not executed for this documentation task. No application
command, personal configuration access, build, installation or PDF operation was
needed. AGENTS.md requires full pytest/Ruff for completed coding tasks; this step
creates documentation source only and does not invoke that coding-task gate.

| Material claim | Implementation and supporting tests |
|---|---|
| Syntax, combinations, prompts, exit categories | [cli.py](../../../../src/seestar_toolkit/cli.py): `build_parser`, `_validate_config_arguments`, `_run_config`, `_run_location_config`; [test_config_commands.py](../../../../tests/unit/archive/test_config_commands.py), [test_location_commands.py](../../../../tests/unit/archive/test_location_commands.py), especially mixed-argument, unattended, Skip and concurrent-edit tests. |
| Default path, schema, policies, hierarchy override | [config.py](../../../../src/seestar_toolkit/archive/config.py): default/load/resolve functions; `cli._run_archive`; [test_config.py](../../../../tests/unit/archive/test_config.py), hierarchy-override and invalid-policy tests in `test_config_commands.py`. |
| Provenance, repair, no-ops and safe persistence | [config_document.py](../../../../src/seestar_toolkit/archive/config_document.py): read/inspect/prepare/persist functions; [test_config_document.py](../../../../tests/unit/archive/test_config_document.py): policy no-op, repair, comments, permissions, symlinks, changed-file and cleanup cases. |
| Location identity, partial edits, overlap, removal and all matches | [config_locations.py](../../../../src/seestar_toolkit/archive/config_locations.py): prepare/edit/removal/matching functions; [test_config_locations.py](../../../../tests/unit/archive/test_config_locations.py): Unicode ambiguity, partial/combined edits, strict legacy repairs, touching circles and preservation; extraction/multiple-match tests in `test_location_commands.py`. |
| Header-only GPS and duplicate/HDU rules | [site_coordinates.py](../../../../src/seestar_toolkit/fits/site_coordinates.py); [test_site_coordinates.py](../../../../tests/unit/fits/test_site_coordinates.py): forbidden data access, numeric repeats, conflicts, incomplete/malformed evidence, extension/table evidence and RA/DEC-only rejection. |
| Cleaning, distance and legacy matching | [planning.py](../../../../src/seestar_toolkit/archive/planning.py): `normalize_archive_component`, `_resolve_location`, `_haversine_m`; [test_planning.py](../../../../tests/unit/archive/test_planning.py) nearest/inclusive-radius tests; tie/antimeridian/antipodal tests in `test_config_locations.py`. |
| Unmatched hierarchy-brace finding | `planning._template_tokens`, `config_document._scalar_value` / `inspect_config_document`, `config_locations._validated_document`, `cli._run_config`; reviewed hierarchy tests cover other invalid forms, not this newly identified path. |

The [authoritative specification](ENH-001_SPECIFICATION.md), applicable AGENTS.md
and relevant architecture/project notes informed scope. The implementation is the
authority for the actual command behaviour described here.
