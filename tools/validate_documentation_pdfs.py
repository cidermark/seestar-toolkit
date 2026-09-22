"""Independently validate generated documentation PDFs and manifests."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import subprocess
import tempfile
import tomllib
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_DOCS = ROOT / "docs" / "user"
EXPECTED_HASHES = {
    "SEESTAR_TOOLKIT_USER_GUIDE.md": (
        "fa4f1b3908d1b43b8e71321cf885eacdd6c855c0824536b153da074951525ffa"
    ),
    "SEESTAR_TOOLKIT_QUICK_START.md": (
        "35252f89b8e31c8bbd560188c3a18ceb1d73295ec4fbb3162384ca00d76f4d83"
    ),
}


@dataclass(frozen=True)
class Document:
    source: Path
    pdf: Path
    manifest: Path | None


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)
    return result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def visible(markdown: str) -> str:
    value = html.unescape(markdown)
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"</?br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"[*~`]", "", value)
    value = re.sub(r"^\s*>+\s?", "", value)
    return value.strip()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("---", "—")
    # PDF extraction preserves discretionary end-of-line hyphenation. Joining
    # only a word-character + hyphen + physical newline + word-character keeps
    # intentional in-line hyphens while normalizing that presentation detail.
    value = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", value)
    translations = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
    value = value.translate(translations).lower()
    return " ".join(value.split())


def markdown_inventory(source: Path) -> tuple[list[str], list[str], list[str]]:
    lines = source.read_text(encoding="utf-8").splitlines()
    headings: list[str] = []
    code_blocks: list[str] = []
    prose_blocks: list[str] = []
    paragraph: list[str] = []
    code: list[str] = []
    in_code = False

    def finish_paragraph() -> None:
        if paragraph:
            text = visible(" ".join(paragraph))
            if text:
                prose_blocks.append(text)
            paragraph.clear()

    for line in lines:
        if line.startswith("```"):
            finish_paragraph()
            if in_code:
                text = "\n".join(code).strip()
                if text:
                    code_blocks.append(text)
                code.clear()
            in_code = not in_code
            continue
        if in_code:
            code.append(line)
            continue
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            finish_paragraph()
            headings.append(visible(heading.group(1)))
            continue
        item = re.match(r"^\s*(?:[-+*]|\d+\.)\s+(.+)$", line)
        if item:
            finish_paragraph()
            prose_blocks.append(visible(item.group(1)))
            continue
        if not line.strip():
            finish_paragraph()
            continue
        paragraph.append(line)
    finish_paragraph()
    if in_code:
        raise AssertionError(f"unclosed code fence in {source}")
    return headings, code_blocks, prose_blocks


def assert_in_order(items: list[str], haystack: str, label: str) -> None:
    position = 0
    for item in items:
        needle = normalize(item)
        if not needle:
            continue
        found = haystack.find(needle, position)
        if found < 0:
            raise AssertionError(f"missing or out-of-order {label}: {item!r}")
        position = found + len(needle)


def parse_info(pdf: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in run("pdfinfo", str(pdf)).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def validate_fonts(pdf: Path) -> list[str]:
    lines = run("pdffonts", str(pdf)).splitlines()
    rows = [line.split() for line in lines[2:] if line.strip()]
    if not rows:
        raise AssertionError(f"no fonts reported for {pdf}")
    for row in rows:
        if len(row) < 8 or row[-5] != "yes" or row[-3] != "yes":
            raise AssertionError(f"font not embedded/unicode in {pdf}: {' '.join(row)}")
    names = sorted({re.sub(r"^[A-Z]{6}\+", "", row[0]) for row in rows})
    if not any("TeXGyreHeros" in name for name in names):
        raise AssertionError(f"TeX Gyre Heros absent from {pdf}: {names}")
    if not any("DejaVuSansMono" in name for name in names):
        raise AssertionError(f"DejaVu Sans Mono absent from {pdf}: {names}")
    return names


def validate_geometry(pdf: Path, pages: int) -> None:
    with tempfile.TemporaryDirectory(prefix="seestar-pdf-bbox-") as directory:
        prefix = Path(directory) / "document"
        run("pdftotext", "-bbox-layout", str(pdf), str(prefix.with_suffix(".html")))
        root = ET.parse(prefix.with_suffix(".html")).getroot()
        page_nodes = [node for node in root.iter() if node.tag.endswith("page")]
        if len(page_nodes) != pages:
            raise AssertionError(f"bbox page count mismatch for {pdf}")
        for number, page in enumerate(page_nodes, 1):
            width = float(page.attrib["width"])
            height = float(page.attrib["height"])
            words = [node for node in page.iter() if node.tag.endswith("word")]
            if not words:
                raise AssertionError(f"unexpected blank page {number} in {pdf}")
            for word in words:
                if (
                    float(word.attrib["xMin"]) < -0.1
                    or float(word.attrib["yMin"]) < -0.1
                    or float(word.attrib["xMax"]) > width + 0.1
                    or float(word.attrib["yMax"]) > height + 0.1
                ):
                    raise AssertionError(f"text outside page {number} in {pdf}")


def validate_manifest(document: Document) -> None:
    if document.manifest is None:
        return
    raw = document.manifest.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise AssertionError(f"manifest is not LF-terminated: {document.manifest}")
    lines = raw.decode("utf-8").splitlines()
    expected = [
        f"{sha256(document.source)}  {document.source.name}",
        f"{sha256(document.pdf)}  {document.pdf.name}",
    ]
    if lines != expected:
        raise AssertionError(f"manifest mismatch: {document.manifest}")
    if document.pdf.stat().st_mtime_ns != document.source.stat().st_mtime_ns:
        raise AssertionError(f"PDF/source mtime mismatch: {document.pdf}")


def validate_document(document: Document) -> dict[str, object]:
    expected_source_hash = EXPECTED_HASHES.get(document.source.name)
    if expected_source_hash is None or sha256(document.source) != expected_source_hash:
        raise AssertionError(f"unapproved Markdown source: {document.source}")
    if not document.pdf.read_bytes().startswith(b"%PDF-"):
        raise AssertionError(f"invalid PDF signature: {document.pdf}")
    if b"%%EOF" not in document.pdf.read_bytes()[-2048:]:
        raise AssertionError(f"missing PDF EOF marker: {document.pdf}")

    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    version = project["version"]
    title = document.source.read_text(encoding="utf-8").splitlines()[0][2:]
    info = parse_info(document.pdf)
    if info.get("Title") != title:
        raise AssertionError(f"PDF title mismatch: {info.get('Title')!r}")
    if info.get("Author") != project["authors"][0]["name"]:
        raise AssertionError(f"PDF author mismatch: {info.get('Author')!r}")
    if version not in info.get("Subject", "") or version not in info.get("Keywords", ""):
        raise AssertionError(f"PDF version metadata mismatch: {document.pdf}")
    if info.get("Encrypted") != "no":
        raise AssertionError(f"encrypted PDF: {document.pdf}")
    pages = int(info["Pages"])
    if pages < 2:
        raise AssertionError(f"implausible page count: {document.pdf}")
    size = info.get("Page size", "")
    dimensions = re.search(r"([0-9.]+) x ([0-9.]+) pts \(A4\)", size)
    if not dimensions or not (
        594.0 <= float(dimensions.group(1)) <= 596.0
        and 841.0 <= float(dimensions.group(2)) <= 843.0
    ):
        raise AssertionError(f"non-A4 page size: {size}")

    extracted = run("pdftotext", "-layout", str(document.pdf), "-")
    extracted_pages = extracted.split("\f")[:-1]
    if len(extracted_pages) != pages:
        raise AssertionError(f"extracted page count mismatch: {document.pdf}")
    for number, page_text in enumerate(extracted_pages, 1):
        nonempty = [line.strip() for line in page_text.splitlines() if line.strip()]
        if not nonempty or nonempty[-1] != str(number):
            raise AssertionError(f"missing footer page number {number}: {document.pdf}")
    normalized_pdf = normalize(extracted)
    headings, code_blocks, prose_blocks = markdown_inventory(document.source)
    # Ordered extracted headings are supplemented by the exact bookmark outline
    # and ordered command coverage below; Contents text alone is insufficient.
    body_position = 0
    for heading in headings:
        needle = normalize(heading)
        found = normalized_pdf.find(needle, body_position)
        if found < 0:
            raise AssertionError(f"missing heading: {heading!r}")
        body_position = found + len(needle)
    code_lines = [line for block in code_blocks for line in block.splitlines() if normalize(line)]
    assert_in_order(code_lines, normalized_pdf, "fenced code line")
    representative = [p for p in prose_blocks if len(normalize(p)) >= 30][::8]
    for prose in representative:
        if normalize(prose) not in normalized_pdf:
            raise AssertionError(f"missing representative prose: {prose[:80]!r}")
    # Check every list item's opening text, in addition to representative prose
    # and all code. Neither approved source contains tables.
    list_items: list[str] = []
    in_code = False
    for line in document.source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code and (item := re.match(r"^\s*(?:[-+*]|\d+\.)\s+(.+)$", line)):
            list_items.append(visible(item.group(1)))
    for item in list_items:
        if normalize(item) not in normalized_pdf:
            raise AssertionError(f"missing list content: {item!r}")
    for opening in prose_blocks[:2]:
        if normalize(opening) not in normalized_pdf:
            raise AssertionError(f"opening source content missing: {opening!r}")
    if normalize(visible(document.source.read_text().splitlines()[-1])) not in normalized_pdf:
        raise AssertionError(f"final source content missing from {document.pdf}")
    if re.search(r"(?m)^#{1,6}\s+\S", extracted) or "```" in extracted:
        raise AssertionError(f"obvious Markdown syntax leaked into {document.pdf}")

    fonts = validate_fonts(document.pdf)
    validate_geometry(document.pdf, pages)
    destinations = run("pdfinfo", "-dests", str(document.pdf))
    if len([line for line in destinations.splitlines() if line.strip()]) < len(headings):
        raise AssertionError(f"insufficient named destinations in {document.pdf}")
    outline = run("mutool", "show", str(document.pdf), "outline")
    outline_titles = re.findall(r'^.*?"(.*)"\s+#', outline, flags=re.MULTILINE)
    expected_outline = headings[1:]
    if [normalize(value) for value in outline_titles] != [
        normalize(value) for value in expected_outline
    ]:
        raise AssertionError(f"PDF bookmark outline mismatch: {document.pdf}")

    with tempfile.TemporaryDirectory(prefix="seestar-pdf-links-") as directory:
        html_file = Path(directory) / "document.html"
        run("pdftohtml", "-i", "-noframes", str(document.pdf), str(html_file))
        rendered_html = html_file.read_text(encoding="utf-8", errors="replace")
        rendered_links = re.findall(r'href="([^"]+)"', rendered_html)
        source_links = re.findall(
            r"(?<!!)\[[^\]]+\]\(([^)]+)\)",
            document.source.read_text(encoding="utf-8"),
        )
        if len(rendered_links) < len(source_links):
            raise AssertionError(f"PDF link annotation count is too low: {document.pdf}")
        if document.source.name.endswith("QUICK_START.md"):
            if "SEESTAR_TOOLKIT_USER_GUIDE.pdf" not in rendered_html:
                raise AssertionError("Quick Start cross-document PDF link missing")
        else:
            if "SEESTAR_TOOLKIT_QUICK_START.pdf" not in rendered_html:
                raise AssertionError("User Guide cross-document PDF link missing")

    # Inspect actual PDF actions, rather than counting HTML outline links as
    # annotations. Every internal destination must resolve to an existing page.
    objects = run("mutool", "show", str(document.pdf), "grep")
    destination_names = set(re.findall(r'"([^"\n]+)"', destinations))
    actions = [line for line in objects.splitlines() if "/Subtype/Link" in line]
    if len(actions) < len(source_links):
        raise AssertionError("missing PDF link annotations")
    for action in actions:
        if "/S/GoToR" in action:
            match = re.search(r"/F\(([^)]+)\)", action)
            if not match or not (USER_DOCS / match.group(1)).is_file():
                raise AssertionError(f"unresolved cross-document link: {action}")
        elif "/S/GoTo" in action:
            match = re.search(r"/D\(([^)]+)\)", action)
            if not match or match.group(1) not in destination_names:
                raise AssertionError(f"unresolved internal link: {action}")
        elif "/S/URI" not in action:
            raise AssertionError(f"unrecognized PDF link action: {action}")
    for uri in (link for link in source_links if link.startswith(("https:", "http:", "mailto:"))):
        if f"/URI({uri})" not in objects:
            raise AssertionError(f"external URI changed: {uri}")

    private_markers = ("/Users/", "/home/", "BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY")
    for marker in private_markers:
        if marker in extracted or any(marker in value for value in info.values()):
            raise AssertionError(f"private marker {marker!r} in {document.pdf}")
    validate_manifest(document)
    return {
        "source": document.source.name,
        "pdf": document.pdf.name,
        "sha256": sha256(document.pdf),
        "pages": pages,
        "title": info["Title"],
        "author": info["Author"],
        "subject": info["Subject"],
        "fonts": fonts,
        "headings": len(headings),
        "code_blocks": len(code_blocks),
        "representative_prose_blocks": len(representative),
        "bookmarks": len(outline_titles),
        "list_items": len(list_items),
        "source_links": len(source_links),
        "rendered_html_links": len(rendered_links),
        "pdf_link_annotations": len(actions),
    }


def render(document: Document, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    prefix = target / document.pdf.stem
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", str(document.pdf), str(prefix)],
        cwd=ROOT,
        check=True,
    )
    pngs = sorted(target.glob(f"{document.pdf.stem}-*.png"))
    if not pngs:
        raise AssertionError(f"no rendered pages for {document.pdf}")
    montage = shutil.which("montage")
    if montage:
        contact_font = run("kpsewhich", "DejaVuSans.ttf").strip()
        subprocess.run(
            [
                montage,
                "-font",
                contact_font,
                *map(str, pngs),
                "-thumbnail",
                "240x",
                "-tile",
                "4x",
                "-geometry",
                "+8+8",
                str(target / f"{document.pdf.stem}-contact-sheet.png"),
            ],
            check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--candidate", nargs=2, metavar=("MARKDOWN", "PDF"))
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    for command in (
        "pdfinfo",
        "pdftotext",
        "pdffonts",
        "pdftoppm",
        "pdftohtml",
        "mutool",
    ):
        if shutil.which(command) is None:
            raise SystemExit(f"required validation command not found: {command}")

    if args.candidate:
        source, pdf = map(Path, args.candidate)
        documents = [Document(source.resolve(), pdf.resolve(), None)]
    else:
        documents = [
            Document(source, source.with_suffix(".pdf"), source.with_suffix(".sha256"))
            for source in (USER_DOCS / name for name in EXPECTED_HASHES)
        ]
    for document in documents:
        result = validate_document(document)
        print(result)
        if args.render_dir:
            render(document, args.render_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
