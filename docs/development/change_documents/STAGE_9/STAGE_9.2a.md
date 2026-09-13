# Stage 9.2a — Clean-Environment Installation and Python Compatibility Validation

**Stage:** 9 — Packaging, Documentation and Release
**Section:** 9.2 — Installation & Runtime Validation
**Step:** 9.2a — Clean-environment installation and Python compatibility validation
**Starting commit:** `1771b9f` — `Stage 9.1d: validate and close distribution CI`
**Target release:** Seestar Toolkit `v1.1.0`
**Status on opening:** STARTED

---

## 1. Purpose

Stage 9.2a converts the successful Stage 9.1d CI/build evidence into an evidence-based Python support policy for Seestar Toolkit v1.1.0.

Stage 9.1d proved that the package builds and the full automated test suite passes on GitHub Actions macOS arm64 for the four candidate Python lines:

- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

Stage 9.2a must now prove that users can install and run Seestar Toolkit from the built distribution artifacts in genuinely clean macOS arm64 environments, without relying on the development checkout or development dependencies.

The result of Stage 9.2a will determine the final Python support envelope for v1.1.0.

---

## 2. Starting state

At Stage 9.2a start:

- canonical branch: `main`;
- starting commit: `1771b9f`;
- GitHub CI for `1771b9f` is green;
- Stage 9.1d is formally complete;
- authoritative version is `1.1.0`;
- package metadata/build configuration is already present;
- wheel and sdist builds are known to succeed;
- GitHub Actions has passed the full 329-test suite for Python 3.11.9, 3.12.10, 3.13.15 and 3.14.7 on macOS arm64;
- these Python versions are still candidates, not final support claims;
- `docs/development/CHANGELOG.md` contains the intentionally pending Stage 9.1d closure entry and is expected to be dirty at Stage 9.2a start.

---

## 3. Authoritative support rule

A Python version becomes officially supported for Seestar Toolkit v1.1.0 only if it satisfies both:

1. Stage 9.1d CI/build validation on macOS arm64; and
2. Stage 9.2a clean-environment installation/runtime validation.

The initial candidate set is:

- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

If all four pass Stage 9.2a, the official v1.1.0 support range becomes Python 3.11 through 3.14 inclusive.

If a candidate fails:

- preserve the failure evidence;
- determine whether the defect is in Seestar Toolkit, packaging metadata, dependency compatibility, interpreter/tool availability or the validation method;
- remediate genuine project defects where appropriate;
- do not silently remove the candidate;
- if a candidate remains unsupported after justified remediation, narrow package metadata before closure;
- rebuild and revalidate the resulting supported set;
- record the unsupported candidate and reason.

Stage 9.2a must not pre-decide the result.

---

## 4. Platform scope

The v1.1.0 supported platform remains:

- macOS;
- Apple Silicon / arm64;
- Apple-supported macOS releases only at release time.

Stage 9.2a validates Python compatibility within this platform policy.

Do not make support claims for:

- Intel macOS;
- Linux;
- Windows;
- Rosetta;
- unsupported macOS releases.

A Python environment may be obtained through Homebrew or another reliable local mechanism for validation, but the user documentation policy remains that Homebrew Python is the recommended installation path.

---

## 5. Interpreter discovery and provenance

Before installing anything new, audit locally available Python interpreters.

For every candidate interpreter found, record:

- Python major/minor/patch version;
- executable path;
- architecture;
- macOS version;
- installation source where determinable;
- whether it is suitable for clean-environment validation.

Do not assume that `python3`, `python3.11`, etc. point to the intended interpreter.

Use direct interpreter paths where needed.

The validation record should include a table equivalent to:

| Candidate | Exact version | Executable | Architecture | macOS | Source | Wheel | Sdist |
|---|---|---|---|---|---|---|---|

If a candidate interpreter is not locally available, determine the least invasive reproducible way to obtain it on Apple Silicon macOS.

Do not alter the Apple system Python.

---

## 6. Clean-environment definition

A Stage 9.2a environment is clean only if:

- it is a newly created temporary virtual environment;
- it is created from the candidate interpreter under test;
- it does not inherit site packages;
- it does not use the existing Seestar Toolkit development venv;
- it does not use an editable install;
- it does not depend on `PYTHONPATH`;
- it does not import from the repository `src/` tree;
- pytest, Ruff and PDF-generation dependencies are not preinstalled unless required for a separate validation step;
- runtime validation runs from outside the repository root where practical;
- the environment can be deleted after validation.

Use separate clean environments for wheel and sdist validation.

Do not reuse one environment for both artifact types.

---

## 7. Distribution source

