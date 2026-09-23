# Stage 9.4a Report

## Decision

**Checkpoint A audit/design work: PASS. Release/public-repository readiness:
FAIL. Stage 9.4a remains STARTED.**

The required baseline, repository, release design and public-content audits were
completed. The audit found a genuine blocker: maintainer-specific filesystem
paths are present in the current tree and all ten commits reachable from public
`main`. The conflict between removing those paths from reachable history and the
standing prohibition on history rewriting requires independent disposition
before Checkpoint B may begin.

## Exact starting state

- HEAD: `ff0ada13ddc1236fb8e416821ea5fca7352e18de`
- Subject: `docs: record Stage 9.3b and BUG-001 completion`
- Branch: `main`; configured `origin/main`; zero ahead/behind locally
- Initial status: expected unstaged `docs/development/CHANGELOG.md` only
- Pending diff: two-line separator/row recording `ff0ada1`; preserved unchanged
- Version: 1.1.0 from `pyproject.toml` `[project].version`
- Public changelog: `1.1.0 - Unreleased`
- Local tags: none
- Supplied remote state: private; no v1.1.0 tag/Release; `ff0ada1` Actions green
- Independent remote query: unavailable because GitHub CLI was unauthenticated
  and the execution environment could not resolve `github.com`

## Files created and modified

Created:

- `docs/development/change_documents/STAGE_9/STAGE_9.4a.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.4a_REPORT.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.4a_CHECKPOINT_A.json`

No pre-existing file was modified. The pending development CHANGELOG row remains
exactly as found.

## Release candidate inventory and design

The exact wheel is `seestar_toolkit-1.1.0-py3-none-any.whl`; the exact sdist is
`seestar_toolkit-1.1.0.tar.gz`. The seven-member, single-root release ZIP and
external checksum are specified in the Stage document. Assembly uses a clean
exact-tree export, fresh inner builds, an explicit allowlist, normalized ZIP
metadata, two-build byte comparison, strict external checksum and an independent
fresh extraction/inspection path. No candidate was assembled in A.

## Public repository and privacy findings

### Blocking findings

1. `docs/development/DEV_VENV_COMMANDS.md` contains an actual maintainer-specific
   `<user-home>/...` virtual-environment path and stale test paths.
2. The original scan reported 42 marker matches across 16 Markdown files.
   Exact reconstruction found 38 actual username-bearing path occurrences; four
   cloud-checkout lines had each been counted under two marker expressions.
   The affected files remain the command document, thirteen Stage 8 change
   documents, `STAGE_9.1a_AUDIT.md` and `STAGE_9.1b_REPORT.md`.
3. The same material is reachable from every commit in the ten-commit public
   history rooted at `c294ffd`. Editing the tip cannot remove it. No history
   rewrite or public-history deletion was performed or authorized.

These findings fail the applicable privacy/history criteria. They are not
converted to PASS because remediation could be planned.

### Passing findings

- `python tools/check_public_inputs.py`: **PASS — 10 reviewed fixtures; clean
  public root; no oversized blobs**.
- Tracked history contains no wheel, sdist, cache, bytecode, build directory,
  private BUGLIST/add_bug utility or other named private-data path.
- Ten approved FIT/FITS fixtures match the strict manifest. Nine real fixtures
  retain the recorded sanitised headers; the Siril mosaic is synthetic.
- No globally ignored `*.fit` or `*.fits` rule exists.
- The largest reachable blob is the reviewed 49,775,040-byte stacked fixture,
  below the 100 MiB policy.
- Synthetic private-path strings in negative validator tests and generic user
  examples such as `/Volumes/Astronomy/...` are intentional test/example data,
  not detected personal disclosures.

## Public-content usefulness

Development records are large but generally useful as architecture, release
decision and validation provenance. README directs ordinary users to the Quick
Start and User Guide. No broad development-history deletion is recommended for
tidiness. The live development command document is both privacy-defective and
outdated, so it needs a specific disposition. Optional later consolidation of
historical material must preserve evidence and is not release-critical once
privacy is resolved.

## Public-facing consistency and BUG-001

