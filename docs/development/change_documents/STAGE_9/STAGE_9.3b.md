# Stage 9.3b — PDF Generation and Documentation Validation

**START boundary: STARTED. Checkpoint A accepted; Checkpoint B authorised.**
**COMPLETE boundary: not reached; independent closure review and formal gates remain.**

## 1. Purpose and authority

Create reproducible, release-quality PDF representations of the two authoritative
v1.1.0 Markdown guides, commit per-guide SHA-256 manifests, and prove that each PDF
is complete, readable and derived from its frozen source. Markdown remains the
documentation authority. PDFs are generated artifacts and must never be edited as
independent sources.

The starting baseline is branch `main`, commit `41c000f` (`Stage 9.3a: complete
user and public documentation`, 2026-09-21). Preserve the expected pending
`docs/development/CHANGELOG.md` Stage 9.3a row. Stage 9.3a is formally complete.

## 2. Checkpoints

**A — requirements audit and design:** inspect the repository and Stage 9 evidence,
create this specification, the progress report and structured evidence, and define
the generator, validator and closure criteria. No generator, PDF or manifest is
created. Stop for independent review and explicit authorisation before B.

**B — implementation, generation, validation and closure:** after authorisation,
declare the documentation toolchain, implement the repository wrapper and
validator, generate both PDFs and manifests, perform two-build reproducibility,
content, link, metadata and visual checks, then run all repository quality gates.
Preserve failures and remediation. Independent review, a user-created closure
commit, exact-state validation and required CI precede formal completion.

## 3. Scope and exclusions

Checkpoint B may add only the minimum development/release tooling and supporting
configuration needed to generate and validate these documentation artifacts. It
may update Stage 9.3b evidence and appropriate development status documentation.
It must not rewrite or reflow the frozen guides, modify production source, tests,
FITS fixtures, runtime dependencies or CI merely to make the pipeline pass.

Do not generate release ZIPs or their external checksums, publish a release,
create a tag, upload assets, publish to PyPI, or start Stage 9.4. Do not introduce
mandatory PDF regeneration in CI for v1.1.0. Do not inspect private maintainer
files outside the repository. Codex must not commit or push.

## 4. Authoritative inputs and exact outputs

The only document inputs are:

- `docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md`, approved SHA-256
  `29cf55b4beb1f1a6ebcd37c946cdc74a4a8ef41c75dbcee62353c61131fc8883`;
- `docs/user/SEESTAR_TOOLKIT_QUICK_START.md`, approved SHA-256
  `b3f61499335f7a7d15b1a323d3fa39056606b5a2d021a9cf9d82942c119ed18f`;
- the package version read from `[project].version` in `pyproject.toml`; and
- repository-controlled Pandoc defaults, LaTeX template/header and local style
  assets introduced in B, if the implementation proves they are needed.

The exact committed user-document set at completion is:

```text
docs/user/SEESTAR_TOOLKIT_QUICK_START.md
docs/user/SEESTAR_TOOLKIT_QUICK_START.pdf
docs/user/SEESTAR_TOOLKIT_QUICK_START.sha256
docs/user/SEESTAR_TOOLKIT_USER_GUIDE.md
docs/user/SEESTAR_TOOLKIT_USER_GUIDE.pdf
docs/user/SEESTAR_TOOLKIT_USER_GUIDE.sha256
```

Temporary HTML, TeX, auxiliary, raster and duplicate-build files must be created
outside `docs/user` and removed after validation. No remote image, stylesheet,
font or other rendering input is permitted.

## 5. Proposed generation architecture

Implement one repository Python wrapper, provisionally
`tools/generate_documentation_pdfs.py`, with fixed mappings for the two approved
sources and outputs. The wrapper must:

1. locate the repository independently of the caller's working directory;
2. reject changed source hashes unless an authorised evidence update establishes
   new approved hashes;
3. parse `pyproject.toml` with `tomllib` and validate every displayed v1.1.0
   document version against `[project].version`;
4. invoke an explicitly version checked Pandoc and XeLaTeX toolchain using a
   committed defaults file/template or header and no shell interpolation;
5. build into a temporary directory, fail without replacing good outputs, and
   accept no arbitrary additional Markdown input;
6. run the repository PDF validator before atomically installing each PDF;
7. set each accepted PDF's filesystem mtime to its Markdown source mtime with
   `os.utime`, without changing the source; and
8. hash, write and re-read each manifest only after all other checks pass.

