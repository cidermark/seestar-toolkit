# Stage 9.2b — Checkpoint A progress report

## A. Status

**PAUSED — Stage 9.2b remains STARTED**

Audit date: 2026-09-13. Branch `main`, starting commit `398b771`:
`Stage 9.2a: validate clean installs and Python compatibility`.
Stage review confirms Stage 9.2a is formally COMPLETE, Python 3.11–3.14
supported, repository PRIVATE and v1.1.0 unreleased. These opening facts are
user-supplied; no remote visibility query or new CI run was performed.
The entire Stage 9.2b specification was read before the audit.

## B. Checkpoint reached

**A — Audit/design only.** No fresh representative installation, conversion,
archive execution, external/removable/NAS inspection or storage test occurred.
Checkpoints B, C and D and formal closure remain outstanding. The 186 closure
criteria are not claimed satisfied by this checkpoint report.

## C. Work completed

### Installed CLI inventory

[Structured evidence](STAGE_9.2b_CHECKPOINT_A.json) preserves exact help/version
output, exit codes and source comparison. A pre-existing noneditable local-directory
installation in `/tmp/seestar-stage91d-313` was used solely for read-only help.
Its provenance is a local-directory installation, **not** a newly installed release
wheel. Python is 3.13.15, macOS 26.5.2, arm64. The imported package is under
`/private/tmp/seestar-stage91d-313/lib/python3.13/site-packages/seestar_toolkit`.
All 33 installed Python source files match the checkout byte-for-byte.
Both entry points ran from `/tmp`; module invocation used `python -I -m
seestar_toolkit`. No repository PYTHONPATH or editable installation was used.
No private source-install URL is reproduced in evidence.

Ten commands passed: for each entry point, `--version`, `--help`,
`convert --help`, `convert-batch --help`, and `archive --help` returned 0,
with empty stderr. Both versions reported `seestar-toolkit 1.1.0`.
This establishes the audited surface, not Checkpoint B's fresh-artifact proof.

```text
seestar-toolkit [-h] [--version] [--verbose] {convert,convert-batch,archive} ...
seestar-toolkit convert [-h] INPUT_FITS OUTPUT_TIFF
seestar-toolkit convert-batch [-h] INPUT_DIR OUTPUT_DIR
seestar-toolkit archive [-h] [--dry-run] [--location LOCATION]
    [--hierarchy HIERARCHY] [--source-action {copy,move}]
    [--collision-policy {skip-identical,error,overwrite}]
    [--non-interactive] [--config PATH] SOURCE_ROOT ARCHIVE_ROOT
```

`python -m seestar_toolkit` exposes the same parser. Every command also accepts
`-h`/`--help`; the version and verbose options belong before the subcommand.
There are no public inspect, config-write, location-save, recursive-batch,
JPEG-policy, archive-plan subcommand or archive-apply subcommand interfaces.
Internal discovery, reconstruction, planning, execution and indexing APIs are
not additional public commands.

### Implemented functional contracts: code and existing-test audit

The following are audited expectations for B, not newly executed workflow results.

| Area | Actual contract |
| --- | --- |
| Single conversion | Explicit input/output paths; raw Bayer, native RGB and Siril RGB supported. Linear uint16 or float32 RGB retained as appropriate. Exclusive output creation rejects existing files; parent directories are not created. Expected FITS/TIFF/value errors return 1. |
| Batch | Sorted, nonrecursive file scan; case-insensitive `.fit`/`.fits`; other extensions ignored. Outputs are `<stem>.tiff`. Creates the output directory only when its parent exists. Per-file expected failures continue with summary and exit 1; empty input also returns 1. No overwrite switch. |
| Archive discovery | Root files and immediate child-directory files only; `_sub` directory and stack filename/product-directory evidence distinguish lights and stacks. Deeper content is not traversed. |
| Archive execution | `--dry-run` plans without writing. Omitting it executes. Copy and skip-identical are defaults unless config overrides them; move/overwrite require explicit CLI or config selection. CLI roots are explicit; planner requires an absolute safe archive root. |
| Hierarchy | Default `{target}/{location}/{session_end_date}`. Each supported token occurs exactly once; permutations supported. `{date}`, absolute templates, traversal and arbitrary literal components are rejected. |
| Date and numbering | `date(capture_datetime + 12 hours)` formatted `YYYYMMDD`, using first light or stack fallback. Numbered `observation_01` directories, chronological grouping and incremental reconciliation; source timestamps unchanged. |
| Products | Original lights in `lights`, their TIFFs in `tiff`, native stacked FITS and TIFFs in `seestar_stacked`. Target `INDEX.md` follows target-token placement. Full and thumbnail JPEGs are discovered but left untouched; there is no JPEG policy control. |
| Safety/partial results | Verified original transfer precedes TIFF generation. Existing TIFFs are preserved and reported as collisions. A TIFF failure after a successful move retains the archived original; this is not whole-workflow rollback. Independent work can continue; partial/failed results return 1. |
| CLI exits | Help/version and no-command help return 0; argparse usage failures return 2; expected operational failures return 1. Complete archive (including empty source) returns 0. Runtime/error evidence is deferred to B. |

Audited implementation: `src/seestar_toolkit/cli.py`, `__main__.py`, `batch.py`,
FITS conversion/TIFF writer, and archive config, discovery, reconstruction,
planning, execution, orchestration and indexing modules.

### Configuration and saved locations

Default configuration is `~/.config/seestar-toolkit/config.toml`, derived from
`Path.home()`. **XDG_CONFIG_HOME is not consulted.** Loading is read-only:
missing implicit config uses defaults without creating files; missing explicit
`--config`, malformed TOML, invalid values or a directory path produce errors.
Unknown keys are ignored. There is no config creation/persistence CLI or saved-location
management command. A manually entered interactive location is not saved.

`[archive]` supports `hierarchy`, `source_action` and `collision_policy`.
`[[locations]]` requires `name`, `latitude`, `longitude`, `radius_m` with finite
numeric values, legal coordinate bounds and nonnegative radius. CLI settings
override config. Location precedence is explicit name, nearest saved match
within its inclusive radius, interactive handling where applicable, then `unknown`.
Matching is local; no geocoder is called. Deterministic tie-breaking is implemented.
Interactive saved-match confirmation/manual fallback requires TTY stdin and no
`--non-interactive`; explicit location avoids prompting. Multiple unmatched
coordinate pairs require explicit/noninteractive handling. The user's real
configuration was not read or changed.

### Relevant existing tests and reusable tooling

| Files under `tests/` | Relevant coverage to retain/reuse |
| --- | --- |
| `unit/test_cli.py`, `unit/test_package.py` | Parser, entry points, version/help, usage errors, config overrides, noninteractive handling, conversion/batch exits. |
| `unit/archive/test_config.py`, `test_planning.py` | Missing/default/malformed config, saved matches, date rollover, hierarchy permutation/normalization, numbering, collisions, deterministic nonmutation. |
| `unit/archive/` remaining tests | Discovery/reconstruction metadata, safe copy/move, collision policies, destination guards and indexing. |
| `integration/test_cli_conversion.py`, `test_raw_conversion.py`, `test_fits_to_tiff_conversion.py`, `test_batch_conversion.py`, `test_stage6_workflows.py` | Real-fixture conversion, dtype/shape/pixels, mixed batch, expected failures and source retention. |
| `integration/test_archive_discovery.py`, `test_archive_reconstruction.py`, `test_archive_planning.py` | Real light/stack association and archive planning contracts. |
| `integration/test_archive_orchestration.py` | Real copy and move, dry-run snapshots, reopened TIFFs, structured index assertions, incremental numbering, alternate hierarchy, saved/explicit/interactive locations, malformed/empty workflows, partial results, collisions, failed TIFF after move, symlink/path escape guards. |
| RGB/Siril integration contracts | Float32/channels-first conversion and historical orientation expectations; not interchangeable with uint16 output proof. |

`tools/validate_clean_install.py` supplies the independent raw GRBG/OpenCV
pixel oracle, module/dependency checks and cleanup pattern. It creates and removes
separate wheel/sdist environments; do not rerun its four-version matrix or treat
it as a persistent B environment. `tools/validate_distribution.py` builds and
inspects isolated distributions and performs runtime smoke checks.
`tools/check_public_inputs.py` verifies the ten approved fixture hashes and
clean public-history boundary. `tools/check_formatting.py` defines the existing
37-file formatting scope. None needs modification for this audit.
Existing tests are evidence of intended coverage, not substitute installed B runs.

### Approved fixture selection

All inputs come from `tests/data/PRIVACY_REVIEW.md` and the approved manifest;
only disposable copies may be used for mutating workflows.

| Fixture relative to `tests/data/` | Bytes | Proposed use |
| --- | ---: | --- |
| `seestar/light.fit` | 4,152,960 | Primary single/batch uint16 GRBG conversion; independent full-pixel oracle; archive light. |
| `seestar/stacked.fit` | 49,775,040 | Matched native IC 434 stack for real archive/index association; uint16 channels-first `(3,3840,2160)`. Larger file justified by existing matched light/stack test. |
| `seestar/stacked_mosaic.fit` | 17,925,120 | Optional smaller native RGB conversion, `(3,2304,1296)`; not a substitute for the matched IC 434 stack. |
| `reference/siril_stacked_mosaic.fit` | 5,760 | Small complementary linear float32 `(3,17,11)` Siril conversion; cannot establish 16-bit output. |
| `reference/siril_stacked.fit` | 24,888,960 | Optional real Siril orientation comparison if needed; not necessary for minimal B raw/archive proof. |
| `seestar/mosaic_1.fit`, `mosaic_4.fit`, `mosaic_6.fit`, `mosaic.fit`, `eq.fit` | 4,152,960 each | Approved raw/mosaic/equatorial alternatives; existing mosaic tests retain their distinct metadata contracts. |

