# Local real-data testing

Real FIT/FITS datasets are tested locally and need not be committed. Developers
supply their own datasets outside the repository, for example under a private
local working directory. Never move or copy the frozen qualification corpus
into tracked public content. Public automated tests must not depend on private
captures or one developer's filesystem layout.

If an in-checkout location is useful, `.private-real-data/` at the repository
root is narrowly ignored. Before using it, verify with `git check-ignore` and
check `git ls-files` to ensure no private file is already tracked. Ignore rules
do not remove tracked files or Git history. Do not force-add private captures.
There is no global FIT/FITS ignore: reviewed synthetic, generated or anonymised
fixtures can remain tracked in the test tree.

## Privacy and sharing

FIT/FITS headers may contain GPS coordinates, site/location information,
telescope/device identifiers, observation timestamps and other potentially
identifying metadata. Inspect every HDU, comments and history before sharing;
review filenames, configs, logs and images as well. Do not paste original
metadata or personal paths into public issue reports. Obtain permission and
record provenance for any real fixture proposed for public redistribution.

The existing ten tracked FITS fixtures have identifying metadata and are not
yet cleared for public sharing. They remain unchanged to preserve test evidence.
Substantive sanitisation/replacement requires an explicitly approved follow-up
with equivalent regression coverage. Review all reachable Git history before
publication: deleting or sanitising the current file alone is insufficient.
The repository documentation boundary is not a privacy access boundary.

## Representative qualification

Choose relevant capture varieties: supported raw Bayer and RGB inputs, standard
and structural mosaic naming, AltAz/EQ, firmware variation, single and multiple
observations, equal-time light/stack boundaries, cross-midnight evidence, large
retained-light gaps and retained counts differing from stack metadata. Existing
Stage 8 ground truth and outcomes remain authoritative historical evidence;
do not regenerate them merely because documentation moved.

Prefer read-only discovery, reconstruction and archive planning. Record expected
membership, stack assignments, diagnostics, plan dates and before/after file
counts, bytes and content/state fingerprints. Never execute archive COPY/MOVE
against private qualification data without a separately authorised test scope.
Use isolated generated temporary fixtures for execution tests.

Keep identifying values out of reports. Any discrepancy is classified and
recorded, not silently fixed or hidden. New camera/mode support requires its own
implementation and representative validation, not an assumption from file type.
