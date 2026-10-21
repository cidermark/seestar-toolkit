# BUG-003 Report — S50 Pro Telescope Identity Recognition

**Status:** Implementation and validation complete; formal closure pending user review.

## Resolution

Archive reconstruction now recognises complete, case-insensitive `TELESCOP` values
in these forms:

- `S50_[0-9a-f]{8}`
- `S50 Pro_[0-9a-f]{8}`

The normalised complete string is the device identity. Therefore an S50 and an S50
Pro with the same hexadecimal suffix remain distinct physical devices. Existing
unknown, missing, malformed, and unsupported identifiers still normalise to no
identity and retain the established compatibility behaviour.

Changed files:

- `src/seestar_toolkit/archive/reconstruction.py`
- `tests/unit/archive/test_reconstruction.py`
- `docs/development/CHANGELOG.md`

## Automated validation

- Focused reconstruction and integration tests: **99 passed**.
- Full test suite: **626 passed**; two pre-existing intentional duplicate-ZIP test
  warnings were emitted.
- Ruff on changed implementation and test files: **passed**.
- `git diff --check`: **passed**.

The added regression coverage verifies S50 and S50 Pro recognition, case folding,
invalid-format rejection, and refusal to associate S50 and S50 Pro frames that use
the same hexadecimal suffix. Existing tests retain coverage for distinct devices,
unknown-identity compatibility, and overlapping streams.

## Twelve-file M27 validation

The original reconnaissance collection at
`/Users/mark/tmp/Astro_Tests/seestar_identity_recon_20261013` contains twelve FITS
files. Its archive-compatible combined source view contains the same twelve unique
FITS payloads and was used with `--source-action copy`, preserving source data.

Dry run produced **six observations**. Actual archive validation used the separate
destination `/private/tmp/bug003-t04b-archive` and completed with **12 copied**, no
moves, no skipped files, and no failures. All six observations contained exactly one
light and one stack; their FITS `TELESCOP` values were homogeneous:

- three observations: `S50_99643794`
- three observations: `S50 Pro_edfe7fb2`

No S50 observation was stack-only and no observation contained files from both
telescopes.

## Closure criteria

Implementation and validation evidence satisfies B003-01 through B003-18. B003-19
passed through the separate copy-mode archive validation above. Formal BUG-003
closure is intentionally not declared here, because the controlling specification
requires user review and approval.