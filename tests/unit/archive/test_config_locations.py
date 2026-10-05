"""Location edits use synthetic documents and the shared safe writer."""

import math
from pathlib import Path

import pytest

from seestar_toolkit.archive.config import load_archive_config
from seestar_toolkit.archive.config_document import persist_config_edit, read_config_document
from seestar_toolkit.archive.config_locations import (
    matching_locations,
    prepare_location_edit,
    prepare_location_removal,
)
from seestar_toolkit.archive.exceptions import ArchiveConfigError
from seestar_toolkit.archive.planning import _haversine_m


def location(name="Home", lat=0, lon=0, radius=100):
    return f'[[locations]]\nname="{name}"\nlatitude={lat}\nlongitude={lon}\nradius_m={radius}\n'


def document(tmp_path, text=""):
    path = tmp_path / "config.toml"
    path.write_text(text)
    return read_config_document(path)


def test_create_partial_update_and_combined_rename_preserve_document(tmp_path):
    doc = document(tmp_path, "# top\n[future]\nvalue=42 # retain\n")
    edit = prepare_location_edit(doc, "  New Site  ", latitude=10, longitude=20)
    persist_config_edit(edit)
    doc = read_config_document(doc.path)
    assert doc.raw["locations"][0]["radius_m"] == 100
    assert doc.raw["locations"][0]["name"] == "New Site"
    doc.path.write_text(doc.path.read_text() + 'extra="keep" # location comment\n')
    edit = prepare_location_edit(
        read_config_document(doc.path),
        " new SITE ",
        latitude=11,
        rename="  Renamed  ",
        radius_m=25.5,
        update=True,
    )
    persist_config_edit(edit)
    saved = load_archive_config(doc.path).saved_locations[0]
    assert (saved.name, saved.latitude, saved.longitude, saved.radius_m) == (
        "Renamed",
        11,
        20,
        25.5,
    )
    text = doc.path.read_text()
    assert "# top" in text and "value=42 # retain" in text
    assert 'extra="keep" # location comment' in text


def test_missing_default_create_and_absent_removal(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    doc = read_config_document()
    persist_config_edit(prepare_location_removal(doc, "Absent"))
    assert not doc.path.parent.exists()
    persist_config_edit(prepare_location_edit(doc, "Home", latitude=0, longitude=0))
    assert doc.path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"latitude": 1},
        {"rename": "New"},
        {"latitude": 1, "longitude": 2, "update": True},
        {"latitude": True, "longitude": 0},
        {"latitude": 91, "longitude": 0},
        {"latitude": 0, "longitude": -181},
        {"latitude": float("nan"), "longitude": 0},
        {"latitude": 0, "longitude": float("inf")},
        {"latitude": 0, "longitude": 0, "radius_m": 0},
        {"latitude": 0, "longitude": 0, "radius_m": -1},
        {"latitude": 0, "longitude": 0, "radius_m": True},
        {"latitude": 0, "longitude": 0, "radius_m": float("inf")},
    ],
)
def test_invalid_creation_does_not_write(tmp_path, kwargs):
    doc = document(tmp_path)
    with pytest.raises(ArchiveConfigError):
        prepare_location_edit(doc, "Site", **kwargs)
    assert doc.path.read_bytes() == b""


@pytest.mark.parametrize("name", ["", "   ", ".", ".."])
def test_invalid_names(tmp_path, name):
    with pytest.raises(ArchiveConfigError):
        prepare_location_edit(document(tmp_path), name, latitude=0, longitude=0)


def test_logical_cleaned_name_conflicts_and_ambiguity(tmp_path):
    doc = document(tmp_path, location("A/B") + location("Other", 30))
    for name in ("a-b", "  A/B  "):
        with pytest.raises(ArchiveConfigError, match="name|identity|conflict"):
            prepare_location_edit(doc, "Other", rename=name)
    with pytest.raises(ArchiveConfigError, match="name|conflict"):
        prepare_location_edit(doc, "a-b", latitude=60, longitude=0)
    ambiguous = document(tmp_path, location(" Straße ") + location("STRASSE", 30))
    for operation in (
        lambda: prepare_location_edit(ambiguous, "strasse", latitude=60),
        lambda: prepare_location_removal(ambiguous, "strasse"),
    ):
        with pytest.raises(ArchiveConfigError, match="[Aa]mbiguous.*manual"):
            operation()


