# Stage 9.3b PROGRESS REPORT

**Stage: STARTED. Checkpoints A and B technical: PASS. Human visual review: PASS.**
**Independent technical closure review and formal closure: PENDING.**

The Checkpoint A sections below preserve the state at that checkpoint. The
Checkpoint B continuation records the later authorisation, work and results.

## Checkpoint A — requirements audit and pipeline design

### Established requirements

Stage 9.1a assigns Markdown-to-PDF generation, source/PDF timestamp synchronization,
per-guide SHA-256 manifests, checksum verification and visual/content validation to
Stage 9.3b. It recommends a repository wrapper around Pandoc and an explicit
XeLaTeX engine with known fonts, while classifying that recommendation as unproven
until this Stage. Stage 9.3a makes the two Markdown files authoritative and assigns
PDFs, reproducibility and manifests here. Stage 9.4 alone owns the release ZIP and
its external checksum.

The final repository set contains Markdown, PDF and `.sha256` for each guide. Each
manifest hashes its Markdown and PDF. Each PDF mtime matches its Markdown source.
The PDFs and manifests are committed; only the PDFs later enter the release ZIP.
PDF tooling remains development/release-only.

### Repository facts

- Starting branch is `main`; HEAD is
  `41c000fb98fdd42ab6f3f9f486f531eafcb520e2`, with subject
  `Stage 9.3a: complete user and public documentation`.
- Initial status contained only the expected modified
  `docs/development/CHANGELOG.md`. Its pending Stage 9.3a row is preserved.
- `pyproject.toml` is the sole version source and reports 1.1.0. Runtime
  dependencies are Astropy, NumPy, OpenCV headless and tifffile. Existing extras
  are build and dev; no PDF dependency is declared.
- No PDF generator, PDF configuration, tracked PDF, tracked `.sha256` manifest or
  PDF CI job exists. `.gitignore` does not exclude PDFs or manifests.
- The clean-install and distribution validators explicitly prove that ReportLab,
  WeasyPrint and fpdf are absent from ordinary runtime-only installs.
- Pandoc, XeLaTeX and Poppler inspection commands were not available on the audit
  PATH. Their absence is not used to choose an accidental local converter.
- CI runs the four supported Python versions on macOS arm64 and performs runtime,
  quality and distribution checks. It does not regenerate documentation.
- The User Guide has 1,880 lines, 14 level-1 headings, 77 level-2 headings, 79
  fenced blocks, 90 links and a 172-character longest line. The Quick Start has
  379 lines, one level-1 heading, 12 level-2 headings, 29 fenced blocks, two links
  and a 108-character longest line. Neither source currently contains a Markdown
  table or image. Both use arrows and box-drawing glyphs, which the selected font
  set must cover.

### Proposed implementation decisions

Use a standard-library Python wrapper invoking version-checked Pandoc and XeLaTeX
with repository defaults/template material and TeX-distributed embedded fonts.
Use independent Poppler commands for PDF metadata, text, font and raster
inspection. Declare and document this toolchain separately from package metadata;
record exact resolved versions in Checkpoint B. No Toolkit runtime or ordinary
user installation dependency changes.

The wrapper has fixed mappings for the two approved guides, reads version 1.1.0
from `pyproject.toml`, checks the frozen source hashes/version text, renders only
from local inputs in temporary directories, validates before atomic replacement,
copies source mtime to PDF, writes strict two-line manifests and verifies them.
Two independent builds must be byte-identical. `SOURCE_DATE_EPOCH`, locale,
timezone, metadata and declared fonts constrain nondeterminism.

The proposed repository-root commands are
`python tools/generate_documentation_pdfs.py --all`, followed by the independent
read-only `python tools/validate_documentation_pdfs.py --all` and recorded rendered
visual inspection. Both commands operate only on the two fixed document mappings.

Use A4 manual styling, embedded readable body/monospace fonts, PDF bookmarks,
working User Guide Contents links, converted guide-to-guide PDF links, restrained
page numbers and robust code/path wrapping. The specification defines automated
source-block coverage plus actual raster inspection of every page. OCR is not the
primary content test.

The exact manifest syntax is:

```text
<64-lowercase-hex>  DOCUMENT_BASENAME.md
<64-lowercase-hex>  DOCUMENT_BASENAME.pdf
```

There is no header, path, timestamp or manifest self-hash. Markdown precedes PDF,
and the file ends with LF.

### CI recommendation

Do not change CI for v1.1.0. Mandatory regeneration would add a large TeX
toolchain to the runtime compatibility matrix. Require the complete local B
generation and validation record instead. A future separately authorised CI check
could validate committed manifest hashes and PDF structure without regeneration.

### Privacy and release scope

No generator input or asset may be fetched remotely during generation. Validate
PDF metadata, extracted text, logs and manifests for private paths, capture data,
credentials, locations/GPS and private maintainer-tool references. Temporary TeX,
raster/contact-sheet and duplicate-build outputs are removed. The later release
ZIP receives only the two PDFs; Markdown, manifests and development tooling remain
outside it.

### Decisions requiring approval before Checkpoint B

Independent review must accept the architecture, the separate development
toolchain declaration, Pandoc/XeLaTeX plus Poppler choice, strict byte-identical
two-build gate, exact manifest format, layout contract and visual/content
procedure. Explicit Checkpoint B authorisation is also required. Tool versions and
font families will be selected from the installed declared toolchain and recorded
during B; no version is invented during this tool-free audit.

### Closure status

The authoritative specification defines 53 criteria. Criteria 1–22 are PASS for
Checkpoint A. Criterion 23 is PENDING independent review/authorisation. Criteria
24–49 are implementation and validation work for B. Criteria 50–53 are independent
review, user-created commit, post-commit verification and formal completion gates.
No implementation criterion is marked PASS.

No documentation or product defect was found. The frozen guides were not changed.
No generator, PDF, final manifest, release artifact, commit or push was created.

### Checkpoint A validation

Both approved guide hashes match. The pending Stage 9.3a development changelog
diff is unchanged. JSON parsing, direct new-document whitespace checks,
repository `git diff --check`, public fixture/history validation, Ruff and the
configured formatting check pass. Ruff 0.16.8 reports `All checks passed!`; the
formatting check reports `37 files already formatted`; public-input validation
reports 10 reviewed fixtures, a clean public root and no oversized blobs. The
default Homebrew Python 3.14 lacked Ruff, so that optional invocation could not
start; the same read-only gates passed in the existing Stage validation
environment. No unexpected production, test, fixture, package-metadata or CI
change exists.

## Checkpoint B — implementation and interrupted-session continuation

The independent A review authorised B and criterion 23. Its refinements are now
recorded in specification section 16. The resumed tree contained the implemented
pipeline and accepted artifacts, but no B JSON and no B report section: the final
evidence patches had failed to apply before the usage interruption. No work was
restarted or discarded. The approved Markdown, PDF bytes and mtimes are unchanged.
The prior successful full suite reported 330 tests in 12.66s; subsequent validator
edits required a new full validation. A complete earlier untracked-file hash
snapshot was not available, so no exhaustive historical byte delta is claimed.

### Toolchain provenance

The automated BasicTeX cask attempt FAILED because administrator authentication
required an interactive terminal. Homebrew TeX Live 20260301 then installed
successfully and generated the accepted PDFs. Its executable is
`/opt/homebrew/bin/xelatex`, reporting XeTeX 0.999998, TeX Live 2026/Homebrew,
kpathsea 6.4.2. The maintainer subsequently installed BasicTeX manually at system
level; `/Library/TeX/texbin/xelatex` reports TeX Live 2026 without the Homebrew
suffix. Both installations exist. The agent PATH and original/final build logs
identify Homebrew as the producer; current clean builds reproduce the exact
accepted hashes. The user-reported system BasicTeX installation is preserved as
separate setup history, not substituted for that evidence.

Pandoc 3.11, Poppler 26.09.0 and MuPDF 1.28.4 are declared development tools.
TeX-distributed TeX Gyre Heros 2.004 and DejaVu Sans Mono 2.34 are embedded with
Unicode mappings. Optional ImageMagick 7.1.2-31 supplied contact sheets. No font
binaries, runtime dependencies, package metadata or CI changes were introduced.