README, public CHANGELOG, User Guide, Quick Start, approved PDFs, current
architecture, CLI help and implementation consistently state that archive does
not automatically create TIFFs for lights or an observation-level `tiff/`
directory and still creates the Seestar-stack TIFF companion. Standalone
conversion remains separate. Historical statements describing the former
contract are labeled by current project notes and need not be rewritten.

Python 3.11–3.14, Apple-silicon macOS, S50 support boundaries, installation,
uninstallation, CLI, archive safety, configuration and privacy statements remain
consistent with prior evidence. No potential product defect was found.

## Checkpoint B and C

B is authorized only after independent review resolves the public-history
privacy conflict. Its designed scope is the accepted narrow remediation,
allowlisted builder/validator implementation, repeatable disposable assembly,
inner distribution and extracted-ZIP validation, checksums/provenance and
affected quality gates.

C rechecks the exact proposed closure tree, reachable history, fixtures,
public-facing consistency, artifacts, checksums, quality gates and absence of
publication actions. Technical readiness remains distinct from independent
review, authorized commit, post-commit validation/CI and formal completion.

## Closure criteria initial accounting

| Criteria | Status | Evidence |
| --- | --- | --- |
| 1–7 | PASS | Baseline, carry-forward, version, prior decisions, inventory, checksum and exclusions recorded. |
| 8–21 | PENDING | Builder, repeatability, artifacts and extracted validation belong to B. |
| 22 | FAIL | Current tracked privacy review found the live personal path. |
| 23 | FAIL | Personal path literals are present throughout reachable public history. |
| 24 | PENDING | No credential was found, but final absence claim awaits complete remediation and C. |
| 25 | FAIL | Inappropriate personal filesystem paths remain current and reachable. |
| 26–30 | PASS | Private utility/build exclusions, size policy, ten-fixture manifest and scoped ignore policy verified. |
| 31 | PASS | Public development-content usefulness disposition recorded. |
| 32–36 | PASS | Public docs/package/support and BUG-001 consistency audit passed. |
| 37 | FAIL | The unresolved privacy/publication defect is release-blocking. |
| 38 | PASS | Public changelog remains Unreleased. |
| 39 | PENDING | Full quality suite intentionally not repeated in audit/design A. |
| 40 | PENDING | Public-input check passed; final Markdown/distribution gates belong to B/C. |
| 41 | PASS | No tag, release, upload, publication or visibility change occurred. |
| 42–49 | PENDING | Independent review, B/C, closure commit, exact-state CI and formal declaration have not occurred. |

## Validation performed

- exact HEAD/subject/branch/upstream/status inspection;
- working diff and staged-state inspection;
- package/build metadata, manifest, tool and CI review;
- complete tracked-tree and ten-commit reachable-history filename/blob inventory;
- public input/fixture/history guard;
- history/current-tree marker and secret-pattern scans with semantic review;
- binary/blob size and tracked release-artifact inventory;
- public documents, issue forms, license and BUG-001 consistency review;
- committed PDF/manifest hash inspection; and
- `git diff --check` before Stage 9.4a files were authored.

Expensive pytest, distribution builds and PDF regeneration were not repeated
because A is design-only and prior exact-baseline evidence remains applicable.

## Boundary confirmation

No builder or release candidate was created. No production source, test,
fixture, package metadata, CI, public guide, PDF, manifest or existing history
was changed. No commit, push, tag, Release, upload, PyPI publication, visibility
change, Stage 9.4b action or formal Stage 9.4a completion occurred.

## Privacy-remediation design continuation

The user intentionally removed these two private-only maintainer documents from
the working tree:

- `docs/development/DEV_VENV_COMMANDS.md`;
- `docs/development/DEV_VENV_DIRECTIONS.md`.

They are to remain outside the public repository and must be removed from all
history reachable from future public `main`. Their private destination is not
recorded. The deletions are user changes and were not performed by this design
pass.

The complete controlled map now covers 18 paths: both removed documents,
thirteen Stage 8 documents, two Stage 9 documents and `PROJECT_Notes.md`. All ten
commits from `c294ffd` through `ff0ada1` are affected. The path categories are
private test-data roots, development-environment paths, cloud-synchronized
checkout paths, private maintainer-document content and references to those
documents. No new privacy category was found. Public author/copyright identity,
generic examples and intentional validator test strings remain untouched.

