# ENH-001 — Configuration Management and Persistence

**Specification date:** 2026-09-30
**Status:** Design agreed; formal specification prepared for review; implementation not started
**Proposed branch:** `enh/ENH-001-config-management`
**Git ownership:** User controls branch creation, commits, pushes, merges and branch deletion.

## 1. Purpose and baseline

Provide a small, explicit interface for inspecting and managing saved preferences and observing locations. Preserve ordinary archive behaviour and the precedence `CLI override > saved configuration > built-in default`. Configuration operations must be reusable by a later GUI without depending on CLI parsing, terminal output or prompts.

The read-only audit supplied on 2026-09-30 inspected `main` at `3c750025f19a9e1165cc8b65841854a4cd96f10f` — `docs: record Stage 9 closure and BUG-002 completion`. The only uncommitted change was `docs/development/CHANGELOG.md`, recording that documentation commit. It was not treated as committed source. The audit did not execute tests or application commands.

Source-verified foundations:

- Default configuration: `~/.config/seestar-toolkit/config.toml`; no XDG override.
- Only `archive` currently loads configuration. Help/version and conversion commands are independent.
- Existing TOML uses `[archive]` and repeated `[[locations]]` entries.
- `archive.hierarchy` defaults to `{target}/{location}/{session_end_date}`. Exactly those three tokens must occur once each as separate relative path components, in any order.
- `archive.source_action`: `copy` or `move`, default `copy`.
- `archive.collision_policy`: `skip-identical`, `error` or `overwrite`, default `skip-identical`.
- Existing saved policy values are case-insensitive, without whitespace trimming. CLI choices are lowercase.
- Saved locations have `name`, `latitude`, `longitude` and `radius_m`. Existing files require all fields; zero radius, duplicates and overlapping areas are currently accepted.
- Archive matching selects the nearest containing location; its boundary is inclusive with `1e-9` metre tolerance. Ties use case-folded name, then original name.
- Distance uses Haversine with Earth radius `6,371,008.8` metres.
- FITS site coordinates use `SITELAT` and `SITELONG`; `RA` and `DEC` describe celestial targets.
- Current FITS inspection loads image data and does not establish conflicts across headers or duplicate cards.
- Unknown configuration keys are ignored at runtime. The runtime model does not retain comments, unknown entries or saved/default provenance.
- The fixed observing-night rule remains `date(capture_datetime + 12 hours)`.

The implementation must recheck its actual branch base and report any material drift before editing code. Documentation-only baseline changes need not reopen agreed product decisions.

## 2. Scope

### Included

1. `config show`, `config set` and `config unset`.
2. Provenance for effective saved/default settings.
3. Management of the three existing archive preferences.
4. Saved locations: manual creation, partial edits, FITS extraction, rename and removal.
5. GPS inspection with all saved matches and distances.
6. Explicit interactive and unattended update behaviour.
7. Validation and targeted repair, with legacy-location compatibility.
8. Comment-preserving TOML edits, safe writes, symbolic-link handling and permission preservation.
9. Meaningful automated tests, CLI help, user documentation, development records and applicable PDF/checksum updates.

### Excluded

ENH-002 and new date-policy settings; changed archive hierarchy behaviour or archive reorganisation; target/telescope corrections; automatic persistence of archive-prompt answers; new camera support; GUI implementation; plugin frameworks; configuration profiles; reset-all; `--save-config`; saving invocation-specific paths/options; release publication, tagging or an unagreed package-version change.

## 3. CLI grammar

The forms below are specification examples, not commands already available in v1.1.0. `--config PATH` is accepted after the new `show`, `set` or `unset` verb. Existing `archive --config PATH` syntax is unchanged.

