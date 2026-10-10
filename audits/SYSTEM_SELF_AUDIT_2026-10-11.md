# System Self-Audit — 2026-10-11

Status: **HARDENED_WITH_REMAINING_FAIL_CLOSED_GAPS**

Scope: control plane, learning admission, execution evidence, generation authorization, Harness/Agent/Skill authority hygiene and continuity compaction. This maintenance pass does not advance the active business stage and does not treat maintenance activity as production progress.

## Audit method

The pass used the control-plane sequence: challenge assumptions -> search for bypasses -> classify local vs systemic defects -> apply the smallest durable fix -> delete dependency-safe superseded mechanisms -> add adversarial regression coverage -> preserve unresolved gaps as explicit blockers.

No ad-hoc session material is used as learning evidence merely because it was visible to the operator during this pass.

## Fixed defect 1 — pre-generation evidence could be mounted under the wrong specialist slot

`generation_guard.py` required separate Art Director, Creative Director and Red Team evidence plus independent execution/context identities, but the external proof bundle did not itself declare and bind the reviewer role. A proof object could therefore be placed under the wrong role key without a direct role-identity mismatch failure.

Fix:

- `reviewer_role` is now required in every verified pre-generation challenge proof.
- `reviewer_role` must equal the challenge slot being authorized.
- Missing or mismatched role identity fails closed.
- Regression tests cover both missing-role and swapped-role evidence.

Distilled rule: **evidence must bind subject, action, artifact and role; dictionary position is not identity proof.**

## Fixed defect 2 — transient session content had no explicit learning-admission boundary

The self-learning protocol defined what useful external material looks like, but did not explicitly distinguish "seen during a session" from "authorized learning source". That creates a contamination risk for ad-hoc conversation, temporary research and side tasks.

Fix:

- learning-source admission is now default deny;
- internal project evidence must be present in the declared work packet;
- external material requires explicit import plus affirmative learning authorization and a durable source reference;
- ambient conversation, unlisted browsing context and undeclared side-task material are outside the durable learning boundary;
- user-declared no-learn/no-persist material must be excluded before durable serialization;
- the system must not persist a content-specific denylist merely to remember an exclusion, because the denylist would itself preserve a trace.

Regression tests pin the policy language so future edits cannot silently collapse this boundary.

Distilled rule: **visibility is not admission; learning must be opt-in at the source boundary.**

## Fixed defect 3 — producer completion could masquerade as role approval

Several `produce` work orders declared an `approval_role`. `AgenticStudio.complete_work()` automatically signed `PASS` for such tasks. This conflated two different facts:

1. the producer completed the assigned artifact contract; and
2. a role approved the resulting artifact/stage.

That is structurally unsafe because successful production is not independent approval.

Fix:

- all producer `approval_role` declarations were removed from `execution-plan.json`;
- workflow required-role gates now contain review/meta-review roles only;
- producer completion remains enforced by work-order completion, artifact existence and producer-output provenance;
- `ExecutionPlanner` and `complete_work()` reject later producer approval-role injection;
- regression tests require that no `produce` task can declare an approval role and that workflow required roles are a subset of actual review/meta-review approval roles.

Distilled rule: **production provenance and approval authority are different evidence classes.**

## Fixed defect 4 — repository contained two machine-readable config authorities

The runtime and installed package actually loaded `video_growth_agent/data/*`, while the repository also carried root `config/*` mirrors and documentation pointed readers at them. Most happened to match, but `techniques.json` had already diverged at the blob/format level. This was an authority-split waiting to become behavioral drift.

Fix:

- removed root `config/workflow.json`, `config/roles.json`, `config/quality-rubric.json` and `config/techniques.json`;
- declared `video_growth_agent/data/` the sole machine-readable runtime resource authority;
- updated Skill, README, workflow reference, tests, Owner Adapter and architecture manifest accordingly;
- retained only the `team.md` Skill/package distribution mirror because both surfaces require it, and added machine equality checking;
- RoleRegistry now declares its local packaged prompt source and the canonical Skill prompt source explicitly.

