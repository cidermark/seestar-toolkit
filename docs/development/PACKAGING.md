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

Stage 9.2a clean wheel AND sdist validation, combined with Stage 9.1d CI,
supports Python 3.11 through 3.14 inclusive for v1.1.0 on macOS arm64.
`requires-python = ">=3.11,<3.15"` excludes unvalidated future Python lines;
version-specific classifiers list exactly 3.11, 3.12, 3.13 and 3.14. Runtime
dependency lower bounds are unchanged. This is a Python-line decision, not
proof of every patch version or macOS release. Tested interpreter patches and
actual dependency resolutions are recorded in the Stage 9.2a evidence.

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
plus the validators and their tests (37 files after Stage 9.2a). Existing unrelated
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

Stage 9.1d formally closed at `1771b9f` after reviewed green Actions evidence.
Its Run 1 FAIL, whitespace remediation and Run 2 PASS remain historical evidence. See the [Stage 9.1d report](change_documents/STAGE_9/STAGE_9.1d_REPORT.md)
for local candidate results and all closure criteria. v1.1.0 remains unreleased.


## Stage 9.2a clean installation validation

The [Stage 9.2a report](change_documents/STAGE_9/STAGE_9.2a_REPORT.md) and
[structured evidence](change_documents/STAGE_9/STAGE_9.2a_EVIDENCE.json) record
interpreter provenance, initial and final wheel/sdist results, dependency sets,
actual temporary site-packages paths and cleanup. Stage 9.2a is formally
COMPLETE at `398b771`, as confirmed by Stage review in the Stage 9.2b starting
context. The [Stage 9.2b completion audit](change_documents/STAGE_9/STAGE_9.2b_REPORT.md)
records passing technical checkpoints A–D, including recovered storage validation,
local privacy/network observations and uninstall facts. Historical setup/harness
failures and the original physical USB device's EIO/unconfirmed cleanup remain
preserved. Stage 9.2b remains STARTED: formal closure readiness is FAIL pending
independent review, approved user commit and post-commit gates. Previously tested
storage need not be reconnected to review the recorded evidence.

Homebrew Python 3.13.15 and 3.14.7 were available under `/opt/homebrew` (arm64).
`python3` selected 3.14.7; its name alone did not identify the requested line.
Inspect `command -v python3`, `python3 --version`, `sys.executable` and
`platform.machine()` together. Use an explicit versioned executable to select
a different installed line. No 3.11/3.12 Homebrew formula was installed locally;
`pyenv versions --bare` was empty, and no framework installation was found.
Homebrew Python remains the recommended later user-install route. Older lines
may require versioned formulae; this stage did not install or validate those
formulae and does not infer their current availability from standalone builds.

