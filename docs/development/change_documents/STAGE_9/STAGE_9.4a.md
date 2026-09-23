# Stage 9.4a — Release Candidate and Public Repository Readiness

**START boundary: STARTED at the pre-remediation equivalent of `93a4299`.**
**Current boundary: Checkpoints A and B COMPLETE; Checkpoint C technical PASS pending independent final review.**
**COMPLETE boundary: not reached.**

## 1. Purpose and authority

Stage 9.4a prepares and validates the exact v1.1.0 release candidate without
publishing it. The authoritative starting baseline is
`ff0ada13ddc1236fb8e416821ea5fca7352e18de` (`docs: record Stage 9.3b and
BUG-001 completion`, 2026-09-22). BUG-001 was fixed by `89e506b`; its corrected
archive behavior is part of the release contract.

Stage 9.4a has three checkpoints:

- **A — audit and design:** inspect the exact baseline, public repository and
  reachable history; define the release inventory, assembly design, later
  checkpoints and closure criteria. Do not implement the builder or assemble
  release artifacts.
- **B — implementation and candidate validation:** after independent acceptance
  of A and explicit authorization, resolve accepted A findings, implement the
  allowlisted release builder, assemble disposable candidates, and validate
  repeatability, contents, nested distributions, checksums and documentation.
- **C — final closure-readiness audit:** validate the exact proposed closure
  tree, public repository and reachable history, release contents and all Stage
  criteria. Independent review, an authorized closure commit, exact post-commit
  validation and exact-commit CI precede formal completion.

Stage 9.4b alone owns Gate 1 approval and every publication action. Stage 9.4a
must not create or push a tag, change repository visibility, create a GitHub
Release, upload assets, publish to PyPI, or declare v1.1.0 released.

## 2. Starting state

- `HEAD`, `main`, `origin/main` and `origin/HEAD` resolve locally to `ff0ada1`;
  `main` is zero ahead and zero behind its configured upstream.
- The only initial working-tree change is the expected unstaged
  `docs/development/CHANGELOG.md` carry-forward row recording `ff0ada1`. It is
  not an unexpected dirty state and must be preserved byte-for-byte until the
  established workflow consumes it.
- Package version authority is `[project].version = "1.1.0"` in
  `pyproject.toml`. `src/seestar_toolkit/__init__.py` resolves installed version
  through package metadata.
- The public `CHANGELOG.md` says `1.1.0 - Unreleased`. No local tag exists.
- The user-supplied starting state says the GitHub repository is private, no
  v1.1.0 GitHub Release exists, and Actions for `ff0ada1` are green. The local
  environment has no authenticated GitHub CLI session and network name
  resolution was unavailable, so A does not independently promote those remote
  facts beyond supplied evidence. C and Stage 9.4b require authenticated checks.

## 3. Authoritative release inventory

The final outer artifact is `seestar-toolkit-1.1.0-release.zip`. It extracts to
one directory named `seestar-toolkit-1.1.0/` containing exactly:

```text
seestar-toolkit-1.1.0/
    SEESTAR_TOOLKIT_QUICK_START.pdf
    SEESTAR_TOOLKIT_USER_GUIDE.pdf
    README.md
    CHANGELOG.md
    LICENSE
    seestar_toolkit-1.1.0-py3-none-any.whl
    seestar_toolkit-1.1.0.tar.gz
```

The distribution filenames are established by current package metadata and the
existing strict distribution validator. The external checksum is
`seestar-toolkit-1.1.0-release.zip.sha256`. It is generated beside the ZIP,
never placed inside it, and neither release artifact is committed.

The ZIP excludes development documentation, guide Markdown, repository guide
manifests, tests and fixtures, `.git`, `.github`, tools, source checkouts,
caches, temporary files, private data and local environment material. The
embedded wheel and sdist retain their separately validated allowlists.

## 4. Candidate assembly architecture

Checkpoint B should implement one repository Python wrapper with fixed input
and output mappings. It must:

1. require the repository to be at the explicitly approved clean source commit,
   apart from a defined development evidence workflow when making candidates;