### Genuine failures and remediation

- **BasicTeX automated installation — FAIL:** Homebrew cask required interactive administrator authentication; cask attempt purged. Homebrew texlive 20260301 was installed successfully. User later installed system BasicTeX manually; both installations remain distinct.

- **Initial tool quality — FAIL:** Unused os import (F401), 153-character line (E501) and formatting failures corrected in the new tools; no configuration weakened.

- **Initial font resolution — FAIL:** Fontspec could not resolve family names. Explicit TeX-distributed filenames fixed resolution; no font binaries committed.

- **Pandoc argument repair — FAIL:** Missing --variable made colorlinks=true an input filename; restored the flag.

- **Header ordering — FAIL:** hypersetup was used before hyperref existed; removed the premature call and used Pandoc variables.

- **Initial reproducibility — FAIL:** Pandoc direct PDF builds differed: ff16f1c73309c5363f62042ad99ddde1b92a5ea7ff20d80da7d3932b9fab53be versus 7a8555ef1bb4d6070428ea8a9af39d9bf23c957268e6e294bb5e1a90c32a09e9. Extracted text matched but embedded font subset names differed.

- **Deterministic time alone — FAIL:** Further debug pairs differed (f059839edea7637e553a49322b99879ffb9f6f880c566f21bad2bbfc7d3209b2 / 4675c26cf379231ffb010893b0bb7d7aa897cd0731ca781629487f93afb8b118; FORCE_SOURCE_DATE pair a60c4fcd68b24e3663739ac4361c55abfba7950afad5de54026c5bbc2f883a0b / 0a8540079488c39361303790e743db1784a4fc56613f41a5cff96e8c1150b10c). Stable relative TeX basename plus two direct XeLaTeX passes repaired font-subset nondeterminism.

- **A4 check — FAIL:** Literal decimal precision differed in pdfinfo; numeric A4 bounds replaced string equality.

- **Heading extraction — FAIL:** Markup stripping removed meaningful underscores; preserved underscores.

- **Prose extraction — FAIL:** Discretionary end-of-line hyphenation required normalization; substantive text remains checked.

- **Font embedding parser — FAIL:** Variable type-column width invalidated fixed column indexing; parse embedding/Unicode columns relative to row end.

- **Bookmarks — FAIL:** Raw-byte Outlines search missed compressed objects; added declared MuPDF inspection.

- **Privacy false positive — FAIL:** Generic /Volumes matched approved synthetic user examples; distinguish approved examples from private home paths.

- **Cross-page code extraction — FAIL:** Quick Start code/tree crosses a footer; ordered code-line validation handles pagination without dropping command content.

- **Contact-sheet font — FAIL:** ImageMagick default font unavailable; use explicit TeX DejaVu Sans font.

- **Later tool formatting — FAIL:** New comprehension required formatting; corrected before passing quality checks.

- **Interrupted evidence writing — INCOMPLETE:** Two evidence patches failed context matching and did not land. The usage interruption left the report at A and no B JSON; this continuation records B without deleting A history.

- **Resume validation gaps — REMEDIATED:** Inspection found no version guard despite the specification, and HTML outline links inflated annotation counts. Added tested Pandoc/XeTeX guards and direct PDF action/destination checks; expanded list/opening coverage and corrected an inaccurate heading-check comment. No rendering inputs or accepted PDF bytes changed.

- **Resume list normalization — FAIL:** Five list openings used Markdown triple hyphens rendered as em dashes. Equivalent punctuation normalization repaired these extraction false positives; all 111/17 list openings now pass.

- **Resume distribution sandbox — FAIL:** Isolated build could not resolve PyPI inside sandbox; authorized network retry passed all unchanged distribution gates.

- **Font-version diagnostic — WARNING:** fc-scan returned versions but warned about unwritable caches; otfinfo independently confirmed exact font versions without that cache dependency.

- **Continuation report writer — FAIL:** Temporary evidence helper shadowed a Path variable; JSON was written but report write failed. Corrected the helper and wrote the report; repository implementation/artifacts were unaffected.

### Final accepted artifacts and independent review

