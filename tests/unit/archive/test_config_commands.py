"""CLI configuration foundation, including failure and independence contracts."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from seestar_toolkit import cli


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path / ".config/seestar-toolkit/config.toml"


def test_show_provenance_saved_and_defaults(config_path, capsys):
    assert cli.main(["config", "show"]) == 0
    output = capsys.readouterr().out
    assert str(config_path) in output and "missing" in output
    assert output.count("archive.source_action") == 1 and "default" in output
    assert not config_path.parent.exists()
    assert cli.main(["config", "set", "archive.source_action", "copy"]) == 0
    capsys.readouterr()
    assert cli.main(["config", "show"]) == 0
    output = capsys.readouterr().out
    assert output.count("archive.source_action") == 1
    assert "archive.source_action = copy [saved]" in output
    assert cli.main(["config", "show", "--saved"]) == 0
    output = capsys.readouterr().out
    assert "source_action" in output and "collision_policy" not in output
    config_path.write_text("[broken")
    before = config_path.read_bytes()
    assert cli.main(["config", "show", "--defaults"]) == 0
    assert config_path.read_bytes() == before
    assert "archive.source_action = copy [default]" in capsys.readouterr().out


@pytest.mark.parametrize(
    "args",
    [
        ["config"],
        ["config", "show", "--saved", "--defaults"],
        ["config", "show", "--defaults", "--config", "x"],
        ["config", "set", "--location", "x"],
        ["config", "set", "archive.source_action", "copy", "--update"],
        ["config", "set", "archive.source_root", "x"],
        ["config", "unset", "archive.source_action", "--saved"],
    ],
)
def test_invalid_arguments_are_usage_errors(config_path, args):
    with pytest.raises(SystemExit) as error:
        cli.main(args)
    assert error.value.code == 2
    assert not config_path.parent.exists()


def test_explicit_path_only_and_invalid_inspection(config_path, tmp_path, capsys):
    assert (
        cli.main(
            [
                "config",
                "set",
                "archive.source_action",
                "copy",
                "--config",
                str(tmp_path / "missing"),
            ]
        )
        == 1
    )
    assert not config_path.parent.exists()
    other = tmp_path / "other.toml"
    other.write_text('[archive]\nsource_action=99\n[future]\nvalue="keep"\n')
    assert cli.main(["config", "show", "--config", str(other)]) == 1
    out = capsys.readouterr()
    assert "99" in out.out and "invalid" in out.out.lower()
    assert "source_action must" in out.err
    assert cli.main(["config", "show", "--saved", "--config", str(other)]) == 1
    assert "[future]" in capsys.readouterr().out
    assert cli.main(["config", "unset", "archive.source_action", "--config", str(other)]) == 0
    assert 'value="keep"' in other.read_text()
    before = other.read_bytes(), other.stat().st_mtime_ns
    assert cli.main(["config", "unset", "archive.source_action", "--config", str(other)]) == 0
    assert (other.read_bytes(), other.stat().st_mtime_ns) == before


@pytest.mark.parametrize(
    "hierarchy",
    [
        "{target/{location}/{session_end_date}",
        "{target}}/{location}/{session_end_date}",
    ],
)
def test_malformed_saved_hierarchy_can_be_inspected_and_repaired(config_path, capsys, hierarchy):
    config_path.parent.mkdir(parents=True)
    config_path.write_text(f'[archive]\nhierarchy="{hierarchy}"\n')

    assert cli.main(["config", "show"]) == 1
    output = capsys.readouterr()
    assert "archive.hierarchy" in output.out and "INVALID" in output.out
    assert "malformed braces" in output.err
    assert "Traceback" not in output.out + output.err

    assert cli.main(["config", "show", "--saved"]) == 1
    output = capsys.readouterr()
    assert hierarchy in output.out
    assert "malformed braces" in output.err
    assert "Traceback" not in output.out + output.err

    valid = "{location}/{target}/{session_end_date}"
    assert cli.main(["config", "set", "archive.hierarchy", valid]) == 0
    capsys.readouterr()
    assert f'hierarchy="{valid}"' in config_path.read_text()

    config_path.write_text(f'[archive]\nhierarchy="{hierarchy}"\n')
    assert cli.main(["config", "unset", "archive.hierarchy"]) == 0
    capsys.readouterr()
    assert "hierarchy" not in config_path.read_text()
    assert cli.main(["config", "show"]) == 0
    assert "archive.hierarchy = {target}/{location}/{session_end_date} [default]" in (
        capsys.readouterr().out
    )


@pytest.mark.parametrize(
    "hierarchy",
    [
        "{target/{location}/{session_end_date}",
        "{target}}/{location}/{session_end_date}",
    ],
)
def test_malformed_hierarchy_cannot_be_saved(config_path, capsys, hierarchy):
    config_path.parent.mkdir(parents=True)
    config_path.write_text('# unchanged\n[archive]\nsource_action="move"\n')
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns

    assert cli.main(["config", "set", "archive.hierarchy", hierarchy]) == 1
    output = capsys.readouterr()
    assert "malformed braces" in output.err
    assert "Traceback" not in output.out + output.err
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before


@pytest.mark.parametrize(
    "hierarchy",
    [
        "invalid",
        "{target/{location}/{session_end_date}",
        "{target}}/{location}/{session_end_date}",
    ],
)
def test_invalid_saved_hierarchy_can_still_be_overridden(config_path, tmp_path, hierarchy):
    config_path.parent.mkdir(parents=True)
    config_path.write_text(f'[archive]\nhierarchy="{hierarchy}"\n')
    source = tmp_path / "source"
    source.mkdir()
    assert (
        cli.main(
            [
                "archive",
                str(source),
                str(tmp_path / "archive"),
                "--dry-run",
                "--non-interactive",
                "--hierarchy",
                "{target}/{location}/{session_end_date}",
            ]
        )
        == 0
    )
    assert (
        cli.main(
            ["archive", str(source), str(tmp_path / "archive"), "--dry-run", "--non-interactive"]
        )
        == 1
    )


def test_help_version_and_conversion_do_not_load_config(config_path, monkeypatch):
    monkeypatch.setattr(
        cli, "load_archive_config", Mock(side_effect=AssertionError("must not read"))
    )
    for args in (["--help"], ["--version"], ["config", "--help"], ["config", "show", "--help"]):
        with pytest.raises(SystemExit) as error:
            cli.main(args)
        assert error.value.code == 0
    monkeypatch.setattr(cli, "convert_fits_to_tiff", lambda *args: Path("output.tiff"))
    assert cli.main(["convert", "input.fit", "output.tiff"]) == 0
    assert not config_path.parent.exists()


def test_cli_failed_write_never_reports_success(config_path, monkeypatch, capsys):
    from seestar_toolkit.archive import config_document

    config_path.parent.mkdir(parents=True)
    config_path.write_text("# untouched\n")
    monkeypatch.setattr(config_document.os, "replace", Mock(side_effect=PermissionError("denied")))
    assert cli.main(["config", "set", "archive.source_action", "move"]) == 1
    output = capsys.readouterr()
    assert "Saved archive" not in output.out and "Unable to save" in output.err
    assert config_path.read_text() == "# untouched\n"


def test_invalid_saved_policy_is_not_bypassed_by_archive_override(config_path, tmp_path):
    config_path.parent.mkdir(parents=True)
    config_path.write_text('[archive]\nsource_action="invalid"\n')
    source = tmp_path / "source"
    source.mkdir()
    assert (
        cli.main(
            [
                "archive",
                str(source),
                str(tmp_path / "archive"),
                "--dry-run",
                "--non-interactive",
                "--source-action",
                "copy",
            ]
        )
        == 1
    )