This follows the Stage 9.1a recommendation of a repository wrapper around Pandoc
and an explicit XeLaTeX engine with known fonts. It avoids browser print state and
keeps layout policy in version-controlled text. B may adjust a technical detail
only when real tool output demonstrates that it is necessary; record the reason
before changing the architecture.

The proposed operator workflow from the repository root is:

```bash
python tools/generate_documentation_pdfs.py --all
python tools/validate_documentation_pdfs.py --all
```

The first command performs both clean builds, automatic validation, atomic PDF
placement, timestamp synchronization and manifest generation. The second is an
independent read-only revalidation suitable for pre-commit and post-commit use.
Both commands process exactly the two fixed document mappings. Rendered visual
inspection and its evidence record follow these commands before acceptance.

## 6. Development-only dependency policy

Pandoc, a XeLaTeX distribution containing the selected fonts, and independent PDF
inspection utilities are development/release tools. They must not enter
`[project].dependencies`, the wheel, sdist, user installation instructions or the
Stage 9.4 release ZIP. Ordinary Toolkit users do not install them.

B must add a small repository-controlled documentation-toolchain declaration and
instructions that name the required commands, minimum or exact tested versions,
font families and macOS arm64 installation route. Record exact resolved versions
and relevant executable paths in evidence. The selected fonts must come from the
declared TeX distribution, cover the guides' box-drawing and arrow glyphs, and
embed in the PDFs. Do not depend on an undeclared developer-machine font.

Use Python's standard library for orchestration, hashing, TOML parsing, timestamps
and subprocess execution. Prefer independent Poppler command-line inspection
(`pdfinfo`, `pdftotext`, `pdffonts`, `pdftoppm`) for validation. If B demonstrates
that an additional package is necessary, declare it in the documentation
toolchain only and record why. Do not alter Toolkit package metadata merely to
declare PDF tooling.

## 7. Version and PDF metadata policy

`pyproject.toml` `[project].version` is the sole version authority. The wrapper
validates the frozen guides' displayed version; it does not maintain or inject a
second literal. PDF title comes from the first Markdown level-1 heading. Metadata
must include title, author from project metadata, subject identifying Seestar
Toolkit v1.1.0 documentation, and the authoritative version as keywords or
subject text. Creator/producer identify the declared toolchain.

Embedded creation/modification time must use a deterministic UTC representation
derived from the source mtime, or be omitted if the chosen tools cannot encode it
deterministically. It must never use the wall-clock build time. B must inspect and
record the resulting metadata.

## 8. Reproducibility and timestamp policy

Run two independent clean temporary builds with identical declared inputs,
environment, locale (`C.UTF-8` where supported), timezone (`UTC`) and toolchain.
Set `SOURCE_DATE_EPOCH` to the integer seconds of the corresponding Markdown
mtime. Compare PDF bytes by SHA-256 before accepting either artifact. A mismatch
is a failed reproducibility gate until its cause is removed or an independently
approved exception changes this specification; do not claim reproducibility from
similar appearance.

After validation and atomic placement, copy the Markdown source's exact mtime in
nanoseconds to the PDF with `os.utime`. Verify `st_mtime_ns` equality immediately.
Git does not preserve source mtimes, so regeneration after checkout uses the mtime
of the authoritative Markdown in that working tree; hashes, not mtimes, establish
content identity. Do not touch the Markdown timestamps.

## 9. Checksum manifest format and policy

Each UTF-8, LF-terminated manifest contains exactly two standard SHA-256 lines,
Markdown first and PDF second, using basenames and two spaces between digest and
name. For example:

```text
<64-lowercase-hex>  SEESTAR_TOOLKIT_USER_GUIDE.md
<64-lowercase-hex>  SEESTAR_TOOLKIT_USER_GUIDE.pdf
```

The Quick Start manifest uses its corresponding two basenames. It contains no
header, absolute path, timestamp or self-hash. The wrapper writes it atomically,
then an independent validator parses it strictly, rejects extra/missing entries
or unsafe paths, recomputes both digests and proves they match. These repository
manifests are distinct from the later external release-ZIP checksum.

## 10. Layout and rendering contract

Use A4 pages with approximately 20 mm side and 18–22 mm top/bottom content
margins. Use restrained, embedded, TeX-distributed serif or sans body type at
roughly 10.5–11 pt and an embedded monospaced face at roughly 8.5–9 pt. Maintain
clear heading hierarchy, modest spacing and readable list indentation. Show the
document title and existing version/status near the opening without inventing a
separate cover or version string.

Generate PDF bookmarks from headings. Preserve the User Guide's linked Contents
navigation and working internal destinations. Convert links between the two
Markdown guides to the corresponding PDF basename; keep valid external links
clickable and visibly identifiable. The Quick Start need not gain a new contents
page that is absent from its source.