The generator command remains `python tools/generate_documentation_pdfs.py --all`;
the independent validator is `python tools/validate_documentation_pdfs.py --all`.
During continuation, two clean temporary builds per guide were compared to the
accepted PDFs without installing/replacing them. Both pairs match exactly.
Temporary builds use the current generator and declared Homebrew toolchain.

- **SEESTAR_TOOLKIT_USER_GUIDE.pdf**: 27 pages, 120047 bytes; both clean builds and accepted artifact SHA-256 `8600d48d03ca8bcdf8bc4e3f2f3403143592a45fa3e769d7c3734ebec11ee70b`. Source/PDF mtime: `1789734082074713848` ns.

- **SEESTAR_TOOLKIT_QUICK_START.pdf**: 5 pages, 43803 bytes; both clean builds and accepted artifact SHA-256 `56f0a92641f86742e0e066b3d3727424396bef76705d27b29cc1f5f59656b033`. Source/PDF mtime: `1789734207766841774` ns.

Both PDFs are unencrypted A4 PDF 1.7, with the source title, Mark Wymer as author,
version 1.1.0 in subject/keywords, LaTeX via pandoc as creator and xdvipdfmx
(20260113) as producer. Creation times derive from source mtimes; no modification
time, custom metadata or XMP stream was added. Strict two-line LF manifests
recompute correctly; exact contents and approved Markdown hashes are in the B JSON.

All 103/13 headings, 79/29 fenced code blocks, 49/9 representative prose blocks,
111/17 list openings and document beginnings/endings validate. There are no tables.
Exact bookmark outlines contain 102/12 entries. Actual annotations number 90/2;
internal destinations resolve and cross-document PDF targets exist. URI schemes
and values are preserved where present. All page footers, geometry and nonblank
content checks pass. Clean build logs contain zero overfull boxes or missing
glyph messages. Source/version drift and extra manifest entries are rejected.

Earlier Codex rendered inspection covered all 32 pages at 150 dpi, with selected
full-resolution samples recorded in B JSON. The user now confirms independent
human visual PASS for all 27 User Guide and five Quick Start pages, including
typography, hierarchy, numbering, code/commands, trees, configurations, transitions,
clipping/overflow and glyphs. No rendering change was requested. Approved PDF
hashes match those reviewed. Temporary rasters/contact sheets are removed after
acceptance; accepted PDFs and manifests remain in docs/user.

### Repository validation and scope

Full pytest, repository-wide Ruff, configured formatting, additional new-tool
formatting, tracked diff checks, direct new/changed documentation whitespace,
Markdown fences/local links/anchors, Issue-form YAML, public fixtures/history,
installed entry points and full isolated distribution validation pass. Exact final
outputs are recorded in B JSON. The untouched pending development CHANGELOG row
is preserved, including its unrelated historical whitespace line.

Distribution validation admits 39 wheel and 46 sdist members, checks runtime-only
imports and conversion, and validates both installed entry points as 1.1.0.
MANIFEST.in explicitly prunes docs/tools. The future release ZIP includes only the
two PDFs, excluding Markdown, repository manifests and development tooling; no
ZIP was built. Privacy review covers metadata, extracted text, PDF objects and
new evidence. Approved synthetic examples remain; no private home path, credential
or private maintainer-file content was introduced. Private maintainer files remain
absent inside the repository; their external locations were not inspected.

No production source, tests, fixtures, package metadata, CI, frozen Markdown,
approved PDF bytes, Checkpoint A evidence or Stage 9.3a evidence were modified.
No unresolved rendering/documentation or potential product defect was found.

### Complete closure accounting

Every criterion is assessed individually in
[Checkpoint B evidence](STAGE_9.3b_CHECKPOINT_B.json).

