# Stage 9.1d — Distribution Build, CI and Package Validation

**Stage:** 9 — Packaging, Documentation and Release
**Step:** 9.1d — Distribution build, CI and package validation
**Public-history starting commit:** `c294ffd` — `Stage 9.1d: bootstrap clean public repository history`
**Pre-public predecessor:** `6a6ddf7` — `Stage 9.1c: configure package metadata, versioning and builds`
**Target release:** Seestar Toolkit `v1.1.0`
**Status on opening:** STARTED

---

## 1. Purpose

Stage 9.1d establishes and validates the automated build and continuous-integration foundations required for the Seestar Toolkit v1.1.0 release.

This step must:

- implement a straightforward GitHub Actions CI workflow;
- validate source-distribution and wheel builds from the clean public-history repository;
- validate package metadata and distribution contents;
- run the automated test suite and code-quality checks in CI;
- exercise the candidate Python-version matrix identified during Stage 9.1a/9.1c;
- confirm that CI does not accidentally imply broader operating-system support;
- prove that public CI depends only on repository-safe fixtures and declared dependencies;
- confirm that generated release artifacts are not committed;
- preserve the strict separation between build/validation automation and release publication.

Stage 9.1d does **not** determine the final supported Python-version range. That decision remains evidence-driven and belongs to Stage 9.2a.

---

## 2. Public-history boundary

Before the formal implementation portion of Stage 9.1d, the repository was moved to a clean GitHub-visible history root because:

- the earlier local development history contained a 272,923,200-byte FITS fixture that exceeded GitHub's regular Git object limit;
- tracked FITS fixtures required a privacy/publication review before first publication;
- the oversized Siril mosaic fixture was replaced with a small deterministic synthetic fixture;
- nine remaining real-data FITS fixtures were sanitised at header level while retaining their original pixel data;
- the resulting public-safe snapshot was committed as `c294ffd`.

The earlier local development history remains private and separately archived.

Development documents created before the bootstrap intentionally retain their historical commit identifiers. Those identifiers refer to the archived pre-public repository and are not required to resolve in the GitHub-visible `main` history.

`docs/development/PUBLIC_HISTORY_BOOTSTRAP.md` records this boundary and rationale.

No Stage 9.1d implementation may attempt to rewrite, recreate, or retroactively renumber historical development records.

---

## 3. Starting state

At the formal implementation start of Stage 9.1d:

- branch: `main`;
- public-history baseline: `c294ffd`;
- `origin/main` points to the same commit;
- GitHub repository exists and is private;
- no CI workflow has yet been implemented;
- the working tree should be clean before implementation begins;
- the original local `master` branch remains preserved as a private pre-public-history reference;
- the pre-public Stage 9.1d safety stash may remain temporarily preserved;
- package metadata/build configuration from Stage 9.1c is present;
- authoritative package version is `1.1.0`;
- 323 automated tests passed after public fixture remediation;
- the public fixture set has completed privacy review;
- no tracked object in the public `main` history exceeds GitHub's 100 MiB regular Git object limit.

---

## 4. Scope

### Included

Stage 9.1d includes:

- GitHub Actions CI workflow design and implementation;
- candidate Python-version CI matrix;
- pytest, Ruff and applicable formatting checks;
- incremental `git diff --check`;
- standards-compliant wheel and sdist builds;
- package metadata and file-content inspection;
- clean installed-wheel functional smoke validation;
- installed-sdist smoke validation where practical;
- console-script and `python -m seestar_toolkit` validation;
- version consistency and runtime-dependency validation;
- confirmation that generated build outputs remain untracked;
- public-repository CI-safety checks;
- development documentation updates where necessary;
- actual GitHub Actions execution on the private repository;
- recorded CI evidence sufficient for closure review.

### Explicitly excluded

Stage 9.1d must **not**:

- publish to PyPI or configure PyPI publishing;
- create or publish GitHub Releases;
- create tags;
- automatically increment or modify the version;
- automatically modify CHANGELOG files or user documentation;
- upload official release ZIP assets;
- generate final release checksums;
- make the repository public;
- define final supported Python versions;
- claim Linux, Windows, Intel macOS or unvalidated macOS support;
- use private Stage 8 datasets in GitHub Actions;
- download or expose private FITS data in CI;
- introduce Git LFS;
- implement release automation;
- begin Stage 9.2, 9.3 or 9.4 work;
- remove the private historical `master` branch or backup.

---

## 5. Platform policy

