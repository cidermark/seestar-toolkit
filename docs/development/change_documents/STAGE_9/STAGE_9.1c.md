# STAGE 9.1c — Package Metadata, Authoritative Versioning and Build Configuration

**Stage:** 9 — Packaging, Documentation and Release
**Step:** 9.1c — Package metadata, authoritative versioning and build configuration
**Starting commit:** `ff304d7` — `Stage 9.1b: reorganise repository and documentation`
**Target release:** Seestar Toolkit `v1.1.0`
**Status on opening:** STARTED
**Date opened:** 2026-09-10

## 1. Purpose

Stage 9.1c establishes the packaging metadata, authoritative version mechanism and build configuration required to produce standards-compliant Python distributions for Seestar Toolkit v1.1.0.

This step converts the requirements identified by the Stage 9.1a audit into repository configuration that can later be exercised by Stage 9.1d and formally proven across clean environments in Stage 9.2a.

This step does **not** declare final supported Python versions. Candidate compatibility may be encoded only to the extent required to build and test candidates. Stage 9.2a remains the authoritative compatibility proof.

## 2. Starting state

Start from:

`ff304d7` — `Stage 9.1b: reorganise repository and documentation`

Expected dirty state:

- `docs/development/CHANGELOG.md` contains the pending Stage 9.1b entry referencing `ff304d7`;
- that CHANGELOG update is intentionally uncommitted and must be carried into the Stage 9.1c commit.

Before changes, report:

```bash
git status --short
git rev-parse HEAD
git log -1 --oneline
```

Explain any unexpected starting changes before proceeding.

## 3. Authoritative evidence

Use as primary evidence:

- `docs/development/change_documents/STAGE_9/STAGE_9.1a.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.1a_AUDIT.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.1b.md`
- `docs/development/change_documents/STAGE_9/STAGE_9.1b_REPORT.md`
- current package source and `pyproject.toml`
- current CLI/version implementation
- existing tests

Where the audit identified duplication, ambiguity or non-standard metadata, 9.1c must resolve it deliberately and document the result.

## 4. Authoritative versioning

Establish **one authoritative package version source** for Seestar Toolkit.

Requirements:

- authoritative value for this release is `1.1.0`;
- `seestar-toolkit --version` must report `1.1.0`;
- `python -m seestar_toolkit --version` must report `1.1.0` if that invocation already supports version reporting or is part of the implemented CLI contract;
- package metadata must resolve to `1.1.0`;
- built wheel/sdist filenames must resolve to `1.1.0`;
- documentation/release tooling added in later stages must be able to consume or validate against the same source;
- remove or neutralise independent hard-coded duplicate version definitions that could drift;
- do not introduce a second release version file merely for convenience unless it is itself the single authoritative source.

Prefer the simplest standards-based mechanism supported by the existing project structure and build backend.

Add tests where appropriate to prove that runtime/CLI/package-facing version access resolves from the authoritative source and remains `1.1.0`.

## 5. `pyproject.toml` and standards-based package metadata

Audit and correct `pyproject.toml` so package metadata is suitable for release.

At minimum validate/configure as appropriate:

- package/project name: `seestar-toolkit`;
- version mechanism linked to the authoritative version source;
- description;
- author: `Mark Wymer`;
- MIT licensing metadata;
- Python requirement mechanism;
- runtime dependency declarations;
- console-script entry point `seestar-toolkit`;
- import package remains `seestar_toolkit`;
- standards-compliant build-system section;
- package discovery/inclusion;
- readme metadata if appropriate;
- classifiers only where factually justified;
- project URLs only if valid and available — do not invent GitHub URLs before a repository exists.

Do not add metadata whose truth cannot yet be established.

## 6. Python compatibility metadata

Stage 9.1a identified Python 3.11, 3.12, 3.13 and 3.14 as **candidates only**.

9.1c may configure Python metadata needed to build/install/test these candidates, but must not present all candidates as officially supported merely because metadata permits them.

Requirements:

- inspect runtime dependencies for declared Python constraints;
- set `requires-python` only to a defensible candidate envelope;
- do not encode a knowingly false support promise;
- do not add Python-version classifiers implying validated support unless evidence already exists;
- clearly record in the 9.1c completion report that final supported versions are deferred to Stage 9.2a;
- if packaging standards require a broad minimum/maximum mechanism, choose one that permits candidate testing without misrepresenting final support.

Any later narrowing required by Stage 9.2a evidence is explicitly allowed there.

## 7. Runtime versus development dependencies

Ensure runtime and development dependencies are clearly separated.

Requirements:

- ordinary installation must not require pytest, Ruff, PDF-generation tools, build-only test helpers, or other development tooling unless genuinely required at runtime;
- runtime dependencies must be explicitly declared;
- development/test/build tooling may be declared in appropriate optional/dependency groups or equivalent standards-based mechanism;
- do not blindly pin all runtime packages to the development environment's exact installed versions;
- add upper bounds only where there is a known compatibility reason;
- preserve reproducibility through explicit documented/tested requirements rather than accidental environment leakage.

