# Stage 9.1d — Implementation and closure review

## Final reassessment following CI Run 2

**Decision: PASS — CI Run 2, final local validation and all 112 criterion
checks are satisfied.** Stage 9.1d remains
STARTED pending final Stage-review closure. The initial report and Run 1
record below are retained as historical evidence, not current status.

### Files changed

Only `docs/development/change_documents/STAGE_9/STAGE_9.1d_REPORT.md` changed
in this follow-up: reviewed Run 2 evidence, final local checks and an individual
reassessment of all 112 criteria. The existing pending
`docs/development/CHANGELOG.md` modification is preserved byte-for-byte.
Production code, tests, fixtures, CI, packaging metadata and validators are
unchanged. No commit was created.

### CI implementation

Unchanged workflow: **Distribution validation**, pushes to main, pull requests
targeting main and manual dispatch. Four candidate jobs on `macos-15`, with
Darwin/arm64 verification; Python 3.11–3.14, `fail-fast: false`, no failure
suppression. Permissions remain `contents: read`, no persisted checkout
credentials, no additional secrets and no explicit caching. No publication,
release, tag, version or CHANGELOG mutation steps exist.

### GitHub Actions evidence and Python candidate findings

Evidence source: CI Run 2 results independently reviewed by the Stage review
and supplied for this report. These are accepted as actual Actions evidence,
not represented as logs downloaded by Codex.

| Candidate/interpreter | Runner | Pytest | Matrix job result |
| --- | --- | --- | --- |
| 3.11 / 3.11.9 | macOS arm64 | 329 passed | PASS |
| 3.12 / 3.12.10 | macOS arm64 | 329 passed | PASS |
| 3.13 / 3.13.15 | macOS arm64 | 329 passed | PASS |
| 3.14 / 3.14.7 | macOS arm64 | 329 passed | PASS |

All four jobs completed successfully. Reviewed results also establish:

- Public fixture/history check: 10 reviewed fixtures, clean public root,
  no oversized blobs — PASS.
- Ruff — PASS on all four jobs.
- Applicable formatting — PASS, 36 files already formatted.
- Incremental whitespace — PASS on all four jobs.
- Wheel and sdist build/inspection — PASS.
- Isolated wheel and sdist runtime validation — PASS.
- Installed entry points — `seestar-toolkit 1.1.0`.
- Temporary build outputs removed.

**Preserved sequence: CI Run 1 FAIL → five specification whitespace violations
remediated → CI Run 2 PASS.** Run 1 remains a genuine failure; its complete
existing record is preserved below. All four candidates were attempted in
Run 1. Run 2 success does not relabel Run 1 or hide its remediation.
Python 3.11–3.14 remain candidates only; final support is a Stage 9.2a decision.

Run 2 authoritative identifier, confirmed by Stage review:
`a3b0e9915d8b7d87c43b1e9b202f96310720afcb` —
`Stage 9.1d: fix CI whitespace validation`. Run URL/ID is not supplied /
unavailable; the triggering SHA is used as the authoritative identifier.
This matches locally verified main and origin/main. Implementation commit
`bfb947f` precedes the whitespace fix, descending from public root `c294ffd`.

Stage review confirms that the GitHub repository remains **PRIVATE**. Stage
review inspected the uploaded CI Run 2 log archive and found no private
filesystem paths, credentials, private FITS metadata, user-specific
configuration or other private data exposed in the logs. These are explicit
review attestations; Codex's read-only `gh` attempt remained unauthenticated
and is not represented as an independent remote inspection.

### Build validation

Final local `python tools/validate_distribution.py` rebuilt and inspected:

- `seestar_toolkit-1.1.0-py3-none-any.whl` — 39 allowed members.
- `seestar_toolkit-1.1.0.tar.gz` — 46 allowed members.

The isolated source copy contains packaging inputs and Python modules only;
the wheel is built from the sdist. Checks verify name, version 1.1.0, Mark
Wymer author metadata, MIT expression/license, README, `Requires-Python: >=3.11`,
all package modules, console entry point and the declared runtime requirements.
Dev/build extras remain separate. Archive allowlists and content scanning
exclude FITS, private datasets, Git metadata, caches and private path/key
markers. Temporary validation outputs are removed; none is a release asset.

### Installed-artifact validation

Final local wheel and sdist checks each use a separate clean temporary venv,
no extras, outside-source working directory, cleared PYTHONPATH/PYTHONHOME,
Python `-I` and no user site. `pip check`, both version entry points and an
exact linear RGB FITS-to-TIFF conversion pass. Import location is verified
beneath each venv at
`lib/python3.13/site-packages/seestar_toolkit/__init__.py`.
Both entry points report `seestar-toolkit 1.1.0`. pytest, Ruff, build and PDF
tooling are absent from runtime environments. Sdist smoke passes with no
observed limitation. Run 2 establishes these checks across all four candidates.

### Final local test/quality

Environment: Python 3.13.15, macOS arm64, Ruff 0.16.7.

