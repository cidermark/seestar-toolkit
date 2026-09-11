# Public Git History Bootstrap

## Background

Seestar Toolkit was developed initially in a local Git repository.

Before the repository was first published to GitHub, release-preparation work identified
an oversized FITS test fixture and potentially identifying metadata in several real-data
test fixtures.

The test fixtures were reviewed before publication. Identifying FITS header metadata was
sanitised where required, and the oversized Siril mosaic fixture was replaced with a
small deterministic synthetic fixture.

## Public history boundary

The GitHub-visible repository history therefore begins with a clean repository snapshot
created during Stage 9.1d.

Development documentation produced before this bootstrap intentionally remains unchanged.
Commit identifiers recorded in those documents refer to the archived pre-public development
history and may not resolve in the GitHub-visible history.

The original pre-public repository history is retained separately as a private development
archive.

## Rationale

Starting the public history from the reviewed snapshot:

- prevents the original oversized FITS object from entering GitHub history;
- prevents superseded unsanitised FITS metadata from entering GitHub history;
- preserves historical development documents without retrospectively rewriting them;
- avoids Git history rewriting and misleading replacement commit identifiers.

This bootstrap does not represent a source-code reset. It establishes the safe publication
boundary for the existing Seestar Toolkit codebase.