2. read name and version from `pyproject.toml` rather than duplicate them;
3. build from a temporary clean export or checkout of that exact tree;
4. invoke `python -m build` in the clean source and require exactly the wheel and
   sdist filenames above;
5. run the existing distribution validator's structural, metadata, privacy,
   clean-install and entry-point checks against freshly built artifacts;
6. verify the approved committed PDF bytes through their strict repository
   manifests and the PDF validator;
7. copy only the seven allowlisted members into a new temporary top-level
   directory, using controlled basenames and refusing symlinks or extra files;
8. create the ZIP with stable member order, normalized POSIX paths, fixed
   timestamps, fixed permissions, and no host-specific archive metadata;
9. build twice independently and require byte-identical ZIPs and identical
   wheel/sdist digests, or record a genuine repeatability failure for review;
10. write one strict LF-terminated checksum line containing the ZIP SHA-256,
    two spaces and its basename; and
11. emit release evidence containing the source commit, tool versions, exact
    inventory, sizes and SHA-256 values for wheel, sdist and ZIP.

Source files and committed PDFs are inputs and are never rewritten by assembly.
Temporary outputs remain outside the repository and are removed after review.
The accepted candidate may be retained only in an explicitly designated private
release staging directory for later Stage 9.4b verification; it is not committed.

## 5. Independent extracted-candidate validation

Validation must extract into a new temporary directory without trusting the
builder. It must reject absolute paths, traversal, links, duplicate names,
unexpected roots, extra or missing members and unsafe permissions. It then:

- compares README, CHANGELOG, LICENSE and both PDFs byte-for-byte with the
  approved source-tree inputs;
- independently recomputes the ZIP checksum and every recorded artifact digest;
- applies strict wheel/sdist member, metadata, license, dependency and privacy
  inspection;
- installs wheel and sdist separately into clean environments and checks both
  entry points, version and representative conversion behavior;
- validates both PDFs, their embedded metadata/fonts/content/navigation and
  their identity with the approved artifacts;
- scans all outer and nested content for private paths, credentials, captures,
  configuration, caches and development-only material; and
- proves extraction and validation do not modify the source tree.

## 6. Checkpoint A audit findings

### A1 — reachable-history privacy conflict — FAIL

The original audit reported 42 maintainer-specific path-marker matches across
16 tracked Markdown files. Exact reconstruction found 38 actual username-bearing
path occurrences across those 16 files; the original count double-counted four
cloud-checkout lines because each matched both the home and cloud expressions.
This refinement preserves the original FAIL. The affected material is present
in all ten commits rooted at `c294ffd`. It includes
`docs/development/DEV_VENV_COMMANDS.md`, thirteen Stage 8 change documents,
`STAGE_9.1a_AUDIT.md` and `STAGE_9.1b_REPORT.md`. Examples reveal a username,
development environment paths, a cloud-synced checkout path and private real-data
dataset roots. The live `DEV_VENV_COMMANDS.md` also presents one such path as an
expected command result.

This is a privacy/publication issue rather than a product-runtime defect. A tip
edit or deletion cannot remove literals from reachable history. The established
Stage 9.4 boundary prohibits rewriting public history, while the current audit
requires inappropriate personal filesystem paths to be absent from history.
Checkpoint A therefore cannot prescribe a compliant unilateral fix. Independent
review must decide whether to authorize a narrowly defined history remediation
before publication or formally accept specific literals as public. Until then,
the public-history and absence-of-private-data closure criteria are **FAIL**.

### A2 — live development command document — FAIL

`docs/development/DEV_VENV_COMMANDS.md` contains `<user-home>/...` and outdated
test paths such as `tests/test_cli.py`; it is unsuitable as current public
development guidance. Regardless of the history decision, B should either
replace those examples with neutral, accurate paths or remove the obsolete live
document after assessing links. This is necessary remediation, not an editorial
preference.

### A3 — public content usefulness — PASS with optional tidiness

The 92 tracked files under `docs/development` are extensive and occasionally
historical, but the Stage records, architecture, packaging decisions, fixture
review and validation evidence provide useful provenance for contributors.
Ordinary users are directed to README and `docs/user`. No broad removal is
recommended solely to shorten the repository. After A1/A2 are resolved, future
archival consolidation may be considered as optional tidiness without erasing
release evidence.

