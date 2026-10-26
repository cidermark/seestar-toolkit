# Seestar Toolkit — Development Changelog

## Purpose and conventions

This is the development history of the Seestar Toolkit repository, **not** a list of features necessarily available in the published v1.1.0 package. Significant commits are presented newest first. The **Work summary** column paraphrases the work and is not necessarily the exact Git commit subject.

Commit identifiers were checked against repository Git history during the 23 October 2026 read-only documentation verification. The six date discrepancies identified in that review have been corrected. Dates below are commit dates, not necessarily dates of formal approval or publication.

The original Stages 1–9 refer to the v1.1.0 development programme; the later S50 Pro qualification Stage 3 is a separate exercise.

## Development commit history

| Work item | Work summary | Commit | Commit date |
|---|---|---|---|
| S50 Pro qualification — Stage 3 | Technical qualification completion, independent closure-readiness PASS and T01–T06 user approval recorded; administrative closure approved subject to documentation and Git workflow completion | `1aac9ec` | 2026-10-26 |
| DOC | Update roadmap with BUG-003 completion | `ff39cb1` | 2026-10-23 |
| BUG-003 | Record BUG-003 closure documentation | `548a632` | 2026-10-21 |
| BUG-003 | Closure documentation | `548a632` | 2026-10-21 |
| BUG-003 | Recognise S50 Pro telescope identities | `ea69b99` | 2026-10-21 |
| ENH-003 | Record final ENH-003 closure bookkeeping | `123c5eb` | 2026-10-13 |
| ENH-003 | Final closure bookkeeping | `123c5eb` | 2026-10-13 |
| DOC | Record ENH-003 completion | `70ec93d` | 2026-10-13 |
| ENH-003c | Integrate archive light TIFF conversion workflow | `511ca08` | 2026-10-13 |
| ENH-003b | Add safe archive light TIFF conversion engine | `e39aa04` | 2026-10-13 |
| ENH-003a | Establish archive light layout foundation | `989c0ea` | 2026-10-09 |
| ENH-002 | Record ENH-002 documentation and closure | `18129d2` | 2026-10-07 |
| ENH-002 | Documentation and closure | `18129d2` | 2026-10-07 |
| ENH-002 | Add configurable observation date policy | `2c48ecd` | 2026-10-07 |
| ENH-001 | Integrate and close configuration management enhancement | `4595540` | 2026-10-05 |
| ENH-001c | Update configuration documentation and validate development PDFs | `b630c24` | 2026-10-05 |
| ENH-001c | Handle malformed hierarchy braces and preserve configuration repair | `2425ccf` | 2026-10-01 |
| ENH-001b | Manage saved locations and extract FITS GPS | `c8ac83d` | 2026-10-01 |
| ENH-001a | Implement ENH-001 configuration foundation and archive preferences | `99c3272` | 2026-09-30 |
| DOC | Record Stage 9 closure and BUG-002 completion | `3c75002` | 2026-09-29 |
| BUG-002 | Telescope-aware reconstruction and incremental archive reconciliation | `11a60b5` | 2026-09-29 |
| 9.4b | Close Stage 9 and v1.1.0 release process | `c0c0336` | 2026-09-24 |
| 9.4b | Correct release evidence | `bf3af81` | 2026-09-23 |
| 9.4b | Release Seestar Toolkit v1.1.0 | `b954d97` | 2026-09-23 |
| 9.4a | Assemble and validate release candidate | `6784f8d` | 2026-09-23 |
| DOC | Record Stage 9.3b and BUG-001 completion | `93a4299` | 2026-09-22 |
| BUG-001 | Stop archive light TIFF generation | `58a57b9` | 2026-09-22 |
| 9.3b | Generate and validate documentation PDFs | `e78c3d0` | 2026-09-21 |
| 9.3a | Complete user and public documentation | `e45ca0d` | 2026-09-21 |
| 9.2b | Validate installed CLI and storage workflows | `62cab64` | 2026-09-14 |
| 9.2a | Validate clean installs and Python compatibility | `1f7de39` | 2026-09-13 |
| 9.1d | Validate and close distribution CI | `c3c14dc` | 2026-09-11 |
| 9.1d | Fix CI whitespace validation | `4c40e54` | 2026-09-11 |
| 9.1d | Add CI validation workflow | `7109ba7` | 2026-09-11 |
| 9.1c | Configure package metadata, versioning and builds | `6a6ddf7` | 2026-09-11 |
| 9.1b | Reorganise repository and documentation | `ff304d7` | 2026-09-10 |
| 9.1a | Audit release requirements, compatibility and packaging | `6d72706` | 2026-09-10 |
| 8.3a | Validate and close Stage 8 | `995c988` | 2026-09-08 |
| 8.2g | Validate full real-data remediation | `a329bd9` | 2026-09-08 |
| 8.2f | Correct mosaic target semantics in archive planning | `491ce26` | 2026-09-08 |
| 8.2d | Correct stack-count diagnostic semantics | `02d92ce` | 2026-09-08 |
| 8.2c | Normalize mosaic target comparison | `25587ef` | 2026-09-07 |
| 8.2b | Correct filename FITS diagnostic semantics | `a5fda62` | 2026-09-07 |
| 8.2a | Correct equal-time reconstruction ordering | `65872ec` | 2026-09-07 |
| 8.1e | Consolidate Stage 8.1 discrepancies | `e1a00f2` | 2026-09-07 |
| 8.1d | Validate Dataset 08 multi-session behavior | `d845067` | 2026-09-07 |
| 8.1c | Validate Datasets 05-07 and 09 | `d5e7f92` | 2026-09-07 |
| 8.1b | Validate Datasets 02-04 | `330d69a` | 2026-09-07 |
| 8.1a | Validate Dataset 01 baseline | `5800b47` | 2026-09-07 |
| 7.1j | Validate and close Stage 7 | `db4db43` | 2026-09-04 |
| 7.1i | Validate complete archive workflows | `ae5abdb` | 2026-09-03 |
| 7.1h | Add target archive indexes | `c3052d5` | 2026-09-03 |
| 7.1g | Add archive CLI and dry-run | `f8f07e5` | 2026-09-03 |
| 7.1f | Integrate archive TIFF orchestration | `07fde20` | 2026-09-03 |
| 7.1e | Add safe archive file operations | `7bdc859` | 2026-09-03 |
| 7.1d | Plan archive destinations | `7c1086f` | 2026-09-03 |
| 7.1c | Reconstruct Seestar observations | `6e8590e` | 2026-09-02 |
| 7.1b | Add Seestar input discovery | `610db0d` | 2026-09-02 |
| 7.1a | Define archive architecture and policies | `22c588a` | 2026-09-02 |
| 6.1h | Validate and close Stage 6 | `de1f14c` | 2026-09-01 |
| 6.1g | Validate Stage 6 conversion and batch workflows | `8969837` | 2026-09-01 |
| 6.1f | Add batch conversion | `e6214e1` | 2026-09-01 |
| 6.1e | Integrate single-file convert CLI | `2fb1614` | 2026-09-01 |
| 6.1d | Validate Siril RGB conversion path | `9458bb7` | 2026-09-01 |
| 6.1c | Validate native Seestar RGB conversion path | `98e42b3` | 2026-08-31 |
| 6.1b | Validate raw Bayer conversion path | `8001815` | 2026-08-31 |
| 6.1a | Define conversion pipeline contract | `6c1ee7e` | 2026-08-31 |
| DOC-7 | Add archive organisation stage to roadmap | `b4a6477` | 2026-08-31 |
| DOC-6 | Reorganize change_documents directory | `980a38a` | 2026-08-31 |
| 5.1f | Validate and close Stage 5 | `75f5c92` | 2026-08-31 |
| 5.1e | Validate integrated TIFF output | `3a940cc` | 2026-08-31 |
| 5.1d | Integrate FITS conversion with TIFF output | `54d8c60` | 2026-08-31 |
| 5.1c | Add float32 TIFF output support | `1debcec` | 2026-08-29 |
| 5.1b | Complete TIFF writer file handling | `7a58987` | 2026-08-29 |
| 5.1a | Add TIFF writer foundation | `b399cd7` | 2026-08-29 |
| 4.1f | Validate and close Stage 4 | `2b62892` | 2026-08-29 |
| 4.1e | Define Stage 4 to Stage 5 handoff | `6ef5566` | 2026-08-29 |
| 4.1d | Validate Siril stacked FITS | `e453343` | 2026-08-29 |
| 4.1c | Validate real Seestar stacked FITS | `2c999ae` | 2026-08-29 |
| 4.1b | Implement RGB layout normalization | `22342e0` | 2026-08-28 |
| 4.1a | Define RGB image handling contract | `d7bb974` | 2026-08-28 |
| 3.1e | Validate and close Stage 3 | `938c1e3` | 2026-08-28 |
| 3.1d | Validate mosaic-session FITS demosaicing | `75ee5e8` | 2026-08-28 |
| 3.1c | Validate real Seestar FITS demosaicing | `041ecb7` | 2026-08-27 |
| 3.1b | Implement genuine Bayer interpolation | `19fa8d8` | 2026-08-27 |
| 3.1a | Add Bayer demosaicing foundation | `9691e8b` | 2026-08-27 |
| DOC-5 | Removed resolved Known Issues | `2d1bde5` | 2026-08-27 |
| DOC-4 | Add Codex development guidance | `d7a2fa9` | 2026-08-27 |
| 2.2e | Validate and close Stage 2 | `3f67cfc` | 2026-08-26 |
| 2.2d | Add reliable FITS image classification | `9271283` | 2026-08-26 |
| DOC-3 | Reformat project changelog | `c4dd737` | 2026-08-26 |
| 2.2c | Expand FITS inspection metadata | `3efd84f` | 2026-08-26 |
| DOC-2 | Update archive layout documentation and changelog | `616bc87` | 2026-08-26 |
| TOOL-1 | Refresh FITS inspection utility | `146147a` | 2026-08-25 |
| DOC-1 | Update documentation through Stage 2.2b.2 | `dd77745` | 2026-08-25 |
| 2.2b.2 | Support RGB FITS Images in the FITS Reader | `1a1f209` | 2026-08-25 |
| 2.2b.1 | Extend FITS image model for multiple image layouts | `bacfe07` | 2026-08-05 |
| 2.2a½ | Document FITS investigation and add developer inspection tools | `e746bbe` | 2026-08-03 |
| x.xx | Reorganize test suite structure | `e86d981` | 2026-07-31 |
| x.xx | Move project to repository root | `50d5251` | 2026-07-31 |
| x.xx | Reorganize project documentation | `bfb756c` | 2026-07-31 |
| 2.2a | Stage 2.2a: Add FITS metadata inspection | `e1ae814` | 2026-07-31 |
| 2.1b | Stage 2.1b: Implement FITS image reader | `cca662b` | 2026-07-30 |
| 2.1a | Stage 2.1a: Add FITS subsystem foundation | `4e8df76` | 2026-07-30 |
| 1.0 | Complete Stage 1 : development environment and project foundations | `d43ed58` | 2026-07-30 |

