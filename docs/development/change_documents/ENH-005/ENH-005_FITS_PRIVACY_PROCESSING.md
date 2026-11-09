# ENH-005 — FITS Privacy Processing

**Document status:** DRAFT — AUTHORITATIVE SPECIFICATION
**Document role:** Controlling ENH-005 specification and recorded closure evidence
**Repository path:** `docs/development/change_documents/ENH-005/ENH-005_FITS_PRIVACY_PROCESSING.md`
**Baseline reviewed:** `main` / `origin/main` at `ebcf02ae09b0c2344598cda6b12b9da920abad8e`
**Scope:** Standalone FITS header reporting, privacy processing, and verification
**Version:** Draft 1.0 — 2026-11-09

> **Implementation authorisation:** No further implementation is authorised by this amendment. It records the agreed functional and privacy-policy design, acceptance evidence, and formal closure of ENH-005b.1, ENH-005b.2, and overall ENH-005b. ENH-005c and ENH-005d remain **NOT STARTED**. The temporary development-only `--noscrub` exception remains subject to its mandatory removal during ENH-005d. This amendment does not authorise implementation, branch creation, commit, push, or merge.

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
- `0` means successful operation or PASS verification; `1` means operational failure, FAIL verification, or REVIEW REQUIRED verification; `2` means CLI argument or usage error.

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
- An interactive invocation presents A/P/Q review for each unique keyword/value combination that remains unknown or potentially sensitive: **(A)nonymise**, **(P)reserve**, or **(Q)uit**. The decision is reused only for an identical combination during that invocation. Empty input is not approval to preserve; decisions are not persisted.
- A preserved unknown value makes the output **REVIEW REQUIRED**. The file may still be created and the scrub operation returns `0` with an explicit warning.
- When either stdin or stdout is not a TTY, the command is non-interactive: it anonymises unresolved unknown metadata, emits warnings without original values, and does not prompt.
- On quit or failure, it publishes no incomplete output file.

### 3.3 `pii-scrub --verify`

`pii-scrub --verify` is read-only and non-interactive. It reads headers without loading pixel arrays or requesting decisions.

- It reports PASS, FAIL, or REVIEW REQUIRED to the terminal by default.
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

Future scrubbed FITS outputs may use separate `lights/` and `seestar_stacked/` directories within `pii-scrubbed/`. Those directories are not part of the ENH-005b `header-report` implementation. The later `pii-scrub` destination classification must distinguish recognised archive lights and recognised archive stacked FITS using the applicable rules above; this does not authorise implementation of `pii-scrub`.

The implementation must apply ENH-004's path-safety requirements before accepting an archive default: reject unsafe dangling symlinks; resolve the observation, applicable canonical source directory, source, and inferred destination; and reject any resolved path that escapes the recognised observation. It must never turn a path-safety failure into ordinary-input fallback. Existing destination safety remains unchanged: never overwrite an existing destination; reject source/destination equivalence; create output directories only when required; publish atomically so failure or quit leaves no incomplete output; and avoid raw sensitive values in logs, exception messages, summaries, and generated filenames.

## 6. FITS integrity requirements

### FITS-1 — Data preservation

Image and other data bytes must be preserved exactly. `pii-scrub` must never decode, rescale, recompress, or otherwise change image data, and must not modify pixel-related technical metadata.

### FITS-2 — HDU and header preservation

Preserve all HDUs, their order, and their data. Inspect every HDU header. Modify only eligible privacy-related header values and comments; do not alter structural metadata.

### FITS-3 — Checksum handling

Do not introduce `CHECKSUM` or `DATASUM` keywords. Preserve valid existing `DATASUM` values when underlying data is unchanged. Update an existing `CHECKSUM` where required, without changing image data to satisfy checksum handling.

If safe rewriting or integrity preservation cannot be guaranteed, issue a clear warning and produce no completed output file.

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
| D14 | AGREED | Interactive unknown-keyword review uses A/P/Q. |
| D15 | SUPERSEDED by B2 | The earlier shared-review treatment for free text and comments is replaced by the explicit description and standalone-comment policy in §4.4. |
| D16 | AGREED | Reuse one decision for an identical keyword/value combination only within one run. |
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

No unresolved defect or material ambiguity affects the completed ENH-005b `header-report` scope. The remaining technical clarifications in §9 are retained for subsequent implementation and validation stages; they do not reopen the completed ENH-005b scope. ENH-005c and ENH-005d remain not started and their boundaries are unchanged. The temporary development-only `--noscrub` option remains prohibited from production release and must be removed during ENH-005d.

## 9. Outstanding technical clarifications

The following are explicitly open for user review; they do not authorise implementation changes.

1. Handling of long strings, `HIERARCH` keywords, and keyword names that may themselves be sensitive remains to be specified for subsequent implementation and validation stages.
2. D1 refines C1 for header reports by approving the narrowly scoped ENH-005 canonical-stacked recognition extension and direct `pii-scrubbed/` report destination. D2 fixes default report filenames and collision handling. No additional ordinary-directory fallback location ambiguity is known: the existing ordinary-directory principle resolves reports to the input parent directory's `pii-scrubbed/`. Any later case in which that exact ordinary fallback cannot be determined must be recorded as a clarification rather than used to invent a destination rule.
3. Detailed handling of malformed/nonstandard HDUs, compressed FITS, scaling, binary-table metadata, and individual cards that cannot safely be rewritten while meeting §6.
4. Exact implementation mechanism for updating existing `CHECKSUM` values while preserving valid `DATASUM` and data bytes.
5. Safe terminal rendering of hostile header values during interactive A/P/Q review.

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

### ENH-005c — FITS processing and verification — NOT STARTED

Proposed scope: `pii-scrub`, A/P/Q review, non-interactive defaults, safe FITS writing, independent verification, integrity validation, and focused tests.

### ENH-005d — Integration, regression, and documentation — NOT STARTED

Proposed scope: approved end-to-end validation, CLI/help review, documentation, compatibility review, removal of the temporary `header-report --noscrub` option, and formal ENH-005 closure evidence. Production release is blocked until that option is removed. Commit, push, and merge remain separate explicit actions.

## 11. Approval gate

Before any remaining or subsequent implementation, resolve the §9 clarifications that materially affect that work, review this specification with the user, mark the relevant scope approved, and explicitly authorise the relevant stage. A1, A2, B1, B2, C1, D1, and D2 are approved; ENH-005b is complete, while ENH-005c and ENH-005d remain separate future-stage gates. This draft does not authorise further implementation.
