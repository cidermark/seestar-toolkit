# Stage 9.2a — Clean installation and Python compatibility report

## A. Decision

**FAIL for formal closure; complete local technical validation PASS.**
All initial and final wheel/sdist combinations passed. Evidence establishes
Python 3.11–3.14 inclusive for v1.1.0 on the existing macOS arm64 platform
policy. Stage 9.2a remains STARTED pending independent review, approved user
commit, post-commit state and green GitHub Actions for changed metadata.
No later stage has begun.

## B. Files changed

| File | Reason |
| --- | --- |
| `pyproject.toml` | Bound Requires-Python to `>=3.11,<3.15`; add 3.11/3.12/3.13/3.14 classifiers and update explanatory comment. |
| `tools/validate_clean_install.py` | Small explicit-interpreter/artifact validator; separate disposable environments, real conversion, dependency/isolation evidence and cleanup. |
| `tools/validate_distribution.py` | Check final bounded Python metadata independent of specifier ordering; verify classifiers match source metadata. |
| `tools/check_formatting.py` | Add the new validator to the existing formatting scope. |
| `tests/unit/test_distribution_validation.py` | Update metadata fixture to final support range; add regression rejection of an unbounded range; preserve existing cases. |
| `docs/development/PACKAGING.md` | Validated Python policy, discovery/reproduction commands, Homebrew caveats, cleanup and CI gates. |
| `docs/development/PROJECT_Notes.md` | Reflect formal 9.1d completion and current 9.2a support decision/closure gates. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2a.md` | User-supplied untracked specification; only trailing Markdown spaces removed to satisfy incremental whitespace checks. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2a_EVIDENCE.json` | Full interpreter provenance, all sixteen initial/final outcomes, dependencies, module paths and cleanup flags. |
| `docs/development/change_documents/STAGE_9/STAGE_9.2a_REPORT.md` | This A–K report and individual 137-criterion assessment. |

No production code or fixture changed. The pending development CHANGELOG and
Stage 9.1d report are byte-identical to their starting state. Version remains
1.1.0. No commit or stage operation was performed.

## C. Interpreter provenance

Discovery preceded downloads: PATH/versioned commands, Homebrew opt paths,
`pyenv versions --bare` (empty), and the framework installation location
(absent) were checked. No candidate 3.11/3.12 was found. Generic python3
selected 3.14.7; direct executable/version/architecture checks were required.

| Candidate | Exact version | Executable used | Architecture | macOS | Source | Wheel | Sdist |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3.11 | 3.11.9 | `/tmp/seestar-stage92a-python/cpython-3.11.9-macos-aarch64-none/bin/python3.11` | arm64 | 26.5.2 | Astral python-build-standalone via uv 0.8.22 | PASS | PASS |
| 3.12 | 3.12.10 | `/tmp/seestar-stage92a-python/cpython-3.12.10-macos-aarch64-none/bin/python3.12` | arm64 | 26.5.2 | Astral python-build-standalone via uv 0.8.22 | PASS | PASS |
| 3.13 | 3.13.15 | `/opt/homebrew/opt/python@3.13/bin/python3.13` | arm64 | 26.5.2 | Homebrew | PASS | PASS |
| 3.14 | 3.14.7 | `/opt/homebrew/opt/python@3.14/bin/python3.14` | arm64 | 26.5.2 | Homebrew | PASS | PASS |

Structured evidence records resolved executable paths, compiler/build strings
and executable fingerprints. The local macOS result is 26.5.2, native arm64;
Homebrew prefix is `/opt/homebrew`, with installed formula versions 3.13.15
and 3.14.7. No Rosetta, Intel, Linux or Windows evidence is claimed.

