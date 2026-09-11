# Stage 5.1b --- Complete TIFF writer file-handling behaviour

## Purpose

Complete the low-level TIFF writer by defining and testing its
destination-path and filesystem behaviour.

Stage 5.1a established the TIFF subsystem and implemented the basic
linear 16-bit RGB TIFF writer.

Stage 5.1b must build on that implementation without introducing
pipeline, CLI, archive, or image-processing behaviour.

## Starting point

Stage 5.1a was completed in commit:

``` text
b399cd7 — Add TIFF writer foundation
```

The existing public API is:

``` text
write_tiff(image, path)
```

The Stage 5.1a writer already:

-   accepts `(height, width, 3)` RGB NumPy arrays;
-   requires `numpy.uint16`;
-   writes a 16-bit-per-channel RGB TIFF using `tifffile`;
-   preserves pixel values exactly;
-   performs no image processing or numeric conversion;
-   rejects unsupported layouts and dtypes;
-   exposes TIFF-specific exceptions.

Do not duplicate or redesign working Stage 5.1a behaviour unless a
genuine defect is discovered.

## Required destination-path contract

The TIFF writer must accept destination paths supplied as either:

``` text
str
```

or:

``` text
pathlib.Path
```

The destination identifies the TIFF file to be written.

The writer must not invent an output filename or alter the supplied
destination path.

Filename generation and higher-level output-path policy belong to later
Stage 5 work.

## Existing-file behaviour

The low-level writer must not silently overwrite an existing destination
file.

If the supplied destination already exists, the write must fail using an
appropriate TIFF-specific exception.

The existing file must remain unchanged.

Do not add an overwrite/force option during Stage 5.1b.

Any future explicit overwrite policy belongs to a higher-level output or
CLI layer unless later design work establishes a strong reason
otherwise.

## Parent-directory behaviour

The low-level TIFF writer must not automatically create missing parent
directories.

If the destination's parent directory does not exist, writing must fail
through the TIFF exception hierarchy.

Directory creation and archive-layout behaviour belong to later stages.

The writer must not implement:

``` text
mkdir
mkdir -p
parents=True
```

or equivalent automatic directory creation as part of normal TIFF
writing.

## Invalid destination behaviour

Destination/file-writing failures must be exposed through the TIFF
subsystem rather than leaking arbitrary filesystem or `tifffile`
exceptions.

Examples may include:

-   missing parent directory;
-   destination is a directory rather than a file;
-   permission/access failure where practical to test portably;
-   other failures raised by the underlying TIFF writer.

Use the existing exception hierarchy unless a genuine gap requires the
smallest appropriate extension.

Do not create a large filesystem-specific exception hierarchy
unnecessarily.

## Partial-output behaviour

Where practical, confirm that a failed TIFF write does not leave behind
a misleading successful-looking output file.

In particular:

-   pre-write validation failures must not create the destination;
-   existing-file rejection must not modify the existing file.

Do not introduce elaborate transactional or temporary-file
infrastructure solely for Stage 5.1b unless the existing implementation
genuinely requires it to meet the contract.

If underlying mid-write failure cleanup cannot be guaranteed simply and
portably, document that limitation rather than over-engineering the
writer.

## Return-value contract

Review existing Seestar Toolkit conventions before finalising the return
value.

If no established project convention conflicts, a successful call should
return the final destination as a:

``` text
pathlib.Path
```

For example:

``` text
result = write_tiff(image, path)
```

should return the path of the TIFF that was successfully written.

The returned path should represent the supplied destination without
inventing a different filename or output location.

Do not introduce a new result dataclass or model solely for this
operation.

## Image-data contract remains unchanged

Stage 5.1b must preserve the Stage 5.1a image contract.

Supported input remains:

``` text
shape: (height, width, 3)
dtype: numpy.uint16
channel order: R, G, B
```

The writer must continue to perform no:

-   scaling;
-   normalization;
-   clipping;
-   stretching;
-   gamma correction;
-   white balance;
-   RGB equalisation;
-   tone mapping;
-   resampling;
-   implicit dtype conversion.

Exact pixel-value preservation must remain protected by tests.

## Tests

Add focused tests only for genuine Stage 5.1b behaviour.

Test coverage should include, as appropriate:

1.  A `pathlib.Path` destination is accepted.
2.  A string destination is accepted.
3.  A successful write returns the documented value.
4.  An existing destination is rejected.
5.  Existing-file rejection leaves the existing file unchanged.
6.  A missing parent directory is not automatically created.
7.  A missing parent directory produces an appropriate TIFF-specific
    error.
8.  A destination that cannot be used as a TIFF file is handled through
    the TIFF exception hierarchy.
9.  Pre-write validation failure does not create an output file.
10. Existing Stage 5.1a exact-pixel round-trip behaviour still passes.

Avoid tests that depend on platform-specific permission behaviour unless
they can be made reliable on the supported development environment.