1. **PASS** — Starting branch, exact commit subject and expected dirty state verified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
2. **PASS** — Pending Stage 9.3a development CHANGELOG row preserved byte-for-byte. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
3. **PASS** — Both authoritative Markdown sources exist and match approved SHA-256 values. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
4. **PASS** — Stage 9.3a completion and relevant Stage 9 evidence reviewed. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
5. **PASS** — Repository PDF tools, scripts, dependencies, ignore rules and artifacts audited. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
6. **PASS** — Existing CI and distribution boundaries audited. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
7. **PASS** — Markdown feature, link, glyph, length and structure inventory recorded. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
8. **PASS** — Existing PDF policy distinguished from prior non-binding proposals. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
9. **PASS** — Exact inputs and six-file final user-document set specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
10. **PASS** — Checkpoint scope, exclusions and A/B boundary specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
11. **PASS** — Repository wrapper architecture specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
12. **PASS** — Development-only dependency and declaration policy specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
13. **PASS** — Runtime, user-installation and distribution isolation specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
14. **PASS** — Single-authority version and deterministic metadata policy specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
15. **PASS** — Two-build byte-reproducibility policy specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
16. **PASS** — Source/PDF timestamp synchronization policy specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
17. **PASS** — Exact two-entry checksum format and independent verification specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
18. **PASS** — Layout, typography, navigation, wrapping and page-number policy specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
19. **PASS** — Machine content-integrity checks specified without OCR dependence. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
20. **PASS** — Rendered all-page and representative-page visual procedure specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
21. **PASS** — Privacy, release-ZIP boundary and CI recommendation specified. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
22. **PASS** — Checkpoint A evidence/report and local quality checks pass. Preserved Checkpoint A PASS evidence; frozen hashes, baseline, scope and pending changelog reconfirmed in final continuation.
23. **PASS** — Independent review accepts A and explicitly authorises Checkpoint B. Independent Checkpoint A review explicitly authorised PASS with refinements, now recorded in specification section 16.
24. **PASS** — Documentation toolchain declaration and installation instructions implemented. PDF_TOOLCHAIN.md declares commands, versions, fonts and installation route.
25. **PASS** — Exact tool/font versions and environment recorded. Resolved Homebrew XeLaTeX, exact versions/font versions, environment and separate manual BasicTeX recorded.
26. **PASS** — Generator wrapper implemented with fixed input/output mappings. Fixed mappings and temporary two-build wrapper present.
27. **PASS** — Independent PDF/manifest validator implemented. Independent Poppler/MuPDF validator and strict manifests pass.
28. **PASS** — Generator rejects source/version drift and avoids shell interpolation. Source/version negative checks reject drift; subprocess argument lists, shell escape disabled; exact tool versions guarded.
29. **PASS** — Generation uses only local approved inputs and temporary staging. Local fixed source/header/filter inputs, temporary staging; no remote generation input.
30. **PASS** — Both PDFs generated without changing either Markdown source or timestamp. Approved source SHA-256 and A-recorded nanosecond mtimes unchanged; existing approved PDFs not replaced during continuation.
31. **PASS** — User Guide PDF meets layout, navigation and metadata contract. 27-page A4 User Guide metadata/navigation/geometry and independent human visual PASS.
32. **PASS** — Quick Start PDF meets layout, navigation and metadata contract. 5-page A4 Quick Start metadata/navigation/geometry and independent human visual PASS.
33. **PASS** — All fonts are present, suitable, embedded and cover required glyphs. TeX Gyre Heros 2.004 and DejaVu Sans Mono 2.34 embedded with Unicode mapping; no missing glyph log messages.
34. **PASS** — Two clean builds of each PDF are byte-identical. Two new clean builds of each equal each other and the accepted artifact SHA-256.
35. **PASS** — Each final PDF mtime exactly matches its Markdown source mtime. Each PDF/source st_mtime_ns equals A evidence.
36. **PASS** — Each strict two-entry manifest is generated and independently verifies. Strict manifests independently rehashed; extra-entry negative checks rejected.
37. **PASS** — Automated content-integrity validation passes for both PDFs. All headings, all code lines, representative prose, all list openings, beginning/end pass; no source tables.
38. **PASS** — Local and external PDF link validation passes. 90/2 real annotations; internal named destinations exist; cross-document files exist; external URI preservation checked where present.
39. **PASS** — Automated page geometry, blank-page and numbering checks pass. 27/5 nonblank A4 pages; every footer numbered in sequence; bounding boxes inside pages; zero overfull log warnings.
40. **PASS** — Every page is rendered and visually inspected; required samples are recorded. Earlier 150-dpi render of all 32 pages and Codex inspection; independent human review now PASS for exact matching artifacts.
41. **PASS** — No clipping, overflow, missing glyph, malformed structure or Markdown leakage remains. Human accepted typography, hierarchy, numbering, code/trees, configurations, transitions, clipping, overflow and glyphs; no required changes.
42. **PASS** — Generated artifacts and evidence pass privacy review. Metadata/text/object/manifest review excludes private paths/credentials; approved synthetic source examples retained; evidence uses repository-relative paths or public tool paths.
43. **PASS** — Release ZIP inclusion/exclusion and wheel/sdist isolation are verified. MANIFEST.in prunes docs/tools; strict wheel/sdist allowlists pass. Future ZIP policy includes only PDFs; actual ZIP assembly remains Stage 9.4.
44. **PASS** — Full pytest, Ruff, configured formatting and whitespace gates pass. Final full pytest, repository Ruff, configured/new-tool formatting, diff and direct new-document whitespace pass; untouched pending changelog whitespace preserved.
45. **PASS** — Markdown navigation, public fixture/history and installed CLI checks pass. Local Markdown/fence/anchor checks, public input/history checks, both installed entry points pass.
46. **PASS** — Full distribution validation passes with no PDF tooling/artifact leakage. Full isolated distribution validator passes: wheel 39 members, sdist 46; runtime-only imports and both entry points pass.
47. **PASS** — Every genuine failure and remediation is preserved in evidence. Separate failed attempts and remediations retained in this chronology; A and Stage 9.3a evidence untouched.
48. **PASS** — Checkpoint B report accounts for every criterion and unresolved defect. This structured evidence and report individually account for criteria 1–53 and pending formal gates.
49. **PASS** — No production, test, fixture, runtime dependency or CI change exceeds scope. No production/tests/fixtures/metadata/CI edits; frozen guides and accepted PDFs unchanged.
50. **PENDING** — Independent review accepts technical completion. PENDING independent review of final technical closure evidence; human visual PASS does not substitute.
51. **PENDING** — User approves and creates the closure commit; Codex does not commit or push. PENDING user authorisation and user-created closure commit; no commit/push performed.
52. **PENDING** — Exact post-commit content, cleanliness and required CI are verified. PENDING exact post-commit cleanliness/content and required CI verification.
53. **PENDING** — Formal COMPLETE is declared only after every preceding criterion passes. PENDING independent formal COMPLETE declaration after all preceding gates.