def test_case_rename_noop_and_untouched_legacy_spelling(tmp_path):
    doc = document(tmp_path, location(" Home "))
    unchanged = prepare_location_edit(doc, "home", latitude=0)
    assert not unchanged.changed
    before = doc.path.read_bytes(), doc.path.stat().st_mtime_ns
    persist_config_edit(unchanged)
    assert (doc.path.read_bytes(), doc.path.stat().st_mtime_ns) == before
    assert unchanged.proposed.value["name"] == " Home "
    persist_config_edit(prepare_location_edit(doc, " home ", rename=" HOME "))
    assert load_archive_config(doc.path).saved_locations[0].name == "HOME"


def test_overlap_touching_and_self_exclusion(tmp_path):
    distance = _haversine_m(0, 0, 0, 1)
    doc = document(tmp_path, location("First", radius=distance / 2))
    with pytest.raises(ArchiveConfigError, match="First.*Second|Second.*First"):
        prepare_location_edit(doc, "Second", latitude=0, longitude=1, radius_m=distance / 2)
    assert prepare_location_edit(
        doc, "Second", latitude=0, longitude=1, radius_m=distance / 2 - 0.001
    ).changed
    assert prepare_location_edit(doc, "First", radius_m=101).changed


def test_legacy_conflicts_allow_unrelated_edits_removal_and_targeted_repair(tmp_path):
    doc = document(
        tmp_path,
        location("A", radius=0)
        + location("A", radius=0)
        + location("Repair", lat='"bad"')
        + location("Far", lat=60),
    )
    with pytest.raises(ArchiveConfigError, match="invalid|number"):
        prepare_location_edit(doc, "Far", radius_m=200)
    repair = prepare_location_edit(doc, "Repair", latitude=30)
    assert repair.warnings
    persist_config_edit(repair)
    doc = read_config_document(doc.path)
    assert prepare_location_edit(doc, "Far", radius_m=200).changed
    assert prepare_location_removal(doc, "Repair").changed
    with pytest.raises(ArchiveConfigError, match="[Aa]mbiguous"):
        prepare_location_removal(doc, "A")


def test_edited_legacy_zero_radius_and_overlap_must_be_repaired(tmp_path):
    doc = document(tmp_path, location("Zero", radius=0) + location("Other", lon=1))
    with pytest.raises(ArchiveConfigError, match="positive"):
        prepare_location_edit(doc, "Zero", rename="New")
    assert prepare_location_edit(doc, "Zero", radius_m=10).changed
    doc = document(tmp_path, location("One") + location("Two"))
    with pytest.raises(ArchiveConfigError, match="overlap"):
        prepare_location_edit(doc, "One", rename="New")
    assert prepare_location_edit(doc, "One", latitude=20).changed
    persist_config_edit(prepare_location_removal(doc, "One"))
    assert len(load_archive_config(doc.path).saved_locations) == 1


def test_matches_boundaries_ties_antimeridian_and_antipodes(tmp_path):
    doc = document(tmp_path, location("Zulu", radius=0) + location("Alpha", radius=0))
    matches = matching_locations(doc, 0, 0)
    assert [m.location.name for m in matches] == ["Alpha", "Zulu"]
    assert all(m.distance_m == 0 for m in matches)
    assert matching_locations(doc, 0, 1) == ()
    assert math.isfinite(_haversine_m(0.08, 0, -0.08, 180))
    assert _haversine_m(0, 179.999, 0, -179.999) < 223
    boundary = _haversine_m(0, 0, 0, 1)
    doc = document(tmp_path, location(radius=boundary))
    assert len(matching_locations(doc, 0, 1)) == 1
    assert prepare_location_edit(document(tmp_path), "Pole", latitude=90, longitude=-180).changed