Do not add tests merely to increase the test count.

## Production-code scope

Modify only the TIFF subsystem as required to implement the Stage 5.1b
file-handling contract.

Expected production files are primarily:

``` text
src/seestar_toolkit/tiff/writer.py
src/seestar_toolkit/tiff/exceptions.py
src/seestar_toolkit/tiff/__init__.py
```

Not all of these need to change.

Keep the implementation minimal.

Do not refactor unrelated working code.

## Documentation

The authoritative Stage 5.1b specification is:

``` text
docs/change_documents/STAGE_5/STAGE_5.1b.md
```

Review existing architecture/project documentation only where necessary
to ensure Stage 5.1b does not contradict an established project
boundary.

Do not make broad documentation changes during this sub-stage.

Preserve the existing user-owned `docs/CHANGELOG.md` modification. The
user will add the Stage 5.1b CHANGELOG entry after the commit ID is
known.

The retrospectively added:

``` text
docs/change_documents/STAGE_5/STAGE_5.1a.md
```

may be present as an intentional uncommitted documentation file at the
start of this stage. Preserve it. It may be committed together with the
Stage 5.1b work unless the user directs otherwise.

## Explicit exclusions

Do not implement:

-   CLI integration;
-   conversion-pipeline integration;
-   output filename generation;
-   archive organisation;
-   configurable archive directory hierarchy;
-   automatic directory creation;
-   overwrite/force command-line options;
-   TIFF metadata embedding;
-   8-bit TIFF output;
-   float-to-`uint16` conversion;
-   float TIFF output;
-   float scaling or normalization policy;
-   clipping or rounding policy;
-   NaN/Inf handling;
-   image stretching;
-   gamma correction;
-   white balance;
-   RGB equalisation;
-   colour enhancement;
-   orientation correction;
-   registration;
-   plate solving;
-   mosaic stitching;
-   batch conversion.

Do not begin Stage 5.1c.

## Validation commands

Run an appropriate focused TIFF test selection.

Then run:

``` bash
pytest
ruff check .
git diff --check
```

Run the applicable Ruff formatting validation for changed Python files.

If documentation-only files are also present, do not treat them as
unexpected working-tree contamination.

## Stage 5.1b closure criteria

Stage 5.1b can be closed only if all of the following are true:

1.  Existing Stage 5.1a TIFF behaviour remains intact.
2.  Both `str` and `pathlib.Path` destinations are supported.
3.  A successful write has a clearly defined return value.
4.  The writer does not silently overwrite an existing destination.
5.  Existing-file rejection leaves the existing file unchanged.
6.  Missing parent directories are not automatically created.
7.  Missing-parent failures are exposed through the TIFF exception
    hierarchy.
8.  Other practical destination/write failures are appropriately
    wrapped.
9.  Pre-write validation failures do not create output files.
10. No output filename-generation policy has been introduced.
11. No archive-directory policy has been introduced.
12. No automatic directory-creation policy has been introduced.
13. No CLI or pipeline integration has been introduced.
14. No 8-bit TIFF behaviour has been introduced.
15. No float-to-integer TIFF policy has been introduced.
16. No image processing or numerical transformation has been introduced.
17. Exact `uint16` RGB pixel preservation remains tested.
18. Focused TIFF tests pass.
19. Full pytest passes.
20. Ruff passes.
21. Formatting validation passes.
22. `git diff --check` passes.
23. No unresolved issue remains that is a genuine Stage 5.1b blocker.

If any criterion fails, do not declare Stage 5.1b complete. Report the
blocker and the smallest appropriate next action.

## Codex completion report

At completion, report:

1.  Whether Stage 5.1b can be closed.
2.  Files created or modified.
3.  Production-code changes.
4.  Test changes.
5.  Final accepted destination-path types.
6.  Final existing-file behaviour.
7.  Final missing-parent-directory behaviour.
8.  Final TIFF/filesystem exception behaviour.
9.  Final partial-output behaviour.
10. Final return-value behaviour.
11. Confirmation that the Stage 5.1a image/numerical contract remains
    unchanged.
12. Confirmation that no automatic directory creation was added.
13. Confirmation that no overwrite option was added.
14. Confirmation that no CLI or pipeline integration was added.
15. Confirmation that no 8-bit or float-output policy was added.
16. Focused TIFF test result.
17. Full pytest result.
18. Ruff result.
19. Formatting result.
20. `git diff --check` result.
21. Documentation changes or preserved documentation files.
22. Any blockers or open questions for Stage 5.1c.
23. Current `git status --short`.

If every closure criterion passes, explicitly state:

**Stage 5.1b can be closed.**

Do not commit changes.

## Stage boundary

Successful completion of Stage 5.1b completes the low-level
file-handling behaviour of the basic `uint16` RGB TIFF writer.

Stage 5.1c may then address the next Stage 5 integration/numeric-policy
boundary, but must not be started during Stage 5.1b.
