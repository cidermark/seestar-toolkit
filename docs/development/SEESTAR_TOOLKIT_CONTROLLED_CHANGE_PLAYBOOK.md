# Seestar Toolkit Controlled Change Playbook

Project reference for ENH-xxx and BUG-xxx work · 13 November 2026

## Use this at the start of every change chat

Read this playbook and the project instructions before replying. Use this playbook to run the workflow and the approved per-change repository document to govern behaviour, scope, validation and closure. Explicit user decisions govern any departure. Resolve conflicts with Mark before issuing a launcher.

The first reply establishes the objective, current and desired behaviour, included and excluded scope, and the consequential decisions still open. For a new change, start in design. For a resumed change, establish the current gate from the document and returned evidence. State the immediate next action. An inventory item, draft specification or prior chat summary does not establish implementation approval.

ChatGPT coordinates design, decisions, launchers and evidence reviews. Mark runs launchers in Codex for VS Code and returns the results. Mark executes Git commands and returns their complete output unless he explicitly delegates the exact operation. Every handoff gives Mark one next action. Wait for the evidence from that action before advancing.

## 1. Define the change and settle decisions

- **Enhancement** — Identify the user-visible outcome, the existing behaviour it builds on, concrete examples, exceptions, and the contracts that must be preserved.
- **Bug** — Record expected and actual behaviour, reproduction, affected inputs and baseline. Separate a suspected cause from a confirmed cause. Agree the regression case and the limits of the fix.
- Ask Mark to decide material differences in behaviour, scope, compatibility, output, defaults or failure handling. Present the options and consequences and record the decision in plain language. Use stable IDs such as D01 when there are several decisions. Track status as OPEN, AGREED or SUPERSEDED. Record the replacement decision when an earlier one changes.
- Use a bounded read-only inspection if a decision depends on repository facts or sample data. Define the evidence needed and return to design when it arrives. During design, repository writes, branch operations and implementation launchers require their own later gates.
- Agree the smallest meaningful stages. Give each a purpose, permitted work, exclusions, evidence and closure criteria. Use sub-stages when an earlier result needs review before later work can safely proceed. A small bug can have one implementation stage.

## 2. Establish the controlling specification

Prepare or review the change document in the established repository format. Use an exact confirmed path under `docs/development/change_documents/<ID>/`. The document should record:

| Section | Required content |
|---|---|
| Status and baseline | ID, title, draft or approved revision, repository path, expected base and current stage authorisation |
| Objective and scope | Existing and expected behaviour, inclusions, exclusions and compatibility requirements |
| Decisions | Agreed behaviour, rationale where useful, superseded proposals and unresolved questions |
| Stage plan | Each stage ID, boundaries, permitted changes, evidence and testable closure criteria |
| Validation | Focused tests, relevant regressions, representative manual evidence where needed and failure cases |
| Records | Acceptance and closure evidence, relevant commit IDs, integration evidence and known limitations |

For initial read-only inspection or document creation, identify the exact intended document path. Have Codex check it first. If it is absent and absence is expected, use the agreed written brief as the authority for that bounded session and, for document creation, inspect an identified precedent. Stop on unexpected absence or conflict. A documentation-only launcher should permit edits only to the named document, require `git diff --check`, and return the changed path and open decisions. Mark reviews the draft and explicitly approves the scope and stage. Record approval before implementation. Stage-specific amendments and temporary exceptions require the same decision and recording discipline.

Use the established branch and specification-commit sequence once approved. Verify the base, expected specification changes, branch name and staged diff at the appropriate gates. Review the specification commit before issuing an implementation launcher.

## 3. Open one stage and issue one bounded launcher

Use the following as top-level headings only at formal boundaries. Replace the example identifier and title with the actual stage. Use a smaller heading such as `## ENH-XXXa — Implementation Review` for routine reviews.

# 🟢 START — ENH-XXXa: Stage Description

# ✅ COMPLETE — ENH-XXXa: Stage Description

**Part A — Configuration outside the copyable block**

