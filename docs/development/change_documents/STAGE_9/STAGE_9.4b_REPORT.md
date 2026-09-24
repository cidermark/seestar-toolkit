# Stage 9.4b Report

## Checkpoint A — Gate 1 and publication design

**PASS (audit/design only). Stage 9.4b remains STARTED.**

### Starting evidence

Local inspection found `HEAD` at
`6784f8d3fc2af7814cdf9e7c328fa0eef2981b06`, subject
`Stage 9.4a: assemble and validate release candidate`, with parent `0b0a6bf`.
The initial tree contained only the expected pending Stage 9.4a development
CHANGELOG row. Local tags were absent. A read-only remote query showed
`origin/main` at the same SHA and no remote tags. The release owner independently
confirmed PRIVATE visibility and GREEN Actions for exact commit `6784f8d`.

GitHub CLI is not authenticated here. Visibility, Actions details, Releases and
settings require authenticated UI/API evidence at execution gates. No server
evidence is invented.

### Findings and policy resolution

The package already declares 1.1.0. Root CHANGELOG, root README and both guide
Markdown sources still say Unreleased; README and Quick Start also use future
publication wording. Guide edits require reproducible PDF regeneration, strict
manifest updates and new pinned source hashes. The candidate validator currently
requires the literal Unreleased heading and needs a final-state rule and tests.

Stage 9.1a allowed a tagged ZIP to retain Unreleased followed by a documentation
update. The current requirement that the final tag carry the correct date
supersedes that option. The specification now uses the release date deliberately
declared by the release owner. The approved/tagged commit must contain that date,
and publication proceeds as one controlled operation associated with it. Gate 2
records the actual GitHub timestamp and verifies the tag and exact commit. An
incidental UTC rollover during that continuous operation is harmless. A
deliberate postponement to a newly chosen release day requires updated affected
outputs, a complete Gate 1 rerun and a new GO. Backdating and silent public-tag
movement are prohibited.

### Result and accounting

The specification defines 60 criteria: 12 design, 16 Gate 1, 12 publication,
15 Gate 2 and 5 closure. Criteria 1–12 PASS. Criteria 13–60 are PENDING because
no final edit, release commit, tag, publication, Gate 2 or closure occurred.

Gate 1 requires the exact clean dated commit and all repository, PDF,
distribution, reproducibility, clean-install, privacy and exact-SHA CI checks.
The proposed commit subject is `Release Seestar Toolkit v1.1.0`. Any missing or
failed evidence is NO-GO.

After GO and authorization, the annotated tag and twice-built artifacts are
verified while private. The tag is pushed and verified before visibility changes.
A normal Release then receives only the ZIP and external checksum. No PyPI.
Gate 2 uses fresh unauthenticated public downloads; only its independent PASS
permits final completion.

| Criteria | Area | Status |
| --- | --- | --- |
| 1–12 | Audit/design | PASS |
| 13–28 | Gate 1 | PENDING |
| 29–40 | Publication | PENDING |
| 41–55 | Gate 2 | PENDING |
| 56–60 | Final closure | PENDING |

### Preservation

The pending Stage 9.4a development CHANGELOG row remains unchanged. No public
release-state file, production source, package metadata, test, CI file, PDF or
release artifact changed. No commit, tag, push, visibility change, Release,
upload, PyPI action or Gate 2 action occurred.

## Checkpoint B — proposed final v1.1.0 release state

**Technical result: PASS. Criteria 26–28 remain PENDING.**

Checkpoint B started with `HEAD == origin/main ==
6784f8d3fc2af7814cdf9e7c328fa0eef2981b06`, no local or remote tags, the
accepted Checkpoint A changes and pending Stage 9.4a development CHANGELOG row.
PRIVATE visibility remains release-owner evidence because GitHub CLI is not
authenticated.

The owner-declared date is `2026-09-23`. Root CHANGELOG, README and both guides
now carry the final release state. Only headings and future-tense download text
changed; support, safety and product content were preserved. Package metadata
was already 1.1.0.

### PDF evidence

Pandoc 3.11 and XeLaTeX `3.141592653-2.6-0.999998 (TeX Live 2026/Homebrew)`
generated each PDF twice with byte-identical results. Independent content,
navigation, link, geometry, page-number, embedded-font, metadata/privacy,
timestamp and manifest validation passed. Rendered inspection covered all 32
pages with no visible clipping, overflow, blank-page, glyph or transition defect.

