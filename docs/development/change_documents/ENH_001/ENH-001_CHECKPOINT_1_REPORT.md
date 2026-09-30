# ENH-001 — START / Checkpoint 1 report

ENH-001: STARTED, unreleased. Checkpoint 1 validation: PASS; ready for user review.
Implementation commit: PENDING user review/user-controlled commit.

## Baseline and scope

Branch `enh/ENH-001-config-management`; HEAD/base
`78488712aef7650258bddb3f31ea2dda2fa0e28d` (`docs: update development commit record`).
Main pointed to the same base. A source/pyproject comparison with audited
`3c75002` showed no intervening configuration-code drift. The supplied
`ENH-001_SPECIFICATION.md` was the only pre-existing untracked addition. It was
read completely and not edited. AGENTS.md and DEV_README.md were consulted.
No branch, staging, commit, stash or remote Git mutations were performed.

## Implemented contracts

- Readable TOML documents are separate from resolved runtime settings. TOMLKit
  retains comments, unknown entries and unaffected locations. Inspection returns
  structured values/provenance/errors/warnings independently of CLI output.
- CLI show/saved/defaults and scalar set/unset manage exactly the three agreed
  archive preferences. Ordinary show has one value per scalar; equal-valued saved
  entries are still saved. Raw invalid entries remain visible without fake defaults.
- Full proposed validation permits targeted repair of a known scalar but rejects
  saves with other existing-schema failures. Existing overlapping/duplicate/zero
  location records are warned about and do not block scalar changes.
- Existing hierarchy override compatibility, archive matching, conversion,
  interactive reconciliation and temporary archive-prompt answers are retained.
- Successful first default set may create the default file. Explicit paths must
  exist. Missing-file inspections/unsets, absent keys and equivalent stored-policy
  sets are no-ops. Existing policy case acceptance remains, without trimming.
- Symlink target replacement preserves links and permission mode; new files are
  0600. Content/stat/link checks detect accidental changes since reading and just
  before replacement. Temporary files are cleaned on preparation/replace failures.
  No distributed locking or guarantee against the final check/replace race is claimed.
- `tomlkit>=0.15.1` is justified as a small document round-trip dependency; no
  custom text rewriter is introduced. Tested 0.15.1 metadata requires Python >=3.9
  and lists 3.11–3.14. Only local Python 3.13 is exercised here; other runtime
  versions/platforms are not claimed tested.

## Acceptance mapping

| Requirements | Checkpoint 1 evidence/status |
|---|---|
| C01 | Scoped show/set/unset/help and argument errors covered; location grammar deferred. |
| C02–C07 | Effective/raw/default views, provenance, absent/explicit files, scalar validation, hierarchy override, unsupported keys and CLI independence covered. |
| C08–C12 | Location creation/update/rename/prompt workflows deferred to Checkpoint 2. |
| C13 | Scalar unset/no-op covered; location removal deferred. |
| C14–C15 | Existing-schema validation retained; new-location strict rules and geographic edge cases deferred. |
| C16 | Existing archive nearest/inclusive/zero-radius tests retained; inspection warnings for legacy names/zero radius/overlap covered. |
| C17 | Unrelated legacy conflicts and targeted scalar repair covered; location edits/removals deferred. |
| C18–C19 | Header-only extraction and all-match inspection deferred to Checkpoint 2. |
| C20–C23 | Invalid raw inspection, repair, comment retention, no-ops, modes/symlinks, change detection, failure cleanup and private creation covered. |
| C24 | Shared API has no argparse/input/print dependency; CLI owns output. Archive/conversion regressions retained. |
| C25 | Targeted tests and full required checks recorded below; install validation exercises TOMLKit. |
| C26 | Implemented-command help and development records updated; final guides/PDF/checksums deferred to Checkpoint 3. |
| C27 | No personal config/datasets, version change, release action, date-policy change, GUI or ENH-002 implementation. |

## Changed files

Production: `archive/config.py` (shared link-safe selection, read diagnostics),
new `archive/config_document.py` (read/inspect/prepare/persist), `cli.py`
(scoped verbs/presentation), and `pyproject.toml` (runtime TOMLKit).
New tests: `tests/unit/archive/test_config_document.py` and
`tests/unit/archive/test_config_commands.py`. Existing tests were not weakened.
`tools/validate_distribution.py` now checks TOMLKit availability and a real
comment-preserving preference edit in wheel and sdist runtime-only installs.
Development documentation: ARCHITECTURE.md, PROJECT_Notes.md, DEV_README.md,
CHANGELOG.md (pending record only) and this report. The specification remains the
user-supplied untracked addition. User guides/PDFs/checksums remain unchanged.

## Validation evidence

Disposable validation environment: Python 3.13, current source via PYTHONPATH=src.
Initial environment setup needed the project's dependencies and an editable
installation to provide package version metadata; early collection errors were
resolved through normal installation, not changes to application version handling.
Initial lint formatting findings were corrected only in touched files.

- First targeted configuration/planning/CLI/archive run: 166 passed.
- Expanded persistence/CLI and distribution-validator unit run: 52 passed.
- Final focused new configuration contracts after write refinements: 45 passed.
- Full suite: `PYTHONPATH=src /private/tmp/enh001-venv/bin/python -m pytest -q --tb=short`:
  **474 passed, 2 warnings in 18.07s**. Both warnings are expected duplicate ZIP
  members deliberately generated by release-validator tests.
- `/private/tmp/enh001-venv/bin/python -m ruff check .`: PASS.
- `/private/tmp/enh001-venv/bin/python tools/check_formatting.py`: PASS,
  43 files already formatted.
- `git diff --check`: PASS.
- `/private/tmp/enh001-venv/bin/python tools/check_public_inputs.py`: PASS,
  10 reviewed fixtures, clean repository root and no oversized history blobs.
- `/private/tmp/enh001-venv/bin/python tools/validate_distribution.py`: PASS.
  Isolated wheel (40 allowed members) and sdist (47 allowed members) runtime-only
  installations passed dependency, metadata, entry-point, conversion and TOMLKit
  comment-preserving edit checks. Initial sandbox build dependency installation
  failed; the approved-network rerun completed successfully. Log:
  `/private/tmp/enh001-distribution.log`.
- Final diff audit: only Checkpoint 1 production, tests, install validation and
  development records changed. No existing tests changed, no staged files, and
  no Git mutations. The supplied specification is retained unchanged.

## Remaining work and limitations

Checkpoint 2: all location mutation, interactive authorisation, strict location
validation, clamped geographic edge cases and header-only GPS/all-match features.
Checkpoint 3: user guides, version/artifact metadata decisions, PDF/checksum
regeneration and formal closure. No publication/version was chosen here.
Legacy archive behaviour remains unchanged; config inspection warns instead of
inventing location ownership. Persistence preserves POSIX permission bits, not a
new cross-platform ACL/ownership management contract. No comprehensive locking.
