"""Build the fixed, reproducible Seestar Toolkit release candidate."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_release_candidate import (  # noqa: E402
    expected_members,
    release_names,
    validate_candidate,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_source(source_ref: str, destination: Path) -> None:
    archive = destination.parent / f"{destination.name}.tar"
    with archive.open("wb") as stream:
        subprocess.run(
            ["git", "archive", "--format=tar", source_ref], cwd=ROOT, stdout=stream, check=True
        )
    destination.mkdir()
    with tarfile.open(archive) as source:
        source.extractall(destination, filter="data")
    archive.unlink()


def build_distributions(source_ref: str, directory: Path, epoch: int) -> tuple[Path, Path]:
    directory.mkdir(parents=True)
    source = directory / "source"
    export_source(source_ref, source)
    project = tomllib.loads((source / "pyproject.toml").read_text())["project"]
    _, wheel_name, sdist_name, _, _ = release_names(project)
    output = directory / "dist"
    environment = os.environ.copy()
    environment.update(
        {
            "SOURCE_DATE_EPOCH": str(epoch),
            "PYTHONHASHSEED": "0",
            "TZ": "UTC",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
    )
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(output)],
        cwd=source,
        env=environment,
        check=True,
    )
    if {path.name for path in output.iterdir()} != {wheel_name, sdist_name}:
        raise AssertionError("fresh build did not produce the exact wheel/sdist inventory")
    normalize_sdist(output / sdist_name, epoch)
    return output / wheel_name, output / sdist_name


def normalize_sdist(sdist: Path, epoch: int) -> None:
    """Replace variable gzip/tar metadata with the release epoch and fixed ownership."""
    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    with tarfile.open(sdist, "r:gz") as source:
        for member in source.getmembers():
            if not (member.isfile() or member.isdir()):
                raise AssertionError(f"unsupported sdist member type: {member.name}")
            data = source.extractfile(member).read() if member.isfile() else None
            entries.append((member, data))

    temporary = sdist.with_suffix(".normalized")
    with (
        temporary.open("wb") as raw,
        gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=epoch, compresslevel=9) as zipped,
        tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as target,
    ):
        for original, data in sorted(entries, key=lambda entry: entry[0].name):
            member = tarfile.TarInfo(original.name)
            member.type = tarfile.DIRTYPE if original.isdir() else tarfile.REGTYPE
            member.mode = 0o755 if original.isdir() else 0o644
            member.mtime = epoch
            member.uid = 0
            member.gid = 0
            member.uname = "root"
            member.gname = "root"
            if data is not None:
                member.size = len(data)
                target.addfile(member, io.BytesIO(data))
            else:
                target.addfile(member)
    temporary.replace(sdist)


def zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    value = dt.datetime.fromtimestamp(epoch, tz=dt.UTC)
    year = max(value.year, 1980)
    return year, value.month, value.day, value.hour, value.minute, value.second // 2 * 2


def write_zip(destination: Path, members: list[tuple[str, Path]], epoch: int) -> None:
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True
    ) as archive:
        for name, source in members:
            info = zipfile.ZipInfo(name, date_time=zip_datetime(epoch))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(
                info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )


def assemble_once(source_ref: str, build_root: Path, output: Path, epoch: int) -> dict[str, Path]:
    project = tomllib.loads(
        subprocess.check_output(["git", "show", f"{source_ref}:pyproject.toml"], cwd=ROOT).decode()
    )["project"]
    release_root, wheel_name, sdist_name, zip_name, checksum_name = release_names(project)
    wheel, sdist = build_distributions(source_ref, build_root, epoch)
    sources = {
        "SEESTAR_TOOLKIT_QUICK_START.pdf": ROOT / "docs/user/SEESTAR_TOOLKIT_QUICK_START.pdf",
        "SEESTAR_TOOLKIT_USER_GUIDE.pdf": ROOT / "docs/user/SEESTAR_TOOLKIT_USER_GUIDE.pdf",
        "README.md": ROOT / "README.md",
        "CHANGELOG.md": ROOT / "CHANGELOG.md",
        "LICENSE": ROOT / "LICENSE",
        wheel_name: wheel,
        sdist_name: sdist,
    }
    for release_name, repository_path in (
        ("README.md", "README.md"),
        ("CHANGELOG.md", "CHANGELOG.md"),
        ("LICENSE", "LICENSE"),
        ("SEESTAR_TOOLKIT_QUICK_START.pdf", "docs/user/SEESTAR_TOOLKIT_QUICK_START.pdf"),
        ("SEESTAR_TOOLKIT_USER_GUIDE.pdf", "docs/user/SEESTAR_TOOLKIT_USER_GUIDE.pdf"),
    ):
        committed = subprocess.check_output(
            ["git", "show", f"{source_ref}:{repository_path}"], cwd=ROOT
        )
        if sources[release_name].read_bytes() != committed:
            raise AssertionError(
                f"working release input differs from {source_ref}: {repository_path}"
            )
    ordered = [(name, sources[Path(name).name]) for name in expected_members(project)]
    output.mkdir()
    candidate = output / zip_name
    write_zip(candidate, ordered, epoch)
    checksum = output / checksum_name
    checksum.write_text(f"{sha256(candidate)}  {candidate.name}\n", encoding="utf-8", newline="\n")
    return {"wheel": wheel, "sdist": sdist, "zip": candidate, "checksum": checksum}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source_ref = subprocess.check_output(
        ["git", "rev-parse", f"{args.source_ref}^{{commit}}"], cwd=ROOT, text=True
    ).strip()
    if (
        source_ref
        != subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    ):
        raise SystemExit("source-ref must resolve to the checked-out committed HEAD")
    output = args.output_dir.resolve()
    if output.exists():
        raise SystemExit(f"output directory already exists: {output}")
    epoch = int(
        subprocess.check_output(
            ["git", "show", "-s", "--format=%ct", source_ref], cwd=ROOT, text=True
        ).strip()
    )
    with tempfile.TemporaryDirectory(prefix="seestar-release-build-") as temporary:
        work = Path(temporary)
        first = assemble_once(source_ref, work / "first-build", work / "first-output", epoch)
        second = assemble_once(source_ref, work / "second-build", work / "second-output", epoch)
        for name in ("wheel", "sdist", "zip", "checksum"):
            if sha256(first[name]) != sha256(second[name]):
                raise SystemExit(f"non-reproducible release artifact: {name}")
        output.mkdir(parents=True)
        accepted_zip = output / second["zip"].name
        accepted_checksum = output / second["checksum"].name
        shutil.copyfile(second["zip"], accepted_zip)
        shutil.copyfile(second["checksum"], accepted_checksum)
    result = validate_candidate(accepted_zip, accepted_checksum, source_ref)
    print("PASS: two independent release builds are byte-identical")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
