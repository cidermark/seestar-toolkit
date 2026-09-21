# Stage 9.3a PROGRESS REPORT

**Stage: STARTED. Checkpoint A: PASS. B and C: not begun. Formal COMPLETE: pending.**

## Checkpoint A — audit and design

Starting branch `main`, HEAD `519f0e3` (Stage 9.2b: validate installed CLI and
storage workflows). Initial dirty state was only the expected pending development
CHANGELOG entry. Its bytes and earlier Stage evidence are preserved. The supplied
request ends mid-sentence; the complete Checkpoint A instructions were sufficient.

Created the authoritative specification with 65 individually numbered criteria.
Criteria 1–18 cover completed A work; 19–65 remain pending later checkpoints or
formal closure. The JSON records each individually; no final closure is claimed.

## Evidence and command audit

The existing noneditable local-directory installation reports 1.1.0, imports from
site-packages and matches all 33 checkout Python source files. This is a current
validated CLI audit, not a fresh wheel installation. Both entry points passed ten
help/version checks. Full exact CLI help is captured in the checkpoint JSON.

Inventory covers root docs, AGENTS, live DEV_README/ARCHITECTURE/PACKAGING/
PROJECT_Notes and relevant Stage 9.1/9.2 Markdown evidence. Of 21 CLI-shaped fenced
examples, 12 parse successfully and nine historical usage/ellipsis lines return
2. Those original outcomes remain recorded: synopsis notation is not executable
shell syntax and must not be presented as copy-paste commands. Additional shell
examples are inventoried by document and line in JSON. Development editable,
validation uv/build/test and historical environment commands are not recommended
user installation sequences. No conversion or archive command was executed for
this documentation audit. B must validate the selected complete example sequences.

No potential product defect was demonstrated. Real file conversion, storage,
config and uninstall claims rely on preserved Stage 9.2 evidence plus current
source/tests, not new access to private capture data or mounted storage.

## Authoritative fact matrix

Short Stage filenames below resolve in this report's directory; abbreviated
`archive/...` source references resolve under `src/seestar_toolkit/`. References
identify files and relevant symbols/sections; installed evidence is in the JSON.

| Claim | Verified finding / qualification | Authority |
|---|---|---|
| Version/release | 1.1.0; semantic versioning; Unreleased until GitHub publication. | pyproject.toml; CHANGELOG.md; docs/development/PACKAGING.md |
| Platform | macOS Apple Silicon arm64 only; qualify tested OS versions and Apple support at actual release. No Intel/Rosetta, Windows or Linux support claim. | docs/development/change_documents/STAGE_9/STAGE_9.1a_AUDIT.md §7; STAGE_9.2a_REPORT.md |
| Python | >=3.11,<3.15; 3.11–3.14 supported, no longer merely candidates. | pyproject.toml; STAGE_9.2a_REPORT.md; STAGE_9.1d_REPORT.md |
| Distribution | Wheel primary, sdist secondary; no Toolkit PyPI, installer script or current published release implied. | docs/development/PACKAGING.md; STAGE_9.2a_REPORT.md |
| Interpreter/venv | Homebrew recommended; check which python3 and version; ~/.venvs/seestar-toolkit activation/deactivation/full-path alternative; no system edits, global PATH or required uv. | docs/development/PACKAGING.md; STAGE_9.1a_AUDIT.md §7 |
| Dependencies | Runtime astropy/numpy/opencv-python-headless/tifffile; dev/build extras separate; installation may download dependencies. | pyproject.toml; STAGE_9.2a_REPORT.md; tools/validate_clean_install.py |
| CLI | Both entry points 1.1.0; help/version/verbose global, convert/convert-batch/archive only; full help captured in JSON. | src/seestar_toolkit/cli.py:build_parser; checkpoint A commands |
| Single conversion | Explicit input/output; existing output rejected; no automatic stretch. | src/seestar_toolkit/conversion.py; tests/integration/test_cli_conversion.py; STAGE_9.2b_CHECKPOINT_B.json |
| Batch | Flat non-recursive, case-insensitive FIT/FITS, per-file continuation, totals, empty input fails; output parent constraints apply. | src/seestar_toolkit/batch.py; tests/unit/test_batch.py; STAGE_9.2b_CHECKPOINT_B.json |
| Archive discovery | Root and immediate child files only; not arbitrary recursion; absolute archive root required. | src/seestar_toolkit/archive/discovery.py:discover_seestar_inputs; archive/planning.py; tests/integration/test_archive_discovery.py |
| Archive naming | {target}/{location}/{session_end_date}; observation_01; date is capture timestamp plus 12 hours, formatted YYYYMMDD. | src/seestar_toolkit/archive/planning.py:session_end_date; tests/integration/test_archive_planning.py |
| Archive products | Observations, lights, TIFFs, seestar_stacked and target INDEX.md; JPEG originals untouched. | src/seestar_toolkit/archive/execution.py; archive/indexing.py; STAGE_9.2b_CHECKPOINT_B.json |
| Archive safety | Dry-run before mutation, backups, explicit copy first; move disposable data only in validation. No whole-operation rollback. | src/seestar_toolkit/archive/execution.py; tests/integration/test_archive_orchestration.py; STAGE_9.2b_REPORT.md |
| Collisions | skip-identical/error/overwrite concern FITS destinations; existing TIFF behaviour separately documented; config can override default copy. | src/seestar_toolkit/cli.py:_run_archive; archive/execution.py; STAGE_9.2b_CHECKPOINT_B.json |
| Configuration | Read-only ~/.config/seestar-toolkit/config.toml; explicit config replaces default lookup; absent default allowed, absent explicit file errors; XDG ignored. | src/seestar_toolkit/archive/config.py; tests/unit/test_cli.py; STAGE_9.2b_CHECKPOINT_D.json |
| Config schema/precedence | [archive] hierarchy/source_action/collision_policy; [[locations]] name/latitude/longitude/radius_m; CLI over config over defaults. No config/saved-location writing or JPEG switch. | src/seestar_toolkit/archive/config.py; src/seestar_toolkit/cli.py:_run_archive |
| Location | Explicit location overrides saved nearest GPS matching; TTY confirmation/manual fallback; --non-interactive suppresses prompts, unknown fallback. No geocoder. | src/seestar_toolkit/cli.py:_resolve_interactive_location; archive/planning.py; tests/unit/test_cli.py |
| Input scope | Validated S50 raw/native RGB, mosaic and evidence-qualified AltAz/EQ; tested Siril float32 RGB standard/mosaic conversion only. | STAGE_9.1a_AUDIT.md §9; tests/integration/test_siril_rgb_conversion.py; tests/integration/test_rgb_handling_contract.py |
| Unsupported | No all Seestar files/modes promise; DSLR, S50 Pro, S30/S30 Pro and MP4 processing unsupported/unimplemented. | STAGE_9.1a_AUDIT.md §9; docs/development/PROJECT_Notes.md |
| TIFF | Linear uint16 RGB for Seestar; float32 RGB for supported Siril. Raw Bayer demosaicing; already-RGB channels handled without second demosaic; no stretch. | src/seestar_toolkit/conversion.py; tests/integration/test_fits_to_tiff_conversion.py; tests/integration/test_siril_rgb_conversion.py |
| Exit codes | 0 success/help/version; 2 parser misuse; 1 expected conversion, batch or archive operational failure. No blanket friendly-error guarantee for arbitrary exceptions. | src/seestar_toolkit/cli.py:main; tests/unit/test_cli.py; STAGE_9.2b_CHECKPOINT_B.json |
| Diagnostics | --verbose before command; summaries and stderr errors; do not claim all internal metadata diagnostics are CLI-visible. | src/seestar_toolkit/cli.py; STAGE_9.2b_CHECKPOINT_A.json |
| Storage | Local, replacement removable device, mounted NAS and cross-storage workflows validated; original removable failure remains historical FAIL. No new storage access here. | STAGE_9.2b_CHECKPOINT_C.json; STAGE_9.2b_CHECKPOINT_D.json; STAGE_9.2b_REPORT.md |
| Privacy | Audited Toolkit runtime has no telemetry, analytics, update checks or external metadata transmission; mounted NAS I/O is filesystem access. Metadata may persist in FITS/indexes/diagnostics. | STAGE_9.2b_CHECKPOINT_D.json; tests/data/PRIVACY_REVIEW.md; archive/indexing.py |
| Permissions | User-selected filesystem access can be restricted; no demonstrated universal Full Disk Access requirement, no bypass instructions. | STAGE_9.2b_REPORT.md; STAGE_9.1a_AUDIT.md §7 |
| Uninstall | Deactivate/remove package or venv independently of optional config cleanup; image/archive data persists. | STAGE_9.2b_CHECKPOINT_D.json; docs/development/PACKAGING.md |
| License | MIT; retain intentional public copyright attribution. | LICENSE; pyproject.toml |
| Fixture authority | Ten reviewed public-safe fixtures; synthetic Siril mosaic is 5760 bytes; never restore oversized historical object. | tests/data/public_fixtures.json; tests/data/README.md; tests/data/PRIVACY_REVIEW.md; tools/check_public_inputs.py |

