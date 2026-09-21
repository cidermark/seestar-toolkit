# Stage 9.3a — Authoritative Markdown User Documentation

**START boundary: STARTED. Checkpoint A only is authorised initially.**
**COMPLETE boundary: not reached; all checkpoints and formal gates below are required.**

## 1. Purpose and authority

Document the release-validated Seestar Toolkit v1.1.0 implementation, not roadmap
interfaces. Starting baseline: `main`, `519f0e3` (Stage 9.2b closure commit).
Preserve the existing pending `docs/development/CHANGELOG.md` modification.
This specification implements the Stage review's Stage 9.3a request. Its attachment
ends mid-sentence in the final validation paragraph; the complete instructions
and the explicit validation requirements here define the executable scope.

## 2. Deliverables and documentation authority

- `docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md`: complete authoritative user detail.
- `docs/user/SEESTAR_TOOLKIT_QUICK_START.md`: abbreviated experienced-user route.
- `README.md`: concise public landing page, not a duplicate guide.
- `CONTRIBUTING.md`: proportionate public contribution guidance.
- `CHANGELOG.md`: user-relevant public release history; 1.1.0 stays Unreleased.
- Development specification, accumulating report, checkpoint JSON evidence, and
  appropriate PACKAGING/PROJECT_Notes status updates.

Resolve user-document conflicts in favour of complete, implementation-verified
Guide detail and correct the abbreviated documents. Development evidence remains
authoritative for historical decisions and validation, not invented interfaces.

## 3. Checkpoints

**A — audit/design:** establish starting state; create this specification; inspect
public docs, actual license, docs/user inventory, metadata, installed CLI help,
PACKAGING, PROJECT_Notes and relevant Stage 9.1/9.2 evidence. Inventory influential
commands and check syntax/help safely. Record a claim/evidence matrix, classified
contradictions, privacy review, full content outlines and Unreleased entry design.
Create `STAGE_9.3a_CHECKPOINT_A.json` and `STAGE_9.3a_REPORT.md`. Do not write the
full guides or change public deliverables. Stop for Stage review before B.

**B — guides:** following explicit authorisation, implement Guide and Quick Start
from the approved design. Check current upstream Homebrew instructions if used;
verify release-download links without implying an unpublished release exists.
Validate examples using installed 1.1.0 and disposable public-safe inputs only.
Preserve failures and produce checkpoint evidence. Stop before C.

**C — public docs and closure audit:** following explicit authorisation, implement
README/CONTRIBUTING and normalise public CHANGELOG; reconcile the five documents,
resolve live documentation defects within scope, validate links/examples/privacy,
run final checks and individually assess every closure criterion. Technical
completion alone does not satisfy the independent review/commit/post-commit gates.

## 4. Mandatory release facts and user coverage

Version is 1.1.0 with semantic versioning, Unreleased until actual GitHub
publication; no invented date. Support is macOS Apple Silicon arm64 on versions
both tested and Apple-supported at release. Do not imply all Apple-supported OS
versions were tested, or support Intel/Rosetta, Windows or Linux. Python support
is >=3.11,<3.15, established by Stage 9.2a with Stage 9.1d CI.

Recommend Homebrew Python; explain `which python3` and `python3 --version` and
selection of a supported interpreter without modifying Apple's Python. uv was
validation tooling, not a user requirement. Wheel is primary, sdist secondary;
no Toolkit PyPI route or installer shell script. Use `~/.venvs/seestar-toolkit/`,
`source ~/.venvs/seestar-toolkit/bin/activate`, `deactivate`, and optional full-path
CLI execution. Do not prescribe global PATH, symlinks or automatic .zshrc edits.

Describe both `seestar-toolkit` and `python -m seestar_toolkit`; use the former
primarily. Global --help/--version/--verbose precede convert, convert-batch or
archive. Preserve exact installed positional arguments and archive options.
No internal Python APIs become public commands. Explain single conversion,
non-recursive batch conversion and the actual archive discovery depth.

Configuration is read-only, defaults to `~/.config/seestar-toolkit/config.toml`,
and does not consult XDG_CONFIG_HOME. Explain explicit config, CLI precedence,
saved-location matching, explicit location, interactive confirmation and
unknown/manual fallback, using current tests/source. No config-writing,
saved-location-writing or JPEG-policy CLI exists. Location matching is local,
without an external geocoder.