Missing interpreters were obtained using pinned uv 0.8.22 from PyPI in a
temporary tooling venv, with `uv --no-config --cache-dir
/tmp/seestar-stage92a-cache python install --install-dir
/tmp/seestar-stage92a-python --no-bin 3.11.9 3.12.10`. uv's pinned catalogue
selects Astral python-build-standalone builds. Both downloaded exact versions
and arm64 architecture were checked before venv creation. No Apple Python,
Homebrew formula, shell startup file, default interpreter or PATH link changed.
See [uv's upstream interpreter documentation](https://docs.astral.sh/uv/guides/install-python/).

Homebrew Python remains the recommended later user-install route; the temporary
standalone builds are validation tooling, not a new installer policy. Older
lines may require versioned Homebrew formulae, but those formulae were not
installed/tested here. `which python3` alone cannot prove version or architecture;
record both command resolution and interpreter-reported values. This stage
neither qualifies every Apple-supported macOS release nor changes that policy.

## D. Wheel clean-install matrix

Every row below used a NEW candidate-created venv, no inherited site packages,
no editable installation and no development venv for runtime proof. Normal
pip installation requested the built artifact with no extras. The orchestrator
was separate tooling only. Runtime work occurred in a temporary outside-source
directory; PYTHONPATH/PYTHONHOME were removed, user site disabled and Python
entry points used `-I`. The actual environment paths are retained in the JSON.
All CLI and module version results were exactly `seestar-toolkit 1.1.0`.

| Python | Initial install | Final install / pip check | CLI / module version | Help | Runtime separation | Real conversion | Final imported module |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3.11.9 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-d91tqlpi/venv/lib/python3.11/site-packages/seestar_toolkit/__init__.py` |
| 3.12.10 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-gqtlixi9/venv/lib/python3.12/site-packages/seestar_toolkit/__init__.py` |
| 3.13.15 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-wq085p88/venv/lib/python3.13/site-packages/seestar_toolkit/__init__.py` |
| 3.14.7 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-tw6n6k2t/venv/lib/python3.14/site-packages/seestar_toolkit/__init__.py` |

## E. Sdist clean-install matrix

A SECOND new venv was used per candidate, with normal pip build isolation
and no wheel-environment reuse. The same isolation, help, dependency, version
and real-conversion checks applied. No build-isolation bypass or pip upgrade
was needed. Final rows use rebuilt artifacts after metadata finalisation.

| Python | Initial build/install | Final build/install / pip check | CLI / module version | Help | Runtime separation | Real conversion | Final imported module |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3.11.9 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-qck2shea/venv/lib/python3.11/site-packages/seestar_toolkit/__init__.py` |
| 3.12.10 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-v138v_wk/venv/lib/python3.12/site-packages/seestar_toolkit/__init__.py` |
| 3.13.15 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-9h_w298_/venv/lib/python3.13/site-packages/seestar_toolkit/__init__.py` |
| 3.14.7 | PASS | PASS / PASS | 1.1.0 / 1.1.0 | PASS | PASS | PASS | `/private/tmp/seestar-clean-zh65ghow/venv/lib/python3.14/site-packages/seestar_toolkit/__init__.py` |

Every imported module resolved beneath its own temporary venv/site-packages.
No import from repository src was used. Environments, staged inputs/artifacts
and TIFFs were removed after evidence capture; JSON records each cleanup.

Actual installed dependency sets for every combination are in the JSON.
All four lines used Astropy 8.0.1, headless OpenCV 5.0.0.93, pyerfa 2.0.1.5,
PyYAML 6.0.3, packaging 26.3 and astropy-iers-data 0.2026.9.7.0.56.14.
Python 3.11 resolved NumPy 2.4.6/tifffile 2026.3.3; the others resolved NumPy
2.5.3/tifffile 2026.9.9. All satisfy unchanged runtime constraints.
pytest, Ruff, build, reportlab, weasyprint and fpdf were absent. Python 3.11's
venv seeded setuptools 65.5.0 and pip 24.0; that seed is interpreter packaging
tooling, not a Toolkit runtime dependency. Sdist builds obtained the declared
setuptools backend through normal isolated build dependencies. No undeclared
development dependency was required for conversion.

## F. Fixture/output evidence

Approved real fixture: `tests/data/seestar/light.fit` (4,152,960 bytes), verified
against `tests/data/public_fixtures.json` before validation. Each runtime uses
its own temporary `input.fit` copy, so no iCloud-specific, NAS, external-drive
or private Stage 8 path participates in conversion. All copied input bytes
remain unchanged after execution.

The installed `seestar-toolkit convert input.fit output.tiff` command produced
RGB uint16 TIFF shape `(1920, 1080, 3)`, 16-bit samples and RGB photometric
metadata. Every output pixel equalled an independent `cv2.cvtColor` GRBG
conversion (`COLOR_BayerGB2RGB`) of the FITS array. The oracle does not call
the Toolkit conversion helper. Output TIFFs and temporary fixture copies
were removed with their environments. Public evidence includes only generic
`/tmp`/`/private/tmp` and `/opt/homebrew` paths, not personal capture paths.

## G. Candidate failures/remediation

No candidate installation, dependency, build, isolation or conversion failed:
8/8 initial and 8/8 final combinations PASS. Discovery initially found no
3.11/3.12 interpreter; obtaining the intended versions in temporary directories
resolved that availability limitation, without substituting a different line.
The metadata change was evidence-driven finalisation, not a workaround for a
failed candidate. Future or genuine failures must remain in JSON/report evidence;
the validator records failed steps/output and still removes the environment.

A final cleanup audit initially asserted that the optional uv cache directory
existed; uv had not created it. This was a cleanup-method assertion failure,
not an interpreter/install/runtime failure. Cleanup was corrected to accept
an already-absent optional directory, and all acquisition/tooling/artifact
directories were verified absent. No candidate result was relabelled.

The supplied specification's five Markdown hard-break endings were trimmed
before submission to avoid repeating the 9.1d whitespace issue. No actual
9.2a CI failure is claimed or hidden. Stage 9.1d's original Run 1 FAIL →
remediation → Run 2 PASS record remains byte-for-byte unchanged.

## H. Final Python support decision

**Evidence-based v1.1.0 Python support range: 3.11 through 3.14 inclusive.**
All four exact candidate interpreters satisfy Stage 9.1d CI/build evidence
AND Stage 9.2a real clean wheel/sdist runtime proof on native macOS arm64.
No other Python line or platform is claimed. Exact patches tested are listed;
minor-line support is not a claim that every patch was separately tested.

Metadata changed from `>=3.11` to `>=3.11,<3.15`, with four matching version
classifiers. Unbounded metadata would have allowed unvalidated 3.15+ despite
the specification's support boundary. No runtime dependency bound changed.
Both artifacts were rebuilt and re-inspected, then all eight clean-install
checks repeated in NEW environments. Runtime code was unchanged. This support
decision is development evidence for Stage review; final user prose remains
with Stage 9.3. Post-commit CI must be green before formal 9.2a closure.

## I. Project validation

| Check | Exact result |
| --- | --- |
| Development-environment pytest | 330 passed in 11.96s (Python 3.13.15). |
| Ruff | All checks passed. |
| Configured formatting | 37 files already formatted. |
| Incremental `git diff --check` | PASS, including separate new-file whitespace checks. |
| Public-fixture/history validation | PASS: 10 reviewed fixtures; clean public root; no oversized blobs. |
| Initial wheel/sdist build + inspection | PASS: 39-member wheel, 46-member sdist. |
| Final wheel/sdist build + inspection | PASS: bounded Python metadata, four classifiers, name/version/author/MIT/README/modules/runtime requirements. |
| Initial clean runtime matrix | 8/8 PASS. |
| Rebuilt final clean runtime matrix | 8/8 PASS. |

Artifacts: `seestar_toolkit-1.1.0-py3-none-any.whl` and
`seestar_toolkit-1.1.0.tar.gz`. Normal `python -m build` built the wheel from
the sdist. Build frontend 1.6.1 was in temporary tooling, not a runtime proof
environment. Initial and final archives passed the existing inspector;
final Requires-Python/classifiers were also checked. Required modules and
console entry points are present; no FITS, private paths, Git data or caches
are packaged. Build/interpreter download outputs remained outside Git. Temporary standalone
interpreters, tooling venv, optional cache and both artifact directories were
removed after evidence capture; only public review evidence is retained.

The existing suite grew from 329 to 330 only by adding a metadata regression
case rejecting an unbounded Python range. Existing cases were retained and
updated to the final metadata contract. No tests or CI checks were weakened.
The unchanged CI workflow will exercise the new metadata on the eventual
approved commit; no green result for that uncommitted change is invented.

## J. Scope exclusions

No commit, tag, GitHub Release, PyPI publishing, public visibility change,
final release ZIP/checksum, history rewrite or later-stage work. Repository
privacy is retained from the established PRIVATE starting context; no remote
settings operation occurred. v1.1.0 remains unreleased. Pre-public history was
not merged or recreated. Stage 9.1d remains formally complete at 1771b9f;
Stage 9.2b/9.3/9.4 did not begin. Pending CHANGELOG preserved.

## K. Closure criteria

The 137 criteria below are assessed individually. Local technical validation
passes; formal closure does not. Evidence files are prepared for review but
cannot be described as committed while Codex is prohibited from committing.

**Unsatisfied/pending: 107, 120, 133, 134, 135, 136, 137.** These require
committed evidence, independent closure review/approval, the user commit,
post-commit state and green post-commit CI. No candidate or runtime failure
remains. Criterion 137's no-premature-COMPLETE safeguard is obeyed; the formal
completion condition is still pending. Stage 9.2a remains STARTED.

| # | Criterion | Status | Evidence / remaining work |
| ---: | --- | --- | --- |
| 1 | Work begins from `main` at or after `1771b9f`. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 2 | Stage 9.1d remains formally complete. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 3 | Pending Stage 9.1d CHANGELOG modification is preserved. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 4 | v1.1.0 remains unreleased. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 5 | Repository remains private. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 6 | Stage 9.2b work is not begun. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 7 | Stage 9.3 work is not begun. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 8 | Stage 9.4 work is not begun. | PASS | main starts at 1771b9f; 9.1d complete; pending CHANGELOG preserved; no publication/visibility/later-stage action. |
| 9 | Python 3.11 candidate is investigated. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 10 | Python 3.12 candidate is investigated. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 11 | Python 3.13 candidate is investigated. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 12 | Python 3.14 candidate is investigated. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 13 | Exact patch version is recorded for every tested interpreter. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 14 | Executable path is recorded. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 15 | Architecture is recorded. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 16 | macOS version is recorded. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 17 | Interpreter source/provenance is recorded where determinable. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 18 | Apple system Python is not modified. | PASS | Discovery and structured provenance record exact four versions, executable paths, sources, macOS 26.5.2 and arm64; system Python unchanged. |
| 19 | Fresh temporary venv used for each wheel candidate. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 20 | Separate fresh temporary venv used for each sdist candidate. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 21 | Existing development venv is not used for runtime proof. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 22 | No editable installation is used. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 23 | `PYTHONPATH` does not provide repository imports. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 24 | Runtime commands run outside repo root where practical. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 25 | Site packages are not inherited. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 26 | Temporary environments are removed after evidence capture. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 27 | Validation does not depend on private local datasets. | PASS | Separate candidate-created venv for every artifact/phase; no editable/user-site/source imports; all environments and outputs removed. |
| 28 | Clean wheel installation succeeds or failure is explicitly preserved. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 29 | `pip check` succeeds if installation succeeds. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 30 | CLI version reports 1.1.0. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 31 | Module version reports 1.1.0. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 32 | Module resolves from temporary site-packages. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 33 | Basic CLI invocation succeeds. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 34 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 35 | Runtime dependency separation is verified. | PASS | Python 3.11.9 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 36 | Clean wheel installation succeeds or failure is explicitly preserved. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 37 | `pip check` succeeds if installation succeeds. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 38 | CLI version reports 1.1.0. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 39 | Module version reports 1.1.0. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 40 | Module resolves from temporary site-packages. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 41 | Basic CLI invocation succeeds. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 42 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 43 | Runtime dependency separation is verified. | PASS | Python 3.12.10 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 44 | Clean wheel installation succeeds or failure is explicitly preserved. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 45 | `pip check` succeeds if installation succeeds. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 46 | CLI version reports 1.1.0. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 47 | Module version reports 1.1.0. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 48 | Module resolves from temporary site-packages. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 49 | Basic CLI invocation succeeds. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 50 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 51 | Runtime dependency separation is verified. | PASS | Python 3.13.15 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 52 | Clean wheel installation succeeds or failure is explicitly preserved. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 53 | `pip check` succeeds if installation succeeds. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 54 | CLI version reports 1.1.0. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 55 | Module version reports 1.1.0. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 56 | Module resolves from temporary site-packages. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 57 | Basic CLI invocation succeeds. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 58 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 59 | Runtime dependency separation is verified. | PASS | Python 3.14.7 wheel: initial/final PASS; pip check, versions, site-packages path, help, independent real conversion and dependency checks recorded. |
| 60 | Clean sdist installation/build succeeds or failure is explicitly preserved. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 61 | `pip check` succeeds if installation succeeds. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 62 | Both version entry points report 1.1.0. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 63 | Module resolves from temporary site-packages. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 64 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 65 | Runtime dependency separation is verified. | PASS | Python 3.11.9 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 66 | Clean sdist installation/build succeeds or failure is explicitly preserved. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 67 | `pip check` succeeds if installation succeeds. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 68 | Both version entry points report 1.1.0. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 69 | Module resolves from temporary site-packages. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 70 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 71 | Runtime dependency separation is verified. | PASS | Python 3.12.10 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 72 | Clean sdist installation/build succeeds or failure is explicitly preserved. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 73 | `pip check` succeeds if installation succeeds. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 74 | Both version entry points report 1.1.0. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 75 | Module resolves from temporary site-packages. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 76 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 77 | Runtime dependency separation is verified. | PASS | Python 3.13.15 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 78 | Clean sdist installation/build succeeds or failure is explicitly preserved. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 79 | `pip check` succeeds if installation succeeds. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 80 | Both version entry points report 1.1.0. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 81 | Module resolves from temporary site-packages. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 82 | Real FITS-to-TIFF conversion succeeds. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 83 | Runtime dependency separation is verified. | PASS | Python 3.14.7 sdist: separate initial/final environments PASS; normal isolated build, pip check, entry points/imports/conversion/dependencies verified. |
| 84 | pytest is not required by runtime installation. | PASS | All sixteen records show runtime-only conversion and no pytest/Ruff/PDF/frontend requirement; actual packages and metadata recorded. |
| 85 | Ruff is not required by runtime installation. | PASS | All sixteen records show runtime-only conversion and no pytest/Ruff/PDF/frontend requirement; actual packages and metadata recorded. |
| 86 | PDF-generation tools are not required by runtime installation. | PASS | All sixteen records show runtime-only conversion and no pytest/Ruff/PDF/frontend requirement; actual packages and metadata recorded. |
| 87 | No undeclared dev dependency is required for conversion. | PASS | All sixteen records show runtime-only conversion and no pytest/Ruff/PDF/frontend requirement; actual packages and metadata recorded. |
| 88 | Runtime dependency metadata matches observed requirements. | PASS | All sixteen records show runtime-only conversion and no pytest/Ruff/PDF/frontend requirement; actual packages and metadata recorded. |
| 89 | Only an approved public-safe FITS fixture is used. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 90 | Fixture used is recorded. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 91 | Temporary TIFF output is outside tracked repo paths. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 92 | Temporary output is removed. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 93 | No private Stage 8 data is used. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 94 | No private path is embedded in committed evidence. | PASS | Only approved light.fit copied into temporary outside-source directories; exact conversion pixels checked; copies/TIFFs removed; no private data. |
| 95 | Evidence for all four candidates is evaluated. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 96 | Final supported Python range is explicitly decided. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 97 | Final support range is based on evidence, not preference. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 98 | Any failed candidate remains documented. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 99 | No unvalidated Python version is claimed. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 100 | Package Python metadata matches the final supported range. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 101 | If metadata changes, wheel and sdist are rebuilt. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 102 | If metadata changes, final supported candidates are revalidated. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 103 | User-facing support claims remain deferred to Stage 9.3. | PASS | All four lines pass both stages; support 3.11–3.14; metadata bounded/classified; rebuilt and revalidated 8/8; user guide deferred. |
| 104 | PACKAGING.md is updated where needed. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 105 | PROJECT_Notes.md is updated where needed. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 106 | Stage 9.2a completion report is created. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 107 | Interpreter provenance is recorded in committed development evidence. | PENDING | Provenance is in review-ready development files; user commit is prohibited until independent approval. |
| 108 | Final Python support decision is recorded in development evidence. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 109 | Historical validation failures are preserved. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 110 | Stage 9.1d CI evidence is not rewritten. | PASS | Packaging/notes/report/JSON document provenance and support; original 9.1d failure/CI report preserved. |
| 111 | Full pytest suite passes. | PASS | Development pytest: 330 passed in 11.96s. |
| 112 | Ruff passes. | PASS | Ruff: All checks passed. |
| 113 | Configured formatting passes. | PASS | Applicable formatting: 37 files already formatted. |
| 114 | Incremental `git diff --check` passes. | PASS | git diff --check and separate new-file whitespace checks pass. |
| 115 | Public-fixture/history validation passes. | PASS | 10 reviewed fixtures; clean public root; no oversized blobs. |
| 116 | Wheel/sdist build validation passes. | PASS | Initial and rebuilt final wheel/sdist build and archive inspections pass; all clean install combinations pass. |
| 117 | No unexpected generated artifacts are tracked. | PASS | Only expected 9.2a changes plus preserved pending CHANGELOG; generated outputs kept outside Git; public evidence scanned. |
| 118 | No unexpected private files are tracked. | PASS | Only expected 9.2a changes plus preserved pending CHANGELOG; generated outputs kept outside Git; public evidence scanned. |
| 119 | Git status contains only expected Stage 9.2a changes before approval. | PASS | Only expected 9.2a changes plus preserved pending CHANGELOG; generated outputs kept outside Git; public evidence scanned. |
| 120 | Any code/metadata change affecting CI receives appropriate CI revalidation before closure. | PENDING | Metadata affects CI; approved user commit must receive green Actions before closure. No commit made here. |
| 121 | No PyPI publication occurs. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 122 | No GitHub Release is created. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 123 | No release tag is created. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 124 | Repository is not made public. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 125 | No final release ZIP is created. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 126 | No Stage 9.2b implementation begins. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 127 | No Stage 9.3 implementation begins. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 128 | No Stage 9.4 implementation begins. | PASS | No publishing/release/tag/public switch/final ZIP or Stage 9.2b/9.3/9.4 action. |
| 129 | Codex returns a complete closure report. | PASS | Complete A–K report and structured sixteen-combination evidence provided. |
| 130 | Every criterion is individually assessed. | PASS | All 137 numbered criteria individually assessed in this table. |
| 131 | Unsatisfied criteria are explicitly listed. | PASS | All outstanding criteria explicitly listed; no unavailable/failing candidate hidden. |
| 132 | Codex does not commit. | PASS | No commit created by Codex. |
| 133 | ChatGPT independently reviews closure evidence. | PENDING | Await independent Stage-review audit and explicit closure approval. |
| 134 | User commits only after explicit approval. | PENDING | Await user commit only after explicit approval; Codex has not committed. |
| 135 | Post-commit state is verified. | PENDING | Post-commit state must be verified after the approved user commit exists. |
| 136 | Any commit affecting CI receives a green post-commit GitHub Actions result before Stage 9.2a is marked COMPLETE. | PENDING | Green post-commit Actions required for changed metadata; cannot run uncommitted snapshot on GitHub. |
| 137 | Stage 9.2a is not marked COMPLETE until all applicable criteria and post-commit checks pass. | PENDING | Stage remains STARTED; all applicable review/commit/CI gates must pass before COMPLETE. |
