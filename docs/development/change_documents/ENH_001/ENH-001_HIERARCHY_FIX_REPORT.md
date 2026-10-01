# ENH-001c — Hierarchy Validation Fix report

Status: **CONFIRMED AND FIXED** (2026-10-01). ENH-001c and ENH-001 remain
STARTED. Implementation commit: **PENDING user review and user-controlled
commit**. Proposed message:
`ENH-001c: handle malformed hierarchy braces and preserve configuration repair`.

## Baseline and scope

- Branch: `enh/ENH-001-config-management`.
- Initial HEAD: `9899524` — `docs: record ENH-001b completion`.
- Expected pre-existing changes were preserved: the approved User Guide and
  Quick Start were modified, and the standalone documentation source was
  untracked. No other initial working-tree changes were present.
- One agent performed this narrowly scoped fix. No Git mutations, personal
  configuration access, PDF/checksum work, dependency, packaging, release,
  location-management, archive-matching or observing-night changes were made.

## Reproduction

Synthetic TOML files under `/private/tmp` used each of these saved values:

```toml
hierarchy = "{target/{location}/{session_end_date}"
hierarchy = "{target}}/{location}/{session_end_date}"
```

Before the fix, both `config show` and `config show --saved` returned status 1
by propagating an uncaught `ValueError` with a traceback from
`string.Formatter().parse()`. A targeted `config set archive.hierarchy` repair
also produced the traceback instead of reaching normal configuration error and
repair handling. The opening-brace case reported `expected '}' before end of
string`; the closing-brace case reported `Single '}' encountered in format
string`.

## Fix and regression coverage

`planning._template_tokens()` now catches `ValueError` only around the
`Formatter.parse()` call and translates it to the established
`ArchivePlanningConfigurationError` with a malformed-braces diagnostic. The
existing configuration layer consequently translates and reports it through
`ArchiveConfigError`. No invalid value is accepted, and all subsequent token,
component and completeness validation is unchanged.

Focused CLI tests cover both unmatched opening and closing braces and prove:

- ordinary and saved-only inspection return handled status 1 diagnostics with
  no traceback;
- a valid complete hierarchy can replace the malformed saved value;
- unsetting the malformed value restores the built-in default;
- attempting to save either malformed value leaves file bytes and modification
  time unchanged;
- a valid explicit archive hierarchy continues to bypass malformed or other
  invalid saved hierarchy values;
- existing valid hierarchy and configuration behaviour remains covered by the
  affected planning and configuration suites.

## Changed files

- `src/seestar_toolkit/archive/planning.py` — translate malformed-format braces
  into the existing planning configuration exception.
- `tests/unit/archive/test_config_commands.py` — add focused inspection, repair,
  rejection, file-preservation and explicit-override regression cases.
- `docs/development/CHANGELOG.md` — add the pending ENH-001c record.
- This report.

## Validation evidence

Environment: existing `/private/tmp/enh001-venv`, Python 3.13, checkout source
via `PYTHONPATH=src`; synthetic temporary configuration files only.

- Tests-first focused run: **6 failed, 1 passed, 12 deselected**, with each new
  unmatched-brace path failing at the uncaught `ValueError` as expected.
- Post-fix affected tests:
  `tests/unit/archive/test_config_commands.py`, `test_config_document.py` and
  `test_planning.py`: **94 passed in 0.60s**.
- Full suite:
  `PYTHONPATH=src /private/tmp/enh001-venv/bin/python -m pytest -q --tb=short`:
  **553 passed, 2 warnings in 19.34s**. Both warnings come from the existing
  deliberately duplicated ZIP-member release-validator fixtures.
- `/private/tmp/enh001-venv/bin/python -m ruff check .`: **PASS**.
- `/private/tmp/enh001-venv/bin/python tools/check_formatting.py`: **PASS**,
  46 files already formatted.
- `git diff --check` and an explicit no-index whitespace check of this new
  report: **PASS**, no diagnostics.

No distribution build or isolated installation was repeated because this fix
changes no dependency, packaging or installed-entry-point behaviour.

## Remaining status

No remaining hierarchy-brace issue is known after the required checks. This
report completes only the verified fix work; ENH-001c and ENH-001 remain STARTED
pending user review, user-controlled commit, and separately controlled remaining
documentation/closure work.