- **Codex chat** — START NEW CHAT / CONTINUE EXISTING CHAT.
- **Recommended model** — Exact available model. Use GPT-5.6 Terra for documentation or simple edits, GPT-5.6 Sol for normal implementation and testing, or GPT-6 Astra for complex debugging or architecture, subject to current availability. Choose the least expensive capable model.
- **Reasoning effort** — Light / Medium / High.
- **IDE Context** — Off unless the task specifically requires it.
- **Session type** — READ-ONLY / IMPLEMENTATION / VALIDATION / DOCUMENTATION / CLOSURE.
- **Authoritative document** — Exact repository path.

Default to a new Codex chat at a new stage or implementation boundary if the document supplies enough context. Continue for a targeted correction or review when the existing chat contains needed evidence. Consider Codex `/status` for long sessions.

**Part B — One copyable fenced text block. Replace every placeholder before handing it to Mark.**

```text
SEESTAR TOOLKIT — [ENH-xxx / BUG-xxx]
[EXACT STAGE ID] — [PURPOSE]

==================================================
1. AUTHORITATIVE SPECIFICATION
==================================================
Read [exact repository path] first and treat it as controlling.
Use [revision and sections]. Stop if this launcher conflicts with it or a material decision remains unresolved for this stage.

==================================================
2. BASELINE AND SAFETY CHECKS
==================================================
Verify [repository], [branch], [expected HEAD], [expected upstream or its absence], and [expected staged, unstaged and untracked state]. Preserve [known pending files and intended changes]. Stop and report the exact difference if the baseline, specification or working tree is unexpected.

==================================================
3. AUTHORISED SCOPE
==================================================
Work only on [approved stage, permitted areas and deliverable].
Preserve [existing contracts]. Exclude [named behaviour and later stages].

==================================================
4. REQUIRED WORK
==================================================
[Give concrete requirements, examples and edge cases relevant to this stage.]

==================================================
5. VALIDATION AND CLOSURE CRITERIA
==================================================
[Name the applicable checks, regression boundaries, manual evidence and criterion IDs.] Report each outcome with supporting evidence. Stop on a material defect and report it with the affected criterion.

==================================================
6. RESTRICTIONS AND GIT BOUNDARIES
==================================================
Use only the authorised session scope. Preserve pre-existing work. Do not stage, commit, push, merge, switch/create/delete branches, fetch, pull, reset, rebase, stash or clean unless this exact operation is authorised. Stop at the requested report. Formal closure is a coordinator decision.

==================================================
7. COMPLETION REPORT
==================================================
Return the repository baseline and final status, actual changed files and their purpose, criterion-by-criterion evidence, commands and results, counts or representative output where relevant, failures, open items and any deviations. State what the evidence establishes for this stage.
```

For an initial draft or read-only investigation, adapt sections 1 and 3 to the approved brief and expected document state. Keep configuration and coordinator commentary outside the fenced block.

## 4. Review evidence before moving forward

1. Compare the returned baseline, diff or changed-file list and checks with the controlling document. Verify the expected output or reproduced/fixed behaviour, exclusions, relevant regressions and intentionally pending files.
2. Use **PASS** when the evidence is sufficient, **FOLLOW-UP REQUIRED** when a targeted action remains, or **BLOCKED** when a discrepancy or user decision prevents progress. Name the specific criterion, evidence and next action. A Codex PASS is an input to this review.
3. If a finding changes agreed behaviour, return to design for that decision, update the controlling document and issue a bounded follow-up. Close resolved findings against fresh evidence. Reuse applicable evidence and rerun only checks affected by an amendment or required at the current gate.
4. Before the implementation commit, use a separate read-only review of the actual diff, tests and scope. Its conclusion is **READY FOR USER-CONTROLLED COMMIT** or **NOT READY**, with reasons. Documentation-only edits use appropriate document and diff checks unless the authoritative criteria require more.
5. Use COMPLETE only after the applicable stage or change closure criteria are evidenced and reviewed. Keep implementation, validation, formal closure, commit, push, integration and remote CI status explicit. Overall formal closure requires its own evidence review.

## 5. Git, documentation and integration

