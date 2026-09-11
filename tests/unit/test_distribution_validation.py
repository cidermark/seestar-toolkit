"""Regression checks that distribution inspection rejects unsafe/incomplete wheels."""

import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "tools/validate_distribution.py"
SPEC = importlib.util.spec_from_file_location("distribution_validation", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


@pytest.mark.parametrize("defect", [None, "extra", "missing", "version", "path", "dependency"])
def test_distribution_inspection_rejects_contract_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str | None
) -> None:
    monkeypatch.setattr(validation, "ROOT", tmp_path)
    (tmp_path / "README.md").write_text("Public description\n")
    (tmp_path / "LICENSE").write_text("MIT license fixture\n")
    project = {
        "name": "seestar-toolkit",
        "version": "1.1.0",
        "requires-python": ">=3.11",
        "dependencies": ["numpy>=2.0"],
    }
    prefix = "seestar_toolkit-1.1.0.dist-info/"
    metadata = (
        "Metadata-Version: 2.4\nName: seestar-toolkit\nVersion: 1.1.0\n"
        "Author: Mark Wymer\nLicense-Expression: MIT\nRequires-Python: >=3.11\n"
        "Requires-Dist: numpy>=2.0\nProvides-Extra: dev\nProvides-Extra: build\n"
        "\nPublic description\n"
    )
    members = {
        "seestar_toolkit/__init__.py": "# package\n",
        prefix + "METADATA": metadata,
        prefix + "licenses/LICENSE": "MIT license fixture\n",
        prefix
        + "entry_points.txt": "[console_scripts]\nseestar-toolkit = seestar_toolkit.cli:main\n",
    }
    if defect == "extra":
        members["private/data.fit"] = "not allowed"
    elif defect == "missing":
        del members["seestar_toolkit/__init__.py"]
    elif defect == "version":
        members[prefix + "METADATA"] = metadata.replace("Version: 1.1.0", "Version: 2.0.0")
    elif defect == "path":
        members["seestar_toolkit/__init__.py"] = "# /Users/synthetic/private-path\n"
    elif defect == "dependency":
        members[prefix + "METADATA"] = metadata.replace("numpy>=2.0", "pytest>=8.0")
    wheel = tmp_path / "test.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    if defect is None:
        validation.inspect_archive(wheel, project, {"seestar_toolkit/__init__.py"})
    else:
        with pytest.raises(AssertionError):
            validation.inspect_archive(wheel, project, {"seestar_toolkit/__init__.py"})