Checkpoint B is technically PASS and independent human visual review is PASS.
Stage 9.3b remains STARTED. Criteria 50–53 remain PENDING: independent technical
closure review, authorised user-created commit, exact post-commit/CI validation,
and independent formal COMPLETE declaration. No commit, push, tag, release or
Stage 9.4 work occurred. Stop for independent closure review.

### Final current-tree check record

After the final tooling edits: **330 passed in 11.95s**; Ruff 0.16.8 reports
**All checks passed!**; configured formatting reports **37 files already
formatted**, and explicit new-tool formatting reports **2 files already
formatted**. `git diff --check` exits 0 without diagnostics. Direct scans find no
new trailing whitespace. Twelve Markdown documents pass fence/link/anchor checks
(126 local links); external URI preservation is checked, not remote HTTP uptime.
All three unchanged Issue-form YAML files validate. Public inputs report
**10 reviewed fixtures; clean public root; no oversized blobs**. The full isolated
distribution validator was rerun after final tooling edits and again passed
39 wheel / 46 sdist members, runtime smoke and both 1.1.0 entry points.

The final generator/header/filter and validator hashes are recorded in B JSON.
Only report/JSON result recording followed those full gates; their final parsing,
Markdown, link, whitespace and privacy checks pass. Continuation modified seven
existing working-tree files (PACKAGING, PROJECT_Notes, PDF_TOOLCHAIN, specification,
report, generator and validator) and created the B JSON. The pending CHANGELOG,
A evidence, both frozen sources, both approved PDFs and both manifests remain
byte-identical with unchanged mtimes from the resume snapshot. No staging,
commit, push, tag, release or later-stage work occurred.
