# Stage 9.1a — Release Requirements, Compatibility and Packaging Audit

Date: 2026-09-10. Target: v1.1.0. **Recommendation: FAIL — criterion 60 is unverified.**

**STAGE START — Stage 9.1a**

## 1. Executive result and evidence distinctions

The audit outputs are complete, but the stage cannot pass while GitHub repository privacy is unverified. This checkout has no remote; `gh repo view --json visibility,isPrivate,nameWithOwner` exits 4 requesting authentication. Neither a missing remote nor missing credentials proves a GitHub repository is private. Repository identity/visibility evidence was requested from the user. No visibility change, upload, tag, commit or publication was attempted. Criterion 60 is FAIL (not established), not a finding that the repository is public. All other criteria pass as audit requirements; downstream implementation findings do not themselves fail an audit that is required to identify them. Stage 9.1b must not begin on this recommendation.

Evidence labels used throughout:

- **Observed:** inspected current source, tracked files, metadata or local commands; does not prove a clean installation.
- **Stage 8 evidence:** the committed final 8.2g regression and 8.3a closure; no new ground-truth investigation.
- **Candidate:** a proposed test target, not official Python/macOS support.
- **Policy:** fixed future release requirements from the authoritative specification, not implemented or published yet.
- **Action:** downstream work with an explicit owner.

## 2. Baseline, bootstrap and scope

Observed HEAD: `995c988cd7effa405ba1495445d877a548b2b9e3`.
`git log -1 --oneline`: `995c988 Stage 8.3a: validate and close Stage 8`.
Initial status: modified `docs/CHANGELOG.md`, modified `docs/PROJECT_Notes.md`, untracked `docs/devlopment/`.
The first two are expected: pending 8.3a detailed history and the Stage 9 roadmap wording change. They are preserved unchanged.

Bootstrap discrepancy: the supplied specification existed only at `docs/devlopment/change_documents/STAGE_9/STAGE_9.1a.md` (misspelled directory). Section 3 explicitly authorizes creation of the correct authoritative path. Its bytes were copied unchanged to `docs/development/change_documents/STAGE_9/STAGE_9.1a.md`; the original is retained. This is the sole layout bootstrap exception, not a wider migration. The audit report is the other newly created repository file. The duplicate path needs a deliberate disposition during 9.1b, not silent deletion here.

No production/test/packaging configuration was changed. No CI, guide, PDF, distribution, release ZIP or private runbook was created. No global/system Python environment was changed. External Stage 8 datasets were not inspected or copied. Tracked fixtures were inspected read-only with metadata values withheld.

## 3. Current packaging/build audit

Observed `pyproject.toml`:

| Area | Current state | Action |
|---|---|---|
| Backend | `setuptools.build_meta`, build requirements `setuptools>=68`, `wheel` | 9.1c: retain backend; align minimum with metadata features |
| Project | `seestar-toolkit`, version 1.1.0, MIT, author Mark Wymer | Preserve identity; update description to include archive and float32 functionality |
| Licence | SPDX-style `license="MIT"`, `license-files=["LICENSE"]`; root licence has required copyright | Minimum setuptools 68 does not guarantee support for this metadata form; choose justified PEP 639-capable minimum |
| Python | `requires-python=">=3.11"`, classifiers 3.11/3.12/3.13 | Candidate declarations only pending 9.2a |
| Platform/maturity | `Operating System :: OS Independent`, `Development Status :: 3 - Alpha` | 9.1c: align with fixed macOS arm64 release scope; no alpha version identifier |
| Discovery | `src` layout, package-dir mapping and find under src | Good isolation; validate exact included packages in 9.1d |
| Entry point | `seestar-toolkit = seestar_toolkit.cli:main`; `__main__.py` delegates to same main | Preserve and prove both installed interfaces |
| Extras | `dev` combines pytest, pytest-cov, Ruff; runtime dependencies separate | Keep runtime free of build/docs/release tools |
| Contents | No explicit release allowlist, MANIFEST.in, release script or CI workflow located | 9.1c/d: deliberate wheel/sdist contents and clean build checks |
| URLs | No project homepage/issues/source/documentation URLs declared; no remote | Supply verified destinations after repository identity is established |
| Build environment | Existing environment has no installed setuptools, wheel or build distribution | Not a runtime failure; isolated build tools must be declared/provisioned later |