The v1.1.0 release policy remains:

- officially supported platform: macOS;
- architecture: Apple Silicon / arm64 only;
- only Apple-supported macOS versions at release time are candidates for official support;
- other operating systems or architectures may work but are unsupported.

GitHub Actions availability must not be confused with product support.

Prefer release-relevant CI on macOS. If a repository-neutral check runs elsewhere, the workflow and documentation must not imply product support on that platform.

---

## 6. Candidate Python versions

Stage 9.1a identified these **candidate** versions:

- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

Stage 9.1d should attempt CI validation across this set where runner/tool availability permits.

A failure must be recorded and must not be hidden by weakening the matrix. Final support remains a Stage 9.2a decision.

If runner/tool availability prevents testing a candidate, record that limitation rather than silently dropping it.

---

## 7. CI workflow requirements

Use GitHub Actions.

Expected triggers:

- pushes to `main`;
- pull requests targeting `main`.

Manual dispatch may be included if useful.

The workflow must cover:

- checkout;
- candidate Python setup;
- dependency installation from declared development/test configuration;
- pytest;
- Ruff;
- applicable formatting checks;
- package build;
- package metadata/content inspection;
- installed-artifact smoke checks.

Use least-privilege permissions. Normal CI must not require repository write access, release write access, personal tokens, secrets or private external data.

Caching may be used if simple and safe, but a cache miss must still produce a valid run.

---

## 8. Dependency policy

Stage 9.1d must verify:

- runtime installation does not install pytest;
- runtime installation does not install Ruff;
- PDF-generation tooling is not a runtime dependency;
- build tools are not runtime dependencies unless technically required;
- CI development dependencies are explicitly declared or deliberately installed;
- no undeclared dependency from the developer workstation is required.

The v1.1.0 “no PyPI” policy prohibits publishing Seestar Toolkit to PyPI. It does not prohibit downloading ordinary third-party dependencies or build tools.

---

## 9. Build requirements

Build both:

- wheel;
- source distribution (`.tar.gz`).

Use standards-based Python build tooling.

The authoritative version remains `1.1.0`.

The build must start from repository source and must not rely on undeclared local generated files.

Generated distributions must remain untracked.

---

## 10. Distribution inspection

Inspect both wheel and sdist.

At minimum verify:

- project name;
- version `1.1.0`;
- Mark Wymer author metadata;
- MIT licensing;
- currently configured Python metadata;
- runtime dependency metadata;
- console-script entry point;
- required package modules;
- README/license metadata;
- absence of private Stage 8 datasets;
- absence of private/local filesystem paths;
- absence of `.git`, caches and accidental temporary files;
- absence of the superseded oversized Siril mosaic.

---

## 11. Installed-artifact validation

At minimum validate the wheel in a clean temporary environment:

- installation succeeds;
- `seestar-toolkit --version` returns `1.1.0`;
- `python -m seestar_toolkit --version` returns `1.1.0`;
- console entry point works from outside the repository;
- imports resolve from the temporary environment/site-packages;
- no development-only dependency is required.

Also smoke-test the sdist in a clean temporary environment where practical.

Stage 9.2a remains the authoritative clean-environment compatibility matrix.

---

## 12. Source-tree isolation

Installed-artifact validation must guard against false success caused by importing local `src/`.

Use an isolated temporary venv, run commands outside the repository where practical, verify the imported module path, and ensure `PYTHONPATH` is not masking an installation failure.

---

## 13. Public fixture policy

The repository's tracked FITS fixtures are public-safe according to:

`tests/data/PRIVACY_REVIEW.md`

CI may use these tracked fixtures.

CI must not use private Stage 8 datasets, external-drive/NAS/iCloud paths, user-specific data, or superseded private metadata.

---

## 14. GitHub repository checks

Verify:

- `origin/main` is the intended development branch;
- CI runs against the clean public-history branch;
- Actions run without additional secrets;
- repository remains private;
- no release is created;
- no tag is created;
- no package is published.

Do not enable automatic release/publish workflows.

---

## 15. Documentation updates

Update development documentation only where necessary, likely:

- `docs/development/PACKAGING.md`
- `docs/development/PROJECT_Notes.md`
- `docs/development/CHANGELOG.md`

Do not create final user-facing support/install claims here. User Guide and Quick Start belong to Stage 9.3.

Do not rewrite historical Stage documents.

The existing pending Stage 9.1c CHANGELOG entry is expected starting state.

---

## 16. Validation

Validation must include the equivalent of:

```bash
pytest
ruff check .
git diff --check
```

plus configured formatting validation.

The Stage 9.1d incremental diff must be clean. Do not mass-edit historical files solely because the orphan root commit exposed legacy whitespace.

Build wheel and sdist, inspect contents/metadata, and test installed artifacts in clean temporary environments.

---

## 17. CI evidence

Before closure, record actual GitHub Actions evidence:

- workflow name;
- triggering commit;
- Python matrix attempted;
- runner OS;
- each job/matrix result;
- pytest result;
- Ruff result;
- formatting result;
- package build result;
- installed-artifact smoke result.

Original failures/remediation cycles must remain part of the development record.

Do not mark failing jobs `continue-on-error` merely to get a green workflow.

---

## 18. Privacy and security

CI logs/artifacts must not expose credentials, private paths, private FITS metadata, private datasets, user configuration, tokens or SSH keys.

No additional secrets should be required for ordinary Stage 9.1d validation.

---

## 19. Generated artifacts

Stage 9.1d build outputs are validation artifacts, not final release artifacts.

Do not commit:

- `dist/`;
- temporary venvs;
- CI artifacts;
- caches;
- temporary checksum files.

Final release artifacts belong to Stage 9.4. Documentation PDF/checksum deliverables belong to Stage 9.3b.

---

## 20. Git policy

Use `main` as the canonical development branch.

Do not merge old local `master` into `main`, cherry-pick the historic chain to recreate history, reintroduce the oversized FITS blob, or rewrite `main` history without explicit review.

Keep private pre-public `master` and the backup through Stage 9.1d closure.

---

## 21. Expected files

Likely changes include:

- `.github/workflows/ci.yml` or equivalent;
- `pyproject.toml` only if justified;
- `docs/development/PACKAGING.md`;
- `docs/development/PROJECT_Notes.md`;
- packaging-validation tests where justified;
- this change document.

Do not modify production code unless validation exposes a genuine release defect. Report any production-code change explicitly.

---

## 22. Closure criteria

Stage 9.1d may close only when all applicable criteria pass.

### Repository/history

1. Work is on `main`.
2. `main` descends from `c294ffd`.
3. Old `master` is not merged into `main`.
4. The 272,923,200-byte FITS blob is not reachable from `main`.
5. No tracked public-history blob exceeds 100 MiB.
6. Repository remains private.
7. No normal 9.1d history rewrite occurs.
8. Historical documents are not retroactively rewritten solely to replace old commit IDs.

### CI

9. GitHub Actions workflow exists.
10. CI runs on pushes to `main`.
11. CI runs on PRs targeting `main`.
12. Workflow permissions are least-privilege.
13. Normal CI needs no personal secrets.
14. CI does not publish packages.
15. CI does not create releases.
16. CI does not create tags.
17. CI does not modify versioning.
18. CI does not modify CHANGELOGs.
19. CI does not require private datasets.
20. CI uses only repository-safe fixtures.

### Python candidates

21. Python 3.11 is attempted where available.
22. Python 3.12 is attempted where available.
23. Python 3.13 is attempted where available.
24. Python 3.14 is attempted where available.
25. Versions remain candidates, not final support claims.
26. Unavailable candidates are recorded.
27. Failing candidates are recorded.
28. Failing candidates are not silently removed.

### Tests/quality

29. Full pytest suite passes for applicable matrix entries.
30. Ruff passes.
31. Configured formatting passes.
32. Incremental `git diff --check` passes.
33. Coverage is not weakened merely for CI.
34. New CI skips are justified.
35. CI is reproducible from clean checkout.

### Build

36. Wheel build succeeds.
37. Sdist build succeeds.
38. Build uses repository source only.
39. Wheel filename/version are correct.
40. Sdist filename/version are correct.
41. Project-name metadata is correct.
42. Version metadata is `1.1.0`.
43. Author metadata is Mark Wymer.
44. MIT licensing metadata is appropriate.
45. Runtime dependency metadata matches Stage 9.1c intent.
46. Dev-only dependencies are not runtime dependencies.
47. Build outputs remain untracked.

### Distribution contents

48. Wheel contents are inspected.
49. Sdist contents are inspected.
50. Required package modules are present.
51. Console-script metadata is present.
52. Expected README/license metadata is present.
53. No private Stage 8 datasets are included.
54. No private local paths are included.
55. No `.git` data is included.
56. No accidental cache/temp files are included.
57. Superseded oversized Siril fixture is absent.

