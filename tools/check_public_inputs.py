"""Fail closed if approved FITS bytes or the public-history boundary change."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def main() -> None:
    approved = json.loads((ROOT / "tests/data/public_fixtures.json").read_text())
    tracked = git("ls-files", "-z").split("\0")
    actual = {p for p in tracked if p.lower().endswith((".fit", ".fits"))}
    assert actual == set(approved), "FITS inventory differs from reviewed inventory"
    for name, expected in approved.items():
        data = (ROOT / name).read_bytes()
        assert len(data) == expected["bytes"], f"Unreviewed fixture size: {name}"
        assert hashlib.sha256(data).hexdigest() == expected["sha256"], (
            f"Fixture changed; repeat privacy review: {name}"
        )
    assert (ROOT / "tests/data/PRIVACY_REVIEW.md").is_file()
    subprocess.run(["git", "merge-base", "--is-ancestor", "0cdc6c2", "HEAD"], cwd=ROOT, check=True)
    assert git("rev-list", "--max-parents=0", "HEAD").split() == [
        git("rev-parse", "0cdc6c2").strip()
    ], "Unexpected history root"
    objects = git("rev-list", "--objects", "HEAD")
    sizes = subprocess.check_output(
        ["git", "cat-file", "--batch-check=%(objecttype) %(objectsize)"],
        input="\n".join(line.split()[0] for line in objects.splitlines()),
        cwd=ROOT,
        text=True,
    )
    for entry in sizes.splitlines():
        kind, size = entry.split()
        assert kind != "blob" or int(size) <= 100 * 1024 * 1024, "Oversized public blob"
    forbidden = (".private-real-data/", "dist/", "build/", ".venv/", "venv/")
    assert not any(p.startswith(forbidden) for p in tracked)
    assert not any(p.endswith((".whl", ".pyc", ".tar.gz")) for p in tracked)
    attributes = ROOT / ".gitattributes"
    assert not attributes.exists() or "filter=lfs" not in attributes.read_text()
    print(f"PASS: {len(approved)} reviewed fixtures; clean public root; no oversized blobs")


if __name__ == "__main__":
    main()
