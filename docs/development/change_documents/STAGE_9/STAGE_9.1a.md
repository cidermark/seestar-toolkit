# STAGE 9.1a — Release Requirements, Compatibility and Packaging Audit

**Stage:** 9 — Packaging, Documentation and Release  
**Step:** 9.1a — Release requirements, compatibility and packaging audit  
**Starting commit:** `995c988` — `validate and close Stage 8`  
**Target release:** Seestar Toolkit `v1.1.0`  
**Status on opening:** STARTED  
**Date opened:** 2026-09-10

---

## 1. Purpose

Stage 9.1a is an **audit-only release-foundation step**.

Its purpose is to inspect the Stage 8 codebase, packaging configuration, dependencies, documentation layout, tests, fixtures, version handling, platform assumptions and real-data evidence, then produce an authoritative set of release requirements for the implementation and validation work that follows.

This step must determine what Stage 9 needs to change, but must **not** prematurely perform the wider repository/documentation reorganisation, packaging implementation, CI implementation, distribution build, clean-install validation, user-guide creation, PDF generation, release assembly or publication.

The findings from 9.1a become the basis for Stages 9.1b–9.4b.

---

## 2. Starting state

The audit starts from:

- Stage 8 closure commit: `995c988` — `validate and close Stage 8`.
- Stage 8 closure validation: 314 automated tests passed.
- Stage 8.2g real-data validation: 9 datasets, 11 observations, 11 plans and 1,020 preserved files.
- The detailed Stage 8.3a development CHANGELOG entry is intentionally pending.
- `PROJECT_Notes.md` is intentionally modified to identify Stage 9 as Packaging, Documentation and Release.
- These expected pending documentation changes must **not** be treated as unexpected dirty-working-tree conditions.
- Stage 9 was formally opened on 2026-09-10.
- Stage 9.1a was formally opened on 2026-09-10.

No implementation beyond the 9.1a audit itself has yet been authorised.

---

## 3. Bootstrap exception for the Stage 9 change-document location

The agreed Stage 9 documentation reorganisation will ultimately move development documentation under:

`docs/development/`

and Stage 9 authoritative change documents under:

`docs/development/change_documents/STAGE_9/`

Stage 9.1b is responsible for the wider repository/documentation reorganisation.

However, Stage 9.1a itself requires an authoritative change document before 9.1b can run.

Therefore the following **bootstrap exception is explicitly authorised**:

- create `docs/development/change_documents/STAGE_9/` if it does not yet exist;
- create this authoritative file as:
  `docs/development/change_documents/STAGE_9/STAGE_9.1a.md`.

This bootstrap creation does **not** authorise the broader documentation migration.

Do not move the existing README, CHANGELOG, ARCHITECTURE, PROJECT_Notes or other development documents during 9.1a.

---

## 4. Stage 9 structure confirmed by this step

Stage 9 uses the following structure:

### 9.1 — Packaging & Release Foundations

- 9.1a — Release requirements, compatibility and packaging audit
- 9.1b — Repository/documentation reorganisation
- 9.1c — Package metadata, authoritative versioning and build configuration
- 9.1d — Distribution build, CI and package validation

### 9.2 — Installation & Runtime Validation

- 9.2a — Clean-environment installation and Python compatibility validation
- 9.2b — Installed CLI, functional and storage validation

### 9.3 — User Documentation

- 9.3a — Authoritative Markdown User Guide, Quick Start and public repository documentation
- 9.3b — PDF generation, checksums and documentation validation

### 9.4 — Release Preparation & Publication

- 9.4a — Release candidate assembly, public-repository/privacy audit and contents validation
- 9.4b — Final release-readiness/publication audit and Stage 9 closure — GO/NO-GO

---

## 5. Release policy to preserve

The audit must treat the following decisions as fixed release policy unless a genuine technical contradiction is discovered and explicitly reported.

### 5.1 Version and release