For non-system-modifying validation, missing interpreters were obtained from
[Astral python-build-standalone via uv](https://docs.astral.sh/uv/guides/install-python/),
using pinned uv 0.8.22 in a disposable tooling venv and explicit versions:

```bash
python3.13 -m venv /tmp/seestar-stage92a-tools
/tmp/seestar-stage92a-tools/bin/python -m pip install 'uv==0.8.22' 'build>=1.2'
/tmp/seestar-stage92a-tools/bin/uv --no-config --cache-dir /tmp/seestar-stage92a-cache python install --install-dir /tmp/seestar-stage92a-python --no-bin 3.11.9 3.12.10
```

No system Python, Homebrew formula, shell startup file or PATH link is modified.
The uv pin fixes its interpreter download catalogue; both installations were
verified as native arm64 before use. These historical patches intentionally
match the Stage 9.1d evidence; this is not advice to install an old patch
instead of a maintained patch for normal use.

Build wheel/sdist into a new temporary output directory using `python -m build`.
Then invoke the small validator once per explicit interpreter:

```bash
python tools/validate_clean_install.py --python /path/to/candidate/python --wheel /tmp/validation-dist/seestar_toolkit-1.1.0-py3-none-any.whl --sdist /tmp/validation-dist/seestar_toolkit-1.1.0.tar.gz --report /tmp/candidate-evidence.json
```

The orchestrating Python is tooling only. Each artifact gets its own new venv
created by the specified candidate. pip uses normal build isolation, no cache
and no editable install. Runtime processes clear Python/pip overrides, disable
user site and run outside the repository using `-I` for Python entry points.
The approved real `tests/data/seestar/light.fit` is copied into the temporary
working directory. Installed CLI conversion produces a uint16 RGB TIFF,
verified against an independent OpenCV GRBG demosaic over every pixel, with
shape/dtype/photometric checks. The source copy's digest must remain unchanged.
All temporary environments, FITS copies and TIFF outputs are removed by the
validator after evidence capture, even on a recorded validation failure.

Do not reuse environments between wheel/sdist or initial/final artifacts.
Any metadata change requires a rebuild and a new full clean-install matrix.
The project validator also checks final Requires-Python and classifier metadata.
No release artifact or checksum is produced by this process.


## Stage 9.2b installed behaviour and removal facts

The public commands are `convert`, nonrecursive `convert-batch`, and `archive`.
Archive hierarchy uses `{session_end_date}` and `observation_01`; configuration
is read-only TOML. No saved-location writer or JPEG-policy switch is exposed.
The completion report inventories every option and records exact error/exit
behaviour for later user documentation.

Local disposable validation establishes that `deactivate` restores the shell
environment without uninstalling. Package uninstall removes its entry point and
module; config and generated/archive data persist. Removing the venv also leaves
those external-to-venv files intact. Config can be removed separately. These
observations do not authorise deleting real user configuration or data.

Source and six instrumented installed paths revealed no Toolkit telemetry,
analytics, updater or external metadata transmission. This is scoped Python/source
evidence, not a packet capture or exhaustive native dependency audit. Local
indexes/diagnostics can contain user metadata. No Full Disk Access requirement
was established and no macOS security settings were changed. D temporary data
and environments were removed; the unavailable original failed USB device's
cleanup remains an explicitly accepted historical environmental limitation.

## Stage 9.3a — Markdown documentation audit

Current baseline is `519f0e3`, the Stage 9.2b validation closure commit supplied
for this Stage. Earlier pre-commit status paragraphs and checkpoint failure
evidence above remain historical records; no post-commit CI evidence is invented.

Stage 9.3a is STARTED. Checkpoint A audits the validated 1.1.0 CLI and designs
the authoritative User Guide, abbreviated Quick Start and public root documents.
The [specification](change_documents/STAGE_9/STAGE_9.3a.md) defines 65 closure
criteria; the [progress report](change_documents/STAGE_9/STAGE_9.3a_REPORT.md)
records the fact matrix, discrepancies and content outlines. Checkpoints B/C
are not begun. Python 3.11–3.14 support remains established; v1.1.0 is Unreleased.

Documentation must preserve shallow archive discovery, read-only config, actual
observation/date naming and both uint16 Seestar and float32 Siril TIFF output.
Use explicit copy in introductory archive examples so existing config cannot
select move. No public guide, package metadata or production change is made in A.
The pending Stage 9.2b development CHANGELOG entry remains unchanged. PDFs and
release checksum artifacts belong to Stage 9.3b, not this documentation stage.

### Stage 9.3a Checkpoint B — guides written

Checkpoint B is PASS pending independent review; Stage 9.3a remains STARTED.
The authoritative [User Guide](../user/SEESTAR_TOOLKIT_USER_GUIDE.md) and
abbreviated [Quick Start](../user/SEESTAR_TOOLKIT_QUICK_START.md) now document
validated 1.1.0 behaviour, including shallow discovery, explicit dry-run/copy,
read-only config and uint16 Seestar versus float32 Siril TIFFs.

The [appended report](change_documents/STAGE_9/STAGE_9.3a_REPORT.md) records 50
command occurrences, validation categories and the preserved helper failure/fix.
B uses an existing source-matching installation and disposable public-safe inputs;
no new wheel/sdist or release artifact was created. Actual clean artifact install
proof remains Stage 9.2a. Root documentation and final validation await explicit
Checkpoint C authorisation. The pending development CHANGELOG remains unchanged;
v1.1.0 remains Unreleased and no Stage 9.3a commit exists.

### Stage 9.3a Checkpoint C — public documentation audit

The root README now serves as the concise package and repository landing page;
the public CHANGELOG retains v1.1.0 as Unreleased, and CONTRIBUTING plus GitHub
issue forms provide privacy-first reporting routes. The final distribution
validator passed after replacing non-ASCII README tree punctuation that caused
its first metadata-payload comparison to fail. Both isolated wheel and sdist
installs passed and temporary artifacts were removed.

The first Checkpoint C audit and its failure remain recorded in the Stage 9.3a
evidence. Final Checkpoint C revalidation has not yet been run. Independent
review, user commit and post-commit verification remain pending; no release
artifact was retained.

#### Checkpoint C final remediation revalidation

Checkpoint C now passes and Stage 9.3a is technically/documentationally ready
for closure review. Fresh pytest, Ruff, configured formatting, whitespace,
public-input/history, documentation, installed-entry-point and full isolated
wheel/sdist validation all pass. The original Checkpoint C failure remains in
the Stage evidence. Independent final review, user approval/commit and
post-commit required CI verification remain pending; v1.1.0 remains Unreleased.
