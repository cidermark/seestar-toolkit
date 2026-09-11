# STAGE 7.1g — Archive CLI, interaction and dry-run

## Status

**Stage:** 7.1g  
**Stage title:** Archive CLI, interaction and dry-run  
**Starting commit:** `07fde20` — `Stage 7.1f: integrate archive TIFF orchestration`  
**Implementation status:** Not yet implemented  
**Commit policy:** Codex must not commit changes.

The intentional `docs/CHANGELOG.md` modification recording Stage 7.1f may already be present in the working tree. It is expected and must not be treated as an unexpected dirty-tree condition.

---

## 1. Purpose

Stage 7.1g exposes the completed Stage 7 archive pipeline through the command line.

This is the first stage in which a user should be able to point Seestar Toolkit at a Seestar `My Works` directory and request an archive operation from the CLI.

Stage 7.1g must provide:

- an archive CLI command;
- clear command-line configuration for archive root, hierarchy, source action and collision policy;
- non-interactive operation;
- interactive location resolution where appropriate;
- saved-location configuration loading;
- user-facing dry-run;
- deterministic exit codes;
- concise but useful plan/result reporting.

This stage must preserve the library architecture established in Stages 7.1a–7.1f.

---

## 2. Required outcome

After Stage 7.1g, a user must be able to run a command conceptually similar to:

```text
seestar-toolkit archive SOURCE_ROOT ARCHIVE_ROOT
```

and optionally:

```text
seestar-toolkit archive SOURCE_ROOT ARCHIVE_ROOT --dry-run
```

The exact argparse syntax may follow existing CLI style, but the command must:

1. discover Seestar inputs;
2. reconstruct observations;
3. plan archive destinations;
4. resolve location according to the agreed policy;
5. show the planned operation in dry-run without mutation;
6. execute the Stage 7.1f orchestration path for real runs;
7. report success/partial/failure clearly;
8. return deterministic exit codes.

---

## 3. Preserve existing Stage 6 CLI

Existing commands must remain unchanged:

```text
seestar-toolkit convert INPUT_FITS OUTPUT_TIFF
seestar-toolkit convert-batch INPUT_DIR OUTPUT_DIR
```

Existing exit semantics must remain:

- 0 success;
- 1 expected failure/partial/no matches;
- 2 usage error.

`convert-batch` must remain flat and non-recursive.

Do not rename, repurpose, or overload the existing Stage 6 commands.

---

## 4. New archive command

Add a dedicated archive subcommand.

Recommended syntax:

```text
seestar-toolkit archive SOURCE_ROOT ARCHIVE_ROOT [options]
```

Required positional arguments:

- `SOURCE_ROOT`
  - normally the Seestar `My Works` directory;
- `ARCHIVE_ROOT`
  - absolute archive destination root, unless existing CLI conventions justify early normalization.

Recommended options:

```text
--dry-run
--location NAME
--hierarchy TEMPLATE
--source-action {copy,move}
--collision-policy {skip-identical,error,overwrite}
--non-interactive
--config PATH
```

Exact option naming may follow current argparse conventions.

Do not add unnecessary aliases.

---

## 5. Archive hierarchy option

Default hierarchy remains:

```text
{target}/{location}/{session_end_date}
```

CLI must allow an alternative hierarchy template supported by Stage 7.1d.

The CLI must not implement its own hierarchy parser.

Pass the value to the existing planner and surface planner configuration errors clearly.

---

## 6. Source action option

Default:

```text
copy
```

Explicit alternative:

```text
move
```

Map CLI input to the existing `SourceAction` model.

Do not duplicate MOVE safety logic in the CLI.

---

## 7. Collision policy option

Expose the Stage 7.1e collision policy.

At minimum support the implemented policy values:

- skip-identical;
- error;
- overwrite.

Default must remain safe and non-destructive.

Recommended default:

```text
skip-identical
```

Do not silently convert differing-content collisions into overwrite.

---

## 8. Dry-run contract

`--dry-run` is a strict zero-mutation mode.

It must execute the same discovery, reconstruction and planning logic required by a real run, including location resolution and all relevant validation.

It must NOT:

- create archive directories;
- copy FITS files;
- move FITS files;
- delete source files;
- overwrite files;
- generate TIFF files;
- create INDEX.md;
- modify configuration;
- save new locations;
- create temp/staging files.

