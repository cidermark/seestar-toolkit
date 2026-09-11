# Stage 9.1c completion report

**STAGE START — Stage 9.1c: Package metadata, authoritative versioning and build configuration**

Opened 2026-09-10; completion report 2026-09-11.
Authority: [STAGE_9.1c.md](STAGE_9.1c.md).

**Recommendation: PASS — all 68 closure criteria pass.**
Ready for formal closure review. No commit is made or authorised by this report.

## Baseline and continuation

Starting and final HEAD: `ff304d76e8f6f8d32c771c8e3ec5b2604d1476a0` —
`Stage 9.1b: reorganise repository and documentation`.

Initial status:

```text
 M docs/development/CHANGELOG.md
?? docs/development/change_documents/STAGE_9/STAGE_9.1c.md
```

The pending detailed Stage 9.1b entry references ff304d7. Its complete file
contents remain unchanged from the initial inventory. The untracked
specification is user-supplied authority, not unexplained work.

On continuation, existing version/configuration/tests/notes were inspected and
retained. The already-running isolated build had completed successfully; it was
not restarted or discarded. Remaining artifact and installed-entry-point checks
were completed. No historical validation was rewritten.

**STEP START / STEP COMPLETE — Baseline and authoritative evidence audit.**
Read the full 9.1c specification, repository instructions, relevant 9.1a audit
and 9.1b migration evidence; inspected metadata, runtime imports and tests.

**STEP START / STEP COMPLETE — Version, metadata and build configuration.**
Added focused regression coverage before removing the duplicate fallback;
updated only authorised package configuration and version access.

**STEP START / STEP COMPLETE — Local build and artifact inspection.**
Built sdist, then wheel from sdist, with isolated setuptools; audited complete
inventories, source bytes, metadata, entry points and license.

**STEP START / STEP COMPLETE — Regression and closure validation.**
Full tests, Ruff, applicable formatting, whitespace, preservation and
built-wheel entry-point checks pass. All 68 criteria evaluated below.

## Files created, modified and deleted

Created:

- `MANIFEST.in`: deliberate source distribution contents and private-data exclusions.
- `docs/development/PACKAGING.md`: developer version/build/dependency policy,
  validated build command and downstream boundaries.
- This completion report.

Modified:

- `pyproject.toml`: backend floor, description, classifiers, build extra and
  explicit package discovery/data policy.
- `src/seestar_toolkit/__init__.py`: remove independent fallback version.
- `tests/unit/test_package.py`: strengthen version test and add eight cases.

Preserved: pending `docs/development/CHANGELOG.md`, supplied specification,
all historical evidence, all ten fixtures and all unrelated source/tests.
No tracked file deleted. Ignored local egg-info/build output may be regenerated
by setuptools; wheel/sdist remain under ignored dist/stage9.1c.

## Version and metadata design

`pyproject.toml [project].version = "1.1.0"` remains the single authority.
Setuptools derives distribution metadata and filenames from it.
Runtime `__version__` reads `importlib.metadata.version("seestar-toolkit")`;
both CLI interfaces share that value. Future tooling can read project.version
with tomllib and validate documentation/release identifiers against it.

There is no second version file or repository-pyproject lookup at runtime.
Uninstalled source imports now raise PackageNotFoundError instead of inventing
a release value. This explicit policy is documented; developers install the
project, normally editable, and reinstall after metadata changes.
Tests prove metadata substitution propagates and missing metadata is not hidden.
Literal expected release values in tests and historical evidence are assertions,
not independently maintained production version definitions.

Metadata retains name seestar-toolkit, import name seestar_toolkit, author
Mark Wymer, MIT SPDX expression, LICENSE and primary console script. Description
now includes conversion, batch conversion and archive organisation.
Removed misleading Alpha/OS Independent and individual Python-version
classifiers without adding unproven replacement support claims or invented URLs.