| Command/check | Result |
| --- | --- |
| `python -m pytest` | PASS: 329 passed in 11.23s. |
| `python -m ruff check .` | PASS: All checks passed. |
| `python tools/check_formatting.py` | PASS: 36 files already formatted. |
| `python tools/check_public_inputs.py` | PASS: 10 reviewed fixtures; clean public root; no oversized blobs. |
| `git diff --check` | PASS: final working-tree diff. |
| `git diff --check c294ffd HEAD` | PASS: committed incremental public-stage changes. |
| `python tools/validate_distribution.py` | PASS: build, inspection, isolated wheel/sdist installs and runtime smoke. |
| Preservation checks | PASS: existing CHANGELOG and complete Run 1 record unchanged. |

Local final validation does not replace or erase either CI run. No new test
skip, candidate removal, dependency change or validation workaround was made.

### Privacy/public checks and scope exclusions

Ten approved fixtures remain unchanged, including the 5,760-byte synthetic
mosaic. The public-history checker passes against current HEAD. Public main
has only the clean bootstrap root; no oversized blob is reachable. Local
master remains present and separate. No LFS, private dataset or generated
artifact was introduced. Distribution checks pass for private-path exclusion;
Stage review confirms PRIVATE visibility and completed clean CI-log review.

No commit, push, tag, GitHub Release, PyPI publication, public switch or history
rewrite was performed. No backup was intentionally deleted. v1.1.0 remains
unreleased. Stage 9.2 (and later stages) have not begun. Final status contains
only this report and the pre-existing pending development CHANGELOG edit.

### Current individual closure assessment

The following is the authoritative current reassessment, superseding the
historical table later in this file. PASS means verified local implementation
or explicitly supplied Stage-review CI evidence. No criterion remains pending on the supplied evidence; formal approval
is a separate Stage-review action.

**Unsatisfied closure criteria: none.** All 112 checks pass on the combined
local and independently reviewed CI evidence. Criterion 112 is satisfied as
a safeguard: the existing implementation/fix commits are recorded, current
post-commit status is verified, and no premature COMPLETE status is assigned.
The expected working-tree changes are this report and the preserved pending
CHANGELOG. The formal close under specification §25 still requires explicit
Stage-review approval; this report does not itself provide that approval or
begin Stage 9.2. No new implementation commit is required or created here.