Distilled rule: **one executable authority; mirrors exist only for a proven distribution need and must be machine-checked.**

## Fixed defect 5 — global Skill references contained active project state

Global references contained project-specific Pilot/Sample consequences. Loading the Skill for a new project could therefore bring historical active-project state into generic operating context.

Fix:

- generalized Agent Studio, reviewer-attestation and production-intelligence references;
- project-specific facts remain under `projects/*` and task continuity state;
- the hygiene Harness dynamically scans every Markdown file under `skills/video-growth-agent/` for known project-state pollution markers and stale root-config references.

Distilled rule: **global Skill stores portable mechanism; project state stays in project authority.**

## Fixed defect 6 — Agent tool labels could be misread as real capability

`agents.json` declared strings such as `image`, `render`, `web` and `media`, but the registry did not prove that the current session/executor actually had those tools, credentials, permissions or modalities.

Fix:

- Agent principles now explicitly define tool labels as capability requests, not execution proof;
- the Skill requires a session capability handshake against `continuity/EXECUTION_CAPABILITIES.json` and actual session tools;
- the assurance taxonomy is pinned: `DECLARED_ONLY`, `HARNESS_WIRED`, `SESSION_EXECUTABLE`, `CHAT_BRIDGED`, `ATTESTED_ISOLATED`;
- `CHAT_BRIDGED` may not masquerade as `ATTESTED_ISOLATED` merely through role switching;
- Harness and tests reject accidental removal of these semantics.

Distilled rule: **declared capability is routing metadata; execution assurance is evidence.**

## Fixed defect 7 — Continuity had become a second business-rule archive

The checkpoint, owner adapter and task index accumulated historical audits, repeated business rules, provider detail and preserved requirement prose. The staged checkpoint-compaction plan itself had become another permanent artifact.

Fix:

- compacted the active checkpoint to executable recovery truth while preserving stage, next action, replay guards, resume epoch and active lease;
- removed cross-domain/preserved-user prose from the checkpoint;
- compacted `TASK_INDEX.md` back to metadata-only discovery;
- compacted Owner Adapter to routing/compatibility/writer/hygiene semantics;
- deleted the completed `CHECKPOINT_COMPACTION_PLAN.json`;
- Harness rejects recurrence of the compaction plan and selected checkpoint/index pollution.

Distilled rule: **continuity points to business truth; it must not become another copy of business truth.**

## Fixed defect 8 — no executable repository hygiene Harness

The repository relied on tests for local behavior but lacked a single command that checked authority duplication, dead Agent profiles, Skill/package mirror drift, project-state pollution and continuity hygiene together.

Fix:

- added `video_growth_agent/system_audit.py`;
- added `vga system-audit --repo-root .` for repository + package checks and `vga system-audit` for installed-package checks;
- CI now runs repository hygiene before pytest, then reruns installed-package audit/CLI smoke outside the repository;
- Harness checks Agent registry/plan validity, dead profiles, producer self-approval configuration, workflow/reviewer coverage, team prompt mirror equality, capability semantics, assurance taxonomy, Skill Git-blob pointer integrity, architecture-manifest authority, root-config absence and continuity hygiene.

A first maintenance CI intentionally went red because old tests still depended on the duplicate root config and because Skill compression accidentally removed capability-handshake terminology. The rules were not weakened: obsolete mirror tests were migrated, while meaningful `session capability handshake`, `CHAT_BRIDGED` and `ATTESTED_ISOLATED` semantics were restored and then promoted into the Harness itself.

Validated behavioral maintenance head: `08f6cb688ad031c637387ce54e7fa964e14c1d92`  
CI run: `38088397683`  
CI job: `114319620599`  
Result: repository system hygiene audit **SUCCESS**, pytest **SUCCESS**, installed-package audit and CLI smoke **SUCCESS**.

## Retention/deletion decisions

