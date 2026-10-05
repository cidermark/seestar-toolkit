"""Location CLI contracts with synthetic configurations and FITS headers."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from astropy.io import fits

from seestar_toolkit import cli
from seestar_toolkit.archive.config import load_archive_config


@pytest.fixture
def config_path(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path / ".config/seestar-toolkit/config.toml"


def create(name="Home", *args):
    return cli.main(
        ["config", "set", "--location", name, "--latitude", "10", "--longitude", "20", *args]
    )


def test_create_unattended_update_partial_and_rename(config_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    assert create("  Home  ") == 0
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns
    assert cli.main(["config", "set", "--location", "home", "--latitude", "11"]) == 1
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before
    assert "--update" in capsys.readouterr().err
    assert (
        cli.main(
            [
                "config",
                "set",
                "--location",
                "home",
                "--latitude",
                "11",
                "--rename",
                " New Home ",
                "--update",
            ]
        )
        == 0
    )
    site = load_archive_config(config_path).saved_locations[0]
    assert (site.name, site.latitude, site.longitude, site.radius_m) == ("New Home", 11, 20, 100)
    assert cli.main(["config", "set", "--location", "missing", "--radius-m", "40", "--update"]) == 1


def test_prompt_skip_then_combined_update(config_path, monkeypatch, capsys):
    assert create() == 0
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns
    prompts = []

    def skip(prompt):
        prompts.append(prompt)
        output = capsys.readouterr().out
        assert "Old:" in output and "Proposed:" in output
        assert "latitude" in output and "longitude" in output and "radius_m" in output
        return "Skip"

    monkeypatch.setattr("builtins.input", skip)
    args = ["config", "set", "--location", "Home", "--rename", "Renamed", "--radius-m", "20"]
    assert cli.main(args) == 0
    assert len(prompts) == 1 and "Update config / Skip" in prompts[0]
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before
    monkeypatch.setattr("builtins.input", lambda _: "Update config")
    assert cli.main(args) == 0
    assert load_archive_config(config_path).saved_locations[0].name == "Renamed"


def test_prompt_external_change_aborts_write(config_path, monkeypatch, capsys):
    assert create() == 0
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)

    def answer(_):
        config_path.write_text(config_path.read_text() + "# external edit\n")
        return "Update config"

    monkeypatch.setattr("builtins.input", answer)
    capsys.readouterr()
    assert cli.main(["config", "set", "--location", "Home", "--latitude", "11"]) == 1
    assert load_archive_config(config_path).saved_locations[0].latitude == 10
    assert "# external edit" in config_path.read_text()
    output = capsys.readouterr()
    assert "Saved location" not in output.out and "changed" in output.err


def test_noop_removal_and_invalid_edits_do_not_prompt(config_path, monkeypatch):
    assert create() == 0
    monkeypatch.setattr("builtins.input", Mock(side_effect=AssertionError("unexpected prompt")))
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns
    assert cli.main(["config", "set", "--location", "Home", "--latitude", "10"]) == 0
    assert cli.main(["config", "unset", "--location", "Absent"]) == 0
    assert cli.main(["config", "set", "--location", "Home", "--radius-m", "0"]) == 1
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before
    assert cli.main(["config", "unset", "--location", "HOME"]) == 0
    assert load_archive_config(config_path).saved_locations == ()


@pytest.mark.parametrize(
    "args",
    [
        ["show", "--saved", "--extract", "x"],
        ["show", "--defaults", "--extract", "x"],
        ["show", "--latitude", "1"],
        ["set", "--location", "Site"],
        ["set", "--latitude", "1"],
        ["set", "archive.source_action"],
        ["set", "archive.source_action", "copy", "--location", "Site", "--latitude", "1"],
        ["set", "archive.source_action", "copy", "--rename", "Site"],
        ["set", "--location", "Site", "--extract", "x", "--latitude", "1"],
        ["set", "--location", "Site", "--extract", "x", "--longitude", "1"],
        ["unset", "--location", "Site", "archive.source_action"],
        ["unset", "--location", "Site", "--update"],
        ["unset"],
    ],
)
def test_invalid_mixed_arguments(config_path, args):
    with pytest.raises(SystemExit) as error:
        cli.main(["config", *args])
    assert error.value.code == 2
    assert not config_path.parent.exists()


def test_fits_create_update_all_matches_and_failures(config_path, tmp_path, capsys):
    path = tmp_path / "site.fits"
    fits.PrimaryHDU(header=fits.Header({"SITELAT": 10, "SITELONG": 20})).writeto(path)
    assert cli.main(["config", "show", "--extract", str(path)]) == 0
    assert "No saved locations" in capsys.readouterr().out
    assert not config_path.parent.exists()
    assert (
        cli.main(
            ["config", "set", "--location", "Site", "--extract", str(path), "--radius-m", "250"]
        )
        == 0
    )
    saved = config_path.read_text()
    config_path.write_text(saved + saved.replace("Site", "Other"))
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns
    assert cli.main(["config", "show", "--extract", str(path)]) == 0
    output = capsys.readouterr()
    assert "Multiple matches (2)" in output.out and "Other" in output.out
    assert "latitude=10" in output.out and "longitude=20" in output.out
    assert "radius_m=250" in output.out and "distance_m=0" in output.out
    assert "overlapping" in output.err
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before
    config_path.write_text(saved)
    fits.PrimaryHDU(header=fits.Header({"SITELAT": 30, "SITELONG": 40})).writeto(
        path, overwrite=True
    )
    assert cli.main(["config", "show", "--extract", str(path)]) == 0
    assert "No matching saved locations" in capsys.readouterr().out
    assert (
        cli.main(["config", "set", "--location", "Site", "--extract", str(path), "--update"]) == 0
    )
    site = load_archive_config(config_path).saved_locations[0]
    assert (site.latitude, site.longitude, site.radius_m) == (30, 40, 250)
    config_path.write_text('[archive]\nsource_action="bad"\n')
    capsys.readouterr()
    assert cli.main(["config", "show", "--extract", str(path)]) == 1
    assert "distance_m=" not in capsys.readouterr().out


def test_conflicts_update_flag_and_fits_errors_never_write_or_prompt(
    config_path, tmp_path, monkeypatch, capsys
):
    assert create() == 0
    assert (
        cli.main(["config", "set", "--location", "Away", "--latitude", "50", "--longitude", "50"])
        == 0
    )
    before = config_path.read_bytes(), config_path.stat().st_mtime_ns
    monkeypatch.setattr("builtins.input", Mock(side_effect=AssertionError("invalid edit prompted")))
    assert cli.main(["config", "set", "--location", "Home", "--rename", "Away", "--update"]) == 1
    assert (
        cli.main(
            [
                "config",
                "set",
                "--location",
                "Home",
                "--latitude",
                "50",
                "--longitude",
                "50",
                "--update",
            ]
        )
        == 1
    )
    assert (
        cli.main(
            [
                "config",
                "set",
                "--location",
                "Home",
                "--extract",
                str(tmp_path / "missing.fit"),
                "--update",
            ]
        )
        == 1
    )
    assert (config_path.read_bytes(), config_path.stat().st_mtime_ns) == before
    assert "overlap" in capsys.readouterr().err


def test_location_explicit_config_does_not_create_default(config_path, tmp_path):
    other = tmp_path / "explicit.toml"
    assert create("Site", "--config", str(other)) == 1
    assert not other.exists() and not config_path.parent.exists()
    other.write_text("# explicit only\n")
    assert create("Site", "--config", str(other)) == 0
    assert not config_path.parent.exists()
    assert load_archive_config(other).saved_locations[0].name == "Site"


def test_longitude_only_update_keeps_latitude_radius_and_unknown_boolean(config_path):
    assert create("Site", "--radius-m", "25.5") == 0
    config_path.write_text(config_path.read_text() + "custom=true # retained\n")
    assert cli.main(["config", "set", "--location", "site", "--longitude", "30", "--update"]) == 0
    site = load_archive_config(config_path).saved_locations[0]
    assert (site.latitude, site.longitude, site.radius_m) == (10, 30, 25.5)
    assert "custom=true # retained" in config_path.read_text()


def test_location_write_failure_has_no_success_message(config_path, monkeypatch, capsys):
    from seestar_toolkit.archive import config_document

    assert create() == 0
    before = config_path.read_bytes()
    capsys.readouterr()
    monkeypatch.setattr(config_document.os, "replace", Mock(side_effect=PermissionError("denied")))
    assert cli.main(["config", "unset", "--location", "Home"]) == 1
    output = capsys.readouterr()
    assert "Removed location" not in output.out and "Unable to save" in output.err
    assert config_path.read_bytes() == before