## Discrepancies and disposition

- **D1 — documentation defect:** DEV_README.md:59 calls archive discovery recursive; current discovery is shallow. Correct live wording when authorised in C.
- **D2 — documentation defect:** Root README and public CHANGELOG are transitional placeholders; docs/user contains only .gitkeep and CONTRIBUTING is absent. Implement only in B/C.
- **D3 — documentation defect:** A blanket 16-bit TIFF description omits validated Siril float32 output. Both types must be explicit in the new guides.
- **D4 — documentation defect:** DEV_README archive examples omit explicit copy, so an existing move configuration can change their action. New copy examples must specify --source-action copy and the chosen collision policy.
- **D5 — documentation defect:** Existing development configuration example contains a named location and nonzero coordinates. Do not promote those values; use clearly synthetic metadata. Review live example correction in C.
- **H1 — not a contradiction / historical context:** {date}, session_01, proposed config writing and JPEG policy belong to plans, not the installed CLI contract. Preserve historical records.
- **H2 — not a contradiction / historical context:** Old Python candidate language, uv validation and editable development install commands are historical/developer context, not current user installation requirements.
- **H3 — not a contradiction / historical context:** Stage 9.2b report retains pre-commit formal FAIL and original storage failures. Starting commit is now 519f0e3; preserve those reports and append current status only.
- **H4 — not a contradiction / historical context:** Nine historical usage/ellipsis parser probes returned 2. They are syntax notation, not executable examples; preserve raw outcomes and exclude from copy-paste commands.
- **H5 — not a contradiction / historical context:** Generic wheel tag does not imply cross-platform support; tested macOS plus Apple-supported-at-release policy does not establish every Apple-supported version.

## Designed User Guide table of contents

1. What Seestar Toolkit is: v1.1.0 scope, Unreleased status and guide authority.
2. Supported environment: macOS Apple Silicon policy, Python 3.11–3.14,
   requirements and unsupported platforms.
3. Supported inputs: S50 raw/native RGB, mosaic, qualified AltAz/EQ, tested Siril;
   unsupported cameras, modes, DSLR and MP4.
4. Install: Homebrew, interpreter installation/checking, venv creation/activation,
   release availability, wheel primary, sdist alternative, installation verification,
   full-path alternative and deactivation.
5. CLI overview: both entry points, help/version/global verbosity and option order.
6. Single FITS-to-TIFF conversion: paths, output verification and collision errors.
7. Batch conversion: flat discovery, explicit output, summaries and partial errors.
8. Archive safely: backups, dry-run inspection, explicit copy, optional move,
   shallow work-root structure, collision policies and partial failure limits.
9. Archive layout: target/location/session_end_date, +12-hour rule, observations,
   lights, stacked Seestar originals, TIFF products, target INDEX.md and JPEGs.
10. Read-only configuration and locations: file/schema, explicit/default lookup,
    precedence, saved matches, prompts, unknown/manual fallback and absent writers.
11. TIFF characteristics: uint16 Seestar / float32 Siril, linearity, raw Bayer
    demosaicing, already-RGB treatment and absence of stretching.
12. Storage and permissions: local, removable, mounted NAS, cross-storage, spaces,
    parent paths, filesystem failures and macOS access restrictions.