```text
seestar-toolkit config show [--config PATH]
seestar-toolkit config show --saved [--config PATH]
seestar-toolkit config show --defaults
seestar-toolkit config show --extract FILE [--config PATH]

seestar-toolkit config set archive.SETTING VALUE [--config PATH]
seestar-toolkit config unset archive.SETTING [--config PATH]

seestar-toolkit config set --location NAME --latitude VALUE --longitude VALUE [--radius-m VALUE] [--config PATH]
seestar-toolkit config set --location NAME --extract FILE [--radius-m VALUE] [--config PATH]
seestar-toolkit config set --location NAME --latitude VALUE [--longitude VALUE] [--radius-m VALUE] [--update] [--config PATH]
seestar-toolkit config set --location NAME --longitude VALUE [--radius-m VALUE] [--update] [--config PATH]
seestar-toolkit config set --location NAME --radius-m VALUE [--update] [--config PATH]
seestar-toolkit config set --location NAME --rename NEW_NAME [other location changes] [--update] [--config PATH]
seestar-toolkit config unset --location NAME [--config PATH]
```

`--update` also applies to FITS-derived updates and combined location edits. It is a location-only option and requires the original named location to exist. At least one change field is required for a location `set`; `--location NAME` alone is an argument error. Scalar and location forms cannot be mixed.

`--extract FILE` and manual latitude/longitude are mutually exclusive. Rename, radius and one permitted coordinate source may be combined. New locations require both coordinates; partial manual coordinates are allowed only when editing an existing entry. A rename always requires an existing entry. No additional `config location` subcommands or old top-level `config --extract` shorthand are required.

`--defaults`, `--saved` and `--extract` are mutually exclusive inspection modes. `--defaults --config PATH` is an argument error. Reject irrelevant flags rather than silently ignoring them.

## 4. Inspection

### Ordinary `config show`

Show one effective value for each supported archive setting, labelled `saved` or `default`. A saved value suppresses the corresponding built-in value in this display, even if the values happen to be equal. Include saved locations and the selected configuration path and existence status. This represents a run without invocation-specific CLI overrides; it does not predict the choices in an arbitrary archive command.

If the default file does not exist, show defaults and no saved locations without creating a directory or file. With invalid known values, show actionable diagnostics and mark affected values as invalid; do not present fallback values as successfully resolved. Unknown entries are not effective managed preferences.

### `--saved`

Show saved entries, including locations and unfamiliar entries, without inventing absent defaults. Readable invalid entries must remain inspectable with diagnostics. Comment display is optional; comment preservation during writing is mandatory.

### `--defaults`

Show built-in defaults without opening saved configuration. It must work when the default file is damaged or inaccessible. There are no default observing sites. The 100 m radius is a new-location creation default, not a missing-field fallback for existing TOML entries.

### `--extract FILE`

Read GPS without writing configuration. Show the input file, site coordinates, selected configuration path and all saved locations containing the point. For each match, show saved name, coordinates, radius and distance in metres. Clearly distinguish no match, no saved locations and multiple matches. Report detected legacy-location conflicts. Never imply that matching succeeded if configuration could not be read or validated under existing validity rules.

Use the same distance definition and point-in-radius boundary as archive matching. Reporting all matches must not change archive's nearest-match selection or tie-breaking behaviour.

## 5. Preference edits

Only `archive.hierarchy`, `archive.source_action` and `archive.collision_policy` are managed scalar preferences in this enhancement.

`set` validates the supplied value and proposed file before saving. It explicitly replaces an existing scalar value without a confirmation prompt, and reports the previous and new state. Saved policy parsing retains existing accepted case behaviour; newly written recognised enum values may be normalised to lowercase. Do not silently trim policy values that existing parsing rejects. Use existing hierarchy validation before saving rather than accepting an arbitrary string.

`unset` removes the requested saved key so the default applies. An absent key is a reported no-op; do not create a file, rewrite formatting, or update modification time. Remove only the requested value; retain unrelated entries and user comments wherever possible. A `set` that has no effective stored change should likewise avoid rewriting and report that no change was needed.

Source/destination paths, dry-run, prompting options, explicit archive-location overrides and the configuration-file selector are invocation-specific and cannot be saved as scalar preferences. Archive-prompt responses remain temporary. Only explicit configuration commands persist preferences.

## 6. Location changes

### Creation and partial updates

New locations require a name and both valid coordinates. If omitted, `radius_m` is written as `100.0`. Existing locations retain all unspecified fields, including radius. Manual latitude-only or longitude-only updates are valid for an existing entry. FITS extraction replaces both coordinates. Display proposed changes before asking about replacement.

