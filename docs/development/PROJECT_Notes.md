# Seestar Toolkit — Project Notes

> **Status date:** 27 October 2026<br>
> **Purpose:** Current project state, architectural decisions, roadmap and outstanding work.<br>
> **Historical detail:** The source notes contain a chronological development diary. The original notes are preserved in `docs/development/history/PROJECT_Notes_HISTORICAL_SNAPSHOT.md` to avoid losing prior checkpoint evidence.

## 1. Project overview

Seestar Toolkit is a Python command-line toolkit for inspecting Seestar FIT/FITS files, converting raw Bayer or stacked RGB data into linear RGB TIFFs, and organising source captures into a structured archive.

**Public release:** v1.1.0 (release commit 23 September 2026; annotated tag created 24 September 2026). Subsequent enhancements and bug fixes have been developed without a separately evidenced new public release. Do not label the published v1.1.0 build as containing all later work.

**Development:** Python 3.13 locally; published package support validated for Python 3.11–3.14 on macOS arm64. The repository uses pytest, Ruff, an editable installation and GitHub Actions.

## 2. Current roadmap

The numbered Stages 1–9 below refer to the original development and release programme. **S50 Pro qualification Stage 3** is a separate qualification exercise and must not be confused with the original **Stage 3 Bayer demosaicing**.

| Item | Scope | Status |
|---|---|---|
| Stage 1 | Development foundations | Complete |
| Stage 2 | FITS inspection and classification | Complete |
| Stage 3 (original) | Bayer demosaicing | Complete |
| Stage 4 | RGB FITS processing | Complete |
| Stage 5 | TIFF writer | Complete |
| Stage 6 | Single-file and batch CLI conversion | Complete |
| Stage 7 | Archive organisation | Complete |
| Stage 8 | Real-data qualification | Complete |
| Stage 9 | Packaging, documentation and v1.1.0 release | Complete |
| BUG-001 | Prevent automatic light-TIFF generation during normal archive runs | Complete |
| BUG-002 | Telescope-aware observation reconstruction and incremental reconciliation | Complete |
| ENH-001 | Configuration management | Complete |
| ENH-002 | Configurable observing-night date policy | Complete |
| ENH-003 | Optional archive light-TIFF conversion | Complete |
| BUG-003 | S50 Pro telescope identity recognition | Complete |
| ENH-004 | Archive-aware standalone conversion | Formally approved and complete 27 October 2026; Git integration pending. Real-world archive testing has not yet been performed. |
| S50 Pro qualification — Stage 3 | Technical qualification T01–T06 | Technical PASS; closure readiness PASS; T01–T06 user acceptance APPROVED 26 October 2026; administrative closure APPROVED, subject to documentation and Git workflow completion |

## 3. Current behaviour and architectural decisions

### 3.1 FITS inspection and image conversion

- The FITS reader classifies two-dimensional raw Bayer images and channels-first `(3, height, width)` RGB FITS.
- Demosaicing supports `RGGB`, `GRBG`, `GBRG` and `BGGR` and produces `(height, width, 3)` RGB `uint16` data.
- RGB layout normalisation preserves channel order, values and dtype. Seestar `uint16` and Siril `float32` are validated cases.
- TIFF writing preserves linear `uint16` or `float32` data; it does not implicitly stretch, scale, clip or white-balance.
- `convert INPUT_FITS [OUTPUT_TIFF]` converts one file. An omitted output is
  inferred only for a direct light under a recognised current
  `observation_NN/fits_images/lights/` path.
- `convert-batch INPUT_DIR [OUTPUT_DIR]` remains flat and non-recursive. Current
  archive inputs at the observation, `fits_images` or canonical lights level
  resolve to canonical lights with either inferred or explicit output; ordinary
  directories require explicit output.
- Inferred standalone derivatives use lazy
  `observation_NN/tiff_images/lights/` creation and retain the conversion
  writer's exclusive-create collision policy. This does not alter archive
  execution or `archive --convert-lights`.

### 3.2 Archive organisation

- Archive hierarchy is configurable; the default order is `{target}/{location}/{session_end_date}`.
- Observation directories are numbered `observation_01`, `observation_02`, etc.
- **Current post-ENH-003 observation layout:**

