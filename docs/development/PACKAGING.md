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
python tools/validate_distribution.py
```

The default isolated build produces the sdist first, then builds the wheel
from that sdist. This checks that the sdist carries the required build inputs.
Neither Git metadata nor an installed Toolkit package is needed by the backend.

Package discovery is restricted to `src/seestar_toolkit` and its ordinary
subpackages. There is currently no runtime package data; implicit data inclusion
is disabled. MANIFEST.in deliberately includes Python source, packaging inputs,
the public root README/CHANGELOG and license. Tests, private fixtures and internal
development documents stay in Git but are excluded from the sdist; they are not
needed to rebuild it. The tracked test fixtures have since completed public
privacy review in Stage 9.1d preflight.
This is artifact selection, not a global Git FIT/FITS ignore or test removal.
The transitional README's development links refer to the repository, not bundled
development documentation; final public prose remains with Stage 9.3a.

Inspect each artifact's complete member list, metadata, entry points, license
and content for private paths, FIT/FITS data, caches and other local material.
Never commit generated artifacts. Use ignored `dist/`/temporary directories.
Do not upload or publish builds as part of this step.

Stage 9.2a owns the final clean-install compatibility matrix; Stage 9.1d
validation does not declare final supported Python or macOS versions. Stage 9.4b's GO and subsequent
publication/closure gates are unchanged.


## Stage 9.1d distribution CI

`.github/workflows/ci.yml` defines **Distribution validation** for pushes to
`main`, PRs targeting `main`, and manual dispatch. All four candidate Python
versions (3.11, 3.12, 3.13, 3.14) run independent jobs with `fail-fast: false`.
No candidate uses `continue-on-error`. The runner is `macos-15`; a runtime
assertion requires Darwin/arm64. This is release-relevant validation, not a
claim that a particular macOS version or other platform is supported.
The [GitHub runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
lists macOS arm64 standard runners for private repositories.

The workflow uses `actions/checkout@v6` and `actions/setup-python@v6`,
`contents: read`, no persisted checkout credentials, no custom secrets and no
explicit caching. A cache miss is valid. There are no publishing, artifact
upload, tag, release, version-edit or changelog-edit steps. Action major tags
receive upstream updates; dependency lower bounds resolve compatible versions
at run time, so this is not a locked or bit-reproducible environment.

Reproduce the workflow in a disposable development venv:

```bash
python -m pip install '.[dev,build]'
python tools/check_public_inputs.py
python -m pytest
python -m ruff check .
python tools/check_formatting.py
git diff --check
python tools/validate_distribution.py
```

Formatting retains the established archive/CLI and mosaic-remediation scope,
plus the new validators and their tests (36 files). Existing unrelated
formatting debt is not silently reformatted. CI checks whitespace against the
push-before or PR-base SHA, falling back to the public bootstrap for manual
runs; it does not lint the orphan root's historical whitespace as a new diff.

`check_public_inputs.py` verifies all ten fixtures against reviewed sizes and
SHA-256 values in `tests/data/public_fixtures.json`, checks the sole public
history root is `c294ffd`, rejects reachable blobs above 100 MiB, and rejects
tracked generated outputs/private-data directories and LFS configuration.
A fixture hash change requires a fresh privacy review; do not simply refresh
the manifest to make CI pass. Historical private `master` is never fetched
from a private archive or merged by this workflow.

`validate_distribution.py` copies only packaging inputs and Python package
source to a temporary source directory with no Git data, caches or old builds.
The isolated PEP 517 build creates the sdist then builds its wheel. Both
archives are checked against a strict member allowlist, required modules,
metadata/version/runtime requirements, README, MIT license and console entry
point, and scanned for private-path/key markers. No FITS or development
history is allowed inside either distribution.

Each archive is independently installed with dependencies and without extras
in a new temporary venv. Commands run outside the checkout with PYTHONPATH
and PYTHONHOME removed, isolated Python (`-I`), no user site, and a verified
site-packages import under that venv. Both version entry points, `pip check`,
absence of pytest/Ruff/build/PDF tools, and a synthetic linear RGB FITS-to-TIFF
conversion must pass. Build isolation may temporarily install setuptools;
it is not a runtime requirement. All validation artifacts/venvs are removed
at completion; no final release checksums are generated.

The workflow is implemented locally but Stage 9.1d remains STARTED pending
approved commit/push, actual Actions evidence and formal review. Git cannot
push uncommitted files. See the [Stage 9.1d report](change_documents/STAGE_9/STAGE_9.1d_REPORT.md)
for local candidate results and all closure criteria. v1.1.0 remains unreleased.
