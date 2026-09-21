# Contributing to Seestar Toolkit

You do not need to be a programmer to make a valuable contribution. Clear bug
reports, enhancement suggestions and information from owners of other Seestar
models can all help improve the Toolkit.

## Report a bug

Use the **Bug Report** issue form. Include the Toolkit version, Python version,
the command you ran, what you expected, what happened and relevant error or
diagnostic text. For archive problems, reproduce with `--dry-run` when practical.

Check all material for private information before posting it. FITS headers,
configuration, archive indexes and diagnostics can contain observing
coordinates, timestamps, device identifiers and other metadata. Do not attach
FITS files or detailed metadata to an Issue by default.

If a capture example may be necessary, first open an Issue describing the
Seestar model, firmware version, available capture types or configurations, and
the behaviour it demonstrates. Wait until a suitable transfer and privacy review
are agreed. Seestar Toolkit v1.1.0 does not provide automatic anonymisation.

## Suggest an enhancement

Use the **Feature Request** issue form and describe the problem or workflow you
want to improve. A suggestion is welcome without a proposed implementation and
does not imply a release commitment.

Representative information from other Seestar models can help future validation.
Depending on what a model produces, useful examples may include raw light frames,
native stacked products, mosaics or captures made with differing configurations.
Do not assume that every model produces every type. Apply the privacy process
above before sharing any file or metadata.

## Propose a code change

Please open an Issue before beginning a substantial code change. This helps
confirm scope and avoids work that conflicts with a staged release boundary.
Keep pull requests focused and include tests when behaviour changes.

Before proposing a code change, run the applicable repository checks:

```bash
python -m pytest
python -m ruff check .
python tools/check_formatting.py
python tools/check_public_inputs.py
git diff --check
```

Do not add private captures, credentials, local paths, generated release files or
unreviewed FIT/FITS fixtures to the repository.