13. Privacy: audited runtime network behaviour, retained FITS/index/diagnostic
    metadata and safe sharing.
14. Diagnostics and troubleshooting: verbose output, errors/exit codes, environment
    verification, known limitations and getting help/reporting problems.
15. Uninstall: deactivate, package/venv removal, optional config removal and
    persistent generated TIFF/archive/user data.

All required User Guide topics map to these sections; this is an outline, not the
Guide implementation. Configuration examples will use a clearly synthetic site
and coordinates, never values copied from development examples.

## Designed Quick Start table of contents

1. Audience, requirements and supported environment.
2. Obtain v1.1.0 artifacts when published; wheel preferred.
3. Install/check supported Homebrew Python.
4. Create and activate the recommended venv; install the local wheel.
5. Verify 1.1.0, entry point and environment.
6. Convert one public-safe example input.
7. Convert a flat batch directory.
8. Archive safety, location/config context and dry-run.
9. Inspect plan, then explicitly copy using the same options; link move/collision detail.
10. Deactivate and follow the authoritative full User Guide.

## Designed root README table of contents

1. Project identity and description.
2. v1.1.0 Unreleased status.
3. Key capabilities.
4. Supported platform/Python and input scope.
5. Installation pointer to Quick Start and Guide.
6. Minimal conversion example.
7. Documentation links and authority.
8. Archive safety and metadata privacy.
9. Known limitations.
10. Contributing and reporting issues.
11. MIT license.

Keep this a landing page; no duplicated full installation/archive manual.

## Designed CONTRIBUTING table of contents

1. Bug reports: version, environment, command and sanitised diagnostics.
2. Feature requests: describe the use case without assuming roadmap promises.
3. Pull requests: focused changes and relevant development instructions.
4. Quality expectations: appropriate tests, Ruff, configured formatting and whitespace.
5. FITS privacy: review/sanitise GPS, device and capture metadata; never request
   private real datasets through public issues.

## Designed public CHANGELOG entry

Retain `## [1.1.0] - Unreleased` without a publication date. Design concise bullets
for single/batch linear FITS conversion, supported native/raw/Siril RGB handling,
archive planning/copy/move with collisions and indexes, read-only configuration
and local location matching. Include supported environment/input boundaries and
privacy/safety pointers where useful. Omit internal Stage chronology and future
feature promises. Detailed history remains in the development CHANGELOG.

## Privacy, scope and next checkpoint

New evidence contains no private home/volume/share names, credentials, real GPS
or capture names. Existing public license attribution is intentional. Fixture
privacy/history validation passed. This is not a claim that every historical
internal document is public-ready; D5 requires a neutral replacement if its live
example is retained in the later documentation work.

Before B, Stage review should accept this design and discrepancy dispositions.
B must verify selected Homebrew instructions against current primary documentation,
resolve an actual release-download link without pretending Unreleased artifacts
are published, and validate neutral install/conversion/archive examples in a
safe disposable context. No new product feature is needed by this audit. Exact
macOS release wording must retain tested-and-Apple-supported qualification.

B and C remain pending. Repository visibility was not changed; no commit, push,
tag, GitHub Release, PyPI publication, PDF or later-stage work occurred. No
production, tests, fixtures, metadata, CI or public deliverable was changed.

## Files changed in Checkpoint A

Created:

- `docs/development/change_documents/STAGE_9/STAGE_9.3a.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.3a_CHECKPOINT_A.json`
- `docs/development/change_documents/STAGE_9/STAGE_9.3a_REPORT.md`

Modified by appending current status:

- `docs/development/PACKAGING.md`
- `docs/development/PROJECT_Notes.md`

Pre-existing `docs/development/CHANGELOG.md` modification preserved unchanged.

## Validation

Results are recorded in the checkpoint JSON and final validation appendix below.
No tests added, changed or weakened. Distribution rebuild is deferred to C because
A does not change the package README or other distribution inputs.

## Checkpoint B

PENDING — not authorised in this invocation.

## Checkpoint C and formal closure

PENDING — all technical and independent review/user commit/post-commit gates must
pass before Stage 9.3a becomes COMPLETE.

## Final Checkpoint A validation results

- Full pytest: **330 passed in 10.80s**, Python 3.13.15.
- Ruff: **PASS**, all checks passed.
- Applicable formatting: **PASS**, 37 files already formatted.
- Public fixture/history checks: **PASS**, 10 reviewed fixtures, clean public root,
  no oversized blobs.
- Installed CLI: **PASS**, ten help/version commands; 33 source files identical.
- Example audit: 12 executable CLI examples accepted; nine historical synopsis
  probes rejected with exit 2 and retained as non-executable notation.
- Documentation/JSON/privacy: **PASS**, local links, 65 ordered criteria and
  28 authoritative fact rows checked; no private values introduced.
- Whitespace: **PASS**, `git diff --check` plus direct checks of new files.
- Preservation: **PASS**, pending development CHANGELOG, root deliverables,
  metadata and earlier Stage evidence remain byte-identical to the audit baseline.

No genuine product/validation failure is hidden; raw synopsis-parser rejections
remain in JSON. No additional permission, network or external-storage operation
was needed. Await independent Stage review before Checkpoint B.

## Checkpoint B — completion report

### A. Status

**PAUSED — Stage 9.3a remains STARTED.** This appended section is the current
checkpoint status; earlier A statements about unstarted B are historical.

### B. Checkpoint reached

**Checkpoint B — PASS**, subject to independent Stage review. Checkpoint C has
not begun. Criteria 19–48 are now satisfied by authorisation, the two documents
and validation; the B JSON individually records all 65 criteria (1–48 PASS,
49–65 PENDING). No formal completion or future commit is claimed.

### C. Files changed

Created:

- `docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md`: full authoritative user guidance.
- `docs/user/SEESTAR_TOOLKIT_QUICK_START.md`: abbreviated experienced-user route.
- `docs/development/change_documents/STAGE_9/STAGE_9.3a_CHECKPOINT_B.json`:
  per-example evidence, original harness failure, remediation and check results.

Modified:

- `docs/development/change_documents/STAGE_9/STAGE_9.3a_REPORT.md`: append this B report.
- `docs/development/PACKAGING.md`: append B status and installation validation limits.
- `docs/development/PROJECT_Notes.md`: append B status and remaining boundary.

Existing pending Stage 9.2b development CHANGELOG, Stage specification, A JSON and
A report prefix preserved. Public root docs, metadata, CI, production, tests and
fixtures unchanged. No public CONTRIBUTING, PDF or release artifact created.

### D. User Guide

Implemented introduction/authority plus all 15 designed topic groups: supported
environment; inputs/limitations; installation; CLI; single conversion; batch;
archive safety; layout; config/locations; TIFF output; storage/permissions;
privacy; diagnostics/troubleshooting; uninstall; help. Requirements and
recommendations are separated. The release remains Unreleased; obtaining artifacts
is explicitly conditional on publication, with no fabricated release URL/date.

Homebrew instructions reference current official installation/formula pages.
Explicit standard-prefix Python avoids changing global shell configuration or
Apple's Python. The dedicated venv route covers wheel, alternate sdist, checks,
activation/deactivation and full-path CLI; no PyPI Toolkit install or uv requirement.

### E. Quick Start

Implemented requirements/release availability, Python/venv/wheel/version checks,
single/batch conversion, backup/dry-run/explicit-copy archive sequence, brief
location/config notes, deactivation and Guide links. Detailed collision tables,
TOML schema, sdist, diagnostics and uninstall instructions deliberately remain in
the authoritative Guide. Support and privacy claims are no broader than the Guide.

### F. Command-example validation

**50 executable bash-line occurrences** across the two documents; every one has
shell syntax validation and a per-example method/result in JSON:

| Category | Count | Evidence |
|---|---:|---|
| Installed CLI executed and parser-validated | 21 | Help/version and single/batch/archive commands; placeholders mapped to disposable approved data. |
| Other commands executed | 11 | Version, brew version, pip check and import-path inspection. |
| Shell exit-status check executed | 1 | `echo $?` in a shell. |
| Temporary venv lifecycle evidence | 7 | Two creation occurrences and five activation/deactivation occurrences covered by one executed fresh lifecycle. |
| Interpreter/entry-point selection checks | 4 | Executed with explicit selected installed paths; no private shell profile read. |
| Static-only | 6 | Two Homebrew install, three pip artifact install and one named uninstall occurrence; official formula/pip help/prior clean-install evidence. |

Two inline positional-argument synopses are syntax/static checked, not literal
filename instructions. One synthetic TOML block is accepted by the installed
configuration loader and used by archive validation.

The existing noneditable installed package is 1.1.0 with all 33 source files
matching checkout. This is not a newly built/installed wheel. Actual wheel/sdist
installation proof remains the preserved Stage 9.2a evidence; B creates no release
artifacts. Empty venv creation/activation is newly exercised. Mutating examples
operate only on disposable approved fixture copies; injected explicit disposable
config prevents reading the real user's configuration. Unmodified examples also
pass parser checks. Sources are preserved, TIFFs reopened (uint16 Seestar and
float32 Siril), and archive originals/TIFFs/indexes verified. Move is dry-run only.
All owned environments/test data were cleaned; the pre-existing CLI is retained.

**Original failure retained:** first harness attempt FAIL with
`FileExistsError: [Errno 17] File exists: '.'`. The helper mistook `convert --help`
for a conversion needing fixture setup; it failed before executing that CLI call.
The completed earlier probes and failure are preserved in JSON. Remediation
classifies help/version before workflow setup. The second complete attempt PASS.
This was a validation-helper defect, not a documented command or product defect.

### G. Archive-safety review

Both documents introduce archive with backups, shallow source-root selection,
explicit dry-run/copy/skip-identical, plan inspection, then copy with otherwise
identical flags. Source root means root/direct-child files, not recursive traversal.
Absolute, separate archive roots and spaces are explained. Move follows later,
with source removal before derivative completion, collision consequences and no
whole-operation rollback. Identical FITS may retain sources even under move;
existing TIFFs remain collisions independently of the FITS overwrite policy.

### H. TIFF/output review

Seestar raw/native RGB produces uint16 RGB TIFF; supported Siril float32 RGB
produces float32 TIFF. The guides do not generalise all outputs as 16-bit. They
explain linearity, demosaicing only raw Bayer, already-RGB preservation and the
lack of automatic stretching/reprojection. Archive claims remain Seestar-specific.

### I. Configuration/location review

Read-only default config path, explicit config requirements, ignored XDG lookup,
CLI/config/default precedence, local nearest saved matching, TTY prompts and
unknown/manual fallback documented. No config-writing, saved-location-writing,
JPEG-policy or plan/apply interfaces invented. TOML values are explicitly synthetic.

### J. Supported/unsupported scope

All 28 A facts reviewed against new prose. macOS arm64 only, Python 3.11–3.14,
qualified tested-and-Apple-supported-at-release OS policy and supported S50/Siril
input boundaries retained. No Intel/Rosetta, Windows/Linux, all-modes, DSLR,
S50 Pro, S30/S30 Pro or MP4 support claim. No future-feature promise.

### K. Privacy review

No private path/volume/share, credential, real GPS or private capture example
introduced. Only neutral placeholders and synthetic site coordinates used. Network
claims remain bounded to the audited Toolkit; metadata retention/sharing warnings
cover FITS, indexes and diagnostics. No USB/NAS access was needed or performed.

### L. Documentation discrepancies

D1 shallow discovery, D3 dtype and D4 explicit copy addressed in new public guides.
D2 is resolved for the two guides only; root-document work remains C. D5 avoided
by synthetic TOML; existing development example remains for C review. Historical
planning and failure records were not rewritten. No potential product defect found.

### M. Validation

- All 50 shell examples checked/classified; 21 installed CLI executions PASS.
- Synthetic TOML schema PASS; neutral disposable conversion/archive results PASS.
- Links/anchors, Markdown fences, version/platform/Python/input consistency,
  archive sequence and public documentation privacy review PASS.