The proposed mechanism is a path-limited `git filter-repo` operation in a fresh
single-branch clone, using a private exact replacement map and complete removal
of both DEV_VENV paths. Before execution it requires a verified private bundle
of all original refs and a separate private copy of working changes. All ten
public-lineage SHAs will change; unrelated `master`, stashes and private backups
must not be rewritten or pushed.

Historical reports may retain old public-lineage SHAs as contemporaneous IDs if
the final report publishes the generated old-to-new mapping and labels them as
superseded by privacy remediation. Operational references—the public-root guard,
CI fallback, live status documents and development CHANGELOG—must use mapped
final-public IDs. Pre-public Stage identifiers remain unchanged.

Pre-push validation requires allowlisted per-commit tree comparisons, exhaustive
current/history scans, DEV_VENV absence, preserved public identity and fixtures,
`git fsck`, a fresh-clone check and every repository quality/distribution/PDF
gate. After a lease-protected private force-push, a new clone must repeat those
checks, verify only `main` moved, confirm private visibility/no publication and
obtain green exact-SHA Actions. Rollback restores old `main` from the private
bundle using force-with-lease while the repository remains private.

This continuation performs design and evidence updates only. Criteria 22–25 and
37 remain FAIL/PENDING exactly as previously recorded. No criterion changes to
PASS because a remediation design exists. No rewrite, commit, push, force-push,
remote change, artifact assembly, Checkpoint B or Stage 9.4b work occurred.

## Local privacy-remediation execution result

**Local remediation: PASS. Remote remediation: PENDING. Release/public readiness:
FAIL.** This is a separate authorized local execution after the design-only
record above; it does not rewrite the earlier finding or design status.

`git-filter-repo` 2.47.0 rewrote only the ten-commit `main` lineage in a
disposable clone. Both private DEV_VENV paths were purged, retained path literals
were neutralized, and live references were removed. All ten commits have one
mapped replacement; full mapping appears in the specification and structured
evidence. The new local root is `0cdc6c2`; the rewritten equivalent of `ff0ada1`
is `93a4299`.

The private offline bundle was verified to contain old `main`, `master`, both
origin tracking refs and the stash. Its SHA-256 is
`902bae43f1175ca49a24990b4f065b8ca2121d83afbdd1c69faf2af6abfa24db`.
The separately verified working-state provenance manifest SHA-256 is
`b368a503da25bf957462d9298fd2187d2eb7743a7ed5a6392f4c33f09b4fc651`.
Backup locations remain private.

Per-commit validation proves order, subjects, authors and dates are preserved;
every tree differs only by the exact transformation across 18 approved paths.
All mapped private strings, DEV_VENV names and private-document signatures are
absent from all rewritten trees and commit messages. Intentionally public Mark
Wymer author/copyright identity remains.

Committed-candidate and fresh-clone gates passed: `git fsck --full --strict`, ten
reviewed fixtures, root/blob/inventory policy, 332 pytest tests in 12.05 seconds,
Ruff, 37-file configured formatting, incremental whitespace, strict PDF manifests
and validator (27-page guide; 5-page Quick Start), and isolated wheel/sdist
validation (39/46 allowed members, both entry points at 1.1.0). The initial bare
Python/PDF-mtime attempt was an environment-only failure; the established Python
environment and disposable mtime synchronization produced the reported PASS
without changing tracked bytes.

The pending changelog, three Stage 9.4a files and intentional current-tree
DEV_VENV absence were restored onto local `93a4299`. Operational root/closure
references now use mapped IDs; contemporaneous historical evidence retains old
IDs under the documented mapping policy.

No remote operation occurred. Local `main` is `93a4299`; `origin/main` remains
`ff0ada1`, producing the expected 10-ahead/10-behind divergence. Criteria 22–25
and 37 are not promoted to PASS until separately authorized remote replacement,
fresh remote validation and exact-SHA Actions succeed. No Checkpoint B work,
release artifact, commit, push, tag, publication or visibility change occurred.