```text
observation_NN/
├── fits_images/
│   └── lights/
├── seestar_stacked/
│   ├── stacked.fit
│   └── stacked.tiff
└── tiff_images/                 # created only when light TIFFs are produced
    └── lights/
```

The stacked filenames are illustrative; the source stack basename is preserved. Normal archiving preserves light FITS without creating light TIFFs. `archive --convert-lights` enables optional light-TIFF conversion from verified archived FITS. Earlier Stage 7 notes described an older `lights/` and `tiff/` layout; those are historical, **not** the current contract.

- Copy is the safe default. Move requires explicit selection and verified file operations.
- Identical content and differing-content filename collisions are handled conservatively; no silent overwrite.
- Archive dry-run uses the planning path without mutating source or destination.
- The target-level `INDEX.md` is a derived convenience index, not authoritative input for reconstruction.
- Location handling supports configured saved locations, GPS matching and interactive workflows where applicable.

### 3.3 Configuration and observing-night policy

- ENH-001 added inspection and persistent editing of supported TOML preferences, including saved locations and FITS GPS extraction.
- ENH-002 added `archive.observation_date_policy` with `end` as the default and `start` as the alternative. It is persisted through configuration, not a per-run archive override.
- The observing-night date is a grouping label; source FITS timestamps are not rewritten. Existing archives are not automatically reorganised when the policy changes.
- Older notes describing configuration as *read-only* or date policy as permanently fixed reflect earlier stages and are superseded.

### 3.4 Telescope identity

- BUG-002 separated observations where positively recognised S50 device identities conflict, including sequential archive reconciliation.
- BUG-003 added recognition of S50 Pro device-specific `TELESCOP` values such as `S50 Pro_edfe7fb2`.
- The observed S50 Pro qualification FITS lacked `INSTRUME`; absence of that field must not invalidate otherwise supported files.
- Unknown or generic telescope identities retain conservative compatibility behaviour; recognition does not establish the origin of otherwise unidentified captures.

## 4. Validation and release history

| Work | Evidence summary |
|---|---|
| Original Stage 8 | Nine datasets; 11 observations; 1,020 external files preserved; completed real-data regression |
| Original Stage 9 | v1.1.0 packaging, documentation and publication completed; GitHub Actions green |
| ENH-001 | Configuration management integrated and closed; C01–C27 accepted |
| ENH-002 | D01–D10 accepted; 568 pytest passes at closure |
| ENH-003 | L01–L36 accepted; three implementation substages and documentation closure |
| BUG-003 | Implementation and validation complete; 626 tests passed; mixed S50/S50 Pro 12-file archive verified; formally closed 21 October 2026 |
| ENH-004 | Formally approved and complete 27 October 2026. ENH-004a archive recognition completed at `ddde7c2`; ENH-004b CLI integration completed at `cc3f86a`; ENH-004c documentation and validation completed at `8a5b294`. T01–T32 coverage satisfied; 195 focused/regression tests and 664 full-suite tests passed; Ruff, changed-file formatting, CLI-help verification and Git whitespace checks passed. No implementation defects remain outstanding. Real-world testing against the user's observing archive has not yet been performed; automated validation is not presented as field testing. Git integration remains pending. |

### 4.1 S50 Pro qualification — separate Stage 3

The qualification report is `docs/development/S50_PRO_QUALIFICATION.md`.

- **T01–T03:** S50 Pro raw Bayer and stacked RGB conversion, plus missing-`INSTRUME` inspection — PASS.
- **T04:** Initial mixed-device association problem led to BUG-003; the corrected 12-file mixed-device exercise passed.
- **T05a/T05b:** Individual S50 (27 FITS) and S50 Pro (36 FITS) archive reconstructions passed.
- **T05c:** Combined reconstruction passed with 63 FITS, six observations, six companion TIFFs, one index and zero failures.
- **T06a/T06b:** Sequential archiving into the same destination passed. All 30 original S50 image files were SHA-256 verified unchanged after adding S50 Pro data. Final archive: 63 FITS, six observations, six TIFFs and updated index.
- A Finder `.DS_Store` file caused a non-blocking discovery warning in a test input. No confirmed product defect was established.