Dry-run should report what **would** happen.

This is a hard closure condition.

---

## 9. Dry-run implementation boundary

Do not implement dry-run by invoking mutating execution code and trying to suppress pieces of it.

Preferred architecture:

```text
discovery
-> reconstruction
-> location resolution
-> planning
-> render plan
-> stop
```

Real execution:

```text
discovery/reconstruction/location/planning
-> Stage 7.1e/7.1f execution
```

If Stage 7.1f currently performs discovery/reconstruction/planning internally, minimal refactoring is acceptable so CLI and dry-run can share the same authoritative planning path without duplicate logic.

Do not introduce a second planner.

---

## 10. Location policy

Stage 7.1a fixed the precedence:

1. explicit CLI/user location;
2. saved configured location matched from FITS GPS;
3. optional reverse-geocoded suggestion;
4. interactive manual entry;
5. `unknown`.

Stage 7.1g must implement the portions possible without a network provider:

1. explicit `--location`;
2. saved-location GPS matching;
3. interactive confirmation/manual entry where appropriate;
4. `unknown` fallback.

Reverse geocoding remains optional/deferred because no provider has been approved.

Do not hard-wire Nominatim or any public geocoder.

---

## 11. Explicit location

`--location NAME` wins.

Requirements:

- no prompt is required when explicit location is supplied;
- logical location value is passed through Stage 7.1d normalization/planning;
- empty/whitespace-only values should be rejected or treated consistently as absent;
- no location is saved automatically merely because it was supplied.

---

## 12. Saved locations

Stage 7.1d already defines `SavedLocation`.

Stage 7.1g must load saved locations from configuration.

Recommended TOML representation:

```toml
[[locations]]
name = "Warfield"
latitude = 51.4
longitude = -0.7
radius_m = 500
```

Exact key names may follow project conventions but must be documented and tested.

The loader must produce existing `SavedLocation` objects rather than duplicating GPS matching logic.

---

## 13. Configuration file

Use TOML.

Use Python standard-library `tomllib` for reading where available.

Configuration should be reusable by CLI and a future UI.

Do not introduce a large settings framework.

Recommended configuration concerns for this stage:

```toml
[archive]
hierarchy = "{target}/{location}/{session_end_date}"
source_action = "copy"
collision_policy = "skip-identical"

[[locations]]
name = "Warfield"
latitude = ...
longitude = ...
radius_m = ...
```

CLI arguments should override configuration values.

---

## 14. Default configuration path

Define one deterministic default user configuration path appropriate to the existing project and macOS/POSIX use.

Prefer a cross-platform/user-home convention such as:

```text
~/.config/seestar-toolkit/config.toml
```

or an existing project convention if one already exists.

Document the choice.

An explicit `--config PATH` must override default path discovery.

A missing default config file must not be treated as an error.

A missing explicitly requested config file should be reported clearly.

---

## 15. Configuration writing scope

Stage 7.1g may support saving a manually entered location if the interaction contract can be implemented safely and minimally.

However, configuration writing is not required merely to satisfy archive execution.

If saving is implemented:

- it must require explicit user consent;
- dry-run must never write config;
- writes must be safe/atomic where practical;
- existing unrelated config content must not be silently discarded;
- duplicate location naming must be handled deterministically.

If safe TOML round-tripping would require a new dependency or broad configuration framework, defer location persistence and keep the config loader read-only in Stage 7.1g.

The CLI may still prompt for a one-run manual location.

---

## 16. Interactive mode

Default CLI operation may be interactive when attached to a terminal.

Interaction must be limited and deterministic.

At minimum, when no explicit location is supplied and no saved location matches:

- user may enter a location name;
- user may choose/accept `unknown`.

Do not require interaction for other planner decisions.

---

## 17. Saved-location match interaction

When GPS matches a configured location in interactive mode, the CLI may:

```text
Location matched: Warfield
Use this location? [Y/n]
```

Required behavior:

- accepting uses the saved name;
- rejecting allows manual location entry or `unknown`;
- no prompt in non-interactive mode.

If implementation chooses automatic acceptance in interactive mode, it must still provide a clear manual override path through `--location`.