Final validation of the exact restored working state passed: 332 pytest tests in
11.65 seconds; 174 focused archive tests in 1.75 seconds; Ruff; 37-file formatting;
the updated public-input guard; both incremental whitespace gates; three Issue
form YAML files; 88 Markdown files with balanced fences and 47 valid local file
links; clean new-evidence whitespace; PDF/manifests; and isolated distribution
validation. The sandboxed distribution rerun genuinely failed because DNS could
not resolve the package index while provisioning isolated setuptools. Its
authorized network-enabled rerun passed with 39 wheel and 46 sdist members, both
entry points and runtime smoke tests. This setup failure and remediation are
preserved rather than converted into an initial pass.

`git fsck --full --strict` returned success and reported two dangling blobs and
one dangling commit from the local fetch/reset workflow. They are unreachable
from rewritten `main`, absent from the verified fresh clone and will not be sent
by the proposed `main` refspec. They were not pruned because this operation does
not delete unrelated or recovery material. A broad all-Markdown whitespace probe
also encountered the development CHANGELOG's pre-existing historical whitespace;
the approved incremental checks and all newly authored evidence pass. No
unrelated formatting was changed.

## Final post-remote privacy verification

**Privacy-history remediation: PASS. Checkpoint A audit/design: PASS. Stage 9.4a
remains STARTED; Checkpoint B has not begun.**

The remote chronology is preserved exactly:

1. The ten-commit local rewrite passed.
2. The approved force-with-lease replaced private remote `main` with rewritten
   `93a4299`.
3. All four Actions jobs for `93a4299` genuinely failed at the public fixture
   and history step.
4. Diagnosis reproduced `fatal: Not a valid object name c294ffd`; committed
   history guards still named the superseded root.
5. Dedicated child commit `0b0a6bf` updated operational root references to
   `0cdc6c2`.
6. The user independently confirmed all four Actions jobs for exact `0b0a6bf`
   are green.

A new remote clone contains exact tip
`0b0a6bf1f8b987a70a35097455aadf7108a934c9`, parent
`93a4299ccc56f4f2d82c39afa9c735f9989608a3` and sole root
`0cdc6c214e87b28925cf938ebf7dc8e75b9dddb2`. Its eleven commits are the ten
mapped replacements in the recorded provenance table followed by the CI
remediation commit. None of the ten original IDs is reachable.

The fresh clone's eleven trees and commit messages contain none of the mapped
private home, dataset, development-environment or cloud-checkout strings, either
DEV_VENV filename, or distinctive private document title/content. Both private
documents are absent from the tip and all reachable history. Mark Wymer remains
in LICENSE and package author metadata as intentional public identity.

The committed `python tools/check_public_inputs.py` passes: ten reviewed FITS
fixtures, clean rewritten public root and no oversized blob. `git fsck --full
--strict` passes without output. The clone is clean. A read-only remote ref query
shows only `refs/heads/main` at `0b0a6bf` and no tags.

GitHub API authentication remained unavailable, so private visibility was not
independently queried; the user's explicit confirmation that the repository is
still private is retained as evidence. Exact-commit Actions evidence is likewise
the user's independent confirmation of four green jobs at `0b0a6bf`, clearly
separated from the locally verified Git evidence.

Current criteria 22–25 and 37 are PASS because remote reachability, privacy,
fixture, integrity and remediation-CI gates now prove the blocking material has
been removed. The original FAIL/PENDING rows remain genuine historical results.
Criteria for builder implementation, release-candidate assembly, Checkpoints B/C,
closure commit and Stage completion remain PENDING. No commit, push, history
rewrite, visibility change, tag, Release, artifact assembly, Checkpoint B or
Stage 9.4b action occurred during this final verification.

## Checkpoint B release-candidate result

**Checkpoint B technical result: PASS. Independent review: PENDING. Stage 9.4a
remains STARTED.**

### Source and implementation

Candidate assembly used exact committed source
`0b0a6bf1f8b987a70a35097455aadf7108a934c9` (`ci: update public history root
after privacy rewrite`). The existing Stage 9.4a evidence and development
document changes remained outside the export. The public `CHANGELOG.md` remains
`1.1.0 - Unreleased`.

`tools/build_release_candidate.py` implements clean `git archive` export,
metadata-derived names, two isolated PEP 517 builds, deterministic sdist and ZIP
metadata, a seven-member allowlist, byte-identity comparison and strict checksum
generation. `tools/validate_release_candidate.py` independently validates paths,
types, modes, duplicates, inventory, exact source bytes, PDFs, both nested
distributions and clean installs. Twelve focused tests cover the release
contract and unsafe outer/nested archive cases. The configured formatter now
includes all three new Python files.

