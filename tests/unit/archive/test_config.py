"""Tests for read-only archive TOML configuration."""

from pathlib import Path

import pytest

from seestar_toolkit.archive import (
    ArchiveConfig,
    ArchiveConfigError,
    CollisionPolicy,
    SourceAction,
    load_archive_config,
)


def test_missing_default_configuration_uses_safe_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert load_archive_config() == ArchiveConfig()


def test_configuration_loads_archive_policy_and_saved_locations(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text(
        """
[archive]
hierarchy = "{location}/{target}/{session_end_date}"
source_action = "move"
collision_policy = "error"
future_option = true

[[locations]]
name = "Warfield"
latitude = 51.4
longitude = -0.7
radius_m = 500
""".strip()
    )

    config = load_archive_config(path)

    assert config.hierarchy == "{location}/{target}/{session_end_date}"
    assert config.source_action is SourceAction.MOVE
    assert config.collision_policy is CollisionPolicy.ERROR
    assert len(config.saved_locations) == 1
    assert config.saved_locations[0].name == "Warfield"


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("[archive\nhierarchy = 'x'", "Unable to load"),
        ("[[locations]]\nname='x'\nlatitude=91\nlongitude=0\nradius_m=1", "latitude"),
        ("[[locations]]\nname='x'\nlatitude=0\nlongitude=181\nradius_m=1", "longitude"),
        ("[[locations]]\nname='x'\nlatitude=0\nlongitude=0\nradius_m=-1", "radius"),
    ],
)
def test_invalid_configuration_is_rejected(tmp_path: Path, content: str, message: str) -> None:
    path = tmp_path / "config.toml"
    path.write_text(content)

    with pytest.raises(ArchiveConfigError, match=message):
        load_archive_config(path)


def test_missing_explicit_configuration_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ArchiveConfigError, match="does not exist"):
        load_archive_config(tmp_path / "missing.toml")