- Ruff PASS; applicable formatting PASS (37 files already formatted).
- Public fixtures/history PASS (10 reviewed fixtures, clean public root, no oversized blobs).
- `git diff --check` PASS, plus direct whitespace checks including untracked files.
- Preservation PASS: pending development CHANGELOG and earlier evidence untouched.
- Full pytest not rerun for documentation/evidence-only B; specification §6
  requires it at C or for behaviour-capable changes. Prior A's 330 PASS is retained
  as historical evidence, not presented as a new run.

### N. Next action

Independent ChatGPT review, then Checkpoint C **only after explicit subsequent
instruction**. Stage remains STARTED. No commit, push, publication, visibility
change, tag, Release, PDF, checksum manifest or later-stage work performed.

## Checkpoint B — editorial remediation revalidation

**Current decision: FAIL. Stage 9.3a remains STARTED; Checkpoint C has not begun.**
The preceding pre-review technical PASS remains historical. The original
independent editorial review failed on documentation quality; that is a genuine
failed review, not a passing Checkpoint B result. The separately remediated User
Guide and Quick Start were supplied as editorially approved candidates for this
validation. The earlier validation-helper `FileExistsError` is also retained.

Both candidates now pass claim-by-claim review against the installed 1.1.0 CLI,
current source and metadata, Stage 9.1a/9.1d/9.2a/9.2b evidence and this Stage
specification. This includes Python 3.11–3.14, qualified Apple-silicon/macOS and
S50 input scope, shallow archive discovery, +12-hour night naming, copy/move and
collision behaviour, partial-operation limits, JPEG handling, archive versus
standalone TIFFs, uint16 Seestar versus float32 Siril output, read-only config,
ignored XDG lookup, location matching, storage, privacy, permissions, exit codes
and installation/uninstall facts. No potential product defect was found.

The installed CLI check used a fresh temporary Python 3.13 development venv with
an editable 1.1.0 install. Both entry points returned 1.1.0. Root and all three
subcommand help pages matched the guides. Global `--verbose --version` worked
before a command; `convert --version` returned parser code 2. The guide's command
forms and archive options parse correctly. This run is not new clean wheel/sdist
proof; the Stage 9.2a installation matrix remains that authority. The current
Homebrew `python@3.13` formula and Apple-silicon `/opt/homebrew` prefix were
checked against official Homebrew pages.

The objective documentation defects reported during validation received only
line-level corrections:

- The Guide dry-run and copy examples now use the same archive path.
- The Guide uninstall module entry point has a valid inline-code span.
- Both documents now contain working relative cross-links.
- Quick Start release downloading is explicitly conditional on publication.
- A Quick Start trailing space was removed, and a concise warning covers
  sharing FITS, configuration, index and diagnostic material.

User Guide Contents includes every intended level-1/level-2 heading; all 90
Markdown links resolve, anchors match, and 158 fence markers are balanced. Quick
Start's two Guide links resolve and its 58 fence markers are balanced. Direct
whitespace checks pass for both guides. No speculative or stylistic rewrite was
made.

Fresh checks: **330 pytest passed**; **Ruff PASS**; **configured formatting PASS**
(37 files); **public fixture/history/privacy check PASS** (10 reviewed fixtures,
clean public root, no oversized blobs); **pip check PASS**. The repository-wide
`git diff --check` **FAILS** on trailing whitespace in the pre-existing modified
`docs/development/PROJECT_Notes.md` lines 781–817. Those user-owned lines are
outside this guide validation and remain untouched. An initial attempt with the
default shell Python could not run pytest/Ruff/Toolkit because those packages
were absent; a sandboxed install attempt could not resolve PyPI. The approved
temporary environment remedied that setup issue; neither initial result is
misstated as a product failure.

Applicable B closure criteria 19–48 are substantively satisfied after the
objective corrections, but the requested repository-wide whitespace gate is
unresolved. Checkpoint B therefore remains **FAIL**, despite both guide
candidates passing their content checks. Criteria 49–65 remain PENDING. The
pending Stage 9.2b development CHANGELOG entry, earlier Stage evidence, public
root docs, production, tests, fixtures, metadata and CI were preserved. No
commit, push, Checkpoint C or Stage 9.3b work occurred.

## Checkpoint B — whitespace remediation revalidation

**Current decision: PASS. Stage 9.3a remains STARTED.** This is a separate
revalidation after the original genuine editorial-quality FAIL and the later
content-validation PASS / repository-whitespace FAIL. Both earlier FAIL results
and the successful content evidence above remain historical facts.

The user removed trailing spaces from the newly added future-enhancement notes
in `docs/development/PROJECT_Notes.md`. The current lines were compared with the
specific content flagged by the previous `git diff --check` run: wording and
ordering remain, with only the offending trailing spaces removed. A direct scan
found no remaining trailing whitespace in that file. Repository-wide
`git diff --check` now **PASSES** with exit 0 and no output.

Both authoritative guides remain present. The previously verified matching
dry-run/copy archive path, corrected uninstall code span, reciprocal links,
conditional release-download wording and Quick Start privacy warning remain.
Direct guide whitespace and fence checks pass. The public fixture/history check
passes (10 reviewed fixtures, clean public root, no oversized blobs). Checkpoint
JSON parses; the protected development CHANGELOG entry, root documentation,
package metadata, license, Stage specification and A JSON retain their recorded
SHA-256 digests. Git status and diff show no unexpected production, test,
fixture, package-metadata or CI change.

The previous full content validation remains applicable: no guide content or
behaviour-bearing file changed after that run. Its 330 passing tests, Ruff,
configured formatting, installed CLI and documentation claim/link checks are
retained without presenting them as newly rerun here. All applicable Checkpoint
B criteria **19–48 remain PASS**. Criteria **49–65 remain PENDING**. Only this
report and Checkpoint B JSON were changed by this revalidation. The expected
Stage 9.2b development CHANGELOG entry is preserved. No commit, push,
Checkpoint C or Stage 9.3b work occurred.

# Stage 9.3a COMPLETION REPORT — Checkpoint C technical audit

## Technical and formal status

**Checkpoint C: FAIL. Stage 9.3a closure readiness: FAIL. Formal COMPLETE: not
reached.** Criteria 1–55 and 57–61 pass; criterion 56 fails because the required
repository-wide Ruff run found `E501` in the pre-existing untracked
`tools/add_bug.py`. Criteria 62–65 remain PENDING formal gates. Checkpoint C,
Stage 9.3b and Stage 9.4 are not being advanced.

