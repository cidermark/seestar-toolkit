# ENH-005 — FITS Privacy Processing

**Document status:** DRAFT — AUTHORITATIVE SPECIFICATION
**Document role:** Controlling ENH-005 specification and recorded closure evidence
**Repository path:** `docs/development/change_documents/ENH-005/ENH-005_FITS_PRIVACY_PROCESSING.md`
**Baseline reviewed:** `main` / `origin/main` at `ebcf02ae09b0c2344598cda6b12b9da920abad8e`
**Scope:** Standalone FITS header reporting, privacy processing, and verification
**Version:** Draft 1.4 — 2026-11-10

> **Implementation authorisation:** ENH-005c.1 and ENH-005c.2 are **COMPLETE**; their closure evidence is recorded in §§8.8–8.9. ENH-005c.3 is explicitly authorised and **IN PROGRESS**, limited to the read-only, non-interactive `pii-scrub --verify` command, its approved PASS/FAIL/REVIEW REQUIRED classifications and safe optional text report, and focused validation using the completed ENH-005c.1 and ENH-005c.2 foundations. It does not authorise ENH-005d, removal of temporary `header-report --noscrub`, batch or recursive processing, or changes to `archive`, `convert`, or `convert-batch`. The temporary development-only `--noscrub` exception remains subject to its mandatory removal during ENH-005d. This amendment does not authorise branch creation, commit, push, or merge.

## 1. Purpose and scope

ENH-005 provides privacy-conscious sharing tools for Seestar FITS metadata and FITS copies. It does not change `archive`, `convert`, or `convert-batch`, and does not modify an input FITS file.

Compliance means conformance with this ENH-005 policy, not a guarantee of anonymity. Preserved telescope identifiers, timestamps, astronomical coordinates, image data, and other technical metadata may permit indirect identification or correlation.

## 2. Commands and exit codes

```text
seestar-toolkit header-report [OPTIONS] INPUT
seestar-toolkit pii-scrub [OPTIONS] INPUT
seestar-toolkit pii-scrub --verify [OPTIONS] INPUT
```

- One FITS input per invocation; no batch or recursive mode.
- Options are documented before `INPUT` and accepted on either side.
- `--output` specifies an exact output filename, never an output directory.
- `0` means successful operation or PASS verification; `1` means operational failure, FAIL verification, or REVIEW REQUIRED verification; `2` means CLI argument or usage error. Malformed or unsupported FITS inputs are operational errors, not privacy classifications.

## 3. Agreed command behaviour

### 3.1 `header-report`

`header-report` is read-only FITS-header inspection. It reads every HDU header without reading image pixel arrays and writes a privacy-processed text report.