- Stage 9 produces the formal Seestar Toolkit `v1.1.0` release.
- Semantic Versioning is used.
- Do not introduce development, alpha, beta or release-candidate identifiers for v1.1.0.
- There must be one authoritative package-version source.
- CLI version output, package metadata, distribution filenames, documentation and release information must derive from or be validated against that source.
- Public root `CHANGELOG.md` must retain v1.1.0 as **Unreleased** until actual GitHub publication.
- The official release date is the actual GitHub publication date.

### 5.2 Supported platform policy

- v1.1.0 officially supports macOS on Apple Silicon (`arm64`) only.
- Only macOS versions still supported by Apple at release time should be considered.
- Stage 9 must establish the exact tested/supported macOS envelope.
- Other platforms may happen to work but are not tested or supported.
- Linux and Windows support are future possibilities only.

### 5.3 Python policy

- Do not predeclare the final supported Python versions in 9.1a.
- 9.1a identifies realistic candidate Python versions and dependency compatibility.
- 9.2a proves clean installation and runtime compatibility.
- Only versions that actually pass may be officially claimed.
- Homebrew Python is the recommended/tested source.
- Apple system-managed Python must not be modified.

### 5.4 Installation policy

Primary installation:

- supplied wheel;
- installed in a Python virtual environment.

Secondary installation:

- supplied standards-compliant `.tar.gz` source distribution.

Recommended venv:

`~/.venvs/seestar-toolkit/`

Normal activation model:

```bash
source ~/.venvs/seestar-toolkit/bin/activate
seestar-toolkit ...
deactivate
```

Also support/document invoking the installed CLI by full path.

Do not:

- modify `.zshrc` automatically;
- modify `PATH` automatically;
- create system symlinks;
- add an installer shell script for v1.1.0.

### 5.5 CLI entry points

Both entry points are officially supported and release-blocking:

- `seestar-toolkit`
- `python -m seestar_toolkit`

The console script is the primary documented interface.

### 5.6 Configuration

Retain:

`~/.config/seestar-toolkit/config.toml`

Do not migrate configuration to macOS Application Support for v1.1.0.

### 5.7 Licence and author

- MIT License.
- Existing root `LICENSE` remains.
- Copyright text:
  `Copyright (c) 2026 Mark Wymer`
- Package metadata identifies Mark Wymer as author.
- Attribution should be clear but unobtrusive.
- Do not add copyright banners throughout source files.

### 5.8 Distribution policy

Do not publish v1.1.0 to PyPI.

Final release artifacts will include:

- wheel;
- standards-compliant Python `.tar.gz` sdist;
- complete release ZIP.

GitHub Releases is the official distribution location.

---

## 6. Python-support sequencing dependency

There is an intentional dependency between 9.1c and 9.2a.

### 6.1 What 9.1a must determine

9.1a must identify:

- currently configured Python requirements;
- dependency-declared Python constraints;
- candidate Python versions realistically worth testing;
- any known compatibility blockers;
- the cleanest standards-based packaging mechanism for expressing Python requirements.

These are **candidate/test requirements**, not final support claims.

### 6.2 What 9.1c may do

9.1c may establish packaging metadata and configuration needed to make the package buildable and testable across the candidate Python envelope.

However, before 9.2a proves compatibility, 9.1c must not present unvalidated individual Python versions as final officially supported versions.

In particular:

- avoid documentation claims that candidate versions are supported;
- avoid treating successful development-machine execution as support proof;
- use the minimum packaging constraints necessary to permit meaningful clean-install testing;
- treat any Python classifiers or equivalent explicit support declarations as provisional unless already justified by evidence.

### 6.3 What 9.2a must do

9.2a is the authoritative compatibility proof.

It must:

1. create genuinely clean environments for each candidate Python version;
2. test wheel installation;
3. test sdist installation;
4. test installed runtime behaviour;
5. verify that no undeclared development dependency is required;
6. record pass/fail results per Python version.

Only passing versions become officially supported.

### 6.4 Metadata finalisation after 9.2a evidence

If the 9.2a results require package metadata to be narrowed or otherwise adjusted, that adjustment is permitted as a direct consequence of 9.2a before the step can close.

Any such change must:

- be limited to declarations directly determined by the compatibility results;
- be covered by the 9.2a change document and closure criteria;
- be followed by the applicable packaging/install validation;
- not silently convert a failed candidate into a pass.

A candidate Python version that fails remains a recorded failure and is not claimed as supported.

This preserves the sequencing:

**candidate identification → testable packaging configuration → clean compatibility proof → final support declaration**

rather than declaring support before it has been proven.

---

## 7. Two-gate Stage 9.4b publication and closure process

Stage 9.4b is a genuine GO/NO-GO audit and also contains the final publication gate.

Its sequencing is fixed as follows.

### Gate 1 — Release-readiness GO/NO-GO

9.4b audits the exact clean committed release tree.

A GO requires every release-readiness and privacy criterion to pass.

If any criterion fails:

- decision is NO-GO;
- publication must not occur;
- no release tag is applied;
- Stage 9 remains open;
- the failed audit remains recorded as a failure.

### Publication sequence after Gate 1 GO

After GO:

1. identify the exact approved full release commit SHA;
2. apply annotated tag `v1.1.0` to that exact commit;
3. tag annotation: `Seestar Toolkit v1.1.0`;
4. clean build directories;
5. build final artifacts from the approved/tagged source;
6. verify final artifacts and checksums;
7. stop on any discrepancy;
8. push approved commits and tag;
9. make the GitHub repository public;
10. create a normal GitHub `v1.1.0` Release;
11. upload the validated release ZIP and external SHA-256 file;
12. perform post-publication verification.

### Gate 2 — Publication/closure verification

Stage 9.4b and Stage 9 are not formally COMPLETE merely because Gate 1 returned GO.

Formal closure occurs only after:

- the tag is correct;
- final artifacts are proven to match the approved source;
- the repository is public as intended;
- the GitHub Release exists and is correct;
- the expected release assets are present;
- checksums verify;
- the public documentation is correct;
- post-publication verification passes;
- required provenance has been recorded;
- the private release-process runbook has been finalised from the proven process.

Any problem between Gate 1 GO and successful post-publication verification is a STOP condition and leaves Stage 9 open.

---

## 8. Scope of Stage 9.1a

Stage 9.1a must perform the following audits and produce explicit findings.

### 8.1 Current package/build configuration

Inspect:

- `pyproject.toml`;
- build-system configuration;
- project metadata;
- package discovery;
- CLI entry points;
- version handling;
- Python requirement declarations;
- dependency declarations;
- optional/development dependency mechanism if present;
- wheel/sdist-related configuration;
- any existing build scripts or release helpers.

Determine:

- current packaging strengths/defects;
- standards-based changes required in 9.1c;
- likely build tooling needed for 9.1d;
- whether the current source layout is distribution-safe.

### 8.2 Authoritative version-source audit

Trace every current place where a version is:

- defined;
- duplicated;
- generated;
- displayed;
- tested;
- documented.

Identify the recommended single authoritative version source for 9.1c.

The audit must explicitly account for:

- `seestar-toolkit --version`;
- `python -m seestar_toolkit`;
- package metadata;
- wheel filename;
- sdist filename;
- documentation version injection;
- release ZIP naming;
- public release information.

### 8.3 Dependency audit

Classify dependencies into:

- runtime;
- test;
- lint/quality;
- build;
- documentation/PDF generation;
- release-only tooling.

Identify:

- undeclared dependencies;
- accidentally runtime-installed development dependencies;
- unnecessary exact pins;
- missing compatibility bounds;
- any upper bounds genuinely required for known compatibility reasons.

Do not blindly copy the versions installed on the development Mac into package constraints.

### 8.4 Candidate Python compatibility audit

Inspect:

- current Python requirement metadata;
- dependency Python requirements;
- test assumptions;
- syntax/features used by the codebase;
- existing development Python version;
- likely Homebrew availability relevant to release testing.

Produce a **candidate Python test matrix** for 9.2a.

Do not label candidates as supported.

### 8.5 macOS/architecture audit

Confirm the implementation does not contradict the intended release boundary:

- macOS only;
- Apple Silicon (`arm64`) only.

Identify:

- code that is platform-specific;
- dependencies with architecture/platform implications;
- likely macOS versions to validate later;
- any claims that must be avoided until tested.

The exact final supported macOS envelope is not declared by 9.1a unless already independently proven; 9.1a defines what must be validated.

### 8.6 CLI audit

Inventory actual commands, options and behaviours for both:

- `seestar-toolkit`;
- `python -m seestar_toolkit`.

Record the authoritative command surface that later documentation examples must match.

Explicitly include:

- version;
- convert;
- convert-batch;
- archive;
- configuration-related behaviour;
- diagnostics/errors;
- exit codes.

Identify discrepancies between code, tests and current documentation.

### 8.7 Supported-input/capture matrix

Create an authoritative **v1.1.0 supported-input/capture evidence matrix** based only on:

- implementation;
- automated tests;
- safe tracked fixtures;
- Stage 8 real-data evidence.

For each relevant input/capture category, record:

- category/mode;
- evidence source;
- automated-test coverage;
- real-data coverage;
- support status;
- documentation wording permitted;
- known limitations.

Do not make generic claims such as “supports all Seestar data”.

Explicit boundaries include:

- no DSLR/conventional-camera ingestion/archive reconstruction in v1.1.0;
- no S50 Pro support claim without suitable real-data validation before release;
- no S30 support claim without representative validation;
- no S30 Pro support claim without representative validation;
- Solar/Lunar/Planetary MP4 processing remains future work unless separately implemented and validated.

### 8.8 Repository/documentation layout audit

Inventory current documentation and references.

Plan the 9.1b migration to:

```text
docs/user/
    SEESTAR_TOOLKIT_QUICK_START.md
    SEESTAR_TOOLKIT_QUICK_START.pdf
    SEESTAR_TOOLKIT_QUICK_START.sha256
    SEESTAR_TOOLKIT_USER_GUIDE.md
    SEESTAR_TOOLKIT_USER_GUIDE.pdf
    SEESTAR_TOOLKIT_USER_GUIDE.sha256

docs/development/
    DEV_README.md
    CHANGELOG.md
    ARCHITECTURE.md
    PROJECT_Notes.md
    REAL_DATA_TESTING.md
    change_documents/STAGE_9/...
```

Determine all repository references that will need updating.

Confirm:

- existing developer root README moves to `docs/development/DEV_README.md`;
- new root README becomes concise and user-facing;
- existing detailed CHANGELOG moves to `docs/development/CHANGELOG.md`;
- new root CHANGELOG becomes concise public release history;
- `PROJECT_Notes.md` remains the future-enhancement authority;
- no `ROADMAP.md`;
- no `RELEASE_NOTES.md`.

Do not perform these migrations in 9.1a except for the authorised change-document bootstrap path.

### 8.9 Test-data/public-repository audit

Audit the current test tree and tracked fixture strategy.

Identify:

- safe synthetic/generated/anonymised fixtures suitable for public Git;
- any private or personal real-world data;
- paths used for local Stage 8 validation;
- whether any tracked FIT/FITS files contain sensitive metadata;
- the safest ignored local location for future private real-data validation.

Requirements:

- do not globally ignore `*.fit` or `*.fits` if legitimate safe fixtures must remain tracked;
- private Stage 8 datasets and future personal captures must not enter the public repository;
- 9.1b must create `docs/development/REAL_DATA_TESTING.md`.

### 8.10 Privacy/network/storage behaviour audit

Inspect source and dependencies sufficiently to verify or challenge the intended v1.1.0 statements that the Toolkit:

- collects no telemetry/analytics;
- performs no automatic update checks;
- transmits no image/FITS metadata to external services;
- operates locally on user-selected filesystem paths.

Also confirm that it may operate on user-selected:

- internal storage;
- external/removable storage;
- mounted network filesystems/NAS paths.

Distinguish filesystem access to a mounted network volume from application telemetry/network services.

Identify any actual macOS storage/permission behaviour that needs later validation rather than guessing exact prompts.

### 8.11 Public-repository preparation audit

Identify work needed before publication for:

- root `CONTRIBUTING.md`;
- Bug Report issue template;
- Feature Request issue template;
- privacy warning concerning FITS GPS/location/personal metadata;
- GitHub Issues;
- GitHub Discussions disabled;
- GitHub Wiki disabled;
- repository remaining private throughout Stage 9 until final 9.4b GO and publication sequence.

Identify what can be automated in-repository and what is a manual GitHub setting.

### 8.12 CI audit

Define the requirements for the 9.1d GitHub Actions workflow.

It must:

- run public automated test/quality checks on appropriate pushes/pull requests;
- test every Python version ultimately declared supported;
- not imply support for the runner operating system;
- not use private real-data datasets.

It must not automatically:

- publish releases;
- create tags;
- upload release assets;
- publish to PyPI;
- alter versions;
- modify documentation.

### 8.13 Documentation/PDF pipeline requirements audit

Determine the cleanest reproducible repository-defined mechanism for:

1. Markdown → PDF;
2. synchronising PDF modification time to its Markdown source;
3. SHA-256 of Markdown;
4. SHA-256 of PDF;
5. writing the two hashes to the guide's repository `.sha256` manifest;
6. checksum validation;
7. visual/content validation.

Confirm PDF tooling is development/release-only.

Determine how the documentation process will obtain the package version from the authoritative version source without maintaining a separate document version.

Do not implement the PDF pipeline in 9.1a.

### 8.14 Release ZIP and artifact requirements audit

Confirm the target release ZIP:

`seestar-toolkit-1.1.0-release.zip`

extracts to:

```text
seestar-toolkit-1.1.0/
    SEESTAR_TOOLKIT_QUICK_START.pdf
    SEESTAR_TOOLKIT_USER_GUIDE.pdf
    README.md
    CHANGELOG.md
    LICENSE
    seestar_toolkit-1.1.0-<wheel-tags>.whl
    seestar_toolkit-1.1.0.tar.gz
```

Confirm the ZIP excludes:

- development docs;
- guide Markdown;
- repository guide SHA manifests;
- tests;
- private data;
- `.git`;
- GitHub/CI infrastructure;
- development tools;
- caches;
- temporary files.

Confirm:

`seestar-toolkit-1.1.0-release.zip.sha256`

is generated beside the final ZIP and not inside it.

Confirm wheel, sdist, release ZIP and external release checksum are release artifacts and are not committed.

### 8.15 Provenance requirements audit

Define the release provenance fields that 9.4b must record:

- Toolkit version;
- full release commit SHA;
- tag;
- build/publication date;
- macOS version;
- architecture;
- Python version;
- pip version;
- relevant build-tool versions;
- wheel SHA-256;
- sdist SHA-256;
- release ZIP SHA-256.

No additional provenance file is to be added to the ordinary-user release ZIP.

### 8.16 Private release-process runbook planning

The private file:

`SEESTAR_TOOLKIT_RELEASE_PROCESS.md`

must remain outside the public repository.

9.1a must identify:

- a safe location outside the Git repository;
- the initial section structure;
- which Stage 9 steps will progressively contribute proven procedures.

Do not pretend future commands have been proven.

The final runbook must ultimately cover:

- development;
- local validation;
- local Git;
- final audit;
- tag;
- clean build;
- artifact validation;
- GitHub push;
- repository publication;
- GitHub Release;
- post-publication verification.

It must use reusable placeholders such as:

- `<VERSION>`;
- `<TAG>`;
- `<RELEASE_COMMIT>`;
- `<RELEASE_DATE>`.

It must include STOP conditions for:

- failed validation;
- dirty/unexpected working tree;
- privacy/publication audit failure;
- checksum mismatch;
- tagged-build discrepancy;
- post-tag/pre-publication problems.

---

## 9. Future enhancements to preserve

Verify that `docs/development/PROJECT_Notes.md` will retain or receive the following future items during the appropriate Stage 9 documentation work:

- S50 Pro validation/support;
- S30 validation/support if representative datasets can be obtained;
- S30 Pro validation/support if representative datasets can be obtained;
- DSLR/conventional-camera ingestion/archive support;
- Solar/Lunar/Planetary MP4 processing, including frame extraction suitable for stacking/processing, useful timing/frame metadata preservation and suitable output formats;
- GUI;
- future native/easier macOS installer;
- privacy-conscious `seestar-toolkit diagnostics`;
- possible Linux/Windows support;
- possible PyPI publication;
- GitHub Discussions if community interest warrants it.

9.1a must report missing items but should not perform the wider PROJECT_Notes reorganisation/migration assigned to 9.1b.

---

## 10. Explicit exclusions

Stage 9.1a must **not**:

- move the existing documentation tree, except for the authorised 9.1a bootstrap document path;
- create the new user-facing root README;
- create the new public root CHANGELOG;
- create CONTRIBUTING or GitHub issue templates;
- implement new packaging metadata;
- change the authoritative version mechanism;
- change dependency declarations;
- implement CI;
- build release distributions as final artifacts;
- declare final supported Python versions;
- declare untested macOS versions supported;
- perform clean-environment compatibility validation;
- create user guides;
- implement PDF generation;
- assemble the final release ZIP;
- tag a release;
- push to GitHub;
- make the repository public;
- create a GitHub Release;
- publish to PyPI;
- add DSLR support;
- add S50 Pro/S30/S30 Pro support without separate implementation and validation;
- add Solar/Lunar/Planetary MP4 processing;
- alter production behaviour merely to make an audit finding disappear.

If the audit discovers a defect requiring implementation, record it as downstream Stage 9 work rather than fixing it silently in 9.1a.

---

## 11. Required outputs

Codex must produce the following 9.1a outputs.

### 11.1 Authoritative change document

This file:

`docs/development/change_documents/STAGE_9/STAGE_9.1a.md`

must exist and remain the authoritative specification for the step.

### 11.2 Audit report

Create:

`docs/development/change_documents/STAGE_9/STAGE_9.1a_AUDIT.md`

The report must include, at minimum:

1. executive result;
2. repository starting-state confirmation;
3. current packaging/build audit;
4. version-source audit;
5. dependency classification;
6. candidate Python test matrix;
7. macOS/architecture validation plan;
8. CLI command/exit-code inventory;
9. supported-input/capture evidence matrix;
10. repository/documentation migration inventory;
11. public/private fixture assessment;
12. privacy/network/storage audit;
13. CI requirements;
14. documentation/PDF pipeline requirements;
15. release artifact/ZIP requirements;
16. provenance requirements;
17. private release-runbook plan;
18. identified risks/blockers;
19. explicit downstream actions mapped to 9.1b–9.4b;
20. closure-criteria checklist.

The report must clearly distinguish:

- proven fact;
- current implementation observation;
- Stage 8 real-data evidence;
- candidate assumption requiring later validation;
- future release policy.

### 11.3 Tests/code

No production-code change is expected.

Tests should not be changed merely to satisfy 9.1a.

If Codex believes a code/test modification is necessary to conduct the audit, it must stop and report why rather than making an unapproved implementation change.

---

## 12. Validation procedure

Codex must validate the audit against the repository.

At minimum:

### 12.1 Repository state

Run and report:

```bash
git status --short
git rev-parse HEAD
git log -1 --oneline
```

Confirm HEAD is `995c988` at the start unless an explicitly authorised documentation-bootstrap write has already occurred without a commit.

Distinguish expected pending documentation changes from unexpected changes.

### 12.2 Test baseline

Run the full existing automated test suite using the project's established test command.

The Stage 8 baseline was 314 passing tests.

Any changed count must be explained.

9.1a does not require exactly 314 tests if repository/test discovery legitimately differs, but any discrepancy must be investigated and reported.

### 12.3 Quality checks

Run the established Ruff checks and any existing repository formatting/diff checks applicable to unchanged production code.

### 12.4 Packaging inspection

Use appropriate non-destructive inspection commands to review:

- package metadata;
- entry points;
- Python constraints;
- dependency declarations;
- source/package layout.

Do not install or mutate the global/system Python environment.

### 12.5 Fixture/privacy inspection

Inspect tracked files and representative safe fixtures sufficiently to determine public-repository suitability.