Checkpoint A remains complete and Checkpoint B remains PASS. Its original
editorial-quality FAIL, later repository-whitespace FAIL and final remediation
PASS remain recorded above and in the B JSON without revision.

## Public deliverables and integration

- `README.md` is now the concise public and package landing page. It explains
  why the Toolkit exists, archive reconstruction, dry-run/copy-first control,
  conversion as an additional capability, validated support boundaries, safety,
  privacy and links to both authoritative guides.
- `CHANGELOG.md` contains a short ordinary-user 1.1.0 Unreleased entry without a
  release date or development-stage chronology.
- `CONTRIBUTING.md` welcomes bug reports, enhancements and non-programmer
  contributions, including privacy-reviewed information from other Seestar
  models. Substantial code work is directed to an Issue first.
- GitHub Issue forms provide distinct Bug Report and Feature Request routes.
  Privacy guidance precedes requests for diagnostics or capture context. Blank
  issues are disabled; Discussions and Wiki were not enabled or introduced.
- `docs/development/BUGLIST.md` remains lightweight maintainer triage rather than
  a public tracker or permanent history. Its real volume path, target, capture
  timestamps and detailed filenames were replaced with neutral public-safe text.
- `docs/development/DEV_README.md` now says archive discovery is shallow, makes
  copy/collision behaviour explicit in archive examples and uses a neutral
  synthetic configuration location.

The User Guide and Quick Start were not edited during Checkpoint C. Their final
SHA-256 values remain `29cf55b4beb1f1a6ebcd37c946cdc74a4a8ef41c75dbcee62353c61131fc8883`
and `b3f61499335f7a7d15b1a323d3fa39056606b5a2d021a9cf9d82942c119ed18f`
respectively, matching the Checkpoint B PASS state.

## Support, privacy and defect review

All five public documents retain 1.1.0 Unreleased status and the validated
boundary: Seestar S50 data within the tested FIT/FITS scope; tested Siril RGB
conversion where stated; Apple-silicon macOS within the tested and
Apple-supported-at-release envelope; Python 3.11–3.14. Other Seestar models may
work but lack sufficient v1.1.0 validation; they are not described as known to
fail. No unsupported platform, capture mode, anonymisation, PyPI, telemetry or
future-feature claim was introduced.

Resolved documentation defects are the transitional public root files, missing
contribution/issue routes, three live DEV_README discrepancies, identifying
BUGLIST content, and README metadata compatibility. No potential product defect
was found. BUG-001 remains an unconfirmed maintainer triage item; Checkpoint C
does not investigate it or change archive behaviour.

## Validation and retained failures

- Full pytest: **PASS — 330 passed in 11.58s**, Python 3.13.15.
- Ruff: **FAIL — `tools/add_bug.py:140:101 E501`**, line length 101. The file was
  already untracked at Checkpoint C start and is user-owned BUGLIST tooling;
  changing it is outside this checkpoint's explicit scope.
- Configured formatting: **PASS — 37 files already formatted**.
- Public fixture/history: **PASS — 10 reviewed fixtures, clean public root, no
  oversized blobs**.
- Repository whitespace: **PASS — `git diff --check` exit 0**.
- Links/Markdown: **PASS** for local links, balanced fences, direct whitespace,
  reciprocal guide navigation and YAML parsing for all three issue files.
- Changed-file privacy: **PASS after BUGLIST remediation**; no private path,
  credential or former identifying capture marker remains in the public-facing
  changes.
- Distribution: initial run failed because the temporary environment lacked
  `build`; after installing the declared build extra, the first complete run
  exposed the README metadata-payload defect. The final rerun **PASSed**: wheel
  39 allowed members, sdist 46, metadata/license/entry point checks, isolated
  installs, both 1.1.0 entry points and runtime smoke conversion. Temporary
  artifacts were removed.

The Ruff failure prevents Checkpoint C and closure-readiness PASS even though
the documentation content and all other executed gates pass. No gate was
weakened, and neither failed distribution attempt is converted into a pass.

## Scope and preservation

The pending Stage 9.2b `docs/development/CHANGELOG.md` entry is byte-preserved.
No production source, test, FITS fixture, package metadata or CI file was changed
by Checkpoint C. The pre-existing untracked `tools/add_bug.py` remains untouched.
No PDF, timestamp synchronization, checksum manifest, release artifact, tag,
publication, commit or push was performed.

A first final direct whitespace scan found Markdown hard-break spaces on the
BUGLIST metadata fields. They were converted to an ordinary list and the direct
changed-document scan passes on rerun. The installed parser accepts the README
archive example, and both installed entry points report 1.1.0. This failure and
remediation are retained in the C JSON.

## Closure criteria 1–65

