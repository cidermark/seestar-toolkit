"""Document-aware scalar configuration contracts, using only synthetic files."""

import os
import stat
from pathlib import Path
from unittest.mock import Mock

import pytest
import tomlkit

from seestar_toolkit.archive import ArchiveConfigError, load_archive_config
from seestar_toolkit.archive import config_document as management


def _read(tmp_path, text):
    path = tmp_path / "config.toml"
    path.write_text(text)
    return management.read_config_document(path)


def _fingerprint(path):
    return path.read_bytes(), path.stat().st_mtime_ns, stat.S_IMODE(path.stat().st_mode)


def test_effective_provenance_and_saved_unknown_entries(tmp_path):
    document = _read(
        tmp_path, '# note\n[archive]\nsource_action="copy" # keep\nfuture=42\n[other]\nx=1\n'
    )
    inspection = management.inspect_config_document(document)
    settings = {s.name: s for s in inspection.settings}
    assert settings["archive.source_action"].source == "saved"
    assert settings["archive.collision_policy"].source == "default"
    assert len(settings) == 3
    assert document.raw["other"]["x"] == 1
    assert not inspection.errors


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        (
            "hierarchy",
            "{location}/{target}/{session_end_date}",
            "{location}/{target}/{session_end_date}",
        ),
        ("source_action", "MOVE", "move"),
        ("collision_policy", "overwrite", "overwrite"),
    ],
)
def test_scalar_set_preserves_comments_unknown_tables_and_permissions(
    tmp_path, key, value, expected
):
    document = _read(tmp_path, '# heading\n[archive]\nfuture=42 # future\n[custom]\nx="stay"\n')
    document.path.chmod(0o640)
    document = management.read_config_document(document.path)
    edit = management.prepare_archive_edit(document, f"archive.{key}", value)
    management.persist_config_edit(edit)
    text = document.path.read_text()
    assert "# heading" in text and "future=42 # future" in text and 'x="stay"' in text
    assert tomlkit.parse(text)["archive"][key] == expected
    assert stat.S_IMODE(document.path.stat().st_mode) == 0o640
    edit = management.prepare_archive_edit(
        management.read_config_document(document.path), f"archive.{key}"
    )
    management.persist_config_edit(edit)
    assert key not in tomlkit.parse(document.path.read_text())["archive"]


def test_missing_default_inspection_and_unset_do_not_create_then_set_creates_private_file(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    document = management.read_config_document()
    assert not document.exists
    assert not management.prepare_archive_edit(document, "archive.source_action").changed
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action")
    )
    assert not (tmp_path / ".config").exists()
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action", "copy")
    )
    assert stat.S_IMODE(document.path.stat().st_mode) == 0o600
    assert load_archive_config().source_action.name == "COPY"


@pytest.mark.parametrize("value", ["copy", "COPY"])
def test_same_policy_is_byte_and_timestamp_preserving_noop(tmp_path, value):
    document = _read(tmp_path, '[archive]\nsource_action = "COPY" # preserve case/comment\n')
    before = _fingerprint(document.path)
    edit = management.prepare_archive_edit(document, "archive.source_action", value)
    assert not edit.changed
    management.persist_config_edit(edit)
    assert _fingerprint(document.path) == before


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("archive.hierarchy", "{target}"),
        ("archive.source_action", " copy "),
        ("archive.collision_policy", "replace"),
        ("archive.source_root", "x"),
    ],
)
def test_invalid_edit_does_not_mutate(tmp_path, key, value):
    document = _read(tmp_path, "# unchanged\n")
    before = _fingerprint(document.path)
    with pytest.raises(ArchiveConfigError):
        management.prepare_archive_edit(document, key, value)
    assert _fingerprint(document.path) == before


def test_targeted_repair_does_not_fallback_or_ignore_another_invalid_value(tmp_path):
    document = _read(tmp_path, '[archive]\nsource_action=42\ncollision_policy="bad"\n')
    inspection = management.inspect_config_document(document)
    assert len(inspection.errors) == 2
    action = next(s for s in inspection.settings if s.name == "archive.source_action")
    assert action.error and action.value == 42 and action.source == "saved"
    before = _fingerprint(document.path)
    with pytest.raises(ArchiveConfigError):
        management.prepare_archive_edit(document, "archive.source_action", "copy")
    assert _fingerprint(document.path) == before
    document.path.write_text('[archive]\nsource_action=42 # repair\nfuture="keep"\n')
    document = management.read_config_document(document.path)
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action", "copy")
    )
    assert load_archive_config(document.path).source_action.name == "COPY"
    assert 'future="keep"' in document.path.read_text()


def test_legacy_location_conflicts_warn_but_do_not_block_scalar_edit(tmp_path):
    text = """[[locations]]
name=" Site "
latitude=0
longitude=0
radius_m=0
[[locations]]
name="site"
latitude=0
longitude=0
radius_m=100
"""
    document = _read(tmp_path, text)
    inspection = management.inspect_config_document(document)
    assert not inspection.errors
    assert any("zero" in w for w in inspection.warnings)
    assert any("name" in w for w in inspection.warnings)
    assert any("overlap" in w for w in inspection.warnings)
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action", "move")
    )
    assert document.path.read_text().startswith(text)
    assert len(load_archive_config(document.path).saved_locations) == 2