Privacy review replaces terrestrial coordinates with synthetic `(0,0)`, serials
with synthetic identifiers and capture dates with 2000-01-01. Celestial pixels
remain real astronomical data under that review. Use synthetic location names
and coordinates only. The removed 272,923,200-byte Siril mosaic is never needed.

### Development documentation audit

`ARCHITECTURE.md` accurately documents `session_end_date`, `observation_01`,
read-only TOML, location precedence and deferred persistence/JPEG policy.
`PACKAGING.md` documents installed validation/build tooling and supported Python.
`PROJECT_Notes.md` and `PACKAGING.md` still described 9.2a as STARTED: their live
status was corrected using Stage review's opening context, with a link here.
Historical Stage 9.2a reports/evidence and fixture privacy history remain intact.
No final user documentation was authored. The authoritative 9.2b specification
is preserved unchanged; its layout example discrepancy is recorded below.

## D. Files changed

Added by this checkpoint:

- `docs/development/change_documents/STAGE_9/STAGE_9.2b_REPORT.md`: this audit and execution design.
- `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_A.json`: exact read-only installed CLI evidence and preservation hashes.

Modified by this checkpoint:

- `docs/development/PROJECT_Notes.md`: confirmed 9.2a completion and 9.2b Checkpoint A status.
- `docs/development/PACKAGING.md`: confirmed 9.2a completion and link to current audit.

Pre-existing pending files, unchanged:

- `docs/development/CHANGELOG.md`: pending Stage 9.2a closure entry preserved byte-for-byte.
- `docs/development/change_documents/STAGE_9/STAGE_9.2b.md`: supplied untracked authoritative specification preserved byte-for-byte.

No production, test, fixture, packaging metadata, workflow or validator changes.

## E. Findings and validation

- **PASS:** ten installed help/version invocations; both entry points report 1.1.0; all 33 installed source files match current source.
- **Documentation discrepancy:** specification section 9 uses `{date}` and `session_01`; implemented and architectural contracts use `{session_end_date}` and `observation_01`. Validate the actual contracts in B; propose justified N/A for the unsupported literal naming expectations at closure, not silent substitution or feature addition.
- **Not exposed:** saved-location/config writing and JPEG policy switches. Record justified N/A for those CLI capabilities; config reading and JPEG preservation still need B validation.
- **Pending risk probes:** permission errors and same-stem batch collisions need actual B evidence. Source inspection alone is not a runtime FAIL. No functional failure was executed or concealed in A.
- **PENDING:** fresh artifact isolation, conversion/archive/config/error runs, storage, privacy/runtime permissions and uninstall proof, final full project validation and closure review.

Local checkpoint checks: `python -m ruff check .` PASS; configured
`python tools/check_formatting.py` PASS (37 files already formatted);
`python tools/check_public_inputs.py` PASS (10 reviewed fixtures, clean public
root, no oversized blobs); `git diff --check` PASS. Added report/JSON whitespace
and JSON parsing were also checked. Preservation hashes confirm unchanged
CHANGELOG and supplied specification. Full pytest was not rerun for this
documentation-only checkpoint; final project-suite evidence remains due in D.

No release,
tag, push, commit, publication, repository visibility change or Stage 9.3/9.4 work.

## F. Next action — Checkpoint B, not executed

1. Audit the explicit Homebrew Python 3.13 executable/version/provenance, architecture and macOS version. Create one uniquely named disposable local root. Build a v1.1.0 wheel with existing build tooling, record its SHA-256 and metadata, then create a **fresh** representative venv and install that wheel normally. Record dependency checks and prove imports resolve exclusively from its site-packages outside the checkout. No editable install or repository PYTHONPATH.
2. Repeat both entry points' version/help; exercise missing arguments/unknown options (2), no-command help (0), and verbose placement. Capture exact command, exit, diagnostic and artifact provenance with private paths redacted.
3. Copy approved `light.fit` into the disposable root. Run `seestar-toolkit convert INPUT_FITS OUTPUT_TIFF`, reopen TIFF, verify uint16 RGB `(1920,1080,3)` and independent OpenCV GRBG pixels, hash source before/after. Test existing output, missing parent/input, unsupported/malformed input and file/directory mistakes in disposable paths. Add the small Siril fixture as distinct float32 proof if useful.
4. Run `convert-batch INPUT_DIR OUTPUT_DIR` over disposable approved copies with mixed `.fit`/`.FITS` suffixes, synthetic unrelated sentinels, a nested ignored directory and an intentionally invalid input. Verify successful/partial/empty runs, existing-output reruns, same-stem collisions, directory creation limits and source hashes.
5. Build the real archive test's matched tree: `IC 434_sub/Light_IC 434.fit` from approved light and `IC 434/Stacked_195_IC 434.fit` from approved stack, plus synthetic JPEG sentinels. Create explicit disposable TOML config. Resolve and guard every root against symlinks, traversal and overlap; snapshot source and nearby sentinels. First run `archive SOURCE_ROOT ARCHIVE_ROOT --config CONFIG --non-interactive --dry-run`, verify no mutation, then repeat without `--dry-run`. Check `observation_01`, originals/TIFFs, JPEG preservation, target index, date and metadata. Use separate fresh trees for `--source-action move`, collision policies and alternative supported hierarchy. Verify incremental numbering and partial failure retains the archived original. Do not interpret a TIFF failure after move as rollback.
6. Test empty/default-valued, explicit missing and malformed disposable config; CLI overrides; synthetic saved `(0,0)` match and unmatched fallback. Use explicit `--config` for all direct archive invocations to avoid reading real user config. Test implicit missing-default loading only with narrowly isolated `Path.home()` in a labelled installed-code harness, separately from unmodified CLI proof; XDG redirection alone cannot isolate this implementation. Use a PTY where needed for real interactive confirmation and manual fallback. Configuration persistence is not implemented.
7. Verify the approved fixture's +12-hour date result in installed output. Retain the existing independent unit rollover cases for boundary coverage; do not alter real FITS fixtures to manufacture another date. Record this distinction between installed representative-date evidence and boundary unit evidence.
8. Exercise local paths with spaces/nesting and safe disposable permission denials where effective; restore modes in cleanup. Hash original inputs and verify guarded destination/sentinel trees for every mutation. Record genuine failures before any minimal, justified remediation. Remove only owned temporary outputs/environments after evidence capture, or explicitly record a retained representative environment if needed for C/D.

Checkpoint C needs separately authorized safe disposable external/NAS locations;
none were enumerated or inspected. Checkpoint D owns remaining privacy/network,
permissions/uninstall and final pytest/Ruff/format/whitespace/public-input checks.
Do not repeat the four-version matrix, begin later stages or claim formal closure.

---

# Checkpoint B progress — 2026-09-14 (current)

The Checkpoint A report above is preserved verbatim as historical checkpoint
evidence. This entry supersedes its current-status and next-action statements.

## A. Status

**PAUSED — Stage 9.2b remains STARTED. Checkpoint B: PASS after the setup and
validation-harness remediation recorded below.** No production defect was
established and no production code was changed. Checkpoints C/D and formal
closure remain outstanding.

## B. Checkpoint reached

**B — Local installed validation.** No external/removable/NAS filesystem was
inspected or tested. No four-version compatibility matrix was repeated.

## C. Work completed

[Checkpoint B evidence](STAGE_9.2b_CHECKPOINT_B.json) records 61 command results
and 45 assertions, including initial failed assertions and successful corrected
reruns. Expected operational errors are distinguished from failed validation.

### Build and representative installation

Built the current v1.1.0 wheel from a disposable copy of the package inputs,
using a separate build venv: build 1.6.1, setuptools 84.0.0, packaging 26.3 and
pyproject_hooks 1.2.0. The build used `python -I -m build --wheel --no-isolation`;
only the build environment contained build tools. Existing distribution
inspection passed: 39 permitted members, metadata, license, entry point and
private-content checks. All 33 wheel source modules match the checkout byte-for-byte.
Exact wheel size and SHA-256 are retained in the evidence `build` object.

Created a fresh normal venv using Homebrew
`/opt/homebrew/opt/python@3.13/bin/python3.13`, Python 3.13.15, macOS 26.5.2,
arm64. Installed the wheel normally with pip, with no editable install and no
repository PYTHONPATH. Runtime commands ran outside the checkout under the
unique `/tmp/seestar-92b-6snhgrz6/local data` tree. Imports resolved to the fresh
venv's site-packages. `pip check` passed; no pytest/Ruff/build/PDF tooling was
installed in the runtime environment. Both entry points reported 1.1.0 and all
public help commands passed. Exact runtime dependency versions are in JSON.

Network access was used only for approved package dependency downloads during
setup; no network/storage feature was introduced or exercised by the functional
checks. The development environment was not used as installed runtime proof.

### Local functional results

