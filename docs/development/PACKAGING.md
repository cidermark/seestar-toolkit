# Packaging and versioning

Stage 9.1c keeps `project.version` in root `pyproject.toml` as the single
authoritative release version. Setuptools writes it into distribution metadata;
`seestar_toolkit.__version__` reads that metadata with `importlib.metadata`.
Both `seestar-toolkit --version` and `python -m seestar_toolkit --version`
use that value. Later documentation/release tooling should read
`project.version` using `tomllib` or validate its output against it.

An uninstalled source checkout deliberately has no fallback release version.
Install the project (an editable install is suitable for development) before
importing it or invoking its CLI. Reinstall after changing project metadata;
an old editable distribution's metadata does not refresh itself automatically.
No repository file is read at runtime to determine the installed version.

## Dependencies and candidate compatibility

Runtime requirements remain Astropy, NumPy, headless OpenCV and tifffile.
The `dev` extra contains pytest, pytest-cov and Ruff. The separate `build`
extra contains the standards-based build frontend. Build isolation obtains
setuptools from `build-system.requires`; none of these tools is an ordinary
runtime requirement. No PDF tools are introduced.

The existing lower bounds are retained, without freezing local versions or
inventing upper bounds. `requires-python = ">=3.11"` is a candidate installation
floor, grounded in the runtime use of stdlib `tomllib`. It permits testing
3.11–3.14 and is not a support declaration for those or future interpreters.
Current local NumPy/tifffile require Python >=3.12; Python 3.11 needs an older
compatible resolution allowed by the constraints. Stage 9.2a must prove clean
wheel AND sdist installs and runtime compatibility for each candidate, and may
narrow metadata in response to evidence. Version-specific Python classifiers
have therefore been removed.

Release support policy is macOS Apple Silicon only, with exact macOS versions
still to be validated. Toolkit's own code is pure Python: its wheel should
truthfully be tagged `py3-none-any`. Native dependencies impose their own
platform/ABI requirements. This wheel tag is not a Linux/Windows support claim.

## Build configuration and commands

Setuptools remains the PEP 517 backend, with a minimum of 77.0.3 for the
PEP 639 SPDX license/license-files configuration. The root MIT license is
included by the backend. Author remains Mark Wymer; no unavailable project
URLs are invented. See the
[setuptools metadata documentation](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).

With the build frontend installed in a development/build environment, run
from the repository root:

```bash
python -m build --outdir dist/stage9.1c
```

The default isolated build produces the sdist first, then builds the wheel
from that sdist. This checks that the sdist carries the required build inputs.
Neither Git metadata nor an installed Toolkit package is needed by the backend.

Package discovery is restricted to `src/seestar_toolkit` and its ordinary
subpackages. There is currently no runtime package data; implicit data inclusion
is disabled. MANIFEST.in deliberately includes Python source, packaging inputs,
the public root README/CHANGELOG and license. Tests, private fixtures and internal
development documents stay in Git but are excluded from the sdist; they are not
needed to rebuild it and are not yet cleared for public distribution.
This is artifact selection, not a global Git FIT/FITS ignore or test removal.
The transitional README's development links refer to the repository, not bundled
development documentation; final public prose remains with Stage 9.3a.

Inspect each artifact's complete member list, metadata, entry points, license
and content for private paths, FIT/FITS data, caches and other local material.
Never commit generated artifacts. Use ignored `dist/`/temporary directories.
Do not upload or publish builds as part of this step.

Stage 9.1d owns CI and broader distribution validation. Stage 9.2a owns the
clean-install compatibility matrix; this step's single-interpreter build/CLI
checks cannot replace that proof. Fixture and reachable-history privacy work
remains a separate pre-publication requirement. Stage 9.4b's GO and subsequent
publication/closure gates are unchanged.