| Gate | What to verify before the next step |
|---|---|
| Baseline and branch | Confirm repository, current branch and HEAD, expected upstream if present, and intended working-tree entries. Establish the expected `main` baseline and user-authorised change branch. |
| Staging | Give Mark `git add -- <exact paths>` with the actual paths. Review the staged names and content and `git diff --cached --check`. Preserve intentional pending changes. |
| Commit | Use a scoped project message such as `ENH-xxx[a]: <specific outcome>` or `docs: record BUG-xxx closure`. After each commit, review `git status --short --branch` and an appropriate `git log --oneline` excerpt. Record the actual ID from the output. |
| Documentation and formal closure | Use separate documentation and closure-review steps. Review each closure criterion, tests, lint or formatting where applicable, manual acceptance, scope, and limitations. Record approved results in the change document and in `docs/development/CHANGELOG.md` and `docs/development/PROJECT_Notes.md` where required. Record an ID in a later documentation change if it only becomes known after the relevant commit. |
| Integration readiness | After formal closure, review branch ancestry, merge base, divergence, expected commits and fast-forward eligibility for the agreed integration method. Confirm readiness from evidence. |
| Integration, push and remote validation | Give the exact command for the approved operation after reviewing the preceding output. Verify the resulting local commit, pushed commit and GitHub Actions for that exact integrated commit. Record final integration and CI status. |
| Branch and inventory closure | Delete branches only after remote validation and final confirmation, with explicit authorisation. Record the delivered behaviour, specification path, relevant commits, final status and any deferred work in the Enhancement Inventory where applicable. Release work requires separate scope. |

Give one exact Git command at a time, or a small bounded block for one gate when appropriate. Wait for the complete output. Unexpected state is a review point. Amend, force-push, rebase, merge and branch deletion require explicit approval. A clean tree alone does not establish readiness.

## Why this follows ENH-005

- **Start with a design conversation.** ENH-005 began with standalone FITS privacy work and explicit boundaries. Its early proposals evolved into separate reporting, processing and verification commands. The decision register captured superseded proposals so later stages could pick up the agreed design.
- **Use evidence to refine the specification.** Read-only metadata reconnaissance preceded implementation. ENH-005b.1 implemented the report, and ENH-005b.2 used four representative S50 and S50 Pro light and stack reports to accept the refined metadata policy. The decision and acceptance evidence went into the controlling document.
- **Authorise only the stage at hand.** ENH-005c.1 was limited to the FITS processing foundation. CLI integration and independent verification had later boundaries. The temporary `--noscrub` option had an explicit removal gate in final validation.
- **Make the handoff enforce the workflow.** The earlier Controlled Change Workflow already captured strong launcher and Git controls. This playbook adds a standard first reply, a live decision record, and a single evidence-based next action at every gate. Mark reported a poor ENH-006 workflow experience. The available ENH-006 completion record establishes the delivered result, while the available conversation evidence is insufficient to attribute the experience to specific exchanges.

Sources reviewed include retrieved ENH-005 chat excerpts, the [early ENH-005 specification](https://chatgpt.com/library?file_id=libfile_61d83720b7a88191a72df46c4fc45d9a&account_id=personal), the [10 November ENH-005 working specification](https://chatgpt.com/library?file_id=libfile_64d9b720ebe88191a6f523171e02dc30&account_id=personal), the [Controlled Change Workflow](https://chatgpt.com/library?file_id=libfile_9af4a39cab508191b5763d0a21b48e9c&account_id=personal), the ENH-006 inventory completion summary and the current project instructions.

## Paste into a new change chat

```text
Read SEESTAR_TOOLKIT_CONTROLLED_CHANGE_PLAYBOOK.md from this project
before replying and apply it throughout this chat.

Change: [ENH-xxx / BUG-xxx — short title]
Request: [describe the desired change or bug, with any examples or evidence]

Act as the development coordinator. Start in design. Your first reply
should set out the objective, current and expected behaviour, proposed
scope and exclusions, material decisions still open, and one next
action. If the reference is unavailable, ask me to attach it before
issuing a launcher. Wait for my scope and specification approval before
preparing an implementation launcher. I run Codex launchers and Git
commands and return the evidence for review.
```