| Area | Result and observed behaviour |
| --- | --- |
| Single conversion | PASS: approved `light.fit` copied to an uppercase `.FITS` path; linear uint16 RGB `(1920,1080,3)` reopened and compared pixel-for-pixel against independent OpenCV GRBG conversion. Source hash unchanged. |
| Single errors | PASS: existing output, missing input, missing parent, directory input/output, malformed synthetic input, unreadable input and unwritable destination returned 1. Existing TIFF/source preserved. Temporary permission modes restored. |
| Batch | PASS: two approved copies with `.fit`/`.FITS`, spaces in paths, ignored text and nested input. Exactly two TIFFs, independent pixel equality and unchanged sources. Missing output directory created; nested missing parent rejected. |
| Batch partial/repeat | PASS: malformed input retained two successful outputs with exit 1. Repeated outputs and same-stem collisions returned 1 without overwriting successful outputs. Empty/missing/file input and file output returned 1. |
| Archive copy | PASS: matched approved IC 434 light/stack copies; dry-run snapshot unchanged before execution. Original hashes preserved, exact archived FITS copies, independent raw/native stack TIFF pixel equality, JPEG untouched and not archived. |
| Layout/date/index | PASS: `{target}/{location}/{session_end_date}`, `20000101`, `observation_01`, `lights`, `tiff`, `seestar_stacked` and target `INDEX.md`. Index preserves synthetic telescope, one light and stack count 195. Index heading is human-readable `Observation 01`. |
| Archive move | PASS: separate disposable tree, dry-run first; FITS removed from source only after archival and JPEG retained. Explicit location exercised. |
| Collisions | PASS: repeat/error-policy runs return 1 and preserve originals/TIFFs. Explicit overwrite restores a deliberately corrupted disposable destination FITS; existing TIFF collisions remain reported with exit 1. Dry-run precedes each mutation and changes no file contents. |
| Config and locations | PASS: explicit empty/default-valued config, saved synthetic `(0,0)` match, alternative hierarchy, CLI location override and `unknown` fallback. Spaces remain in `Synthetic Site`. Config hashes unchanged. |
| Interactive configuration | PASS: actual CLI dry-run under PTY, saved-match acceptance and manual unknown-location naming; exit 0 and no file mutation. No location saving is exposed. |
| Config errors/default | PASS: explicit missing config, malformed TOML and directory config return 1. Implicit missing-default behaviour is separately verified against installed code using a narrow `Path.home()` patch; default path verified and no config created. This API harness is not claimed as unmodified CLI proof. |
| Archive errors | PASS: missing/file source and unsupported `{date}` hierarchy return 1; empty source returns 0. |
| Usage contract | PASS: invalid option/missing arguments return 2; success/help/version/no-command help return 0. |

Only the approved light and native stack FITS were required; selected fixture
hashes are recorded and all ten approved tracked fixture hashes were rechecked.
Malformed inputs, JPEG/text sentinels and the corrupted archive destination are
explicitly synthetic disposable error cases, not additional real captures.

Installed date evidence uses the approved fixtures' synthetic 2000-01-01
capture times; the full project suite supplies independent +12-hour rollover
boundary coverage. No real FITS header or tracked fixture was modified.

Mutating archive calls used distinct resolved source/destination paths beneath
the owned temporary root, with dry-run first, file snapshots and source/destination
hash checks. This is bounded path-safety evidence, not a claim to have monitored
all unrelated filesystem activity. Real user config was never read: direct CLI
archive calls always supplied disposable `--config`. XDG redirection was not
misrepresented as effective isolation.

### Project checks and cleanup

- Full pytest: **330 passed in 11.87 seconds**.
- Ruff: PASS.
- Configured formatting: PASS, 37 files already formatted.
- Public inputs/history: PASS, ten reviewed fixtures, clean public root, no oversized blobs.
- Wheel metadata/content/source inspection: PASS.
- Whitespace and final evidence/privacy/preservation checks: PASS.

Removed the entire uniquely owned temporary root, including wheel, copied
build sources, separate build/runtime venvs, one-off harnesses, configuration,
FITS copies, TIFFs, archives and sentinels. Temporary permission modes were
restored before deletion. The temporary root and locator file no longer exist.
No development venv, real config or unrelated filesystem was removed.

## D. Files changed

This invocation:

- Added `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_B.json`.
- Appended this entry to `docs/development/change_documents/STAGE_9/STAGE_9.2b_REPORT.md`, preserving the complete Checkpoint A text.
- Updated `docs/development/PROJECT_Notes.md` and `PACKAGING.md` to record Checkpoint B and outstanding storage/final checks.

Earlier pending Checkpoint A changes remain: its JSON and report, and the live
development documentation updates. The supplied untracked Stage 9.2b specification
and intentionally modified development CHANGELOG remain unchanged. No production,
test, fixture, metadata, CI or persistent validation-tool changes.

## E. Findings — failures preserved

1. Initial build failed because the development environment had no `build` module. A prematurely attempted wheel install also failed because no wheel existed. A separate temporary build venv resolved this; no development environment dependency was added.
2. Sandbox dependency installation failed on PyPI DNS resolution. Approved escalation allowed the download; build and runtime installation then succeeded. This was not a package compatibility failure.
3. Two initial harness assertions wrongly expected `observation_01` in index prose and `Synthetic_Site` in the path. Actual behaviour is `Observation 01` in the index and preserved spaces in paths. Corrected assertions passed; initial failures remain recorded.
4. An installed default-config harness incorrectly compared an auto-valued enum to the string `copy`. Comparing to `SourceAction.COPY` passed. No production change.
5. A supplemental temporary script stopped with `NameError` because its archive helper was not loaded. The helper was supplied and the supplemental checks rerun successfully. No affected archive command had executed before that failure.
6. Final privacy checking detected a home path in pip's cache-permission warning. The path was redacted to `<user-pip-cache>` while preserving the warning; final evidence contains no home paths. This warning did not fail `pip check`.

These original failures are not retrospectively described as passing attempts.
They are resolved setup/harness findings, with passing final checks. No unresolved
Checkpoint B release defect was demonstrated. No production change was warranted.
C/D privacy/network, storage, macOS permission interpretation and uninstall claims
remain pending; this checkpoint does not establish those broader closure gates.

## F. Next action

Checkpoint C only after a subsequent instruction and identification of safe,
explicit disposable external/removable and/or already-mounted network locations.
Do not enumerate unrelated mounts or reuse production archives. This invocation
stops before C. A future checkpoint needs a new representative installation
because B's temporary environments were removed as requested.

No commit, push, tag, GitHub Release, PyPI publication, visibility change or
Stage 9.3/9.4 work occurred. Stage 9.2b remains STARTED.

---

# Checkpoint C progress — 2026-09-14 (current)

Checkpoint A and B evidence above is preserved verbatim. This entry supersedes
only the current checkpoint status and next action.

## A. Status

**PAUSED — Stage 9.2b remains STARTED. Checkpoint C: FAIL.**

The external filesystem returned `OSError: [Errno 5] Input/output error` during
archive input preparation and subsequently disappeared from its authorised
mount path. Remaining external archive/cross-storage checks and on-device
cleanup are **incomplete**. Independent mounted network/NAS validation passed.
No production defect was established; no production change was made.

## B. Checkpoint reached

**C — storage validation, partially executed with a genuine failure.**
Checkpoint D has not begun. The external failure is not waived, reclassified as
PASS, or obscured by the successful NAS checks.

## C. Work completed

[Structured evidence](STAGE_9.2b_CHECKPOINT_C.json) retains both attempts, exact
commands, exit statuses, assertions, failure and cleanup outcomes, build
provenance and preservation hashes. Storage identities are replaced by labels.

### Environment and safety

Rebuilt v1.1.0 into a 46,318-byte wheel using disposable source/build inputs.
SHA-256: `e66363bd682fd405f785946f8126db3f8492c3e00a58d102f1a906358534cb9c`.
Existing metadata/content/privacy inspection passed (39 allowed members), and
all 33 source modules matched the checkout byte-for-byte. Build tooling:
build 1.6.1, setuptools 84.0.0, packaging 26.3, pyproject_hooks 1.2.0.

Installed normally into a fresh Homebrew Python 3.13.15 venv on macOS 26.5.2
arm64. Both entry points reported 1.1.0, `pip check` passed, imports resolved
inside the temporary runtime site-packages, and build/dev dependencies were
absent. No editable install or repository PYTHONPATH was used. Setup package
downloads were explicitly approved; runtime checks used mounted filesystem I/O.
Exact dependency versions are preserved in the evidence.

Targeted `statfs` calls confirmed the two specified paths were actual mount
points: **exFAT** for the user-designated external/removable test volume and
**smbfs** for the mounted network/NAS test volume. The filesystem-type probe did
not print or store mount-source/host/share fields. No broader mounts or root
contents were enumerated. Both fixed disposable paths were absent before this
run; even pre-existing empty directories would have caused refusal.

The harness checked mount identity, symlinks, resolved containment and device
identity before operations, with disjoint guarded archive source/destination
paths. It used only copies of approved `light.fit` and `stacked.fit` or outputs
generated from those inputs inside storage roots. Explicit empty TOML config
was held in the owned local temporary tree, never the user's configuration.
Paths containing spaces were exercised. No private captures were used.

### Results

| Check | External/removable test volume | Mounted network/NAS test volume |
| --- | --- | --- |
| Mounted/filesystem identity | PASS initially: exFAT; later absent/unmounted | PASS: SMB filesystem |
| Disposable create/write/read | PASS, approved fixture copied and hash verified | PASS, approved fixture copied and hash verified |
| Installed single conversion | PASS, exit 0 | PASS, exit 0 |
| Installed batch conversion | PASS, exit 0; exactly two outputs | PASS, exit 0; exactly two outputs |
| Pixels/source integrity | PASS, uint16 RGB and exact independent pixels; source hashes unchanged | PASS, uint16 RGB and exact independent pixels; source hashes unchanged |
| Archive copy | INCOMPLETE: EIO preparing source before archive CLI execution | PASS: dry-run plan inspected, no dry-run mutation, execution exit 0 |
| Archive originals/TIFFs/index | Not reached | PASS: exact original copies, independent light/stack TIFF pixels, expected hierarchy/index metadata |
| Archive move | Not reached because of external failure | Not required by minimum NAS scope; not performed |
| Local input → storage output | Not reached | PASS, exit 0; different filesystem devices verified |
| Storage input → local output | Not reached | PASS, exit 0; different filesystem devices verified |
| Cleanup | UNVERIFIED on device: root disappeared before exact-path recovery could run | PASS: dedicated directory removed |