### A4 — fixtures and tracked binaries — PASS

`tools/check_public_inputs.py` passed: exactly ten allowlisted FIT/FITS fixtures
match reviewed byte sizes and SHA-256 values; public history has the expected
root; no blob exceeds 100 MiB; no build distribution is tracked. The nine real
astronomical fixtures remain safe after documented header sanitisation and the
small Siril mosaic is synthetic. The two committed PDFs and their manifests are
intentional release documentation inputs. No blanket FIT/FITS ignore is used.

### A5 — BUG-001 consistency — PASS

Implementation, CLI help, README, public CHANGELOG, current architecture text,
User Guide, Quick Start and approved PDFs describe the corrected behavior:
archive preserves individual light FITS without automatic TIFF conversion or an
observation-level `tiff/` directory, while the Seestar stack companion remains.
Older Stage 7/early project-note statements are preserved historical contracts
and current notes explicitly identify the former behavior. No unresolved
BUG-001 product defect was found.

### A6 — package, CI and publication boundary — PASS/PENDING

Packaging is setuptools based, version 1.1.0, Python `>=3.11,<3.15`, with exact
runtime dependencies and console entry point declared in `pyproject.toml`.
`MANIFEST.in` prunes docs, tests, tools and private data from the sdist. Existing
CI uses macOS 15 arm64 and Python 3.11–3.14 with read-only contents permission;
it runs public-input, pytest, Ruff, formatting, whitespace and distribution
validation and performs no publication. Local repository state has no tag or
release artifact. Remote visibility, release absence and exact-SHA Actions are
PENDING authenticated confirmation at C/9.4b.

## 7. Evidence reuse and required reruns

Checkpoint B may reuse unchanged Stage 9.1a support decisions, Stage 9.1c package
policy, Stage 9.1d CI design, Stage 9.2a Python compatibility, Stage 9.2b installed
behavior, Stage 9.3a guide content validation, Stage 9.3b PDF visual approval and
BUG-001 closure evidence. It must rerun checks affected by a new builder,
candidate contents, privacy remediation or generated distributions.

B must freshly run builder tests, two independent builds, distribution
validation, PDF/manifests, extracted-ZIP validation, artifact privacy scans,
pytest, Ruff, configured formatting, `git diff --check`, public-input/history
checks and changed-document link/fence/whitespace checks. C must rerun every
release-facing and public-history check against the exact proposed closure tree.

## 8. Checkpoint B scope

After A is independently reviewed and the A1 policy conflict is resolved, B may:

- perform only the authorized privacy/current-document remediation;
- implement and test the allowlisted release-candidate builder and independent
  validator;
- produce disposable two-build candidate artifacts outside the repository;
- record hashes, provenance, inventory and failure/remediation chronology; and
- update Stage 9.4a evidence and necessary development status documents.

B must not publish, tag, push, change visibility, date the public changelog,
upload assets, publish to PyPI or begin Stage 9.4b.

## 8A. Checkpoint A privacy-remediation design addendum

This addendum records design only. No history operation has been executed.

### Final DEV_VENV disposition

Git status identifies the user-deleted files exactly as:

- `docs/development/DEV_VENV_COMMANDS.md`;
- `docs/development/DEV_VENV_DIRECTIONS.md`.

Both are private maintainer reference material. They must be absent from the
final tree and from every object reachable from future public `main`. They must
not be recreated, sanitized or replaced in the public repository. Their private
destination is deliberately not recorded. The live references in
`PROJECT_Notes.md` must be removed. Historical Stage 9 migration references
must be replaced with a neutral phrase such as `<private development-environment
notes>` while preserving the fact that private notes were reorganized.

### Exact remediation map