| # | Status | Evidence |
|---:|:---:|---|
| 1 | PASS | Preserved Checkpoint A |
| 2 | PASS | Preserved Checkpoint A |
| 3 | PASS | Preserved Checkpoint A |
| 4 | PASS | Preserved Checkpoint A |
| 5 | PASS | Preserved Checkpoint A |
| 6 | PASS | Preserved Checkpoint A |
| 7 | PASS | Preserved Checkpoint A |
| 8 | PASS | Preserved Checkpoint A |
| 9 | PASS | Preserved Checkpoint A |
| 10 | PASS | Preserved Checkpoint A |
| 11 | PASS | Preserved Checkpoint A |
| 12 | PASS | Preserved Checkpoint A |
| 13 | PASS | Preserved Checkpoint A |
| 14 | PASS | Preserved Checkpoint A |
| 15 | PASS | Preserved Checkpoint A |
| 16 | PASS | Preserved Checkpoint A |
| 17 | PASS | Preserved Checkpoint A |
| 18 | PASS | Preserved Checkpoint A |
| 19 | PASS | Explicit user instruction to perform B |
| 20 | PASS | User Guide/Quick Start and B validation |
| 21 | PASS | User Guide/Quick Start and B validation |
| 22 | PASS | User Guide/Quick Start and B validation |
| 23 | PASS | User Guide/Quick Start and B validation |
| 24 | PASS | User Guide/Quick Start and B validation |
| 25 | PASS | User Guide/Quick Start and B validation |
| 26 | PASS | User Guide/Quick Start and B validation |
| 27 | PASS | User Guide/Quick Start and B validation |
| 28 | PASS | User Guide/Quick Start and B validation |
| 29 | PASS | User Guide/Quick Start and B validation |
| 30 | PASS | User Guide/Quick Start and B validation |
| 31 | PASS | User Guide/Quick Start and B validation |
| 32 | PASS | User Guide/Quick Start and B validation |
| 33 | PASS | User Guide/Quick Start and B validation |
| 34 | PASS | User Guide/Quick Start and B validation |
| 35 | PASS | User Guide/Quick Start and B validation |
| 36 | PASS | User Guide/Quick Start and B validation |
| 37 | PASS | User Guide/Quick Start and B validation |
| 38 | PASS | User Guide/Quick Start and B validation |
| 39 | PASS | User Guide/Quick Start and B validation |
| 40 | PASS | User Guide/Quick Start and B validation |
| 41 | PASS | User Guide/Quick Start and B validation |
| 42 | PASS | User Guide/Quick Start and B validation |
| 43 | PASS | User Guide/Quick Start and B validation |
| 44 | PASS | User Guide/Quick Start and B validation |
| 45 | PASS | User Guide/Quick Start and B validation |
| 46 | PASS | User Guide/Quick Start and B validation |
| 47 | PASS | User Guide/Quick Start and B validation |
| 48 | PASS | User Guide/Quick Start and B validation |
| 49 | PASS | User explicitly authorised Checkpoint C in this invocation. |
| 50 | PASS | README.md is a concise archive-first landing page linked to both guides. |
| 51 | PASS | CONTRIBUTING.md covers non-code contributions, reports, scoped PRs, checks and privacy-first capture handling. |
| 52 | PASS | CHANGELOG.md contains concise user-facing 1.1.0 Unreleased content with no date or Stage history. |
| 53 | PASS | PACKAGING.md and PROJECT_Notes.md record Checkpoint C status and validation accurately. |
| 54 | PASS | Local link, Markdown fence, command, issue-form and five-document consistency checks passed. |
| 55 | PASS | Public input/history check passed; public-facing changed files were privacy scanned; BUGLIST identifying material was sanitised. |
| 56 | FAIL | pytest 330 passed; formatting and git diff --check passed; Ruff failed on tools/add_bug.py:140 E501 (101 > 100). |
| 57 | PASS | validate_distribution.py passed after retained initial dependency and README metadata-payload failures and remediation. |
| 58 | PASS | A/B failure history and all C failures/remediation are retained without relabelling. |
| 59 | PASS | All 65 criteria are individually assessed here with PASS, FAIL or PENDING. |
| 60 | PASS | No production, test or fixture change was made; package metadata and CI are unchanged. |
| 61 | PASS | No PDF, timestamp sync, checksum manifest, release artifact or later-stage work was performed. |
| 62 | PENDING | Independent ChatGPT review has not yet accepted technical completion. |
| 63 | PENDING | User closure approval/commit has not occurred; Codex did not commit or push. |
| 64 | PENDING | No Stage 9.3a commit exists, so post-commit content, cleanliness and CI cannot be verified. |
| 65 | PENDING | Formal COMPLETE is prohibited while criterion 56 fails and criteria 62-64 remain pending. |

Criteria 62–65 are formal gates, not technical documentation claims. Formal
Stage 9.3a completion remains prohibited until criterion 56 passes and those
pending gates complete. The next technical action is resolution of the out-of-scope
Ruff error followed by a clean affected-gate rerun.

## Checkpoint C — private maintainer-file scope cleanup

After the first Checkpoint C FAIL, the maintainer decided that `BUGLIST.md` and
`tools/add_bug.py` are private personal files outside the Seestar Toolkit
repository and outside its public documentation, release, support and utility
scopes. Both were absent from the repository when this cleanup began. Their new
private filesystem location and private contents are deliberately not recorded.

The first audit remains genuine historical evidence: both files were present in
the working tree, Ruff failed on the then-untracked tool's E501 violation, and
the development list was reviewed and sanitised. Those facts are retained above
and in the Checkpoint C JSON. They do not make either file a current repository
requirement.

Live references were removed from CONTRIBUTING, PACKAGING and PROJECT_Notes.
The Bug Report and Feature Request forms, generic GitHub Issues route, submission
privacy guidance and representative other-model capture guidance remain intact.
No User Guide or Quick Start change was made. This was scope cleanup only;
Checkpoint C revalidation was explicitly not performed. No commit, push or
later-stage work occurred.

## Checkpoint C — final remediation revalidation

**Checkpoint C: PASS. Stage 9.3a technical/documentation closure readiness:
PASS. Stage status: STARTED; formal COMPLETE remains pending.** This is a new
validation attempt after the genuine original Checkpoint C FAIL and accepted
scope cleanup. Nothing above is rewritten or relabelled.

Neither private filename exists anywhere in the repository. The private-scope
decision was not revisited, and no private location was located or inspected.
The three GitHub Issue-template files remain intentional public deliverables.
The User Guide and Quick Start remain byte-identical to Checkpoint B PASS at
SHA-256 `29cf55b4beb1f1a6ebcd37c946cdc74a4a8ef41c75dbcee62353c61131fc8883`
and `b3f61499335f7a7d15b1a323d3fa39056606b5a2d021a9cf9d82942c119ed18f`.

Fresh final results:

- pytest: **PASS — 330 passed in 11.75s**, Python 3.13.15;
- Ruff: **PASS — All checks passed!**;
- configured formatting: **PASS — 37 files already formatted**;
- repository `git diff --check`: **PASS**, exit 0 with no output;
- direct changed-document whitespace: **PASS**;
- public fixture/history/privacy: **PASS — 10 reviewed fixtures, clean public
  root, no oversized blobs**;
- Markdown structure, fences, navigation, local links and anchors: **PASS**;
- GitHub Issue-form YAML: **PASS** for Bug Report, Feature Request and config;
- README/CHANGELOG/CONTRIBUTING policy and support-boundary assertions: **PASS**;
- README archive example parser check: **PASS**;
- installed console and module entry points: **PASS**, both version outputs are
  `seestar-toolkit 1.1.0`, and both help routes succeed;
