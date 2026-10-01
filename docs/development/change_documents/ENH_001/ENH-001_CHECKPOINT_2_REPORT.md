# ENH-001b — START / Location Management report

ENH-001b is specification Checkpoint 2. Validation: PASS (2026-10-01); ready for user review.
ENH-001 remains STARTED and unreleased. Implementation commit: PENDING user review
and user-controlled commit. Proposed message:
`ENH-001b: manage saved locations and extract FITS GPS`.

## Baseline and scope

- Branch: `enh/ENH-001-config-management`.
- Clean initial HEAD: `53fe9fb` — `docs: record ENH-001a completion`.
- Local origin tracking reference matched HEAD; no fetch/network synchronisation
  claim is made. ENH-001a implementation foundation: `99c3272`.
- No unexpected changes or baseline drift. The authoritative specification and
  applicable AGENTS.md/development instructions were read. One agent performed
  this work. No Git mutations, personal configuration reads or personal datasets.
- Reused ENH-001a document reading, prepared edits and atomic persistence. No new
  dependency, packaging, version, release, date policy or archive layout change.

## Implemented behaviour

- `config show --extract FILE` reads site coordinates and displays all matching
  saved names, coordinates, radii and distances. No sites, no match and multiple
  matches are distinct. Existing-schema errors prevent successful match reporting;
  legacy conflicts produce warnings. Inspection never writes.
- `config set --location NAME` supports manual or FITS coordinates, decimal radius,
  partial existing updates, rename, combined changes and explicit `--update`.
  New entries require both coordinates and default radius to 100 m; existing
  unspecified fields and unknown entries remain. No radius fallback repairs an
  incomplete existing entry without an explicit supplied value.
- Existing edits show complete old/proposed entries and ask Update config / Skip
  once, defaulting to Skip. Noninteractive changes require `--update`, which
  requires an existing target and cannot bypass validation. Effective stored
  no-ops succeed without asking or rewriting. One combined edit uses one save.
- `config unset --location NAME` removes one unique entry without confirmation;
  an absent entry is a no-op. Trimmed Unicode case-folded ambiguity errors instead
  of selecting or deleting an arbitrary legacy entry.
- New/renamed names are trimmed; untouched legacy spellings remain. Logical and
  case-insensitive cleaned-directory conflicts fail. Existing archive component
  cleaning is reused. Blank names and the standalone names `.` and `..` are rejected;
  supported names containing characters cleaned by the archive remain usable.
- Edited locations have finite numeric coordinates within inclusive bounds and
  positive radii. Boolean values fail. Edited/new circles cannot touch or overlap
  another circle (`distance <= sum of radii + 1e-9`); self is excluded. Errors name
  both sites and show distance/radii. Case-only rename is allowed when unique.
- Unrelated legacy duplicates, overlaps and zero-radius entries are retained with
  warnings. Targeted invalid-field repairs and removals are supported only when
  the whole proposed document passes existing schema and hierarchy validation.
- Strict FITS extraction inspects all headers and duplicate site cards; headers
  with neither site card are ignored. Every participating header needs a complete
  valid pair. Exact numeric repeats are accepted; differing duplicates/pairs,
  incomplete evidence, malformed headers, booleans, nonfinite or out-of-range
  values fail with site-card/HDU diagnostics. RA/DEC are never used. Extraction
  does not access image/table data or depend on TIFF-supported image types.
- ENH-001a persistence retains permissions, symlinks, comments/unknown entries,
  change-since-read checks and temporary-file cleanup. Location table removal
  retains standalone comments even when relocation is needed; the entry's own
  fields/inline comments are removed. Inline location arrays remain supported.
- Only the required Haversine [0, 1] clamp changes shared archive calculation.
  Nearest selection, inclusive boundaries, case-folded/original name ties and
  legacy zero-radius/overlap/duplicate matching remain unchanged. Strict single
  FITS extraction is separate from archive inspection/multi-file reconciliation.

## Changed files

New production modules:

- `src/seestar_toolkit/archive/config_locations.py`
- `src/seestar_toolkit/fits/site_coordinates.py`

Modified production files:

- `src/seestar_toolkit/cli.py` — grammar, presentation and update authorisation.
- `src/seestar_toolkit/archive/planning.py` — one-line Haversine clamp.

New tests:

- `tests/unit/archive/test_config_locations.py`
- `tests/unit/archive/test_location_commands.py`
- `tests/unit/fits/test_site_coordinates.py`

Updated test: `tests/unit/archive/test_config_commands.py` removes the former
Checkpoint 1 expectation that `show --extract` is an unsupported argument; the
new extraction cases replace it. All other prior expectations remain intact.

Development records: `docs/development/ARCHITECTURE.md`, `DEV_README.md`,
`PROJECT_Notes.md`, `CHANGELOG.md`, and this report. Historical ENH-001a reports,
the specification, user guides, PDFs, checksums and release records are unchanged.