| # | Criterion | Status | Current evidence / remaining work |
| ---: | --- | --- | --- |
| 1 | Work is on `main`. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 2 | `main` descends from `c294ffd`. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 3 | Old `master` is not merged into `main`. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 4 | The 272,923,200-byte FITS blob is not reachable from `main`. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 5 | No tracked public-history blob exceeds 100 MiB. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 6 | Repository remains private. | PASS | Stage review explicitly confirms GitHub repository remains PRIVATE; no visibility change performed. |
| 7 | No normal 9.1d history rewrite occurs. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 8 | Historical documents are not retroactively rewritten solely to replace old commit IDs. | PASS | main at a3b0e99 descends from c294ffd; public-input/history check passes; no history changes. |
| 9 | GitHub Actions workflow exists. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 10 | CI runs on pushes to `main`. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 11 | CI runs on PRs targeting `main`. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 12 | Workflow permissions are least-privilege. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 13 | Normal CI needs no personal secrets. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 14 | CI does not publish packages. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 15 | CI does not create releases. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 16 | CI does not create tags. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 17 | CI does not modify versioning. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 18 | CI does not modify CHANGELOGs. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 19 | CI does not require private datasets. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 20 | CI uses only repository-safe fixtures. | PASS | Unchanged workflow inspected; reviewed Run 2 passes; main triggers/read-only/no publishing or private inputs. |
| 21 | Python 3.11 is attempted where available. | PASS | Reviewed Run 2: candidate attempted on macOS arm64; 329 tests and complete matrix job PASS. |
| 22 | Python 3.12 is attempted where available. | PASS | Reviewed Run 2: candidate attempted on macOS arm64; 329 tests and complete matrix job PASS. |
| 23 | Python 3.13 is attempted where available. | PASS | Reviewed Run 2: candidate attempted on macOS arm64; 329 tests and complete matrix job PASS. |
| 24 | Python 3.14 is attempted where available. | PASS | Reviewed Run 2: candidate attempted on macOS arm64; 329 tests and complete matrix job PASS. |
| 25 | Versions remain candidates, not final support claims. | PASS | All candidates retained; Run 1 FAIL and remediation retained; Run 2 PASS; final support deferred. |
| 26 | Unavailable candidates are recorded. | PASS | All candidates retained; Run 1 FAIL and remediation retained; Run 2 PASS; final support deferred. |
| 27 | Failing candidates are recorded. | PASS | All candidates retained; Run 1 FAIL and remediation retained; Run 2 PASS; final support deferred. |
| 28 | Failing candidates are not silently removed. | PASS | All candidates retained; Run 1 FAIL and remediation retained; Run 2 PASS; final support deferred. |
| 29 | Full pytest suite passes for applicable matrix entries. | PASS | 329 tests passed on each of 3.11.9, 3.12.10, 3.13.15 and 3.14.7 in reviewed Run 2. |
| 30 | Ruff passes. | PASS | Reviewed Run 2 passes all jobs; final local Ruff, 36-file formatting and whitespace pass. |
| 31 | Configured formatting passes. | PASS | Reviewed Run 2 passes all jobs; final local Ruff, 36-file formatting and whitespace pass. |
| 32 | Incremental `git diff --check` passes. | PASS | Reviewed Run 2 passes all jobs; final local Ruff, 36-file formatting and whitespace pass. |
| 33 | Coverage is not weakened merely for CI. | PASS | No tests, skips, matrix or validation behaviour changed in this follow-up. |
| 34 | New CI skips are justified. | PASS | No tests, skips, matrix or validation behaviour changed in this follow-up. |
| 35 | CI is reproducible from clean checkout. | PASS | Four successful clean Actions jobs plus isolated-source build/install validation. |
| 36 | Wheel build succeeds. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 37 | Sdist build succeeds. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 38 | Build uses repository source only. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 39 | Wheel filename/version are correct. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 40 | Sdist filename/version are correct. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 41 | Project-name metadata is correct. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 42 | Version metadata is `1.1.0`. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 43 | Author metadata is Mark Wymer. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 44 | MIT licensing metadata is appropriate. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 45 | Runtime dependency metadata matches Stage 9.1c intent. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 46 | Dev-only dependencies are not runtime dependencies. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 47 | Build outputs remain untracked. | PASS | Reviewed Run 2 and fresh local wheel/sdist build/metadata/runtime dependency checks PASS; temporary outputs removed. |
| 48 | Wheel contents are inspected. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 49 | Sdist contents are inspected. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 50 | Required package modules are present. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 51 | Console-script metadata is present. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 52 | Expected README/license metadata is present. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 53 | No private Stage 8 datasets are included. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 54 | No private local paths are included. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 55 | No `.git` data is included. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 56 | No accidental cache/temp files are included. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 57 | Superseded oversized Siril fixture is absent. | PASS | Wheel 39 members/sdist 46 members; strict allowlists, module/metadata/license and private-path inspection PASS. |
| 58 | Wheel installs in clean temporary environment. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 59 | Installed `seestar-toolkit --version` is `1.1.0`. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 60 | Installed `python -m seestar_toolkit --version` is `1.1.0`. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 61 | Console entry point works outside repository source tree. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 62 | Module entry point works outside repository source tree. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 63 | Imported package resolves from temporary environment/site-packages. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 64 | Installed package does not require pytest. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 65 | Installed package does not require Ruff. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 66 | Installed package does not require PDF tooling. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 67 | Sdist smoke validation succeeds where practical. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 68 | Any sdist limitation is documented. | PASS | Run 2 and fresh local independent wheel/sdist venv checks PASS: outside-source entry points, site-packages imports, runtime-only dependencies. |
| 69 | `tests/data/PRIVACY_REVIEW.md` remains present. | PASS | Public validator PASS: ten unchanged approved fixture hashes, reviewed synthetic mosaic, no oversized blob or LFS. |
| 70 | Synthetic Siril mosaic remains the reviewed small fixture. | PASS | Public validator PASS: ten unchanged approved fixture hashes, reviewed synthetic mosaic, no oversized blob or LFS. |
| 71 | Sanitised real FITS fixtures remain sanitised. | PASS | Public validator PASS: ten unchanged approved fixture hashes, reviewed synthetic mosaic, no oversized blob or LFS. |
| 72 | CI does not restore old identifying metadata. | PASS | Public validator PASS: ten unchanged approved fixture hashes, reviewed synthetic mosaic, no oversized blob or LFS. |
| 73 | CI logs expose no private fixture metadata/paths. | PASS | Stage review inspected Run 2 log archive: no private paths, credentials, FITS metadata, user configuration or private data. |
| 74 | No Git LFS dependency is introduced. | PASS | Public validator PASS: ten unchanged approved fixture hashes, reviewed synthetic mosaic, no oversized blob or LFS. |
| 75 | `PACKAGING.md` reflects implemented build/CI process where needed. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 76 | `PROJECT_Notes.md` reflects 9.1d status where needed. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 77 | `PUBLIC_HISTORY_BOOTSTRAP.md` remains accurate. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 78 | Historical Stage documents are preserved. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 79 | User Guide work is not prematurely moved into 9.1d. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 80 | Final Python support claims remain deferred to 9.2a. | PASS | Existing packaging/notes document implementation and defer closure/support to this report/review; bootstrap/history preserved. |
| 81 | At least one real GitHub Actions run occurs. | PASS | Stage review confirms real Run 1 FAIL and Run 2 PASS. |
| 82 | Triggering commit is recorded. | PASS | Stage review confirms Run 2 triggering SHA a3b0e9915d8b7d87c43b1e9b202f96310720afcb; URL unavailable. |
| 83 | Attempted Python matrix is recorded. | PASS | All four exact candidate interpreters recorded in current Run 2 table. |
| 84 | Runner OS is recorded. | PASS | macOS arm64 confirmed by Stage review; workflow specifies macos-15. |
| 85 | Job outcomes are recorded. | PASS | All four Run 2 matrix jobs PASS; Run 1 remains FAIL. |
| 86 | Pytest outcome is recorded. | PASS | 329 pytest tests passed on each of the four Run 2 jobs. |
| 87 | Ruff outcome is recorded. | PASS | Ruff passed on all four Run 2 jobs. |
| 88 | Formatting outcome is recorded. | PASS | Applicable formatting passed: 36 files already formatted. |
| 89 | Build outcome is recorded. | PASS | Run 2 wheel/sdist build and inspection PASS; fresh local repeat PASS. |
| 90 | Installed-artifact smoke outcome is recorded. | PASS | Run 2 isolated wheel/sdist smoke PASS; version entry points 1.1.0; fresh local repeat PASS. |
| 91 | Failure/remediation cycles remain visible. | PASS | Run 1 record retained byte-for-byte; whitespace-only remediation and Run 2 PASS explicitly sequenced. |
| 92 | Final applicable CI state required for closure is passing. | PASS | Stage review independently confirms all four Run 2 jobs completed successfully. |
| 93 | No PyPI publication. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 94 | No GitHub Release. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 95 | No release tag. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 96 | Repository stays private. | PASS | Stage review explicitly confirms GitHub repository remains PRIVATE; no visibility change performed. |
| 97 | Stage 9.2 not begun. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 98 | Stage 9.3 not begun. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 99 | Stage 9.4 not begun. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 100 | No automatic release workflow. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 101 | Pre-public `master` preserved through closure. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 102 | Private pre-public backup not intentionally deleted during 9.1d. | PASS | No publishing/tag/release/visibility/next-stage/history operations; master preserved; no backup intentionally deleted. |
| 103 | Final pytest passes. | PASS | Fresh final pytest: 329 passed in 11.23s. |
| 104 | Final Ruff passes. | PASS | Fresh final Ruff: All checks passed. |
| 105 | Final formatting passes. | PASS | Fresh final applicable formatting: 36 files already formatted. |
| 106 | Final incremental `git diff --check` passes. | PASS | Fresh final git diff --check and c294ffd-to-HEAD whitespace checks PASS. |
| 107 | Pre-commit `git status` contains only expected 9.1d changes. | PASS | Only report edit plus pre-existing pending CHANGELOG; no code/data/workflow or generated/private-file changes. |
| 108 | No unexpected generated artifacts are tracked. | PASS | Only report edit plus pre-existing pending CHANGELOG; no code/data/workflow or generated/private-file changes. |
| 109 | No unexpected private files are tracked. | PASS | Only report edit plus pre-existing pending CHANGELOG; no code/data/workflow or generated/private-file changes. |
| 110 | Codex provides a complete closure report mapped to these criteria. | PASS | All 112 criteria individually reassessed here with supplied evidence and remaining gaps identified. |
| 111 | Codex does not commit. | PASS | No commit created in this follow-up; existing implementation/fix commits are recorded accurately. |
| 112 | 9.1d is not marked COMPLETE until the approved commit exists and post-commit state is verified. | PASS | Existing implementation/fix commits and current post-commit status verified; STARTED safeguard retained pending explicit formal closure approval. |