| Affected path/group | Commits | Category | Safe pattern | Proposed treatment | Current tree | History |
| --- | --- | --- | --- | --- | --- | --- |
| Both `docs/development/DEV_VENV_*.md` files | all 10 | private maintainer-only content and environment layout | `<private development-environment notes>` | remove both paths completely | accept intentional deletions | purge path blobs |
| `PROJECT_Notes.md` | all 10 | live references to private-only files | `DEV_VENV_*` | remove the two-line live reference without replacement | change required | rewrite reference from prior trees |
| Stage 9.1a audit and Stage 9.1b report | all 10 | historical references to private-only filenames | `DEV_VENV_*` | use neutral private-notes wording; retain migration chronology | change required | rewrite retained blobs |
| Stage 8.0, 8.1a–d, 8.2a–g and 8.3a | all 10 | private real-data root and dataset paths | `<user-home>/tmp/.../<dataset>` | replace private root with `<private-test-data>`; retain dataset identifiers where technically meaningful | change required | rewrite retained blobs |
| Stage 8.2e–g and 8.3a | all 10 | private development-environment executable | `<user-home>/venvs/...` | replace with `<development-environment>/bin/python` | change required | rewrite retained blobs |
| Stage 8.2e–g and 8.3a | all 10 | cloud-synchronized checkout/import path | `<user-home>/Library/.../<repository>/src/...` | replace with `<repository-root>/src/seestar_toolkit/__init__.py` | change required | rewrite retained blobs |
| Stage 9.1a audit and Stage 9.1b report | all 10 | private development-environment directory | `<user-home>/venvs/.../bin/` | replace with `<development-environment>/bin/` | change required | rewrite retained blobs |

There are 18 distinct paths requiring treatment: two removed DEV_VENV files,
thirteen Stage 8 documents, two Stage 9 documents and `PROJECT_Notes.md`.
Every one of the ten public-lineage commits changes because the affected blobs
were already present in the bootstrap root. Generic temporary paths, generic
`/Volumes/Astronomy/...` user examples, deliberate negative-test markers and
the public author/copyright identity are outside this remediation.

### Controlled rewrite mechanism

If independently authorized, use a dedicated fresh local clone containing only
the ten-commit `main` lineage. Do not run the rewrite in the maintainer's active
worktree and do not rewrite `master`, stashes, private backup refs or other
preserved pre-public history.

1. Confirm the remote remains private and `origin/main` is exactly the expected
   old tip. Fetch without pruning.
2. Create a private offline bare bundle or mirror containing all original refs,
   plus a separate private copy of the current working changes. Record its hash
   and prove it can enumerate `ff0ada1`, `master` and the stash. Do not push a
   backup ref to the future public repository.
3. Create a fresh single-branch rewrite clone from the verified old `main`.
4. Prepare a private `git-filter-repo` replacement file from the exact map. Use
   fixed literal replacements for the private test root, development environment
   and cloud checkout. Keep the replacement file and raw values outside the
   repository and out of command logs/evidence.
5. In one controlled `git filter-repo` operation limited to `main`, remove both
   DEV_VENV paths with `--invert-paths` and apply the literal replacements to
   retained blobs. Do not rewrite commit messages unless a fresh scan proves a
   mapped literal occurs there.
6. Preserve the generated old-to-new commit map. All ten commit IDs will change.
   Compare every mapped old/new tree and permit differences only in the approved
   remediation paths and exact substitutions.
7. Apply the current intentional DEV_VENV deletions, neutralized references,
   Stage 9.4a evidence and preserved pending development CHANGELOG state to the
   rewritten lineage. Update operational root references described below.
8. Run the complete pre-push validation in an isolated worktree. Only an
   independently reviewed PASS may authorize replacement of local `main`.
9. Replace local `main` with an exact compare-and-swap against its verified old
   SHA. Push only `main` using
   `--force-with-lease=refs/heads/main:<verified-old-tip>`; never use a mirror
   push or an unqualified force push.
10. Run post-push validation against the exact fetched remote SHA before any
    visibility change. The repository remains private throughout.

Creating another orphan public root is unnecessary: the existing lineage has
only ten commits, and a path-limited rewrite preserves its order, authors,
dates, subjects and technical chronology while changing only approved blobs.

### Commit-reference policy