If the project currently has undeclared runtime imports that work only because developer packages are installed, identify and correct that packaging defect.

## 8. Build backend and configuration

Configure a standards-compliant build backend capable of producing:

- wheel;
- source distribution (`.tar.gz`).

Requirements:

- build metadata must be self-contained enough for isolated builds;
- package source layout must be handled correctly;
- console script must be installed correctly;
- required runtime files must be included;
- tests/private datasets/development-only material must not be unintentionally packaged as runtime package data;
- source distribution should include the source and packaging files required for a normal standards-compliant rebuild;
- do not yet assemble the final release ZIP;
- do not publish to PyPI;
- do not create GitHub Actions.

Use the simplest backend appropriate for the current repository unless the existing backend is already suitable.

## 9. Package contents audit

Inspect what would be included in wheel and sdist.

Explicitly check for accidental inclusion of:

- private FIT/FITS data;
- caches;
- `.DS_Store`;
- local config;
- personal paths;
- development change documents in the wheel;
- test-only files in the wheel unless required;
- virtual environments;
- build artifacts;
- temporary files.

The sdist may legitimately contain public source/tests/docs needed for source distribution, but its contents must be deliberate and safe.

Do not globally exclude legitimate source/tests from the repository merely to shrink artifacts.

## 10. CLI entry points

Validate package entry points for:

```text
seestar-toolkit
python -m seestar_toolkit
```

Requirements:

- both remain official/release-blocking interfaces;
- primary documented executable remains `seestar-toolkit`;
- module invocation remains functional;
- no CLI behaviour regression;
- version reporting is consistent with the authoritative version source;
- exit-code behaviour from existing CLI remains unchanged.

Add/adjust tests as needed.

## 11. Build validation within 9.1c

9.1c must prove that configuration can produce local wheel and sdist artifacts.

Run a clean local build using the configured backend/build frontend.

Validate:

- wheel builds successfully;
- sdist builds successfully;
- artifact filenames contain version `1.1.0`;
- metadata inside the artifacts reports `1.1.0`;
- expected console entry point is present;
- package contents are sane;
- no private/personal data is bundled;
- build succeeds without relying on undeclared local repository state.

Generated wheel/sdist artifacts are **not committed**.

This is build-configuration validation only. It is not Stage 9.2a clean-environment compatibility proof.

## 12. Platform metadata

Initial release support policy is macOS Apple Silicon only, with exact supported macOS versions to be finalised later.

Do not use Python package metadata in a way that falsely implies a platform restriction that the package format itself does not require.

If current package is pure Python and wheel is platform-independent, retain technically correct wheel tagging rather than forcing an artificial `arm64` wheel tag.

Document the distinction in the completion report:

- release support policy may be macOS Apple Silicon only;
- package artifact metadata must truthfully reflect whether code is technically platform-independent.

Do not claim Linux/Windows support.

## 13. Licensing and attribution

Ensure release metadata is consistent with:

- MIT License;
- copyright `(c) 2026 Mark Wymer`;
- author `Mark Wymer`.

Do not add source-file banners or intrusive attribution.

Validate that the license file is included where packaging standards/build backend expect it.

## 14. Documentation updates within scope

Update development documentation only where needed to record:

- authoritative version mechanism;
- package/build configuration;
- runtime vs development dependency structure;
- candidate Python metadata versus final validation boundary;
- build commands actually validated;
- downstream actions for 9.1d and 9.2a.

Do not write the final user installation guide or Quick Start.

The pending 9.1b CHANGELOG entry must be preserved.

## 15. Explicit exclusions

Do not:

- create GitHub repository or remote;
- authenticate or push to GitHub;
- create GitHub Actions/CI;
- publish artifacts;
- upload to PyPI;
- create release ZIP;
- generate final user documentation PDFs/checksums;
- declare final supported Python versions;
- perform the full clean-environment compatibility matrix;
- make unsupported platform claims;
- add S50 Pro/S30/S30 Pro/DSLR/MP4 functionality;
- refactor unrelated production code.

## 16. Validation

Run and report at minimum:

- full pytest suite;
- Ruff;
- applicable formatting checks;
- `git diff --check`;
- standards-compliant wheel build;
- standards-compliant sdist build;
- artifact metadata inspection;
- artifact content inspection;
- CLI/version tests;
- final `git status --short`.

Expected pre-9.1c baseline is 314 tests. Explain any count change.

Generated build artifacts must be removed or left only in ignored temporary build directories and must not be committed.

## 17. Closure criteria

Stage 9.1c passes only if all criteria below pass.

