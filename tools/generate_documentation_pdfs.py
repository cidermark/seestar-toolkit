"""Generate the two authoritative documentation PDFs reproducibly."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_DOCS = ROOT / "docs" / "user"
HEADER = ROOT / "tools" / "documentation_pdf_header.tex"
FILTER = ROOT / "tools" / "documentation_pdf_filter.lua"


@dataclass(frozen=True)
class Document:
    source: Path
    pdf: Path
    manifest: Path
    expected_hash: str
    title: str


DOCUMENTS = (
    Document(
        USER_DOCS / "SEESTAR_TOOLKIT_USER_GUIDE.md",
        USER_DOCS / "SEESTAR_TOOLKIT_USER_GUIDE.pdf",
        USER_DOCS / "SEESTAR_TOOLKIT_USER_GUIDE.sha256",
        "fa4f1b3908d1b43b8e71321cf885eacdd6c855c0824536b153da074951525ffa",
        "Seestar Toolkit User Guide",
    ),
    Document(
        USER_DOCS / "SEESTAR_TOOLKIT_QUICK_START.md",
        USER_DOCS / "SEESTAR_TOOLKIT_QUICK_START.pdf",
        USER_DOCS / "SEESTAR_TOOLKIT_QUICK_START.sha256",
        "35252f89b8e31c8bbd560188c3a18ceb1d73295ec4fbb3162384ca00d76f4d83",
        "Seestar Toolkit Quick Start",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_metadata() -> tuple[str, str]:
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]
    return project["version"], project["authors"][0]["name"]


def require_tools() -> None:
    for command in ("pandoc", "xelatex", "pdfinfo", "pdftotext", "pdffonts", "pdftohtml", "mutool"):
        if shutil.which(command) is None:
            raise SystemExit(f"required documentation command not found: {command}")

    expected = {
        "pandoc": "pandoc 3.11",
        "xelatex": "XeTeX 3.141592653-2.6-0.999998 (TeX Live 2026/Homebrew)",
    }
    for command, first_line in expected.items():
        result = subprocess.run([command, "--version"], check=True, capture_output=True, text=True)
        if result.stdout.splitlines()[0] != first_line:
            raise SystemExit(
                f"unvalidated {command} version; see docs/development/PDF_TOOLCHAIN.md"
            )


def validate_source(document: Document, version: str) -> None:
    actual_hash = sha256(document.source)
    if actual_hash != document.expected_hash:
        raise SystemExit(f"frozen source hash mismatch for {document.source}: {actual_hash}")
    text = document.source.read_text(encoding="utf-8")
    if not text.startswith(f"# {document.title}\n\n**Version {version} --- Unreleased**\n"):
        raise SystemExit(f"title/version mismatch in {document.source}")


def build(document: Document, output: Path, version: str, author: str) -> None:
    epoch = str(document.source.stat().st_mtime_ns // 1_000_000_000)
    environment = os.environ.copy()
    environment.update(
        {
            "SOURCE_DATE_EPOCH": epoch,
            "FORCE_SOURCE_DATE": "1",
            "SOURCE_DATE_EPOCH_TEX_PRIMITIVES": "1",
            "TZ": "UTC",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "XDG_CACHE_HOME": str(output.parent / "cache"),
        }
    )
    tex_source = output.with_suffix(".tex")
    pandoc_command = [
        "pandoc",
        str(document.source),
        "--from=gfm+smart",
        "--standalone",
        "--pdf-engine=xelatex",
        f"--lua-filter={FILTER}",
        f"--include-in-header={HEADER}",
        "--metadata",
        f"author={author}",
        "--metadata",
        f"subject=Seestar Toolkit {version} documentation",
        "--metadata",
        f"keywords=Seestar Toolkit, {version}, documentation",
        "--variable",
        "papersize=a4",
        "--variable",
        "fontsize=11pt",
        "--variable",
        "geometry:top=20mm,bottom=20mm,left=20mm,right=20mm",
        "--variable",
        "colorlinks=true",
        "--variable",
        "linkcolor=blue",
        "--variable",
        "urlcolor=blue",
        "--output",
        str(tex_source),
    ]
    subprocess.run(pandoc_command, cwd=ROOT, env=environment, check=True)
    latex_command = [
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-no-shell-escape",
        tex_source.name,
    ]
    # Two passes resolve page references, bookmarks and internal links. Running
    # XeLaTeX directly with a stable basename avoids Pandoc's random temporary
    # TeX filename becoming part of embedded font subset identifiers.
    for _ in range(2):
        result = subprocess.run(
            latex_command,
            cwd=output.parent,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if result.returncode:
            raise SystemExit(result.stdout)


def validate_candidate(document: Document, pdf: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "validate_documentation_pdfs.py"),
            "--candidate",
            str(document.source),
            str(pdf),
        ],
        cwd=ROOT,
        check=True,
    )


def install_artifact(document: Document, candidate: Path) -> None:
    staged = document.pdf.with_name(f".{document.pdf.name}.tmp")
    try:
        shutil.copyfile(candidate, staged)
        os.replace(staged, document.pdf)
    finally:
        staged.unlink(missing_ok=True)
    source_mtime = document.source.stat().st_mtime_ns
    os.utime(document.pdf, ns=(source_mtime, source_mtime))
    if document.pdf.stat().st_mtime_ns != source_mtime:
        raise SystemExit(f"PDF/source mtime mismatch for {document.pdf}")

    manifest_text = (
        f"{sha256(document.source)}  {document.source.name}\n"
        f"{sha256(document.pdf)}  {document.pdf.name}\n"
    )
    staged_manifest = document.manifest.with_name(f".{document.manifest.name}.tmp")
    try:
        staged_manifest.write_text(manifest_text, encoding="utf-8", newline="\n")
        os.replace(staged_manifest, document.manifest)
    finally:
        staged_manifest.unlink(missing_ok=True)


def generate(document: Document, version: str, author: str) -> None:
    validate_source(document, version)
    with (
        tempfile.TemporaryDirectory(prefix="seestar-pdf-build-") as first_dir,
        tempfile.TemporaryDirectory(prefix="seestar-pdf-build-") as second_dir,
    ):
        first = Path(first_dir) / document.pdf.name
        second = Path(second_dir) / document.pdf.name
        build(document, first, version, author)
        build(document, second, version, author)
        first_hash = sha256(first)
        second_hash = sha256(second)
        print(f"{document.pdf.name} build 1 SHA-256: {first_hash}")
        print(f"{document.pdf.name} build 2 SHA-256: {second_hash}")
        if first_hash != second_hash:
            raise SystemExit(f"non-reproducible PDF builds for {document.pdf.name}")
        validate_candidate(document, second)
        install_artifact(document, second)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all", action="store_true", help="Generate both fixed documentation PDFs."
    )
    args = parser.parse_args()
    if not args.all:
        parser.error("--all is required")
    require_tools()
    version, author = package_metadata()
    for document in DOCUMENTS:
        generate(document, version, author)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "validate_documentation_pdfs.py"),
            "--all",
        ],
        cwd=ROOT,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