For an existing entry, ask `Update config / Skip` in an interactive terminal unless `--update` was supplied. Skip makes no changes and is successful user cancellation. Without a terminal and without `--update`, report that explicit update authorisation is required and stop without writing. `--update` is not permission to overwrite a conflicting different location or bypass validation.

Creation needs no separate confirmation: the `set` command explicitly requests saving. The interactive replacement question is specific to location edits, including rename and combined edits. Use one question and one save for a combined edit; failures must not leave a partially applied rename or coordinate change.

### Names

Trim leading/trailing spaces on newly saved or explicitly renamed names, retaining internal spaces and chosen capitalisation. Compare requested names using Unicode case-folding and trimmed outer whitespace. Preserve untouched legacy spellings in the file. A lookup must not silently select among multiple matching legacy entries: report ambiguity and explain that the file needs manual disambiguation.

Validate names using existing archive-location safety/sanitisation rules. Reject blank names, duplicate logical names and new/renamed names that collide after existing directory-name cleaning. Compare cleaned directory names conservatively without regard to case on the supported macOS platform. Do not redesign sanitisation. A case-only rename is allowed for the same unique entry. Any other existing entry occupying the destination identity is a conflict, not a replacement candidate.

Rename updates saved configuration only. Existing directories and indexes are not renamed or reconstructed.

### Values and overlap

Require finite numeric coordinates/radii; reject booleans. Latitude is within `[-90, 90]`, longitude within `[-180, 180]`, and a newly created/edited radius is strictly positive. Decimal metres are allowed.

Reject a new or edited location if its circle touches or overlaps any other saved circle. Exclude only the entry being edited from its own comparison. With valid inputs, reject when `distance <= radius_a + radius_b + 1e-9 metres`. Keep matching and overlap distance calculations consistent. Clamp the Haversine intermediate to its mathematical range to avoid floating-point failures near antipodal points, without changing established valid matching behaviour.

Report both conflicting names and enough distance/radius information to explain the rejection. Never offer a prompt to override overlap validation. Any renamed/edited location must itself satisfy the new rules, including overlap rules.

### Removal

`unset --location NAME` removes the complete uniquely identified entry with no additional confirmation. An absent name is a reported no-op. Ambiguous legacy names are an error rather than a reason to remove several entries. Preserve all other locations and unfamiliar fields belonging to other entries.

## 7. FITS GPS extraction

Implement header-only extraction so locating a site does not decode/copy image arrays or require an image type supported by TIFF conversion. Inspect headers across the FITS HDUs and duplicate occurrences of the site cards. Do not scan datasets or multiple input files.

Supported GPS source is numeric degree values from `SITELAT` and `SITELONG`. No sexagesimal conversion, geocoding or alternative-header guessing is required. Never use `RA` or `DEC` for site coordinates.

Each header containing either site card must contain a complete usable pair. Headers with neither card provide no evidence and are ignored. Do not combine a latitude from one header with a longitude from another. Require finite, in-range numbers and reject unreadable, malformed or incomplete site evidence.

Identical repeated values, after numeric interpretation, are accepted. Different values in duplicate cards or different complete pairs across headers are a conflict. Reject rather than choose a header or average readings. Exact numeric equality after interpretation is sufficient; inventing a GPS error-tolerance policy is outside this enhancement. A file with no complete site evidence produces a clear missing-GPS error. Show which headers/cards caused a conflict without exposing unrelated metadata.

These strict checks belong to configuration extraction; do not silently change existing FITS inspection or multi-file archive GPS reconciliation behaviour.

## 8. Compatibility and invalid-file recovery

### Read behaviour

Retain existing archive behaviour for legacy zero-radius, duplicate-name and overlapping locations. Report these conflicts in configuration inspection, but do not newly block ordinary archive use solely for those conditions. No incomplete legacy location receives an automatic radius default.

Malformed TOML, unreadable files, invalid existing required types/values and missing explicitly selected files remain errors. Operations using configuration stop rather than automatically fall back. Help/version and conversion commands stay independent. `show` may display readable invalid raw entries with a failing status to support repair; it must not claim those entries resolve successfully.