Preferred behavior is confirmation, because Stage 7.1a explicitly anticipated accept/reject interaction.

---

## 18. Non-interactive mode

Provide a way to suppress all prompts.

Recommended:

```text
--non-interactive
```

Non-interactive precedence:

1. explicit `--location`;
2. matching saved location;
3. `unknown`.

Never block waiting for stdin.

This behavior must be tested.

---

## 19. TTY awareness

If practical, avoid prompting when stdin is not interactive even if `--non-interactive` was not supplied.

A reasonable policy:

```python
interactive = not args.non_interactive and sys.stdin.isatty()
```

Tests must avoid depending on a real terminal.

---

## 20. Manual location entry

Interactive manual entry should:

- trim surrounding whitespace;
- permit ordinary spaces;
- preserve logical case;
- accept a clear blank/unknown choice;
- rely on Stage 7.1d for archive-component normalization.

Do not duplicate path normalization in the CLI.

---

## 21. Multiple observation/location considerations

A single archive invocation may contain multiple observations.

Location resolution must remain coherent with Stage 7.1d.

If the source set contains GPS coordinates that resolve differently across observations, do not silently force all observations to one saved location unless an explicit `--location` override was supplied.

If current Stage 7.1d planning API resolves saved locations per observation, preserve that behavior.

Interactive prompting should not become a complex per-file prompt loop.

If multiple unresolved logical locations make a single manual location unsafe, surface the issue explicitly rather than guessing.

---

## 22. User-facing dry-run output

Dry-run should be concise but useful.

For each planned observation, show enough to understand:

- target;
- resolved location;
- session end date;
- observation number;
- number of light FITS;
- stack FITS if present;
- planned destination directory;
- source action that would be used;
- TIFF destinations or count;
- any planning problems.

Exact formatting may be plain text.

Do not build a full table/rendering framework.

---

## 23. Real-run output

Real execution should summarize:

- observations planned;
- FITS copied;
- FITS moved;
- identical FITS skipped;
- original-file failures/collisions;
- TIFFs created;
- TIFF collisions;
- TIFF failures;
- overall COMPLETE/PARTIAL/FAILED result.

Per-file diagnostics may be printed for failures/collisions.

Avoid excessive success spam unless useful.

---

## 24. Exit codes

Preserve Stage 6 conventions.

Archive command should use:

```text
0 = complete success
1 = expected archive failure, collision, partial completion, planning problem, or other operational failure
2 = command-line usage/configuration syntax error handled by argparse
```

A genuinely empty no-op archive result may return 0 if Stage 7.1f defines it as COMPLETE.

Invalid configuration content encountered after argument parsing should normally return 1 unless it is naturally represented as argparse usage error.

Be consistent and test the mapping.

---

## 25. Error handling

CLI should catch expected project/archive exceptions and present concise diagnostics.

Do not catch broad programming errors merely to force exit code 1.

Unexpected exceptions should remain visible during development.

Avoid traceback output for ordinary expected user/file/configuration errors where existing CLI conventions suppress it.

---

## 26. Configuration precedence

Required precedence, highest first:

1. command-line option;
2. configuration file value;
3. established default.

At minimum apply this to:

- hierarchy;
- source action;
- collision policy.

Location has its separate precedence rules.

---

## 27. Invalid configuration

Reject clearly invalid config.

Examples:

- malformed TOML;
- `locations` entry missing required fields;
- invalid latitude/longitude;
- invalid radius;
- unsupported source action;
- unsupported collision policy;
- hierarchy value of wrong type.

Use existing Stage 7.1d models for validation where possible.

Diagnostics should identify the problem.

---

## 28. Configuration comments/unknown keys

Unknown unrelated keys may be ignored for forward compatibility unless project conventions dictate strict validation.

Do not fail merely because a future setting is present.

Document this policy.

---

## 29. Archive root handling

Pass archive root into existing planning logic.

Do not create archive root during dry-run.

Real execution may create it only as required by Stage 7.1e/7.1f.

Do not duplicate archive-root traversal validation.

---

## 30. Source root handling

Use the existing discovery API.

Do not add a separate recursive scanner.

The source root should normally be `My Works`.

Existing Stage 7.1b bounded discovery behavior remains unchanged.

