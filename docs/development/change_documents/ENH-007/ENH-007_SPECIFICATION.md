# ENH-007 — Telescope Identity and Archive Hierarchy

**Status:** APPROVED

**Specification revision:** Draft 2.3 — administrative stage-status correction
following the D08 historical target-identification amendment (18 November 2026)

**Status record reconciled:** 20 November 2026; approved behaviour unchanged

**Formal closure:** APPROVED — 20 November 2026; Checkpoint 6C PASS;
accepted feature-branch commit `4b61259`

**Specification date:** 17 November 2026

**Repository baseline:** `cidermark/seestar-toolkit`, `main`,
`4c487016fc534b4e9237154e60d686db94bb7665`

**Approval and authorisation:** The user formally approved Draft 2 on
18 November 2026. ENH-007c completed and was committed as `9ef8e61`.
ENH-007d completed at `696e32d`. The coordinator accepted ENH-007e as complete
following the Checkpoint 5F final acceptance review. Formal ENH-007 closure was
approved on 20 November 2026 following the Checkpoint 6C PASS review, accepting
feature-branch commit `4b61259`. The formal closure-record commit remains
pending. Git operations remain under user control. Archive reorganisation
remains excluded.

The user approved the D08 specification amendment on 18 November 2026. Its
implementation correction was delivered in `696e32d` and accepted with the
ENH-007d and ENH-007e evidence. This administrative reconciliation does not
alter the approved Draft 2.3 behaviour.

## 1. Objective and motivation

ENH-007 introduces an optional `{telescope}` archive-hierarchy component for
the recognised *individual* Seestar telescope that produced an observation.
It enables layouts such as:

```text
{target}/{location}/{session_end_date}/{telescope}
```

For recognised devices, the component distinguishes both telescope model and
device identifier, for example:

```text
S50_A1B2C3D4
S50_Pro_EDFE7FB2
```

This is prospective archive planning behaviour. It does not reorganise,
rename, infer, or otherwise mutate existing archives. Archive reorganisation
remains outside ENH-007 and is relevant to future ENH-008 work.

## 2. Verified current behaviour

The current default hierarchy is:

```text
{target}/{location}/{session_end_date}
```

It is configured by `archive.hierarchy`. Current validation accepts only the
three tokens above, requires each exactly once, and permits alternative order.
Planning appends a numbered `observation_NN` directory under the resolved
hierarchy directory.

Archive reconstruction recognises complete, case-insensitive `TELESCOP`
identities in these forms:

```text
S50_[0-9a-f]{8}
S50 Pro_[0-9a-f]{8}
```

The model is part of the identity. Thus an S50 and S50 Pro with the same
hexadecimal suffix are different identities. Missing, generic, malformed and
unsupported telescope values produce no recognised identity and retain the
established conservative grouping behaviour.

Reconstruction already prevents different recognised identities from
associating, but it retains telescope metadata through member FITS inspections
rather than exposing a resolved observation-level identity. Archive planning
currently retains the first non-null raw `TELESCOP` value for reporting only;
it is not a hierarchy component.

`convert` and `convert-batch` recognise an archive structurally from the
canonical `observation_NN/fits_images/lights` layout and do not require a
fixed number or order of hierarchy ancestors. Archive indexing maps configured
hierarchy tokens to concrete directory components and therefore must be
updated for any new token.

## 3. Scope

### 3.1 Included

1. An optional `{telescope}` hierarchy component.
2. Observation-level resolution of already recognised telescope identities
   after reconstruction.
3. Telescope-component directory normalisation.
4. Hierarchy validation that preserves existing valid configurations while
   allowing any non-empty, non-duplicated ordering of supported components.
5. Compatible planning, observation numbering, incremental reconciliation,
   indexing, dry-run display and conversion-recognition behaviour.
6. Focused and regression validation of the established archive contracts
   affected by the new component.
7. The D08-limited use of an existing archive-root `INDEX.md` to preserve an
   otherwise unrecoverable historical logical target in a target-free hierarchy.

### 3.2 Excluded

- Changes to FITS classification, conversion, image processing or FITS
  metadata.
- Changes to telescope recognition formats, including S30 or S30 Pro support.
- Changes to observation reconstruction or metadata-assisted grouping based on
  focal length, gain, focus, dimensions, pixel characteristics, or other
  supporting metadata.
- Inventing an individual identity from model-level metadata or a friendly
  name.
- Automatic changes to the default hierarchy or existing saved hierarchy
  configurations.
