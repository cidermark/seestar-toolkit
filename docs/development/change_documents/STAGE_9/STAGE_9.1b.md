# STAGE 9.1b — Repository and Documentation Reorganisation

**Stage:** 9 — Packaging, Documentation and Release
**Step:** 9.1b — Repository/documentation reorganisation
**Starting commit:** `6d72706` — `Stage 9.1a: audit release requirements, compatibility and packaging`
**Target release:** Seestar Toolkit `v1.1.0`
**Status on opening:** STARTED
**Date opened:** 2026-09-10

## 1. Purpose

Stage 9.1b performs the repository and documentation reorganisation identified by the Stage 9.1a audit. It establishes the public/development documentation boundary and prepares the repository for later packaging, CI, user documentation and release work.

The authoritative Stage 9.1a audit is `docs/development/change_documents/STAGE_9/STAGE_9.1a_AUDIT.md`.

This step must not implement Stage 9.1c package metadata/versioning, Stage 9.1d CI/distribution, Stage 9.2 runtime validation, Stage 9.3 final user guides/PDFs, or Stage 9.4 release/publication work.

## 2. Starting state

Start from commit `6d72706`.

Expected dirty state: the detailed development CHANGELOG contains the pending Stage 9.1a entry referencing `6d72706`. This update is intentionally uncommitted and must be carried into the 9.1b commit.

Before changes run:
- `git status --short`
- `git rev-parse HEAD`
- `git log -1 --oneline`

Explain any unexpected starting change before proceeding.

## 3. Target structure

Establish:

```text
README.md
CHANGELOG.md
LICENSE
docs/
  user/
  development/
    DEV_README.md
    CHANGELOG.md
    ARCHITECTURE.md
    PROJECT_Notes.md
    REAL_DATA_TESTING.md
    change_documents/
      STAGE_1/ ... STAGE_9/
```

Inspect actual historic change-document names rather than guessing. Preserve Stage 1–8 content and history as far as practical.

## 4. Development documentation migration

- Preserve the existing developer-oriented root README as `docs/development/DEV_README.md`.
- Create only a concise transitional root `README.md`: identify Seestar Toolkit, say v1.1.0 release preparation is in progress, avoid unsupported installation/support claims, and point developers to `docs/development/DEV_README.md`. Stage 9.3a owns the final public README.
- Move `docs/CHANGELOG.md` to `docs/development/CHANGELOG.md`, preserving all detailed history and the pending Stage 9.1a entry referencing `6d72706`.
- Create concise public root `CHANGELOG.md`; v1.1.0 remains **Unreleased** with no invented publication date.
- Move `docs/ARCHITECTURE.md` to `docs/development/ARCHITECTURE.md`.
- Move `docs/PROJECT_Notes.md` to `docs/development/PROJECT_Notes.md`.
- Classify other existing `docs/` files by audience and move development-only/reference material appropriately. Do not move files merely for visual tidiness.
- Update live repository references to moved paths.

`PROJECT_Notes.md` remains the authoritative internal future-enhancement record. Preserve/record: S50 Pro, S30, S30 Pro validation/support; DSLR/conventional-camera ingestion/archive; Solar/Lunar/Planetary MP4 processing; GUI; easier/native macOS installer; privacy-conscious diagnostics; possible Linux/Windows; possible PyPI; possible GitHub Discussions. Do not create `ROADMAP.md`.

## 5. Historic change documents

Migrate historic Stage 1–8 change documents to `docs/development/change_documents/`.

Requirements:
- preserve content/evidence;
- preserve understandable stage grouping;
- use `git mv` where practical;
- do not retrospectively rewrite historic specifications;
- update live references to old paths.

The existing Stage 9 bootstrap directory remains `docs/development/change_documents/STAGE_9/` and contains 9.1a, its audit, and this 9.1b specification.

## 6. User documentation foundation

Create `docs/user/`.

Stage 9.3 later owns:
- `SEESTAR_TOOLKIT_QUICK_START.md/.pdf/.sha256`
- `SEESTAR_TOOLKIT_USER_GUIDE.md/.pdf/.sha256`

Do not create final guide content now. If needed, use `.gitkeep` only to retain the empty directory.

## 7. REAL_DATA_TESTING.md

Create `docs/development/REAL_DATA_TESTING.md`.

It must explain:
- real FIT/FITS datasets are tested locally and need not be committed;
- developers use their own local datasets;
- FIT/FITS headers can contain GPS/location, telescope/device identifiers, timestamps and other potentially identifying metadata;
- files should be inspected before public sharing;
- representative validation should cover relevant capture varieties;
- private datasets stay outside tracked public content;
- safe synthetic/generated/anonymised fixtures may remain tracked.

Do not include Mark's private dataset paths, coordinates or personal capture metadata.

## 8. Private data and tracked FITS fixtures

Do not globally ignore `*.fit` or `*.fits`.

Establish/document a narrowly scoped local/private real-data location or naming convention and add a narrow `.gitignore` rule only if needed.

Review the ten tracked FITS fixtures flagged by 9.1a for public suitability. For each, determine whether it is safe/synthetic or contains identifying metadata requiring remediation.

If safe remediation requires substantive fixture/test changes beyond this reorganisation, report it as a blocker/downstream action rather than weakening coverage or improvising. Never silently delete evidence.

Do not move/copy private Stage 8 datasets into the repository.

## 9. Reference audit

