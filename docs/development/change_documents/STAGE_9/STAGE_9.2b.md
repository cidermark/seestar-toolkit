# Stage 9.2b — Installed CLI, Functional and Storage Validation

**Stage:** 9 — Packaging, Documentation and Release
**Section:** 9.2 — Installation & Runtime Validation
**Step:** 9.2b — Installed CLI, functional and storage validation
**Starting commit:** `398b771` — `Stage 9.2a: validate clean installs and Python compatibility`
**Target release:** Seestar Toolkit `v1.1.0`
**Status on opening:** STARTED

## 1. Purpose

Stage 9.2b proves that a normally installed Seestar Toolkit v1.1.0 package is usable as an end-user tool on the supported macOS Apple Silicon platform.

Stage 9.2a established clean installation and Python compatibility. Stage 9.2b validates the installed CLI and realistic workflows: command/help behaviour, single and batch FITS conversion, archive functionality actually exposed by the CLI, configuration/location behaviour, local storage, external/removable storage, mounted network/NAS storage where safely available, cross-storage operation, anticipated filesystem failures, exit codes, privacy/network behaviour, macOS permissions, and uninstall/cleanup facts needed by Stage 9.3.

This is validation, not feature expansion.

## 2. Starting state

- Branch: `main`.
- Starting commit: `398b771`.
- Stage 9.2a is COMPLETE.
- Supported Python: `>=3.11,<3.15` (3.11–3.14).
- Release platform remains macOS Apple Silicon/arm64 under the existing release policy.
- Version remains 1.1.0 and unreleased.
- Repository remains private.
- `docs/development/CHANGELOG.md` contains the intentionally pending Stage 9.2a closure entry; this is expected.

## 3. Representative runtime environment

Do not repeat the Stage 9.2a four-version wheel/sdist matrix. Use one representative supported end-user installation, preferably Homebrew Python 3.13 unless audit evidence justifies another choice.

Use a fresh venv installed from a built v1.1.0 release artifact. Do not use the development editable installation.

Record exact Python version, executable/provenance, architecture, macOS version, artifact and venv/test location. Run outside the checkout where practical and prove `seestar_toolkit.__file__` resolves from the representative venv site-packages.

Do not use `pip install -e`, repository `PYTHONPATH`, or direct execution from `src/`.

## 4. Resumable checkpoints

This step is deliberately resumable.

**Checkpoint A — Audit/design:** inspect installed CLI, archive commands, config implementation, tests and development docs. Determine exact implemented public commands and syntax from code/help, not roadmap assumptions.

**Checkpoint B — Local installed validation:** create the representative clean installation and validate CLI, single conversion, batch conversion, archive/config features actually exposed, and local filesystem/error behaviour.

**Checkpoint C — Storage validation:** validate external/removable and mounted network/NAS storage only when safe disposable locations are available. Never fabricate evidence. User-assisted validation may be requested if Codex cannot safely identify an appropriate mount.

**Checkpoint D — Final audit:** validate privacy/network, permissions, uninstall/cleanup facts, project tests and closure evidence.

Codex may stop after any checkpoint and return the progress format in section 24. A progress report does not close Stage 9.2b.

## 5. Public-safe data and path safety

Use only fixtures approved by `tests/data/PRIVACY_REVIEW.md`. Prefer small fixtures.

Never use private Stage 8 datasets, personal captures, the production archive, unreviewed FITS files, or unrelated external/NAS content.

For directory workflows, create disposable trees from approved fixtures. All mutating archive/storage tests must operate only inside explicitly verified disposable roots. Dry-run first when available.

Committed evidence must not contain usernames/home paths, private volume names, NAS host/share names, credentials, real GPS coordinates, private capture filenames or private FITS metadata.

## 6. Installed CLI inventory

From the installed artifact validate:

- `seestar-toolkit --version`;
- `python -m seestar_toolkit --version`;
- top-level help;
- help for every public subcommand;
- successful help/version exit statuses.

Create an authoritative inventory of installed public commands/options for Stage 9.3. Distinguish internal Python APIs from released CLI features.

If development docs disagree with installed behaviour, record/correct development documentation. Do not redesign the CLI for documentation convenience.

## 7. Single conversion

Using an approved fixture, validate installed `convert` behaviour:

- successful FIT/FITS input;
- TIFF creation and success exit status;
- readable 16-bit RGB TIFF with correct dimensions;
- source remains unchanged;
- existing-output behaviour;
- missing-input behaviour;
- invalid/unsupported-input behaviour where safely testable;
- cleanup of temporary output.

Reuse existing stronger independent pixel/content validators where appropriate.

## 8. Batch conversion

Using a disposable input tree built only from approved fixtures, validate:

- multiple supported inputs;
- expected TIFF outputs;
- intact sources;
- unrelated/unsupported-file behaviour;
- output-directory handling;
- success exit status;
- partial/error behaviour;
- repeated invocation/existing-output behaviour;
- cleanup.

Do not invent recursive or overwrite semantics not present in the implementation.

## 9. Archive CLI audit and validation

First determine the exact installed archive CLI surface. Validate only functionality actually exposed.

Audit, where present: source/input root, archive destination, hierarchy/template, plan/dry-run, apply/execution, source action, JPEG policy, stacked FITS/TIFF handling, location resolution, saved locations/config, session/observation handling, index generation, diagnostics and exit statuses.

If archive planning/dry-run is public, use disposable test data and verify applicable established behaviour including default `{target}/{location}/{date}`, +12-hour archive date rule, `session_01`, `seestar_stacked`, source/JPEG/index plan, and no dry-run mutation.

If mutating archive operation is public, inspect dry-run first, safety-check exact disposable roots, execute, verify hierarchy/files/source action/JPEG/index/session behaviour, prove nothing outside disposable roots changed, then clean up.

If functionality exists internally but is not exposed by the released CLI, record that distinction; do not add a new feature in 9.2b.

## 10. Configuration and location

Audit actual implementation. Expected config path is `~/.config/seestar-toolkit/config.toml`.

Where exposed, validate missing config, read, create/write, malformed config, saved locations, location fallback/unknown behaviour and relevant GPS-derived handling.

Never modify the real user config. Redirect HOME/XDG config to a temporary isolated location where practical. Never commit real personal coordinates.

No external geocoding/network service should be silently required unless already explicitly part of implementation/policy; unexpected network behaviour is release-critical.

## 11. Local filesystem

Using disposable local paths validate:

- writable local operation;
- paths containing spaces;
- nested paths;
- existing destinations;
- missing destination creation where expected;
- non-existent input;
- file-vs-directory mistakes where relevant.

Record exact behaviour and exit status.

## 12. External/removable storage

If a safe mounted external/removable filesystem is available, create one uniquely named disposable Stage 9.2b directory and perform minimal representative installed operations using approved fixtures only.

Do not inspect unrelated volume contents or touch the production astronomy archive.

Record privacy-safe mount/filesystem evidence and result. Remove the disposable directory afterwards.

If unavailable, report that honestly. Do not fabricate PASS.

## 13. Mounted network/NAS storage

If a safe already-mounted network filesystem is available, create a dedicated disposable directory and perform minimal representative read/write validation.

Do not configure SMB/NFS, handle credentials, enumerate unrelated NAS content or touch production archive directories. This validates an already-mounted filesystem, not a Toolkit network service.

Record privacy-safe mount evidence and result; clean up. If unavailable, report honestly.

## 14. Cross-storage

Where safely possible, validate at least one source/output combination on different storage roots (for example local→external, external→local or local→mounted-network). Use disposable data only.

Record any inability to perform this validation rather than inventing evidence.

## 15. Errors, permissions and exit codes

Using disposable paths, safely exercise representative missing input, unreadable input if practical, unwritable destination if practical, file-vs-directory error, invalid config and malformed/unsupported input.

Prove useful diagnostics, no unintended source loss and no destructive partial archive operation. Restore any temporary permission changes.

Audit the established exit contract:

- `0` success;
- `1` operational/runtime failure;
- `2` command-line/usage error.

Any discrepancy is a genuine finding.

## 16. Privacy/network and macOS permissions

Confirm by code/runtime audit that the Toolkit does not provide telemetry, analytics, update checks or external image/FITS metadata transmission.

Mounted network filesystem I/O is not telemetry. Do not introduce network access for validation.

Record observed macOS permission prompts/requirements conservatively. Do not bypass privacy controls or claim Full Disk Access is required without evidence.

## 17. Uninstall/cleanup facts

Using disposable representative environment/config paths, establish facts needed by Stage 9.3:

- `deactivate` behaviour;
- package/venv removal behaviour;
- package uninstall does not automatically remove user config;
- config is removable separately;
- generated/archive user data is not automatically removed.

Do not remove the development venv or real config.

## 18. Change policy

Stage 9.2b is primarily validation. Production changes are permitted only for proven release defects.

Preserve original failure evidence, make the minimum justified fix, add/update automated tests, rerun affected installed validation and full project validation.

Do not add new features. Future enhancements belong in `PROJECT_Notes.md`.

Small development-only validation helpers are allowed if safe, explicit-path, privacy-safe and non-destructive. Prefer extending existing validation tooling where sensible.

## 19. Development documentation and CHANGELOG

Update development docs only where validated findings require it, likely `PACKAGING.md`, `PROJECT_Notes.md`, and Stage 9.2b report/evidence.

Capture exact validated CLI syntax/facts for Stage 9.3, but do not author the final User Guide or Quick Start.

Preserve the pending Stage 9.2a entry in `docs/development/CHANGELOG.md`. Do not add the Stage 9.2b commit ID before it exists.

After approved Stage 9.2b commit, add its commit ID/message/date to the development CHANGELOG and leave that edit pending for Stage 9.3a.

## 20. Final project validation

Before closure run and record:

- full pytest;
- Ruff;
- configured formatting;
- `git diff --check`;
- public-fixture/history safety validation;
- installed Stage 9.2b validator if added;
- distribution build/inspection if package/runtime/metadata changes make it relevant.

No unexpected generated/private files may be tracked.

If CI-relevant files change, the exact final Stage 9.2b commit must receive green GitHub Actions before formal closure. A manual rerun against the exact SHA is acceptable if jobs do not trigger automatically, provided no genuine failed validation is concealed.

## 21. Scope exclusions

Do not: repeat the Stage 9.2a Python matrix; author final user docs/PDFs; create documentation/release checksums; assemble final release ZIP; create tag/GitHub Release; make repository public; publish to PyPI; add Linux/Windows/Intel support; add GUI/new Seestar model/DSLR/MP4 features; begin Stage 9.3 or 9.4.

## 22. Expected deliverables

1. Installed CLI inventory.
2. Representative installed-environment provenance.
3. Single conversion evidence.
4. Batch conversion evidence.
5. Archive CLI audit and exposed-workflow evidence.
6. Configuration/location evidence where exposed.
7. Local storage evidence.
8. External/removable evidence if safely available.
9. Mounted network/NAS evidence if safely available.
10. Cross-storage evidence where feasible.
11. Error/permission/exit-code evidence.
12. Privacy/network/macOS permission observations.
13. Uninstall/cleanup observations.
14. Development documentation updates.
15. Formal completion report and optional structured evidence.

## 23. Closure criteria

### Starting state
1. Branch is `main`.
2. Work starts at or after `398b771`.
3. Stage 9.2a remains COMPLETE.
4. Pending Stage 9.2a CHANGELOG entry is preserved.
5. Version remains 1.1.0.
6. v1.1.0 remains unreleased.
7. Repository remains private.
8. Stage 9.3 has not begun.
9. Stage 9.4 has not begun.

### Representative installed environment
10. Representative supported Python is justified.
11. Exact patch version is recorded.
12. Executable/provenance is recorded.
13. macOS version is recorded.
14. arm64 is confirmed.
15. Fresh venv is used.
16. Distribution artifact is installed.
17. No editable install is used.
18. Development venv is not runtime proof.
19. Repository PYTHONPATH is not used.
20. Module resolves from representative site-packages.
21. Commands run outside checkout where practical.

### Installed CLI
22. `seestar-toolkit --version` passes.
23. `python -m seestar_toolkit --version` passes.
24. Both report 1.1.0.
25. Top-level help passes.
26. Every public subcommand is inventoried.
27. Every public subcommand help is validated.
28. Exact public syntax is recorded for Stage 9.3.
29. Internal APIs are not presented as public CLI.

### Single conversion
30. Approved fixture is used.
31. Installed convert succeeds.
32. Success exit status is correct.
33. TIFF is created.
34. TIFF is readable.
35. Dimensions are correct.
36. RGB structure is correct.
37. 16-bit output is confirmed.
38. Source is unchanged.
39. Existing-output behaviour is recorded.
40. Missing-input behaviour is recorded.
41. Invalid/unsupported behaviour is recorded where safely testable.
42. Temporary outputs are cleaned.