Pre-public/private-lineage identifiers such as Stage 8 and earlier commit IDs
remain historical evidence and must not be rewritten merely because they are
mentioned. The ten old public-lineage IDs become pre-remediation identifiers.
Historical Stage reports may retain them as contemporaneous evidence, provided
this Stage 9.4a report records the complete old-to-new map and explains that the
old IDs were superseded by the controlled privacy rewrite.

References that operate on or identify the final public lineage must change to
the mapped IDs. This includes the root assertions in
`tools/check_public_inputs.py`, the CI whitespace fallback, current root/status
statements in `PACKAGING.md` and `PROJECT_Notes.md`, and public-lineage rows in
the development CHANGELOG. Exact operational referrers must be re-inventoried
after filtering. Do not mechanically replace every SHA in historical reports.

### Validation before force-push

The candidate rewritten branch must pass all of the following before remote
replacement:

- exact ten-commit subject/order/author/date comparison plus an archived
  old-to-new commit map;
- allowlisted per-commit tree-difference comparison;
- absence of mapped private literals from the tip, every reachable commit,
  commit messages, tags and all reachable blobs;
- absence of both DEV_VENV paths and their content from every object reachable
  from candidate `main`;
- confirmation that unrelated local branches, stashes and private backups were
  not rewritten and will not be pushed;
- preservation of public author/copyright identity;
- `git fsck --full` on the candidate and successful fresh clone from it;
- ten-fixture manifest/privacy verification, no oversized blob, private capture,
  credential, secret, cache or build artifact;
- exact package/source/test/documentation inventory comparison outside the
  allowlist; historical evidence readability and JSON/Markdown/link validation;
- full pytest, Ruff, configured formatting, whitespace, distribution, installed
  entry-point, PDF/manifest and BUG-001 checks; and
- clean branch state with the candidate tip recorded for independent review.

### Validation after private remote replacement

Fetch the private remote into a new clone and require `origin/main` to equal the
approved rewritten SHA. Repeat the current/history privacy scan, DEV_VENV
absence, fixture/public-input guard, `git fsck`, complete repository quality and
distribution gates, documentation/PDF validation and exact tree comparison.
Verify only `main` moved, repository visibility remains private, no tag or
Release was created, and GitHub Actions for the exact rewritten SHA pass on
Python 3.11–3.14/macOS arm64. Any failure blocks publication and Stage closure.

### Rollback

Keep the verified private bundle/mirror and original worktree untouched until
post-push validation passes. If local validation fails, discard only the
disposable rewrite clone. If validation fails after the private force-push,
keep the repository private, stop publication, and restore old `main` from the
private backup with a force-with-lease against the failed rewritten tip. Fetch
and verify the restored SHA, then diagnose in a new disposable clone. Never
delete the backup, preserved branch or stash as part of remediation.

## 8B. Local privacy-remediation execution

The independently authorized local-only rewrite used `git-filter-repo` 2.47.0
in a fresh single-branch clone. No remote was contacted or modified. The exact
old-to-new mapping is:

| Original public SHA | Rewritten local SHA | Subject |
| --- | --- | --- |
| `c294ffd917634a5d381cccc3ce3fd62a6fba4e89` | `0cdc6c214e87b28925cf938ebf7dc8e75b9dddb2` | Stage 9.1d: bootstrap clean public repository history |
| `bfb947f6263e58473899e09a8c12622050ffc126` | `7109ba7ed4172420ff50929205232f63ea4fc455` | Stage 9.1d: add CI validation workflow |
| `a3b0e9915d8b7d87c43b1e9b202f96310720afcb` | `4c40e5423a590848f886bc8179f47953989119e2` | Stage 9.1d: fix CI whitespace validation |
| `1771b9f31a9a96b35b228a1db9cac3d2c3499ab1` | `c3c14dc31f06f41b81fe882f1d6dce2e98f47ce6` | Stage 9.1d: validate and close distribution CI |
| `398b7712a2145d2017286f7bb4a73bbfecaf24ab` | `1f7de39f725f274341389a151fd2953cdc9f2ece` | Stage 9.2a: validate clean installs and Python compatibility |
| `519f0e393bc24615b9ffdf17471f78bba9a3be7a` | `62cab642be0a29019178d8f6429f785b0fc8c283` | Stage 9.2b: validate installed CLI and storage workflows |
| `41c000fb98fdd42ab6f3f9f486f531eafcb520e2` | `e45ca0df71d69cbb4a70358e767004d65dd563a9` | Stage 9.3a: complete user and public documentation |
| `560b1e0548f9b5b2262bba2df3e49696c8a27b5b` | `e78c3d0cdeefca39a7e123bac59e677ded6e294f` | Stage 9.3b: generate and validate documentation PDFs |
| `89e506b52b494ebf8c598e95c34a12a14b083e12` | `58a57b92efff96da0f41b71e1f021d709a7be0f3` | BUG-001: stop archive light TIFF generation |
| `ff0ada13ddc1236fb8e416821ea5fca7352e18de` | `93a4299ccc56f4f2d82c39afa9c735f9989608a3` | docs: record Stage 9.3b and BUG-001 completion |

