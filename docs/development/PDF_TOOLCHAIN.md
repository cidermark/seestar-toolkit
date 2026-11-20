# PDF documentation toolchain

This toolchain is for maintainers generating the committed User Guide and Quick
Start PDFs. It is not required to install or run Seestar Toolkit.

## Tested environment

The approved ENH-007 documentation toolchain uses the following packages on
macOS arm64:

- Pandoc 3.14 at `/opt/homebrew/bin/pandoc`;
- TeX Live 2026/Homebrew (`texlive` 20260301), providing XeTeX
  0.999998 and the TeX Gyre Heros and DejaVu Sans Mono fonts; and
- Poppler 26.09.0, providing `pdfinfo`, `pdftotext`, `pdffonts`,
  `pdftoppm` and `pdftohtml`; and
- MuPDF tools 1.28.4, providing `mutool` for independent bookmark-outline
  inspection that Poppler's command-line tools do not expose.

Install the tested commands without changing shell startup files:

```bash
brew install pandoc poppler texlive mupdf-tools
```

The smaller Homebrew BasicTeX cask was considered first, but its macOS package
installer requires an interactive administrator password. The Homebrew TeX Live
formula was therefore used for the validated non-interactive environment. Do not
add these tools to `pyproject.toml`: they are development/release dependencies.

## Generate and validate

From the repository root:

```bash
python tools/generate_documentation_pdfs.py --all
python tools/validate_documentation_pdfs.py --all
```

The generator has fixed source/output mappings. It performs two clean builds,
requires byte-identical PDFs, validates candidates, installs each PDF atomically,
synchronises its mtime to its Markdown source, writes its two-entry SHA-256
manifest, and then runs final validation.

The current frozen sources are the unreleased ENH-007 development editions,
labelled `Development — ENH-007 (unreleased)` and dated 2026-11-19. This does
not change the published v1.1.0 release, assign a later release version, or
claim formal ENH-007 completion.

The validator is read-only. To create temporary visual-review images outside the
repository:

```bash
python tools/validate_documentation_pdfs.py --all \
  --render-dir /private/tmp/seestar-toolkit-pdf-review
```

Review every rendered page and the generated contact sheets before accepting the
PDFs. Temporary review images are not repository or release artifacts.

## Artifact boundary

Markdown remains authoritative. Never edit a generated PDF as a documentation
source. The PDFs and repository `.sha256` manifests are committed. The later
release ZIP contains the two PDFs, but excludes the Markdown guides, manifests,
generation tools and this development toolchain.

## Provenance and reproducibility details

The failed automated BasicTeX cask installation did not install the cask: it
required interactive administrator authentication. Homebrew `texlive` 20260301
was subsequently installed successfully and generated the accepted PDFs.
The maintainer also installed BasicTeX manually at system level. Its executable
is `/Library/TeX/texbin/xelatex` and reports TeX Live 2026, kpathsea 6.4.2.
The accepted-generation and revalidation logs instead identify TeX Live
2026/Homebrew, selected through `/opt/homebrew/bin/xelatex`. These are distinct
installations; matching XeTeX version numbers do not make their output equivalent.

The generator invokes the approved `/opt/homebrew/bin/pandoc` directly and
rejects any version other than Pandoc 3.14. It also retains strict XeTeX version
checking. This is deliberately not support for arbitrary Pandoc versions and
does not alter shell startup files, PATH, or Homebrew links. Font files are
resolved through TeX Live: TeX Gyre Heros 2.004 and DejaVu Sans Mono 2.34, with
regular/bold variants embedded. No font binary is copied into this repository.

The ENH-007 D-PDF-01 comparison used the same Markdown sources, ENH-007
metadata, Lua filter, LaTeX header, source timestamps, XeTeX engine and render
settings with Pandoc 3.12 and 3.14. All eight clean builds were reproducible.
For both documents, the two versions produced byte-identical PDFs: matching
text, links, bookmarks, fonts, metadata and PDF structure. All 45 rendered
pages were identical, with zero differing pixels. This evidence approves
Pandoc 3.14 for this strict toolchain only; it is not formal ENH-007 closure.

Generation fixes UTC, C.UTF-8, SOURCE_DATE_EPOCH, FORCE_SOURCE_DATE and
SOURCE_DATE_EPOCH_TEX_PRIMITIVES from the source mtime. Pandoc writes TeX to a
stable basename and XeLaTeX runs twice in each clean temporary directory with
shell escape disabled. Stable filenames prevent font-subset identifier drift.
Git does not preserve mtimes: identical PDF bytes are required between builds
with identical source mtimes and this declared toolchain, not across arbitrary
fresh checkouts with different filesystem timestamps.

Optional ImageMagick 7.1.2-31 `montage` creates contact sheets when available;
`pdftoppm` alone supplies all required 150-dpi page images. It was installed as a
Homebrew TeX Live dependency. Current page counts are recorded by final
validation after generation. Temporary review images are removed after
acceptance; rerendering for a later review is optional and does not replace the
PDFs.