---

## 31. CLI-to-library separation

Keep argparse/UI concerns outside core archive planning/execution models.

Recommended organization:

```text
cli.py
archive/config.py          (if needed)
archive/interaction.py     (only if small/useful)
```

Do not contaminate planner/executor models with argparse Namespace or terminal I/O.

---

## 32. Dry-run and orchestration reuse

To avoid duplicate pipeline logic, it is acceptable to add a non-mutating preparation API such as:

```python
prepare_seestar_archive(...)
```

that returns discovery/reconstruction/plan.

Then:

```text
dry-run -> prepare -> render
real run -> prepare -> execute prepared plan / orchestration
```

Alternatively, refactor `archive_seestar_session()` internally.

Any such refactoring must preserve 7.1f semantics and tests.

---

## 33. Avoid double discovery

A real CLI invocation must not unnecessarily perform discovery/reconstruction/planning twice.

If dry-run and real-run paths share preparation logic, real execution should consume that prepared result where feasible.

If minimal refactoring is needed, add explicit tests/inspection proving the pipeline is not duplicated accidentally.

---

## 34. No INDEX.md

Do not generate target indexes.

Stage 7.1h owns this.

---

## 35. JPEG policy

JPEG and thumbnail files remain ignored/untouched.

Do not add CLI switches to delete them in 7.1g.

---

## 36. Compression

Do not expose gzip/zip/tgz source actions.

Compression remains deferred.

---

## 37. Reverse geocoding

No network geocoder.

No automatic public API calls.

If future provider support is anticipated, keep boundaries extensible only.

---

## 38. DSLR boundary

No DSLR/Canon ingestion.

---

## 39. Dry-run filesystem proof

Tests must prove zero mutations.

At minimum snapshot or assert:

- archive root absent before and after dry-run;
- source hashes unchanged;
- source mtimes unchanged where stable/reliable;
- no destination directories;
- no TIFF files;
- no temp files;
- no config writes.

Use temporary filesystem fixtures.

---

## 40. CLI tests

Add focused CLI/integration tests.

At minimum cover:

1. archive command is registered;
2. help describes command/options;
3. Stage 6 convert still works;
4. Stage 6 convert-batch still works;
5. archive default action is COPY;
6. `--source-action move` maps to MOVE;
7. collision policy parsing;
8. hierarchy option pass-through;
9. config defaults applied;
10. CLI overrides config;
11. missing default config is allowed;
12. missing explicit config is reported;
13. malformed TOML is reported;
14. invalid saved location is reported;
15. explicit location wins;
16. saved GPS location used in non-interactive mode;
17. unmatched GPS -> unknown in non-interactive mode;
18. interactive saved-location acceptance;
19. interactive saved-location rejection/manual entry;
20. blank manual location -> unknown;
21. `--non-interactive` never prompts;
22. non-TTY mode never prompts if TTY-awareness implemented;
23. dry-run runs discovery/reconstruction/planning;
24. dry-run produces useful plan output;
25. dry-run creates no archive directory;
26. dry-run copies no FITS;
27. dry-run moves/deletes no FITS;
28. dry-run generates no TIFF;
29. dry-run writes no configuration;
30. real COPY archive CLI integration;
31. real MOVE archive CLI integration;
32. complete archive returns exit 0;
33. partial/failure archive returns exit 1;
34. planning/config operational error returns exit 1;
35. usage error remains argparse exit 2;
36. empty complete no-op mapping;
37. JPEGs remain untouched;
38. no INDEX.md generated;
39. no compression;
40. no reverse-geocoder/network calls;
41. Stage 7.1f tests remain green;
42. Stage 7.1e tests remain green;
43. Stage 7.1d tests remain green;
44. Stage 7.1c tests remain green;
45. Stage 7.1b tests remain green;
46. Stage 5/6 conversion and CLI tests remain green;
47. full suite remains green.

---

## 41. Documentation

Update as required:

- preserve `docs/change_documents/STAGE_7/STAGE_7.1g.md` as authoritative;
- update `docs/PROJECT_Notes.md`;
- update `docs/ARCHITECTURE.md`;
- update CLI usage documentation if README or another existing CLI doc owns that content;
- preserve pending `docs/CHANGELOG.md` entry recording `07fde20`.