### Installed artifacts

58. Wheel installs in clean temporary environment.
59. Installed `seestar-toolkit --version` is `1.1.0`.
60. Installed `python -m seestar_toolkit --version` is `1.1.0`.
61. Console entry point works outside repository source tree.
62. Module entry point works outside repository source tree.
63. Imported package resolves from temporary environment/site-packages.
64. Installed package does not require pytest.
65. Installed package does not require Ruff.
66. Installed package does not require PDF tooling.
67. Sdist smoke validation succeeds where practical.
68. Any sdist limitation is documented.

### Privacy/public fixtures

69. `tests/data/PRIVACY_REVIEW.md` remains present.
70. Synthetic Siril mosaic remains the reviewed small fixture.
71. Sanitised real FITS fixtures remain sanitised.
72. CI does not restore old identifying metadata.
73. CI logs expose no private fixture metadata/paths.
74. No Git LFS dependency is introduced.

### Documentation

75. `PACKAGING.md` reflects implemented build/CI process where needed.
76. `PROJECT_Notes.md` reflects 9.1d status where needed.
77. `PUBLIC_HISTORY_BOOTSTRAP.md` remains accurate.
78. Historical Stage documents are preserved.
79. User Guide work is not prematurely moved into 9.1d.
80. Final Python support claims remain deferred to 9.2a.

### GitHub execution evidence

81. At least one real GitHub Actions run occurs.
82. Triggering commit is recorded.
83. Attempted Python matrix is recorded.
84. Runner OS is recorded.
85. Job outcomes are recorded.
86. Pytest outcome is recorded.
87. Ruff outcome is recorded.
88. Formatting outcome is recorded.
89. Build outcome is recorded.
90. Installed-artifact smoke outcome is recorded.
91. Failure/remediation cycles remain visible.
92. Final applicable CI state required for closure is passing.

### Scope control

93. No PyPI publication.
94. No GitHub Release.
95. No release tag.
96. Repository stays private.
97. Stage 9.2 not begun.
98. Stage 9.3 not begun.
99. Stage 9.4 not begun.
100. No automatic release workflow.
101. Pre-public `master` preserved through closure.
102. Private pre-public backup not intentionally deleted during 9.1d.

### Final audit

103. Final pytest passes.
104. Final Ruff passes.
105. Final formatting passes.
106. Final incremental `git diff --check` passes.
107. Pre-commit `git status` contains only expected 9.1d changes.
108. No unexpected generated artifacts are tracked.
109. No unexpected private files are tracked.
110. Codex provides a complete closure report mapped to these criteria.
111. Codex does not commit.
112. 9.1d is not marked COMPLETE until the approved commit exists and post-commit state is verified.

---

## 23. Codex completion report

Return:

- **Decision:** PASS/FAIL.
- **Files changed:** all files and reasons.
- **CI implementation:** workflow, triggers, runner OS, Python matrix, permissions, caching, jobs.
- **Build validation:** wheel/sdist filenames, version, metadata and contents.
- **Installed-artifact validation:** clean-env method, installed module path, CLI/module version checks, sdist smoke result.
- **GitHub Actions evidence:** run URL/ID if available, triggering SHA, matrix/job outcomes, failures/remediation.
- **Test/quality:** exact pytest, Ruff, formatting and `git diff --check` results.
- **Python candidate findings:** 3.11/3.12/3.13/3.14 each as PASS/FAIL/UNAVAILABLE with reason; do not declare final support.
- **Privacy/public checks:** safe fixtures only, no private datasets, no >100 MiB public blob, no LFS, no private paths/secrets.
- **Scope exclusions:** confirm no commit/tag/release/PyPI/public switch and no Stage 9.2 work.
- **Closure criteria:** state whether all 112 criteria are satisfied and identify every unsatisfied item.

---

## 24. Commit policy

Codex must **not commit**.

After ChatGPT approves the report, suggested commit message:

`Stage 9.1d: add distribution CI and package validation`

After that commit, update `docs/development/CHANGELOG.md` with Stage 9.1d, final commit ID/message/date and intentionally leave that update pending for Stage 9.2a.

---

## 25. Formal close condition

Stage 9.1d closes only after:

- all applicable closure criteria pass;
- actual GitHub Actions execution is reviewed;
- ChatGPT explicitly approves closure;
- the approved Stage 9.1d commit is created;
- its commit ID is confirmed;
- the post-commit working-tree state is verified.

Only then may Stage 9.2a begin.
