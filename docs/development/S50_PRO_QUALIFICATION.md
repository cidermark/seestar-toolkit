# Seestar Toolkit — S50 Pro Qualification

## Stage 3 — Qualification Report

## Purpose and scope

Stage 3 qualified original Seestar S50 Pro FITS data against the existing
Seestar Toolkit conversion, FITS inspection, archive-reconstruction and
incremental archive-reconciliation workflows. The exercise used the
representative M27 reconnaissance dataset described below, including combined
and sequential S50/S50 Pro archive exercises.

This qualification is limited to the tested source data, capture
configurations, firmware and workflows. It records technical qualification
evidence; it does not constitute formal Stage 3 administrative closure.

## Test environment

| Item | Qualification environment |
|---|---|
| Telescopes | Original Seestar S50 and Seestar S50 Pro |
| Firmware | PROGRAM 9.31 |
| Dataset | M27 reconnaissance dataset captured 13 October 2026 |
| Sample | Twelve representative FITS files |
| Capture coverage | Three capture configurations per telescope |
| S50 `TELESCOP` | `S50_99643794` |
| S50 Pro `TELESCOP` | `S50 Pro_edfe7fb2` |

The qualification datasets are maintained outside this Git repository. The
Stage 3 qualification root is
`/Users/mark/tmp/Astro_Tests/seestar_toolkit_testfiles/S50Pro_qualification_test`.
The original nine qualification datasets are at
`/Users/mark/tmp/Astro_Tests/seestar_toolkit_testfiles/captures_for_seestar_toolkit`.
The reported exercises used these controlled datasets; they were not moved,
modified, regenerated or deleted as part of this documentation update.

The S50 Pro FITS files do not contain an `INSTRUME` keyword.

## Qualification tests

| Test | Description | Result |
|---|---|---|
| T01 | S50 Pro raw Bayer light conversion | PASS |
| T02 | S50 Pro stacked FITS conversion | PASS |
| T03 | Missing `INSTRUME` handling | PASS |
| T04a | Combined S50/S50 Pro archive reconstruction | PASS following BUG-003 |
| T04b | Actual copy-mode archive validation | PASS |
| T05a | S50-only archive | PASS |
| T05b | S50 Pro-only archive | PASS |
| T05c | Combined S50/S50 Pro archive reconstruction | PASS |
| T06a | Sequential archive: initial S50 archive | PASS |
| T06b | Sequential archive: S50 Pro incremental reconciliation | PASS |

T01 and T02 each produced verified output of 3840 × 2160 pixels with three RGB
channels and unsigned 16-bit data. T03 successfully inspected S50 Pro FITS
files without an `INSTRUME` keyword.

## BUG-003 discovery and resolution

The combined dataset initially exposed cross-telescope light association.
The cause was that S50 Pro `TELESCOP` values were not recognised, allowing the
existing unknown-identity compatibility rules to associate them with recognised
S50 identities.

BUG-003 added explicit, model-aware recognition of complete S50 and S50 Pro
identities, preventing association between different recognised telescopes
while preserving the established compatibility behaviour for unknown
identities. The authoritative requirements are in
[BUG-003 specification](change_documents/BUG_003/BUG_003.md); implementation
and validation evidence is recorded in the
[BUG-003 completion report](change_documents/BUG_003/BUG_003_REPORT.md).

## Final archive validation

The copy-mode validation used twelve original FITS files and reconstructed six
complete observations: three per telescope, with one light and one stack per
observation. It copied all twelve files, with zero moves, skips or failures.

There was no cross-telescope light association and no incorrectly stack-only
S50 observation. Copy mode preserved the original source data. The BUG-003
completion report is the authoritative evidence for this final archive
validation.

## Qualification limitations

- Qualification covers only the tested firmware and FITS formats.
- S30 and S30 Pro were not qualified.
- Other firmware versions and capture modes were not qualified.
- T05 and T06 evidence covers the recorded S50/S50 Pro datasets only; it does
  not establish compatibility with other Seestar models, data formats or
  untested capture configurations.
- Independent inspection of archive hierarchy, stack companion TIFFs and
  archive-index contents was not evidenced as part of T04b acceptance. T05
  and T06 provide additional archive-artifact and index evidence only for
  their stated datasets and scenarios.

The final limitation records the boundary of the acceptance evidence; it does
not indicate failure of those additional checks.

## T05 — Archive reconstruction validation

### Objective and method

T05 validated archive reconstruction from complete S50-only, S50 Pro-only and
combined inputs. It used the archive command in copy mode against the
qualification datasets identified above. The individual invocation commands
and destination paths are not retained in this report; the recorded command
outcomes, output inventories and independent FITS-header checks below are the
qualification evidence.

T05c is a combined reconstruction exercise: both telescope datasets were
reconstructed together from source inputs into one archive. It is distinct
from T06, which validates reconciliation when a second telescope is added to
an already populated archive.