- The report includes a concise summary and a privacy-processed header representation.
- Recognised safe values are preserved. Recognised sensitive values are replaced under §4.
- Unknown values are represented as `WITHHELD`; their originals must never appear in the report.
- Keyword descriptions (the text following a card's `/` separator) are processed under §4.4 independently of their associated values. Standalone `COMMENT` and `HISTORY` card contents are always withheld.
- No prompt occurs during report generation. Unknown metadata requiring review does not prevent successful generation; successful creation returns `0`.
- After successful generation, an interactive terminal may offer **View / Finder / Quit**. `--noprompt` suppresses that convenience menu. Finder integration is macOS-only.
- The menu requires both stdin and stdout to be TTYs. It is otherwise suppressed. Viewer/Finder launch failures are warnings and do not invalidate an already-created report.

#### 3.1.1 Temporary development-only `--noscrub` exception

For the limited ENH-005b.1 implementation stage only, `header-report` may accept a temporary development-only `--noscrub` option to support comparison of privacy-processed reports with representative original-header reports.

- It generates a text report containing original FITS header values and comments, preserving header card order, duplicate cards, and HDU boundaries.
- It reads headers only and never modifies the source FITS.
- It displays a clear terminal privacy warning before reporting success. It must never automatically share original metadata or include it in logs, fixtures, summaries, completion reports, exception messages, or generated filenames other than the required distinguishable output filename.
- Without `--output`, its default report filename must contain `_UNSCRUBBED` (for example, before the text-report suffix). `--output` remains an exact destination filename under §5.
- It follows every applicable safe-output requirement in §5, including no overwrite, source/destination equivalence rejection, required-directory creation only, and no incomplete output after failure.
- It is excluded from normal `--help` output and public documentation. It must be documented only internally as a temporary development exception.
- It must be removed during ENH-005d before production release. Production release is blocked while `--noscrub` exists.

This exception does not alter the normal privacy-processed behaviour of `header-report`, nor does it make original metadata safe to distribute.

### 3.2 `pii-scrub`

`pii-scrub` creates a separate privacy-processed FITS file.

- It never modifies, moves, or deletes the input.
- It inspects every HDU header and applies §4 while preserving all HDUs, their order, and their data under §6.
- An interactive invocation presents A/P/Q review for every occurrence of an unknown metadata value: **(A)nonymise**, **(P)reserve**, or **(Q)uit**. An occurrence is specific to its HDU and card occurrence; duplicate keyword/value pairs, including those in separate HDUs, are reviewed separately. The prompt displays the keyword, current value, and proposed replacement. Empty input is not approval to preserve; decisions are not persisted.
- A preserved unknown value makes the output **REVIEW REQUIRED**. The file may still be created and the scrub operation returns `0` with an explicit warning. Its intentional preservation remains visible to later verification as REVIEW REQUIRED; it is not silently treated as safe. No tracking marker or processing-history record is added; a P decision applies only to that occurrence in that scrub operation.
- When either stdin or stdout is not a TTY, the command is non-interactive: it anonymises unresolved unknown metadata, emits warnings without original values, and does not prompt.
- On quit or failure, it publishes no incomplete output file.

### 3.3 `pii-scrub --verify`

`pii-scrub --verify` is read-only and non-interactive. It reads headers without loading pixel arrays or requesting decisions.

- It reports PASS, FAIL, or REVIEW REQUIRED to the terminal by default. It distinguishes a confirmed privacy-policy violation (FAIL) from unresolved unknown metadata (REVIEW REQUIRED). A malformed or unsupported FITS input instead produces a privacy-safe operational diagnostic and exit code `1`.
- `--output` additionally writes a text report.
- PASS returns `0`; FAIL and REVIEW REQUIRED return `1`.
- Output identifies safe keyword names, counts, and status only; it must not disclose sensitive original values.

## 4. Agreed privacy policy

The same classification and replacement policy applies to reports, scrubbing, and verification. Every card in every HDU is inspected, including duplicate cards and card comments.

### 4.1 Recognised sensitive metadata

Automatically anonymise these keywords:

```text
SITELAT  SITELONG  OBSERVER  OBSERVAT  SITENAME  SITEALT  LATITUDE  LONGITUD
AUTHOR   EMAIL     USERNAME  USER      HOSTNAME   FILENAME  FILEPATH
```

### 4.2 Recognised safe metadata

Preserve technical and astronomical metadata, including complete `TELESCOP` values and device identifiers; observation dates and timestamps; `RA`, `DEC`, and WCS information; exposure, gain, filter, focus, temperature, and other capture settings; `INSTRUME`, `CREATOR`, `PRODUCER`, and `PROGRAM`; and image-related and structural metadata.

Do not modify structural keywords merely because their names resemble privacy-related fields. Unknown keyword values follow the review policy in §3; descriptions and standalone free text follow the mandatory withholding policy in §4.4.

### 4.3 Replacement values

| Value type | Replacement |
|---|---|
| Text | `REMOVED` |
| Integer | `0` |
| Floating point | `0.0` |
| Boolean | `False` |
| `SITELAT` / `SITELONG` | `0.0` |
| Unknown value in `header-report` | `WITHHELD` |

Replacement values retain valid FITS value types. Recognised safe text may be preserved. Descriptions and standalone free-text cards follow §4.4.

### 4.4 Card-description and standalone-comment policy

This policy applies independently to every keyword value, keyword description, `COMMENT` card, and `HISTORY` card. It is shared by `header-report`, `pii-scrub`, and `pii-scrub --verify`.

- The reviewed S50/S50 Pro light and stacked technical descriptions form the initial approved description set, including recognised WCS/SIP technical descriptions.
- Preserve a keyword description only when it exactly matches an approved keyword/description combination in that set. The recognition mechanism must be a conservative, explicit allow-list of approved pairs (or an equivalently precise, documented mapping); matching a keyword alone is insufficient, and the mechanism must not preserve unrestricted free text or use heuristic privacy detection.
- The literal `no comment` is permitted only when it is the approved description in an explicitly approved technical keyword/description combination.
- Always withhold an unknown, modified, unclassified, or potentially sensitive keyword description, including a description attached to an otherwise recognised-safe keyword. A safe keyword alone does not make its description safe; these descriptions are not eligible for interactive preservation.
- Always withhold the contents of standalone `COMMENT` cards.
- Always withhold the contents of standalone `HISTORY` cards.
- Replace recognised-sensitive field values under §§4.1 and 4.3 regardless of whether an attached description is recognised safe, withheld, or absent.
- Standalone `COMMENT` and `HISTORY` contents, and all unrecognised descriptions, are never eligible for preservation and are always withheld/anonymised. The §3.2 A/P/Q process applies to unknown metadata values, not to these free-text contents.

The report representation must not disclose withheld text. Verification must evaluate descriptions and standalone comments independently and report only safe keyword names, counts, and status.

### 4.5 Approved recognised-safe technical metadata

The following keywords are recognised-safe technical metadata. Their values are preserved in privacy-processed reports and receive the same shared classification treatment in future scrubbing and verification functionality:

```text
BIAS      XORGSUBF  YORGSUBF  APERTURE  EQMODE    WIDECAM
CCDXBIN   CCDYBIN   XPIXSZ    YPIXSZ    DATE-EXP  TOTALEXP
STACKCNT  IMAGEW    IMAGEH
```

Recognised WCS and SIP metadata, including the technical fields used by stacked FITS files, is recognised safe and preserved. This includes the established WCS/SIP keyword families and their explicitly defined technical values; it does not authorise preservation of an unknown free-text description attached to one of those fields.

## 5. Output destinations and safety

For canonical archived FITS inputs, the approved header-report layout is:

```text
observation_NN/
├── fits_images/
│   └── lights/
│       └── Light_example.fit
├── seestar_stacked/
│   └── Stacked_example.fit
└── pii-scrubbed/
    ├── Light_example_header.txt
    └── Stacked_example_header.txt
```

For `header-report`, the default report destination is determined as follows:

- A recognised archive light FITS uses the containing recognised observation's `pii-scrubbed/` directory. Recognition must reuse the established ENH-004 current-archive recognition rules: the source must be an existing regular `.fit` or `.fits` file directly beneath `observation_NN/fits_images/lights`, and that canonical lights directory and inferred destination must resolve beneath the existing observation.
- A recognised archive stacked FITS uses the containing recognised observation's `pii-scrubbed/` directory. This is a narrowly scoped ENH-005 extension for `observation_NN/seestar_stacked`: the source must be an existing regular `.fit` or `.fits` file directly beneath that canonical directory, and it must meet requirements equivalent to the ENH-004 light-input structural and path-safety requirements. This extension does not modify ENH-004 or redefine its existing light-recognition rules.
- An ordinary non-archive FITS uses `pii-scrubbed/` beneath the input file's parent directory. An archive-recognition failure that is not a path-safety failure is treated as this ordinary non-archive case; observation-like naming alone is never sufficient to select an archive destination.
- An explicit `--output` is the exact destination filename and does not invoke default-destination inference. It remains subject to every output-safety requirement in this section.

The normal default report filename is `<input_stem>_header.txt`. The temporary development-only `--noscrub` default report filename is `<input_stem>_header_UNSCRUBBED.txt`. An existing destination is refused without overwrite, returns exit code `1`, and produces a safe error; automatic numeric suffixes are not permitted. An explicit `--output` remains the exact supplied destination filename.

For ENH-005c `pii-scrub`, default destination inference reuses the established archive-aware recognition and path-safety rules above for recognised archive inputs. Recognised archive light and stacked FITS outputs are written directly to the recognised observation's `pii-scrubbed/` directory; do not create `lights/` or `seestar_stacked/` subdirectories there. Ordinary inputs use a `pii-scrubbed/` directory alongside the input file. The output retains the original FITS filename. If two inputs select the same output filename, the no-overwrite rule applies; do not rename automatically. An explicit `--output` remains an exact destination filename and bypasses default inference. The later `pii-scrub` destination classification must distinguish recognised archive lights and recognised archive stacked FITS using the applicable rules above; this does not authorise implementation of `pii-scrub`.

The implementation must apply ENH-004's path-safety requirements before accepting an archive default: reject unsafe dangling symlinks; resolve the observation, applicable canonical source directory, source, and inferred destination; and reject any resolved path that escapes the recognised observation. It must never turn a path-safety failure into ordinary-input fallback. Existing destination safety remains unchanged: never overwrite an existing destination; reject source/destination equivalence; create output directories only when required; write to a temporary output beside the intended final destination on the same filesystem; validate the completed temporary FITS file before atomically publishing it without replacing an existing destination; remove temporary output after failure or cancellation; reject operations for which safe atomic no-overwrite publication cannot be guaranteed; and avoid raw sensitive values in logs, exception messages, summaries, generated filenames, and unsafe terminal rendering. Terminal rendering must escape control characters, neutralise terminal escape/control sequences, and truncate excessively long displayed metadata values. The local interactive A/P/Q prompt is the only approved exception to non-disclosure of an unknown value, and remains subject to those safe-rendering requirements.

## 6. FITS integrity requirements

### FITS-1 — Data preservation

Modify FITS headers only. Astronomical data blocks must be preserved byte-for-byte in every supported HDU. `pii-scrub` must never decode, rescale, recompress, or otherwise change image data, and must not modify pixel-related technical metadata. Header size may change when required; valid FITS 2880-byte block alignment and HDU ordering must be maintained, and original data offsets need not remain unchanged when header growth requires relocation. It must never modify the source FITS file.

### FITS-2 — HDU and header preservation

Preserve all supported HDUs, their order, and their data. Inspect every HDU header. Modify only eligible privacy-related header values and comments; do not alter structural metadata. Support valid `HIERARCH` keywords and `CONTINUE` long-string metadata when their complete logical keywords and values are safely interpretable, and classify those complete logical items under §4. Reject unsupported encodings safely. Valid compressed-image and binary-table structures must be supported where header processing and exact data-byte preservation can be guaranteed; do not decode, rescale, recompress, or rewrite their astronomical data blocks. Reject unsupported structures safely. Unfamiliar metadata keywords remain subject to the privacy policy; unfamiliar does not by itself mean malformed or unsupported.

### FITS-3 — Checksum handling

Do not introduce `CHECKSUM` or `DATASUM` keywords. Reject an input with an invalid existing `CHECKSUM` or `DATASUM`; do not silently repair invalid inputs. Preserve valid existing `DATASUM` values when underlying data is unchanged. Recalculate a valid existing `CHECKSUM` where header changes require it, without changing image data to satisfy checksum handling.

If safe rewriting, FITS block alignment after header-size change, checksum integrity, or data preservation cannot be guaranteed, reject the file, issue a clear safe warning, and produce no completed output file. Malformed or unsupported structures must not produce partially processed output.

## 7. Verification policy

Verification assesses current metadata against §4.

| Result | Meaning | Exit code |
|---|---|---:|
| PASS | No policy violation or unresolved review item | 0 |
| FAIL | Recognised sensitive metadata is not compliant | 1 |
| REVIEW REQUIRED | Unknown metadata remains, or a preserved unknown is not covered by an explicitly agreed safe classification | 1 |

`SITELAT=0.0` and `SITELONG=0.0` are compliant. Recognised sensitive text values must equal approved replacement markers. No processing-history record is required. A user-approved preserved unknown remains REVIEW REQUIRED for privacy purposes even though successful scrub creation returns `0`.

## 8. Historical evidence and decision history

### 8.1 Fixture privacy review

`tests/data/PRIVACY_REVIEW.md` records an earlier fixture-sanitisation policy. It replaced `SITELAT`/`SITELONG` with `0.0`, replaced telescope identifiers and timestamps with synthetic values for public test fixtures, preserved astronomical and technical metadata, preserved image data, and inspected selected `COMMENT`/`HISTORY` content.

That historical fixture policy is not the ENH-005 policy: ENH-005 preserves complete `TELESCOP` values and observation timestamps.

### 8.2 Decision register

| Decision | Status | Decision |
|---|---|---|
| D01 | AGREED | Command name: `pii-scrub`. |
| D02 | SUPERSEDED | The earlier nested `process`/`report` proposal was replaced by standalone `header-report` and direct `pii-scrub`. |
| D03 | AGREED | Preserve complete `TELESCOP` device identity. |
| D04 | AGREED | Selective privacy replacements while retaining technical metadata and FITS structure. |
| D05 | AGREED | `header-report` does not need image pixels. |
| D06 | AGREED | Single-file input. |
| D07 | AGREED | Use the separate `pii-scrubbed` output hierarchy in §5. |
| D08 | SUPERSEDED | Header reporting is a separate command, not a default `pii-scrub` action. |
| D09 | AGREED | Technical summary plus privacy-processed full header representation. |
| D10 | AGREED | No `--dry-run`. |
| D11 | AGREED | `header-report` writes a text file. |
| D12 | AGREED | Verification writes terminal results and optionally a text report. |
| D13 | AGREED | Preserve capture dates and timestamps. |
| D14 | REFINED by C03 | Interactive unknown-keyword review uses A/P/Q; C03 defines occurrence-level review and prompt content for ENH-005c. |
| D15 | SUPERSEDED by B2 | The earlier shared-review treatment for free text and comments is replaced by the explicit description and standalone-comment policy in §4.4. |
| D16 | SUPERSEDED by C03 | The earlier within-run decision-reuse proposal is replaced by occurrence-level review, including repeated keywords and separate HDUs. |
| D17 | AGREED | Non-interactive scrubbing anonymises unresolved review items and warns. |
| D18 | AGREED | A user-preserved unknown may be emitted with a REVIEW REQUIRED warning. |
| D19 | AGREED | `header-report` never prompts during generation; it withholds unknown values and can succeed with review items. |
| D20 | AGREED | Interactive `header-report` may offer View / Finder / Quit; `--noprompt` suppresses it. |
| D21 | AGREED | Document options before input and accept them on either side. |
| C1 | APPROVED | ENH-005 default archive destinations reuse established ENH-004 archive-recognition and path-safety rules; do not infer archive membership from `observation_NN` naming alone. Current ENH-004 direct-file recognition covers canonical archived lights only, not stacked FITS. Refined by D1 for ENH-005 header-report destinations. |
| D1 | APPROVED | Refines C1: canonical archived light and stacked header reports are written directly to the recognised observation's `pii-scrubbed/` directory, with no `reports/` subdirectory. Light recognition remains ENH-004's existing rule. ENH-005 adds only a narrowly scoped, structurally and path-safety-equivalent recognition extension for canonical `observation_NN/seestar_stacked/` FITS inputs; archive membership is never inferred from the observation directory name alone. |
| D2 | APPROVED | Normal reports use `<input_stem>_header.txt`; temporary development-only `--noscrub` reports use `<input_stem>_header_UNSCRUBBED.txt`. Existing destinations are refused with exit code `1` and a safe error, with no automatic numeric suffixes. Explicit `--output` is the exact supplied destination filename, subject to all output-safety rules. |
| B1 | APPROVED | The listed S50/S50 Pro technical keywords and recognised WCS/SIP metadata, including stacked-FITS technical fields, are recognised safe; preserve their values in reports and apply the shared classification in future scrubbing and verification. |
| B2 | APPROVED | Preserve only explicitly recognised approved technical keyword descriptions; withhold all other descriptions and all standalone `COMMENT` and `HISTORY` contents. |
| A1 | APPROVED | Report layout preserves card order, duplicates, and HDU boundaries, as confirmed by representative corrected real-world reports. |
| A2 | APPROVED | Corrected real-world reports confirm the approved free-text treatment: standalone `COMMENT` contents are withheld and approved technical descriptions are preserved. |
| C01 | APPROVED | FITS data integrity: modify headers only; preserve astronomical data blocks byte-for-byte in all supported HDUs; recalculate existing checksums when needed; reject files that cannot be processed safely; never modify the source FITS. |
| C02 | APPROVED | Use conservative processing for unusual FITS structures: safely process valid supported structures and apply the privacy policy to unfamiliar metadata; reject malformed or unsupported structures when safe processing cannot be guaranteed; never publish partially processed output. |
| C03 | APPROVED | Interactive privacy review is per unknown metadata occurrence: display keyword, current value, and proposed replacement; A anonymises, P preserves, and Q cancels without output. Non-interactive mode anonymises unknown values. |
| C04 | APPROVED | `pii-scrub --verify` returns PASS/0 only with no violations or unresolved unknown metadata; confirmed violations are FAIL/1; unresolved unknown metadata is REVIEW REQUIRED/1; invalid CLI usage is 2. |
| C05 | APPROVED | `pii-scrub` uses established archive-aware destination inference for recognised archive inputs and a sibling `pii-scrubbed/` directory for ordinary inputs; it preserves the input filename, supports exact explicit destinations, never overwrites, uses temporary output, validates before atomic publication, cleans temporary output on failure/cancellation, and never modifies the source. |
| C06 | APPROVED | Support valid `HIERARCH` keywords and `CONTINUE` long-string metadata when complete logical keywords and values are safely interpretable and can be classified; reject unsupported encodings safely. |
| C07 | APPROVED | Header size may change. Preserve all data blocks byte-for-byte, retain valid 2880-byte FITS block alignment and HDU order, and permit data relocation when header growth requires it. |
| C08 | APPROVED | Reject inputs with invalid existing `CHECKSUM` or `DATASUM`; do not repair them silently. Recalculate a valid existing `CHECKSUM` when header changes require it, preserve valid `DATASUM` when data is unchanged, and do not add absent checksum keywords. |
| C09 | APPROVED | Support valid compressed-image and binary-table structures only where header processing and exact data-byte preservation are guaranteed; otherwise reject safely. Never decode, rescale, recompress, or rewrite their astronomical data blocks. |
| C10 | APPROVED | Malformed or unsupported FITS inputs are operational errors with exit code `1`, not privacy PASS, FAIL, or REVIEW REQUIRED results; diagnostics are privacy-safe. |
| C11 | APPROVED | Escape control characters, neutralise terminal escape/control sequences, truncate excessively long displayed metadata values, and never disclose sensitive values in logs, errors, or non-interactive warnings. The local interactive A/P/Q prompt is the limited exception, subject to safe rendering. |
| C12 | APPROVED | Remaining unknown metadata values are REVIEW REQUIRED in verification. Do not add tracking markers or processing history; an interactive P decision applies only to that occurrence during that scrub operation. |
| C13 | APPROVED | Archive light and stacked FITS outputs are written directly to `observation_NN/pii-scrubbed/`, with original filenames and no automatic renaming; do not create `lights/` or `seestar_stacked/` subdirectories. Ordinary outputs remain `INPUT_PARENT/pii-scrubbed/`. |
| C14 | APPROVED | Create temporary output beside the final destination on the same filesystem, validate it before atomically publishing without replacement, clean it after failure or cancellation, and reject operations lacking safe atomic no-overwrite publication. |

### 8.3 ENH-005b.2 review outcomes and acceptance evidence

Real-world S50 and S50 Pro report review produced the following approved privacy-policy refinements:

- **B1 — APPROVED:** The recognised-safe technical metadata policy is expanded by §4.5. This classification is shared by reporting, future `pii-scrub`, and future verification.
- **B2 — APPROVED:** §4.4 distinguishes technical keyword descriptions from standalone free-text cards. It requires an explicit conservative recognition mechanism for technical descriptions and mandatory withholding for all other descriptions and for every standalone `COMMENT` and `HISTORY` content.

The user reviewed four corrected privacy-processed FITS header reports and approved A1 and A2. These representative real-world acceptance results are not exhaustive FITS-format validation:

| Representative report | Header cards | Sensitive values replaced | Standalone comments withheld |
|---|---:|---:|---:|
| S50 — M108 light | 44 | 2 | 2 |
| S50 — M108 stacked | 86 | 2 | 2 |
| S50 Pro — M27 light | 43 | 2 | 2 |
| S50 Pro — M27 stacked | 85 | 2 | 2 |

All four reports contain one HDU; preserve approved technical metadata and approved technical descriptions; replace `SITELAT` and `SITELONG` with `0.0`; withhold standalone `COMMENT` contents; preserve complete telescope identifiers; and retain the expected header structure. The stacked reports additionally retain approved WCS/SIP metadata and descriptions.

Accordingly, A1, A2, B1, and B2 are **APPROVED**. These approvals refine the policy. ENH-005b.1 is formally complete as recorded in §8.4. ENH-005b.2 formal closure is recorded in §8.5; overall ENH-005b closure is recorded in §8.6. The temporary development-only `--noscrub` exception and its mandatory ENH-005d removal gate remain unchanged.

### 8.4 ENH-005b.1 formal closure evidence

ENH-005b.1 implementation and focused validation were reviewed and accepted for formal closure. Closure approval is based on review of the Codex completion report and the authoritative closure criteria; it is not based on independent source inspection.

The completion report records the following implementation evidence:

- D1 archive-light recognition reuses ENH-004; D1 canonical-stacked recognition is implemented within ENH-005.
- Both recognised archive report types use `observation_NN/pii-scrubbed/`; ordinary FITS uses `INPUT_PARENT/pii-scrubbed/`.
- D2 filenames and no-overwrite behaviour are implemented.
- Source/destination equivalence and symlink/path safety are validated.
- Header-only processing, the privacy policy, multi-HDU behaviour, and the interactive menu are validated.
- Temporary `--noscrub` safeguards are validated.
- Atomic-publication failure cleanup is validated.

The completion report records the following focused validation evidence:

- 56 focused tests passed in 0.46 seconds.
- Ruff lint passed.
- Ruff formatting check passed.
- `git diff --check` passed.
- ENH-004 recognition tests passed.
- The full test suite was intentionally not run.

This closure does not alter the temporary development-only status of `--noscrub`; ENH-005d must remove it before production release.

### 8.5 ENH-005b.2 formal closure evidence

ENH-005b.2 is formally complete. Closure review found the acceptance evidence in §8.3 sufficient: the user reviewed and approved corrected privacy-processed reports for S50 light, S50 stacked, S50 Pro light, and S50 Pro stacked inputs.

The approved A1 evidence confirms preservation of header structure, card order, duplicate cards, and HDU boundaries. The approved A2 evidence confirms the required free-text treatment. The same four reports confirm B1 preservation of approved technical metadata, including WCS/SIP values in stacked reports, and B2 preservation only of approved technical descriptions while withholding unknown descriptions and standalone `COMMENT` and `HISTORY` contents. No ENH-005b.2 acceptance finding remains outstanding.

This closure records the reviewed acceptance evidence; it does not regenerate reports or repeat acceptance testing.

### 8.6 Overall ENH-005b closure evidence

Overall ENH-005b is formally complete. ENH-005b.1 is formally complete under §8.4 and ENH-005b.2 is formally complete under §8.5. The specification consistently records the approved A1, A2, B1, B2, C1, D1, and D2 decisions. D1 and D2 implementation and focused validation evidence is retained in §8.4.

No unresolved defect or material ambiguity affects the completed ENH-005b `header-report` scope. The §9 technical clarifications are resolved for subsequent implementation and validation stages; they do not reopen the completed ENH-005b scope and did not, by themselves, authorise ENH-005c implementation. At the time of ENH-005b closure, ENH-005c and ENH-005d remained not started. The later authorisation recorded by this amendment is limited to ENH-005c.1 and does not alter the completed ENH-005b evidence. The temporary development-only `--noscrub` option remains prohibited from production release and must be removed during ENH-005d.

### 8.7 Git integration record

- **Commit:** `f1de3eb` — `ENH-005b: implement privacy-safe FITS header reporting`
- **Branch:** `enh/ENH-005-fits-privacy-processing`
- **Push:** confirmed.
- **Working tree:** clean after push.

### 8.8 ENH-005c.1 formal closure evidence

ENH-005c.1 is formally complete. Formal closure was approved following review of Codex's completion evidence; it does not imply that an independent source-code audit was performed.

The reviewed implementation evidence records:

- internal FITS inspection and transformation;
- byte-preserving HDU data handling;
- multi-HDU and duplicate-card support;
- `HIERARCH` and `CONTINUE` handling;
- FITS alignment and header growth;
- `CHECKSUM` and `DATASUM` validation;
- internal output validation; and
- no source modification, CLI integration, or final publication.

The reviewed focused validation evidence records:

- 11 focused tests passed;
- 37 header-report regression tests passed;
- 86 broader FITS subsystem tests passed;
- Ruff lint passed;
- Ruff formatting passed; and
- `git diff --check` passed.

The full application suite was not run during this focused implementation stage. The implementation remains deliberately conservative at unsupported-FITS boundaries: malformed, unsupported, or safely uninterpretable structures and encodings must be rejected rather than rewritten or published where exact data preservation, structural integrity, checksum handling, or internal validation cannot be guaranteed.

- **Implementation commit:** `c2f0226`
- **Branch:** `enh/ENH-005-fits-privacy-processing`
- **Push:** confirmed.

### 8.9 ENH-005c.2 formal closure evidence

ENH-005c.2 is formally complete. Formal closure was approved after review of Codex's completion report; this records reviewed reported evidence and does not imply that an independent source-code audit was performed.

The reviewed implementation evidence records:

- standalone `pii-scrub` CLI integration with single-file input and approved exit codes;
- occurrence-level interactive A/P/Q review;
- non-interactive anonymisation;
- privacy-safe terminal rendering;
- approved archive-aware destination inference;
- safe atomic no-overwrite publication and temporary-file cleanup;
- FITS integrity and source preservation; and
- reuse of the completed ENH-005c.1 processing foundation.

The reviewed validation evidence records:

- 15 focused tests passed;
- 79 relevant regression tests passed;
- Ruff lint passed;
- Ruff formatting passed; and
- `git diff --check` passed.

The full application suite was intentionally not run. The implementation commit is `f347677`, and its Git push to `origin/enh/ENH-005-fits-privacy-processing` was confirmed.

## 9. Resolved technical clarifications

The nine technical clarifications previously open for ENH-005c are resolved by C06–C14. Those decisions did not, by themselves, authorise implementation changes; the separate implementation authorisation in this amendment is limited to ENH-005c.3.

1. **Long strings and `HIERARCH` (C06):** Support valid forms when complete logical keywords and values are safely interpretable and classifiable; reject unsupported encodings safely.
2. **Header rewriting and block alignment (C07):** Header growth is permitted, provided data blocks remain byte-for-byte preserved, FITS 2880-byte alignment and HDU ordering remain valid, and data relocation is allowed when required.
3. **Checksums (C08):** Reject invalid existing `CHECKSUM` or `DATASUM`; preserve valid `DATASUM` where data is unchanged; recalculate valid existing `CHECKSUM` when header changes require it; do not add absent checksum keywords.
4. **Compressed images and binary tables (C09):** Support valid structures only where header processing and exact data-byte preservation are guaranteed; otherwise reject safely without decoding, rescaling, recompressing, or rewriting astronomical data blocks.
5. **Malformed and unsupported FITS (C10):** Treat these as privacy-safe operational errors with exit code `1`, distinct from PASS, FAIL, and REVIEW REQUIRED.
6. **Safe A/P/Q terminal rendering (C11):** Escape control characters, neutralise terminal control sequences, truncate excessively long displayed values, and keep sensitive values out of logs, errors, and non-interactive warnings. The local A/P/Q prompt remains the limited, safely rendered exception.
7. **Intentional P decisions (C12):** Do not add a marker or history record. Every remaining unknown value is REVIEW REQUIRED in verification; P applies only to its occurrence during the scrub operation.
8. **Archive FITS-output layout (C13):** Use `observation_NN/pii-scrubbed/` directly for recognised archive lights and stacked FITS, retain the original filename, and do not create type-specific subdirectories. Ordinary inputs use `INPUT_PARENT/pii-scrubbed/`.
9. **Temporary publication semantics (C14):** Create the temporary output beside the final destination on the same filesystem, validate it before atomic no-overwrite publication, clean it after failure or cancellation, and reject any operation for which those guarantees cannot be made.

No genuine implementation-blocking ambiguity remains in these resolved areas. Capability boundaries remain deliberately conservative: where safe interpretation, exact data preservation, or safe publication cannot be guaranteed, the input or operation must be rejected as specified.

## 10. Stage boundaries

### ENH-005a — Metadata reconnaissance — COMPLETE

Read-only reconnaissance was completed on the recorded baseline. It inventoried relevant production, utility, test, and metadata evidence; no implementation occurred.

### ENH-005b — Shared policy and `header-report` — COMPLETE

ENH-005b.1 and ENH-005b.2 are formally complete. A1, A2, B1, B2, C1, D1, and D2 are approved. The implementation, focused validation, acceptance evidence, and closure rationale are retained in §§8.3–8.6. Later stages remain separately authorised and scoped.

#### ENH-005b.1 — Limited `header-report` implementation — COMPLETE

The limited implementation reads FITS headers without loading pixel arrays; generates privacy-processed text reports; preserves header card order, duplicates, and HDU boundaries; implements the agreed metadata classification and safe report output; provides the post-generation menu; and permits the temporary development-only `--noscrub` comparison exception in §3.1.1. Its implementation and focused validation are formally closed; the evidence and basis for approval are recorded in §8.4.

It does not implement `pii-scrub`, FITS rewriting, or `--verify`. The temporary `--noscrub` exception remains development-only and must be removed in ENH-005d.

The focused validation completed for ENH-005b.1 was limited to its implemented `header-report` scope and demonstrated:

- source/destination equivalence is rejected, including equivalent spellings and resolved-path aliases;
- every approved sensitive replacement type and keyword is represented correctly, while approved safe values, withheld unknown values, descriptions, `COMMENT`, and `HISTORY` follow §§4.1–4.5;
- header-only access for every HDU, with no image-array loading;
- CLI option placement, exit status, and TTY-only View / Finder / Quit menu behaviour, including `--noprompt`;
- viewer and Finder launch failures are warnings after successful publication and do not alter success;
- the temporary `--noscrub` path retains its distinguishable filename, privacy warning, header-only operation, and all ordinary safe-output safeguards;
- default report-destination selection and filename policy follow §5, including recognised canonical archive lights and stacked FITS, ordinary directories, rejected archive-like inputs, ENH-004-equivalent symlink/path-escape rejection, direct `pii-scrubbed/` report placement without a `reports/` directory, no-overwrite exit code `1`, and no automatic suffixes; and
- atomic-publication failure paths leave neither a completed nor a partial destination and preserve the source.

The validation must remain proportional: it need not test future FITS rewriting or verification behaviour. The ENH-005b.1 stacked-input work must remain confined to the D1-approved narrowly scoped extension; it must not modify ENH-004 or expand archive recognition beyond that decision.

#### ENH-005b.2 — Representative report review — COMPLETE

The real-world corrected S50 and S50 Pro report review passed. It confirms the approved B1 and B2 refinements in §§4.4, 4.5, and 8.3, and the user approved A1 and A2 after reviewing the representative reports recorded in §8.3. Formal closure evidence and rationale are recorded in §8.5.

#### ENH-005b validation and closure — COMPLETE

Overall ENH-005b closure evidence and rationale are recorded in §8.6. This closure is confined to the completed shared-policy and `header-report` scope; it does not authorise later-stage implementation.

### ENH-005c — FITS processing and verification — IN PROGRESS

Approved design scope: `pii-scrub`, occurrence-level A/P/Q review, non-interactive anonymisation, safe FITS writing, independent verification, integrity validation, and focused tests. The §9 technical clarifications are resolved. ENH-005c.1 and ENH-005c.2 are complete. Implementation authorisation is currently limited to ENH-005c.3 as defined below.

#### ENH-005c.1 — FITS processing foundation — COMPLETE

ENH-005c.1 implemented and validated the following internal FITS processing foundation required by later stages:

- internal inspection of every HDU, supported FITS structures, valid `HIERARCH` and `CONTINUE` metadata, and conservative rejection of malformed or unsupported inputs;
- safe header transformation using the approved privacy policy, including type-preserving sensitive replacements, recognised-safe technical metadata, descriptions, standalone `COMMENT` and `HISTORY`, duplicate occurrences, and internal unknown-metadata handling without A/P/Q prompts;
- header-only transformation with byte-for-byte preservation of every supported HDU data block, valid 2880-byte alignment, preserved HDU order and structural metadata, and permitted header growth;
- validation and handling of existing `CHECKSUM` and `DATASUM` under C08, without introducing absent checksum keywords; and
- internal output validation and focused tests covering the authorised foundation.

Its formal closure evidence, conservative unsupported-FITS boundaries, and focused-validation limits are recorded in §8.8. It did not include `pii-scrub` CLI integration, `pii-scrub --verify`, interactive A/P/Q prompts, archive destination inference, or final publication workflow.

#### ENH-005c.2 — CLI privacy-processing integration — COMPLETE

ENH-005c.2 implemented and focus-validated the standalone `pii-scrub` command using the ENH-005c.1 processing foundation:

- accept a single FITS input and follow the approved CLI option and exit-code conventions;
- implement occurrence-level interactive A/P/Q decisions, safe terminal metadata rendering, approved cancellation behaviour, and explicit warnings when unknown metadata is intentionally preserved;
- detect non-TTY input or output, anonymise unresolved unknown metadata without prompting, and emit warnings that do not disclose sensitive original values;
- infer default destinations using the approved archive-aware recognition for canonical archive lights and stacks, use the direct `pii-scrubbed/` layout, support ordinary FITS inputs and exact `--output` filenames, and preserve original FITS filenames by default;
- never modify the input, never overwrite an existing destination, reject source/destination equivalence, apply approved symlink and path-safety rules, write temporary output beside the destination, validate before atomic no-overwrite publication, and remove temporary output after failure or cancellation; and
- add focused tests for CLI arguments and exit codes, interactive A/P/Q occurrences, non-interactive behaviour, archive and ordinary destinations, collisions and path safety, cancellation and cleanup, and existing header-report regressions.

Its formal closure evidence and reviewed validation results are recorded in §8.9. It did not include `pii-scrub --verify`, user-facing PASS/FAIL/REVIEW REQUIRED verification behaviour, ENH-005c.3, ENH-005d integration or documentation work, removal of temporary `header-report --noscrub`, changes to `archive`, `convert`, or `convert-batch`, or batch or recursive `pii-scrub` processing.

#### ENH-005c.3 — Independent verification — IN PROGRESS

ENH-005c.3 is explicitly authorised to implement and focus-validate only `seestar-toolkit pii-scrub --verify [OPTIONS] INPUT` using the completed ENH-005c.1 and ENH-005c.2 foundations:

- operate read-only on one FITS input per invocation, without prompts or pixel-array loading, and inspect every HDU header using the approved shared privacy policy;
- report PASS when there is no recognised privacy-policy violation and no unresolved unknown metadata; report FAIL for a confirmed privacy-policy violation; and report REVIEW REQUIRED when unknown metadata remains outside the approved recognised-safe policy, including a value previously preserved during `pii-scrub`;
- treat malformed or unsupported FITS inputs as privacy-safe operational errors rather than privacy classifications;
- return exit code `0` for PASS, `1` for FAIL, REVIEW REQUIRED, and operational failure, and `2` for invalid CLI usage;
- display the verification status in the terminal and support an optional `--output` text report, reporting only safe keyword names and counts and never original sensitive values;
- apply the existing safe-output rules to the optional report and never modify the source FITS; and
- add focused tests for PASS, FAIL, and REVIEW REQUIRED; sensitive and unknown metadata detection; preserved unknown followed by verification; multi-HDU and duplicate-card coverage; descriptions and `COMMENT`/`HISTORY` policy; malformed and unsupported FITS handling; output-report safety and no-overwrite; exit codes and CLI option placement; source preservation; and existing ENH-005 regressions.

This authorisation excludes ENH-005d integration or documentation work, removal of temporary `header-report --noscrub`, batch or recursive processing, changes to `archive`, `convert`, or `convert-batch`, unrelated refactoring, and new features outside this verification scope.

#### ENH-005c acceptance criteria — APPROVED DESIGN REQUIREMENTS

The following criteria are approved testable requirements for ENH-005c. ENH-005c.1 and ENH-005c.2 are complete. ENH-005c.3 is authorised only for the applicable independent-verification, safe-output, source-preservation, and focused-validation portions:

1. **C01:** A scrubbed output modifies eligible FITS headers only; for every supported HDU, its astronomical data block is byte-for-byte identical to the source, HDU order is preserved, and the source file is unchanged.
2. **C02:** Every header card in every supported HDU is evaluated under §4, including duplicates and additional HDUs. Recognised sensitive metadata is replaced with the approved type-preserving value, recognised safe metadata is preserved, and unknown metadata receives the C03 handling; structures that cannot be safely processed are rejected without partial publication.
3. **C03:** Interactive operation prompts separately for each unknown metadata occurrence, including identical keyword/value pairs and occurrences in separate HDUs. Each safely rendered prompt presents keyword, current value, and proposed replacement; A affects only that occurrence, P affects only that occurrence, and Q returns without a published output or remaining temporary file.
4. **C04:** `--verify` reports PASS/0 only for a compliant file with no unresolved unknown metadata; it reports FAIL/1 for a confirmed policy violation and REVIEW REQUIRED/1 for an unknown value. Invalid CLI usage returns 2, and output does not disclose sensitive originals.
5. **C05:** Default destinations use established archive-aware recognition and path-safety rules for recognised archive inputs and `INPUT_PARENT/pii-scrubbed/` for ordinary inputs; the output retains the original FITS filename. Exact `--output` destinations are supported, and an archive path-safety failure is rejected rather than treated as ordinary fallback.
6. **C06:** Valid `HIERARCH` keywords and `CONTINUE` long-string metadata with safely interpretable complete logical keywords and values are classified under §4. Unsupported encodings are rejected safely.
7. **C07:** Header-size changes preserve each data block byte-for-byte, retain valid 2880-byte FITS block alignment and HDU ordering, and permit data relocation when header growth requires it.
8. **C08:** Inputs with invalid existing `CHECKSUM` or `DATASUM` are rejected without silent repair. Valid existing `CHECKSUM` values are recalculated when header changes require it; valid existing `DATASUM` values remain valid when data is unchanged; neither keyword is introduced when absent.
9. **C09:** Valid compressed-image and binary-table structures are processed only where header processing and exact data-byte preservation can be guaranteed; their astronomical data blocks are not decoded, rescaled, recompressed, or rewritten. Unsupported structures are rejected safely.
10. **C10:** Malformed or unsupported FITS inputs result in a privacy-safe operational diagnostic and exit code 1, never PASS, FAIL, or REVIEW REQUIRED.
11. **C11:** Terminal rendering escapes control characters, neutralises terminal escape/control sequences, truncates excessively long displayed metadata values, and does not disclose sensitive values in logs, errors, or non-interactive warnings.
12. **C12:** All remaining unknown metadata values produce REVIEW REQUIRED during verification. No tracking marker or processing-history record is introduced, and an interactive P decision applies only to that occurrence in that scrub operation.
13. **C13:** Recognised archive light and stacked FITS outputs are written directly to `observation_NN/pii-scrubbed/`, without type-specific subdirectories or automatic filename changes. Ordinary outputs use `INPUT_PARENT/pii-scrubbed/`; filename collisions are refused by the no-overwrite rule.
14. **C14:** Temporary output is created beside the intended final destination on the same filesystem, validated before atomic no-overwrite publication, and removed after failure or cancellation. An operation lacking those safe-publication guarantees is rejected.
15. Focused tests cover every criterion above, including byte-level data comparisons for each supported HDU, repeated unknown occurrences, non-interactive behaviour, P followed by verification, checksums, destination safety, cancellation, temporary-file cleanup, safe terminal rendering, operational-error handling, and every approved unusual-structure capability boundary.

### ENH-005d — Integration, regression, and documentation — NOT STARTED

Proposed scope: approved end-to-end validation, CLI/help review, documentation, compatibility review, removal of the temporary `header-report --noscrub` option, and formal ENH-005 closure evidence. Production release is blocked until that option is removed. Commit, push, and merge remain separate explicit actions.

## 11. Approval gate

ENH-005c.1 and ENH-005c.2 are complete. ENH-005c.3 is explicitly authorised by this amendment and is **IN PROGRESS**, limited to the scope defined in §10. Before any remaining or subsequent implementation, review this specification with the user, mark the relevant scope approved, and explicitly authorise the relevant sub-stage or stage. A1, A2, B1, B2, C1, D1, D2, and C01–C14 remain approved design decisions; those decisions do not independently authorise work beyond ENH-005c.3. ENH-005d remains **NOT STARTED** and unauthorised.