Deletion is not age-based.

Deleted because fully superseded and not needed for recovery/regression/failure-learning:
- root `config/*` runtime mirrors;
- completed checkpoint-compaction plan;
- duplicate project-state prose embedded in global Skill/Continuity surfaces;
- unproven legacy user-provided tutorial material as a durable learning source.

Retained deliberately:
- `projects/pilot-001/README.md`, because it records durable production failure-learning such as stream-duration, black-frame, pseudo-3D and evidence-over-invented-interface lessons;
- `audits/SYSTEM_SELF_AUDIT_2026-10-10.md` and this 2026-10-11 audit, because they document different defects, bypasses and regression rationale;
- rejected Pilot 002 audit/sample references needed to prevent invalid replay and explain current recovery state;
- Skill/package `team.md` mirror because both distribution surfaces need it, now under equality enforcement.

## Concurrent-main reconciliation

During this maintenance branch, `main` received `d6b5472e4bc756e19bb4eaaaa462bd6a8c00021e` (`Declare Video Growth Agent product architecture`) adding `continuity/AGENT_MANIFEST.json`. The maintenance process did not overwrite it. Its architecture intent was preserved, while stale references to removed root `config` authority were corrected to `video_growth_agent/data/` and the new system-audit Harness was added to its declared validation surface.

Promotion must therefore be rebased/reparented against the latest observed `main` and use compare-and-swap rather than force-overwriting concurrent work.

## Remaining fail-closed gaps

### Producer execution identity is still not provider-attested

Producer work orders prove declared packet, completion and output provenance, but the current provider-backed `ExecutionAttestation` path is enforced primarily for critical review work. Therefore the system must not claim that every producer persona has independently executed merely because a work order and artifact exist.

Required future evolution: generalize execution attestation or introduce an equally strong producer-execution receipt bound to provider/model/run identity, work-order digest, exact input digests and output/result digests.

### Learning-source admission is policy-pinned but not yet a universal runtime guard

The declared work packet already limits normal agent inputs, and the policy forbids ambient learning. However a universal runtime mechanism that rejects a `learning_candidate` containing undeclared external provenance is not yet wired at the lowest boundary.

Required future evolution: machine-validate learning candidate source manifests against the declared work packet plus explicitly imported learning sources before LEARN can pass.

### Quality-critical generation gateway remains unavailable

The generation guard is stronger, but a single enforced generation gateway that resolves durable review receipts/attestations and then authorizes generator calls is still unavailable. Quality-critical generation therefore remains fail closed.

### Trusted reviewer executors remain empty

Configured reviewer roles and provider adapters do not equal trusted isolated execution. No executor should be promoted to trusted status until live media access, provider/model identity, run/request identity semantics, context/trace semantics and inspectable proof are verified.

### Main branch protection is not enabled

At the latest observation GitHub reports `main` as `protected:false` with required-status-check enforcement off. The maintenance protocol can voluntarily require a green branch CI and compare-and-swap promotion, but that is not equivalent to server-enforced branch protection.

## Business-state preservation

This audit is maintenance only. It does not authorize the frozen full rebuild, does not mark the active visual-preview work as passed, and does not substitute governance hardening for actual isolated Art Director / Creative Director / Red Team execution. The active business stage, next action, resume epoch and active lease remain preserved.

## Net evolution

The system moved from:

- challenge-slot key as implicit reviewer identity -> explicit reviewer-role binding;
- session visibility as an ambiguous learning source -> default-deny learning admission;
- producer completion plus automatic PASS -> producer provenance separated from review authority;
- human-facing config mirror + packaged runtime config -> one packaged runtime authority;
- static known-file hygiene assumptions -> executable dynamic Skill/repository audit;
- Agent tool label as ambiguous capability implication -> declarative request plus assurance taxonomy;
- continuity/history accumulation -> compact recovery pointers plus preserved replay guards.

The remaining gaps are preserved as blockers rather than represented as completed capability.