- Archive reorganisation, migration, repair, or inference of hierarchy tokens
  from existing archive paths.
- Changes to source copy/move semantics, collision policy, observing-night
  date policy, TIFF conversion policy, or archive-aware conversion layout.
- General-purpose index parsing, regeneration or repair commands. D08 permits
  only the narrowly defined historical-target fallback in Section 5.6.
- Unrelated refactoring or documentation changes outside an authorised later
  stage.

## 4. Decision register

| ID | Status | Decision |
|---|---|---|
| D01 | AGREED | `{telescope}` represents a recognised individual telescope identity, including model and device identifier. It is never merely a model or friendly name. |
| D02 | AGREED | All hierarchy components are optional. A hierarchy contains at least one supported component; no component may repeat; supported components may appear in any order. Supported components are `{target}`, `{location}`, `{session_end_date}`, and `{telescope}`. Existing valid configurations remain valid. When configured, `{telescope}` resolves to `unidentified` for an observation without a recognised identity. When absent, existing destination behaviour is preserved. |
| D03 | AGREED | Telescope directory names preserve model and identifier, use consistent capitalisation, and replace spaces with underscores: `S50_A1B2C3D4` and `S50_Pro_EDFE7FB2`. Existing path-safety requirements remain applicable. FITS metadata is not modified. |
| D04 | AGREED | Reconstruction behaviour remains unchanged. Resolve telescope identity after reconstruction by inspecting every member light and stack. Adopt an identity only if all recognised identities agree; missing or malformed member values do not prevent adoption. No recognised value means unidentified. Conflicting recognised values are reconstruction-integrity errors: they are reported, not silently selected or treated as unidentified, and the affected observation is not archived. No additional metadata-based grouping is introduced. |
| D05 | AGREED | The default remains `{target}/{location}/{session_end_date}`. `{telescope}` is not automatically added to existing configurations. |
| D06 | AGREED | Preserve `observation_NN`. Number observations independently within each resolved hierarchy directory, permitting multiple observations from one telescope and independent numbering across telescope directories. Preserve incremental archive compatibility. |
| D07 | AGREED | Preserve established behaviour for dry-run, optional light-TIFF conversion, single and batch conversion, indexing, incremental reconciliation, collisions, and copy/move. `{telescope}` works in any hierarchy position and implementation must not assume fixed hierarchy depth. |
| D08 | AGREED | For a target-free hierarchy only, an archive-root `INDEX.md` records each observation's resolved logical target and exact relative archive-observation path. During root-index regeneration, that existing index may be read as a last-resort historical-target fallback when established evidence cannot identify the target. It must never override reliable FITS, reconstruction, or source-directory evidence. No sidecar is introduced. Missing, unreadable, malformed, ambiguous or inconsistent required fallback evidence prevents publication of the affected root index, preserves existing archive and index content, reports a diagnostic, and makes the archive operation exit `1`. |

### Supporting design evidence

The user has reported ZWO-confirmed focal lengths:

| Model | Focal length |
|---|---:|
| S50 Pro | 260 mm |
| S50 | 250 mm |
| S30 Pro | 160 mm |
| S30 | 150 mm |

This evidence can distinguish models, not individual physical telescopes. It
does not alter D01 or D04, authorise model inference, or extend support to S30
or S30 Pro.

## 5. Functional requirements

### 5.1 Supported hierarchy syntax

The hierarchy grammar shall support these component tokens:

```text
{target}
{location}
{session_end_date}
{telescope}
```

A valid hierarchy must:

1. be a relative slash-separated path;
2. contain one or more components;
3. use exactly one supported token in each component, with no literal prefix,
   suffix, formatting expression, conversion, or combined token;
4. contain no repeated token;
5. contain no empty, `.` or `..` component, backslash, or absolute path form;
6. remain subject to archive-root containment checks after values are resolved.

Existing three-token hierarchies are valid. Examples of valid configurations
include:

```text
{target}
{telescope}/{target}
{target}/{location}/{session_end_date}
{location}/{session_end_date}/{target}/{telescope}
```

For example, `{telescope}/{object}` is invalid because `{object}` is not a
supported token.

### 5.2 Telescope identity resolution

For every reconstructed observation, identity resolution shall inspect its
member light FITS and optional stack FITS, using the existing recognised S50
and S50 Pro identity rules.

- If the set of recognised identities is exactly one value, that value is the
  resolved observation identity.
- Missing, generic, malformed and unsupported `TELESCOP` values contribute no
  identity and do not override a unanimous recognised value.