## Acceptance coverage

| Requirement | ENH-001b evidence/status |
|---|---|
| C01 | Location/extraction grammar and mixed/irrelevant argument failures tested; existing commands retained. |
| C02–C07 | ENH-001a scalar/default/provenance/precedence tests retained, including hierarchy override and conversion independence. |
| C08 | Manual/FITS creation, default/explicit radius, and missing-existing-radius repair tests. |
| C09 | Partial latitude/longitude and FITS updates retain other fields/radius; combined validation tested. |
| C10 | Old/proposed display, interactive update/Skip, unattended rejection/authorisation, missing target, no-op and prompt-time concurrent edit tested. |
| C11 | Rename and combined changes, case-only rename, occupied-name rejection, unknown-field preservation; no archive-output mutation path. |
| C12 | Unicode trimmed/case-folded lookup, cleaned collisions, ambiguous legacy edits/removal tested. |
| C13 | Unique removal and missing/no-op cases preserve bytes/timestamps; no extra prompt. |
| C14 | Boundaries, boolean/nonfinite/out-of-range coordinates, nonpositive radii, blank/dot names tested. |
| C15 | Touching/overlap rejection, separated circles, self-exclusion, poles/antimeridian/antipodal rounding tested. |
| C16 | Existing archive tests retained; all-match/nearest/tie/zero-radius and legacy conflict warnings tested. |
| C17 | Unrelated conflicts do not block valid edits/removal; selected invalid location repair and unrelated-schema-error rejection tested. |
| C18 | Array access forbidden in header-only tests; duplicate/across-HDU agreement/conflict, malformed extension, incomplete/missing evidence, table HDU and RA/DEC-only cases tested. |
| C19 | Every match with name/coordinates/radius/distance, no sites/no match/multiple matches and invalid config reporting tested read-only. |
| C20–C23 | ENH-001a persistence tests retained; location-specific comments/unknown entries, inline arrays, symlinks/modes, private creation, failed replace cleanup and success-message ordering covered. |
| C24 | Shared operations are UI-independent; CLI alone parses/prompts/prints. Existing archive inspector/reconciliation untouched. |
| C25 | Actual validation below; no dependency/packaging changes requiring repeat ENH-001a installation builds. |
| C26 | CLI help and development records updated; final guides/PDF/checksums deferred to ENH-001c as requested. |
| C27 | No personal data, Git mutations, version/release actions, observing-night/ENH-002 changes or archive reorganisation. |

## Validation evidence

Environment: existing `/private/tmp/enh001-venv`, Python 3.13, source checkout via
`PYTHONPATH=src`. Synthetic configuration/FITS fixtures only for new tests.
Other Python versions/platforms are not claimed tested.

- Initial tests-first collection failed for the two not-yet-created modules.
- Initial new shared tests: 40 passed; initial CLI/foundation tests: 31 passed.
- Focused new and affected configuration, CLI, FITS, planning and archive
  orchestration run: **262 passed in 3.71s**.
- Expanded new tests: **74 passed in 0.69s**, after correcting a test's call to an
  existing keyword-only function. Subsequent final refinements are covered by
  the full run below. Formatting findings were corrected in touched files only.
- Full suite: `PYTHONPATH=src /private/tmp/enh001-venv/bin/python -m pytest -q --tb=short`:
  **547 passed, 2 warnings in 17.95s**. Both warnings are the existing deliberately
  duplicated ZIP-member fixtures in release-validator tests.
- `/private/tmp/enh001-venv/bin/python -m ruff check .`: **PASS**.
- `/private/tmp/enh001-venv/bin/python tools/check_formatting.py`: **PASS**,
  46 files already formatted. Explicit `ruff format --check` on the new FITS
  production/test modules: **PASS**, 2 files already formatted.
- `git diff --check` plus `git diff --no-index --check -- /dev/null PATH` for
  each of the six new files: **PASS**, no whitespace diagnostics. The initial
  wrapper incorrectly treated no-index's ordinary difference exit status 1 as
  a failure; the corrected check accepts 0/1 only with no diagnostics.
- `/private/tmp/enh001-venv/bin/python tools/check_public_inputs.py`: **PASS**,
  10 reviewed fixtures, clean public root, no oversized history blobs.
- Wheel/sdist builds and dependency installations were intentionally not repeated:
  ENH-001a validated TOMLKit and runtime installation; no dependency or packaging
  change or demonstrated installation issue occurred in ENH-001b.

## Remaining work and limitations

ENH-001c: final user guides, PDF/checksum regeneration and frozen metadata/version
agreement, final acceptance evidence and formal closure. No release/version was
chosen here. Stop for user review and a user-controlled ENH-001b commit.

Persistence has ENH-001a's lightweight concurrent-change protection, not locking
or a guarantee against the final check/replace race. POSIX mode preservation is
retained without a new ownership/ACL management contract. Renaming configuration
never renames or rebuilds existing archive directories or indexes.