Build validation artifacts from the Stage 9.2a working tree using the existing standards-based build configuration.

Use the package version source already established in Stage 9.1c.

Expected outputs:

- `seestar_toolkit-1.1.0-py3-none-any.whl`
- `seestar_toolkit-1.1.0.tar.gz`

Artifacts generated during Stage 9.2a are temporary validation artifacts only.

Do not commit them.

---

## 8. Wheel validation sequence

For each candidate Python version:

1. create a fresh temporary virtual environment;
2. upgrade/install only the packaging tools required for normal installation if needed;
3. install the built wheel;
4. run `pip check` or equivalent dependency consistency validation;
5. record installed runtime dependencies;
6. confirm pytest is not installed as a runtime dependency;
7. confirm Ruff is not installed as a runtime dependency;
8. confirm PDF-generation tooling is not installed as a runtime dependency;
9. run `seestar-toolkit --version`;
10. run `python -m seestar_toolkit --version`;
11. confirm both report `1.1.0`;
12. import `seestar_toolkit` and record its resolved module path;
13. verify the module path is inside the temporary environment/site-packages;
14. run a basic help/non-destructive CLI invocation;
15. perform a real FITS-to-TIFF conversion using an approved public-safe fixture;
16. confirm conversion succeeds and output is created;
17. validate the output sufficiently to prove the installed package executed the intended conversion path;
18. remove the environment after recording evidence.

Run commands from outside the repository root where practical.

---

## 9. Sdist validation sequence

For each candidate Python version:

1. create a second fresh temporary virtual environment;
2. install the sdist using normal pip/build isolation;
3. confirm the package builds and installs successfully;
4. run `pip check`;
5. record installed runtime dependencies;
6. confirm pytest/Ruff/PDF tooling are not runtime dependencies;
7. run both version entry points;
8. verify module resolution from site-packages;
9. run a basic CLI invocation;
10. perform the same real FITS-to-TIFF conversion;
11. verify output;
12. remove the environment after recording evidence.

Do not disable build isolation merely to make the installation succeed unless a proven project defect requires investigation.

If build isolation exposes a defect, preserve the failure evidence.

---

## 10. Real conversion fixture

Use only a fixture already approved for public use by:

`tests/data/PRIVACY_REVIEW.md`

Prefer a small fixture that exercises the normal conversion path while keeping validation fast.

Do not use:

- private Stage 8 datasets;
- personal external-drive datasets;
- NAS paths;
- iCloud-specific paths;
- any unreviewed FITS file.

Record the fixture used.

Temporary TIFF output must be written outside tracked repository locations and removed after validation.

---

## 11. Runtime dependency validation

For each clean installation, record the actual installed package set or at minimum the direct/runtime dependencies relevant to Seestar Toolkit.

Verify:

- all required runtime dependencies are present;
- no undeclared development dependency is needed;
- pytest is absent unless explicitly installed for a separate test;
- Ruff is absent;
- PDF-generation tools are absent;
- imports succeed from a runtime-only installation;
- FITS-to-TIFF conversion works without development dependencies.

If a transitive dependency introduces tooling coincidentally, distinguish that from Seestar Toolkit declaring it as a runtime dependency.

---

## 12. Source-tree isolation

This is release-critical.

For each candidate/artifact combination:

- validation must occur outside the repository root where practical;
- `PYTHONPATH` must not point to the repository;
- record `seestar_toolkit.__file__`;
- confirm that path resolves beneath the temporary venv;
- do not invoke code through `src/seestar_toolkit`;
- do not use `pip install -e`.

A validation that accidentally imports the local source tree is invalid and must be rerun.

---

## 13. Python candidate failure handling

Any failure is real evidence.

Do not:

- relabel a failure as PASS;
- silently install additional undeclared dependencies;
- silently change the interpreter;
- change the candidate set merely to obtain a clean result;
- weaken runtime checks.

Permitted remediation includes:

- fixing package metadata;
- fixing dependency constraints;
- fixing genuine runtime defects;
- correcting a faulty validation script;
- installing the intended candidate interpreter correctly;
- narrowing the supported range when evidence shows a candidate is genuinely unsupported.

If a project change is required:

- record the original failure;
- make the minimal justified change;
- rebuild artifacts;
- rerun the affected candidate;
- rerun any broader validation required to prove the change did not regress passing candidates.

---

## 14. Python metadata finalisation

Stage 9.2a is authoritative for final Python support metadata.

After candidate validation:

- compare evidence with current `requires-python` / classifier metadata;
- if the evidence supports all current candidates, retain or adjust metadata so it accurately represents Python 3.11–3.14 support;
- if a candidate fails permanently, narrow metadata accordingly;
- do not claim versions outside the validated set;
- rebuild wheel and sdist after any metadata change;
- inspect rebuilt metadata;
- rerun clean-install validation across the final supported set.

Any metadata change must be reported explicitly.

---

## 15. Homebrew/user-install implications

Stage 9.2a should collect evidence useful for later documentation, including:

- how Homebrew Python was identified;
- interpreter command/path expectations;
- any version-specific Homebrew caveats;
- whether `python3 --version` and `which python3` are sufficient checks;
- whether users need versioned Homebrew formulae for older supported Python lines.

Do not write the final User Guide here; Stage 9.3 owns user-facing documentation.

Record findings in development documentation so Stage 9.3 can use validated facts.

---

## 16. macOS version evidence

Record:

- exact macOS version used for local clean-environment validation;
- architecture output;
- relevant Homebrew architecture where applicable.

Stage 9.2a does not need to prove every Apple-supported macOS version locally.

Do not expand or narrow the macOS support envelope based solely on one local machine unless the evidence requires it.

The exact supported macOS release policy will be stated conservatively in Stage 9.3/9.4 based on Apple-supported versions and available validation evidence.

---

## 17. Automation/script policy

Codex may add a small reusable validation script if that materially improves reproducibility.

Any script must:

- be readable;
- accept explicit interpreter/artifact inputs where appropriate;
- avoid destructive system changes;
- use temporary directories;
- clean up after itself;
- avoid private paths;
- avoid hidden network services;
- not become a release installer;
- not modify shell startup files.

Do not build a complex compatibility framework unnecessarily.

---

## 18. Documentation updates

Update development documentation where needed, likely:

- `docs/development/PACKAGING.md`
- `docs/development/PROJECT_Notes.md`
- `docs/development/CHANGELOG.md` only according to the established post-commit process
- the Stage 9.2a completion report

Record:

- candidate versions tested;
- exact interpreter provenance;
- wheel/sdist outcomes;
- final supported Python range;
- any failed candidate/remediation;
- any package metadata changes.

Do not create final user-facing support/install documentation yet.

---

## 19. CHANGELOG handling

At Stage 9.2a start:

`docs/development/CHANGELOG.md`

contains the pending Stage 9.1d closure entry.

This is expected and must not be treated as an unrelated dirty-tree defect.

During Stage 9.2a:

- preserve the pending Stage 9.1d entry;
- do not add the Stage 9.2a commit ID before that commit exists;
- after ChatGPT approves Stage 9.2a and the user commits it, add the Stage 9.2a entry with its commit ID/message/date;
- intentionally leave that update pending for Stage 9.2b.

---

## 20. Tests and quality

Before closure, run the full applicable project validation from the development environment:

- pytest;
- Ruff;
- configured formatting validation;
- incremental `git diff --check`;
- public-fixture/history validation;
- package build validation.

If production/package metadata changes occur, rerun all relevant tests and CI-sensitive checks.

Do not rely only on manual clean-install results.

---

## 21. GitHub CI relationship

Stage 9.1d CI remains authoritative evidence that all four candidates passed:

- Python 3.11.9;
- Python 3.12.10;
- Python 3.13.15;
- Python 3.14.7;

on macOS arm64 with 329 tests.

Stage 9.2a must not replace or rewrite that evidence.

If Stage 9.2a changes package metadata or runtime code in a way that affects CI, the resulting commit must receive a green GitHub Actions run before final closure.

---

## 22. Scope exclusions

Stage 9.2a does not include:

- archive/storage validation beyond what is necessary for a conversion smoke test;
- external drive/NAS runtime validation;
- installed archive workflow validation;
- user documentation;
- PDF documentation generation;
- final release ZIP assembly;
- release checksums;
- GitHub Release creation;
- tag creation;
- public-repository switch;
- PyPI publishing;
- Linux/Windows testing;
- GUI work;
- S50 Pro/S30/S30 Pro support;
- Solar/Lunar/Planetary MP4 work.

Those belong elsewhere or in future releases.

---

## 23. Expected deliverables

Stage 9.2a must produce:

1. interpreter discovery/provenance record;
2. wheel clean-install results for each candidate;
3. sdist clean-install results for each candidate;
4. runtime dependency evidence;
5. source-tree-isolation evidence;
6. real FITS-to-TIFF conversion evidence;
7. final evidence-based Python support decision;
8. updated package metadata if required;
9. rebuilt/revalidated distributions if metadata changes;
10. development-documentation updates;
11. formal completion report mapped to all closure criteria.

---

## 24. Closure criteria

