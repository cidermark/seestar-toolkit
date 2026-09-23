# Stage 9.4b — Final release, publication and closure

## Status and authority

Stage 9.4b is **STARTED**. Checkpoint A is audit/design only and authorizes no
release action. Stage 9.4a closed at
`6784f8d3fc2af7814cdf9e7c328fa0eef2981b06`; its expected pending development
CHANGELOG row is carried into this stage.

This is the authoritative v1.1.0 release procedure. The release owner's later
requirement supersedes Stage 9.1a's optional follow-up-date approach: the final
`v1.1.0` tag must point to content carrying the release date deliberately
declared by the release owner. The two-gate model remains unchanged.

No tag, push, visibility change, GitHub Release or upload is permitted before
Gate 1 GO and explicit publication authorization. v1.1.0 is not published to
PyPI. Genuine failures and later remediations remain separately recorded.

## Checkpoint A baseline

- `main == origin/main == 6784f8d3fc2af7814cdf9e7c328fa0eef2981b06`.
- The initial working-tree difference is only the pending Stage 9.4a row in
  `docs/development/CHANGELOG.md`.
- Package version is 1.1.0; public release state is `Unreleased`.
- No local or remote tag and no GitHub Release exist.
- The repository is PRIVATE and exact-commit Actions are GREEN, independently
  confirmed by the release owner.

## Required final-state changes

While the repository remains private, for the controlled release operation:

1. replace `Unreleased` with the release date declared by the release owner in root
   `CHANGELOG.md`;
2. remove `Unreleased` and future-publication wording from root `README.md`;
3. remove `Unreleased` from both guide Markdown files and replace the Quick
   Start's future-publication wording;
4. regenerate both PDFs and strict SHA-256 manifests;
5. update the PDF generator and validator's pinned source hashes;
6. change the release-candidate validator to require a valid ISO-dated v1.1.0
   heading and reject `Unreleased` or malformed dates, with focused tests;
7. update reviewed Stage 9.4b evidence, development status and development
   CHANGELOG through the established workflow.

`pyproject.toml` already declares 1.1.0. No package metadata, production, CI,
LICENSE, CONTRIBUTING or Issue-form change is needed absent a concrete defect.
The proposed final commit subject is `Release Seestar Toolkit v1.1.0`.

## Publication-date rule

`<RELEASE_DATE>` is the release date deliberately declared by the release owner
in `YYYY-MM-DD` form when preparing the final release state. The exact Gate 1
approved and tagged commit must contain that date. Publication is expected to
proceed as one controlled operation associated with the declared date.

Gate 2 records the actual GitHub Release publication timestamp and verifies the
Release corresponds to the correct `v1.1.0` tag and exact Gate 1 approved commit.
An incidental UTC calendar-date rollover during a continuous publication
operation does not invalidate the release, require a new commit or require
retagging.

If publication is deliberately postponed and the release owner chooses a
different release day, stop before publication. Update the declared date and all
affected Markdown, PDFs, manifests, pinned hashes and artifacts; repeat Gate 1
in full; and obtain a new GO. Never backdate a release merely to match an earlier
preparation date. Changing a remote unpublished tag requires explicit
authorization and evidence. Once publicly accessible, tags and asset bytes are
immutable; correct defects through a reviewed remediation or new version.

## Gate 1 — exact-tree GO/NO-GO

Against the exact clean final release commit while PRIVATE:

1. independently review the final diff and date consistency;
2. run full pytest and focused release/PDF tests;
3. run Ruff, configured formatting and repository/direct whitespace checks;
4. run public-input, reachable-history and privacy checks;
5. validate Markdown, fences, navigation, links and Issue YAML;
6. regenerate PDFs twice and prove byte identity, correct manifests, embedded
   fonts, metadata/privacy, timestamps, extracted content and rendered pages;
7. run distribution validation and two independent candidate builds;
8. require byte-identical candidates and independent validation of both;
9. inspect ZIP and nested distributions against strict allowlists;
10. clean-install wheel and sdist separately, check both entry points and run
    the representative runtime/conversion smoke test;
11. prove 1.1.0 and the dated release state agree everywhere;
12. prove release artifacts are excluded and the tree is clean;
13. push the reviewed commit to `main` while private, prove synchronization,
    and require all Python 3.11–3.14 Actions jobs GREEN at that exact SHA;
14. obtain independent review and an explicit GO or NO-GO.

Any failed, missing or discrepant evidence is NO-GO. Preserve the failure,
apply no tag and perform no publication action.

## Controlled sequence after GO

After independent GO and explicit publication authorization:

1. create annotated `v1.1.0` at the approved SHA with annotation
   `Seestar Toolkit v1.1.0` and verify its type and target;
2. make two builds from a fresh clean checkout of that exact tag;
3. require byte identity and independently validate inventory, hashes, PDFs,
   nested distributions, clean installs, entry points and runtime smoke;
4. record provenance and obtain artifact approval;
5. push the tag while private and verify its remote target;
6. repeat final privacy, settings and remote-ref review;
7. change repository visibility from PRIVATE to PUBLIC;
8. create the normal GitHub Release and upload the two approved assets;
9. proceed immediately to Gate 2 without treating publication as closure.

## Tag, artifacts and GitHub Release

The annotated tag is exactly `v1.1.0`, annotation
`Seestar Toolkit v1.1.0`, targeting the Gate 1 approved commit.

Upload exactly:

- `seestar-toolkit-1.1.0-release.zip`
- `seestar-toolkit-1.1.0-release.zip.sha256`

The ZIP contains exactly seven top-level files: both guide PDFs, `README.md`,
`CHANGELOG.md`, `LICENSE`, one 1.1.0 wheel and one 1.1.0 sdist. The checksum is
external. Wheel and sdist are not separate assets. No provenance file is added.