### Batch conversion
43. Disposable batch tree is used.
44. Only approved fixtures populate it.
45. Multiple supported inputs are exercised.
46. Expected TIFF outputs are created.
47. Sources remain intact.
48. Unsupported/unrelated-file behaviour is recorded.
49. Output-directory behaviour is correct.
50. Success exit status is correct.
51. Error/partial behaviour is recorded.
52. Repeated/existing-output behaviour is recorded.
53. Temporary data is cleaned.

### Archive
54. Exact public archive CLI surface is audited.
55. Source/destination semantics are recorded.
56. Hierarchy/template semantics are recorded where exposed.
57. Plan/dry-run availability is recorded.
58. Mutating/apply availability is recorded.
59. Source/JPEG/stacked/location/session/index semantics are recorded.
60. Internal-only functionality is distinguished from CLI.
61. Public dry-run is validated if exposed.
62. Disposable source is used for archive validation.
63. Discovery/reconstruction result is correct for test data where applicable.
64. Planned hierarchy matches design where applicable.
65. +12-hour rule is verified where applicable.
66. `session_01` is verified where applicable.
67. `seestar_stacked` is verified where applicable.
68. Dry-run causes no unintended mutation.
69. Public mutating operation is tested if exposed.
70. Dry-run is inspected first where available.
71. Exact disposable roots are safety-checked.
72. Executed hierarchy/files/actions match plan where applicable.
73. Nothing outside disposable roots is modified.
74. Archive test data is cleaned.

### Configuration/location
75. Actual config implementation is audited.
76. Expected config path is verified or discrepancy recorded.
77. Missing-config behaviour is validated.
78. Read/write/create behaviour is validated where exposed.
79. Malformed config behaviour is validated.
80. Real user config is untouched.
81. Temporary isolated config is used where practical.
82. Saved-location behaviour is validated where exposed.
83. Fallback/unknown location behaviour is validated where exposed.
84. No personal GPS enters committed evidence.
85. No unexpected external geocoding/network dependency exists.

### Local storage
86. Writable local operation succeeds.
87. Paths containing spaces are exercised.
88. Nested paths are exercised.
89. Existing destination behaviour is recorded.
90. Missing destination creation is validated where expected.
91. Non-existent input behaviour is validated.
92. File/directory type errors are validated where relevant.

### External/removable
93. Safe external/removable availability is assessed.
94. If available, only a disposable directory is used.
95. If available, representative operation passes or genuine failure is preserved.
96. If unavailable, limitation is honestly recorded.
97. Production astronomy archive is untouched.
98. Identifying volume path is not committed.

### Mounted network/NAS
99. Safe mounted-network availability is assessed.
100. If available, only a disposable directory is used.
101. If available, representative operation passes or genuine failure is preserved.
102. If unavailable, limitation is honestly recorded.
103. No credentials are stored.
104. Production NAS archive is untouched.
105. Identifying NAS details are not committed.
106. Mounted I/O is distinguished from Toolkit network-service behaviour.

### Cross-storage
107. Cross-storage is attempted where feasible.
108. At least one different-root scenario passes where feasible.
109. No same-filesystem assumption is introduced.
110. Inability to test is recorded.

### Errors/exit codes
111. Missing input non-zero behaviour is validated.
112. Unwritable destination is tested where safely reproducible.
113. File-vs-directory error is tested where relevant.
114. Invalid config is tested where relevant.
115. Unsupported/malformed input is tested.
116. Anticipated errors provide useful diagnostics.
117. No unintended source loss occurs.
118. Temporary permissions are restored.
119. Exit 0 is verified for success.
120. Exit 1 is verified for operational failure.
121. Exit 2 is verified for usage error.
122. Any discrepancy is treated as a finding.

### Privacy/network/permissions
123. No telemetry is found.
124. No analytics is found.
125. No update checking is found.
126. No external FITS/image metadata transmission is found.
127. No network access is introduced for validation.
128. Mounted network I/O is characterised accurately.
129. Unexpected network behaviour is release-blocking.
130. Observed macOS permission requirements are recorded.
131. Privacy controls are not bypassed.
132. Full Disk Access is not claimed necessary without evidence.