**Current status:** Technical qualification and independent closure-readiness
review PASS. User acceptance of T01–T06 is **APPROVED, 26 October 2026**;
qualification limitations and the non-blocking Finder `.DS_Store` warning are
accepted. Administrative closure is **APPROVED, subject to completion of the
documentation and Git workflow**. Qualification is limited to the tested
firmware, captures and workflows; S30/S30 Pro and untested modes are not
qualified.

## 5. Future work and deferred ideas

These are candidates, not approved implementations or commitments. Priorities and ENH/BUG identifiers must be agreed before work begins.

| Candidate | Description | Origin | Status |
|---|---|---|---|
| TIFF verification | Independently verify archived TIFF derivatives against authoritative FITS conversion output | ENH-003 deferred follow-up | Deferred |
| Archive regeneration | Rebuild or reorganise existing archives safely when hierarchy or date policy changes | Post-release enhancement inventory; ENH-002 deferral | Deferred |
| Telescope hierarchy token | Optional telescope model or device identity in archive paths | Archive hierarchy enhancement proposal | Deferred |
| Anonymise | Produce privacy-sanitised FITS copies without modifying originals | Post-release enhancement inventory | Deferred |
| Dry-run summary | Concise observation-level archive plan by default, detailed per-file output via an optional verbose mode | S50 Pro qualification follow-up | Deferred |
| Configuration prompt clarity | Make Enter-to-skip and `y`-to-save behaviour clearer; preserve existing accepted responses | Configuration usability observation | Deferred |
| Additional telescope qualification | S30/S30 Pro and other firmware or capture configurations, subject to representative evidence | S50 Pro qualification scope boundary | Deferred |
| Additional capture formats | Solar, Lunar, planetary video; DSLR/conventional-camera ingestion | Longer-term roadmap | Deferred |
| Distribution and UI | GUI, macOS bundle, Windows/Linux packaging, optional Siril integration | Longer-term roadmap | Deferred |
| Diagnostics and community | Privacy-conscious diagnostics, possible GitHub Discussions | Longer-term roadmap | Deferred |

## 6. Open technical questions

- Confirm planetary and Lunar capture outputs and relevant metadata.
- Continue comparing raw and stacked FITS header variants across firmware.
- Investigate why one reviewed Siril standard preprocessing script applies `mirrorx_single result` while its mosaic script does not.
- Investigate the `.DS_Store` warning only if it becomes an agreed product issue; qualification alone does not establish a defect.

## 7. Project documentation and authoritative evidence

| Document | Role |
|---|---|
| `docs/development/PROJECT_Notes.md` | Current roadmap, architecture summary and deferred work |
| `docs/development/CHANGELOG.md` | Development commit record |
| `docs/development/history/PROJECT_Notes_HISTORICAL_SNAPSHOT.md` | Superseded historical notes retained for provenance |
| `docs/development/S50_PRO_QUALIFICATION.md` | S50 Pro qualification evidence and limits |
| `docs/development/change_documents/` | Controlling ENH/BUG and historical stage specifications and reports |
| `docs/development/ARCHITECTURE.md` | Detailed implementation architecture |
| `docs/development/SEESTAR_FITS_REFERENCE.md` | Observed FITS layouts and metadata |
| `docs/development/DEV_README.md` | Development setup |
| `docs/development/REAL_DATA_TESTING.md` | Private capture/testing rules |
| `docs/user/` | End-user guides |

## 8. Maintenance and change-control conventions

1. Keep the roadmap and current-behaviour sections **current**; do not leave superseded *STARTED* or *PENDING* statements alongside closed work.
2. Record implementation history and commit IDs in `CHANGELOG.md`; do not duplicate long checkpoint diaries here.
3. Use an authoritative change document before implementation. Resolve material design decisions with the user first.
4. Separate implementation, validation, formal closure, commit, push and merge operations.
5. Preserve older technical evidence in the change documents and historical snapshot; do not reinterpret it as a current feature contract.
6. Administrative approval of S50 Pro qualification Stage 3 does not itself
   complete the documentation or Git workflow; record any completed Git action
   only after it occurs.