The bundle SHA-256 is
`902bae43f1175ca49a24990b4f065b8ca2121d83afbdd1c69faf2af6abfa24db`.
It contains original `main`, `master`, origin tracking refs and the stash. The
separate working-state provenance manifest SHA-256 is
`b368a503da25bf957462d9298fd2187d2eb7743a7ed5a6392f4c33f09b4fc651`.
Neither private backup location is recorded here.

All ten commits mapped once. Ordering, subjects, author/committer identities and
dates are preserved. Every mapped tree equals the exact approved transformation,
limited to the 18 mapped paths. Both DEV_VENV paths and their identifying content
are absent from all rewritten trees and commit messages. Exact private literals
are absent from all reachable rewritten content.

The rewritten committed candidate passed `git fsck --full --strict`, a fresh
local clone, the ten-fixture manifest/privacy and blob-size policy, 332 pytest
tests, Ruff, configured formatting, incremental whitespace, both strict PDF
manifests/PDF validation and isolated wheel/sdist validation. The first gate
attempt used a bare Python lacking pytest/Ruff and encountered checkout mtime
loss for PDFs; rerunning with the established environment and synchronizing only
disposable filesystem mtimes passed without changing tracked bytes.

Local `main` now points to `93a4299`; `origin/main` remains at old `ff0ada1`.
The branches therefore diverge ten commits each until a separately authorized
lease-protected remote replacement. Local remediation is PASS; remote remediation
is PENDING. Privacy closure criteria remain failed/pending until remote history
and exact-SHA Actions are validated.

## 8C. Final post-remote privacy verification

The approved force-with-lease subsequently replaced private `origin/main` with
the rewritten lineage at `93a4299`. GitHub Actions for that exact commit genuinely
failed in all four jobs at **Public fixture and history checks** because the
committed `tools/check_public_inputs.py` still named superseded root `c294ffd`.
The committed CI whitespace fallback also retained that obsolete identifier.
This failure remains a FAIL and is not reinterpreted as successful rewrite
validation.

Dedicated commit `0b0a6bf1f8b987a70a35097455aadf7108a934c9` (`ci: update
public history root after privacy rewrite`) followed `93a4299` and changed the
operational root identifiers to `0cdc6c2`. The user independently confirmed all
four GitHub Actions jobs for exact `0b0a6bf` are green.

A new clone served by the still-private remote verified:

- tip `0b0a6bf`, parent `93a4299`, root `0cdc6c2` and the exact expected
  eleven-commit lineage;
- none of the ten superseded original public commits is reachable from remote
  `main`;
- no mapped private home, dataset, environment or cloud-checkout literal and no
  private DEV_VENV filename/title/content is present in any of the eleven trees
  or commit messages;
- both DEV_VENV paths are absent from the current tree and all objects reachable
  from remote `main`;
- public Mark Wymer author/copyright identity remains in package metadata and
  LICENSE;
- the committed public-input/history guard passes with ten reviewed fixtures,
  the rewritten root and no oversized blob;
- `git fsck --full --strict` passes without output and the fresh clone is clean;
  and
- the remote advertises only `refs/heads/main` at `0b0a6bf` and no tags.

Authenticated GitHub API access was unavailable, so visibility was not
independently queried. The user's explicit confirmation that the repository
remains private is recorded as the visibility evidence. No visibility change,
tag, Release, publication or release artifact was performed.