| Document | Markdown SHA-256 | PDF SHA-256 | Pages |
| --- | --- | --- | ---: |
| Quick Start | `6eff27daf2e0424dda33727fa0be65c08bd6ab2f7b5fdedf3ca9f27831def8f6` | `0f53427c2f3f6c3527eda561bd177214f7ca21e9d90c62e004f78ac2f5b88fb0` | 5 |
| User Guide | `6da3bb935401535a7145cfda3ecdc1ed0da4bf23bd0f534f4883f8dc800faa25` | `ef423be5a4215d13208bfef4e6752d0b6fba04ff3570e1494ee7a59a33b0d5ad` | 27 |

Pinned hashes match. Release validation now requires a real ISO calendar date
and tests reject `Unreleased`, non-ISO and impossible dates.

### Candidate and installation evidence

The uncommitted proposed tree was copied to an isolated temporary repository;
only that copy received a validation commit so the commit-only builder could run.
It is not a project commit/ref/tag or release provenance SHA. Two builder
invocations, each containing two builds, produced byte-identical results:

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| Wheel | 47,807 | `e7edceb7c81ae99c006fef783f0e04939727c4635d1f0928984faf11ed9d3265` |
| Normalized sdist | 34,036 | `19aefb4d8f815e7f441ef2eec11320f46df6081875e4a35652f2843bf951601d` |
| Release ZIP | 243,118 | `6793535544b5709ee50430be1d742e9eae278e9c644568d07d2d61c15b8cf368` |
| External checksum | 100 | `0514ef8871656702062480935d1d746505b2dc058d216ec507f4f13448fdfb6a` |

The checksum line is exact. Extraction found one versioned root and seven
approved files. Wheel/sdist had 39/46 allowed members, correct metadata,
dependencies, Python range, licence and entry point, and no private/development
payload. Separate clean installs passed `pip check`; both entry points reported
1.1.0; both installed float32 FITS-to-TIFF smoke tests passed. Artifacts remain
outside the repository and are not final tagged-release artifacts.

### Quality, privacy and BUG-001

- Full pytest: **349 passed, 2 expected duplicate-archive warnings**.
- Focused release tests: **17 passed, 2 expected warnings**.
- Ruff PASS; formatting PASS (`40 files already formatted`).
- `git diff --check` and direct changed-file whitespace PASS.
- Public-input/history guard PASS: 10 fixtures, clean public root, no oversized blobs.
- Distribution, Markdown/fences/links/navigation and three Issue YAML files PASS.
- Proposed-addition and candidate privacy scans PASS.
- BUG-001 wording and regression behavior PASS: lights receive no automatic
  TIFF, stack companion TIFF remains, standalone conversion remains separate.

### Preserved failure/remediation chronology

1. Initial Ruff/formatting failed on new `UP012` and two formatting differences;
   exact minimal corrections were applied; rerun PASS.
2. Initial distribution validation failed when sandbox DNS blocked PyPI; the
   unchanged network-approved rerun passed. No package defect was found.
3. Direct whitespace found a pre-existing whitespace-only line in development
   CHANGELOG; only its spaces were removed and the pending row preserved; PASS.
4. Ad hoc YAML/privacy commands initially used a Python without PyYAML and
   scanned a validator's own pre-existing forbidden-marker constants. Corrected
   environment and added-lines/untracked scans passed.

### Criteria 13–28

| Criterion | Status | Reason |
| ---: | --- | --- |
| 13–25 | PASS | Final state, tests, quality, privacy, documents/PDFs, reproducibility, artifacts, installs and smoke all pass. |
| 26 | PENDING | Requires authorized final commit and clean committed tree; artifacts are excluded. |
| 27 | PENDING | Requires push/synchronization and exact-final-commit Actions. |
| 28 | PENDING | Requires independent review and explicit Gate 1 GO. |

No unresolved technical defect remains. The proposed tree awaits independent
review and commit authorization. No real commit, push, tag, visibility change,
Release, upload, PyPI publication or Gate 2 action occurred.

## Checkpoint C — private tag and final artifacts, first attempt

**FAIL — STOP before remote tag push.**

Gate 1 was independently accepted as GO for exact release commit
`b954d97b92a11f389a6378d3f5ca462a6a455217`, with criteria 1–28 PASS and
release-owner authorization to create and push the private annotated tag.

Local annotated tag `v1.1.0` was created with tag-object SHA
`37c7d27d689a6e483251ac4c02a56ab908bd9b97`, annotation
`Seestar Toolkit v1.1.0`, and exact target `b954d97b92a11f389a6378d3f5ca462a6a455217`.
It was the only local tag. A fresh clean detached checkout resolved to that
commit.