def test_removal_preserves_unrelated_entries_and_comments(tmp_path):
    doc = document(
        tmp_path,
        "# top\n"
        + location("Delete")
        + location("Keep", lat=40)
        + "unknown=42 # keep me\n[future]\nvalue=3 # future\n",
    )
    persist_config_edit(prepare_location_removal(doc, " delete "))
    text = doc.path.read_text()
    assert "Delete" not in text and "Keep" in text
    assert "# top" in text and "unknown=42 # keep me" in text and "value=3 # future" in text


def test_targeted_boolean_repair_and_invalid_remainder(tmp_path):
    doc = document(tmp_path, location(lat="true"))
    persist_config_edit(prepare_location_edit(doc, "Home", latitude=1))
    assert load_archive_config(doc.path).saved_locations[0].latitude == 1
    doc = document(tmp_path, '[archive]\nsource_action="invalid"\n' + location())
    with pytest.raises(ArchiveConfigError, match="invalid"):
        prepare_location_removal(doc, "Home")


def test_inline_location_arrays_round_trip_and_removal_retains_standalone_comments(tmp_path):
    doc = document(tmp_path, 'locations=[{name="Home", latitude=0, longitude=0, radius_m=100}]\n')
    persist_config_edit(prepare_location_edit(doc, "Away", latitude=30, longitude=0))
    assert len(load_archive_config(doc.path).saved_locations) == 2
    doc = document(tmp_path, location("Delete") + "# next site note\n" + location("Keep", lat=30))
    persist_config_edit(prepare_location_removal(doc, "Delete"))
    assert "# next site note" in doc.path.read_text()


def test_location_update_uses_shared_symlink_permissions_and_failure_cleanup(tmp_path, monkeypatch):
    from seestar_toolkit.archive import config_document

    doc = document(tmp_path, location())
    doc.path.chmod(0o640)
    link = tmp_path / "link.toml"
    link.symlink_to(doc.path)
    edit = prepare_location_edit(read_config_document(link), "Home", longitude=20)
    persist_config_edit(edit)
    assert link.is_symlink() and doc.path.stat().st_mode & 0o777 == 0o640
    assert load_archive_config(link).saved_locations[0].longitude == 20
    before = doc.path.read_bytes(), doc.path.stat().st_mtime_ns

    def fail(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(config_document.os, "replace", fail)
    with pytest.raises(ArchiveConfigError, match="Unable to save"):
        persist_config_edit(prepare_location_removal(read_config_document(link), "Home"))
    assert (doc.path.read_bytes(), doc.path.stat().st_mtime_ns) == before
    assert not list(tmp_path.glob(".*.tmp"))


@pytest.mark.parametrize("lat,lon", [(90, 180), (-90, -180), (0, 180), (0, -180)])
def test_coordinate_endpoints_and_widely_separated_circles(tmp_path, lat, lon):
    doc = document(tmp_path, location("Origin"))
    assert prepare_location_edit(doc, "Distant", latitude=lat, longitude=lon).changed


def test_archive_tie_break_and_all_match_reporting_agree_for_legacy_locations(tmp_path):
    from seestar_toolkit.archive.planning import _resolve_location

    doc = document(
        tmp_path,
        location("Zulu", radius=0)
        + location("alpha", radius=0)
        + location("Alpha", radius=0)
        + location("Farther", lat=0.001, radius=200),
    )
    sites = load_archive_config(doc.path).saved_locations
    assert (
        _resolve_location(explicit=None, latitude=0, longitude=0, saved_locations=sites) == "Alpha"
    )
    assert [match.location.name for match in matching_locations(doc, 0, 0)] == [
        "Alpha",
        "alpha",
        "Zulu",
        "Farther",
    ]


def test_invalid_existing_radius_requires_explicit_repair(tmp_path):
    doc = document(tmp_path, location().replace("radius_m=100\n", ""))
    with pytest.raises(ArchiveConfigError, match="missing required fields"):
        prepare_location_edit(doc, "Home", latitude=1)
    persist_config_edit(prepare_location_edit(doc, "Home", radius_m=30))
    assert load_archive_config(doc.path).saved_locations[0].radius_m == 30