Current privacy criteria 22, 23, 24, 25 and 37 are now PASS for the controlled
privacy remediation. Their original FAIL/PENDING assessments remain preserved
earlier in this specification/report chronology. Checkpoint B implementation,
candidate construction and every later procedural criterion remain PENDING.

## 8D. Checkpoint B implementation and candidate validation

Checkpoint B used exact committed source
`0b0a6bf1f8b987a70a35097455aadf7108a934c9`. The builder exports that commit,
derives package identity from its `pyproject.toml`, verifies each static release
input byte-for-byte against it, builds the wheel and sdist twice, normalizes
archive metadata, and assembles only the seven allowlisted files. The accepted
candidate and its external checksum remain untracked in private release staging.

The first assembly attempt genuinely failed before artifact creation because
the new wrapper had not created its temporary build parent. After that narrow
fix, the repeatability gate genuinely rejected setuptools sdists whose gzip/tar
metadata varied between builds. Fixed epoch, ownership, permissions and member
ordering were then applied to the sdist; no package payload was changed. The
next two independent builds were byte-identical for wheel, sdist, ZIP and
checksum. These failures remain part of the evidence chronology.

Independent extraction found one root and the exact seven regular files. Strict
outer ZIP and nested wheel/sdist checks reject traversal, links, duplicates and
extras. Both distributions passed metadata, member, privacy, clean-install,
entry-point, version and conversion smoke checks. The committed PDFs and their
manifests passed content, link, metadata, font and page validation and matched
the extracted PDF bytes. Full repository validation passed with 344 tests,
Ruff, 40-path configured formatting, incremental whitespace, ten reviewed
fixtures, Markdown/link/fence checks, Issue-form YAML parsing and isolated
distribution validation.

Criteria 8–21, 39 and 40 are technically PASS. Criteria 1–42 are consequently
PASS on current evidence. Criterion 43 remains PENDING independent review and
authorization for Checkpoint C; criteria 44–49 remain PENDING. No Checkpoint C,
commit, push, tag, publication, visibility change or Stage 9.4b action occurred.

## 9. Checkpoint C scope

C audits the exact intended Stage 9.4a closure tree and repeats the full public
repository/history privacy audit, fixture verification, public-document and
package consistency audit, BUG-001 check, release builder/validator gates and
quality checks. It verifies no publication action occurred and inventories the
candidate without treating it as a release. Independent technical review then
authorizes any closure commit. Post-commit validation and exact-commit CI are
required before a separate formal Stage 9.4a COMPLETE declaration.

## 10. Closure criteria