Render fenced and inline code in monospace without syntax-colouring complexity.
Preserve indentation and box-drawing archive trees. Use wrapping that keeps long
commands and paths readable, with visible continuation where practical; no line
may clip outside the content box. Tables must repeat header rows when split and
must neither clip nor shrink below readable size. Keep headings with following
content, discourage orphan list items, avoid a final heading stranded on a page,
and allow genuinely long blocks to split cleanly instead of overflowing.

Use a quiet running header only if it materially aids navigation. Every content
page must have an unobtrusive footer page number; suppress it on a dedicated title
page only if one becomes technically necessary. Avoid decorative backgrounds,
screenshots and unrelated branding.

## 11. Content-integrity validation

Implement a separate validation mode or tool, provisionally
`tools/validate_documentation_pdfs.py`, which does not trust successful converter
exit alone. For each pair it must verify:

- approved Markdown hash, version, PDF signature/EOF, nonzero sensible page count,
  page sizes, metadata, embedded fonts and absence of encryption;
- all source headings occur in extracted PDF text in order and expected bookmark
  destinations exist;
- representative prose throughout, all fenced code/command content in order,
  important commands and paths, and list/table coverage sufficient to detect
  omission or truncation, allowing legitimate presentation normalization only;
- first and final substantive source text are present, preventing prefix-only or
  truncated conversion;
- local cross-document and internal links have valid PDF targets, while external
  URI schemes remain intact;
- every page has substantive content except an explicitly designed title page,
  and page numbering is complete; and
- manifest entries, source/PDF hashes and PDF/source mtimes match policy.

Text extraction is the primary machine content check; OCR is neither required nor
accepted as a substitute. The validator records counts for source headings,
blocks, links and PDF pages so evidence can show coverage.

## 12. Rendered visual-validation procedure

After automated validation, rasterize every page locally at no less than 150 dpi.
Create temporary contact sheets for whole-document review and inspect selected
pages at full resolution. Record page numbers and PASS/FAIL observations for both
documents covering:

1. first/title page and title/version treatment;
2. the User Guide Contents and internal navigation;
3. representative prose and nested-list pages;
4. every distinct fenced-code/tree style and representative inline code;
5. every table if any exists at generation time;
6. the longest commands and paths identified from the Markdown;
7. heading, list, code and page transitions near page boundaries;
8. final page and final source text;
9. footer numbering and consistent page geometry; and
10. all-page scan for clipping, overflow, blank pages, missing glyphs, broken
    headings/lists, unreadable code and leaked Markdown syntax.

Use PDF geometry/text bounding boxes as an additional automated clipping check,
but do not present that as a substitute for actual rendered inspection. Temporary
rasters and contact sheets are validation aids and are not committed.

## 13. Privacy and release boundary

Generation must be offline after tool installation and must use only the approved
guides, package metadata and committed rendering assets. Scan commands, logs,
metadata, extracted text, manifests and PDFs for development-machine paths,
credentials, private captures, private locations/GPS, and private maintainer-tool
references. Evidence may contain neutral repository-relative paths and declared
tool versions, but no private filesystem location.

The PDFs and their per-guide manifests are committed repository artifacts. The
later v1.1.0 release ZIP includes the two PDFs only. It excludes the guide
Markdown, repository manifests, generator, validator, TeX/Pandoc configuration
and development dependencies. Stage 9.4 owns ZIP assembly and the external ZIP
checksum.

## 14. CI recommendation and quality gates

No CI change is proposed for v1.1.0. Mandatory regeneration would add a large,
platform-sensitive TeX toolchain to the established four-version runtime matrix.
Checkpoint B instead requires a complete local generation/validation record.
A future lightweight CI check may verify already committed manifest hashes and
PDF structure without regeneration, but it is outside this Stage unless separately
authorised.

B must pass: frozen-source hashes; two-build byte equality; generator and validator
checks; manifest and mtime verification; recorded rendered visual inspection;
Markdown links/fences/navigation; public fixture/history/privacy checks; full
pytest; repository-wide Ruff; configured formatting; direct documentation
whitespace checks; `git diff --check`; installed entry points/version; and full
distribution validation. It must confirm the documentation tooling and generated
artifacts do not enter wheel/sdist contents. Preserve each genuine failure and its
remediation without converting the original result into a pass.

## 15. Individually assessed closure criteria