def test_symlink_target_permissions_and_link_preserved(tmp_path):
    target = tmp_path / "actual.toml"
    target.write_text("# target\n")
    target.chmod(0o640)
    link = tmp_path / "config.toml"
    link.symlink_to(target.name)
    document = management.read_config_document(link)
    assert document.target == target
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action", "move")
    )
    assert link.is_symlink() and os.readlink(link) == target.name
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert load_archive_config(link).source_action.name == "MOVE"


@pytest.mark.parametrize("kind", ["content", "link", "appearance", "permissions"])
def test_changes_since_read_abort_without_overwriting(tmp_path, monkeypatch, kind):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    target = tmp_path / "target.toml"
    target.write_text("# initial\n")
    link = tmp_path / "config.toml"
    link.symlink_to(target)
    document = (
        management.read_config_document()
        if kind == "appearance"
        else management.read_config_document(link)
    )
    edit = management.prepare_archive_edit(document, "archive.source_action", "move")
    if kind == "content":
        target.write_text("# external edit\n")
    elif kind == "link":
        other = tmp_path / "other.toml"
        other.write_text("# initial\n")
        link.unlink()
        link.symlink_to(other)
    elif kind == "permissions":
        target.chmod(0o400)
    else:
        document.path.parent.mkdir(parents=True)
        document.path.write_text("# external creation\n")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.toml")}
    with pytest.raises(ArchiveConfigError, match="changed"):
        management.persist_config_edit(edit)
    assert before == {p: p.read_bytes() for p in before}


@pytest.mark.parametrize("failure", ["replace", "fsync"])
def test_failed_write_preserves_original_and_cleans_temp(tmp_path, monkeypatch, failure):
    document = _read(tmp_path, "# original\n")
    before = _fingerprint(document.path)
    monkeypatch.setattr(management.os, failure, Mock(side_effect=PermissionError("denied")))
    with pytest.raises(ArchiveConfigError):
        management.persist_config_edit(
            management.prepare_archive_edit(document, "archive.source_action", "move")
        )
    assert _fingerprint(document.path) == before
    assert list(tmp_path.iterdir()) == [document.path]


@pytest.mark.parametrize("kind", ["broken", "loop", "malformed", "missing"])
def test_unreadable_document_is_not_missing_default(tmp_path, monkeypatch, kind):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    path = tmp_path / ".config/seestar-toolkit/config.toml"
    path.parent.mkdir(parents=True)
    if kind == "broken":
        path.symlink_to("absent")
    elif kind == "loop":
        path.symlink_to(path.name)
    elif kind == "malformed":
        path.write_text("[archive\n")
    with pytest.raises(ArchiveConfigError):
        management.read_config_document(path if kind == "missing" else None)
    if kind != "missing":
        with pytest.raises(ArchiveConfigError):
            load_archive_config()


def test_unset_preserves_comments_and_unrelated_location_fields(tmp_path):
    text = """# header
[archive]
# policy note
source_action="move" # keep explanation
future=42 # unfamiliar
[[locations]]
name="Site"
latitude=0
longitude=0
radius_m=0
extra="preserve"
"""
    document = _read(tmp_path, text)
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action")
    )
    result = document.path.read_text()
    for comment in ("# header", "# policy note", "# keep explanation", "# unfamiliar"):
        assert comment in result
    assert tomlkit.parse(result)["locations"][0]["extra"] == "preserve"
    assert "source_action" not in tomlkit.parse(result)["archive"]


def test_read_permission_failure_has_clear_error(tmp_path, monkeypatch):
    document = _read(tmp_path, "# untouched\n")
    monkeypatch.setattr(Path, "read_bytes", Mock(side_effect=PermissionError("denied")))
    with pytest.raises(ArchiveConfigError, match="Unable to read"):
        management.read_config_document(document.path)


def test_edit_detects_change_after_temp_preparation_and_cleans_temp(tmp_path, monkeypatch):
    document = _read(tmp_path, "# original\n")
    edit = management.prepare_archive_edit(document, "archive.source_action", "move")
    original_fsync = management.os.fsync

    def concurrent_edit(fd):
        original_fsync(fd)
        document.path.write_text("# another writer\n")

    monkeypatch.setattr(management.os, "fsync", concurrent_edit)
    with pytest.raises(ArchiveConfigError, match="changed"):
        management.persist_config_edit(edit)
    assert document.path.read_text() == "# another writer\n"
    assert list(tmp_path.iterdir()) == [document.path]


@pytest.mark.parametrize(
    "text", ["archive=42\n", 'locations="invalid"\n', '[[locations]]\nname="missing fields"\n']
)
def test_invalid_structures_are_inspectable_but_block_unrelated_edit(tmp_path, text):
    document = _read(tmp_path, text)
    assert management.inspect_config_document(document).errors
    before = _fingerprint(document.path)
    with pytest.raises(ArchiveConfigError):
        management.prepare_archive_edit(document, "archive.source_action", "copy")
    assert _fingerprint(document.path) == before


def test_symlinked_parent_target_update_and_missing_link_target_error(tmp_path):
    actual = tmp_path / "actual"
    actual.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    target = actual / "config.toml"
    target.write_text("# actual\n")
    document = management.read_config_document(alias / "config.toml")
    management.persist_config_edit(
        management.prepare_archive_edit(document, "archive.source_action", "move")
    )
    assert alias.is_symlink() and document.target == target
    assert load_archive_config(target).source_action.name == "MOVE"