1. Exact starting baseline, subject, branch/upstream and initial status recorded.
2. Pending Stage 9.3b/BUG-001 development CHANGELOG carry-forward preserved.
3. Version authority and 1.1.0 Unreleased state verified.
4. Relevant Stage 9.1–9.3 and BUG-001 decisions reviewed.
5. Exact seven-member release inventory and filenames established.
6. External ZIP checksum name, format and placement established.
7. Explicit release exclusions established.
8. Clean-source, allowlisted assembly architecture implemented.
9. Builder derives name/version from package metadata and refuses unsafe state.
10. ZIP member order, timestamp, path and permission normalization implemented.
11. Two independent builds prove repeatability for ZIP and inner artifacts.
12. Fresh wheel and sdist pass strict member and metadata validation.
13. Wheel and sdist pass separate clean-install and entry-point validation.
14. Approved PDFs are byte-identical to committed, manifested artifacts.
15. Extracted ZIP has one correct root and exactly seven expected regular files.
16. Extracted text/PDF/license inputs match the approved tree byte-for-byte.
17. ZIP and nested archives reject traversal, links, duplicates and extras.
18. Wheel, sdist and ZIP hashes, sizes, tools and source SHA are recorded.
19. External ZIP checksum independently verifies and is not inside the ZIP.
20. Assembly and validation do not modify source files.
21. Generated candidates/checksums remain untracked and private before release.
22. Current tracked content receives privacy/security review.
23. Every reachable public-history commit receives privacy/security review.
24. No credential, secret, token, private config or unintended personal data remains.
25. No inappropriate personal filesystem path remains in public current/history state.
26. No private maintainer utility/data is tracked or released.
27. No unintended build artifacts, caches or temporary files are tracked/released.
28. No reachable blob exceeds the approved public size policy.
29. Ten FIT/FITS fixtures match the reviewed inventory and privacy record.
30. FIT/FITS ignore policy remains scoped rather than global.
31. Public repository development content has a recorded usefulness disposition.
32. Public README, CHANGELOG, CONTRIBUTING, issue forms and LICENSE are consistent.
33. User Guide and Quick Start remain authoritative and internally consistent.
34. Package metadata and Python/platform/support claims remain consistent.
35. Installation, CLI, archive safety, configuration and privacy claims remain accurate.
36. BUG-001 corrected behavior is consistent across code, tests and release documents.
37. No unresolved product or release-documentation defect remains.
38. Public CHANGELOG remains 1.1.0 Unreleased throughout Stage 9.4a.
39. Full pytest, Ruff, configured formatting and whitespace gates pass.
40. Public-input/history, Markdown/link and distribution gates pass.
41. No tag, release, upload, PyPI publication or visibility change occurs.
42. Checkpoint A evidence/report pass independent review and authorize B.
43. Checkpoint B implementation/evidence pass independent review and authorize C.
44. Checkpoint C exact-tree audit passes every technical criterion.
45. Independent technical closure review accepts the exact proposed tree.
46. Authorized Stage 9.4a closure commit is created without publication action.
47. Exact post-commit validation and exact-commit GitHub Actions pass.
48. Independent review authorizes formal Stage 9.4a COMPLETE declaration.
49. Stage 9.4a is formally declared COMPLETE separately from technical readiness.

Criteria 1–7 and 29–31 are evidenced by A except that privacy criteria 23–25
remain failed. Criteria 8–21 and most final gates are pending B/C. Procedural
criteria 42–49 cannot pass within this Checkpoint A authoring turn.

## 11. Checkpoint A boundary

Checkpoint A creates only this specification, its report and structured evidence.
It does not implement the builder, remediate existing files, assemble candidates,
run expensive validation already established by prior evidence, commit, push,
tag, publish, change visibility or start Stage 9.4b.

## 12. Checkpoint C exact-tree closure-readiness audit

Checkpoint B passed independent review, satisfying criterion 43. Checkpoint C
audited the exact uncommitted tree proposed for the Stage 9.4a closure commit.
Every changed path belongs to the authorized privacy-remediation record, release
builder/validator, focused tests, formatting coverage or Stage status evidence.
No production source, package metadata, public user document, fixture or CI file
is changed by the proposed closure tree. Generated candidate artifacts remain
outside Git.

The PDF hashes reported in Checkpoint B differ from the original Stage 9.3b
hashes for a documented reason. BUG-001 commit `58a57b9` subsequently corrected
both guide Markdown files, regenerated both PDFs and updated both two-entry
manifests. Current repository and committed `0b0a6bf` bytes agree exactly:
Quick Start PDF `32bd5b42...f394f` and User Guide PDF `f9c716ca...d56e3`.
Their pre-BUG-001 Stage 9.3b values remain historical evidence. The privacy
history rewrite did not alter PDF bytes.

Fresh closure-tree validation passed: 344 pytest tests, 12 focused release tests,
Ruff, 40-path configured formatting, incremental and new-file whitespace,
ten-fixture public history guard, both PDF manifests/validators, 88-file Markdown
fence/link validation, three Issue-form YAML files and isolated wheel/sdist
build/install validation. The retained candidate hash and exact seven-member
inventory were reconfirmed without rebuilding it unnecessarily.

Criterion 44 is PASS. Criteria 45–49 remain PENDING in their required sequence:
independent final review, authorized closure commit, exact post-commit validation
and CI, authorization of formal completion, and a separate COMPLETE declaration.
Checkpoint C is PASS and Stage 9.4a is ready for independent final review and
closure commit authorization. No commit, push, tag, Release, publication,
visibility change or Stage 9.4b action occurred.