Stage 9.2a may close only when every applicable criterion below is satisfied or explicitly marked not applicable with sound justification.

### Starting state and scope

1. Work begins from `main` at or after `1771b9f`.
2. Stage 9.1d remains formally complete.
3. Pending Stage 9.1d CHANGELOG modification is preserved.
4. v1.1.0 remains unreleased.
5. Repository remains private.
6. Stage 9.2b work is not begun.
7. Stage 9.3 work is not begun.
8. Stage 9.4 work is not begun.

### Interpreter provenance

9. Python 3.11 candidate is investigated.
10. Python 3.12 candidate is investigated.
11. Python 3.13 candidate is investigated.
12. Python 3.14 candidate is investigated.
13. Exact patch version is recorded for every tested interpreter.
14. Executable path is recorded.
15. Architecture is recorded.
16. macOS version is recorded.
17. Interpreter source/provenance is recorded where determinable.
18. Apple system Python is not modified.

### Clean-environment integrity

19. Fresh temporary venv used for each wheel candidate.
20. Separate fresh temporary venv used for each sdist candidate.
21. Existing development venv is not used for runtime proof.
22. No editable installation is used.
23. `PYTHONPATH` does not provide repository imports.
24. Runtime commands run outside repo root where practical.
25. Site packages are not inherited.
26. Temporary environments are removed after evidence capture.
27. Validation does not depend on private local datasets.

### Wheel — Python 3.11

28. Clean wheel installation succeeds or failure is explicitly preserved.
29. `pip check` succeeds if installation succeeds.
30. CLI version reports 1.1.0.
31. Module version reports 1.1.0.
32. Module resolves from temporary site-packages.
33. Basic CLI invocation succeeds.
34. Real FITS-to-TIFF conversion succeeds.
35. Runtime dependency separation is verified.

### Wheel — Python 3.12

36. Clean wheel installation succeeds or failure is explicitly preserved.
37. `pip check` succeeds if installation succeeds.
38. CLI version reports 1.1.0.
39. Module version reports 1.1.0.
40. Module resolves from temporary site-packages.
41. Basic CLI invocation succeeds.
42. Real FITS-to-TIFF conversion succeeds.
43. Runtime dependency separation is verified.

### Wheel — Python 3.13

44. Clean wheel installation succeeds or failure is explicitly preserved.
45. `pip check` succeeds if installation succeeds.
46. CLI version reports 1.1.0.
47. Module version reports 1.1.0.
48. Module resolves from temporary site-packages.
49. Basic CLI invocation succeeds.
50. Real FITS-to-TIFF conversion succeeds.
51. Runtime dependency separation is verified.

### Wheel — Python 3.14

52. Clean wheel installation succeeds or failure is explicitly preserved.
53. `pip check` succeeds if installation succeeds.
54. CLI version reports 1.1.0.
55. Module version reports 1.1.0.
56. Module resolves from temporary site-packages.
57. Basic CLI invocation succeeds.
58. Real FITS-to-TIFF conversion succeeds.
59. Runtime dependency separation is verified.

### Sdist — Python 3.11

60. Clean sdist installation/build succeeds or failure is explicitly preserved.
61. `pip check` succeeds if installation succeeds.
62. Both version entry points report 1.1.0.
63. Module resolves from temporary site-packages.
64. Real FITS-to-TIFF conversion succeeds.
65. Runtime dependency separation is verified.

### Sdist — Python 3.12

66. Clean sdist installation/build succeeds or failure is explicitly preserved.
67. `pip check` succeeds if installation succeeds.
68. Both version entry points report 1.1.0.
69. Module resolves from temporary site-packages.
70. Real FITS-to-TIFF conversion succeeds.
71. Runtime dependency separation is verified.

### Sdist — Python 3.13

72. Clean sdist installation/build succeeds or failure is explicitly preserved.
73. `pip check` succeeds if installation succeeds.
74. Both version entry points report 1.1.0.
75. Module resolves from temporary site-packages.
76. Real FITS-to-TIFF conversion succeeds.
77. Runtime dependency separation is verified.

### Sdist — Python 3.14

78. Clean sdist installation/build succeeds or failure is explicitly preserved.
79. `pip check` succeeds if installation succeeds.
80. Both version entry points report 1.1.0.
81. Module resolves from temporary site-packages.
82. Real FITS-to-TIFF conversion succeeds.
83. Runtime dependency separation is verified.

### Runtime dependency policy

84. pytest is not required by runtime installation.
85. Ruff is not required by runtime installation.
86. PDF-generation tools are not required by runtime installation.
87. No undeclared dev dependency is required for conversion.
88. Runtime dependency metadata matches observed requirements.