## Historical implementation and Run 1 evidence — preserved

Everything below records the earlier implementation/remediation snapshots.
Statements such as “Actions has not run” or “a subsequent passing run is still
required” retain their historical meaning; current Run 2 evidence and the
individual assessment above supersede them without rewriting the failure.


> **CI Run 1 follow-up: FAIL; Stage 9.1d remains STARTED.** The sections below
> through the original closure assessment preserve the pre-run implementation
> report. Their statements that Actions had not run describe that earlier
> snapshot, not the current state. The CI Run 1 remediation record at the end
> supersedes those statements; Run 1 must never be reclassified as PASS.

**Decision: FAIL (formal closure); local implementation and validation PASS.**
Stage remains STARTED. Actual Actions evidence, reviewed commit/push and
post-commit verification are required before COMPLETE. This report is not
approval to start Stage 9.2a.

## Files changed

| File | Reason |
| --- | --- |
| `.github/workflows/ci.yml` | Four-candidate macOS arm64 distribution-validation workflow. |
| `tools/check_public_inputs.py` | Reviewed fixture hashes, public-root/large-object and tracked-artifact/LFS guards. |
| `tests/data/public_fixtures.json` | Size/SHA-256 inventory of all ten approved fixtures, matching the public baseline. |
| `tools/check_formatting.py` | Explicit existing formatting scope plus new validation code/tests. |
| `tools/validate_distribution.py` | Clean build, archive inspection and independent runtime-only wheel/sdist installations. |
| `tests/unit/test_distribution_validation.py` | Six positive/negative archive-inspection tests. |
| `docs/development/PACKAGING.md` | Implemented process, commands, limitations and candidate/platform policy. |
| `docs/development/PROJECT_Notes.md` | STARTED status, evidence gate and future-stage boundary. |
| `docs/development/change_documents/STAGE_9/STAGE_9.1d_REPORT.md` | This report, validation evidence and all 112 criteria. |

The supplied `STAGE_9.1d.md` was already untracked at start; it was read in full
and left byte-for-byte unchanged. Otherwise the starting tree was clean, on
`main` at `c294ffd917634a5d381cccc3ce3fd62a6fba4e89`, equal to the locally recorded
`origin/main`. No production code, pyproject metadata, existing tests or FITS
bytes changed. The CHANGELOG is intentionally untouched: specification §24
requires the final commit ID/date entry after the approved commit.

## CI implementation