- If the recognised set is empty, the observation is unresolved as
  `unidentified` for hierarchy-component purposes.
- If the recognised set has more than one value, it is an internal
  reconstruction-integrity error. The implementation shall report the affected
  observation and every conflicting recognised identity, skip that observation,
  and shall not choose an identity by member ordering, model, raw text, focal
  length, gain, focus, image dimensions, or any other inferred property.

Identity resolution occurs only after the existing reconstruction result is
available. It must not introduce a second grouping pass, change membership,
attempt automatic regrouping, or otherwise correct a conflict.

The implementation shall preserve the raw FITS telescope value for existing
reporting/index metadata where that contract currently applies. A resolved
identity used for a hierarchy component is a separate derived value.

### 5.3 Telescope component formatting

For a resolved recognised identity, the component shall use a canonical display
form with:

- `S50` capitalised;
- `Pro` capitalised when present;
- an uppercase eight-character hexadecimal device identifier; and
- underscores in place of spaces.

Thus the current recognised forms map as follows:

| Recognised identity | `{telescope}` component |
|---|---|
| `S50_a1b2c3d4` | `S50_A1B2C3D4` |
| `S50 Pro_edfe7fb2` | `S50_Pro_EDFE7FB2` |
| no recognised identity | `unidentified` |

The component must additionally use the established traversal-safe archive
component handling. This formatting is limited to generated directory names;
it must not rewrite FITS headers or other stored metadata.

### 5.4 Planning, numbering and reconciliation

Planning shall make the resolved telescope component available only when
`{telescope}` occurs in the configured hierarchy. A hierarchy without that
token retains its existing destination behaviour.

An observation with a conflicting recognised-identity integrity error is not
planned, numbered, reconciled, copied, moved, converted, or indexed. Valid
unrelated observations continue through the established preparation and
execution flow where safe.

Observation numbering shall continue to be chronological and deterministic
within the fully resolved hierarchy directory. Consequently, when telescope is
configured, each telescope directory receives its own `observation_01`,
`observation_02`, and so on. Width expansion above 99 observations remains
unchanged.

Incremental reconciliation shall stay confined to the resolved hierarchy
directory. It must retain its existing recognised-identity safeguards when
reusing archived observations and must not reuse an observation across distinct
telescope hierarchy directories.

### 5.5 Operational compatibility

- `archive --dry-run` must display the effective hierarchy and the same
  resolved destinations a real run would use, without filesystem mutation.
- `archive --convert-lights` must retain its established archived-FITS and
  TIFF-destination behaviour under any valid hierarchy depth.
- `convert` and `convert-batch` archive recognition must continue to use the
  canonical observation-internal layout and must not require a fixed hierarchy
  ancestor depth or order.
- For a hierarchy containing `{target}`, archive indexes must correctly locate
  that component, parse every configured supported token, and continue to
  produce target-level indexes under valid alternative orderings. `{target}`
  need not be first; `{telescope}` may precede or follow it.
- For a hierarchy without `{target}`, archive indexes must be generated at the
  archive root. Index records must retain each observation's target from
  observation metadata and a stable identifier formed from the observation's
  relative archive path; the implementation must not create artificial target
  directories.
- Copy/move source actions, planned-file collision detection, filesystem
  collision policy, and source-preservation guarantees remain unchanged.

### 5.6 Limited historical target retention for target-free indexes

For a hierarchy omitting `{target}`, each archive-root index record shall retain
the resolved logical target and an exact, stable observation identifier based on
the POSIX relative path from the archive root through `observation_NN`. The
identifier must distinguish, for example, separate `observation_01` directories
under different resolved hierarchy directories. The index remains
human-readable Markdown.

Target identification retains its established precedence. FITS metadata,
reconstruction metadata and source-directory evidence remain the normal
sources; a reliably identified target must not be replaced by stale index
information. For a historical observation absent from the current plan, when
the established available evidence cannot identify its target, the existing
archive-root `INDEX.md` may be read solely to recover a target from an exact,
unambiguous matching observation identifier.

This is a limited exception to the established rule that indexes are derived
artifacts rather than archive metadata. It does not authorise a general-purpose
index parser, regeneration or repair command, an observation metadata sidecar,
or recovery outside target-free root-index generation. Independent index
regeneration and recovery remain deferred to ENH-008.