The independent NAS attempt recorded nine commands and 36 passing assertions.
Its archive used `{session_end_date}`, `observation_01`, `lights`, `tiff`,
`seestar_stacked`, and target `INDEX.md`. Dry-run destinations had to match the
expected exact paths before execution. No file or directory changed in the
snapshot during dry-run. Archive copy retained source FITS hashes.

Raw TIFFs were compared against independent OpenCV GRBG demosaicing; native
stack TIFFs against channels-last source planes. Reopened TIFFs had exact
array equality, expected shapes, uint16 dtype, RGB photometric interpretation
and 16 bits/sample. Sources remained unchanged for successful copy/conversion
operations. The two NAS cross-storage directions demonstrate different-device
I/O; no external cross-storage success is inferred from them.

### Failure and cleanup sequence

1. External single/batch conversion and verification passed.
2. External archive source preparation stalled. A targeted metadata check of the known disposable stack file also waited, later reporting that file present at 49,775,040 bytes. This does not establish successful copy integrity.
3. The main validation process returned an EIO exception before executing any external archive command. The record remains FAIL. The harness process itself exited 0 after recording the caught exception; that process exit is not treated as validation success.
4. Its `finally` cleanup removed the unused NAS disposable directory. External cleanup refused because the interrupted copy had created a destination before ownership registration completed. It did not delete unregistered content.
5. A separately approved recovery attempt allowed only the exact eight known created/attempted file paths and their ancestor directories, refusing any other entry. Its mount guard failed before deletion. A targeted follow-up confirmed the authorised external root no longer existed and was not mounted. No remount or filesystem reconfiguration was attempted.
6. Independent NAS validation then completed successfully in a newly created dedicated directory and removed all its registered files/directories. This did not alter the original external failure evidence.
7. All owned local temporary environments, build sources, wheel, configuration, fixture copies, outputs and one-off harnesses were removed after processes finished. On-device external files may still remain and are explicitly **not** claimed cleaned.

A sandbox process-lookup attempt also failed because process-list access was
unavailable; an approved scoped lookup found no remaining main validation
process after it exited. This diagnostic limitation did not change test results.

### Validation boundary

Ruff passed; configured formatting passed (37 files already formatted).
`git diff --check`, JSON/privacy checks and prior-evidence preservation checks
passed. All ten approved fixture hashes were checked during both validation
attempts. Full pytest and broader final audit were not rerun: no code/tests/tools
were changed and Checkpoint D was explicitly excluded. B's 330-test result
remains historical evidence, not a new C test run.

Mounted SMB reads/writes are ordinary filesystem operations, not evidence of
Toolkit telemetry. Broader privacy/network/uninstall conclusions remain D's
scope. No claim of monitoring unrelated filesystem contents is made; safety
proof is bounded to specified mount metadata and owned disposable paths.

## D. Files changed

This invocation only:

- Added `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_C.json`.
- Appended this Checkpoint C entry to `docs/development/change_documents/STAGE_9/STAGE_9.2b_REPORT.md`.

Checkpoint A/B JSON, the entire earlier report prefix, the authoritative
specification and pending development CHANGELOG modification are preserved.
Earlier pending PACKAGING.md and PROJECT_Notes.md modifications are retained
unchanged by this invocation; their latest B status predates this C entry.
No production, tests, fixtures, metadata, CI or persistent validator changes.

## E. Findings

**PASS:** NAS local/storage operations, archive copy, both NAS cross-storage
directions and cleanup; external single/batch conversion before failure.

**FAIL:** external filesystem EIO followed by loss of the authorised mount.
Remaining external copy/move/cross-storage validation and on-device cleanup
are unsatisfied. The observations establish a filesystem failure during setup,
not a demonstrated Toolkit release defect. No production remediation is justified.

**Cleanup limitation:** known run-created external data may remain on the
unavailable device. Do not treat path absence while unmounted as successful
removal. No unknown/pre-existing content was deleted.

## F. Next action

Resume **Checkpoint C**, not D, only after the user confirms the external test
volume is safely available again. First reconcile the known run-created
`seestar-toolkit-stage92b-test` contents against the recorded allowed paths;
refuse unknown content and obtain explicit cleanup direction if ownership is
uncertain. Then use a fresh temporary installation for outstanding external
archive copy/move and cross-storage checks, preserving this EIO history.
Do not configure/remount storage or substitute another root automatically.

No commit, push, tag, publication, visibility change, Checkpoint D or Stage
9.3/9.4 work occurred. Stage 9.2b remains STARTED.

---

# Checkpoint C replacement-device recovery — 2026-09-14 (current)

All previous checkpoint text remains unchanged. This entry records a recovery
on a **different physical USB device**, as explicitly confirmed by the user,
even though it uses the same authorised mount pathname. It does not revise the
original device's failure or imply its remaining files were cleaned.

## A. Status

**PAUSED — Stage 9.2b remains STARTED. Overall Checkpoint C: PASS.**

Replacement-device recovery validation: **PASS**.
Replacement-device cleanup: **completed and verified**.
Seestar Toolkit production defect demonstrated: **none**.

The original EIO and unconfirmed old-device cleanup remain a documented
environmental limitation. Under the user's recovery instructions, that
limitation does not prevent C from passing after replacement-device success.

## B. Checkpoint reached

**C — recovery completed.** Checkpoint D has not begun.

The historical sequence remains:

1. Original external device: EIO → disappearance → cleanup unconfirmed (**FAIL**).
2. Mounted network/NAS validation and cleanup: **PASS**, evidence retained without rerunning any NAS operation.
3. Replacement external/removable device: archive copy/move, external cross-storage checks and cleanup **PASS**.

## C. Work completed

The [Checkpoint C JSON](STAGE_9.2b_CHECKPOINT_C.json) retains every original
field and adds `replacement_device_recovery`, `overall_checkpoint_c_status`
and an explicit status-scope explanation. Its original `status` remains the
historical FAIL; the new overall field records the current PASS disposition.
Nine recovery commands and 44 assertions passed. No genuine recovery failure
occurred or was removed from evidence.

### Replacement baseline and installation

Only the authorised mount itself and exact dedicated disposable path were
checked. The path was mounted, not a symlink, and its disposable directory
was absent. No unknown/pre-existing content required reconciliation. macOS
`statfs` reported **msdos** (FAT-family filesystem); no mount-source identity,
volume name, hostname, credentials or wider filesystem inventory was recorded.
The different physical identity is user-confirmed, not inferred merely from
the pathname or filesystem type. Successful approved-fixture creation,
reopening and SHA-256 equality established writable/readable operation.

A fresh normal Homebrew Python 3.13.15 installation on macOS 26.5.2 arm64 used
a rebuilt 1.1.0 wheel. The 46,318-byte wheel has SHA-256:
`5d018fcad8f5a5c73c8dc26b31393ff36d7d9ada387d6c05824eb1bc243f4b9f`.
Metadata/content/privacy inspection passed (39 permitted members), and all 33
wheel source modules matched the current checkout. A separate temporary build
venv used build 1.6.1 and setuptools 84.0.0. Runtime imports resolved from the
fresh site-packages, `pip check` passed, both entry points reported 1.1.0, and
build/dev packages were absent. No editable install or repository PYTHONPATH.
Exact installed dependencies are retained in JSON. Setup downloads alone used
approved network access; no NAS testing, access or configuration was repeated.

### Recovery results

| Required check | Result |
| --- | --- |
| Mounted/writable baseline | PASS: mounted msdos filesystem; exact disposable root created; approved light copy hash/readback verified. |
| Archive COPY | PASS: fresh approved light/stack source copies, dry-run first, execution exit 0, originals retained with identical hashes. |
| Archive MOVE | PASS: second fresh source tree, dry-run first, execution exit 0, archived hashes identical and original source FITS removed. |
| Hierarchy/products | PASS: nested archive destination, `IC 434/unknown/20000101/observation_01`, light/stack originals and TIFFs, target index. Index verifies synthetic device and stack count. |
| Dry-run safety | PASS: exact planned original/TIFF/index destinations checked; full dedicated-tree file/directory snapshot unchanged before execution. |
| TIFF validation | PASS: raw light `(1920,1080,3)` and native stack `(3840,2160,3)`, uint16 RGB, 16 bits/sample, exact independent pixel equality. |
| Local → replacement external | PASS: installed conversion exit 0, reopened output pixel equality, source hash unchanged. |
| Replacement external → local | PASS: installed conversion exit 0, reopened output pixel equality, source hash unchanged. |
| Different-filesystem proof | PASS: local input device identifier differs from replacement mount device identifier; identifiers compared locally, not published. |
| Spaces/nesting | PASS: baseline, source and output names contain spaces; archive destination has nested directories. |
| Replacement cleanup | PASS: only registered created paths removed; exact dedicated directory confirmed absent. |
| Local cleanup | PASS: build/runtime environments, copied sources, wheel, config, test data and one-off harness removed. |