No build was run. The src layout is a sound starting point but distribution safety is unproven: setuptools defaults can include unwanted tests/docs, and Git ignore rules are not distribution policy. 9.1d should use isolated `python -m build`, `twine check` (validation only; never upload), archive-member/metadata inspection and build a wheel from the extracted sdist without a Git checkout. Confirm licence and no missing runtime files. See [setuptools licence migration](https://github.com/pypa/setuptools/blob/main/docs/userguide/license_migration.rst): PEP 639 support begins at v77. Choose a tested compatible floor (e.g. 77.0.3), not the developer's arbitrary installed tool version.

## 4. Version-source inventory and recommendation

Observed current live sites:

| Site | Role |
|---|---|
| `pyproject.toml:7` | Static project.version 1.1.0; build metadata and filenames derive here |
| `src/seestar_toolkit/__init__.py:6` | Reads installed distribution metadata through importlib.metadata |
| Same file, line 8 | Duplicate fallback literal 1.1.0 when distribution is absent; drift risk |
| `src/seestar_toolkit/cli.py:11,45` | Imports __version__; argparse --version displays it |
| `src/seestar_toolkit/__main__.py` | Delegates module execution to the same CLI (no independent version) |
| `tests/unit/test_cli.py:17` | Hardcoded equality to 1.1.0 |
| Same test, line 305 | Checks CLI output against __version__ |
| `tests/unit/test_package.py:5` | Tests version existence, not metadata equality |
| `tests/integration/test_stage6_workflows.py:14,219` | Version output uses __version__; source-tree/development environment coverage |
| `README.md:8`, `CHANGELOG.md:5` | Public/developer version wording and Unreleased header |
| `docs/PROJECT_Notes.md:11` | Development version wording |
| `<private development-environment notes>:40,73,83` | Version-bearing development examples |
| `docs/change_documents/STAGE_6/STAGE_6.1h.md:605` | Historical version evidence |
| Stage 9.1a specification | Fixed release version, artifact names and future tag; policy, not additional runtime authority |

Recommendation for 9.1c: keep static `project.version` in pyproject.toml as the single authoritative source. Installed package/CLI use importlib.metadata. Remove the independently maintained source fallback literal; choose a clear uninstalled-checkout policy or generate an appropriate source fallback from the authoritative value without runtime dependence on a repository pyproject file. Tests compare built/installed metadata and entry-point output with project.version; historical stage transcripts are not live version sources.

Build tooling reads project.version with stdlib tomllib. Wheel/sdist filenames derive from metadata; docs version injection, ZIP name, tag validation and public information are generated or validated against the same value. Document headers have no separately maintained version. Repository Markdown placeholders/metadata are resolved from that value; any displayed literal is checked. v1.1.0 has no dev/alpha/beta/rc identifier. Public root CHANGELOG remains Unreleased until actual GitHub publication. Future assembly is a candidate artifact of version 1.1.0, not a pre-release version.

## 5. Dependency classification and constraints

Local installed metadata is evidence of this environment only:

| Class | Declared / observed | Python or dependency implications |
|---|---|---|
| Runtime | astropy>=7.0; installed 8.0.1 | Installed Requires-Python >=3.11; numpy>=2.0, packaging>=25, pyerfa>=2.0.1.3, PyYAML>=6 and astropy-iers-data transitive |
| Runtime | numpy>=2.0; installed 2.5.1 | Installed Requires-Python >=3.12; older compatible resolution needed for 3.11 |
| Runtime | opencv-python-headless>=4.10; installed 5.0.0.93 | Installed Requires-Python >=3.6; numpy>=2 on Python>=3.9; binary architecture/ABI availability still needs proof |
| Runtime | tifffile>=2025.1.10; installed 2026.7.14 | Installed Requires-Python >=3.12 and numpy>=2.1; investigate older releases for 3.11 |
| Test | pytest>=8, pytest-cov>=6 via dev extra | Installed 9.1.1 / 7.1.0; Python floors >=3.10 / >=3.9 |
| Lint/quality | ruff>=0.9 via dev | Installed 0.16.0; formatting/lint configuration in pyproject |
| Build | setuptools>=68, wheel in build-system | Backend minimum needs correction; build frontend not declared as runtime |
| Documentation/PDF | None currently | Proposed Pandoc, explicit XeLaTeX engine/fonts, repository wrapper; development/release-only |
| Release-only | None configured | build, twine check, Git/GitHub CLI, stdlib ZIP/hash/provenance tooling; no PyPI upload |

AST import inventory across production source found stdlib plus astropy, numpy, cv2 and tifffile; no undeclared direct third-party runtime import was found. tomllib is used directly and provides a concrete Python 3.11 floor. Existing pytest integration tests often run with source-root/PYTHONPATH context; they are not clean-install proof. No runtime use of pytest/Ruff/build/Pandoc was found. tifffile optional codecs/plotting and Astropy all/docs/test extras are not required by the actual local FITS/uncompressed TIFF path; do not install them indiscriminately. No current exact runtime pins or known justified runtime upper caps were identified.

Policy: use documented minimum constraints justified by APIs and actual tested resolutions. Do not freeze the development Mac's packages into runtime requirements. Record resolved versions separately for reproducible validation. Add upper caps or exclusions only for demonstrated incompatibilities with a regression reference; none recommended without such evidence now. 9.1c chooses candidate-compatible packaging constraints; 9.2a proves them. `pip check` on the existing environment passes but does not prove the whole declared dependency range.

## 6. Candidate Python matrix — NOT official support

| Candidate | Why test | Known constraint / required proof |
|---|---|---|
| Homebrew CPython 3.13 | Current 3.13.15 development baseline passes 314 tests | Still requires clean wheel/sdist and installed runtime proof |
| Homebrew CPython 3.12 | Meets installed NumPy/tifffile Python floors | Resolve arm64 wheels, clean installation and all required runtime cases |
| Homebrew CPython 3.14 | Available Homebrew stable formula; useful current-generation candidate | Verify native dependency wheels/ABI and runtime, no assumption from metadata alone |
| Homebrew CPython 3.11 | Existing declared floor and tomllib floor | Current installed NumPy/tifffile versions cannot run on it; determine whether allowed older releases resolve and pass |

All four are test candidates, none declared supported here. <3.11 is not a candidate under current source/dependency design. Future/prerelease interpreters and alternate/free-threaded builds are outside this initial candidate matrix unless separately added.
[Homebrew 3.11](https://formulae.brew.sh/formula/python@3.11), [3.12](https://formulae.brew.sh/formula/python@3.12), [3.13](https://formulae.brew.sh/formula/python@3.13), [3.14](https://formulae.brew.sh/formula/python@3.14) were inspected on the audit date; formula availability is not Toolkit compatibility evidence.

Sequence is mandatory: 9.1a candidates → 9.1c testable packaging using standard Requires-Python/PEP 440 declarations → 9.2a clean wheel AND sdist installation and runtime proof → final supported-Python declaration. Run from outside the checkout without PYTHONPATH/editable/dev dependencies; inspect import paths and console locations, pip check, both entry points and runtime cases. Preserve every candidate failure. A direct metadata correction justified by 9.2a is permitted only within its specification, then rebuild/reinstall/revalidate affected artifacts before closing 9.2a. Classifiers and user support tables must not advertise candidates prematurely. An open-ended >= floor is not proof for every future Python version; document the tested set precisely.

## 7. macOS/architecture and storage test envelope

Observed host: macOS 26.5.2, build 25F84, arm64. This is a development-host observation, not final OS certification. Production code uses pathlib and standard filesystem APIs, with no machine/OS rejection check. A platform-neutral Python wheel may install elsewhere; that does not expand the fixed support policy. Native NumPy/OpenCV/Astropy dependencies determine ABI, deployment-target and architecture feasibility.

Policy: v1.1.0 supports only tested macOS on Apple Silicon. Intel/Rosetta, Linux and Windows are untested/unsupported, even if they work. Replace the existing OS Independent support claim in 9.1c; do not forge macOS wheel tags for a pure-Python package merely to express policy.

Candidate macOS families: Tahoe 26, Sequoia 15 and Sonoma 14, only if Apple still supports them at actual release time. Recheck [Apple security releases](https://support.apple.com/en-us/100100) then; no fixed “latest three” guarantee or exact supported OS envelope is asserted now. Obtain real arm64 hosts/appropriate VMs/runners, record hardware, OS build and native interpreter architecture, and test oldest/newest intended supported OS combinations with each claimed Python. 9.2a proves installation; 9.2b proves runtime/storage. If access is unavailable, do not claim the corresponding OS.

Test internal storage, removable/external media and mounted NAS paths where practical, including spaces/Unicode, permissions, read-only mounts, insufficient space, collisions, interruptions, symlinks and same-volume temporary-file/atomic-replace/fsync semantics. Toolkit uses user-selected filesystem paths; availability and filesystem guarantees matter. Do not invent exact macOS permission prompts or instruct blanket Full Disk Access. Record observed Terminal/host application permission behaviour. Do not modify Apple-managed Python, shell profiles, PATH or system symlinks. Primary venv is ~/.venvs/seestar-toolkit; document activation/deactivation and full-path invocation. No installer shell script.

## 8. CLI/configuration/diagnostic inventory

Both entry points delegate to cli.main; existing environment --version returns `seestar-toolkit 1.1.0` for both. This is development-install inspection, not 9.2 proof.

| Surface | Current arguments and behaviour |
|---|---|
| Global | `-h/--help`, `--version`, `--verbose`; verbosity is global, document it before the subcommand; no command prints help |
| convert | `INPUT_FITS OUTPUT_TIFF`; explicit destination, no overwrite; linear RGB TIFF |
| convert-batch | `INPUT_DIR OUTPUT_DIR`; flat, non-recursive, case-insensitive FIT/FITS extension scan, sorted filenames; output directory can be created if parent exists; per-file continuation and totals |
| archive | `SOURCE_ROOT ARCHIVE_ROOT`; archive root absolute; discovery at root/direct child level, not arbitrary recursive capture discovery |
| archive options | `--dry-run`, `--location`, `--hierarchy`, `--source-action {copy,move}`, `--collision-policy {skip-identical,error,overwrite}`, `--non-interactive`, `--config PATH`, `-h/--help` |
| Defaults | copy; skip-identical; hierarchy `{target}/{location}/{session_end_date}` |
| Configuration | `~/.config/seestar-toolkit/config.toml`; explicit --config replaces default lookup; missing default uses defaults, missing explicit config errors; unknown keys ignored |
| TOML | `[archive]` hierarchy/source_action/collision_policy; `[[locations]]` name/latitude/longitude/radius_m |
| Precedence | CLI over TOML over defaults; explicit location over nearest saved GPS match; interactive confirmation/manual location on TTY unless non-interactive; fallback unknown |

No `config`, `diagnostics`, update or self-install subcommand exists. Config loader is read-only and does not persist manual choices. +12-hour archive date, observation numbering and target/light/stack/tiff directory structure remain Stage 8 contracts. Archive COPY/MOVE, collision handling, indexes and TIFF outputs are supported existing operations, but were not executed on external data during this audit. Dry-run does not write outputs.

| Outcome | Current exit/status presentation |
|---|---|
| Help/version/no command | 0; help or version on stdout |
| Parser misuse/invalid option choice | 2; argparse usage/error |
| Conversion success | 0; Created TIFF on stdout |
| Expected conversion failure | 1; Error on stderr; unsupported input/output/overwrite issues |
| Batch all succeed with nonzero inputs | 0; created paths and discovered/converted/failed totals |
| Batch partial failure, empty input, invalid directory | 1; failures/no-input diagnostic; expected per-file failures do not stop subsequent files |
| Archive COMPLETE, including legitimate empty no-op | 0; summary and outputs |
| Archive partial/failed operation, config/planning error | 1; original/TIFF/index errors and relevant summaries |
| Dry-run | 0 if no operational problems, else 1; plans, discovery/planning problems and planned indexes |

No blanket promise that arbitrary unexpected exceptions are converted to these friendly messages. Current dry-run presentation does not explicitly print every observation metadata diagnostic; full API diagnostics are richer. 9.2b/9.3a must verify what users actually see rather than promise exhaustive diagnostic display.

Documentation discrepancies: README says archive is recursive although discovery is shallow; description omits archive and float32 output; root CHANGELOG still calls convert a placeholder; README has development installation only; verbose option absent from examples. Map wording fixes to 9.1b structural handoff and 9.3a definitive public text, metadata wording to 9.1c. Tests/unit and integration CLI files remain the command acceptance evidence.

## 9. Supported-input/capture evidence matrix

Status below is a functionality/evidence boundary, not Python/platform certification.

| Category | Automated / fixture evidence | Stage 8 real evidence | Permitted wording and limits |
|---|---|---|---|
| S50 raw Bayer uint16 FIT/FITS | fits reader/inspector, demosaic, raw conversion and Seestar integration tests | D01–D09 light membership | Supported tested S50 raw inputs; known Bayer pattern required; no claim for all files |
| Bayer patterns | Unit coverage GRBG/RGGB/GBRG/BGGR | GRBG observed | Algorithm supports four patterns; real device validation is GRBG |
| Native S50 RGB stacks uint16 | RGB contract, Seestar conversion, stacked fixtures | All 11 stacks classified RGB_IMAGE despite GRBG keyword | Preserve RGB, no redemosaicing; output linear uint16 |
| Siril RGB float32 standard/mosaic | Two tracked reference fixtures; RGB/Siril integration and float TIFF tests | Not a separate Stage 8 corpus category | Supported tested finite float32 channels-first RGB conversion; not generic Siril project ingestion/archive reconstruction |
| S50 AltAz / EQ | Reconstruction compatibility tests, eq fixture | D01–D05 / D06–D09 | Qualified modes in frozen corpus |
| Firmware 7.75 / 8.46 / 9.31 | Model/metadata parsing, fixture tests | D06/D07; D01–D03; D04/D05/D08/D09 | State validated firmware examples, not universal firmware support |
| Structural mosaic directories | Discovery/planning generated regressions, mosaic fixtures | D02/D05/D07/D09 | Comparison-only naming support; no typed mosaic state or WCS inference |
| Same-target sessions, equal time, large gap, midnight | Reconstruction ordering/boundary tests | D08 12/1/135; D02/D05/D09 equal time | Frozen grouping and +12-hour policy; no arbitrary session inference |
| Unknown target | Discovery/planning tests | D02 | Legitimate Unknown retained; no target override |
| STACKCNT divergence | Count greater/less/missing and contradictory metadata tests | D08 Session 03: 135 retained versus 106 integrated, 3180/30 | Membership independent of STACKCNT |
| JPEG/thumbnail | Discovery classifications and ignore policy tests | Ancillary corpus items excluded | Recognized ancillary files, not JPEG conversion/archive processing |
| Malformed/unsupported FITS | Exceptions, reader/classifier and CLI tests | No universal malformed real corpus qualification | Unsupported layouts/dtypes/nonfinite output fail visibly; no stretch, colour correction or automatic orientation claim |
| S50 Pro, S30, S30 Pro | No representative proof identified | None | No support claim; future separate representative validation |
| DSLR/conventional camera | No ingestion/archive implementation | None | Explicitly excluded from v1.1.0 |
| Solar/Lunar/Planetary MP4 | No video pipeline | None | Future work: extraction, timing metadata and output formats require separate implementation/validation |

Stage 8.2g is the authoritative final corpus evidence: 9 datasets, 11 COMPLETE observations, 11 plans, 1,020 files preserved. F8-01/F8-02/F8-03/F8-03A/F8-04 are resolved; failed 8.2e remains failed. Generic FITS reading is not a support claim for every camera/capture type. uint16 Seestar and finite float32 Siril RGB outputs are covered; no image stretching or clipping added.

## 10. Documentation inventory and complete migration map

9.1b owns moves and reference repair; 9.3a owns finished public writing. Existing root CHANGELOG already exists and is Unreleased; do not overwrite it blindly or invent a second public history. No CHANGELOG_root.md exists on disk despite the IDE tab label.

| Current | Planned destination / disposition |
|---|---|
| README.md | Preserve current developer-oriented content at docs/development/DEV_README.md; establish root user-facing entry boundary in 9.1b, finish concise user text in 9.3a |
| CHANGELOG.md | Retain public root history, refresh truthful concise Unreleased v1.1.0 contents in 9.3a |
| docs/CHANGELOG.md | docs/development/CHANGELOG.md, retain detailed pending-entry workflow |
| docs/ARCHITECTURE.md | docs/development/ARCHITECTURE.md |
| docs/PROJECT_Notes.md | docs/development/PROJECT_Notes.md; sole future-enhancement authority |
| <private development-environment notes>, <private development-environment notes> | Same basenames under docs/development; repair relative references |
| docs/SEESTAR_FITS_REFERENCE.md | docs/development/SEESTAR_FITS_REFERENCE.md; privacy-review before public visibility |
| docs/change_documents/** (Stages 2–8 and TOOLS) | docs/development/change_documents/**, preserve stage history/outcomes |
| docs/devlopment/change_documents/STAGE_9/STAGE_9.1a.md | Duplicate typo path; compare with bootstrapped authoritative file and resolve deliberately in 9.1b |
| docs/development/change_documents/STAGE_9/** | Already correct bootstrap location; preserve |
| absent REAL_DATA_TESTING.md | Create docs/development/REAL_DATA_TESTING.md in 9.1b |
| absent user documentation | Reserve docs/user/ in layout; 9.3a writes SEESTAR_TOOLKIT_QUICK_START.md and SEESTAR_TOOLKIT_USER_GUIDE.md; 9.3b adds matching .pdf and .sha256 files |
| AGENTS.md | Keep root; update references to relocated development documents during authorized 9.1b |
| tests/data/README.md | Keep with safe fixture inventory; update real/synthetic/anonymized provenance and exclusions |
| LICENSE | Keep root unchanged |
| absent CONTRIBUTING.md / .github issue templates | 9.3a creates public-safe contribution, bug and feature instructions |

No ROADMAP.md or RELEASE_NOTES.md is to be created. 9.4a release notes mean GitHub Release text and concise root CHANGELOG content, not an extra file. Root README version/build readme reference in pyproject must still resolve after the handoff. Preserve old stage requirements/results as historical evidence while repairing navigation; private literals in historical reports need explicit privacy treatment, not accidental retention in public history.

Reference search covered tracked Markdown/Python/TOML, old docs paths, README/CHANGELOG links, version/config references, CLI examples and local paths. Exact file inventory is in Appendix A. High-impact sites: AGENTS.md (PROJECT_Notes/ARCHITECTURE/CHANGELOG and pending workflow), pyproject readme, developer venv documents, PROJECT_Notes links to stage records, ARCHITECTURE development references, Stage 2–8 documents including absolute historical local paths, tests/data README, and CLI config examples. Rerun link/reference validation after migration; do not replace real runtime config paths with development-document paths. Preserve frozen evidence values with a public-safe presentation/provenance policy.

Future enhancement inventory: PROJECT_Notes already mentions GUI, macOS bundle, Windows executable, Linux package, DSLR future work and observed MP4 source types. It lacks explicit actionable entries for S50 Pro, S30, S30 Pro validation; full Solar/Lunar/Planetary MP4 extraction/timing/output roadmap; privacy-conscious diagnostics command; possible PyPI; GitHub Discussions; and a clearly scoped easier native installer. 9.1b preserves existing notes and adds missing named future items; 9.3a documents current limits. Observation of MP4 files is not implementation. No future item is implemented here.

## 11. Fixtures, private data and public history

Observed 10 tracked FIT/FITS files total **390,430,080 bytes**. All ten have non-empty SITELAT/SITELONG and device-related header keys; two Siril files also have HISTORY. Values are deliberately not reproduced. They are not cleared as anonymized or public-safe merely because tests track them. The tests/data README's “small” fixture description is inaccurate for the 272,923,200-byte mosaic reference.

| Tracked file/group | Bytes / assessment |
|---|---|
| tests/data/seestar/{eq,light,mosaic,mosaic_1,mosaic_4,mosaic_6}.fit | 4,152,960 each; real capture/location/device metadata review required |
| tests/data/seestar/stacked.fit | 49,775,040; same privacy assessment |
| tests/data/seestar/stacked_mosaic.fit | 17,925,120; same privacy assessment |
| tests/data/reference/siril_stacked.fit | 24,888,960; location/device/history review required |
| tests/data/reference/siril_stacked_mosaic.fit | 272,923,200; privacy and large-blob publication/storage risk |
| Generated arrays/FITS in unit/integration tmp_path tests | Appropriate public strategy after literal metadata/path review; retain behaviour assertions |

No tracked fixture was changed. Before publication, sanitize/anonymize or replace fixtures only under a separately scoped, approved downstream task with regression equivalence and provenance/redistribution approval. Do not erase real-data evidence or weaken tests. 9.1b owns fixture/privacy strategy; if actual fixture changes exceed its approved scope, open an explicit follow-up; 9.1d validates the public fixture suite; 9.4a gates all reachable Git history. Removing a file from HEAD does not remove sensitive data/large blobs from history. History rewriting, if required, is a separate deliberate approval, never an audit action.

Current .gitignore globally ignores *.fit/*.fits (and tif/tiff) with exceptions for two test directories. This contradicts the desired general safe-fixture policy and leaves future fixture locations easy to miss. 9.1b should replace blanket FIT/FITS patterns with scoped private/output rules, preserving safe tracked fixtures. `.DS_Store/` targets directories rather than the normal file; correct deliberately in the same ignore-policy task.

Proposed private test location: `<private-work-root>/seestar-toolkit-real-data/` outside every repository, not automatically cloud-synced or exposed to CI. If an in-repository convenience location is needed, use one narrowly ignored `.private-real-data/` path and verify `git check-ignore` plus tracked-file checks; outside-repository storage is preferred. Never relocate/copy the frozen Stage 8 corpus automatically. REAL_DATA_TESTING.md must use placeholders and opt-in external paths; public tests must not require personal captures. Audit documentation itself and earlier reports for personal absolute paths, coordinates, serial identifiers, attachments and Git history; no sensitive header values in public reports.

## 12. Privacy/network/storage findings

Observed production imports and call paths show no application HTTP client, telemetry SDK, analytics, update checker, geocoder or metadata upload. FITS reads use local Path objects through astropy.io.fits; OpenCV is used for cvtColor and tifffile for local output. Astropy as a dependency has network-capable features (for example remote data support), but those capabilities are not evidence that this Toolkit invokes them. No coordinate/time-service path was found. Build/install/Homebrew/GitHub/Pandoc provisioning can access networks and must not be conflated with runtime privacy.

Permitted provisional wording: “The Toolkit has no telemetry or automatic update-check feature and processes inputs on user-selected filesystem paths.” Do not promise a mathematical absence of network activity in every third-party dependency/version, or treat static search as packet-level proof. 9.2b should exercise installed commands with outbound application services unavailable/monitored and record dependency versions; don't introduce new runtime flags merely to satisfy an audit assertion.

Mounted NAS access is filesystem I/O and may use SMB/NFS over the network under OS control; it is not telemetry or external metadata submission. User-selected destinations, preserved FITS headers, generated indexes and CLI errors may contain locations/paths. Advise users to redact logs, configs, FITS GPS/device information and screenshots before submitting issues. No actual storage permission prompts were tested in this audit.

## 13. Public repository and CI requirements

9.3a: root CONTRIBUTING.md, Bug Report and Feature Request templates; include safe minimal reproduction, version, tested platform, diagnostic text, privacy warning and instructions not to upload original personal FITS/configs casually. No automatic log upload. Keep author/licence attribution unobtrusive.

Manual/authenticated GitHub settings: establish intended owner/repo; verify PRIVATE throughout pre-publication; enable Issues; disable Discussions and Wiki; review collaborators, Actions permissions, artifacts/log visibility and repository history. Repository files cannot prove current server settings. 9.4a records settings/privacy audit; 9.4b changes visibility only after Gate 1. Current repo identity/privacy is unverified and is this stage's blocker (criterion 60).

9.1d CI: run safe public tests, Ruff and agreed formatting/package checks on relevant pushes/pull requests, use pinned/reviewed action references and least privilege (`contents: read`), avoid secrets for untrusted PRs. Provision candidate Python jobs as candidates, then synchronize matrix to every officially supported version after 9.2a; every final supported version must be tested. Prefer suitable macOS arm64 runners for runtime evidence; portable quality jobs on another OS do not imply product support there. No private real datasets or personally identifying fixture/log artifacts. Validate wheel/sdist metadata and contents, build-from-sdist and baseline tests. No automatic release, tag, release asset upload, PyPI publish, version edits or documentation changes. Ordinary ephemeral build/test artifacts, if retained, require privacy/content review and must not become GitHub Release assets automatically.

## 14. Markdown/PDF/checksum pipeline requirements

9.3a sources are the two exact Markdown guide names in docs/user. 9.3b should provide a repository-defined wrapper/defaults/template using Pandoc and an explicit XeLaTeX engine with known fonts. This is a recommended mechanism, not a proven installed toolchain. [Pandoc manual](https://pandoc.org/MANUAL.html) documents Markdown-to-PDF and engine selection. Pin/record tested tool/font versions for reproducibility; keep everything development/release-only, never a wheel runtime prerequisite.

Per guide, the future wrapper must:

1. Read the one authoritative package version; inject it into rendering without a separate document version. Validate source placeholders/literals and generated version against it.
2. Render to a temporary PDF using only approved local assets and explicit options; no silent remote assets or hand-edited PDF.
3. Fail on conversion/version/content errors, then replace the output only after validation.
4. Set PDF filesystem modification time to the Markdown source's mtime using a portable stdlib operation. Record filesystem precision; validate immediately and after checkout/release extraction where applicable. mtime alone does not prove freshness; Git does not preserve source mtimes.
5. Hash final Markdown bytes and final PDF bytes with SHA-256, and write exactly two named entries to that guide's repository `.sha256` manifest using stable relative filenames.
6. Re-read/verify both hashes. Do not hash the manifest into itself. Source/assets/version/tool changes require regeneration and checks.
7. Verify text extraction/searchability, title/version, contents/bookmarks, links, example correctness, fonts, code wrapping, tables, page breaks and visual pagination; no clipped or missing content. Test offline readability.

Repository policy includes Markdown, PDFs and per-guide SHA manifests at the specified docs/user paths; they are distinct from uncommitted wheel/sdist/ZIP artifacts. Git checkout timestamps and PDF embedded dates require deliberate deterministic rules. A second build should compare bytes under controlled toolchain/metadata; if nondeterminism exists, record its cause rather than claim byte reproducibility. No PDF is generated here.

## 15. Release artifacts, ZIP and exclusions

Fixed official distribution: GitHub Releases only, no PyPI. Primary supplied wheel installed into a user venv; secondary standards-compliant sdist. No installer script or native installer. Artifacts remain uncommitted.

Exact ZIP name: `seestar-toolkit-1.1.0-release.zip`; one top-level directory:

```text
seestar-toolkit-1.1.0/
    SEESTAR_TOOLKIT_QUICK_START.pdf
    SEESTAR_TOOLKIT_USER_GUIDE.pdf
    README.md
    CHANGELOG.md
    LICENSE
    seestar_toolkit-1.1.0-<wheel-tags>.whl
    seestar_toolkit-1.1.0.tar.gz
```

Exclude development docs, guide Markdown, repository guide SHA manifests, tests, private data, .git, GitHub/CI infrastructure, development tools, caches and temporary files. Use an allowlist and inspect nested wheel/sdist contents as well as the outer ZIP to avoid smuggling exclusions through embedded archives. Recommend minimal runtime wheel and buildable sdist containing source/build metadata, licence and required public readme, with no test/private/dev payload. Top-level PDFs supply end-user manuals; normal wheel installation must not render PDFs. 9.1c/d defines and verifies the precise inner distributions; 9.4a assembles the exact final inventory.

The external checksum is `seestar-toolkit-1.1.0-release.zip.sha256`, beside and never inside the ZIP; hash the final ZIP bytes, name the ZIP correctly, verify after upload/download. Wheel, sdist, ZIP and external checksum are generated uncommitted artifacts. The GitHub Release must upload the ZIP and external SHA file; wheel/sdist are included in ZIP. Do not silently add separate assets or a provenance file to the ordinary-user ZIP. 9.4a release text derives from root CHANGELOG, not a RELEASE_NOTES.md file.

## 16. Provenance, two gates and publication-date handling

9.4b records privately/in the agreed development audit: Toolkit version; full release SHA; tag; build and publication dates; macOS version/build; architecture; Python and pip versions; relevant setuptools/wheel/build and PDF/archive tool versions; SHA-256 of wheel, sdist and release ZIP. Link tested candidate evidence to final clean artifacts. No extra provenance file in user ZIP.

**Gate 1:** audit exact clean committed release tree. Expected pending development entries are incorporated through the established approval/commit workflow before the clean-tree GO; they are expected during development, not waived on the final tree. Any readiness/privacy failure = NO-GO, no tag/publication, Stage 9 open; retain the failed audit. Immutable audit evidence must identify the full approved SHA.

Only after GO and publication authorization: annotate `v1.1.0` at that exact SHA with `Seestar Toolkit v1.1.0`; clean build directories; build final artifacts from approved/tagged source; verify contents, source relationship and hashes; STOP on mismatch; push approved commits/tag; make repository public; create normal v1.1.0 GitHub Release; upload ZIP/external checksum; independently verify the published release/downloads.

**Gate 2:** Stage 9.4b and Stage 9 COMPLETE only after tag/source/artifact match, intended public visibility, correct release and assets, downloaded checksum validation, correct public documentation, recorded provenance and finalized private runbook. Any post-GO, post-tag or pre-publication problem is STOP and leaves Stage 9 open. A later successful replacement audit does not rewrite an earlier failure.

Publication-date sequencing needs explicit treatment in 9.4a/b: tagged source and ZIP may legitimately retain Unreleased because actual publication has not occurred. After actual publication, update public root CHANGELOG using the actual GitHub date in a separately recorded documentation-only follow-up, without moving the approved tag or silently rebuilding/replacing audited assets. Gate 2 must check and explain the tagged-versus-current documentation distinction. If the release owner instead requires a dated CHANGELOG inside the ZIP, that conflicts with an immutable pre-publication build plus an unknown actual publication date; resolve the policy explicitly before GO, not by backdating or retagging. No change to the two-gate model is proposed here.

## 17. Private runbook plan

Proposed location: `<private-work-root>/seestar-toolkit-release/SEESTAR_TOOLKIT_RELEASE_PROCESS.md`, a user-selected private directory outside this repository and all public/synced repositories. Verify the parent is not a Git worktree and is not published/backed up publicly before writing. Do not use docs/development as a substitute for private storage. No runbook created now.

Sections and proven-procedure contributors:

- release contract/prerequisites and placeholders `<VERSION>`, `<TAG>`, `<RELEASE_COMMIT>`, `<RELEASE_DATE>` — 9.1a;
- development layout, local safe data, privacy policy — 9.1b;
- version and packaging inputs — 9.1c;
- local validation/build/CI, local Git review workflow — 9.1d;
- clean installation and compatibility records — 9.2a;
- installed CLI/storage/configuration checks — 9.2b;
- guide maintenance — 9.3a;
- proven PDF/checksum procedure — 9.3b;
- candidate contents/privacy/GO checklist — 9.4a;
- exact final audit, annotated tag, clean build, artifact verification, GitHub push, repository visibility, GitHub Release, post-publication checks and recovery — 9.4b.

Future commands remain marked proposed until actually executed/validated by the owning stage. Finalize from the proven publication process at Gate 2. STOP conditions: failed validation; unexpected dirty tree; any dirty final GO tree; privacy/publication failure; checksum mismatch; approved/tagged build discrepancy; any post-tag/pre-publication problem; wrong assets/tag/date or failed post-publication verification. Never solve a STOP by silently replacing audited evidence.

## 18. Findings, blockers and downstream action register

| ID | Finding / requirement | Owner / disposition |
|---|---|---|
| A01 | GitHub identity/privacy unverified, no remote/auth | 9.1a criterion 60 FAIL; obtain evidence before approving this step; then 9.4a/b recheck |
| A02 | Specification under misspelled devlopment | Correct bootstrap copy created under explicit exception; duplicate disposition 9.1b |
| A03 | Full layout/reference migration outstanding | 9.1b, with 9.3a public content completion |
| A04 | Version fallback/test/doc literals duplicate authority | 9.1c, with 9.3a/b derived docs version and 9.4a/b identity checks |
| A05 | Backend floor does not guarantee licence syntax | 9.1c correct; 9.1d isolated builds prove |
| A06 | Misleading alpha/OS Independent and incomplete description/URLs | 9.1c; final Python declarations only after 9.2a |
| A07 | Installed dependencies differ from declared Python floor | 9.2a candidate proof; 9.1c candidate-compatible config; no blind pins |
| A08 | No release content allowlist/build/CI | 9.1c configuration, 9.1d build/CI; 9.4a nested contents gate |
| A09 | Tracked real FITS contain potentially identifying metadata; large blob | 9.1b privacy/fixture strategy, authorized follow-up if needed; 9.1d safe tests; 9.4a history/privacy blocker |
| A10 | Blanket FIT/FITS ignores, inaccurate fixture inventory | 9.1b scoped ignores/REAL_DATA_TESTING and fixture documentation |
| A11 | README/CHANGELOG incomplete or inaccurate CLI wording | 9.1b handoff; 9.3a accurate user documents |
| A12 | Clean installation/platform/storage proof absent | 9.2a installation/Python/macOS envelope; 9.2b installed runtime/storage/privacy |
| A13 | Missing guides/PDF/mtime/manifests | 9.3a Markdown, 9.3b validated generation |
| A14 | Public contribution/templates/settings absent/unverified | 9.3a repository files; 9.4a manual settings/privacy, 9.4b visibility only after GO |
| A15 | Release ZIP/checksums/provenance/runbook unimplemented | 9.4a candidate assembly; 9.4b final build/publication/Gate 2; runbook populated progressively |
| A16 | Missing explicit future enhancement entries | 9.1b PROJECT_Notes only; 9.3a limits; no implementation |
| A17 | Actual publication date versus immutable tagged docs | 9.4a/b explicit documented sequence before GO, no silent date/tag/artifact mutation |
| A18 | Earlier formatting debt and private literals in historical docs | 9.1b migration/privacy scope; 9.1d agreed quality scope; 9.4a full-history privacy check |

These are audit findings/requirements, not implemented fixes. No release readiness or distribution safety is asserted now. Stage 8 correctness remains its established baseline.

## 19. Validation results and final state

**STEP COMPLETE — Packaging, runtime and release evidence audit**
**STEP START — Validation and report checks**

| Check | Result |
|---|---|
| git status/rev-parse/log | Correct 995c988 baseline; expected pending docs plus typo bootstrap identified |
| python -m pytest | 314 passed in 11.30s; unchanged Stage 8 test count |
| ruff check . | PASS |
| Established archive-scoped Ruff format check | PASS: 26 unchanged files already formatted |
| Audit/spec Markdown format check | PASS: both files already formatted |
| git diff --check | PASS |
| importlib.metadata inspection | Existing editable 1.1.0 distribution; declared entry point and dependencies inventoried |
| Both --version entry points | seestar-toolkit 1.1.0, exit 0 |
| python -m pip check | No broken requirements; cache-disabled permission warning is non-blocking; no install attempted |
| Read-only tracked FITS header audit | All 10 inspected; identifying-key presence reported without values; no fixture write |
| Cross-reference/version/import search | Completed; inventories in report/appendix |
| gh repo view | Exit 4: not authenticated; no remote to identify repository; criterion 60 unverified |
| git tag --list | Empty initially; no tag created |

Environment: project development Python 3.13.15 at the established project venv; macOS 26.5.2 arm64; pytest 9.1.1; Ruff 0.16.0. No clean venv or release build performed. Applicable formatting follows existing Stage 8 scoped validation; known broader formatting debt is not hidden or “fixed” opportunistically. Auditing an unchanged source tree does not authorize reformatting it.

Files created: authoritative bootstrap `STAGE_9.1a.md` and this `STAGE_9.1a_AUDIT.md` in docs/development/change_documents/STAGE_9. No existing file modified by this task. Expected pending docs and the misspelled original are preserved and hash-checked. Temporary audit scripts/indexes under /tmp are outside the repository and contain no FITS data or private metadata values. No commit, staging, tag, push, publication, broader documentation migration, production/test change or Stage 9.1b execution occurred.

## 20. Explicit closure-criteria audit

61 PASS; 1 FAIL (60: repository privacy not established). FAIL is retained until separately verified; a missing proof is not converted into a pass. This report is not approval to commit or begin 9.1b.

| # | Result | Criterion and evidence |
|---|---|---|
| 1 | PASS | The audit identifies `995c988` as the Stage 8 closure baseline. See section 2. |
| 2 | PASS | Expected pending Stage 8.3a CHANGELOG work is identified and not misclassified as unexpected. See section 2. |
| 3 | PASS | Expected pending `PROJECT_Notes.md` Stage 9 change is identified and not misclassified as unexpected. See section 2. |
| 4 | PASS | No unauthorised production-code change has been made. See section 2. |
| 5 | PASS | No broader documentation reorganisation has been performed beyond the 9.1a bootstrap exception. See section 2. |
| 6 | PASS | Current packaging/build configuration is fully inventoried. See section 3. |
| 7 | PASS | All current version-definition/use sites are inventoried. See section 4. |
| 8 | PASS | A recommended single authoritative version-source approach is identified for 9.1c. See section 4. |
| 9 | PASS | Runtime dependencies are distinguished from development/test/build/docs/release dependencies. See section 5. |
| 10 | PASS | Any undeclared or suspicious dependency coupling is identified. See section 5. |
| 11 | PASS | Proposed version-constraint policy avoids blind development-machine pinning. See section 5. |
| 12 | PASS | Known reasons for any recommended upper bounds are stated. See section 5. |
| 13 | PASS | A candidate Python test matrix is produced. See section 6. |
| 14 | PASS | Candidate versions are not falsely labelled supported. See section 6. |
| 15 | PASS | The 9.1c → 9.2a sequencing dependency is explicitly preserved. See section 6. |
| 16 | PASS | The process for finalising Python metadata after 9.2a evidence is explicitly defined. See section 6. |
| 17 | PASS | Apple Silicon/macOS-only release intent is checked against the current code/dependencies. See section 7. |
| 18 | PASS | A later macOS validation plan is defined. See section 7. |
| 19 | PASS | No unsupported platform is accidentally presented as officially supported. See section 7. |
| 20 | PASS | Both official entry points are inventoried. See section 8. |
| 21 | PASS | Actual commands/options needed for later documentation are inventoried. See section 8. |
| 22 | PASS | Diagnostics/error/exit-code behaviour is inventoried sufficiently for 9.3. See section 8. |
| 23 | PASS | An evidence-based supported-input/capture matrix is produced. See section 9. |
| 24 | PASS | Matrix claims distinguish automated-test evidence from Stage 8 real-data evidence. See section 9. |
| 25 | PASS | No unvalidated S50 Pro/S30/S30 Pro support claim is made. See section 9. |
| 26 | PASS | DSLR/conventional-camera archive ingestion is explicitly excluded from v1.1.0. See section 9. |
| 27 | PASS | Solar/Lunar/Planetary MP4 processing remains a future enhancement unless separately implemented and validated. See section 9. |
| 28 | PASS | Current documentation paths are inventoried. See section 10. |
| 29 | PASS | The complete 9.1b migration map is defined. See section 10. |
| 30 | PASS | Old-path references requiring updates are identified. See section 10. |
| 31 | PASS | Current test fixtures are assessed for public suitability. See section 11. |
| 32 | PASS | A safe ignored private real-data testing strategy is proposed without globally ignoring legitimate FIT/FITS fixtures. See section 11. |
| 33 | PASS | Intended telemetry/update/network privacy statements are checked against source behaviour. See section 12. |
| 34 | PASS | Mounted network filesystem behaviour is distinguished from application telemetry/network services. See section 12. |
| 35 | PASS | Public-repository preparation work is mapped to downstream steps. See section 13. |
| 36 | PASS | Manual GitHub settings are distinguished from repository files. See section 13. |
| 37 | PASS | CI requirements are fully defined. See section 13. |
| 38 | PASS | CI is explicitly prevented from performing publication/tag/version/doc mutation tasks. See section 13. |
| 39 | PASS | PDF-generation requirements are fully defined. See section 14. |
| 40 | PASS | PDF tooling is classified as development/release-only. See section 14. |
| 41 | PASS | Documentation-version derivation from the authoritative package version is planned. See section 14. |
| 42 | PASS | Release ZIP contents/exclusions are fully defined and match the release policy. See section 15. |
| 43 | PASS | External release-ZIP checksum handling is correctly defined. See section 15. |
| 44 | PASS | Wheel/sdist/ZIP release artifacts are confirmed as uncommitted generated artifacts. See section 15. |
| 45 | PASS | Required release provenance fields are defined. See section 16. |
| 46 | PASS | A safe outside-repository plan for `SEESTAR_TOOLKIT_RELEASE_PROCESS.md` is defined. See section 17. |
| 47 | PASS | The runbook's progressive/proven-procedure model is preserved. See section 17. |
| 48 | PASS | Required runbook STOP conditions are defined. See section 17. |
| 49 | PASS | Stage 9.4b Gate 1 GO/NO-GO sequencing is preserved. See section 16. |
| 50 | PASS | Tag/build/publication steps occur only after Gate 1 GO. See section 16. |
| 51 | PASS | Stage 9.4b COMPLETE and Stage 9 COMPLETE occur only after Gate 2 post-publication verification. See section 16. |
| 52 | PASS | A post-GO/pre-publication problem is explicitly treated as a STOP condition leaving Stage 9 open. See section 16. |
| 53 | PASS | Full existing automated tests pass, or any failure is fully explained and causes 9.1a to fail. See section 19. |
| 54 | PASS | Ruff/established quality checks pass. See section 19. |
| 55 | PASS | `git diff --check` or the repository-equivalent whitespace validation passes. See section 19. |
| 56 | PASS | `STAGE_9.1a_AUDIT.md` exists and covers every required audit area. See section 19. |
| 57 | PASS | Every identified downstream action is mapped to the appropriate Stage 9 step. See section 19. |
| 58 | PASS | No release publication action has occurred. See section 19. |
| 59 | PASS | No release tag has been created. See section 19. |
| 60 | FAIL | The repository remains private. No authenticated visibility evidence; no remote configured. Do not infer PRIVATE. |
| 61 | PASS | The audit ends with an explicit **PASS** or **FAIL** recommendation. Explicit FAIL recommendation; criterion 60 is not waived. |
| 62 | PASS | If any criterion is unsatisfied, the recommendation is **FAIL** and the step must not be retrospectively described as passed. Explicit FAIL recommendation; criterion 60 is not waived. |

## Appendix A — Cross-reference file inventory for 9.1b

Files matched for old documentation paths, README/CHANGELOG/architecture/project-note references, or local Stage 8 validation paths. Inspect semantic context before editing; do not mass-replace frozen provenance. Contents with personal values are not reproduced here.

- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/change_documents/STAGE_2/STAGE_2.2e.md`
- `docs/change_documents/STAGE_3/STAGE_3.1a.md`
- `docs/change_documents/STAGE_3/STAGE_3.1b.md`
- `docs/change_documents/STAGE_3/STAGE_3.1c.md`
- `docs/change_documents/STAGE_3/STAGE_3.1e.md`
- `docs/change_documents/STAGE_4/STAGE_4.1a.md`
- `docs/change_documents/STAGE_4/STAGE_4.1b.md`
- `docs/change_documents/STAGE_4/STAGE_4.1c.md`
- `docs/change_documents/STAGE_4/STAGE_4.1d.md`
- `docs/change_documents/STAGE_4/STAGE_4.1e.md`
- `docs/change_documents/STAGE_4/STAGE_4.1f.md`
- `docs/change_documents/STAGE_5/STAGE_5.1b.md`
- `docs/change_documents/STAGE_5/STAGE_5.1c.md`
- `docs/change_documents/STAGE_5/STAGE_5.1d.md`
- `docs/change_documents/STAGE_5/STAGE_5.1e.md`
- `docs/change_documents/STAGE_5/STAGE_5.1f.md`
- `docs/change_documents/STAGE_6/STAGE_6.1a.md`
- `docs/change_documents/STAGE_6/STAGE_6.1b.md`
- `docs/change_documents/STAGE_6/STAGE_6.1c.md`
- `docs/change_documents/STAGE_6/STAGE_6.1d.md`
- `docs/change_documents/STAGE_6/STAGE_6.1e.md`
- `docs/change_documents/STAGE_6/STAGE_6.1f.md`
- `docs/change_documents/STAGE_6/STAGE_6.1g.md`
- `docs/change_documents/STAGE_6/STAGE_6.1h.md`
- `docs/change_documents/STAGE_7/STAGE_7.1a.md`
- `docs/change_documents/STAGE_7/STAGE_7.1b.md`
- `docs/change_documents/STAGE_7/STAGE_7.1c.md`
- `docs/change_documents/STAGE_7/STAGE_7.1d.md`
- `docs/change_documents/STAGE_7/STAGE_7.1e.md`
- `docs/change_documents/STAGE_7/STAGE_7.1f.md`
- `docs/change_documents/STAGE_7/STAGE_7.1g.md`
- `docs/change_documents/STAGE_7/STAGE_7.1h.md`
- `docs/change_documents/STAGE_7/STAGE_7.1i.md`
- `docs/change_documents/STAGE_7/STAGE_7.1j.md`
- `docs/change_documents/STAGE_8/STAGE_8.0.md`
- `docs/change_documents/STAGE_8/STAGE_8.1a.md`
- `docs/change_documents/STAGE_8/STAGE_8.1b.md`
- `docs/change_documents/STAGE_8/STAGE_8.1c.md`
- `docs/change_documents/STAGE_8/STAGE_8.1d.md`
- `docs/change_documents/STAGE_8/STAGE_8.1e.md`
- `docs/change_documents/STAGE_8/STAGE_8.2a.md`
- `docs/change_documents/STAGE_8/STAGE_8.2b.md`
- `docs/change_documents/STAGE_8/STAGE_8.2c.md`
- `docs/change_documents/STAGE_8/STAGE_8.2d.md`
- `docs/change_documents/STAGE_8/STAGE_8.2e.md`
- `docs/change_documents/STAGE_8/STAGE_8.2f.md`
- `docs/change_documents/STAGE_8/STAGE_8.2g.md`
- `docs/change_documents/STAGE_8/STAGE_8.3a.md`
- `docs/CHANGELOG.md`
- `<private development-environment notes>`
- `<private development-environment notes>`
- `docs/development/change_documents/STAGE_9/STAGE_9.1a.md`
- `docs/devlopment/change_documents/STAGE_9/STAGE_9.1a.md`
- `docs/PROJECT_Notes.md`
- `pyproject.toml`

**STEP COMPLETE — Validation and report checks**

**STAGE COMPLETE — Stage 9.1a audit execution — FAIL recommendation; approval blocked by criterion 60.**


---

## Closure revalidation R1 — 2026-09-10

**STAGE START — Stage 9.1a narrow closure revalidation**

**Current recommendation: PASS — all 62 closure criteria now pass. Stage 9.1a can be closed, subject to the established report-review and commit-approval workflow.**

### R1.1 Historical result and new authoritative evidence

The initial validation remains **FAIL: 61 PASS / 1 FAIL**, because criterion 60 could not be proven. Its report, criterion table and FAIL banners above are preserved byte-for-byte. This appended revalidation does not retrospectively change that result.

The user subsequently confirmed the authoritative project state:

- No GitHub repository has yet been created for Seestar Toolkit.
- No public GitHub repository exists and no GitHub publication has occurred.
- The project exists only as the local Git repository.
- The earlier `docs/devlopment` path was a user typo; the user removed that incorrect copy.
- The specification remains `docs/development/change_documents/STAGE_9/STAGE_9.1a.md`.

Criterion 60 now passes on this explicit user-supplied project-state evidence: the project has not been made public. This is not a claim that a nonexistent GitHub repository has a PRIVATE visibility setting, nor an inference from a missing Git remote. No GitHub query, authentication, repository creation or publication operation was required or performed during revalidation. Future repository creation must preserve private status until the specified publication gate.

Initial finding A01 is resolved by this new evidence. A02's remaining typo-copy disposition was completed by the user, not by a wider documentation migration during revalidation. The original descriptions remain historical. All other downstream findings and ownership remain unchanged; their implementation is not a prerequisite of this audit-only stage.

**STEP COMPLETE — Current state and historical evidence verified**
**STEP START — Repository validation and criterion re-evaluation**

### R1.2 Reconfirmed repository state and validation

Starting and ending HEAD: `995c988cd7effa405ba1495445d877a548b2b9e3` (Stage 8.3a: validate and close Stage 8).

Expected pending tracked changes remain exactly the Stage 8.3a detailed entry in `docs/CHANGELOG.md` and Stage 9 wording in `docs/PROJECT_Notes.md`. The authorized bootstrap specification and audit are untracked under `docs/development/`. The misspelled directory is absent. No unexpected implementation changes were found.

| Check | Revalidation result |
|---|---|
| `python -m pytest` using project venv | **314 passed in 11.84s**, unchanged baseline count |
| `ruff check .` | PASS |
| Applicable `ruff format --check` | PASS: 28 files already formatted (archive source/unit tests, three archive integration files, specification and audit) |
| `git diff --check` | PASS |
| `git diff HEAD -- src tests pyproject.toml .gitignore` | Empty: no production, packaging, test or ignore-policy changes |
| `git diff --cached` | Empty: no staging |
| `git remote -v` / `git tag --list` | Empty; corroborating local observations, not independent proof of GitHub state |
| Pending docs/specification hashes | Unchanged throughout revalidation |
| Original audit prefix | Preserved byte-for-byte; only this section appended |

Environment remains project Python 3.13.15, pytest 9.1.1, Ruff 0.16.0. Commands use `<development-environment>/bin/`. Existing unrelated formatting debt is unchanged; applicable checks retain the established scope.

Only `STAGE_9.1a_AUDIT.md` was modified during this revalidation. No production/package/test implementation, new audit scope, fixture inspection or external dataset operation was undertaken. No GitHub publication action, tag, push, commit or Stage 9.1b work occurred. The specification and expected pending documentation are unchanged.

### R1.3 All 62 closure criteria re-evaluated

The original evidence was reviewed for continuing applicability against the unchanged baseline. Criteria 1–59 and 61–62 retain their audit evidence, supplemented by fresh quality checks and history-preservation checks. Criterion 60 changes from unverified/FAIL to PASS only on the subsequent user confirmation.

| # | R1 result | Criterion and revalidation evidence |
|---|---|---|
| 1 | PASS | The audit identifies `995c988` as the Stage 8 closure baseline. R1.2: unchanged baseline, expected pending docs, no implementation/migration; typo copy removed by user. |
| 2 | PASS | Expected pending Stage 8.3a CHANGELOG work is identified and not misclassified as unexpected. R1.2: unchanged baseline, expected pending docs, no implementation/migration; typo copy removed by user. |
| 3 | PASS | Expected pending `PROJECT_Notes.md` Stage 9 change is identified and not misclassified as unexpected. R1.2: unchanged baseline, expected pending docs, no implementation/migration; typo copy removed by user. |
| 4 | PASS | No unauthorised production-code change has been made. R1.2: unchanged baseline, expected pending docs, no implementation/migration; typo copy removed by user. |
| 5 | PASS | No broader documentation reorganisation has been performed beyond the 9.1a bootstrap exception. R1.2: unchanged baseline, expected pending docs, no implementation/migration; typo copy removed by user. |
| 6 | PASS | Current packaging/build configuration is fully inventoried. Initial section 3 remains applicable; no implementation or policy change. |
| 7 | PASS | All current version-definition/use sites are inventoried. Initial section 4 remains applicable; no implementation or policy change. |
| 8 | PASS | A recommended single authoritative version-source approach is identified for 9.1c. Initial section 4 remains applicable; no implementation or policy change. |
| 9 | PASS | Runtime dependencies are distinguished from development/test/build/docs/release dependencies. Initial section 5 remains applicable; no implementation or policy change. |
| 10 | PASS | Any undeclared or suspicious dependency coupling is identified. Initial section 5 remains applicable; no implementation or policy change. |
| 11 | PASS | Proposed version-constraint policy avoids blind development-machine pinning. Initial section 5 remains applicable; no implementation or policy change. |
| 12 | PASS | Known reasons for any recommended upper bounds are stated. Initial section 5 remains applicable; no implementation or policy change. |
| 13 | PASS | A candidate Python test matrix is produced. Initial section 6 remains applicable; no implementation or policy change. |
| 14 | PASS | Candidate versions are not falsely labelled supported. Initial section 6 remains applicable; no implementation or policy change. |
| 15 | PASS | The 9.1c → 9.2a sequencing dependency is explicitly preserved. Initial section 6 remains applicable; no implementation or policy change. |
| 16 | PASS | The process for finalising Python metadata after 9.2a evidence is explicitly defined. Initial section 6 remains applicable; no implementation or policy change. |
| 17 | PASS | Apple Silicon/macOS-only release intent is checked against the current code/dependencies. Initial section 7 remains applicable; no implementation or policy change. |
| 18 | PASS | A later macOS validation plan is defined. Initial section 7 remains applicable; no implementation or policy change. |
| 19 | PASS | No unsupported platform is accidentally presented as officially supported. Initial section 7 remains applicable; no implementation or policy change. |
| 20 | PASS | Both official entry points are inventoried. Initial section 8 remains applicable; no implementation or policy change. |
| 21 | PASS | Actual commands/options needed for later documentation are inventoried. Initial section 8 remains applicable; no implementation or policy change. |
| 22 | PASS | Diagnostics/error/exit-code behaviour is inventoried sufficiently for 9.3. Initial section 8 remains applicable; no implementation or policy change. |
| 23 | PASS | An evidence-based supported-input/capture matrix is produced. Initial section 9 remains applicable; no implementation or policy change. |
| 24 | PASS | Matrix claims distinguish automated-test evidence from Stage 8 real-data evidence. Initial section 9 remains applicable; no implementation or policy change. |
| 25 | PASS | No unvalidated S50 Pro/S30/S30 Pro support claim is made. Initial section 9 remains applicable; no implementation or policy change. |
| 26 | PASS | DSLR/conventional-camera archive ingestion is explicitly excluded from v1.1.0. Initial section 9 remains applicable; no implementation or policy change. |
| 27 | PASS | Solar/Lunar/Planetary MP4 processing remains a future enhancement unless separately implemented and validated. Initial section 9 remains applicable; no implementation or policy change. |
| 28 | PASS | Current documentation paths are inventoried. Initial section 10 remains applicable; no implementation or policy change. |
| 29 | PASS | The complete 9.1b migration map is defined. Initial section 10 remains applicable; no implementation or policy change. |
| 30 | PASS | Old-path references requiring updates are identified. Initial section 10 remains applicable; no implementation or policy change. |
| 31 | PASS | Current test fixtures are assessed for public suitability. Initial section 11 remains applicable; no implementation or policy change. |
| 32 | PASS | A safe ignored private real-data testing strategy is proposed without globally ignoring legitimate FIT/FITS fixtures. Initial section 11 remains applicable; no implementation or policy change. |
| 33 | PASS | Intended telemetry/update/network privacy statements are checked against source behaviour. Initial section 12 remains applicable; no implementation or policy change. |
| 34 | PASS | Mounted network filesystem behaviour is distinguished from application telemetry/network services. Initial section 12 remains applicable; no implementation or policy change. |
| 35 | PASS | Public-repository preparation work is mapped to downstream steps. Initial section 13 remains applicable; no implementation or policy change. |
| 36 | PASS | Manual GitHub settings are distinguished from repository files. Initial section 13 remains applicable; no implementation or policy change. |
| 37 | PASS | CI requirements are fully defined. Initial section 13 remains applicable; no implementation or policy change. |
| 38 | PASS | CI is explicitly prevented from performing publication/tag/version/doc mutation tasks. Initial section 13 remains applicable; no implementation or policy change. |
| 39 | PASS | PDF-generation requirements are fully defined. Initial section 14 remains applicable; no implementation or policy change. |
| 40 | PASS | PDF tooling is classified as development/release-only. Initial section 14 remains applicable; no implementation or policy change. |
| 41 | PASS | Documentation-version derivation from the authoritative package version is planned. Initial section 14 remains applicable; no implementation or policy change. |
| 42 | PASS | Release ZIP contents/exclusions are fully defined and match the release policy. Initial section 15 remains applicable; no implementation or policy change. |
| 43 | PASS | External release-ZIP checksum handling is correctly defined. Initial section 15 remains applicable; no implementation or policy change. |
| 44 | PASS | Wheel/sdist/ZIP release artifacts are confirmed as uncommitted generated artifacts. Initial section 15 remains applicable; no implementation or policy change. |
| 45 | PASS | Required release provenance fields are defined. Initial section 16 remains applicable; no implementation or policy change. |
| 46 | PASS | A safe outside-repository plan for `SEESTAR_TOOLKIT_RELEASE_PROCESS.md` is defined. Initial section 17 remains applicable; no implementation or policy change. |
| 47 | PASS | The runbook's progressive/proven-procedure model is preserved. Initial section 17 remains applicable; no implementation or policy change. |
| 48 | PASS | Required runbook STOP conditions are defined. Initial section 17 remains applicable; no implementation or policy change. |
| 49 | PASS | Stage 9.4b Gate 1 GO/NO-GO sequencing is preserved. Initial section 16 remains applicable; no implementation or policy change. |
| 50 | PASS | Tag/build/publication steps occur only after Gate 1 GO. Initial section 16 remains applicable; no implementation or policy change. |
| 51 | PASS | Stage 9.4b COMPLETE and Stage 9 COMPLETE occur only after Gate 2 post-publication verification. Initial section 16 remains applicable; no implementation or policy change. |
| 52 | PASS | A post-GO/pre-publication problem is explicitly treated as a STOP condition leaving Stage 9 open. Initial section 16 remains applicable; no implementation or policy change. |
| 53 | PASS | Full existing automated tests pass, or any failure is fully explained and causes 9.1a to fail. Fresh full run: 314 passed in 11.84s. |
| 54 | PASS | Ruff/established quality checks pass. Fresh Ruff and applicable formatting checks pass. |
| 55 | PASS | `git diff --check` or the repository-equivalent whitespace validation passes. Fresh git diff --check passes. |
| 56 | PASS | `STAGE_9.1a_AUDIT.md` exists and covers every required audit area. Complete initial report preserved, with this appended revalidation. |
| 57 | PASS | Every identified downstream action is mapped to the appropriate Stage 9 step. Initial section 18 action register retained; A01 resolved by confirmation, A02 typo cleanup completed by user. |
| 58 | PASS | No release publication action has occurred. User confirms no GitHub repository/publication exists; no publication operation by this task. |
| 59 | PASS | No release tag has been created. No local tags and no tag operation; HEAD unchanged. |
| 60 | PASS | The repository remains private. R1.1: authoritative user confirmation establishes local-only, not-public project state; no GitHub repository exists yet. |
| 61 | PASS | The audit ends with an explicit **PASS** or **FAIL** recommendation. Current revalidation explicitly recommends PASS with 62/62 satisfied. |
| 62 | PASS | If any criterion is unsatisfied, the recommendation is **FAIL** and the step must not be retrospectively described as passed. Initial FAIL is intact; this is a subsequent PASS based on new evidence, not a rewritten failure. |

### R1.4 Closure decision and boundaries

**PASS — Stage 9.1a can be closed.** No closure criterion remains unsatisfied. This approves neither a release nor downstream implementation. Candidate Python versions remain candidates; 9.2a remains the compatibility proof. Stage 9.4b Gate 1 readiness GO and Gate 2 post-publication/closure verification remain distinct and unchanged.

The report must still follow the established review/commit-approval workflow. No commit was made. Stage 9.1b was not started and must not begin until Stage 9.1a is formally approved and committed.

**STEP COMPLETE — Repository validation and all 62 criteria re-evaluated**

**STAGE COMPLETE — Stage 9.1a closure revalidation R1 — PASS (62/62)**