Preserve hierarchy precedence: archive validates the effective hierarchy after CLI overrides. A valid explicit hierarchy may continue to bypass an invalid saved hierarchy string. Invalid saved policies/types that currently fail loading still fail; ENH-001 does not generalise override-based bypasses.

### Edits and repair

Keep raw readable TOML separate from the resolved runtime model, so invalid values can be inspected and corrected without losing comments or unknown entries. Broken TOML cannot be safely edited by these commands and requires manual correction.

Validate the complete proposed document under existing structural/type rules and hierarchy rules. Allow pre-existing location violations of the new rules to remain untouched: they must not block archive-preference edits. Validate each new or edited location strictly. Allow removal even when unrelated legacy location conflicts remain. Report remaining conflicts.

Do not save a new invalid hierarchy or a new invalid existing-schema value. A targeted edit may correct an existing invalid value, but if another existing-schema failure prevents complete validation, explain the remaining problem and leave the file untouched. Manual repair remains available; a batch repair language is outside scope.

## 9. Persistence

Default path selection is unchanged. An explicitly selected `--config PATH` must exist; do not create a new file at a typoed explicit path. Successful `set` may create the absent default directory and file. Inspection, no-ops and `unset` never create either.

Follow symbolic links to their actual target for reads and writes, display the actual destination when it differs, and replace the target rather than the link. Preserve the link itself and existing target permissions. Broken links and link loops are errors, not absent-default cases. Validate permission and destination failures with clear messages.

Use a comment-preserving TOML document representation; serialising only `ArchiveConfig` is insufficient. Preserve unrelated known and unknown entries, table ordering where supported, comments and unaffected locations. Deleting a requested location necessarily deletes its own fields; do not erase unrelated comments or sections as collateral. Do not promise byte-identical whitespace around edited values.

A dependency providing TOML round-tripping may be introduced if justified; verify it supports the project's Python 3.11–3.14 range and include it in normal package metadata and installation validation. Do not build a fragile custom TOML rewriter or a plugin framework merely to avoid a small dependency.

Validate the complete proposed result before committing a write. Prepare a temporary file beside the resolved destination and atomically replace that destination only after successful serialisation and preparation. Preserve existing access permissions; newly created personal configuration should use owner-only file access. Clean temporary files on errors.

Use a lightweight change-since-read check, including target resolution when a link is involved. If the observed file or link target changed during a prompt/edit, stop and ask for retry. This is accidental-edit protection, not a distributed locking system or a guarantee against every possible concurrent race. Report success only after replacement completes. Failures before replacement leave the original intact.

## 10. Architecture and error conventions

Separate configuration document reading, validation, provenance, matching and update preparation from CLI presentation and prompt decisions. The future GUI should be able to use the same operations without pretending to be a terminal. Reuse existing models and validation/distance logic where suitable; do not make unrelated archive restructuring part of this change.

Follow the repository's established success/error exit conventions. Ordinary success, explicit skip and absent-entry no-ops return success. Invalid arguments, invalid file content, GPS conflicts, ambiguous names, disallowed unattended updates and failed writes return the applicable existing nonzero category. Specify actual numeric codes in CLI help/tests based on established repository conventions rather than introducing incompatible new codes.

An inspection that successfully reads legacy locations may report compatibility warnings without failing solely for new-rule violations. Existing-schema errors are not warnings implying safe effective operation. Retain human-readable output; JSON output is not required for GUI reuse.

## 11. Acceptance requirements and validation

Each requirement below must have implementation or test evidence. Prefer meaningful unit/integration checks for behavioural contracts and failure handling rather than tests that mirror private implementation details.