Do not expose private personal dataset contents in the audit document.

If private paths or metadata are found, describe the issue minimally and safely.

### 12.6 Cross-reference validation

Search the repository for:

- old documentation paths;
- version literals;
- README/CHANGELOG references;
- package version references;
- config paths;
- CLI command examples;
- references to private Stage 8 datasets or local paths;
- likely release/publication-sensitive files.

---

## 13. Closure criteria

Stage 9.1a can pass only if **all** of the following criteria are satisfied.

### A. Starting-state integrity

1. The audit identifies `995c988` as the Stage 8 closure baseline.
2. Expected pending Stage 8.3a CHANGELOG work is identified and not misclassified as unexpected.
3. Expected pending `PROJECT_Notes.md` Stage 9 change is identified and not misclassified as unexpected.
4. No unauthorised production-code change has been made.
5. No broader documentation reorganisation has been performed beyond the 9.1a bootstrap exception.

### B. Packaging/version/dependencies

6. Current packaging/build configuration is fully inventoried.
7. All current version-definition/use sites are inventoried.
8. A recommended single authoritative version-source approach is identified for 9.1c.
9. Runtime dependencies are distinguished from development/test/build/docs/release dependencies.
10. Any undeclared or suspicious dependency coupling is identified.
11. Proposed version-constraint policy avoids blind development-machine pinning.
12. Known reasons for any recommended upper bounds are stated.

### C. Python/platform support preparation

13. A candidate Python test matrix is produced.
14. Candidate versions are not falsely labelled supported.
15. The 9.1c → 9.2a sequencing dependency is explicitly preserved.
16. The process for finalising Python metadata after 9.2a evidence is explicitly defined.
17. Apple Silicon/macOS-only release intent is checked against the current code/dependencies.
18. A later macOS validation plan is defined.
19. No unsupported platform is accidentally presented as officially supported.

### D. CLI and input-support evidence

20. Both official entry points are inventoried.
21. Actual commands/options needed for later documentation are inventoried.
22. Diagnostics/error/exit-code behaviour is inventoried sufficiently for 9.3.
23. An evidence-based supported-input/capture matrix is produced.
24. Matrix claims distinguish automated-test evidence from Stage 8 real-data evidence.
25. No unvalidated S50 Pro/S30/S30 Pro support claim is made.
26. DSLR/conventional-camera archive ingestion is explicitly excluded from v1.1.0.
27. Solar/Lunar/Planetary MP4 processing remains a future enhancement unless separately implemented and validated.

### E. Repository/publication/privacy preparation

28. Current documentation paths are inventoried.
29. The complete 9.1b migration map is defined.
30. Old-path references requiring updates are identified.
31. Current test fixtures are assessed for public suitability.
32. A safe ignored private real-data testing strategy is proposed without globally ignoring legitimate FIT/FITS fixtures.
33. Intended telemetry/update/network privacy statements are checked against source behaviour.
34. Mounted network filesystem behaviour is distinguished from application telemetry/network services.
35. Public-repository preparation work is mapped to downstream steps.
36. Manual GitHub settings are distinguished from repository files.

### F. CI/docs/release artifacts

37. CI requirements are fully defined.
38. CI is explicitly prevented from performing publication/tag/version/doc mutation tasks.
39. PDF-generation requirements are fully defined.
40. PDF tooling is classified as development/release-only.
41. Documentation-version derivation from the authoritative package version is planned.
42. Release ZIP contents/exclusions are fully defined and match the release policy.
43. External release-ZIP checksum handling is correctly defined.
44. Wheel/sdist/ZIP release artifacts are confirmed as uncommitted generated artifacts.
45. Required release provenance fields are defined.

### G. Private runbook and release gating

46. A safe outside-repository plan for `SEESTAR_TOOLKIT_RELEASE_PROCESS.md` is defined.
47. The runbook's progressive/proven-procedure model is preserved.
48. Required runbook STOP conditions are defined.
49. Stage 9.4b Gate 1 GO/NO-GO sequencing is preserved.
50. Tag/build/publication steps occur only after Gate 1 GO.
51. Stage 9.4b COMPLETE and Stage 9 COMPLETE occur only after Gate 2 post-publication verification.
52. A post-GO/pre-publication problem is explicitly treated as a STOP condition leaving Stage 9 open.