Archive roots were explicitly disjoint, contained beneath the dedicated root,
and checked for symlinks, resolved containment, mount identity and unchanged
device identity before operations. Generated destinations were registered
before execution; cleanup refused any entry outside that known set. No
unrelated root contents were enumerated. Only approved `light.fit` and
`stacked.fit` copies and their generated outputs populated the storage tree.
All ten approved repository fixture hashes were verified before testing.

Pixel validation used independent OpenCV GRBG demosaicing for raw lights and
channels-last source planes for native RGB stacks. Reopened TIFFs were compared
for exact array equality, shape, dtype and TIFF RGB/bit-depth tags. No automatic
stretching or other pixel transformation was assumed.

Original external single/batch PASS evidence was reused as requested; no
standalone single/batch regression set was repeated. Conversion invocations in
this recovery specifically established the outstanding cross-storage directions.
No already-passing NAS operation was repeated and no old physical-device files
were sought, reconciled or deleted.

Ruff and configured formatting passed (37 files already formatted).
`git diff --check`, JSON/privacy checks and preservation checks passed.
Full pytest was not rerun for this evidence-only recovery; no production,
test or persistent tooling changes were made and D remains unstarted.

## D. Files changed

This recovery invocation only:

- `docs/development/change_documents/STAGE_9/STAGE_9.2b_REPORT.md`: appended this entry, preserving the complete earlier report prefix.
- `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_C.json`: added recovery evidence/current disposition; all original failure/NAS fields retained unchanged.

Checkpoint A/B JSON, authoritative specification and pending development
CHANGELOG were verified unchanged. Earlier pending PACKAGING.md and
PROJECT_Notes.md changes remain untouched. No production, tests, fixtures,
package metadata, CI or persistent validator changes.

## E. Findings

The replacement-device recovery passed with confirmed cleanup and no demonstrated
Toolkit defect. NAS evidence remains valid and unchanged. The old physical
USB device's genuine EIO, disappearance and unconfirmed on-device cleanup are
still recorded exactly as failures/limitations of that initial attempt.
Nothing in this recovery establishes that the failed device has been repaired
or cleaned. No production remediation was needed or performed.

## F. Next action

Checkpoint D only on a subsequent instruction. It will need a fresh temporary
representative installation because all recovery environments were removed.
Stage-wide final audit, remaining closure gates and review are not established
by this C recovery report. Stage 9.2b remains STARTED.

No commit, push, tag, release, publication, visibility change, Checkpoint D or
Stage 9.3/9.4 work occurred.

---

# Stage 9.2b final completion report — Checkpoint D — 2026-09-14

This is the current completion audit. All earlier checkpoint text and A/B/C
JSON remain unchanged historical evidence. No unavailable storage was searched,
queried, reconnected or tested in D.

## A. Decision

**FAIL for formal closure readiness. Technical validation: PASS.**

All technical checkpoint work is complete for review. Formal criteria **140,
182, 183, 184 and 185** remain unsatisfied: evidence is not yet committed,
independent review/approval and the user closure commit are pending, and the
post-commit state/exact-commit CI gates cannot yet be verified. These are
intentional closure gates, not demonstrated product defects. Do not bypass them.

**Stage 9.2b remains STARTED.** The 186 individual assessments comprise
176 PASS, 5 FAIL and 5 justified N/A. No technical criterion requires live
access to the now-unavailable external/NAS filesystems.

## B. Files changed

Every pending file at the end of Stage 9.2b:

| File | Purpose and ownership |
| --- | --- |
| `docs/development/CHANGELOG.md` | Pre-existing pending Stage 9.2a closure entry; preserved byte-for-byte, no Stage 9.2b commit invented. |
| `docs/development/PACKAGING.md` | Live 9.2a completion and 9.2b audit, uninstall and privacy facts; final gates remain pending. |
| `docs/development/PROJECT_Notes.md` | Live technical checkpoint completion with Stage 9.2b still STARTED. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b.md` | User-supplied untracked authoritative specification; unchanged. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b_REPORT.md` | Historical A/B/C reports plus this complete A–N final audit. Earlier report prefix preserved. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_A.json` | Installed CLI audit evidence, unchanged in D. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_B.json` | Local installed results and genuine setup/harness failures, unchanged in D. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_C.json` | Initial device FAIL, NAS PASS and replacement recovery PASS, unchanged in D. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2b_CHECKPOINT_D.json` | New final local privacy/uninstall/build evidence, preservation hashes and all 186 assessments. |

No production, tests, fixtures, package metadata, CI or persistent validation
helper changed. No file was deleted from the repository. No index/staging change.

## C. Representative environment

B, C and D use supported **Homebrew Python 3.13.15, macOS 26.5.2, arm64**.
Exact base executable is recorded in JSON under the Homebrew Python 3.13.15
Cellar framework. Runtime commands execute outside the checkout from fresh
normal wheel-installed venvs. Imports resolve beneath those venvs' site-packages;
no editable install, development-venv runtime proof or repository PYTHONPATH.

D rebuilt wheel and sdist with a separate temporary build environment using
build 1.6.1/setuptools 84.0.0. The wheel was built from the sdist and normally
installed for the uninstall/privacy audit. Both distributions passed existing
metadata/content/license/entry-point/privacy inspection. All 33 wheel source
modules match the checkout. Exact artifact sizes, hashes and dependency
versions are recorded in [D evidence](STAGE_9.2b_CHECKPOINT_D.json).

`pip check` passed before and after uninstall. No pytest/Ruff/build packages
were present in the disposable runtime. No compatibility matrix was repeated;
Python support remains `>=3.11,<3.15` as established in Stage 9.2a.

## D. Installed CLI inventory

Both entry points report `seestar-toolkit 1.1.0`; top-level and all subcommand
help passed with exit 0 in A/B. The public interface is:

```text
seestar-toolkit [-h] [--version] [--verbose] {convert,convert-batch,archive} ...
seestar-toolkit convert [-h] INPUT_FITS OUTPUT_TIFF
seestar-toolkit convert-batch [-h] INPUT_DIR OUTPUT_DIR
seestar-toolkit archive [-h] [--dry-run] [--location LOCATION]
    [--hierarchy HIERARCHY] [--source-action {copy,move}]
    [--collision-policy {skip-identical,error,overwrite}]
    [--non-interactive] [--config PATH] SOURCE_ROOT ARCHIVE_ROOT
```

`python -m seestar_toolkit` uses the same parser. `-h` means `--help`; global
version/verbose options precede the subcommand. No command prints help and
returns 0. No public config-write/location-save/JPEG-policy or separate
plan/apply subcommand is present. Internal Python APIs are not public commands.

## E. Conversion results

B's single conversion of approved `light.fit` produces uint16 RGB
`(1920,1080,3)` with exact independent OpenCV GRBG pixel equality. Source hashes
remain unchanged. Existing outputs are preserved; missing input/parent,
malformed data and file/directory errors return 1. B's batch processes two
`.fit`/`.FITS` copies nonrecursively, ignores unrelated/nested input, and
creates exactly two verified outputs. Partial, repeat, same-stem and empty-input
behaviour is preserved in the evidence; successful outputs are not overwritten.

C supplies recorded storage-specific conversion/source verification, including
all required external/NAS cross-storage directions. No such checks were repeated
in D. D's limited local conversions create uninstall data while observing
runtime network events; they do not replace B/C's stronger pixel evidence.

## F. Archive results

B and C verify public `--dry-run`, then copy/move execution on disposable data.
Actual hierarchy uses **`{target}/{location}/{session_end_date}`** and
**`observation_01`**, with `lights`, `tiff`, `seestar_stacked` and target
`INDEX.md`. Do not substitute `{date}` or `session_01`. Date computation is
`date(capture_datetime + 12 hours)`; installed representative dates and existing
unit boundary cases support it.

Plans, output paths, FITS hashes, TIFF arrays, index metadata and source actions
are verified. Copy retains sources; successful move removes only transferred
source FITS. JPEGs remain untouched and no JPEG-policy switch is exposed.
Repeated existing TIFFs return partial/exit 1 while preserving them; explicit
FITS overwrite does not overwrite those TIFFs. This is not whole-workflow
rollback: existing integration tests retain the archived original after a
post-move TIFF failure. Recorded path guards/snapshots are bounded evidence,
not a claim of whole-system filesystem surveillance.

## G. Configuration/location results

The read-only TOML loader uses `~/.config/seestar-toolkit/config.toml` via
`Path.home()`; it does not consult XDG_CONFIG_HOME. Explicit `--config` supplies
all direct test archive invocations and isolates real user configuration.
B separately labels its installed-code Path.home patch for absent implicit
config; no default file is created. Explicit missing/malformed/directory config
returns 1. CLI overrides, synthetic saved-location matching, unknown/manual
fallback and real PTY confirmation passed. Configuration hashes remain unchanged.

Supported data: `[archive]` hierarchy/source_action/collision_policy and
`[[locations]]` name/latitude/longitude/radius_m. Saved matching is local distance
calculation; no geocoding service. Config creation/persistence and saved-location
writing are not exposed, and no missing roadmap interface was implemented.

## H. Storage results

| Storage evidence | Final interpretation |
| --- | --- |
| Original external device, exFAT | Genuine EIO during archive setup, then disappearance. Initial single/batch PASS retained; failed-device cleanup remains **unconfirmed**. |
| Replacement physical external device, FAT-family/msdos | Archive copy/move, both local/external directions, path/source/output verification and dedicated-directory cleanup **PASS**. Different physical device is user-confirmed despite same pathname. |
| Mounted network/NAS, smbfs | Single/batch, archive copy, local→NAS and NAS→local plus cleanup **PASS**. |
| Cross-storage | Four local/storage directions passed with different-device evidence. |
| Current availability | User reports both storage resources unavailable; expected and not re-probed in D. Recorded results remain valid. |