| ID | Required evidence |
|---|---|
| C01 | New verbs/help work; existing CLI commands remain compatible. Invalid or mixed option combinations are rejected. |
| C02 | `show` resolves one value per setting, distinguishes saved/default including equal-valued saved entries, and includes locations/path status. |
| C03 | `--saved` exposes saved/unknown entries; `--defaults` does not read a damaged default file; inspection combinations follow grammar. |
| C04 | Absent default uses defaults and inspection creates nothing. Explicit missing config errors. First valid default `set` creates the file. |
| C05 | All three scalar settings validate and persist; `unset` restores the applicable default; CLI precedence remains unchanged. |
| C06 | Invalid hierarchy cannot be saved, but a valid CLI hierarchy still bypasses an invalid saved hierarchy on archive runs as before. |
| C07 | Unsupported/invocation-specific preferences cannot be persisted; archive prompts never write configuration. |
| C08 | Manual and FITS creation write both coordinates and default 100 m radius; explicit radius overrides it. Existing TOML missing radius remains invalid. |
| C09 | Existing manual partial updates and FITS updates retain unspecified fields/radius; validation uses the resulting entry. |
| C10 | Existing-name prompt shows complete proposed changes; Skip changes no bytes or modification time. Noninteractive replacement requires `--update`; a missing `--update` target errors. |
| C11 | Rename alone/combined edits preserve entry data, permit case-only changes, reject occupied names, and never rename archive outputs. |
| C12 | Trimmed/case-folded logical names and cleaned directory collisions are checked; ambiguous legacy lookup does not choose an arbitrary entry. |
| C13 | Location removals and absent-location/scalar no-ops work without extra prompts or unintended rewrites. |
| C14 | Coordinate boundaries, nonfinite values, booleans, nonpositive new radii and invalid names are rejected. |
| C15 | Touching/overlapping circles fail, genuinely separated circles pass, and the edited entry is excluded from self-comparison. Include geographic edge cases. |
| C16 | Zero-radius/overlap/duplicate legacy configurations retain existing archive matching, nearest/tie behaviour and inclusive boundary. Inspection reports conflicts. |
| C17 | Unrelated legacy location conflicts do not block scalar edits/removal; new/edited entries must pass strict checks; repair preserves other entries. |
| C18 | GPS extraction is header-only, reads numeric site cards, accepts identical repeats, rejects duplicate/across-HDU disagreements and incomplete/invalid evidence, and never substitutes RA/DEC. |
| C19 | GPS inspection reports all matching names, coordinates, radii/distances; no-match and multiple-match cases are clear and read-only. |
| C20 | Broken TOML stays untouched; readable invalid known values can be inspected/targeted for repair without resolving a fake default. |
| C21 | Comments, unknown sections/keys and unaffected locations survive successful edits; no-op changes preserve original bytes and timestamps. |
| C22 | Writes replace the resolved target atomically and preserve permissions/links; broken links, permissions, detected changed target/content and preparation failures leave originals untouched. |
| C23 | Temporary-file cleanup and post-success reporting are correct. New default configuration has suitably private file permissions. |
| C24 | Shared configuration operations do not depend on CLI parsing/prompts/output; archive matching and conversion semantics remain unchanged. |
| C25 | Required checks and applicable regression tests pass; dependency/package install checks include any new TOML dependency. |
| C26 | CLI help, guides and development records match final behaviour; PDFs/checksums and generation expectations are refreshed and validated for their stated document version. |
| C27 | Diff contains no personal configuration, GPS datasets, unrelated cleanup, new date-policy behaviour, version/tag/publication changes or out-of-scope enhancements. |

### Test and check scope

Use synthetic temporary configuration and FITS fixtures; do not need personal capture files to prove persistence and header interpretation. Reuse the reviewed configuration, planning, inspector, CLI and orchestration tests, preserving explicit legacy matching expectations.

During implementation run targeted tests appropriate to each change. At closure run the project's required full pytest, Ruff, formatting and whitespace checks, plus applicable packaging/install and documentation/PDF validation. Use repository-mandated commands and environments; do not invent test totals or claim platform validation that was not performed. Repeat full checks only for relevant new changes, failures or remaining uncertainty.

The audited candidate test files are `tests/unit/archive/test_config.py`, `tests/unit/archive/test_planning.py`, `tests/unit/fits/test_inspector.py`, `tests/unit/test_cli.py` and `tests/integration/test_archive_orchestration.py`. New persistence/CLI tests may be placed alongside them according to repository conventions.