1. Starting branch, exact commit subject and expected dirty state verified.
2. Pending Stage 9.3a development CHANGELOG row preserved byte-for-byte.
3. Both authoritative Markdown sources exist and match approved SHA-256 values.
4. Stage 9.3a completion and relevant Stage 9 evidence reviewed.
5. Repository PDF tools, scripts, dependencies, ignore rules and artifacts audited.
6. Existing CI and distribution boundaries audited.
7. Markdown feature, link, glyph, length and structure inventory recorded.
8. Existing PDF policy distinguished from prior non-binding proposals.
9. Exact inputs and six-file final user-document set specified.
10. Checkpoint scope, exclusions and A/B boundary specified.
11. Repository wrapper architecture specified.
12. Development-only dependency and declaration policy specified.
13. Runtime, user-installation and distribution isolation specified.
14. Single-authority version and deterministic metadata policy specified.
15. Two-build byte-reproducibility policy specified.
16. Source/PDF timestamp synchronization policy specified.
17. Exact two-entry checksum format and independent verification specified.
18. Layout, typography, navigation, wrapping and page-number policy specified.
19. Machine content-integrity checks specified without OCR dependence.
20. Rendered all-page and representative-page visual procedure specified.
21. Privacy, release-ZIP boundary and CI recommendation specified.
22. Checkpoint A evidence/report and local quality checks pass.
23. Independent review accepts A and explicitly authorises Checkpoint B.
24. Documentation toolchain declaration and installation instructions implemented.
25. Exact tool/font versions and environment recorded.
26. Generator wrapper implemented with fixed input/output mappings.
27. Independent PDF/manifest validator implemented.
28. Generator rejects source/version drift and avoids shell interpolation.
29. Generation uses only local approved inputs and temporary staging.
30. Both PDFs generated without changing either Markdown source or timestamp.
31. User Guide PDF meets layout, navigation and metadata contract.
32. Quick Start PDF meets layout, navigation and metadata contract.
33. All fonts are present, suitable, embedded and cover required glyphs.
34. Two clean builds of each PDF are byte-identical.
35. Each final PDF mtime exactly matches its Markdown source mtime.
36. Each strict two-entry manifest is generated and independently verifies.
37. Automated content-integrity validation passes for both PDFs.
38. Local and external PDF link validation passes.
39. Automated page geometry, blank-page and numbering checks pass.
40. Every page is rendered and visually inspected; required samples are recorded.
41. No clipping, overflow, missing glyph, malformed structure or Markdown leakage remains.
42. Generated artifacts and evidence pass privacy review.
43. Release ZIP inclusion/exclusion and wheel/sdist isolation are verified.
44. Full pytest, Ruff, configured formatting and whitespace gates pass.
45. Markdown navigation, public fixture/history and installed CLI checks pass.
46. Full distribution validation passes with no PDF tooling/artifact leakage.
47. Every genuine failure and remediation is preserved in evidence.
48. Checkpoint B report accounts for every criterion and unresolved defect.
49. No production, test, fixture, runtime dependency or CI change exceeds scope.
50. Independent review accepts technical completion.
51. User approves and creates the closure commit; Codex does not commit or push.
52. Exact post-commit content, cleanliness and required CI are verified.
53. Formal COMPLETE is declared only after every preceding criterion passes.

## 16. Approved Checkpoint B refinements and implementation facts

The independent Checkpoint A review authorised criterion 23 PASS. It explicitly
approved representative prose plus complete heading/command coverage and
sufficient list/table checks instead of constructing a second Markdown renderer.
Section 11 records that approved refinement; neither source contains tables.
The two-build byte-equality requirement remains unchanged. No font binaries may
be copied into the repository. Independent human review is required in addition
to automated and Codex rendered inspection.

The implementation uses Pandoc to produce TeX, then invokes XeLaTeX twice with a
stable relative basename. Direct Pandoc PDF generation produced differing font
subset identifiers because its temporary TeX names differed. Deterministic source
time, UTC and locale alone did not repair that failure. The stable-basename method
produces byte-identical PDFs without post-processing accepted PDF bytes.

MuPDF's `mutool` supplements Poppler to inspect compressed bookmark/action
objects. ImageMagick contact sheets are optional review aids. The tested rendering
environment is declared in `docs/development/PDF_TOOLCHAIN.md`; it uses Homebrew
TeX Live, with explicit TeX font filenames. A later manual BasicTeX installation
is recorded separately and is not claimed as the producer of these artifacts.
The approved PDFs retain Pandoc's restrained default code highlighting; no custom
syntax-colouring system was introduced. All 32 pages have now passed independent
human visual review. That acceptance does not replace independent technical
closure review, user commit, post-commit validation or formal completion.