### Fixture/output safety

89. Only an approved public-safe FITS fixture is used.
90. Fixture used is recorded.
91. Temporary TIFF output is outside tracked repo paths.
92. Temporary output is removed.
93. No private Stage 8 data is used.
94. No private path is embedded in committed evidence.

### Python support decision

95. Evidence for all four candidates is evaluated.
96. Final supported Python range is explicitly decided.
97. Final support range is based on evidence, not preference.
98. Any failed candidate remains documented.
99. No unvalidated Python version is claimed.
100. Package Python metadata matches the final supported range.
101. If metadata changes, wheel and sdist are rebuilt.
102. If metadata changes, final supported candidates are revalidated.
103. User-facing support claims remain deferred to Stage 9.3.

### Development documentation

104. PACKAGING.md is updated where needed.
105. PROJECT_Notes.md is updated where needed.
106. Stage 9.2a completion report is created.
107. Interpreter provenance is recorded in committed development evidence.
108. Final Python support decision is recorded in development evidence.
109. Historical validation failures are preserved.
110. Stage 9.1d CI evidence is not rewritten.

### Final project validation

111. Full pytest suite passes.
112. Ruff passes.
113. Configured formatting passes.
114. Incremental `git diff --check` passes.
115. Public-fixture/history validation passes.
116. Wheel/sdist build validation passes.
117. No unexpected generated artifacts are tracked.
118. No unexpected private files are tracked.
119. Git status contains only expected Stage 9.2a changes before approval.
120. Any code/metadata change affecting CI receives appropriate CI revalidation before closure.

### Release-scope control

121. No PyPI publication occurs.
122. No GitHub Release is created.
123. No release tag is created.
124. Repository is not made public.
125. No final release ZIP is created.
126. No Stage 9.2b implementation begins.
127. No Stage 9.3 implementation begins.
128. No Stage 9.4 implementation begins.

### Formal closure

129. Codex returns a complete closure report.
130. Every criterion is individually assessed.
131. Unsatisfied criteria are explicitly listed.
132. Codex does not commit.
133. ChatGPT independently reviews closure evidence.
134. User commits only after explicit approval.
135. Post-commit state is verified.
136. Any commit affecting CI receives a green post-commit GitHub Actions result before Stage 9.2a is marked COMPLETE.
137. Stage 9.2a is not marked COMPLETE until all applicable criteria and post-commit checks pass.

---

## 25. Codex completion report format

Return a concise but complete report containing:

### A. Decision

`PASS` or `FAIL`

### B. Files changed

List every added/modified/deleted file and why.

### C. Interpreter provenance

For each of 3.11, 3.12, 3.13 and 3.14 report:

- exact Python version;
- executable;
- architecture;
- macOS version;
- source/provenance.

### D. Wheel clean-install matrix

For each candidate:

- environment method;
- install result;
- `pip check`;
- module path;
- CLI version;
- module version;
- dependency-separation result;
- real FITS-to-TIFF result.

### E. Sdist clean-install matrix

Same evidence as wheel.

### F. Fixture/output evidence

Report approved fixture used and temporary-output handling.

### G. Candidate failures/remediation

Preserve every failure and explain any remediation.

### H. Final Python support decision

State the evidence-based v1.1.0 support range.

If metadata changes, report the exact change and revalidation performed.

### I. Project validation

Report exact results for:

- pytest;
- Ruff;
- formatting;
- `git diff --check`;
- public-fixture/history validation;
- wheel/sdist build validation.

### J. Scope exclusions

Confirm no publication/tag/release/public-switch and no Stage 9.2b/9.3/9.4 work.

### K. Closure criteria

Assess all 137 criteria individually and identify every unsatisfied criterion.

---

## 26. Commit policy

Codex must **not commit**.

After Codex reports completion:

1. ChatGPT audits all evidence and closure criteria.
2. Any defect is remediated and revalidated.
3. Only after explicit approval does the user commit.

Suggested commit message:

`Stage 9.2a: validate clean installs and Python compatibility`

After the commit:

- update `docs/development/CHANGELOG.md` with Stage 9.2a, final commit ID, message and date;
- leave that CHANGELOG update pending for Stage 9.2b.

---

## 27. Formal close condition

Stage 9.2a closes only after:

- all applicable closure criteria pass;
- the final Python support range is evidence-based and recorded;
- package metadata accurately represents that range;
- clean wheel and sdist runtime validation is complete;
- ChatGPT explicitly approves closure;
- the approved commit exists;
- post-commit GitHub Actions is green if applicable;
- the working tree is in the expected post-commit state.

Only then may Stage 9.2b begin.
