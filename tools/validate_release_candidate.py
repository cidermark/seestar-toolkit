"""Independently validate the fixed Seestar Toolkit release candidate."""

from __future__ import annotations

import argparse
import hashlib
import stat
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_distribution import inspect_archive, smoke  # noqa: E402

PRIVATE_MARKERS = (
    b"/Users/",
    b"/home/",
    b"com~apple~CloudDocs",
    b"BEGIN PRIVATE KEY",
    b"BEGIN RSA PRIVATE KEY",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_bytes(source_ref: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{source_ref}:{path}"], cwd=ROOT)


def project_at(source_ref: str) -> dict:
    return tomllib.loads(git_bytes(source_ref, "pyproject.toml").decode())["project"]


def release_names(project: dict) -> tuple[str, str, str, str, str]:
    version = project["version"]
    distribution = project["name"].replace("-", "_")
    root = f"{project['name']}-{version}"
    return (
        root,
        f"{distribution}-{version}-py3-none-any.whl",
        f"{distribution}-{version}.tar.gz",
        f"{root}-release.zip",
        f"{root}-release.zip.sha256",
    )


def expected_members(project: dict) -> tuple[str, ...]:
    root, wheel, sdist, _, _ = release_names(project)
    basenames = (
        "SEESTAR_TOOLKIT_QUICK_START.pdf",
        "SEESTAR_TOOLKIT_USER_GUIDE.pdf",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        wheel,
        sdist,
    )
    return tuple(f"{root}/{name}" for name in basenames)


def validate_zip_members(archive: zipfile.ZipFile, project: dict) -> None:
    infos = archive.infolist()
    names = [entry.filename for entry in infos]
    if len(names) != len(set(names)):
        raise AssertionError("duplicate release ZIP member")
    if tuple(names) != expected_members(project):
        raise AssertionError(f"release ZIP inventory/order mismatch: {names}")
    for entry in infos:
        path = PurePosixPath(entry.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in entry.filename:
            raise AssertionError(f"unsafe release ZIP path: {entry.filename}")
        mode = entry.external_attr >> 16
        if not stat.S_ISREG(mode) or stat.S_IMODE(mode) != 0o644:
            raise AssertionError(f"unsafe release ZIP mode: {entry.filename}: {oct(mode)}")
        if entry.create_system != 3:
            raise AssertionError(f"non-POSIX release ZIP member: {entry.filename}")


def validate_checksum(candidate: Path, checksum: Path) -> None:
    raw = checksum.read_bytes()
    expected = f"{sha256(candidate)}  {candidate.name}\n".encode()
    if raw != expected:
        raise AssertionError("external release checksum is not the exact required line")


def validate_sdist_safety(sdist: Path) -> None:
    with tarfile.open(sdist) as archive:
        names: set[str] = set()
        for member in archive.getmembers():
            if member.name in names:
                raise AssertionError(f"duplicate sdist member: {member.name}")
            names.add(member.name)
            path = PurePosixPath(member.name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in member.name
                or not (member.isfile() or member.isdir())
            ):
                raise AssertionError(f"unsafe sdist member: {member.name}")


def validate_wheel_safety(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        infos = archive.infolist()
        names = [member.filename for member in infos]
        if len(names) != len(set(names)):
            raise AssertionError("duplicate wheel member")
        for member in infos:
            path = PurePosixPath(member.filename)
            mode = member.external_attr >> 16
            if path.is_absolute() or ".." in path.parts or "\\" in member.filename:
                raise AssertionError(f"unsafe wheel member: {member.filename}")
            if mode and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise AssertionError(f"unsafe wheel member type: {member.filename}")


def validate_release_documents(files: dict[str, bytes], project: dict) -> None:
    changelog = files["CHANGELOG.md"].decode()
    if "## [1.1.0] - Unreleased" not in changelog:
        raise AssertionError("public CHANGELOG is not v1.1.0 Unreleased")
    readme = files["README.md"].decode()
    required_readme = (
        "Individual light FITS files remain in `lights/` without automatic TIFF",
        "its required TIFF\ncompanion is generated beside it in `seestar_stacked/`",
        "--dry-run --source-action copy",
    )
    for text in required_readme:
        if text not in readme:
            raise AssertionError(f"missing release-facing archive statement: {text!r}")
    if project["version"] != "1.1.0":
        raise AssertionError(f"unexpected release version: {project['version']}")


def validate_candidate(candidate: Path, checksum: Path, source_ref: str) -> dict[str, object]:
    source_ref = subprocess.check_output(
        ["git", "rev-parse", f"{source_ref}^{{commit}}"], cwd=ROOT, text=True
    ).strip()
    project = project_at(source_ref)
    root_name, wheel_name, sdist_name, zip_name, checksum_name = release_names(project)
    if candidate.name != zip_name or checksum.name != checksum_name:
        raise AssertionError("release artifact filename mismatch")
    validate_checksum(candidate, checksum)

    with tempfile.TemporaryDirectory(prefix="seestar-release-validation-") as directory:
        work = Path(directory)
        with zipfile.ZipFile(candidate) as archive:
            validate_zip_members(archive, project)
            archive.extractall(work)
        root = work / root_name
        if not root.is_dir():
            raise AssertionError("missing release root directory")
        actual = {p.name for p in root.iterdir() if p.is_file()}
        expected = {PurePosixPath(name).name for name in expected_members(project)}
        if actual != expected or any(p.is_dir() for p in root.iterdir()):
            raise AssertionError(f"extracted release inventory mismatch: {sorted(actual)}")

        source_map = {
            "README.md": "README.md",
            "CHANGELOG.md": "CHANGELOG.md",
            "LICENSE": "LICENSE",
            "SEESTAR_TOOLKIT_QUICK_START.pdf": ("docs/user/SEESTAR_TOOLKIT_QUICK_START.pdf"),
            "SEESTAR_TOOLKIT_USER_GUIDE.pdf": "docs/user/SEESTAR_TOOLKIT_USER_GUIDE.pdf",
        }
        release_files: dict[str, bytes] = {}
        for release_name, source_name in source_map.items():
            data = (root / release_name).read_bytes()
            if data != git_bytes(source_ref, source_name):
                raise AssertionError(f"release input differs from {source_ref}: {release_name}")
            if any(marker in data for marker in PRIVATE_MARKERS):
                raise AssertionError(f"private marker in release input: {release_name}")
            release_files[release_name] = data
        validate_release_documents(release_files, project)

        wheel = root / wheel_name
        sdist = root / sdist_name
        modules = {
            str(path.relative_to(ROOT / "src"))
            for path in (ROOT / "src/seestar_toolkit").rglob("*.py")
        }
        inspect_archive(wheel, project, modules)
        inspect_archive(sdist, project, modules)
        validate_wheel_safety(wheel)
        validate_sdist_safety(sdist)
        smoke(wheel, work / "wheel-install")
        smoke(sdist, work / "sdist-install")

        for markdown, pdf in (
            ("SEESTAR_TOOLKIT_QUICK_START.md", "SEESTAR_TOOLKIT_QUICK_START.pdf"),
            ("SEESTAR_TOOLKIT_USER_GUIDE.md", "SEESTAR_TOOLKIT_USER_GUIDE.pdf"),
        ):
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/validate_documentation_pdfs.py"),
                    "--candidate",
                    str(ROOT / "docs/user" / markdown),
                    str(root / pdf),
                ],
                cwd=ROOT,
                check=True,
            )

        return {
            "source_commit": source_ref,
            "release_zip": candidate.name,
            "release_zip_bytes": candidate.stat().st_size,
            "release_zip_sha256": sha256(candidate),
            "checksum_file_sha256": sha256(checksum),
            "wheel": wheel.name,
            "wheel_bytes": wheel.stat().st_size,
            "wheel_sha256": sha256(wheel),
            "sdist": sdist.name,
            "sdist_bytes": sdist.stat().st_size,
            "sdist_sha256": sha256(sdist),
            "members": sorted(actual),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    parser.add_argument("--source-ref", required=True)
    args = parser.parse_args()
    result = validate_candidate(args.zip.resolve(), args.checksum.resolve(), args.source_ref)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
