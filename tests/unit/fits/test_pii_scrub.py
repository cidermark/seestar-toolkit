"""Focused safe-publication tests for ENH-005c.2."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from astropy.io import fits

from seestar_toolkit.fits import (
    PiiScrubError,
    UnknownMetadataAction,
    infer_pii_scrub_path,
    inspect_fits_structure,
    safe_terminal_value,
    scrub_fits,
)


def _fits(path: Path, *, second_hdu: bool = False) -> bytes:
    primary = fits.PrimaryHDU(np.arange(4, dtype=np.uint16).reshape(2, 2))
    primary.header.append(("MYSTERY", "same", "private description"))
    primary.header.append(("MYSTERY", "same", "private description"))
    hdus: list[fits.hdu.base._BaseHDU] = [primary]
    if second_hdu:
        extension = fits.ImageHDU(np.arange(3, dtype=np.int16))
        extension.header["OTHER"] = "second"
        hdus.append(extension)
    fits.HDUList(hdus).writeto(path)
    return path.read_bytes()


def test_occurrences_are_reviewed_individually_across_hdus_and_source_is_unchanged(
    tmp_path: Path,
) -> None:
    source = tmp_path / "image.fit"
    original = _fits(source, second_hdu=True)
    seen: list[tuple[int, int, str]] = []
    actions = iter(
        (
            UnknownMetadataAction.PRESERVE,
            UnknownMetadataAction.ANONYMIZE,
            UnknownMetadataAction.ANONYMIZE,
        )
    )

    def review(occurrence, _replacement):
        seen.append((occurrence.hdu_index, occurrence.card_index, occurrence.keyword))
        return next(actions)

    result = scrub_fits(source, reviewer=review)

    assert [item[0] for item in seen] == [0, 0, 1]
    assert [item[2] for item in seen] == ["MYSTERY", "MYSTERY", "OTHER"]
    assert result.preserved_unknown_count == 1
    assert result.anonymized_unknown_count == 2
    assert source.read_bytes() == original
    inspect_fits_structure(result.output_path)
    with fits.open(result.output_path) as hdus:
        assert hdus[0].header["MYSTERY"] == "same"
        assert hdus[0].header.cards["MYSTERY", 1].value == "REMOVED"
        assert hdus[1].header["OTHER"] == "REMOVED"


def test_noninteractive_default_anonymizes_unknowns(tmp_path: Path) -> None:
    source = tmp_path / "image.fit"
    _fits(source)

    result = scrub_fits(source)

    assert result.anonymized_unknown_count == 2
    with fits.open(result.output_path) as hdus:
        values = [card.value for card in hdus[0].header.cards if card.keyword == "MYSTERY"]
        assert values == ["REMOVED", "REMOVED"]


def test_cancellation_before_publication_leaves_no_output_or_temporary(tmp_path: Path) -> None:
    source = tmp_path / "image.fit"
    _fits(source)

    def cancel(_occurrence, _replacement):
        from seestar_toolkit.fits import PiiScrubCancelled

        raise PiiScrubCancelled("cancelled")

    with pytest.raises(PiiScrubError, match="cancelled"):
        scrub_fits(source, reviewer=cancel)

    assert not (tmp_path / "pii-scrubbed").exists()
    assert not tuple(tmp_path.glob(".pii-scrub-*"))


def test_destinations_cover_ordinary_archive_light_stack_and_exact_output(tmp_path: Path) -> None:
    ordinary = tmp_path / "ordinary.fit"
    _fits(ordinary)
    observation = tmp_path / "archive/observation_02"
    light = observation / "fits_images/lights/Light.fit"
    stack = observation / "seestar_stacked/Stacked.fits"
    light.parent.mkdir(parents=True)
    stack.parent.mkdir(parents=True)
    _fits(light)
    _fits(stack)

    assert infer_pii_scrub_path(ordinary) == tmp_path / "pii-scrubbed/ordinary.fit"
    assert infer_pii_scrub_path(light) == observation / "pii-scrubbed/Light.fit"
    assert infer_pii_scrub_path(stack) == observation / "pii-scrubbed/Stacked.fits"
    exact = tmp_path / "exact/name.fits"
    assert scrub_fits(ordinary, exact).output_path == exact


def test_collision_equivalence_and_dangling_destination_symlink_are_rejected(
    tmp_path: Path,
) -> None:
    source = tmp_path / "image.fit"
    _fits(source)
    with pytest.raises(PiiScrubError, match="different files"):
        scrub_fits(source, source)
    alias = tmp_path / "alias.fit"
    alias.symlink_to(source)
    with pytest.raises(PiiScrubError, match="different files"):
        scrub_fits(source, alias)
    destination = tmp_path / "existing.fit"
    destination.write_bytes(b"existing")
    with pytest.raises(PiiScrubError, match="refusing to overwrite"):
        scrub_fits(source, destination)
    dangling = tmp_path / "dangling.fit"
    dangling.symlink_to(tmp_path / "missing.fit")
    with pytest.raises(PiiScrubError, match="refusing to overwrite"):
        scrub_fits(source, dangling)


def test_archive_source_and_destination_symlink_escapes_are_rejected(tmp_path: Path) -> None:
    observation = tmp_path / "archive/observation_02"
    lights = observation / "fits_images/lights"
    lights.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    escaped = outside / "Light.fit"
    _fits(escaped)
    source = lights / "Light.fit"
    source.symlink_to(escaped)
    with pytest.raises(PiiScrubError, match="Unsafe archive path"):
        scrub_fits(source)

    source.unlink()
    _fits(source)
    (observation / "pii-scrubbed").symlink_to(outside, target_is_directory=True)
    with pytest.raises(PiiScrubError, match="Unsafe archive path"):
        scrub_fits(source)


def test_publication_failure_cleans_temporary_and_does_not_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "image.fit"
    _fits(source)
    destination = tmp_path / "output.fit"
    monkeypatch.setattr("seestar_toolkit.fits.pii_scrub.os.link", Mock(side_effect=OSError()))

    with pytest.raises(PiiScrubError, match="safely publish"):
        scrub_fits(source, destination)

    assert not destination.exists()
    assert not tuple(tmp_path.glob(".pii-scrub-*"))


def test_atomic_publication_race_never_replaces_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "image.fit"
    _fits(source)
    destination = tmp_path / "output.fit"

    def collide(_temporary: Path, target: Path) -> None:
        target.write_bytes(b"racing file")
        raise FileExistsError

    monkeypatch.setattr("seestar_toolkit.fits.pii_scrub.os.link", collide)

    with pytest.raises(PiiScrubError, match="refusing to overwrite"):
        scrub_fits(source, destination)

    assert destination.read_bytes() == b"racing file"
    assert not tuple(tmp_path.glob(".pii-scrub-*"))


def test_hostile_terminal_values_are_escaped_and_truncated() -> None:
    rendered = safe_terminal_value("secret\x1b[2J\n" + "x" * 300)

    assert "\x1b" not in rendered
    assert "\n" not in rendered
    assert "\\x1b" in rendered
    assert "\\n" in rendered
    assert len(rendered) == 160
    assert rendered.endswith("...")