## Release and closure distinctions

- **v1.1.0:** release commit `b954d97` dated **23 September 2026**; annotated tag `v1.1.0` created **24 September 2026**. Subsequent development work is not represented here as a newly published release.
- **BUG-001, BUG-002 and BUG-003:** completed and closed. BUG-003 implementation `ea69b99`, closure documentation `548a632`, and roadmap update `ff39cb1` are separate recorded events.
- **ENH-001, ENH-002 and ENH-003:** completed and closed.
- **S50 Pro qualification Stage 3:** technical PASS and independent
  closure-readiness PASS recorded; T01–T06 user acceptance was approved on 26
  October 2026. Administrative closure is approved subject to completion of
  the documentation and Git workflow. This pending administrative entry has no
  commit identifier. It is not part of the original Stage 3 demosaicing work.
- The `.DS_Store` input discovery warning recorded during qualification is non-blocking; no product defect was confirmed from that finding.

## Provenance and maintenance

- The commit identifiers and dates in the table reflect the targeted Git verification report supplied on 23 October 2026. The verification did not independently rerun private external datasets.
- Historical implementation narratives and deferred ideas belong in the relevant change reports, `PROJECT_Notes.md` and the preserved historical snapshot, rather than being duplicated here.
- Record an actual commit only after it exists. Keep implementation, validation, documentation, formal closure and Git actions distinct.