### Results

| Exercise | FITS archived | Observations | Companion TIFFs | Archive index | Failures | Exit code |
|---|---:|---:|---:|---:|---:|---:|
| T05a — S50 only | 27 | 3 | 3 | 1 | 0 | 0 |
| T05b — S50 Pro only | 36 | 3 | 3 | 1 | 0 | 0 |
| T05c — combined | 63 | 6 | 6 | 1 | 0 | 0 |

T05c reconstructed three observations per telescope with no cross-telescope
associations. Telescope identities were independently verified from FITS
headers. The resulting observation distribution was:

| Observation | Telescope | Lights | Stacks |
|---:|---|---:|---:|
| 01 | S50 | 6 | 1 |
| 02 | S50 Pro | 12 | 1 |
| 03 | S50 Pro | 10 | 1 |
| 04 | S50 | 8 | 1 |
| 05 | S50 | 10 | 1 |
| 06 | S50 Pro | 11 | 1 |

### Finding and conclusion

A Finder `.DS_Store` file initially generated a discovery warning when it was
present in the test input. Removing that Finder-generated file from the test
input cleared the warning. This is recorded as a non-blocking qualification
finding, not as a confirmed product defect.

T05 passed: isolated and combined reconstruction correctly preserved the
three-observations-per-telescope separation and produced the expected archive
artifacts without failures.

## T06 — Sequential multi-telescope archive validation

### Objective and method

T06 validated incremental archive reconciliation rather than combined source
reconstruction. First, S50 captures were archived into an empty destination.
Then S50 Pro captures were archived into that same destination. The acceptance
criteria were preservation of the original archive content, correct addition
of the S50 Pro content, correct telescope separation, and a reconciled archive
index.

As with T05, the exact invocations and destination paths are not retained in
this report. The documented archive-command outcomes and independent SHA-256,
FITS-header and archive-index checks are the evidence.

### T06a baseline archive

The initial S50 archive completed with 27 FITS, three observations and three
TIFFs, with zero failures and exit code 0. SHA-256 baselines were recorded for
all 30 resulting image files (27 FITS and three TIFFs).

### T06b incremental reconciliation results

Adding the S50 Pro captures to the existing archive completed with zero
failures and exit code 0. The final archive contained 63 FITS, six
observations, six TIFFs and one updated archive index.

All 30 original S50 FITS and TIFF files were verified after reconciliation:
zero were missing, zero were modified, and SHA-256 verification passed.

| Observation | Telescope | Lights | Stacks |
|---:|---|---:|---:|
| 01 | S50 | 6 | 1 |
| 02 | S50 | 8 | 1 |
| 03 | S50 | 10 | 1 |
| 04 | S50 Pro | 12 | 1 |
| 05 | S50 Pro | 10 | 1 |
| 06 | S50 Pro | 11 | 1 |

Independent FITS-header verification confirmed three observations per
telescope, no mixed telescope identities, 57 lights and six stacked FITS, and
correct light counts in every observation. The verified telescope identities
were `S50_99643794` (S50) and `S50 Pro_edfe7fb2` (S50 Pro). Overall
header-based verification passed.

The archive index correctly represented six observations with the correct
telescope identities and light counts. Its observing-night date was
2026-10-14, and its exposure, filter and capture-mode metadata were correct.
Archive-index verification passed.

### Conclusion

T06 passed. Incremental reconciliation added the S50 Pro observations without
altering the pre-existing S50 image files, while retaining correct observation
membership, telescope identities and index metadata.

## Overall Stage 3 qualification conclusion

The Seestar S50 Pro successfully passed Stage 3 technical qualification for
the tested conversion, FITS inspection, combined archive-reconstruction and
sequential archive-reconciliation workflows. T05 confirms correct isolated
and combined S50/S50 Pro reconstruction without cross-telescope associations.
T06 independently confirms preservation of an existing S50 archive while S50
Pro material is incrementally reconciled into it.

The only new qualification finding is the non-blocking Finder `.DS_Store`
discovery warning described in T05; it is not a confirmed product defect. No
unresolved failure is recorded within the stated qualification scope.
Technical qualification completion remains distinct from formal Stage 3
administrative closure, which requires separate review and approval.

## Formal closure status

- **Stage 3 technical qualification:** PASS.
- **Independent closure-readiness review:** PASS.
- **User acceptance of T01–T06:** APPROVED, 26 October 2026.
- **Qualification limitations:** ACCEPTED.
- **Finder `.DS_Store` warning:** ACCEPTED as non-blocking.
- **BUG-003:** previously resolved and formally closed.
- **Administrative closure:** APPROVED, subject to completion of the
  documentation and Git workflow.

This status records approval of the administrative closure decision. It does
not assert that the required documentation or Git workflow has been completed,
and it does not alter the technical qualification evidence or its stated
limitations.