### Preserved failure and remediation chronology

1. The prior temporary validation environment's interpreter had been upgraded
   and no longer exposed pytest/Ruff. A fresh temporary Python 3.13 environment
   was created. Its first sandboxed dependency install could not resolve PyPI;
   the authorized network-enabled retry installed the declared extras.
2. The focused initial Ruff run found five overlength lines and three unused
   imports in the new unformatted implementation. Formatting/import cleanup
   resolved these; focused Ruff then passed.
3. The first assembly attempt failed before producing an artifact with
   `FileNotFoundError` for the temporary source tar. The builder now creates its
   temporary build parent before export.
4. The second assembly attempt built two identical wheels but correctly stopped
   with `non-reproducible release artifact: sdist`. Setuptools retained variable
   gzip/tar metadata despite `SOURCE_DATE_EPOCH`.
5. The builder now rewrites only sdist container metadata with the source commit
   epoch, fixed root ownership, fixed file/directory modes and sorted members.
   Payload bytes remain the freshly built payload. The next independent pair
   was byte-identical for wheel, sdist, release ZIP and checksum.
6. Final review made wheel/sdist traversal, link and duplicate rejection
   explicit and added six more focused tests. The accepted artifact bytes did
   not change; the final independent validator rerun passed.
7. An informational all-history Markdown whitespace probe reported known
   whitespace in unchanged historical documents. The authoritative incremental
   `git diff --check`, root-to-HEAD committed check and direct new-file checks
   all passed; no unrelated historical prose was reformatted.

### Accepted private candidate

The untracked artifacts are retained at the normalized private location
`<private-release-staging>/`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `seestar-toolkit-1.1.0-release.zip` | 242979 | `2abda7623b8381e1d2a335f7041adef1454383c0a2159c8f113ec26357f92ff4` |
| `seestar-toolkit-1.1.0-release.zip.sha256` | 106 | `a9ec24b5b49124f2b6b903e19c5de0db03e90b723e106f748d47ec8bba31c9c9` |
| nested wheel | 47819 | `7b3fa9b2a465933d4eae65cf2e34b53fcf7319181d5cb526d194e54fe6bacf57` |
| nested sdist | 34045 | `9798475650ba82b84f5490465d43ccb216ecb204e6e8d9e5ca8fa13f8babf251` |

The checksum file is exactly one LF-terminated line containing the ZIP digest,
two spaces and `seestar-toolkit-1.1.0-release.zip`. It is outside the ZIP.

The ZIP has one implicit root, `seestar-toolkit-1.1.0/`, and exactly these seven
0644 regular members in fixed order: Quick Start PDF, User Guide PDF, README,
public CHANGELOG, LICENSE, wheel and sdist. There is no archive comment, extra
field, development documentation, Markdown guide source, repository PDF
manifest, test, fixture, source tree, CI file, tool, Git data, cache or private
material.

### Artifact and repository validation

- Two independent builds: PASS; wheel, normalized sdist, ZIP and checksum are
  byte-identical.
- Independent extraction/source comparison: PASS; all five static inputs match
  exact commit `0b0a6bf` byte-for-byte.
- Wheel: PASS; 39 allowed members, metadata/license/entry point, isolated install,
  both entry points at 1.1.0 and runtime conversion smoke test.
- Sdist: PASS; 46 allowed files, safe members, metadata/license/entry point,
  isolated install, both entry points at 1.1.0 and runtime conversion smoke test.
- PDFs/manifests: PASS; Quick Start 5 pages, SHA-256 `32bd5b42...f394f`;
  User Guide 27 pages, SHA-256 `f9c716ca...d56e3`; committed manifests, fonts,
  metadata, content, links and navigation validated.
- Full pytest: PASS, 344 tests. Ruff: PASS. Configured formatting: PASS, 40
  paths. `git diff --check` and root-to-HEAD committed whitespace: PASS.
- Public inputs/history: PASS; ten reviewed fixtures, rewritten root and no
  oversized blob. Markdown: PASS; 88 files, balanced fences and 47 valid local
  links. Issue-form YAML: PASS, three files. Isolated repository distribution
  validation: PASS, including wheel/sdist clean installs.