Archive terminology is `{target}/{location}/{session_end_date}` and
`observation_01`, not historical `{date}`/`session_01`. Explain observations,
lights, TIFF products, seestar_stacked, target INDEX.md and the +12-hour date rule.
Prominently require backups, dry-run, planned-path review, explicit copy first,
collision understanding, then optional move. Explicit source-action avoids
configuration changing the safety of examples. Explain skip-identical/error/
overwrite, source preservation, existing TIFF collision behaviour, untouched
JPEGs and absence of whole-operation transactional rollback.

Bound input claims to validated S50 FIT/FITS raw/native RGB and tested Siril RGB,
including evidence-qualified capture modes. No all-files/all-modes claim; no
DSLR, S50 Pro, S30/S30 Pro support or Solar/Lunar/Planetary MP4 extraction.
Preserve linear output: uint16 Seestar TIFF and float32 Siril RGB TIFF where
validated; raw Bayer demosaicing and already-RGB preservation, no invented stretch,
white balance or colour processing. The generic 16-bit description must not hide
the validated float32 exception.

Cover diagnostics, errors, exit codes, environment verification, troubleshooting,
limitations and help/reporting. Describe validated local/removable/mounted NAS/
cross-storage behaviour without generalising to every filesystem. Bound no
telemetry/analytics/update-checking/metadata-transmission claims to the audited
Toolkit runtime; dependency installation and mounted filesystem I/O are distinct.
Warn that FITS, indexes and diagnostics can retain GPS/device/capture metadata.
macOS can restrict selected folders/storage; do not require Full Disk Access or
suggest bypassing privacy controls. Explain uninstall/deactivate/package/venv
removal separately from optional config removal and persistent TIFF/archive data.

Quick Start covers requirements, obtaining the release when published, Python,
venv, wheel, version, single/batch, archive dry-run then copy, location/config,
deactivation and Guide link. README covers identity/status/capabilities/environment/
input scope/install pointer/minimal example/docs/safety/limitations/contributing/
license. CONTRIBUTING covers bug reports, requests, PRs, checks and sanitised FITS
sharing; never request private real datasets. Public CHANGELOG omits internal
Stage history. Future enhancements remain in PROJECT_Notes, not user promises.

## 5. Evidence, defects and privacy

Record claim, exact repository authority, finding and qualification in the fact
matrix. Distinguish executed checks from historical evidence and deferred work.
Classify discrepancies as documentation defect, potential product defect, or not
a contradiction / historical context. Preserve and report potential release
product defects before B; do not silently document around or fix them in A.
Preserve genuine failed validation and subsequent remediation without relabelling
original runs. Historical development records are not rewritten merely to match
new documentation. Record neutral paths, synthetic locations/coordinates and
public-safe fixture names only; no actual home paths, usernames, volume/share
names, credentials or private capture names. Preserve existing license attribution.

## 6. Validation and exclusions

A requires metadata/doc inventory, installed help/version and safe example parser
checks where practical, JSON/evidence consistency, privacy review, Ruff,
`python tools/check_formatting.py`, `python tools/check_public_inputs.py`, and
`git diff --check` including new files' whitespace. Full pytest is mandatory if
behaviour-capable content changes, and may be run for additional baseline evidence.
B requires safe example validation, links, privacy and documentation consistency.
C requires full pytest, Ruff, configured formatting, public fixture/history checks,
whitespace, complete documentation checks and `python tools/validate_distribution.py`
(the root README forms package metadata). Retain failures and rerun after fixes.
No extra formatting scope or weakened validation. No unapproved production,
test, fixture, dependency, packaging or CI changes. No external storage probing
in A; reuse recorded Stage 9.2b evidence.

Do not commit or push, publish PyPI, create tags/Releases, change private visibility,
or begin later stages. Stage 9.3b owns PDFs, reproducibility, timestamp sync,
SHA-256/manifests and visual PDF checks. No generated release artifacts in A.

## 7. Formal workflow and report formats

At each checkpoint return **Stage 9.3a PROGRESS REPORT** with: status and checkpoint
PASS/FAIL/incomplete; work/evidence; exact files changed; findings/defect classes;
validation results and limitations; pending work and next authorised boundary;
preservation/scope confirmation. Accumulating report retains each checkpoint.