Original EIO/disappearance/unconfirmed cleanup are not retrospectively changed
to PASS or labelled a Toolkit defect. Under explicit recovery instructions,
old-device cleanup is an accepted historical environmental limitation, not a
reason to downgrade recovered C. No final-audit criterion needs live storage;
there are no unresolved live-storage operations or substituted devices.

## I. Error/exit-code results

| Trigger | Observed result |
| --- | --- |
| Help/version, successful convert/batch/archive, no-command help | 0 |
| Missing/invalid/unreadable FITS, unwritable output, existing TIFF, file/directory mistakes | 1 with diagnostic |
| Empty batch | 1; reports no FIT/FITS files |
| Mixed batch | 1; successful outputs retained |
| Missing/malformed/directory config, unsupported hierarchy token | 1 with diagnostic |
| Empty archive input | 0; no invented observation |
| Existing TIFF archive rerun or explicit FITS overwrite with retained TIFF collisions | 1/partial; existing TIFFs preserved |
| Explicit archive collision policy error | 1/failed; originals preserved |
| Missing arguments/unknown option | 2/usage error |
| Module invocation after successful uninstall | 1, module no longer found; expected uninstall outcome |

No unexplained runtime exit discrepancy was hidden. Harness assertion failures
are separately preserved and not mislabelled as application failures.

## J. Privacy/permissions/uninstall results

All 33 source modules' imports and call sites were audited. No telemetry,
analytics, updater, external FITS/image metadata transmission or network service
was found. Version lookup is local package metadata. FITS paths and archive
operations use filesystem APIs; location matching is local arithmetic.

Six fresh installed module executions (help, version, single, batch, archive
dry-run and archive copy) used a CPython audit hook installed before package
import. It blocks and records `socket.*` and subprocess/system/spawn events.
**Zero actual events occurred.** The hook self-test used `sys.audit` only and
made no socket, DNS or connection attempt. No network access was introduced to
prove absence. Approved dependency downloads were setup-only. This is scoped
source/Python-runtime evidence, not packet capture or an exhaustive audit of
native dependency binaries or all possible inputs. Local CLI/index output may
contain user-selected paths and metadata; absence of transmission is not a
promise to sanitize arbitrary user data. Evidence uses approved synthetic values.

B demonstrated local permission denial and mode restoration. C demonstrated
successful authorised mounted I/O. D local operations succeeded. CLI logs do
not establish GUI/TCC prompt state; tool sandbox approvals are not macOS
privacy settings. No security setting was altered, no privacy control bypassed,
and no Full Disk Access permission was requested or claimed necessary.

D's 14 commands and 29 checks establish:

- Activation selects the temporary venv; `deactivate` restores PATH/unsets VIRTUAL_ENV and leaves the installation intact.
- `pip uninstall -y seestar-toolkit` removes its console entry point and importable module.
- Config and every source/generated/archive file hash remain unchanged after uninstall.
- Removing the owned runtime venv also leaves those files unchanged.
- Removing config separately leaves generated/source/archive data unchanged.
- All remaining owned local tooling, artifacts, data and harnesses were then removed.

No development venv or real user config was modified by uninstall/cleanup.
The old failed physical device remains outside D access and its cleanup is
still unconfirmed.

## K. Findings/remediation

Historical findings are preserved, not silently converted into passing attempts:

1. B missing build tool and premature missing-wheel install; resolved with separate temporary build tooling and correct build/install order.
2. B sandbox DNS failure; approved setup download retry succeeded.
3. B incorrect harness assumptions about index text, spaces and enum value; corrected assertions passed, originals retained.
4. B supplemental missing helper caused NameError; supplied helper and successful rerun recorded.
5. B private cache path in a pip warning detected by final evidence validation; only that path redacted, warning retained.
6. C original device EIO and disappearance; conservative cleanup refusal, failed mount-guard recovery and old-device cleanup limitation retained. Sandbox process-lookup limitation also recorded.
7. C NAS PASS and different replacement-device PASS/cleanup supplied the required recovery without rewriting the failure.

D found no new production defect and required no production change. Its audit
clarifies the difference between historical C `status` and current
`overall_checkpoint_c_status`, and between written evidence and the still-pending
commit/review gates. No technical failure is concealed by that distinction.

## L. Project validation

| Check | Result |
| --- | --- |
| Full pytest | **330 passed in 11.85s** |
| Ruff | PASS |
| Configured formatting | PASS, 37 files already formatted |
| git diff --check / added evidence whitespace | PASS |
| Public fixture/history validation | PASS: 10 reviewed fixtures; clean public root; no oversized blobs |
| Stage 9.2b evidence/privacy | PASS: valid JSON; preserved A/B/C/spec/CHANGELOG hashes and report prefix; no identifying mount/home/credential data added |
| Wheel inspection | PASS: 39 permitted members; metadata/license/entry point/privacy; 33 source modules identical |
| Sdist inspection | PASS: 46 permitted members; metadata/license/entry point/privacy |
| D installed local validation | PASS: 14 commands, 29 checks; six runtime network-event probes |
| Git scope/artifact audit | Only expected development files; no source/test/fixture/CI/metadata delta; index untouched; owned temporary artifacts removed |

Independent sdist runtime validation is retained from 9.2a; no runtime or metadata
change makes repeating its matrix necessary. D inspected both rebuilt artifacts
and installed the wheel built from the sdist. No helper requires live storage,
and no existing validation behaviour was weakened to accommodate absent mounts.

## M. Scope exclusions

No commit, push, release tag, GitHub Release, PyPI publication, public visibility
switch, final release ZIP, final user documentation or Stage 9.3/9.4 work. No
new production feature. Version 1.1.0 remains unreleased. Repository privacy is
the user-confirmed starting state preserved by this run, not a newly queried
remote claim. No Stage 9.2b commit ID added to CHANGELOG.

## N. Closure criteria

Exactly one status is assigned per specification criterion. **FAIL: 140, 182,
183, 184, 185.** These require the later reviewed/approved commit and post-commit
gates. **N/A: 66, 159, 166, 167, 168**, with justification in the individual
rows. All others PASS within their stated evidence scope. None fails merely
because previously validated storage is now disconnected.