A missing `INDEX.md` is not itself an error where the target remains
recoverable through established evidence. If required historical target recovery
cannot proceed because the index is missing, unreadable, malformed, ambiguous,
inconsistent or lacks an exact matching identifier, the archive-root index
publication is the affected operation: it must be safely aborted, leave existing
archive files and index content unchanged, and emit a clear diagnostic naming
the observation identifier and recovery failure. Other independently safe
archive placement work may continue, but the command returns exit status `1`.
The implementation must not silently replace such a previously known target
with `unknown`.

## 6. Error, diagnostic and safety behaviour

Invalid hierarchy templates must be rejected before archive execution and must
identify the invalid token, repetition, omission, unsafe path shape, or other
applicable validation failure without creating archive content.

An absent recognised identity is normal and maps to `unidentified` only where
`{telescope}` is configured. It must not cause an invented identity or a change
to a hierarchy that lacks `{telescope}`.

Conflicting recognised identities in one reconstructed observation are internal
reconstruction-integrity errors. Diagnostics must identify the affected
observation, display the conflicting recognised identities, and clearly state
that the observation was skipped. The system must not select an identity, treat
the conflict as `unidentified`, regroup members, or attempt recovery.

Archive processing must continue with unrelated valid observations where safe,
but the archive command returns exit code `1` if any reconstruction-integrity
error occurs. `archive --dry-run` reports the same integrity error and skipped
observation policy, returns exit code `1`, and retains its existing guarantee
of zero filesystem mutation. No new reporting mode or recovery option is
introduced.

All existing safeguards remain in force, including absolute archive-root
requirements, resolved containment beneath the archive root, avoidance of
traversal, safe symlink handling, established collision policy, and dry-run
non-mutation.

## 7. Backward compatibility

1. The built-in default remains unchanged.
2. Existing valid hierarchy configurations, including any ordering of the
   original three tokens, remain valid and retain their destinations.
3. Saved configurations are not rewritten automatically.
4. A user opts into telescope-specific placement only by configuring
   `{telescope}`.
5. Existing archive recognition remains structural beneath `observation_NN`;
   no existing archive is required to acquire a telescope ancestor.
6. Existing raw telescope reporting remains raw metadata rather than a claim
   of resolved identity.
7. ENH-007 performs no existing-archive migration. A later archive
   reorganisation enhancement must independently handle recovery of identity
   from archived FITS and unknown/conflicting evidence.
8. Existing target-containing hierarchies retain target-level index placement.
   Archive-root indexes apply only to newly permitted configurations that omit
   `{target}`; no artificial target directory is added.
9. D08 is a deliberately narrow compatibility exception: a target-free
   archive-root index may be consulted only for exact historical target recovery
   under Section 5.6. Target-containing hierarchy behaviour remains unchanged.

## 8. Acceptance criteria

| ID | Criterion |
|---|---|
| E007-01 | The default hierarchy remains `{target}/{location}/{session_end_date}`. |
| E007-02 | Existing valid three-token hierarchies remain valid and retain their existing resolved destinations. |
| E007-03 | Every non-empty ordering of unique supported components is accepted, including `{telescope}` alone and four-component forms. |
| E007-04 | Empty, duplicate, unsupported, combined, malformed, absolute and traversal-containing templates are rejected. |
| E007-05 | A recognised S50 identity produces the canonical individual telescope component. |
| E007-06 | A recognised S50 Pro identity produces the canonical model-preserving component. |
| E007-07 | Missing, generic or malformed identity produces `unidentified` only when `{telescope}` is configured. |
| E007-08 | A unanimous recognised identity is adopted even when other observation members lack recognised identity. |
| E007-09 | Conflicting recognised identities are reconstruction-integrity errors, are diagnosed with the affected observation and all conflicting recognised values, and are never resolved by arbitrary member selection or metadata inference. |
| E007-10 | An observation with a recognised-identity integrity error is skipped, never treated as unidentified, and is not planned, archived, converted, reconciled, or indexed. |
| E007-11 | Unrelated valid observations continue where safe when an integrity error occurs, and the archive command returns exit code `1`. |
| E007-12 | Dry-run reports equivalent integrity diagnostics and skipped-observation behaviour, returns exit code `1`, and creates or changes no filesystem state. |
| E007-13 | Reconstruction membership and the recognised-identity compatibility rules remain unchanged. |
| E007-14 | Numbering is independent for distinct resolved hierarchy directories and remains deterministic for multiple observations from one telescope. |
| E007-15 | Incremental reconciliation preserves recognised-device safeguards and does not cross telescope hierarchy directories. |
| E007-16 | Dry-run, light-TIFF conversion, copy/move and collision behaviour remain compatible under telescope-enabled hierarchy configurations. |
| E007-17 | Single-file and batch archive-aware conversion work under telescope-enabled hierarchies without a fixed-depth dependency. |
| E007-18 | For configurations containing `{target}`, archive index generation works with `{telescope}` before or after `{target}` and remains target-level. |
| E007-19 | For configurations without `{target}`, archive index generation writes at the archive root, records every observation's resolved logical target and exact relative archive-observation identifier, and creates no artificial target directory. For a historical observation absent from the current plan whose established evidence cannot identify its target, an existing root index is used only as the Section 5.6 exact, unambiguous, last-resort fallback. Required fallback recovery failure preserves existing archive and index content, emits a diagnostic, and returns exit status `1`; no known target is silently replaced with `unknown`. |
| E007-20 | No FITS metadata, source file, or existing archive is rewritten solely because of ENH-007. |
| E007-21 | Focused regressions, the complete test suite, Ruff, and whitespace checks pass at the authorised validation gate. |