- distribution validation: **PASS** — wheel 39 allowed members, sdist 46,
  metadata/license/entry points, isolated installs and runtime smoke checks;
  temporary outputs removed.

Criterion 56 therefore has two distinct results: **original Checkpoint C FAIL**
from the recorded E501 finding, and **final remediation revalidation PASS** from
the clean repository-wide Ruff result plus the other quality gates. No Ruff
configuration or exclusion changed.

The public README remains a concise archive-first front door; conversion remains
an additional capability. The public CHANGELOG is concise and v1.1.0 remains
Unreleased. CONTRIBUTING and the Issue forms retain non-programmer participation,
prior discussion for substantial code work, other-model capture context and
privacy-first sharing guidance. Support claims remain bounded to established
S50, Apple-silicon macOS, Python 3.11–3.14 and validated input evidence. No
screenshots, anonymisation claim or future behaviour promise was introduced.

No new documentation or product defect was found. No production, test, fixture,
package-metadata or CI change was made. No PDF, checksum manifest, later-stage
work, commit or push occurred.

### Final criteria 1–65 accounting

| # | Status | Evidence |
|---:|:---:|---|
| 1 | PASS | Preserved Checkpoint A |
| 2 | PASS | Preserved Checkpoint A |
| 3 | PASS | Preserved Checkpoint A |
| 4 | PASS | Preserved Checkpoint A |
| 5 | PASS | Preserved Checkpoint A |
| 6 | PASS | Preserved Checkpoint A |
| 7 | PASS | Preserved Checkpoint A |
| 8 | PASS | Preserved Checkpoint A |
| 9 | PASS | Preserved Checkpoint A |
| 10 | PASS | Preserved Checkpoint A |
| 11 | PASS | Preserved Checkpoint A |
| 12 | PASS | Preserved Checkpoint A |
| 13 | PASS | Preserved Checkpoint A |
| 14 | PASS | Preserved Checkpoint A |
| 15 | PASS | Preserved Checkpoint A |
| 16 | PASS | Preserved Checkpoint A |
| 17 | PASS | Preserved Checkpoint A |
| 18 | PASS | Preserved Checkpoint A |
| 19 | PASS | Explicit user instruction to perform B |
| 20 | PASS | User Guide/Quick Start and B validation |
| 21 | PASS | User Guide/Quick Start and B validation |
| 22 | PASS | User Guide/Quick Start and B validation |
| 23 | PASS | User Guide/Quick Start and B validation |
| 24 | PASS | User Guide/Quick Start and B validation |
| 25 | PASS | User Guide/Quick Start and B validation |
| 26 | PASS | User Guide/Quick Start and B validation |
| 27 | PASS | User Guide/Quick Start and B validation |
| 28 | PASS | User Guide/Quick Start and B validation |
| 29 | PASS | User Guide/Quick Start and B validation |
| 30 | PASS | User Guide/Quick Start and B validation |
| 31 | PASS | User Guide/Quick Start and B validation |
| 32 | PASS | User Guide/Quick Start and B validation |
| 33 | PASS | User Guide/Quick Start and B validation |
| 34 | PASS | User Guide/Quick Start and B validation |
| 35 | PASS | User Guide/Quick Start and B validation |
| 36 | PASS | User Guide/Quick Start and B validation |
| 37 | PASS | User Guide/Quick Start and B validation |
| 38 | PASS | User Guide/Quick Start and B validation |
| 39 | PASS | User Guide/Quick Start and B validation |
| 40 | PASS | User Guide/Quick Start and B validation |
| 41 | PASS | User Guide/Quick Start and B validation |
| 42 | PASS | User Guide/Quick Start and B validation |
| 43 | PASS | User Guide/Quick Start and B validation |
| 44 | PASS | User Guide/Quick Start and B validation |
| 45 | PASS | User Guide/Quick Start and B validation |
| 46 | PASS | User Guide/Quick Start and B validation |
| 47 | PASS | User Guide/Quick Start and B validation |
| 48 | PASS | User Guide/Quick Start and B validation |
| 49 | PASS | User explicitly authorised Checkpoint C in this invocation. |
| 50 | PASS | README.md is a concise archive-first landing page linked to both guides. |
| 51 | PASS | CONTRIBUTING.md covers non-code contributions, reports, scoped PRs, checks and privacy-first capture handling. |
| 52 | PASS | CHANGELOG.md contains concise user-facing 1.1.0 Unreleased content with no date or Stage history. |
| 53 | PASS | PACKAGING.md and PROJECT_Notes.md record Checkpoint C status and validation accurately. |
| 54 | PASS | Local link, Markdown fence, command, issue-form and five-document consistency checks passed. |
| 55 | PASS | Public input/history check passed; public-facing changed files were privacy scanned; BUGLIST identifying material was sanitised. |
| 56 | PASS | Final remediation revalidation: pytest 330 passed; Ruff all checks passed; 37 files formatted; git diff --check and direct changed-document whitespace passed. |
| 57 | PASS | validate_distribution.py passed after retained initial dependency and README metadata-payload failures and remediation. |
| 58 | PASS | All A/B/C failures, remediations, private-scope cleanup and final revalidation are retained chronologically. |
| 59 | PASS | All 65 criteria are individually assessed here with PASS, FAIL or PENDING. |
| 60 | PASS | No production, test or fixture change was made; package metadata and CI are unchanged. |
| 61 | PASS | No PDF, timestamp sync, checksum manifest, release artifact or later-stage work was performed. |
| 62 | PENDING | Independent review of final technical completion has not yet occurred; accepted private-scope cleanup is narrower. |
| 63 | PENDING | User closure approval and commit have not occurred; Codex did not commit or push. |
| 64 | PENDING | No Stage 9.3a closure commit exists; exact-commit content, cleanliness and required CI remain unverified. |
| 65 | PENDING | Technical/documentation closure readiness passes, but formal COMPLETE awaits criteria 62-64. |

Criteria 1–61 now PASS. Criteria 62–65 remain PENDING formal gates:
independent final technical review; user approval and closure commit; post-commit
content, cleanliness and required CI verification; then formal COMPLETE.