## 12. Documentation and release boundary

Update `docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md`, `docs/user/SEESTAR_TOOLKIT_QUICK_START.md`, new command help, `docs/development/ARCHITECTURE.md`, `docs/development/PROJECT_Notes.md` and applicable changelog/change records. Historical Stage records remain historical.

The existing PDF workflow uses `tools/generate_documentation_pdfs.py`, `tools/validate_documentation_pdfs.py`, `documentation_pdf_header.tex` and `documentation_pdf_filter.lua`, with frozen source hashes/title/version/date and reproducibility checks. Refresh those expectations intentionally with guide changes, regenerate applicable PDFs and paired checksums, and run the required validation.

Do not claim that the published v1.1.0 already contains these new commands. Development documentation must identify ENH-001 as unreleased until its release metadata is agreed. An actual next-release number and publication are separate user-controlled decisions. If frozen PDF metadata requires that decision before final artifacts can validate, report the precise requirement and settle it before closure; do not choose a release version or weaken the validators silently.

## 13. Git and start procedure — user controlled

No repository files or Git state were changed while preparing this document. The specification is a deliverable for review, not proof that its repository placement or implementation has occurred.

Before branch creation, the user reviews `git status` and the known pending development changelog edit. Preserve it; do not discard it or silently carry unrelated work into the enhancement. If it is still the expected commit-record update, the user can commit it separately using the established documentation workflow. Record the resulting clean HEAD as the actual implementation base.

User commands for initial inspection:

```bash
git status
git diff -- docs/development/CHANGELOG.md
git log -3 --oneline --decorate
```

Once reviewed, committed/synchronised as appropriate, and the tree is clean, the user creates the branch:

```bash
git switch main
git pull --ff-only
git switch -c enh/ENH-001-config-management
git status
```

If any command reports conflicts, unexpected changes or a diverged branch, stop and resolve that specific condition; do not reset, force-push or automatically stash.

Place this reviewed specification and its report/checklist under the existing development change-document conventions on the enhancement branch. Confirm the exact ENH directory naming against repository instructions; do not invent a migration of historical Stage directories.

Codex may inspect status/diffs and implement/test the authorised specification. It must not switch branches, commit, push, merge, delete branches or modify unrelated pre-existing edits unless separately instructed. User commits follow reviewed checkpoints, with summaries and proposed commit messages supplied by Codex. Record identifiers through the established changelog workflow.

Keep the branch short-lived. Merge into `main` only after acceptance evidence and closure validation pass, the user reviews the final diff, and required repository checks are successful. Do not release/tag merely because the enhancement is merged. The user controls push/merge strategy and branch deletion; avoid an automatic history rewrite.

## 14. Work checkpoints and closure

Use prominent `ENH-001 — START`/`COMPLETE` reports at actual implementation start and successful formal closure. The planning start announcement does not mean production implementation has begun. Keep ENH identifiers rather than restarting Stage numbering.

Recommended implementation checkpoints, each with concise evidence and user-controlled Git actions:

1. **Foundation and preferences:** document-aware loading, provenance, validation compatibility, scalar inspection and persistence.
2. **Locations:** extraction, all-match reporting, creation/update/rename/removal, strict-edit rules and legacy compatibility.
3. **Documentation and closure:** guide/PDF/checksum updates, dependency/install validation, full required checks and final acceptance evidence.

Checkpoint boundaries can share reusable infrastructure; they are review units, not reasons to build frameworks or create extra branches. Do not declare a checkpoint passed before its applicable tests/checks succeed. Report blockers and incomplete requirements clearly.

Formal closure requires a report tied to the final reviewed commit(s), outcomes for C01–C27, actual test/check results and explicit documentation-artifact/version status. After user-controlled integration, verify clean `main`, expected remote synchronisation and applicable CI success. A separate documentation commit may record implementation and integration identifiers under the established workflow. Never claim pushed/merged/closed solely from local test success.

**Next gate:** Review this specification, preserve/resolve the pending changelog record, and create the branch under user control. A Codex implementation prompt follows that start checkpoint; it is not included in this document.