## 9. Regression test requirements

Implementation stages must add or update tests for at least:

1. all supported hierarchy component combinations and orderings, including the
   legacy three-token forms;
2. duplicates, empty templates, unsupported tokens, literal text, unsafe path
   forms, and single-component valid templates;
3. S50 and S50 Pro canonical directory-component formatting, including case
   and surrounding-whitespace normalisation;
4. missing, generic, malformed and unsupported identity mapped to
   `unidentified` only when configured;
5. one recognised identity plus unidentified member FITS;
6. conflicting-recognised-identity integrity-error diagnostics containing the
   observation and every conflicting recognised identity, with no identity
   selection, unidentified fallback, regrouping, or archive placement;
7. same target/location/date across two recognised devices, with independent
   observation numbering when telescope is configured;
8. several observations for one recognised telescope;
9. incremental reconciliation and reruns in telescope-specific directories;
10. safe continuation of unrelated valid observations and archive exit code
    `1` when one observation has an integrity error;
11. equivalent dry-run integrity diagnostics, exit code `1`, and zero
    filesystem mutation;
12. dry-run destination and warning output without mutation for valid
    observations;
13. copy and move archive operations, planned and filesystem collisions, and
    optional light-TIFF destinations under telescope-enabled layouts;
14. `convert` and `convert-batch` with `{telescope}` in
    each hierarchy position; and
15. target-level index generation where `{target}` appears before or after
    `{telescope}`, plus archive-root index generation without `{target}` that
    retains observation target metadata and creates no artificial directory;
16. unchanged reconstruction tests demonstrating that focal length, gain,
    focus, and image dimensions are not new grouping constraints.
17. D08 historical target recovery: a target-free historical observation absent
    from the current plan with no usable FITS `OBJECT` and a target recoverable
    from `INDEX.md`; distinct `observation_01` identifiers in different
    hierarchy directories; a missing index with usable FITS evidence; required
    recovery from a missing or malformed index; exact unambiguous matching and
    rejection of ambiguous or inconsistent records; preservation of existing
    index content when recovery fails; and target-containing hierarchy
    compatibility.

## 10. Resolved technical policies

The Draft 1 technical questions are resolved as follows:

- **T01 — reconstruction integrity:** conflicting recognised identities in a
  reconstructed observation are internal reconstruction-integrity errors. The
  affected observation is skipped and is not archived; no automatic correction,
  regrouping, or unidentified fallback is permitted.
- **T02 — error reporting:** diagnostics identify the affected observation and
  conflicting recognised identities, clearly state that it was skipped, permit
  unrelated safe work to continue, and result in archive exit code `1`.
  Dry-run has the same diagnostic and exit policy without mutation.
- **T03 — archive indexing:** a hierarchy containing `{target}` retains a
  target-level index regardless of token order. A hierarchy without `{target}`
  writes one index at the archive root and retains target names plus exact
  relative archive-observation identifiers in Markdown records without
  inventing target directories. D08 permits reading that root index only as the
  Section 5.6 last-resort historical-target fallback.

No additional material technical question is open at this approved revision.

## 11. Implementation stages

ENH-007c is complete at `9ef8e61`. ENH-007d is complete at `696e32d`, including
the separately authorised D08 implementation correction. ENH-007e and the
Checkpoint 5F final acceptance review are complete. Formal ENH-007 closure was
approved on 20 November 2026 after the Checkpoint 6C review returned PASS; the
accepted feature-branch commit is `4b61259`. The closure-record commit remains
pending.