At C return **Stage 9.3a COMPLETION REPORT** with: technical and formal status;
deliverables/files; authoritative facts and resolved/open defects; validation and
failure history; privacy/scope confirmation; every numbered criterion assessed
individually with evidence; remaining gates. Use PASS, FAIL or PENDING; never mark
a deferred gate PASS. Independent ChatGPT review precedes a user-approved closure
commit. Codex does not commit. Verify the actual resulting commit/content, expected
working-tree state and required green CI after the user commit before declaring
formal COMPLETE. Do not invent commit IDs or CI evidence.

## 8. Individually assessed closure criteria

1. Starting branch and commit verified.
2. Expected pending development CHANGELOG preserved.
3. Authoritative specification created before documentation implementation.
4. Checkpoint boundaries and exclusions explicit.
5. Existing public documentation and license audited.
6. Package metadata and release version verified.
7. Both installed CLI entry points audited.
8. Full exposed command and option inventory recorded.
9. Existing influential command examples inventoried and checked safely.
10. Authoritative fact matrix recorded.
11. Contradictions classified without converting plans into requirements.
12. Potential product defects reported before Checkpoint B.
13. Guide table of contents covers every required topic.
14. Quick Start table of contents designed.
15. README and CONTRIBUTING structures designed.
16. Public Unreleased changelog entry designed.
17. Checkpoint A privacy review and evidence recorded.
18. Checkpoint A local validation passes.
19. Independent review authorises continuation to Checkpoint B.
20. Full authoritative Markdown User Guide implemented.
21. Concise Quick Start implemented and linked to Guide.
22. Semantic version and Unreleased status consistent.
23. Platform support limited to validated macOS Apple Silicon policy.
24. Python 3.11–3.14 support accurately documented.
25. Homebrew interpreter installation and checking documented.
26. System Python remains untouched; uv not required.
27. Wheel primary and sdist secondary installation documented.
28. No Toolkit PyPI or installer-script installation claims.
29. Recommended venv activation, deactivation and full-path alternative documented.
30. No normal global PATH, symlink or shell-profile modifications.
31. Both entry points and exact global-option placement documented.
32. Single conversion and flat batch behaviour documented.
33. Supported S50 and Siril data distinguished from unsupported modes.
34. TIFF dtype, linearity, demosaicing and RGB preservation documented.
35. Archive dry-run, backups and explicit copy safety prominent.
36. Move, collisions, existing TIFFs and non-transactional risks documented.
37. Actual hierarchy, observations, products, indexes and archive date documented.
38. Read-only config path, precedence and ignored XDG behaviour documented.
39. Actual location matching, prompts and fallback documented.
40. Absent config-writing, saved-location-writing and JPEG switches not invented.
41. Diagnostics, errors, exit codes and troubleshooting documented.
42. Local, removable, mounted network and cross-storage scope qualified.
43. Privacy claims bounded by evidence and metadata-sharing risks explained.
44. macOS permissions described without Full Disk Access requirement or bypass.
45. Uninstall separates environment, persistent config and user data.
46. Getting help and limitations documented without future-feature promises.
47. Checkpoint B command examples verified safely and evidence preserved.
48. Checkpoint B documentation consistency, links and privacy checks pass.
49. Independent review authorises continuation to Checkpoint C.
50. Root README concise and consistent with authoritative Guide.
51. Concise CONTRIBUTING includes quality and FITS privacy guidance.
52. Public CHANGELOG user-relevant, Unreleased and without fabricated date.
53. Development status and packaging documentation updated appropriately.
54. Final Markdown content, links and command examples validated.
55. Final public fixture/history and changed-document privacy checks pass.
56. Final full pytest, Ruff, applicable formatting and whitespace checks pass.
57. Final distribution build/inspection validates changed README metadata.
58. Every genuine failure and remediation retained.
59. All closure criteria individually assessed with evidence.
60. No production/test/fixture changes without demonstrated authorised defect.
61. No PDF, timestamp sync, checksum manifest or later-stage work performed.
62. Independent ChatGPT review accepts technical completion.
63. User approves and creates closure commit; Codex never commits or pushes.
64. Post-commit content, branch, cleanliness and required CI verified.
65. Formal COMPLETE declared only after every closure gate passes.
