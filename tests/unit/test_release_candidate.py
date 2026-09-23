"""Contract tests for release ZIP and external checksum validation."""

import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "tools/validate_release_candidate.py"
SPEC = importlib.util.spec_from_file_location("release_candidate_validation", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


def project() -> dict:
    return {"name": "seestar-toolkit", "version": "1.1.0"}


@pytest.mark.parametrize("defect", [None, "extra", "duplicate", "traversal", "mode"])
def test_release_zip_inventory_rejects_contract_violations(
    tmp_path: Path, defect: str | None
) -> None:
    members = list(validation.expected_members(project()))
    if defect == "extra":
        members.append("seestar-toolkit-1.1.0/private.txt")
    elif defect == "traversal":
        members[0] = "seestar-toolkit-1.1.0/../private.txt"
    release = tmp_path / "release.zip"
    with zipfile.ZipFile(release, "w") as archive:
        for index, name in enumerate(members):
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (0o100600 if defect == "mode" and index == 0 else 0o100644) << 16
            archive.writestr(info, b"fixture")
        if defect == "duplicate":
            archive.writestr(members[0], b"duplicate")
    with zipfile.ZipFile(release) as archive:
        if defect is None:
            validation.validate_zip_members(archive, project())
        else:
            with pytest.raises(AssertionError):
                validation.validate_zip_members(archive, project())


def test_external_checksum_requires_exact_line(tmp_path: Path) -> None:
    release = tmp_path / "release.zip"
    release.write_bytes(b"release")
    checksum = tmp_path / "release.zip.sha256"
    checksum.write_text(f"{validation.sha256(release)}  {release.name}\n")
    validation.validate_checksum(release, checksum)
    checksum.write_text(f"{validation.sha256(release)} *{release.name}\n")
    with pytest.raises(AssertionError):
        validation.validate_checksum(release, checksum)


@pytest.mark.parametrize("defect", ["duplicate", "traversal", "link"])
def test_nested_wheel_rejects_unsafe_members(tmp_path: Path, defect: str) -> None:
    wheel = tmp_path / "fixture.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        name = "../escape.py" if defect == "traversal" else "package/module.py"
        info = zipfile.ZipInfo(name)
        info.create_system = 3
        info.external_attr = (0o120777 if defect == "link" else 0o100644) << 16
        archive.writestr(info, b"fixture")
        if defect == "duplicate":
            archive.writestr(info, b"duplicate")
    with pytest.raises(AssertionError):
        validation.validate_wheel_safety(wheel)


@pytest.mark.parametrize("defect", ["duplicate", "traversal", "link"])
def test_nested_sdist_rejects_unsafe_members(tmp_path: Path, defect: str) -> None:
    sdist = tmp_path / "fixture.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        name = "../escape.py" if defect == "traversal" else "package/module.py"
        info = tarfile.TarInfo(name)
        info.type = tarfile.SYMTYPE if defect == "link" else tarfile.REGTYPE
        data = b"fixture"
        info.size = 0 if defect == "link" else len(data)
        archive.addfile(info, None if defect == "link" else io.BytesIO(data))
        if defect == "duplicate":
            duplicate = tarfile.TarInfo(name)
            duplicate.size = len(data)
            archive.addfile(duplicate, io.BytesIO(data))
    with pytest.raises(AssertionError):
        validation.validate_sdist_safety(sdist)