Do not mark Stage 7.1g complete before Stage-chat review.

---

## 42. Explicit exclusions

Do not implement:

- INDEX.md generation;
- Stage 7.1h work;
- broad Stage 7 workflow validation/closure;
- Stage 7.1i work;
- Stage 7.1j closure;
- reverse-geocoder providers;
- JPEG deletion/archive;
- compression;
- DSLR ingestion;
- new FITS classification;
- new demosaicing;
- new TIFF encoding;
- Stage 8 qualification;
- Stage 9 packaging/release.

---

## 43. Validation

Run at least:

```text
pytest
ruff check .
git diff --check
```

Run formatting validation on changed Python files.

Explicitly confirm:

- Stage 7.1f orchestration tests green;
- Stage 7.1e execution tests green;
- Stage 7.1d planning tests green;
- Stage 7.1c reconstruction tests green;
- Stage 7.1b discovery tests green;
- Stage 5/6 conversion and CLI tests green;
- `convert` behavior unchanged;
- `convert-batch` flat/non-recursive behavior unchanged;
- dry-run zero filesystem mutations;
- no INDEX.md;
- no compression;
- no network/reverse geocoding;
- Stage 7.1h not started.

---

## 44. Closure criteria

1. Dedicated archive CLI command exists.
2. Existing `convert` command remains unchanged.
3. Existing `convert-batch` command remains unchanged.
4. `convert-batch` remains flat/non-recursive.
5. Archive CLI accepts source root.
6. Archive CLI accepts archive root.
7. Archive CLI supports dry-run.
8. Archive CLI supports explicit location.
9. Archive CLI supports hierarchy template.
10. Archive CLI supports source action.
11. Archive CLI supports collision policy.
12. Archive CLI supports non-interactive operation.
13. Archive CLI supports explicit config path.
14. COPY remains default.
15. MOVE requires explicit selection.
16. Default collision policy is non-destructive.
17. CLI maps source-action values to existing `SourceAction`.
18. CLI maps collision values to existing `CollisionPolicy`.
19. CLI does not duplicate MOVE safety.
20. CLI does not duplicate collision hashing.
21. CLI does not duplicate FITS discovery.
22. CLI does not duplicate reconstruction.
23. CLI does not duplicate planning.
24. CLI does not duplicate TIFF conversion.
25. Default hierarchy remains `{target}/{location}/{session_end_date}`.
26. Hierarchy CLI override passes through planner.
27. Invalid hierarchy surfaces clearly.
28. TOML configuration loading exists.
29. Standard-library `tomllib` is used unless project constraints require otherwise.
30. Missing default config is allowed.
31. Missing explicit config is reported.
32. Malformed TOML is reported.
33. Configuration can provide hierarchy default.
34. Configuration can provide source-action default.
35. Configuration can provide collision-policy default.
36. Configuration can provide saved locations.
37. Saved locations become existing `SavedLocation` models.
38. CLI values override configuration.
39. Configuration overrides built-in defaults.
40. Unknown unrelated config keys are handled according to documented forward-compatible policy.
41. Invalid saved-location latitude is rejected.
42. Invalid saved-location longitude is rejected.
43. Invalid saved-location radius is rejected.
44. Explicit CLI location wins.
45. Explicit location does not require prompt.
46. Saved GPS match is used in non-interactive mode.
47. Unmatched GPS becomes `unknown` in non-interactive mode.
48. Non-interactive mode never waits on stdin.
49. Interactive mode can accept a matched saved location.
50. Interactive mode can reject matched saved location.
51. Interactive mode can enter a manual location.
52. Blank/manual fallback can resolve to `unknown`.
53. CLI does not duplicate archive-component normalization.
54. Reverse geocoding is not introduced.
55. No network service is required.
56. Dry-run performs discovery.
57. Dry-run performs reconstruction.
58. Dry-run performs location resolution.
59. Dry-run performs planning.
60. Dry-run uses the same authoritative planning semantics as real execution.
61. Dry-run does not create archive root.
62. Dry-run does not create archive directories.
63. Dry-run does not copy FITS.
64. Dry-run does not move FITS.
65. Dry-run does not delete FITS.
66. Dry-run does not overwrite files.
67. Dry-run does not generate TIFF.
68. Dry-run does not create temp/staging files.
69. Dry-run does not generate INDEX.md.
70. Dry-run does not modify configuration.
71. Dry-run does not save locations.
72. Dry-run leaves source content unchanged.
73. Dry-run output identifies planned observations.
74. Dry-run output identifies target.
75. Dry-run output identifies location.
76. Dry-run output identifies session date.
77. Dry-run output identifies observation number/destination.
78. Dry-run output identifies planned FITS/TIFF work sufficiently for user review.
79. Dry-run output shows planning problems.
80. Real run uses Stage 7.1f/7.1e execution semantics.
81. Real run does not unnecessarily duplicate discovery/reconstruction/planning.
82. Real COPY archive works.
83. Real MOVE archive works.
84. MOVE + TIFF remains functional.
85. Real-run output summarizes copied files.
86. Real-run output summarizes moved files.
87. Real-run output summarizes skipped identical files.
88. Real-run output summarizes original failures/collisions.
89. Real-run output summarizes TIFF creation.
90. Real-run output summarizes TIFF collisions/failures.
91. Complete archive maps to exit 0.
92. Partial archive maps to exit 1.
93. Failed archive maps to exit 1.
94. Expected planning failure maps to exit 1.
95. Expected config operational failure maps to exit 1.
96. Usage errors continue to map to exit 2.
97. Empty COMPLETE/no-op behavior has deterministic exit mapping.
98. Expected errors are reported concisely.
99. Broad programming errors are not silently swallowed.
100. JPEGs remain untouched.
101. No JPEG-delete CLI switch is added.
102. INDEX.md is not generated.
103. Compression is not implemented.
104. Compression CLI options are not added.
105. DSLR ingestion is not added.
106. Stage 7.1f semantics remain unchanged or are minimally refactored without behavior change.
107. Stage 7.1e safety semantics remain unchanged.
108. Stage 7.1d planning semantics remain unchanged.
109. Stage 7.1c reconstruction semantics remain unchanged.
110. Stage 7.1b discovery semantics remain unchanged.
111. Focused CLI test verifies command registration/help.
112. Focused tests verify configuration precedence.
113. Focused tests verify saved-location loading.
114. Focused tests verify interactive location acceptance.
115. Focused tests verify interactive rejection/manual entry.
116. Focused tests verify non-interactive fallback.
117. Focused tests prove dry-run zero mutation.
118. Focused tests verify real COPY CLI workflow.
119. Focused tests verify real MOVE CLI workflow.
120. Focused tests verify archive exit-code mapping.
121. Stage 7.1f tests pass.
122. Stage 7.1e tests pass.
123. Stage 7.1d tests pass.
124. Stage 7.1c tests pass.
125. Stage 7.1b tests pass.
126. Stage 5/6 conversion tests pass.
127. Stage 5/6 CLI tests pass.
128. Full test suite passes.
129. Ruff lint passes.
130. Formatting validation passes.
131. `git diff --check` passes.
132. Stage 6 `convert` remains unchanged.
133. Stage 6 `convert-batch` remains flat/non-recursive.
134. No reverse-geocoder/network code is added.
135. No INDEX.md implementation is added.
136. Stage 7.1h is not started.
137. Broad real-dataset qualification remains Stage 8.
138. Packaging/release remains Stage 9.
139. Documentation accurately records Stage 7.1g without premature closure.
140. Pending CHANGELOG entry for Stage 7.1f is preserved.
141. Codex makes no Git commit.

---

## 45. Codex completion report

Return a concise completion report containing:

1. files changed;
2. final archive CLI syntax/options;
3. configuration path/schema and precedence;
4. location-resolution/interaction behavior;
5. dry-run implementation and proof of zero mutation;
6. real-run pipeline and reuse/refactoring details;
7. output/exit-code behavior;
8. tests added and what they prove;
9. validation commands and exact results;
10. explicit confirmation of closure criteria 1–141, or identification of any unsatisfied criterion;
11. assumptions/open points;
12. current `git status --short`;
13. confirmation no Git commit was made;
14. confirmation Stage 7.1h was not started.

Do not commit.

The Stage chat will audit the completion report against all closure criteria before Stage 7.1g may be marked COMPLETE or committed.