1. Starting commit is `ff304d7`.
2. Pending 9.1b detailed CHANGELOG entry is recognised and preserved.
3. No unexpected starting change is ignored.
4. One authoritative version source exists.
5. Authoritative version is `1.1.0`.
6. CLI `seestar-toolkit --version` resolves to `1.1.0`.
7. Module invocation version behaviour is consistent with the authoritative source.
8. Package metadata resolves to `1.1.0`.
9. Wheel filename resolves to version `1.1.0`.
10. Sdist filename resolves to version `1.1.0`.
11. Independent duplicate hard-coded version definitions that can drift are removed/neutralised.
12. Project/package name is correctly `seestar-toolkit`.
13. Import package remains `seestar_toolkit`.
14. Author metadata is `Mark Wymer`.
15. MIT license metadata is correctly represented.
16. License file is correctly available to packaging.
17. Build-system metadata is standards-compliant.
18. Build backend is explicitly configured.
19. Package discovery/inclusion is correct.
20. Console entry point `seestar-toolkit` is correctly configured.
21. `python -m seestar_toolkit` remains functional.
22. Existing CLI behaviour is not regressed.
23. Existing exit-code behaviour remains unchanged.
24. Runtime dependencies are explicitly declared.
25. Development/test/build dependencies are separated from runtime dependencies.
26. Ordinary runtime install does not require pytest/Ruff/PDF tooling.
27. No known runtime import depends on an undeclared development package.
28. Runtime constraints are not blindly copied from exact developer-environment pins.
29. Python 3.11–3.14 remain candidates, not falsely declared final support.
30. `requires-python` is defensible for candidate testing.
31. No unvalidated Python classifiers falsely imply final support.
32. Completion report explicitly defers final Python support proof to 9.2a.
33. Platform metadata remains technically truthful.
34. No false arm64 wheel tagging is introduced if package is pure Python.
35. Completion report distinguishes release support policy from artifact platform tagging.
36. Wheel builds successfully.
37. Sdist builds successfully.
38. Builds use standards-compliant tooling.
39. Build succeeds without relying on undeclared local state.
40. Wheel metadata version is `1.1.0`.
41. Sdist metadata version is `1.1.0`.
42. Expected console entry point is present in built distribution metadata.
43. Wheel contents are sane and intentional.
44. Sdist contents are sane and intentional.
45. No private FIT/FITS data is bundled.
46. No local config/personal paths are bundled.
47. No caches/temporary junk are bundled.
48. Development change documents are not unintentionally included in the wheel.
49. Generated build artifacts are not committed.
50. No release ZIP is assembled.
51. No PyPI publication occurs.
52. No GitHub repository/remote/authentication/push occurs.
53. No CI/GitHub Actions implementation occurs.
54. No final supported Python version declaration is made.
55. No 9.2a compatibility proof is claimed.
56. No final user documentation/PDF/checksum work is performed.
57. Relevant development documentation is updated only as needed.
58. Full pytest suite passes.
59. Ruff passes.
60. Applicable formatting checks pass.
61. `git diff --check` passes.
62. Any test-count change from 314 is explained.
63. Build/artifact inspection results are included in completion report.
64. No unrelated production refactor is introduced.
65. Stage 9.1c completion report explicitly evaluates all closure criteria.
66. PASS is returned only if every criterion passes.
67. No commit is made before ChatGPT closure review.
68. Stage 9.1d is not started.

If any criterion fails, return FAIL. Do not weaken or retrospectively reinterpret criteria to obtain a pass.

## 18. Commit and CHANGELOG workflow

Do not commit until the Codex completion report has been reviewed and approved in the Stage 9 development chat.

After approval:

1. commit with:
   `Stage 9.1c: configure package metadata, versioning and builds`
2. user supplies the actual commit ID from Git;
3. add the Stage 9.1c entry with that actual commit ID to `docs/development/CHANGELOG.md`;
4. leave that CHANGELOG update intentionally pending for Stage 9.1d.

Do not start 9.1d until 9.1c is formally passed and committed.

## 19. Required Codex completion report

Return:

1. PASS/FAIL recommendation.
2. Starting commit and initial status.
3. Files created/modified/deleted.
4. Authoritative version design.
5. `pyproject.toml`/metadata changes.
6. Runtime vs development dependency result.
7. Python candidate metadata and explicit 9.2a deferral.
8. Build backend/configuration result.
9. Wheel build result.
10. Sdist build result.
11. Artifact filenames and metadata versions.
12. Wheel contents audit.
13. Sdist contents audit.
14. Entry-point/module invocation validation.
15. Licensing/author metadata validation.
16. Platform metadata/support-policy distinction.
17. Full pytest result.
18. Ruff result.
19. Formatting result.
20. `git diff --check` result.
21. Explicit evaluation of all 68 closure criteria.
22. Current `git status --short`.
23. Remaining downstream actions/blockers.
24. Confirmation generated build artifacts are not committed.
25. Confirmation no GitHub/CI/publication work occurred.
26. Confirmation no commit was made.
27. Confirmation Stage 9.1d was not started.