- BUG-001: PASS through the full regression suite and release README statements:
  individual light FITS files are not automatically converted, while the
  Seestar stack TIFF companion remains required.
- Privacy/release content: PASS. Generated artifacts remain outside the
  repository, untracked and private. Assembly and validation produced no source
  change.

Tool provenance: Python 3.13.15, build 1.6.1, setuptools 84.0.0 in isolated
builds, Ruff 0.16.8, Git 2.50.1, Pandoc 3.11, XeTeX/TeX Live 2026 and Poppler
26.09.0. ZIP construction uses Python's standard-library `zipfile`, with fixed
metadata derived from the source commit epoch.

### Checkpoint B criteria

| Criteria | Status | Evidence |
| --- | --- | --- |
| 1–7 | PASS | Checkpoint A baseline, inventory, checksum and exclusions remain valid. |
| 8–10 | PASS | Clean-source metadata-derived allowlisted builder and normalized ZIP implemented. |
| 11 | PASS | Two independent builds produced identical inner and outer artifacts. |
| 12–13 | PASS | Strict wheel/sdist inspection and separate clean installs/entry points passed. |
| 14–16 | PASS | PDFs and all static inputs match committed approved bytes; exact seven-file extraction passed. |
| 17 | PASS | Outer and nested traversal/link/duplicate/extra rejection is implemented and tested. |
| 18–19 | PASS | Source/tool/hash/size provenance recorded; strict external checksum verifies. |
| 20–21 | PASS | Source tree unchanged by assembly; artifacts remain untracked/private. |
| 22–38 | PASS | Accepted Checkpoint A privacy, repository, document, package and BUG-001 evidence remains valid. |
| 39–40 | PASS | Fresh full quality, public-input, Markdown/link, PDF and distribution gates passed. |
| 41 | PASS | No publication, tag, visibility or upload action occurred. |
| 42 | PASS | Checkpoint A was independently accepted and B explicitly authorized. |
| 43–49 | PENDING | Independent B review, Checkpoint C and formal closure gates have not occurred. |

No product, packaging, documentation, privacy or release-content defect remains
open from Checkpoint B. The two builder defects were detected by required gates,
fixed narrowly and preserved above as genuine failed attempts. No Checkpoint C,
commit, push, tag, Release, PyPI upload, visibility change, publication or Stage
9.4b work occurred.

## Checkpoint C final exact-tree audit

**Checkpoint C: PASS. Stage 9.4a is ready for independent final review and
closure commit authorization. Stage 9.4a remains STARTED.**

Checkpoint B was independently reviewed and accepted, so criterion 43 is PASS.
This audit reconciled all earlier evidence without changing any historical FAIL:
the original public-history privacy finding, ten-commit local rewrite, approved
force-with-lease, four-job CI failure at `93a4299`, stale `c294ffd` diagnosis,
`0b0a6bf` remediation and its four green jobs, plus every Checkpoint B failed
attempt and remediation, all remain visible.

### Proposed closure-tree scope

| Path | Scope reason |
| --- | --- |
| `docs/development/CHANGELOG.md` | Preserved rewritten public-lineage identifiers and pending development history. |
| `docs/development/PACKAGING.md` | Current operational root/closure identifiers and release-candidate tooling policy. |
| `docs/development/PROJECT_Notes.md` | Private-note reference removal, rewritten identifiers and Stage 9.4a status. |
| `docs/development/change_documents/STAGE_9/STAGE_9.4a.md` | Authoritative specification, privacy chronology and A–C results. |
| `STAGE_9.4a_CHECKPOINT_A.json` | Structured A/privacy remediation evidence, including preserved failures. |
| `STAGE_9.4a_CHECKPOINT_B.json` | Structured candidate implementation and validation evidence. |
| `STAGE_9.4a_CHECKPOINT_C.json` | Structured exact-tree closure-readiness evidence. |
| `STAGE_9.4a_REPORT.md` | Consolidated Stage chronology and audit results. |
| `tools/build_release_candidate.py` | Public development tooling for clean, reproducible allowlisted assembly. |
| `tools/validate_release_candidate.py` | Public independent extraction, distribution, PDF, checksum and safety validator. |
| `tests/unit/test_release_candidate.py` | Focused release archive/checksum safety contract tests. |
| `tools/check_formatting.py` | Adds the three new Python paths without removing or weakening existing coverage. |