### H. Validation and reporting

53. Full existing automated tests pass, or any failure is fully explained and causes 9.1a to fail.
54. Ruff/established quality checks pass.
55. `git diff --check` or the repository-equivalent whitespace validation passes.
56. `STAGE_9.1a_AUDIT.md` exists and covers every required audit area.
57. Every identified downstream action is mapped to the appropriate Stage 9 step.
58. No release publication action has occurred.
59. No release tag has been created.
60. The repository remains private.
61. The audit ends with an explicit **PASS** or **FAIL** recommendation.
62. If any criterion is unsatisfied, the recommendation is **FAIL** and the step must not be retrospectively described as passed.

---

## 14. Expected downstream ownership

Audit findings should normally map as follows.

### 9.1b

- documentation/repository reorganisation;
- old-reference updates;
- safe private real-data location/ignore policy;
- `REAL_DATA_TESTING.md`.

### 9.1c

- authoritative version source;
- package metadata;
- author/licence metadata;
- dependency separation;
- packaging/build configuration;
- candidate Python constraints needed for clean testing.

### 9.1d

- wheel/sdist build process;
- build validation;
- CI;
- package-content/metadata checks.

### 9.2a

- clean environments;
- candidate Python compatibility proof;
- final supported-Python determination;
- directly evidence-driven final Python metadata adjustment if required.

### 9.2b

- installed CLI;
- functional commands;
- storage/configuration;
- external/removable/network-mounted storage where practical;
- runtime privacy/storage confirmation.

### 9.3a

- Markdown User Guide;
- Markdown Quick Start;
- user-facing root README;
- concise public root CHANGELOG;
- CONTRIBUTING;
- GitHub issue templates.

### 9.3b

- PDF generation;
- timestamp synchronisation;
- repository SHA manifests;
- checksum validation;
- visual/content validation.

### 9.4a

- release candidate ZIP assembly;
- release notes;
- public-repository/privacy audit;
- contents validation;
- publication preparation.

### 9.4b

- exact committed-tree GO/NO-GO;
- approved commit/tag relationship;
- final clean build;
- artifact checksums/provenance;
- publication;
- post-publication verification;
- private runbook finalisation;
- Stage 9 closure.

---

## 15. Commit policy for 9.1a

Do not commit until the completion report has been returned to the Stage 9 ChatGPT development chat and audited against all 62 closure criteria.

If approved, the 9.1a commit should include only the authorised 9.1a outputs plus the already expected carried-forward pending documentation changes that the Stage 9 chat explicitly approves for inclusion.

The detailed Stage 8.3a CHANGELOG entry must be carried into the first Stage 9 commit as previously agreed.

After the approved 9.1a commit:

- record the 9.1a commit ID/message in the detailed development CHANGELOG;
- intentionally leave that CHANGELOG update pending for the next commit;
- do not treat that expected pending CHANGELOG update as an unexpected dirty-working-tree condition.

Stage 9.1b must not start until 9.1a has formally passed and been committed.

---

## 16. Required Codex completion report

Codex must return a concise but complete report containing:

1. **Result:** PASS or FAIL recommendation.
2. **Starting commit / repository state.**
3. **Files created/modified.**
4. **Audit summary.**
5. **Candidate Python matrix.**
6. **Supported-input/capture evidence matrix summary.**
7. **Key packaging/version/dependency findings.**
8. **Privacy/publication findings.**
9. **Risks/blockers.**
10. **Validation commands and results.**
11. **Automated-test result.**
12. **Ruff/quality result.**
13. **Closure criteria:** explicit confirmation of all 62 criteria, identifying any unsatisfied item by number.
14. **Downstream Stage 9 actions.**
15. **Confirmation that no commit was made.**
16. **Confirmation that Stage 9.1b was not started.**

The report will be audited by the Stage 9 development chat before commit approval.