Two independent release-builder invocations from the tagged checkout passed;
each also proved its two internal builds byte-identical and completed ZIP,
distribution, PDF, clean-install, both-entry-point and conversion-smoke
validation. Both invocations produced:

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| Wheel | 47,807 | `ee34d766c6bc1e6291fe62bc73e0257ada22080aae41775f7e5ef20e9ce91617` |
| Normalized sdist | 34,033 | `28f6a2fa9b9f4293f62812a1c7c5ab3894a61ef2eca6335972f733021f3476a5` |
| Release ZIP | 243,115 | `8953bd71ff12a7fc173d9aa28bff6882e1cb2f208f931baad3876226adabf361` |
| External checksum | 100 | `b8f70961f998cef51be25231c0257779517e8f81f6fc05a9b85dc0c4a9db0e00` |

Direct comparison confirmed the two ZIPs and checksum files were identical.
The checksum verified the ZIP. Independent extraction confirmed the exact
seven-file inventory, tagged README/CHANGELOG/LICENSE/PDF byte matches, and no
private marker in release or nested distribution content.

The required STOP occurred when final verification exposed that the committed
Checkpoint B report and JSON had incorrectly recorded the earlier checksum file
as 101 bytes. The actual earlier file was also 100 bytes. Its recorded SHA-256
and content were correct, but the byte-count statement was a genuine evidence
defect in the approved/tagged commit. This working-tree remediation corrects the
number while preserving this failure chronology; it does not alter the tag.

The initial local tag command was also blocked by sandbox permission before any
tag was created. The unchanged authorized command succeeded with repository
metadata permission. A later supplemental validation command used an unintended
working directory after `cd`; its preceding comparisons passed, but subsequent
PDF/public-input commands did not run in that invocation. The committed builder
had already completed those checks successfully. Neither operational failure is
reinterpreted as an initial pass.

The tag was not pushed. A remote query confirmed zero remote tags and
`origin/main` remained at the approved commit. Repository visibility remains
PRIVATE by release-owner confirmation. The PyPI JSON endpoint returned HTTP 404.
No visibility change, GitHub Release, upload, PyPI publication or Gate 2 action
occurred.

Criteria 29 and 30 PASS. Criterion 31 PASS. Criterion 32 is FAIL because the
complete final local verification found the evidence discrepancy. Criterion 33
is PENDING until corrected evidence is committed and independently validated.
Criteria 34–39 remain PENDING. Criterion 40 PASS. Publication remains stopped.

### Checkpoint C evidence remediation

The live Checkpoint B report table and structured evidence now state the proven
100-byte size. Repository-wide search found no other live 101-byte assertion;
remaining occurrences describe the genuine rejected claim in this chronology.
No public release-state file, source, package metadata, PDF, manifest, release
tool, tag or artifact was changed. The local-only tag remained untouched with
the same object, annotation and target throughout remediation.

This evidence-only remediation does not convert the Checkpoint C FAIL into a
PASS and does not resume publication. Criteria 32 and 33 remain FAIL/PENDING
until a corrected evidence commit is independently validated and Gate 1 is
explicitly re-established. Criteria 34–39 remain PENDING.

## Checkpoint D — Gate 2 public verification

**FAIL — public artifacts pass, but the curated Release notes omit one required
source-archive distinction. Stage 9.4b remains STARTED.**

The evidence-only Checkpoint C correction was independently accepted and
committed. Publication then used commit
`bf3af815f15704eb75965a6831c06db3859a3ce9`, subject
`Stage 9.4b: correct release evidence`. The original Checkpoint C FAIL above
remains genuine and unchanged.

### Public identity and server state

An unauthenticated fresh HTTPS clone and GitHub's public API prove that the
repository is PUBLIC, public `main` is exactly `bf3af815`, and annotated tag
`v1.1.0` has tag-object SHA `653e8a03bc4befd65036439d868e4563ba26cd20`,
exact annotation `Seestar Toolkit v1.1.0`, and dereferenced target `bf3af815`.
Only branch `main` and tag `v1.1.0` are present.

Normal Release ID `395669312` is named `Seestar Toolkit v1.1.0`, is neither a
draft nor a prerelease, is Latest, and uses tag `v1.1.0`. It was created at
`2026-09-24T10:48:59Z` and published at `2026-09-24T12:43:39Z`. The tag target,
not the Release API's mutable `target_commitish` label, proves the exact Release
commit is `bf3af815`.

Actions run `35872684075` is tied to exact SHA `bf3af815`; all four macOS arm64
jobs for Python 3.11, 3.12, 3.13 and 3.14 completed successfully. The public
PyPI JSON endpoint for Seestar Toolkit 1.1.0 returns HTTP 404.