There are no staged changes. No unrelated personal file, private maintainer
utility, DEV_VENV document, private capture, generated candidate, wheel, sdist,
cache or temporary file is in the proposed commit scope. Existing ignored
historical `dist/stage9.1c` artifacts are outside Git and outside this scope.

The three release tooling/test files contain no private data or concrete private
path. The generic privacy-marker byte strings in the validator are intentional
rejection rules. Review found no dependency addition, runtime behavior change,
unsafe extraction acceptance or formatting-gate reduction.

### PDF integrity reconciliation

The original Stage 9.3b accepted artifacts were:

- Quick Start PDF `56f0a92641f86742e0e066b3d3727424396bef76705d27b29cc1f5f59656b033`;
- User Guide PDF `8600d48d03ca8bcdf8bc4e3f2f3403143592a45fa3e769d7c3734ebec11ee70b`.

BUG-001 commit `58a57b92efff96da0f41b71e1f021d709a7be0f3` then changed both Markdown guides
to remove automatic individual-light TIFF claims and describe the retained stack
companion. That same commit regenerated the PDFs and updated both manifests.
Current and committed `0b0a6bf` bytes are identical and authoritative:

- Quick Start Markdown `35252f89...76f4d83`; PDF
  `32bd5b4231ae9067c2ee6891c1473aaf233f573a4566add4ec641b2b601f394f`;
- User Guide Markdown `fa4f1b390...525ffa`; PDF
  `f9c716ca68d18958657b4fbec9ded7061f0bf3e6040383757ccfc291e31d56e3`.

The differing hashes therefore reflect a traced, committed documentation change,
not the privacy rewrite or unexplained byte drift. Both strict manifests and PDF
validators pass.

### Candidate and validation result

The retained private candidate remains SHA-256
`2abda7623b8381e1d2a335f7041adef1454383c0a2159c8f113ec26357f92ff4`.
Its checksum verifies and its single root contains exactly the approved seven
members. Checkpoint B's independent validation proves all five static inputs
match `0b0a6bf` and both nested distributions came from its clean export; none of
the uncommitted Stage 9.4a evidence entered the candidate. No rebuild was needed
because neither the committed source nor retained candidate changed.

Fresh Checkpoint C gates passed:

- full pytest: 344 passed in 10.58 seconds; focused release suite: 12 passed;
- Ruff: all checks passed; configured formatting: 40 files already formatted;
- `git diff --check`, rewritten-root-to-HEAD and direct new-file whitespace: PASS;
- public input/history guard: ten reviewed fixtures, clean root, no oversized blob;
- PDFs/manifests: PASS, 27-page User Guide and 5-page Quick Start;
- Markdown: 88 files, balanced fences, 47 valid local links; three Issue forms parse;
- isolated distribution validation: wheel 39 files, sdist 46 files, both clean
  installs, both entry points at 1.1.0 and runtime conversion smoke tests;
- exact proposed-scope privacy scan and tracked/generated inventory: PASS; and
- public `CHANGELOG.md`: `1.1.0 - Unreleased`.

Remote ref inspection shows only `refs/heads/main` at `0b0a6bf` and no tags.
GitHub CLI remains unauthenticated, so repository visibility and Release absence
were not independently queried in this audit; the previously accepted private
visibility/no-Release evidence remains applicable and no local action changed
either state.

### Final criteria status

- **44 PASS** — the exact proposed closure tree passes every technical audit.
- **45 PENDING** — independent technical closure review has not yet accepted this
  exact proposed tree.
- **46 PENDING** — no closure commit has been authorized or created.
- **47 PENDING** — exact post-commit validation and exact-commit Actions require
  the future closure commit.
- **48 PENDING** — independent authorization of formal completion must follow 47.
- **49 PENDING** — Stage 9.4a has not been formally declared COMPLETE.

No discrepancy or release blocker remains. No commit, push, history rewrite,
tag, GitHub Release, PyPI publication, visibility change or Stage 9.4b work
occurred during Checkpoint C.