Workflow: **Distribution validation**. Triggers: push to main, PR targeting
main, manual dispatch. One job expanded across candidate Python 3.11, 3.12,
3.13 and 3.14, `fail-fast: false`, no `continue-on-error`, 30-minute timeout.
Runner: `macos-15`, with explicit Darwin/arm64 assertion. This is not a final
macOS-version or Python-support claim. The
[official runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
identifies macOS arm64 standard runners for private repositories.

Checkout v6 (full public history, no persisted credentials), setup-python v6,
`contents: read`, no additional secrets, no explicit caching. Dependencies
come from `.[dev,build]`. Steps run public-input checks, full pytest, Ruff,
scoped formatting, incremental whitespace, isolated build/archive/runtime
validation, and a final tracked-file mutation check. No artifacts are uploaded
and no publish/release/version/tag operations exist. All candidates must pass;
runner or dependency failures must remain visible in the eventual Actions run.

## Build validation

PASS locally on Python 3.13.15 and 3.14.7, macOS 26.5.2 arm64:

- `seestar_toolkit-1.1.0-py3-none-any.whl`: 39 allowed members.
- `seestar_toolkit-1.1.0.tar.gz`: 46 allowed members.

The build starts from a fresh temporary copy of packaging inputs and package
Python files, with no Git directory, local egg-info, old builds or caches.
PEP 517 isolation produces an sdist and builds its wheel from that sdist.
Archives contain all 33 package modules and only approved ancillary files.
Inspection verifies `seestar-toolkit`, `1.1.0`, Mark Wymer, MIT license
expression and exact LICENSE, `Requires-Python: >=3.11`, exact README payload,
console entry point and runtime requirements:
`astropy>=7.0`, `numpy>=2.0`, `opencv-python-headless>=4.10`,
`tifffile>=2025.1.10`. The dev/build extras stay separate.
No FITS, private datasets, `.git`, caches, temporary files, private filesystem
paths or private-key markers occur in either artifact. Validation outputs
were temporary and deleted by the validator; no final release checksum was
created. The universal wheel tag describes Toolkit code, not platform support.

## Installed-artifact validation

Both artifacts independently installed into fresh pip-only venvs for each
available candidate. Installations requested no extras and passed `pip check`.
Processes ran in an outside-source temporary directory, with PYTHONPATH and
PYTHONHOME removed, user site disabled and Python `-I`. Actual package imports
resolved beneath each temporary venv:

- `lib/python3.13/site-packages/seestar_toolkit/__init__.py`
- `lib/python3.14/site-packages/seestar_toolkit/__init__.py`

Absolute random temporary prefixes are deliberately omitted from this public
report. The validator asserts the resolved path is beneath `sys.prefix`.
Both console and module entry points returned exactly `seestar-toolkit 1.1.0`;
metadata and imported `__version__` were `1.1.0`. Runtime imports of Astropy,
NumPy, OpenCV and tifffile succeeded; a generated linear RGB FITS converted to
TIFF with exact pixel equality. pytest, Ruff, build, reportlab, weasyprint and
fpdf were absent. The installed distribution inventory was only pip, Toolkit,
Astropy, astropy-iers-data, NumPy, headless OpenCV, packaging, pyerfa, PyYAML and
tifffile. Sdist smoke succeeded independently; no sdist limitation was observed.

## GitHub Actions evidence

**No run URL/ID or triggering implementation SHA exists.** Git cannot push
uncommitted workflow files. No commit/push/dispatch was attempted. Actual
Actions execution therefore requires the Stage-review-approved commit/push
step; this is a hard evidence gap, not a passing simulated run.

Read-only `gh repo view` could not authenticate (`gh` reports no login/token).
Repository privacy is stated by the user and unchanged by this work, but a
fresh remote privacy/default-branch check is unavailable. Locally recorded
`origin/main` equals the public baseline; no network fetch was represented as
fresh evidence. No personal token was requested or introduced.

| Candidate | Actual Actions result | Runner/build/test/smoke evidence |
| --- | --- | --- |
| 3.11 | NOT RUN | Awaiting approved commit/push; configured macos-15 arm64. |
| 3.12 | NOT RUN | Awaiting approved commit/push; configured macos-15 arm64. |
| 3.13 | NOT RUN | Local evidence below is not Actions evidence. |
| 3.14 | NOT RUN | Local evidence below is not Actions evidence. |

Failure/remediation record:

1. Initial sandbox dependency install failed on PyPI DNS access. Repeated with
   approved network access; declared dependencies installed successfully.
2. Source inspection caught that version output includes `seestar-toolkit`;
   the smoke expectation was corrected before executing artifact validation.
3. An auxiliary clean-snapshot command was initially launched outside the Git
   repository and failed before copying source. Rerun from the correct working
   directory succeeded. This did not alter implementation or test expectations.
4. The new-file whitespace wrapper initially treated Git's expected
   `--no-index` difference status 1 as an error. It was corrected to accept
   status 0/1 only with empty diagnostic output; every new file passed.
5. No candidate test/build failure was hidden or skipped. No actual Actions
   failure/remediation cycle exists yet; preserve any such cycle at review.

## Test/quality

| Check | Exact result |
| --- | --- |
| Python 3.13.15 final full pytest | 329 passed in 11.45s. |
| Python 3.14.7 full pytest | 329 passed in 75.98s (first fresh-environment run). |
| Python 3.13 clean exported-source snapshot | 329 passed in 11.84s, outside original checkout. |
| Ruff 0.16.7 on both candidates | All checks passed. |
| Configured formatting on both candidates | 36 files already formatted. |
| Public-input validator | 10 reviewed fixtures, clean public root, no oversized blob: PASS. |
| YAML structural validation | Expected triggers/matrix/read permission parsed: PASS. |
| Incremental `git diff --check` | PASS; new implementation files also checked with `--no-index --check`. |
| Build and installed artifacts | Both formats PASS on both available candidates. |

Initial 3.13 suite before the six new inspector checks: 323 passed in 69.11s.
The new tests exercise valid archives and rejection of an extra file, missing
module, wrong version, private path and wrong dependency. No existing test or
assertion was removed, weakened or skipped. The exported-source run used
`git archive HEAD` plus the new implementation files, without `.git`, generated
build inputs or workstation caches, and a fresh declared-dependency environment.
These are local 9.1d checks, not the final Stage 9.2a compatibility qualification.

Resolved versions included Astropy 8.0.1, NumPy 2.5.3, headless OpenCV 5.0.0.93,
tifffile 2026.9.9, build 1.6.1, pytest 9.1.1 and Ruff 0.16.7. Lower-bound metadata
was not narrowed or pinned to hide candidate-resolution issues.

## Python candidate findings

| Candidate | Local status | Reason |
| --- | --- | --- |
| 3.11 | UNAVAILABLE | No local 3.11 interpreter found in PATH/Homebrew locations; retained in Actions. |
| 3.12 | UNAVAILABLE | No local 3.12 interpreter found in PATH/Homebrew locations; retained in Actions. |
| 3.13 | PASS | Fresh declared environment, full tests/quality, wheel/sdist build and isolated runtime smoke. |
| 3.14 | PASS | Same checks on 3.14.7; no candidate-specific workaround. |

These remain candidates; no final support determination is made.

## Privacy/public checks

All ten current FITS files match the approved byte inventory, including the
5,760-byte synthetic Siril mosaic and nine sanitised real fixtures. No fixture
was changed. `PRIVACY_REVIEW.md` remains intact as historical pre-bootstrap
review evidence; `PUBLIC_HISTORY_BOOTSTRAP.md` explains its subsequent clean
publication boundary. The only root reachable from main is c294ffd; no
reachable blob exceeds 100 MiB (largest fixture: 49,775,040 bytes). The old
272,923,200-byte blob is not reachable from main. Private master remains
separate and was not read into the public build/history.

CI's source/tests/workflow have no real user paths or private dataset inputs;
the new rejection test uses only an explicitly fictional path marker.
Artifact allowlisting excludes development documents and all fixtures.
Historical documents retain their prior observations and are not newly
certified by this scoped check. No credentials or private headers are printed
by the validators; actual GitHub log review remains pending. No LFS dependency
or generated artifact is tracked. Final status contains only the nine intended
implementation files and the originally supplied untracked specification.

## Scope exclusions

No commit, push, tag, GitHub Release, PyPI publication, repository-public switch,
version change, release asset/checksum or automatic publishing configuration.
v1.1.0 remains unreleased. Stage 9.2/9.3/9.4 have not begun. Local master remains
present, no history rewrite occurred, and no private backup/stash was deleted.
The backup's existence/content was not independently audited or exposed.

## Closure criteria

Not all 112 criteria are satisfied. PASS below means local evidence or a
verified implementation/control. PENDING means remote evidence or a formal
gate is still required; UNAVAILABLE/UNVERIFIED is not a pass. Configured CI
triggers are distinct from actual execution. Criterion 112's prohibition on
premature completion is obeyed, but its approved-commit/post-commit gate remains
open. No COMPLETE status is assigned.

**Outstanding:** 6, 21, 22, 29, 73, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 96, 112.

| # | Criterion | Status | Evidence / remaining work |
| ---: | --- | --- | --- |
| 1 | Work is on `main`. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 2 | `main` descends from `c294ffd`. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 3 | Old `master` is not merged into `main`. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 4 | The 272,923,200-byte FITS blob is not reachable from `main`. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 5 | No tracked public-history blob exceeds 100 MiB. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 6 | Repository remains private. | UNVERIFIED | User states private; gh has no authenticated account, so remote verification is pending. |
| 7 | No normal 9.1d history rewrite occurs. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 8 | Historical documents are not retroactively rewritten solely to replace old commit IDs. | PASS | Local main/root/history inspection; only c294ffd reachable; no history operations. |
| 9 | GitHub Actions workflow exists. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 10 | CI runs on pushes to `main`. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 11 | CI runs on PRs targeting `main`. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 12 | Workflow permissions are least-privilege. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 13 | Normal CI needs no personal secrets. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 14 | CI does not publish packages. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 15 | CI does not create releases. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 16 | CI does not create tags. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 17 | CI does not modify versioning. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 18 | CI does not modify CHANGELOGs. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 19 | CI does not require private datasets. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 20 | CI uses only repository-safe fixtures. | PASS | Workflow inspected: main push/PR, read-only, four candidates, no mutation/publishing/private inputs. |
| 21 | Python 3.11 is attempted where available. | UNAVAILABLE locally / PENDING CI | Interpreter unavailable locally; still configured in Actions, which has not run. |
| 22 | Python 3.12 is attempted where available. | UNAVAILABLE locally / PENDING CI | Interpreter unavailable locally; still configured in Actions, which has not run. |
| 23 | Python 3.13 is attempted where available. | PASS | Available local candidate exercised with full test/build/runtime checks; Actions still pending. |
| 24 | Python 3.14 is attempted where available. | PASS | Available local candidate exercised with full test/build/runtime checks; Actions still pending. |
| 25 | Versions remain candidates, not final support claims. | PASS | All four candidates retained; local availability/results recorded; support deferred. |
| 26 | Unavailable candidates are recorded. | PASS | All four candidates retained; local availability/results recorded; support deferred. |
| 27 | Failing candidates are recorded. | PASS | All four candidates retained; local availability/results recorded; support deferred. |
| 28 | Failing candidates are not silently removed. | PASS | All four candidates retained; local availability/results recorded; support deferred. |
| 29 | Full pytest suite passes for applicable matrix entries. | PENDING | 329 tests pass locally on 3.13/3.14; full remote candidate matrix remains unexecuted. |
| 30 | Ruff passes. | PASS | Final local Ruff/36-file formatting/incremental whitespace checks pass. |
| 31 | Configured formatting passes. | PASS | Final local Ruff/36-file formatting/incremental whitespace checks pass. |
| 32 | Incremental `git diff --check` passes. | PASS | Final local Ruff/36-file formatting/incremental whitespace checks pass. |
| 33 | Coverage is not weakened merely for CI. | PASS | No existing tests weakened and no skips or continue-on-error added. |
| 34 | New CI skips are justified. | PASS | No existing tests weakened and no skips or continue-on-error added. |
| 35 | CI is reproducible from clean checkout. | PASS | Clean exported public-source snapshot plus implementation: 329 tests pass; isolated clean builds pass. |
| 36 | Wheel build succeeds. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 37 | Sdist build succeeds. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 38 | Build uses repository source only. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 39 | Wheel filename/version are correct. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 40 | Sdist filename/version are correct. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 41 | Project-name metadata is correct. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 42 | Version metadata is `1.1.0`. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 43 | Author metadata is Mark Wymer. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 44 | MIT licensing metadata is appropriate. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 45 | Runtime dependency metadata matches Stage 9.1c intent. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 46 | Dev-only dependencies are not runtime dependencies. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 47 | Build outputs remain untracked. | PASS | Both formats built and inspected on 3.13/3.14; metadata/dependency separation verified; outputs temporary. |
| 48 | Wheel contents are inspected. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 49 | Sdist contents are inspected. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 50 | Required package modules are present. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 51 | Console-script metadata is present. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 52 | Expected README/license metadata is present. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 53 | No private Stage 8 datasets are included. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 54 | No private local paths are included. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 55 | No `.git` data is included. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 56 | No accidental cache/temp files are included. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 57 | Superseded oversized Siril fixture is absent. | PASS | 39-member wheel and 46-member sdist pass strict contents/metadata/private-path inspection. |
| 58 | Wheel installs in clean temporary environment. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 59 | Installed `seestar-toolkit --version` is `1.1.0`. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 60 | Installed `python -m seestar_toolkit --version` is `1.1.0`. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 61 | Console entry point works outside repository source tree. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 62 | Module entry point works outside repository source tree. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 63 | Imported package resolves from temporary environment/site-packages. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 64 | Installed package does not require pytest. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 65 | Installed package does not require Ruff. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 66 | Installed package does not require PDF tooling. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 67 | Sdist smoke validation succeeds where practical. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 68 | Any sdist limitation is documented. | PASS | Separate clean runtime-only wheel and sdist venvs on 3.13/3.14; versions/import location/conversion verified. |
| 69 | `tests/data/PRIVACY_REVIEW.md` remains present. | PASS | Ten fixture sizes/hashes match approved baseline; no FITS changes or LFS; CI uses repository data. |
| 70 | Synthetic Siril mosaic remains the reviewed small fixture. | PASS | Ten fixture sizes/hashes match approved baseline; no FITS changes or LFS; CI uses repository data. |
| 71 | Sanitised real FITS fixtures remain sanitised. | PASS | Ten fixture sizes/hashes match approved baseline; no FITS changes or LFS; CI uses repository data. |
| 72 | CI does not restore old identifying metadata. | PASS | Ten fixture sizes/hashes match approved baseline; no FITS changes or LFS; CI uses repository data. |
| 73 | CI logs expose no private fixture metadata/paths. | PENDING | No actual Actions logs exist to review; validator implementation does not emit private metadata. |
| 74 | No Git LFS dependency is introduced. | PASS | Ten fixture sizes/hashes match approved baseline; no FITS changes or LFS; CI uses repository data. |
| 75 | `PACKAGING.md` reflects implemented build/CI process where needed. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 76 | `PROJECT_Notes.md` reflects 9.1d status where needed. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 77 | `PUBLIC_HISTORY_BOOTSTRAP.md` remains accurate. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 78 | Historical Stage documents are preserved. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 79 | User Guide work is not prematurely moved into 9.1d. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 80 | Final Python support claims remain deferred to 9.2a. | PASS | Packaging/notes updated; bootstrap and historical documents preserved; later-stage claims deferred. |
| 81 | At least one real GitHub Actions run occurs. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 82 | Triggering commit is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 83 | Attempted Python matrix is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 84 | Runner OS is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 85 | Job outcomes are recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 86 | Pytest outcome is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 87 | Ruff outcome is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 88 | Formatting outcome is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 89 | Build outcome is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 90 | Installed-artifact smoke outcome is recorded. | PENDING | No Actions run/triggering implementation SHA; requires approved commit/push; local results are separate. |
| 91 | Failure/remediation cycles remain visible. | PASS | Local failures/remediations recorded; no Actions failures yet to record or suppress. |
| 92 | Final applicable CI state required for closure is passing. | PENDING | No applicable Actions passing state exists yet. |
| 93 | No PyPI publication. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 94 | No GitHub Release. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 95 | No release tag. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 96 | Repository stays private. | UNVERIFIED | User states private; gh has no authenticated account, so remote verification is pending. |
| 97 | Stage 9.2 not begun. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 98 | Stage 9.3 not begun. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 99 | Stage 9.4 not begun. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 100 | No automatic release workflow. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 101 | Pre-public `master` preserved through closure. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 102 | Private pre-public backup not intentionally deleted during 9.1d. | PASS | No publication/tag/release/visibility/history/next-stage action; master and private backup not deleted. |
| 103 | Final pytest passes. | PASS | Final local full tests, Ruff, scoped formatting and incremental whitespace pass. |
| 104 | Final Ruff passes. | PASS | Final local full tests, Ruff, scoped formatting and incremental whitespace pass. |
| 105 | Final formatting passes. | PASS | Final local full tests, Ruff, scoped formatting and incremental whitespace pass. |
| 106 | Final incremental `git diff --check` passes. | PASS | Final local full tests, Ruff, scoped formatting and incremental whitespace pass. |
| 107 | Pre-commit `git status` contains only expected 9.1d changes. | PASS | Status reviewed: intended implementation plus pre-existing spec only; no generated/private files added. |
| 108 | No unexpected generated artifacts are tracked. | PASS | Status reviewed: intended implementation plus pre-existing spec only; no generated/private files added. |
| 109 | No unexpected private files are tracked. | PASS | Status reviewed: intended implementation plus pre-existing spec only; no generated/private files added. |
| 110 | Codex provides a complete closure report mapped to these criteria. | PASS | This report explicitly assesses each of the 112 numbered criteria. |
| 111 | Codex does not commit. | PASS | No commit created; main remains c294ffd. |
| 112 | 9.1d is not marked COMPLETE until the approved commit exists and post-commit state is verified. | PENDING | Stage remains STARTED; approved commit and post-commit state do not yet exist. |


After Stage review approves a commit/push, run and review all four Actions
entries, verify repository privacy/default branch and run outcomes, record
run URL and triggering SHA, retain failures/remediation, then verify approved
commit and post-commit state. Only the separately approved formal closure
permits Stage 9.2a. Suggested implementation commit message remains the one
in the specification; no commit is made by this work.


## CI Run 1 — FAIL: specification trailing whitespace

Evidence source: the independently reviewed CI Run 1 finding supplied for
this remediation. Run 1 was a genuine GitHub Actions **FAIL**. The
**Incremental whitespace** check correctly detected exactly five
trailing-whitespace violations in
`docs/development/change_documents/STAGE_9/STAGE_9.1d.md`, lines 3–7.
Each line ended with two Markdown hard-break spaces. This was specification
whitespace, not a Python-candidate compatibility defect.

| Python candidate | CI Run 1 attempt evidence | Platform |
| --- | --- | --- |
| 3.11 | Attempted | macOS arm64 |
| 3.12 | Attempted | macOS arm64 |
| 3.13 | Attempted | macOS arm64 |
| 3.14 | Attempted | macOS arm64 |

All four candidates were attempted; none was removed. Run URL/ID, triggering
SHA and individual step results were not supplied with this finding and are
not invented here. The overall result remains FAIL, irrespective of the
local remediation result. A subsequent passing run is still required.

Remediation is limited to removing those ten trailing space bytes across
five lines, preserving their textual meaning, and updating this report.
The GitHub Actions whitespace check and Python matrix are unchanged, as are
production code, tests, fixtures, packaging metadata and validation behaviour.
The pre-existing CHANGELOG modification is preserved.

Local remediation validation:

- `python tools/check_formatting.py`: PASS, 36 files already formatted.
- `git diff --check`: PASS.
- New/untracked report whitespace check: PASS, no diagnostics.
- Exact specification diff: only the two trailing spaces on each of lines
  3–7 removed; all other bytes unchanged.

These are local formatting/whitespace results, not a retrospective CI PASS.
The original 112-criterion table above is retained as pre-run evidence;
this follow-up establishes the candidate attempts and occurrence of Run 1,
but does not perform a new full closure audit. No commit or CI rerun was made
in this remediation. Stage 9.1d remains **STARTED**; Stage 9.2 has not begun.