### Public downloads and installed validation

Fresh public downloads contained exactly the two intended uploaded assets.
GitHub additionally presents its two automatic source-code archives.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| Release ZIP | 243,119 | `b8cb2a2be2af8ec817462d0c3d861f474f388f07e67b419ffd73cabb5b757429` |
| External checksum | 100 | `c7a97dfb25e037ca89e970efb156e0104013e44201e6f672c5f795a403929add` |
| Embedded wheel | 47,807 | `97fa0a37ba8803aa8c0d0468c8221170046bb9c5484b2bf5a9701af87e284a4d` |
| Embedded normalized sdist | 34,036 | `e0b9f6e803924e99d2cc1a67ba41693fb55fdfff8555b0ee02bb9faf255f9f33` |

The checksum validates the downloaded ZIP. Independent extraction found one
versioned root and exactly the seven approved files: CHANGELOG, LICENSE, README,
both PDFs, the wheel and the sdist. The committed release validator passed
against those downloaded bytes and exact source ref `v1.1.0`. It proved source
file byte identity; wheel/sdist allowlists of 39/46 members; metadata, licence,
entry point and privacy rules; both clean Python 3.13 installs; clean `pip
check`; both console and module entry points reporting 1.1.0; both installed
float32 FITS-to-TIFF conversion smokes; and PDF content, navigation, fonts and
metadata/privacy. The validator reports source commit `bf3af815` and the same
four artifact hashes above.

### Repository and documentation validation

- Full pytest: **349 passed, 2 expected duplicate-archive warnings**.
- Focused release/distribution tests: **24 passed, 2 expected warnings**.
- Ruff PASS; configured formatting PASS (`40 files already formatted`).
- `git diff --check`, direct evidence-file whitespace and fresh-clone repository
  integrity PASS.
- Public-input/history guard PASS: 10 fixtures, clean public root, expected
  rewritten root and no oversized blobs.
- Fresh public-clone Markdown fence/local-link validation PASS across 92 files;
  all three Issue-form YAML files parse and have their required structure.
- Public README, dated CHANGELOG, LICENSE, guides, PDFs, support boundaries and
  privacy wording PASS. No private utility, private capture, release build or
  unsupported capability is exposed.

An attempted repository `--all` PDF validation reported a source/PDF
nanosecond-mtime mismatch after checkout. Git does not preserve committed file
mtimes, so this generation-workspace invariant cannot be reconstructed from a
fresh clone. The Gate 2 release-artifact validator's candidate mode is the
applicable public-byte check and passed both PDFs against the exact tagged
sources. No PDF byte, manifest or content discrepancy was found.

Read-only operational failures are preserved: an initial asset-download command
used the API host with browser download paths and received HTTP 404; using the
exact API-provided public URLs succeeded. The first clean-install validator run
was blocked by sandbox DNS; the unchanged network-enabled rerun passed. Initial
ad hoc focused-test/PDF commands named a nonexistent test file and used invalid
PDF-validator arguments; corrected commands produced the results above. These
were command/environment failures, not product or public-asset defects.

### Gate 2 failure

The curated Release body identifies
`seestar-toolkit-1.1.0-release.zip` as the supported package and the external
checksum as its verifier, but it does **not** state that v1.1.0 is not published
to PyPI, and it does **not** state that GitHub's automatic source archives are
source snapshots rather than the recommended release ZIP. The authoritative
specification requires both points in the curated body. Consequently publication
criterion 37 and Gate 2 criterion 44 FAIL. Criterion 39 is also not satisfied in
the published notes, although GitHub's interface separately labels the automatic
archives as source code. No product code or uploaded artifact is affected.

The audit made no Release or asset change, as required. Because any failed Gate
2 requirement is Gate 2 FAIL, criterion 55 is FAIL. Criteria 41–43 and 45–54
PASS. Criterion 56 PASS because the complete failure/remediation chronology is
preserved. Criterion 57 PASS with the public provenance above. Criterion 58 is
PENDING because private-runbook finalization was not independently evidenced in
this audit. Criteria 59–60 remain PENDING. Stage 9.4b, Stage 9.4, Stage 9 and
the v1.1.0 release process cannot yet formally close.

## Checkpoint E — Gate 2 Release-note remediation revalidation

**PASS — Gate 2 criteria 41–55 now pass. Final closure criteria remain
pending.**

Checkpoint D's original Gate 2 FAIL remains preserved above. The release owner
subsequently edited only the existing GitHub Release description. An
unauthenticated public API inspection of Release ID `395669312` found both
required additions in the live body:

- `Seestar Toolkit v1.1.0 is not published to PyPI.`
- GitHub's automatic **Source code (zip)** and **Source code (tar.gz)** files
  are identified as GitHub-generated source snapshots, are explicitly described
  as not being the recommended package, and users are directed to the validated
  `seestar-toolkit-1.1.0-release.zip` instead.

This wording satisfies the authoritative no-PyPI and generated-source-archive
requirements. The Release remains named `Seestar Toolkit v1.1.0`, uses tag
`v1.1.0`, and remains neither draft nor prerelease. Its original publication
timestamp is `2026-09-24T12:43:39Z`; the API reports the post-edit Release
update timestamp as `2026-09-24T13:33:00Z`.

The two uploaded assets remain unchanged from Checkpoint D. The ZIP is 243,119
bytes with SHA-256
`b8cb2a2be2af8ec817462d0c3d861f474f388f07e67b419ffd73cabb5b757429`;
the checksum file is 100 bytes with SHA-256
`c7a97dfb25e037ca89e970efb156e0104013e44201e6f672c5f795a403929add`.
Both retain API update timestamp `2026-09-24T12:37:09Z`, before the Release-note
edit. No tag, asset, repository release file, GitHub Release identity or PyPI
state was changed by this evidence pass.

Criteria 37, 39 and 44 now PASS against the remediated live description. With
the previously proven criteria 41–54 all passing, independent revalidation now
records criterion 55 PASS and overall Gate 2 PASS.

Criterion 56 remains PASS because both the initial FAIL and subsequent
remediation are preserved. Criterion 57 remains PASS. Criterion 58 remains
PENDING: the available repository and public evidence do not independently
establish that the private release runbook was finalized. To close it, the
release owner must confirm that the private runbook has been updated from the
actual proven operation and contains the prerequisites/date rule, final edits,
Gate 1 evidence and GO, exact tag/build/provenance, push/visibility/Release/upload
sequence, Gate 2 results and stop procedures required by the specification.

Criteria 59 and 60 remain PENDING because criterion 58 and the independent
formal closure declarations have not occurred. Therefore Stage 9.4b, Stage 9.4,
Stage 9 and the v1.1.0 release process cannot yet formally close, despite Gate 2
now passing.

## Checkpoint F — final closure audit

**PASS — all 60 criteria pass. Stage 9.4b, Stage 9.4, Stage 9 and the
v1.1.0 release process are COMPLETE.**

The release owner confirms that private `SEESTAR_TOOLKIT_RELEASE_PROCESS.md` is
present and readable in the private companion directory, has been reviewed, and
is suitable as the operational release runbook reconstructed from the actual
v1.1.0 operation. The confirmed coverage includes prerequisites and date policy;
final-state preparation; Gate 1 evidence and GO; release commit and exact-commit
CI; annotated tag and reproducible tagged-source builds; artifact inventory,
hashes and provenance; private tag push and final review; visibility transition;
Release and asset publication; Gate 2 public downloads, checksum, clean installs
and conversion smoke; stop/remediation rules; public-tag immutability; generated
source archives; no-PyPI policy; closure/bookkeeping; the reusable checklist;
and the proven v1.1.0 identity and Gate 2 FAIL-to-remediation-to-PASS chronology.

This explicit release-owner confirmation is the required evidence for criterion
58, which now PASSes. The private runbook was not opened, copied, summarized
beyond the owner's supplied coverage, or added to the public repository.

All preceding criteria remain valid. Checkpoint D remains the genuine initial
Gate 2 FAIL; Checkpoint E remains the subsequent remediation PASS. Criteria 56
and 57 remain PASS, and criterion 58 now PASSes. Independent final review finds
no remaining failed or pending prerequisite, so criterion 59 PASSes and formally
closes Stage 9.4b and Stage 9.4. Criterion 60 PASSes and formally closes Stage 9
and the v1.1.0 release process.

The exact release identity remains commit
`bf3af815f15704eb75965a6831c06db3859a3ce9`, annotated tag `v1.1.0`, tag object
`653e8a03bc4befd65036439d868e4563ba26cd20`, annotation
`Seestar Toolkit v1.1.0`, and dereferenced target `bf3af815`. Local `main` and
`origin/main` remain equal. The public Release and its two uploaded asset bytes
remain unchanged after the accepted description-only remediation.

Final accounting is criteria 1–12 PASS, 13–28 PASS, 29–40 PASS, 41–55 PASS and
56–60 PASS. No product or public release file changed. No tag, Release, asset or
PyPI operation occurred during closure.