Search all tracked files for old live references including:
- `docs/CHANGELOG.md`
- `docs/PROJECT_Notes.md`
- `docs/ARCHITECTURE.md`
- `docs/change_documents`
- old README/development paths.

Update live references. Historic prose may remain when it describes historical state rather than serving as a live instruction/path.

## 10. GitHub boundary

No GitHub repository currently exists. Preserve that state.

Do not create a GitHub repository, add a remote, authenticate GitHub, push, or publish anything. GitHub setup will be performed deliberately with the user in a later Stage 9 step.

## 11. Explicit exclusions

Do not implement:
- 9.1c package metadata/version-source/dependency changes;
- 9.1d CI/GitHub Actions/distribution;
- final Python support declarations;
- 9.2 clean-install/runtime validation;
- final User Guide/Quick Start;
- PDF/checksum pipeline;
- release ZIP/tag/publication/PyPI;
- new capture/camera support;
- unrelated production refactors.

## 12. Validation

Run/report:
- full pytest suite (baseline 314; explain differences);
- Ruff;
- applicable formatting;
- `git diff --check`;
- final `git status --short`.

Validate moved files, live references, historic change documents, intact 9.1a spec/audit, detailed history, 9.1a CHANGELOG entry `6d72706`, root v1.1.0 Unreleased status, no private data addition, and no GitHub action.

Use Git diff/rename detection where practical to guard against migration data loss.

## 13. Closure criteria

Stage 9.1b passes only if all 58 criteria pass:

1. Starting commit is `6d72706`.
2. Pending 9.1a detailed CHANGELOG entry is recognised/preserved.
3. No unexpected starting change is ignored.
4. `docs/development/` is established.
5. `docs/user/` is established.
6. Developer README content is preserved in `docs/development/DEV_README.md`.
7. Root README is a safe transitional user-facing document without unsupported claims.
8. Detailed development CHANGELOG is `docs/development/CHANGELOG.md`.
9. Detailed CHANGELOG preserves prior history.
10. It includes the carried 9.1a entry with `6d72706`.
11. Concise public root `CHANGELOG.md` exists.
12. Public v1.1.0 remains Unreleased.
13. No invented v1.1.0 publication date appears.
14. Architecture docs are under `docs/development/`.
15. Project Notes are under `docs/development/`.
16. Project Notes remain the authoritative internal future-enhancement record.
17. Required future enhancement categories are preserved/recorded.
18. No separate ROADMAP is created.
19. Historic change documents are migrated under `docs/development/change_documents/`.
20. Historic contents/evidence are preserved.
21. Stage grouping remains understandable.
22. 9.1a specification remains intact.
23. 9.1a audit including original FAIL and R1 history remains intact.
24. 9.1b specification is at the correct path.
25. Other development-only docs are classified/moved appropriately.
26. Every moved file is identified in the completion report.
27. `REAL_DATA_TESTING.md` exists.
28. It explains private local real-data testing.
29. It warns about identifying/location FITS metadata.
30. It discloses no private paths, coordinates or personal capture metadata.
31. No private Stage 8/personal dataset is added.
32. No global FIT/FITS ignore is introduced.
33. A narrow private-real-data strategy is documented.
34. Flagged tracked FITS fixtures receive explicit public-suitability review.
35. No fixture is silently removed or coverage weakened.
36. Substantive fixture remediation is recorded rather than improperly performed.
37. Live references to moved docs are updated.
38. No live instruction depends on obsolete doc paths.
39. Historic prose is not unnecessarily rewritten.
40. No production behaviour changes.
41. No 9.1c packaging/version implementation.
42. No 9.1d CI implementation.
43. No final Python-support claim.
44. No final User Guide/Quick Start implementation.
45. No PDF/checksum pipeline.
46. No release artifacts assembled.
47. No GitHub repository created.
48. No GitHub remote added.
49. No GitHub publication.
50. Full tests pass.
51. Ruff passes.
52. Applicable formatting passes.
53. `git diff --check` passes.
54. Migration has no unexplained data loss.
55. Completion report explicitly evaluates all criteria.
56. PASS only if every criterion passes.
57. No commit before ChatGPT closure review.
58. Stage 9.1c is not started.

If any criterion fails, return FAIL; do not weaken or rewrite it to obtain a pass.

## 14. Commit/CHANGELOG workflow

Do not commit until ChatGPT reviews the completion report.

After approval:
- commit message: `Stage 9.1b: reorganise repository and documentation`;
- user supplies actual commit ID;
- add 9.1b entry with that ID to `docs/development/CHANGELOG.md`;
- leave that CHANGELOG update pending for 9.1c.

Do not start 9.1c before 9.1b is passed and committed.

## 15. Required Codex completion report

Return:
1. PASS/FAIL recommendation.
2. Starting commit and initial status.
3. Complete created/moved/modified/deleted summary.
4. Documentation migration summary.
5. Historic change-document migration summary.
6. Root README/public CHANGELOG status.
7. Detailed development CHANGELOG status.
8. Project Notes future-enhancement status.
9. REAL_DATA_TESTING/private-data policy.
10. Tracked FITS privacy-review result.
11. Repository-reference audit.
12. Confirmation of no production/packaging/CI/GitHub/publication work.
13. Full test result.
14. Ruff result.
15. Formatting result.
16. `git diff --check`.
17. Explicit evaluation of all 58 criteria.
18. Current `git status --short`.
19. Remaining blockers/downstream actions.
20. Confirmation no commit was made.
21. Confirmation 9.1c was not started.