### Uninstall/cleanup
133. `deactivate` behaviour is recorded.
134. package/venv removal behaviour is recorded.
135. Config persistence after uninstall is understood.
136. Separate config removal is understood.
137. User/archive data is not automatically removed.
138. Development venv is untouched.
139. Real user config is untouched.

### Evidence/docs/project validation
140. Installed CLI inventory is committed in development evidence.
141. Environment provenance is recorded.
142. Conversion evidence is recorded.
143. Batch evidence is recorded.
144. Archive evidence/limitations are recorded.
145. Storage evidence/limitations are recorded.
146. Error/exit evidence is recorded.
147. Privacy/permission/uninstall observations are recorded.
148. No private paths/credentials/GPS are committed.
149. Completion report is created.
150. Structured evidence is added if useful.
151. PACKAGING.md is updated where needed.
152. PROJECT_Notes.md is updated where needed.
153. Final user docs are not authored.
154. Full pytest passes.
155. Ruff passes.
156. Formatting passes.
157. `git diff --check` passes.
158. Public-fixture/history validation passes.
159. Installed validator passes if added.
160. Distribution validation passes where relevant.
161. No unexpected generated artifacts are tracked.
162. No unexpected private files are tracked.
163. Pre-approval working tree contains only expected changes.

### Change/release control
164. Genuine failures are preserved.
165. Production changes occur only for proven defects.
166. Production fixes receive automated tests.
167. Affected installed validation is rerun after fixes.
168. Full validation is rerun after fixes.
169. No new feature work is introduced.
170. No PyPI publication occurs.
171. No GitHub Release is created.
172. No release tag is created.
173. Repository is not made public.
174. No final release ZIP is created.
175. Stage 9.3 implementation does not begin.
176. Stage 9.4 implementation does not begin.

### Formal closure
177. Codex returns a complete closure report.
178. All criteria are individually assessed.
179. Every N/A has explicit justification.
180. Unsatisfied criteria are listed.
181. Codex does not commit.
182. ChatGPT independently reviews evidence.
183. User commits only after explicit approval.
184. Post-commit repository state is verified.
185. Exact final commit receives green CI where required.
186. Stage 9.2b is not marked COMPLETE until all applicable gates pass.

## 24. Codex progress report format

If pausing before completion, return:

**A. Status:** `PAUSED — Stage 9.2b remains STARTED`

**B. Checkpoint reached:** A, B, C or D.

**C. Work completed:** exact validations/results.

**D. Files changed:** every file changed so far.

**E. Findings:** preserve PASS/FAIL findings.

**F. Next action:** exact next checkpoint/command or user-assisted storage requirement.

Do not claim formal closure from a progress report.

## 25. Codex completion report format

Return:

**A. Decision** — PASS/FAIL for formal closure readiness.

**B. Files changed** — every added/modified/deleted file and reason.

**C. Representative environment** — Python/provenance/macOS/architecture/artifact/isolation.

**D. Installed CLI inventory** — exact public commands/options/help/version.

**E. Conversion results** — single and batch.

**F. Archive results** — CLI audit, dry-run/planning/execution or explicit N/A.

**G. Configuration/location results** — behaviour and isolation.

**H. Storage results** — local, external/removable, network/NAS, cross-storage.

**I. Error/exit-code results** — exact representative behaviour.

**J. Privacy/permissions/uninstall results**.

**K. Findings/remediation** — preserve every failure and correction.

**L. Project validation** — pytest/Ruff/format/whitespace/public-fixture/build/installed validation.

**M. Scope exclusions** — confirm no release/tag/publication/public-switch/9.3/9.4.

**N. Closure criteria** — assess all 186 criteria individually, justify N/A, list unsatisfied criteria.

## 26. Commit policy

Codex must **not commit**.

ChatGPT reviews the report/evidence first. User commits only after explicit approval.

Suggested commit message:

`Stage 9.2b: validate installed CLI and storage workflows`

After commit, add Stage 9.2b commit ID/message/date to `docs/development/CHANGELOG.md` and leave that update pending for Stage 9.3a.

## 27. Formal close condition

Stage 9.2b closes only after all applicable criteria pass; every N/A is justified; no release-critical operational defect remains; ChatGPT approves; the approved commit exists; required post-commit CI is green; and the working tree is in the expected post-commit state.

Only then is Stage 9.2 COMPLETE and Stage 9.3a permitted to begin.