| # | Specification criterion | Status | Evidence / justification |
| ---: | --- | --- | --- |
| 1 | Branch is `main`. | PASS | Git branch is main. |
| 2 | Work starts at or after `398b771`. | PASS | HEAD remains 398b771; no commits made. |
| 3 | Stage 9.2a remains COMPLETE. | PASS | User-confirmed formal 9.2a completion; baseline commit retained. |
| 4 | Pending Stage 9.2a CHANGELOG entry is preserved. | PASS | CHANGELOG SHA-256 matches the opening checkpoint hash. |
| 5 | Version remains 1.1.0. | PASS | Metadata and both installed entry points report 1.1.0. |
| 6 | v1.1.0 remains unreleased. | PASS | Unreleased state preserved; no release action performed. |
| 7 | Repository remains private. | PASS | User-confirmed private starting state preserved; no visibility action. No fresh remote query claimed. |
| 8 | Stage 9.3 has not begun. | PASS | No Stage 9.3 work performed. |
| 9 | Stage 9.4 has not begun. | PASS | No Stage 9.4 work performed. |
| 10 | Representative supported Python is justified. | PASS | Supported native Homebrew Python 3.13 chosen as the representative interpreter. |
| 11 | Exact patch version is recorded. | PASS | B/C/D record Python 3.13.15. |
| 12 | Executable/provenance is recorded. | PASS | Exact Homebrew base executable recorded in B/C/D JSON. |
| 13 | macOS version is recorded. | PASS | macOS 26.5.2 recorded. |
| 14 | arm64 is confirmed. | PASS | arm64 confirmed by runtime provenance. |
| 15 | Fresh venv is used. | PASS | B and D use fresh normal venvs; C recovery also used a fresh venv. |
| 16 | Distribution artifact is installed. | PASS | Built release-format 1.1.0 wheel installed normally. |
| 17 | No editable install is used. | PASS | B noneditable check and normal wheel installs; no editable install used. |
| 18 | Development venv is not runtime proof. | PASS | Development Python runs project checks only, not installed runtime proof. |
| 19 | Repository PYTHONPATH is not used. | PASS | Runtime environment removes repository PYTHONPATH; module probes use -I. |
| 20 | Module resolves from representative site-packages. | PASS | B/C/D module paths resolve beneath temporary site-packages. |
| 21 | Commands run outside checkout where practical. | PASS | Runtime commands execute from disposable local directories outside checkout. |
| 22 | `seestar-toolkit --version` passes. | PASS | A/B/C both-entry evidence; normal installed D console version also passed. |
| 23 | `python -m seestar_toolkit --version` passes. | PASS | A/B/C module --version returned 0. |
| 24 | Both report 1.1.0. | PASS | Both entry points print seestar-toolkit 1.1.0. |
| 25 | Top-level help passes. | PASS | Installed top-level help returns 0. |
| 26 | Every public subcommand is inventoried. | PASS | convert, convert-batch and archive inventoried in A and final section D. |
| 27 | Every public subcommand help is validated. | PASS | Both-entry help for all three commands passed in A/B. |
| 28 | Exact public syntax is recorded for Stage 9.3. | PASS | Exact syntax/options in A evidence and final section D. |
| 29 | Internal APIs are not presented as public CLI. | PASS | Archive Python APIs distinguished from the three public commands. |
| 30 | Approved fixture is used. | PASS | Approved light.fit and manifest hash used in B. |
| 31 | Installed convert succeeds. | PASS | B installed single success returned 0. |
| 32 | Success exit status is correct. | PASS | Success exit 0 recorded. |
| 33 | TIFF is created. | PASS | TIFF creation verified in B. |
| 34 | TIFF is readable. | PASS | TIFF reopened with tifffile. |
| 35 | Dimensions are correct. | PASS | Raw-derived output shape 1920 x 1080 x 3 verified. |
| 36 | RGB structure is correct. | PASS | RGB photometric interpretation and array structure verified. |
| 37 | 16-bit output is confirmed. | PASS | uint16 confirmed in B; C also verifies 16 bits/sample. |
| 38 | Source is unchanged. | PASS | B source hash unchanged. |
| 39 | Existing-output behaviour is recorded. | PASS | Existing output rejected with exit 1 and unchanged bytes. |
| 40 | Missing-input behaviour is recorded. | PASS | Missing input returns 1 with diagnostic. |
| 41 | Invalid/unsupported behaviour is recorded where safely testable. | PASS | Malformed synthetic input and input/output type errors return 1. |
| 42 | Temporary outputs are cleaned. | PASS | B local outputs removed; original failed-device leftovers remain the expressly accepted C environmental exception. |
| 43 | Disposable batch tree is used. | PASS | B owned disposable batch tree used. |
| 44 | Only approved fixtures populate it. | PASS | Only approved FITS copies; clearly synthetic malformed/unrelated sentinels exercise error/ignore handling. |
| 45 | Multiple supported inputs are exercised. | PASS | Two .fit/.FITS inputs processed. |
| 46 | Expected TIFF outputs are created. | PASS | Exactly two expected TIFFs verified. |
| 47 | Sources remain intact. | PASS | Batch source snapshots unchanged. |
| 48 | Unsupported/unrelated-file behaviour is recorded. | PASS | Text and nested input ignored; case-insensitive FITS suffixes accepted. |
| 49 | Output-directory behaviour is correct. | PASS | Output directory created with existing parent; missing parent/file destination rejected. |
| 50 | Success exit status is correct. | PASS | B successful batch returns 0. |
| 51 | Error/partial behaviour is recorded. | PASS | Mixed batch retains two successes and returns 1; empty input returns 1. |
| 52 | Repeated/existing-output behaviour is recorded. | PASS | Repeat and same-stem collisions return 1 while preserving outputs. |
| 53 | Temporary data is cleaned. | PASS | B local batch tree removed; original failed-device cleanup exception remains explicit. |
| 54 | Exact public archive CLI surface is audited. | PASS | A installed archive help and source audit agree. |
| 55 | Source/destination semantics are recorded. | PASS | Explicit source/destination roots documented and exercised. |
| 56 | Hierarchy/template semantics are recorded where exposed. | PASS | Actual session_end_date template/permutations validated; unsupported date token rejected. |
| 57 | Plan/dry-run availability is recorded. | PASS | Public --dry-run verified. |
| 58 | Mutating/apply availability is recorded. | PASS | Omitting --dry-run executes; no separate apply subcommand. |
| 59 | Source/JPEG/stacked/location/session/index semantics are recorded. | PASS | A inventory plus B/C originals, JPEG retention, stacks, locations, observations and index evidence. |
| 60 | Internal-only functionality is distinguished from CLI. | PASS | No invented public commands for internal APIs. |
| 61 | Public dry-run is validated if exposed. | PASS | B/C dry-run commands return 0 and preserve snapshots. |
| 62 | Disposable source is used for archive validation. | PASS | Only disposable approved light/stack copies used. |
| 63 | Discovery/reconstruction result is correct for test data where applicable. | PASS | One matched IC 434 observation with one retained light and stack count 195 verified. |
| 64 | Planned hierarchy matches design where applicable. | PASS | Plans match actual target/location/session_end_date hierarchy and observation_01. |
| 65 | +12-hour rule is verified where applicable. | PASS | Installed representative date plus full unit suite test_session_end_date_uses_twelve_hour_rule boundary cases. |
| 66 | `session_01` is verified where applicable. | N/A | Literal session_01 is not implemented; user confirms observation_01 is authoritative and it is verified in B/C. No alias feature added. |
| 67 | `seestar_stacked` is verified where applicable. | PASS | Native stack originals/TIFFs verified in seestar_stacked. |
| 68 | Dry-run causes no unintended mutation. | PASS | B file hashes and C complete file/directory snapshots unchanged during dry-run. |
| 69 | Public mutating operation is tested if exposed. | PASS | Installed archive copy and move passed in B and replacement C. |
| 70 | Dry-run is inspected first where available. | PASS | Dry-run inspected before each tested archive mutation. |
| 71 | Exact disposable roots are safety-checked. | PASS | Resolved containment/disjointness/symlink/device checks recorded; no live storage needed in D. |
| 72 | Executed hierarchy/files/actions match plan where applicable. | PASS | Expected original/TIFF/index paths and source actions verified. |
| 73 | Nothing outside disposable roots is modified. | PASS | Recorded guarded destinations and snapshots show only owned roots used; not a whole-system monitoring claim. |
| 74 | Archive test data is cleaned. | PASS | B, NAS and replacement archive data cleaned; old failed-device partial setup remains the explicitly accepted environmental limitation. |
| 75 | Actual config implementation is audited. | PASS | Read-only TOML loader and CLI reviewed in A/D. |
| 76 | Expected config path is verified or discrepancy recorded. | PASS | Path.home()/.config/seestar-toolkit/config.toml verified; XDG variable is not consulted. |
| 77 | Missing-config behaviour is validated. | PASS | Missing explicit config returns 1; absent implicit default verified in labelled installed-code harness. |
| 78 | Read/write/create behaviour is validated where exposed. | PASS | Exposed reads verified and config hashes unchanged; create/write persistence is not exposed. |
| 79 | Malformed config behaviour is validated. | PASS | Malformed TOML returns 1 with useful diagnostic. |
| 80 | Real user config is untouched. | PASS | Direct archive invocations use explicit disposable --config; real config not read or written. |
| 81 | Temporary isolated config is used where practical. | PASS | Disposable config; Path.home patch only in separately labelled missing-default API harness. |
| 82 | Saved-location behaviour is validated where exposed. | PASS | Synthetic saved-location match and real PTY acceptance verified. |
| 83 | Fallback/unknown location behaviour is validated where exposed. | PASS | Unknown fallback, manual naming and explicit CLI precedence verified. |
| 84 | No personal GPS enters committed evidence. | PASS | Only approved synthetic coordinates/identifiers enter evidence. |
| 85 | No unexpected external geocoding/network dependency exists. | PASS | Local distance matching; no geocoder call/import; D runtime network events empty. |
| 86 | Writable local operation succeeds. | PASS | Local conversion/archive and D uninstall-data operations succeed. |
| 87 | Paths containing spaces are exercised. | PASS | Input, output, source and location names with spaces tested. |
| 88 | Nested paths are exercised. | PASS | Nested local/archive paths tested. |
| 89 | Existing destination behaviour is recorded. | PASS | Existing TIFF rejection, identical FITS skip, explicit collision/error/overwrite recorded. |
| 90 | Missing destination creation is validated where expected. | PASS | Batch and archive directory creation verified; single missing-parent error documented. |
| 91 | Non-existent input behaviour is validated. | PASS | Missing single/batch/archive inputs return 1. |
| 92 | File/directory type errors are validated where relevant. | PASS | File/directory input, output and config mistakes return 1. |
| 93 | Safe external/removable availability is assessed. | PASS | C recorded actual authorised mount/type before testing; no re-probe required in D. |
| 94 | If available, only a disposable directory is used. | PASS | Only dedicated run-created directory used on each physical device. |
| 95 | If available, representative operation passes or genuine failure is preserved. | PASS | Initial exFAT EIO retained; replacement FAT-family archive/cross-storage PASS. |
| 96 | If unavailable, limitation is honestly recorded. | PASS | Old-device disappearance/unconfirmed cleanup and current expected absence explicitly recorded. |
| 97 | Production astronomy archive is untouched. | PASS | No real captures or production archive accessed. |
| 98 | Identifying volume path is not committed. | PASS | Only privacy-safe storage labels in evidence; no actual volume path. |
| 99 | Safe mounted-network availability is assessed. | PASS | C recorded mounted smbfs at the authorised root. |
| 100 | If available, only a disposable directory is used. | PASS | Only the dedicated NAS disposable directory used. |
| 101 | If available, representative operation passes or genuine failure is preserved. | PASS | NAS single/batch/archive and both local directions passed; cleanup confirmed. |
| 102 | If unavailable, limitation is honestly recorded. | PASS | Current expected NAS absence documented; historical PASS remains valid. |
| 103 | No credentials are stored. | PASS | No NAS credentials/configuration read or recorded. |
| 104 | Production NAS archive is untouched. | PASS | No production NAS archive accessed. |
| 105 | Identifying NAS details are not committed. | PASS | No host/share/volume identity in evidence. |
| 106 | Mounted I/O is distinguished from Toolkit network-service behaviour. | PASS | Mounted filesystem operations distinguished from Toolkit services/telemetry. |
| 107 | Cross-storage is attempted where feasible. | PASS | Local-to/from NAS and replacement external directions executed in C. |
| 108 | At least one different-root scenario passes where feasible. | PASS | Four recorded different-device directions pass. |
| 109 | No same-filesystem assumption is introduced. | PASS | Local/external and local/NAS device identity comparisons prove distinct filesystems. |
| 110 | Inability to test is recorded. | PASS | Initial external inability preserved and later recovery recorded; D does not require live devices. |
| 111 | Missing input non-zero behaviour is validated. | PASS | Missing inputs return 1 with diagnostics. |
| 112 | Unwritable destination is tested where safely reproducible. | PASS | B chmod-based unwritable destination returns 1/EACCES; modes restored. |
| 113 | File-vs-directory error is tested where relevant. | PASS | B file-versus-directory errors verified. |
| 114 | Invalid config is tested where relevant. | PASS | B missing/malformed/directory config errors verified. |
| 115 | Unsupported/malformed input is tested. | PASS | B deliberately invalid FITS returns operational failure. |
| 116 | Anticipated errors provide useful diagnostics. | PASS | Captured expected errors are diagnostic, without CLI traceback; separate harness traceback preserved as harness failure. |
| 117 | No unintended source loss occurs. | PASS | Input hashes preserved for copy/failures; successful moves retain identical archived originals; no Toolkit-caused loss demonstrated. |
| 118 | Temporary permissions are restored. | PASS | B records restoration before owned-root cleanup. |
| 119 | Exit 0 is verified for success. | PASS | Installed successful operations return 0. |
| 120 | Exit 1 is verified for operational failure. | PASS | Expected runtime/config/filesystem/collision failures return 1. |
| 121 | Exit 2 is verified for usage error. | PASS | Missing arguments and unknown option return 2. |
| 122 | Any discrepancy is treated as a finding. | PASS | Setup/harness failures and storage EIO preserved; no unexplained exit discrepancy hidden. |
| 123 | No telemetry is found. | PASS | No telemetry found in all-module source audit or six instrumented runtime paths; stated audit limits apply. |
| 124 | No analytics is found. | PASS | No analytics imports/calls/events found in the same scoped audit. |
| 125 | No update checking is found. | PASS | No updater/version-network lookup; package version comes from local metadata. |
| 126 | No external FITS/image metadata transmission is found. | PASS | No external image/FITS metadata transmission found; local indexes may retain metadata by design. |
| 127 | No network access is introduced for validation. | PASS | No network request introduced for runtime privacy proof. Explicit setup downloads are separated from functional/audit traffic. |
| 128 | Mounted network I/O is characterised accurately. | PASS | SMB filesystem I/O is user-selected storage, not Toolkit telemetry. |
| 129 | Unexpected network behaviour is release-blocking. | PASS | Unexpected network events would fail the local audit; none observed; remain release-blocking if found. |
| 130 | Observed macOS permission requirements are recorded. | PASS | B permission denial and C authorised I/O recorded; GUI/TCC prompt state not inferred from CLI logs. |
| 131 | Privacy controls are not bypassed. | PASS | No macOS security settings changed; sandbox approvals are not TCC bypasses. |
| 132 | Full Disk Access is not claimed necessary without evidence. | PASS | No Full Disk Access request or unsupported requirement claim. |
| 133 | `deactivate` behaviour is recorded. | PASS | D subshell activation/deactivate restores PATH and unsets VIRTUAL_ENV; installation remains. |
| 134 | package/venv removal behaviour is recorded. | PASS | D pip uninstall removes console/module; subsequent owned venv removal verified. |
| 135 | Config persistence after uninstall is understood. | PASS | D config hash unchanged after uninstall. |
| 136 | Separate config removal is understood. | PASS | D separate config deletion verified without changing generated/archive data. |
| 137 | User/archive data is not automatically removed. | PASS | D all source/generated/archive hashes unchanged after package uninstall and venv removal. |
| 138 | Development venv is untouched. | PASS | Only disposable runtime/build venvs removed; development venv not modified by dependency operations. |
| 139 | Real user config is untouched. | PASS | Real user config untouched throughout; D uses explicit disposable path. |
| 140 | Installed CLI inventory is committed in development evidence. | FAIL | Installed inventory is written in proposed development evidence but not committed; no-commit instruction intentionally leaves this gate unsatisfied. |
| 141 | Environment provenance is recorded. | PASS | B/C/D exact Python/macOS/architecture/artifact/isolation recorded. |
| 142 | Conversion evidence is recorded. | PASS | B and C pixel/source/exit evidence retained. |
| 143 | Batch evidence is recorded. | PASS | B and C batch evidence retained. |
| 144 | Archive evidence/limitations are recorded. | PASS | B/C archive results and original failed-device limitation retained. |
| 145 | Storage evidence/limitations are recorded. | PASS | C initial failure, NAS PASS, replacement PASS and current unavailability retained. |
| 146 | Error/exit evidence is recorded. | PASS | B operational/usage diagnostics and D post-uninstall module absence recorded. |
| 147 | Privacy/permission/uninstall observations are recorded. | PASS | D source/runtime privacy, bounded macOS observations and uninstall facts recorded. |
| 148 | No private paths/credentials/GPS are committed. | PASS | New evidence privacy scan passes; A/B/C hashes preserved; no private storage/home/credential details introduced. |
| 149 | Completion report is created. | PASS | Final A–N completion report appended, preserving checkpoint history. |
| 150 | Structured evidence is added if useful. | PASS | A/B/C retained; D structured evidence and individual closure audit added. |
| 151 | PACKAGING.md is updated where needed. | PASS | PACKAGING.md updated with current audit/uninstall/privacy facts and formal gates. |
| 152 | PROJECT_Notes.md is updated where needed. | PASS | PROJECT_Notes.md updated to technically validated STARTED, pending independent closure gates. |
| 153 | Final user docs are not authored. | PASS | No final User Guide/Quick Start/PDF authored. |
| 154 | Full pytest passes. | PASS | Final pytest: 330 passed in 11.85s. |
| 155 | Ruff passes. | PASS | Final Ruff: all checks passed. |
| 156 | Formatting passes. | PASS | Configured formatter: 37 files already formatted. |
| 157 | `git diff --check` passes. | PASS | Final git diff --check and new-evidence whitespace checks pass. |
| 158 | Public-fixture/history validation passes. | PASS | Ten approved fixture hashes, clean public root, no oversized blobs pass. |
| 159 | Installed validator passes if added. | N/A | No persistent installed Stage 9.2b validator added. Temporary D probes passed and were removed; existing helpers have no live-storage dependency. |
| 160 | Distribution validation passes where relevant. | PASS | D wheel and sdist metadata/content/privacy inspection pass; wheel built from sdist installed. Independent sdist runtime already established by unchanged 9.2a metadata/runtime. |
| 161 | No unexpected generated artifacts are tracked. | PASS | No tracked build/venv/wheel/tar/pyc artifacts; all owned D temporary data removed. |
| 162 | No unexpected private files are tracked. | PASS | Tracked public-input checks and changed-evidence privacy audit pass. |
| 163 | Pre-approval working tree contains only expected changes. | PASS | Only expected development documentation/evidence and preserved CHANGELOG differ; index untouched. |
| 164 | Genuine failures are preserved. | PASS | Every B setup/harness failure and C EIO/recovery remains preserved. |
| 165 | Production changes occur only for proven defects. | PASS | No production changes; no demonstrated production defect. |
| 166 | Production fixes receive automated tests. | N/A | No production fix was made, so fix-specific new regression tests are inapplicable; existing tests retained. |
| 167 | Affected installed validation is rerun after fixes. | N/A | No production fix requiring affected installed rerun; D installed audit still passes. |
| 168 | Full validation is rerun after fixes. | N/A | No production fix requiring another full-suite rerun; final full project suite passes. |
| 169 | No new feature work is introduced. | PASS | No new application feature added. |
| 170 | No PyPI publication occurs. | PASS | No PyPI publication performed. |
| 171 | No GitHub Release is created. | PASS | No GitHub Release created. |
| 172 | No release tag is created. | PASS | No release tag created; local v1.1.0 tag absent. |
| 173 | Repository is not made public. | PASS | No visibility change; user-confirmed private state preserved. |
| 174 | No final release ZIP is created. | PASS | No final release ZIP assembled; disposable inspection artifacts removed. |
| 175 | Stage 9.3 implementation does not begin. | PASS | Stage 9.3 not begun. |
| 176 | Stage 9.4 implementation does not begin. | PASS | Stage 9.4 not begun. |
| 177 | Codex returns a complete closure report. | PASS | Complete A–N report delivered for review. |
| 178 | All criteria are individually assessed. | PASS | All IDs 1–186 individually assessed and mechanically checked for completeness. |
| 179 | Every N/A has explicit justification. | PASS | Every N/A includes explicit implementation/scope-based justification. |
| 180 | Unsatisfied criteria are listed. | PASS | Unsatisfied IDs 140, 182, 183, 184, 185 explicitly listed. |
| 181 | Codex does not commit. | PASS | No commit performed. |
| 182 | ChatGPT independently reviews evidence. | FAIL | Independent ChatGPT review of this final D report has not yet occurred. |
| 183 | User commits only after explicit approval. | FAIL | The approved user closure commit does not yet exist; awaiting independent review and explicit approval. |
| 184 | Post-commit repository state is verified. | FAIL | No closure commit exists to verify post-commit state against. |
| 185 | Exact final commit receives green CI where required. | FAIL | No exact final Stage 9.2b commit/CI result exists. Current-base evidence cannot substitute for the later gate. |
| 186 | Stage 9.2b is not marked COMPLETE until all applicable gates pass. | PASS | Stage remains STARTED; no premature COMPLETE claim. |