Setuptools remains the backend. Its minimum is raised from 68 to 77.0.3 for
the existing PEP 639 licensing syntax. The separate wheel build requirement is
unnecessary with this backend. See
[setuptools's metadata documentation](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).
No source-file attribution banners were added.

## Dependencies and candidate Python envelope

Direct import audit found only astropy, numpy, cv2 and tifffile outside stdlib
and the package. These map exactly to the four declared runtime dependencies.

| Runtime declaration | Locally installed version | Installed Requires-Python |
|---|---|---|
| astropy>=7.0 | 8.0.1 | >=3.11 |
| numpy>=2.0 | 2.5.1 | >=3.12 |
| opencv-python-headless>=4.10 | 5.0.0.93 | >=3.6 |
| tifffile>=2025.1.10 | 2026.7.14 | >=3.12 |

All runtime bounds remain unchanged. No local exact-version freeze or speculative
upper bound was introduced. Optional dev contains pytest, pytest-cov and Ruff;
optional build contains build>=1.2. The isolated backend requirement is separate.
Artifact unconditional Requires-Dist contains exactly the four runtime packages;
development tools have extra markers. No PDF tooling was added.

Requires-Python >=3.11 is an installation floor justified by runtime tomllib,
not proof of support. Python 3.11–3.14 remain candidates only. Older compatible
NumPy/tifffile resolution is needed for 3.11. This stage has not proven that
resolution or the whole declared dependency range. **Stage 9.2a owns final clean
wheel/sdist installation and compatibility proof**, including narrowing
metadata when required. No candidate matrix was performed.

Policy remains macOS Apple Silicon only; exact macOS support is deferred.
Toolkit itself has pure Python source, so py3-none-any is technically truthful.
Native dependency wheels carry their own ABI/platform restrictions. No forced
arm64 tag or Linux/Windows support claim was introduced.

## Build commands, tooling and results

Build tooling was absent initially. The user explicitly clarified that ordinary
build-tool downloads are authorised and only PyPI publication is prohibited.
Tools were installed in temporary /tmp/seestar-stage91c-buildenv; the existing
project environment was not upgraded.

| Tool | Version used | Role |
|---|---|---|
| CPython | 3.13.15 | Existing local interpreter |
| pip | 26.2 | Temporary environment bootstrap/install |
| build | 1.6.1 | Downloaded PEP 517 frontend |
| packaging | 26.3 | Frontend dependency |
| pyproject_hooks | 1.2.0 | Frontend dependency |
| setuptools | 84.0.0 | Downloaded declared backend in isolated build environments |

The declared 77.0.3 backend floor is standards-based; the resolved backend
actually exercised here is 84.0.0. No minimum-backend matrix is claimed.

Commands executed:

```bash
# Temporary build environment; no project dependency updates.
python -m venv /tmp/seestar-stage91c-buildenv
/tmp/seestar-stage91c-buildenv/bin/python -m pip install --no-cache-dir 'build>=1.2'
# From repository root:
/tmp/seestar-stage91c-buildenv/bin/python -m build --outdir dist/stage9.1c
```

Default PyPA build produced the sdist first, then the wheel from the extracted
sdist. Backend dependencies were installed in isolated environments; no Git
checkout, editable Toolkit install or undeclared local source file was needed
for the sdist-to-wheel rebuild. Build stdout/stderr is retained locally in
/tmp/stage91c_build.log. Exit status 0.

| Artifact | Bytes | Files | Version |
|---|---:|---:|---|
| seestar_toolkit-1.1.0-py3-none-any.whl | 46,295 | 39 | 1.1.0 |
| seestar_toolkit-1.1.0.tar.gz | 35,286 | 46 | 1.1.0 |

Artifacts remain only in ignored dist/stage9.1c. git check-ignore confirms both;
neither is tracked, staged or committed. No release ZIP was assembled.

## Metadata, contents and privacy validation

Both artifacts have Name seestar-toolkit, Version 1.1.0, Author Mark Wymer,
License-Expression MIT, License-File LICENSE, Requires-Python >=3.11 and the
expected extra-marked dependency separation. Entry points map
seestar-toolkit to seestar_toolkit.cli:main. Wheel WHEEL declares
Root-Is-Purelib: true and Tag: py3-none-any. License bytes equal the root MIT
license, including Copyright (c) 2026 Mark Wymer.

All 33 packaged Python source files match repository bytes. Wheel RECORD sizes
and hashes verify. Every member was compared against an exact deliberate
inventory, and member/content checks found no FIT/FITS, local configuration,
private paths, external dataset references, caches, .DS_Store, bytecode, venv,
build debris or temporary files. No links or unsafe member paths occur.

The sdist deliberately excludes repository tests and development documentation
because they are unnecessary for rebuilding and contain material not cleared
for public distribution. Nothing is deleted or excluded from Git to achieve
this. No global Git FIT/FITS ignore is added. The transitional public root
documents are included; README development links refer to the repository.
Final public content remains with Stage 9.3a.

This artifact result does not clear the repository or its history for public
publication. The ten retained FITS fixtures and historical private literals
still require their separately approved privacy work.

## Entry points and repository validation

Installed the built wheel with --no-index --no-deps --no-compile --target into a
fresh temporary directory. Executed its generated console script and module
invocation from /tmp, with PYTHONPATH pointing only to the target installation.
Confirmed imported package origin is the built-wheel target, not checkout source.
Existing development-environment runtime dependencies were reused deliberately;
this is not a clean dependency environment or Stage 9.2a proof.

| Built-wheel interface | --version | --help | --invalid-option |
|---|---|---|---|
| seestar-toolkit | 1.1.0, exit 0 | Commands present, exit 0 | Error, exit 2 |
| python -m seestar_toolkit | 1.1.0, exit 0 | Commands present, exit 0 | Error, exit 2 |

| Repository check | Result |
|---|---|
| Focused package tests after implementation | 9 passed |
| Full pytest | 322 passed in 13.48s |
| Ruff check . | PASS |
| Applicable Ruff formatting | PASS: 28 Python files |
| git diff --check | PASS |
| git diff --cached --check | PASS |
| Tracked-content preservation | Only pyproject, package __init__ and package test differ from initial hashes |
| Pending changelog / historical evidence / fixtures | Byte-identical to initial inventory |
| git remote -v | Empty |

Test count increased from 314 to 322: two metadata-selection/absence tests plus
six parametrized console/module version/help/error cases. The pre-existing
package test was strengthened. Initial test-first run recorded one expected
failure because the old fallback swallowed missing metadata; after the authorised
fix, all nine focused tests passed. No failure was retrospectively rewritten.

Applicable formatting retains the established 26-file archive scope and adds
the two changed Python files. Unrelated pre-existing formatting debt is not
reformatted. Markdown layout/whitespace is checked separately.

## Classified execution observations

- Initial tooling download failed due sandbox DNS restrictions. Approved network
  execution then succeeded; this was infrastructure, not a package failure.
- Setuptools emits no-match warnings for defensive manifest exclusions when the
  excluded data/junk is already absent. Complete archive inventories prove the
  exclusions; no warning was hidden or treated as a missing required file.
- pip reports its normal cache-permission warning in the sandbox; cache use was
  disabled and installation completed.
- Fixture/history privacy remains a downstream publication blocker, not bundled
  artifact contamination or an unmet 9.1c requirement.

## Explicit closure criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Starting commit is `ff304d7`. | PASS | Initial and final HEAD ff304d76e8f6f8d32c771c8e3ec5b2604d1476a0. |
| 2 | Pending 9.1b detailed CHANGELOG entry is recognised and preserved. | PASS | Initial pending entry references ff304d7; its entire file hash is unchanged. |
| 3 | No unexpected starting change is ignored. | PASS | Only expected changelog and supplied untracked specification at start; continuation preserved all work. |
| 4 | One authoritative version source exists. | PASS | Static pyproject.toml project.version feeds setuptools metadata and runtime importlib.metadata. |
| 5 | Authoritative version is `1.1.0`. | PASS | project.version remains 1.1.0; focused test asserts release value. |
| 6 | CLI `seestar-toolkit --version` resolves to `1.1.0`. | PASS | Built-wheel console invocation prints seestar-toolkit 1.1.0, exit 0. |
| 7 | Module invocation version behaviour is consistent with the authoritative source. | PASS | Built-wheel module invocation prints the same, exit 0. |
| 8 | Package metadata resolves to `1.1.0`. | PASS | Both artifacts and runtime metadata report 1.1.0. |
| 9 | Wheel filename resolves to version `1.1.0`. | PASS | seestar_toolkit-1.1.0-py3-none-any.whl. |
| 10 | Sdist filename resolves to version `1.1.0`. | PASS | seestar_toolkit-1.1.0.tar.gz. |
| 11 | Independent duplicate hard-coded version definitions that can drift are removed/neutralised. | PASS | Removed independent __init__ fallback literal; absent metadata raises PackageNotFoundError. |
| 12 | Project/package name is correctly `seestar-toolkit`. | PASS | Project and artifact Name are seestar-toolkit. |
| 13 | Import package remains `seestar_toolkit`. | PASS | All 33 source files retain seestar_toolkit import layout. |
| 14 | Author metadata is `Mark Wymer`. | PASS | Both artifact Author fields are Mark Wymer. |
| 15 | MIT license metadata is correctly represented. | PASS | Both artifacts contain License-Expression: MIT. |
| 16 | License file is correctly available to packaging. | PASS | Root LICENSE matches packaged license bytes; License-File: LICENSE. |
| 17 | Build-system metadata is standards-compliant. | PASS | PEP 517 setuptools.build_meta and declared setuptools>=77.0.3; isolated builds pass. |
| 18 | Build backend is explicitly configured. | PASS | Existing setuptools backend retained explicitly. |
| 19 | Package discovery/inclusion is correct. | PASS | Discovery restricted to ordinary seestar_toolkit packages; exact source inventory verified. |
| 20 | Console entry point `seestar-toolkit` is correctly configured. | PASS | project.scripts and built entry_points.txt both map seestar-toolkit to seestar_toolkit.cli:main. |
| 21 | `python -m seestar_toolkit` remains functional. | PASS | Built-wheel module help/version/error checks pass. |
| 22 | Existing CLI behaviour is not regressed. | PASS | Full 322-test suite plus built-wheel help/version checks pass. |
| 23 | Existing exit-code behaviour remains unchanged. | PASS | Built-wheel invalid option returns 2 for both interfaces; full existing CLI suite passes. |
| 24 | Runtime dependencies are explicitly declared. | PASS | AST inventory: astropy, numpy, cv2, tifffile; all four distributions declared. |
| 25 | Development/test/build dependencies are separated from runtime dependencies. | PASS | dev extra retains test/lint; build extra contains frontend; backend isolated separately. |
| 26 | Ordinary runtime install does not require pytest/Ruff/PDF tooling. | PASS | Unconditional Requires-Dist contains exactly the four runtime dependencies. |
| 27 | No known runtime import depends on an undeclared development package. | PASS | AST audit found no other direct third-party runtime imports. |
| 28 | Runtime constraints are not blindly copied from exact developer-environment pins. | PASS | Existing lower bounds retained; no exact runtime pins or speculative upper bounds added. |
| 29 | Python 3.11–3.14 remain candidates, not falsely declared final support. | PASS | No individual Python-version classifiers; documentation identifies candidates only. |
| 30 | `requires-python` is defensible for candidate testing. | PASS | Retained >=3.11 floor based on stdlib tomllib; compatible dependency resolution remains to be proven. |
| 31 | No unvalidated Python classifiers falsely imply final support. | PASS | Removed 3.11/3.12/3.13 classifiers; no 3.14 support classifier added. |
| 32 | Completion report explicitly defers final Python support proof to 9.2a. | PASS | Explicit deferral in PACKAGING.md and this report. |
| 33 | Platform metadata remains technically truthful. | PASS | Pure Python source and Root-Is-Purelib: true; misleading OS Independent classifier removed. |
| 34 | No false arm64 wheel tagging is introduced if package is pure Python. | PASS | Wheel is truthfully py3-none-any; no forced binary platform tag. |
| 35 | Completion report distinguishes release support policy from artifact platform tagging. | PASS | Policy remains macOS Apple Silicon only; technical wheel portability is distinct. |
| 36 | Wheel builds successfully. | PASS | Isolated build succeeded; 46,295-byte wheel. |
| 37 | Sdist builds successfully. | PASS | Isolated build succeeded; 35,286-byte .tar.gz sdist. |
| 38 | Builds use standards-compliant tooling. | PASS | PyPA build 1.6.1 invoking setuptools 84.0.0 under PEP 517 isolation. |
| 39 | Build succeeds without relying on undeclared local state. | PASS | Wheel built from extracted sdist without Git checkout or installed Toolkit/backend state. |
| 40 | Wheel metadata version is `1.1.0`. | PASS | Wheel METADATA Version: 1.1.0. |
| 41 | Sdist metadata version is `1.1.0`. | PASS | Sdist PKG-INFO Version: 1.1.0. |
| 42 | Expected console entry point is present in built distribution metadata. | PASS | Both built entry_points.txt files verified. |
| 43 | Wheel contents are sane and intentional. | PASS | 39 exact allowed files; 33 sources plus six metadata/license files; RECORD verified. |
| 44 | Sdist contents are sane and intentional. | PASS | 46 exact allowed files; required source/build inputs and public root documents only. |
| 45 | No private FIT/FITS data is bundled. | PASS | No FIT/FITS members; private fixture bytes never copied into artifacts. |
| 46 | No local config/personal paths are bundled. | PASS | Complete member/content audit rejects personal path patterns; no local configs included. |
| 47 | No caches/temporary junk are bundled. | PASS | Exact inventories exclude cache, bytecode, venv, temporary and build junk. |
| 48 | Development change documents are not unintentionally included in the wheel. | PASS | No docs/development or change documents in wheel. |
| 49 | Generated build artifacts are not committed. | PASS | Artifacts only in ignored dist/stage9.1c; none staged or tracked. |
| 50 | No release ZIP is assembled. | PASS | No release ZIP created. |
| 51 | No PyPI publication occurs. | PASS | Only authorised tool downloads; no upload or PyPI release. |
| 52 | No GitHub repository/remote/authentication/push occurs. | PASS | No GitHub operation; git remote -v empty. |
| 53 | No CI/GitHub Actions implementation occurs. | PASS | No CI files created or modified. |
| 54 | No final supported Python version declaration is made. | PASS | No final Python-support declaration made. |
| 55 | No 9.2a compatibility proof is claimed. | PASS | Only current-interpreter packaging/entry-point checks; no candidate matrix run or claimed. |
| 56 | No final user documentation/PDF/checksum work is performed. | PASS | Only development packaging notes/report; no guides, PDFs or release checksums. |
| 57 | Relevant development documentation is updated only as needed. | PASS | New PACKAGING.md records design, actual commands and stage boundaries. |
| 58 | Full pytest suite passes. | PASS | 322 passed in 13.48s. |
| 59 | Ruff passes. | PASS | ruff check . passes. |
| 60 | Applicable formatting checks pass. | PASS | 28 applicable Python files pass ruff format --check; Markdown layout checked separately. |
| 61 | `git diff --check` passes. | PASS | git diff --check and cached whitespace check pass. |
| 62 | Any test-count change from 314 is explained. | PASS | 314 + eight new tests = 322; existing package test strengthened, not removed. |
| 63 | Build/artifact inspection results are included in completion report. | PASS | Build tools, commands, artifacts, metadata and complete inventories below. |
| 64 | No unrelated production refactor is introduced. | PASS | Only runtime production edit is authorised version access in __init__.py. |
| 65 | Stage 9.1c completion report explicitly evaluates all closure criteria. | PASS | This table contains all 68 original criteria with individual evidence. |
| 66 | PASS is returned only if every criterion passes. | PASS | All 68 pass; no omitted build or publication criterion treated as waived. |
| 67 | No commit is made before ChatGPT closure review. | PASS | HEAD unchanged; no staging or commit performed. |
| 68 | Stage 9.1d is not started. | PASS | No Stage 9.1d implementation or specification created. |

## Complete artifact member inventories

### Wheel — 39 files

```text
seestar_toolkit-1.1.0.dist-info/METADATA
seestar_toolkit-1.1.0.dist-info/RECORD
seestar_toolkit-1.1.0.dist-info/WHEEL
seestar_toolkit-1.1.0.dist-info/entry_points.txt
seestar_toolkit-1.1.0.dist-info/licenses/LICENSE
seestar_toolkit-1.1.0.dist-info/top_level.txt
seestar_toolkit/__init__.py
seestar_toolkit/__main__.py
seestar_toolkit/archive/__init__.py
seestar_toolkit/archive/config.py
seestar_toolkit/archive/discovery.py
seestar_toolkit/archive/exceptions.py
seestar_toolkit/archive/execution.py
seestar_toolkit/archive/execution_models.py
seestar_toolkit/archive/index_models.py
seestar_toolkit/archive/indexing.py
seestar_toolkit/archive/models.py
seestar_toolkit/archive/orchestration.py
seestar_toolkit/archive/orchestration_models.py
seestar_toolkit/archive/planning.py
seestar_toolkit/archive/planning_models.py
seestar_toolkit/archive/reconstruction.py
seestar_toolkit/archive/reconstruction_models.py
seestar_toolkit/archive/target_comparison.py
seestar_toolkit/batch.py
seestar_toolkit/cli.py
seestar_toolkit/conversion.py
seestar_toolkit/fits/__init__.py
seestar_toolkit/fits/exceptions.py
seestar_toolkit/fits/inspector.py
seestar_toolkit/fits/models.py
seestar_toolkit/fits/reader.py
seestar_toolkit/imaging/__init__.py
seestar_toolkit/imaging/demosaic.py
seestar_toolkit/imaging/rgb.py
seestar_toolkit/models.py
seestar_toolkit/tiff/__init__.py
seestar_toolkit/tiff/exceptions.py
seestar_toolkit/tiff/writer.py
```

### Sdist — 46 files

```text
CHANGELOG.md
LICENSE
MANIFEST.in
PKG-INFO
README.md
pyproject.toml
setup.cfg
src/seestar_toolkit.egg-info/PKG-INFO
src/seestar_toolkit.egg-info/SOURCES.txt
src/seestar_toolkit.egg-info/dependency_links.txt
src/seestar_toolkit.egg-info/entry_points.txt
src/seestar_toolkit.egg-info/requires.txt
src/seestar_toolkit.egg-info/top_level.txt
src/seestar_toolkit/__init__.py
src/seestar_toolkit/__main__.py
src/seestar_toolkit/archive/__init__.py
src/seestar_toolkit/archive/config.py
src/seestar_toolkit/archive/discovery.py
src/seestar_toolkit/archive/exceptions.py
src/seestar_toolkit/archive/execution.py
src/seestar_toolkit/archive/execution_models.py
src/seestar_toolkit/archive/index_models.py
src/seestar_toolkit/archive/indexing.py
src/seestar_toolkit/archive/models.py
src/seestar_toolkit/archive/orchestration.py
src/seestar_toolkit/archive/orchestration_models.py
src/seestar_toolkit/archive/planning.py
src/seestar_toolkit/archive/planning_models.py
src/seestar_toolkit/archive/reconstruction.py
src/seestar_toolkit/archive/reconstruction_models.py
src/seestar_toolkit/archive/target_comparison.py
src/seestar_toolkit/batch.py
src/seestar_toolkit/cli.py
src/seestar_toolkit/conversion.py
src/seestar_toolkit/fits/__init__.py
src/seestar_toolkit/fits/exceptions.py
src/seestar_toolkit/fits/inspector.py
src/seestar_toolkit/fits/models.py
src/seestar_toolkit/fits/reader.py
src/seestar_toolkit/imaging/__init__.py
src/seestar_toolkit/imaging/demosaic.py
src/seestar_toolkit/imaging/rgb.py
src/seestar_toolkit/models.py
src/seestar_toolkit/tiff/__init__.py
src/seestar_toolkit/tiff/exceptions.py
src/seestar_toolkit/tiff/writer.py
```

## Final Git status

```text
 M docs/development/CHANGELOG.md
 M pyproject.toml
 M src/seestar_toolkit/__init__.py
 M tests/unit/test_package.py
?? MANIFEST.in
?? docs/development/PACKAGING.md
?? docs/development/change_documents/STAGE_9/STAGE_9.1c.md
?? docs/development/change_documents/STAGE_9/STAGE_9.1c_REPORT.md
```

## Downstream work and closure recommendation

No unresolved Stage 9.1c blocker. CI/distribution automation belongs to 9.1d;
candidate install proof to 9.2a; installed functional/storage validation to
9.2b; final Markdown/PDF documentation to 9.3; privacy/publication and the
two 9.4b gates remain outstanding. This PASS is not release readiness.

No GitHub repository, remote, authentication, push, CI or publication action
occurred. No PyPI upload/release, release ZIP, final guides, PDFs or release
checksum pipeline was created. No unrelated production refactor occurred.
No staging or commit was performed; HEAD remains the starting commit.

**STAGE COMPLETE — Stage 9.1c: PASS recommendation, 68/68 criteria.**

Await formal closure review before user commit. After an approved commit, record
its actual ID/message in the detailed changelog and leave that update pending
for the following stage. Stage 9.1d has not been started.
