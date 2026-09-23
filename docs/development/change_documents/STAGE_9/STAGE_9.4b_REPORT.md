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
| External checksum | 101 | `0514ef8871656702062480935d1d746505b2dc058d216ec507f4f13448fdfb6a` |

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