### ENH-007c — Identity resolution and hierarchy planning foundation

**Status:** COMPLETE — implementation commit `9ef8e61`

**Purpose:** Add the optional hierarchy grammar and derive a resolved,
observation-level telescope component without changing reconstruction grouping.

**Permitted work:** Planning/configuration models and validation, identity
resolution, destination generation, observation numbering, focused unit tests.

**Exclusions:** Archive execution, CLI presentation, indexing, conversion
integration, broader documentation, and archive reorganisation.

**Closure evidence:** E007-01 through E007-10 and E007-13 through E007-14 as
applicable; focused tests; Ruff for changed files; `git diff --check`; no
reconstruction-membership regression. Checkpoint 5F accepted the applicable
criteria and found no outstanding evidence gap.

### ENH-007d — Archive operation and integration compatibility

**Status:** COMPLETE — implementation commit `696e32d`

**Purpose:** Integrate the approved foundation across incremental
reconciliation, archive indexing, dry-run output, light-TIFF paths, and
archive-aware conversion contracts.

**Permitted work:** The original stage authorisation covered only integration
areas required by D06–D07 and their focused/integration regressions. The D08
implementation correction was subsequently authorised separately and delivered
within this stage; its approved specification amendment is recorded above.

**Exclusions:** Changes to identity formats, reconstruction grouping, FITS
metadata, archive reorganisation, general-purpose index parsing or repair, and
unrelated output redesign.

**Closure evidence:** E007-11 through E007-12 and E007-15 through E007-20;
integrity-error safe-continuation and dry-run non-mutation evidence; copy/move
and collision regression evidence; index and conversion-recognition evidence;
D08 exact historical-target fallback, required-recovery failure preservation
and diagnostic evidence; `git diff --check`. Checkpoint 5F accepted the
applicable criteria and found no outstanding evidence gap.

### ENH-007e — Full validation and closure review

**Status:** COMPLETE — coordinator accepted Checkpoint 5F on 20 November 2026

**Purpose:** Validate the approved implementation as one compatible archive
change and prepare closure evidence.

**Permitted work:** Authorised validation, bounded defect correction if a
separate launcher approves it, and authorised closure documentation only.

**Exclusions:** New functionality, hierarchy migration, and ENH-008 work.

**Closure evidence:** Complete `pytest`; `ruff check .`; applicable formatting
and whitespace checks; review of actual diff and scope; all E007 criteria;
documented known limitations; coordinator review before any user-controlled
Git action. Accepted evidence records 941 tests passed with zero failures and
two expected duplicate-ZIP-entry warnings; Ruff lint, formatting, PDF,
SHA-256-manifest and whitespace validation passed; E007-01 through E007-21
passed; D01 through D08 were compliant; documentation and the complete change
set passed review; no product defect or acceptance-criteria gap remained.

## 12. Records and limitations

ENH-007 is based on the established BUG-002/BUG-003 recognised identity rules,
the current archive architecture, and the ENH-007a and ENH-007a.2 read-only
investigations. The investigations established that focal length can distinguish
the reported Seestar models but cannot establish an individual device; gain,
focus, image dimensions and related fields do not provide sufficient evidence
to change grouping.

ENH-007c implementation completed and was committed as `9ef8e61`. ENH-007d,
including the D08 correction, completed at `696e32d`. ENH-007e completed after
the Checkpoint 5F final acceptance review passed all 21 acceptance criteria and
confirmed all eight decisions compliant. The accepted evidence includes 527
focused tests and 941 complete-suite tests, with two expected warnings, plus
passing Ruff, formatting, public-input, PDF, SHA-256-manifest and whitespace
checks. The two expected warnings were duplicate-ZIP-entry warnings. Checkpoint
6B commit `4b61259` was verified, and the Checkpoint 6C
formal closure review returned PASS. No unresolved ENH-007 product defect
remained.

Distribution validation remains inconclusive because external PyPI name
resolution was unavailable; it is recorded separately from product validation
and was not an explicit ENH-007e completion requirement. Formal ENH-007
development closure was approved on 20 November 2026 following the Checkpoint
6C PASS review, with feature-branch commit `4b61259` accepted. The formal
closure-record commit, integration-readiness review, integration into `main`,
push to origin, GitHub Actions verification and feature-branch cleanup remain
pending. Release is separate scope. This record does not claim migration or any
of those pending delivery activities. General ENH-008 recovery work remains
outside scope.