The normal, non-draft, non-prerelease GitHub Release title is
`Seestar Toolkit v1.1.0`. Its manually curated body derives from the dated
public CHANGELOG and covers archive use, validated support, limitations/safety,
installation/download, no PyPI, checksum verification, and that GitHub's source
archives are source snapshots rather than the recommended release ZIP.

Record privately: version; commit and tag-object SHAs; tag; build/publication
dates; OS/build/architecture; Python, pip, setuptools, wheel, build, Pandoc,
XeLaTeX and PDF/archive tool versions; inventory; wheel, sdist, ZIP and checksum
hashes; local/download comparisons; CI identity; approvals and remediations.

## Stop and rollback rules

- Before GO: NO-GO, stay private, create no tag.
- After GO but before tagging: stop and remediate through review.
- Local tag/artifact failure: preserve evidence; delete only an unpublished
  local tag if needed; repeat validation and approval.
- Remote tag failure while private: remain private; never silently move it.
  Deletion/replacement requires explicit authorization and full evidence.
- Visibility failure: remain private and stop.
- Failure after visibility changes: stop, preserve state/evidence and obtain
  owner direction; a privacy exposure may require an explicit re-private action.
- Upload/download mismatch: never silently overwrite; use an explicitly
  reviewed Release remediation.
- After public access: never move the tag or replace same-named asset bytes.

## Gate 2 — independent public verification

Using fresh locations without authenticated private access:

1. prove the repository is public and public `main` has the approved lineage;
2. prove annotated `v1.1.0` resolves to the approved commit;
3. verify the normal Release, tag, title, date and curated notes;
4. download exactly the intended two assets;
5. byte/hash-compare them with approved local artifacts and verify the ZIP with
   its external checksum;
6. extract independently and prove the seven-file and nested allowlists;
7. install the downloaded wheel and sdist in separate clean environments;
8. prove both entry points report 1.1.0 and run the installed conversion smoke;
9. verify public README, dated CHANGELOG, LICENSE, guides/PDFs and privacy;
10. verify exact-release-commit Actions remains GREEN;
11. verify no unexpected branch, tag, Release, asset or private material became
    public and confirm no PyPI publication;
12. finalize the private runbook from the steps actually proven;
13. obtain independent Gate 2 PASS or FAIL review.

Any failed or unverified requirement is Gate 2 FAIL. Only accepted Gate 2 PASS
permits Stage 9.4b COMPLETE, Stage 9.4 COMPLETE, Stage 9 COMPLETE and the v1.1.0
release process COMPLETE.

## Private runbook

The private runbook receives the proven prerequisites, placeholders, date rule,
final edits, Gate 1 commands/evidence, GO approval, tag/build/provenance,
push/visibility/Release/upload sequence, Gate 2 public validation and all stop
procedures. Public evidence records completion without exposing private storage
location or private-only content.

## Closure criteria

### Audit/design — 1–12

1. Stage 9.4a baseline identified.
2. Expected carry-forward diff preserved.
3. Scope and two-gate authority explicit.
4. Required final-state files identified.
5. No unnecessary product/package change proposed.
6. Release-owner declared-date policy is explicit.
7. Rollover and deliberate-postponement handling prevents backdating/stale tags.
8. Final commit requirements defined.
9. Tag name, type, annotation and target defined.
10. Artifact/upload allowlists defined.
11. No-PyPI and generated-source policies explicit.
12. Authenticated/manual evidence boundaries explicit.

### Gate 1 — 13–28

13. Approved final-state edits implemented.
14. Root CHANGELOG has the release-owner declared date.
15. README and guides have consistent final state.
16. PDFs/manifests and pinned hashes agree.
17. Package metadata remains correct at 1.1.0.
18. Full and focused tests pass.
19. Ruff, formatting and whitespace pass.
20. Public-input/history/privacy gates pass.
21. Markdown/link/fence/navigation and YAML pass.
22. PDF technical/content/privacy/visual gates pass.
23. Two release builds are byte-identical.
24. ZIP/nested allowlists and hashes pass.
25. Clean installs, entry points and smoke pass.
26. Exact tree is clean; artifacts excluded.
27. Main/remote synchronize; exact Actions GREEN.
28. Independent review records Gate 1 GO.

### Publication — 29–40

29. Explicit owner authorization recorded.
30. Annotated tag name/message/target correct.
31. Tagged-source builds reproducible.
32. Final local artifact validation passes.
33. Provenance and hashes recorded.
34. Remote private tag target verified.
35. Final privacy/settings/ref review passes.
36. PRIVATE-to-PUBLIC succeeds.
37. GitHub Release tag/title/timestamp/body correct and tied to the approved commit.
38. Exactly ZIP/checksum uploaded.
39. Generated archives distinguished.
40. No PyPI publication.

### Gate 2 — 41–55

41. Public unauthenticated repository access passes.
42. Public main lineage correct.
43. Public annotated tag target correct.
44. Release metadata correct.
45. Exactly intended assets downloadable.
46. Downloads byte-match approved artifacts.
47. External checksum verifies ZIP.
48. ZIP seven-file inventory exact.
49. Nested distribution validation passes.
50. Downloaded wheel/sdist clean installs pass.
51. Both entry points report 1.1.0.
52. Installed runtime/conversion smoke passes.
53. Public documents/privacy/support pass.
54. Exact Actions GREEN; remote state expected.
55. Independent Gate 2 review records PASS.

### Final closure — 56–60

56. Failure/remediation chronology preserved.
57. Final provenance complete.
58. Private runbook finalized.
59. Stage 9.4b and 9.4 independently closed.
60. Stage 9 and v1.1.0 process independently closed.

At Checkpoint A, criteria 1–12 PASS and criteria 13–60 remain PENDING.
