# System Self-Audit — 2026-10-11

Status: **HARDENED_WITH_REMAINING_FAIL_CLOSED_GAPS**

Scope: control plane, learning admission, execution evidence, generation authorization, Harness/Agent/Skill authority hygiene, continuity compaction, work-order replay safety, artifact reachability and production-knowledge admission. This maintenance pass does not advance the active business stage and does not treat maintenance activity as production progress.

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
- the hygiene Harness scans every Markdown file under `skills/video-growth-agent/` for project-state pollution and stale root-config references.

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
- CI runs repository hygiene before pytest, then reruns installed-package audit/CLI smoke outside the repository;
- Harness checks Agent registry/plan validity, dead profiles, producer self-approval configuration, workflow/reviewer coverage, team prompt mirror equality, capability semantics, assurance taxonomy, Skill Git-blob pointer integrity, architecture-manifest authority, root-config absence and continuity hygiene.

A first maintenance CI intentionally went red because old tests still depended on the duplicate root config and because Skill compression accidentally removed capability-handshake terminology. The rules were not weakened: obsolete mirror tests were migrated, while meaningful `session capability handshake`, `CHAT_BRIDGED` and `ATTESTED_ISOLATED` semantics were restored and then promoted into the Harness itself.

Earlier validated behavioral maintenance head: `08f6cb688ad031c637387ce54e7fa964e14c1d92`  
Earlier CI run: `38088397683`  
Earlier CI job: `114319620599`  
Result: repository system hygiene audit **SUCCESS**, pytest **SUCCESS**, installed-package audit and CLI smoke **SUCCESS**.

## Re-entry audit — runtime 0.5.2

The same authoritative `main` was challenged again instead of assuming the previous green CI meant the architecture was clean. This second pass found executable defects that the original Harness did not model.

### Fixed defect 9 — invalidation could resurrect stale completed work orders and evidence

`invalidate_from()` cleared approvals and moved the stage backward but left downstream active artifacts and QA pointers in state. Work-order IDs were stable by task, and `dispatch_stage()` treated any prior `COMPLETED` order as permanently complete. Producer work orders also lacked current-input digest enforcement. A material upstream change could therefore leave stale work orders/artifacts active or force manual filesystem cleanup before a legitimate rerun.

Fix:

- invalidation now retires downstream **active** artifact/QA pointers while preserving immutable historical receipts;
- changed upstream artifacts preserve the newly written source artifact but invalidate dependent active outputs;
- work-order IDs are generation-aware and include the current state revision;
- completed work orders are retired and regenerated when task contract, current input digests or current output provenance no longer match;
- producer/measure work orders now persist input digest bindings;
- the base process guard checks current input digest bindings for produce, measure, review and meta-review tasks;
- historical review attestations authorize only their exact work-order generation;
- historical execution/provider/context/trace identities remain non-reusable, preventing the same external execution from being repackaged as a new run.

Distilled rule: **immutable history may survive invalidation; active authorization may not. A rerun needs a new work-order generation and, where attested, a new execution identity.**

### Fixed defect 10 — TECH_QA depended on an undeclared side effect

The execution plan had `media_qa` with no declared output while the following reviewer required `technical_qa`. Runtime `record_qa()` happened to create that artifact as a side effect, so the graph looked valid only to callers that knew an undocumented bridge.

Fix:

- `media_qa` explicitly declares `technical_qa` as its single output;
- ffmpeg/ffprobe measure work orders cannot be completed through generic `complete_work()`;
- `complete_media_qa()` is the governed completion path and binds the QA receipt/artifact to the active work-order ID and input digest;
- artifact-reachability Harness checks stage/wave producers and catches hidden inputs;
- RELEASE `final_media` and `publish_pack` are explicitly declared external stage inputs with an owner boundary contract rather than silently appearing from outside the execution graph.

Distilled rule: **if an artifact is required downstream, its producer or external boundary must be explicit in the execution graph.**

### Fixed defect 11 — Agent kind and execution-plan usage could contradict each other

`growth_strategist` was registered as reviewer-only while the PERFORMANCE stage assigned it a `produce` task. The old validator blocked worker-as-reviewer but did not block reviewer-as-producer.

Fix:

- `growth_strategist` is now a supervisor because it performs both judgment and post-publication analysis without self-approving stage gates;
- planner validation rejects reviewer-only Agents used as producers.

Distilled rule: **Agent kind is a capability boundary, not decorative taxonomy. Execution-plan use must be compatible with it.**

### Fixed defect 12 — Technique Library candidates leaked into ordinary production lookup

Historical candidate techniques were queryable by default and some carried bare vendor/tool names as `evidence_refs`. The learning policy had already moved to default-deny admission, but the old Technique Library schema/query behavior had not been migrated.

Fix:

- `TechniqueLibrary.find()` is validated-only by default;
- candidate techniques require explicit `validated_only=False` / CLI `--include-candidates` opt-in and are restricted to learning/prototype use;
- every technique now records an origin class;
- historical external candidates point to durable repository rationale/project evidence instead of bare vendor labels;
- legacy validated techniques are honestly marked as pre-admission/grandfathered rather than being retroactively presented as newly source-verified;
- Harness checks production-default isolation, technique status/origin and durable evidence shape for historical external candidates.

Distilled rule: **a useful candidate is not production knowledge until admitted and validated; discoverability must respect that boundary.**

### Fixed defect 13 — Harness encoded the current repository instead of the architecture

The first Harness hard-coded runtime `0.5.1` and a three-string project pollution list. A normal version bump or differently named future project could make the checker itself stale.

Fix:

- runtime version is derived from installed package metadata / `pyproject.toml`;
- Agent/ExecutionPlan/Architecture/Continuity version checks compare dynamically against that authority;
- project aliases are derived from `projects/*` instead of a fixed project-name list;
- versioned Sample/Release state is scanned structurally;
- artifact reachability is derived from workflow order, task waves, declared outputs and explicit external inputs.

Distilled rule: **a Harness should encode invariants, not memorize today's filenames, version number or project names.**

### Fixed defect 14 — CI execution substrate had become stale and mutable

CI used `ubuntu-latest`, `actions/checkout@v4` and `actions/setup-python@v5`; prior logs already warned that the old Node 20 action runtime was deprecated and being forced onto Node 24.

Fix:

- runner pinned to `ubuntu-24.04`;
- checkout pinned to official v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1`;
- setup-python pinned to official v7.0.0 commit `5fda3b95a4ea91299a34e894583c3862153e4b97`;
- pytest is pinned to `9.1.1` in CI;
- installed smoke derives package version dynamically and checks Agent/Plan consistency instead of hard-coding the release number.

Distilled rule: **the Harness substrate is part of the Harness; mutable/deprecated CI dependencies are themselves governance debt.**

### Re-entry validation

Validated behavioral re-entry head: `4de1c520a1e23b50af132d500025e63f8fa764d9`  
CI run: `38109430324`  
CI job: `114381713154`  
Result:

- repository + package `vga system-audit`: **PASS, zero failures**;
- pytest: **113 passed**;
- installed-package audit: **PASS**;
- installed CLI/AgenticStudio smoke: **PASS**;
- pinned checkout/setup-python actions executed successfully on Ubuntu 24.04.

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
- Skill/package `team.md` mirror because both distribution surfaces need it, now under equality enforcement;
- immutable historical work-order/review/QA/attestation receipts; invalidation retires active pointers rather than deleting historical failure/recovery evidence.

### Remote branch hygiene

The branch namespace is also a pollution surface even though Runtime does not load branch refs.

Confirmed safe stale refs:
- `maintenance/system-harness-cleanup-2026-10-11` was identical to `main` at inspection;
- `pilot002-sample-v1` had no commits ahead of `main` and was only an old ancestor.

Branches such as `learning-visual-dev-2026-10-09` and `tts-pilot002-kokoro` contain unique specialist material and are **not** classified as disposable until that material is either explicitly retained or distilled into authority. Several older hardening/runtime branches appear functionally superseded but still carry unique commit history, so age/name alone is insufficient deletion proof.

The connected GitHub control surface does not expose branch-ref deletion. Therefore no remote branch is falsely reported as deleted; safe deletion candidates are recorded for later repository-admin cleanup.

## Concurrent-main reconciliation

During the earlier maintenance branch, `main` received `d6b5472e4bc756e19bb4eaaaa462bd6a8c00021e` (`Declare Video Growth Agent product architecture`) adding `continuity/AGENT_MANIFEST.json`. The maintenance process did not overwrite it. Its architecture intent was preserved, while stale references to removed root `config` authority were corrected to `video_growth_agent/data/` and the system-audit Harness was added to its declared validation surface.

Every promotion must be reconciled against the latest observed `main` and use compare-and-swap rather than force-overwriting concurrent work.

## Remaining fail-closed gaps

### Producer execution identity is still not provider-attested

Producer work orders now prove current input digests, completion and output provenance, but the provider-backed `ExecutionAttestation` path is still enforced primarily for critical review work. Therefore the system must not claim that every producer persona has independently executed merely because a work order and artifact exist.

Required future evolution: generalize execution attestation or introduce an equally strong producer-execution receipt bound to provider/model/run identity, work-order generation, exact input digests and output/result digests.

### Learning-source admission is policy-pinned but not yet a universal runtime guard

The declared work packet already limits normal agent inputs, and the policy forbids ambient learning. Technique candidates are now isolated from production lookup. However a universal runtime mechanism that rejects a `learning_candidate` containing undeclared external provenance is not yet wired at the lowest boundary.

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
- static known-file hygiene assumptions -> structural/dynamic Skill/repository audit;
- Agent tool label as ambiguous capability implication -> declarative request plus assurance taxonomy;
- continuity/history accumulation -> compact recovery pointers plus preserved replay guards;
- stable task-name work orders + active stale outputs -> generation-aware work orders + retired active evidence;
- implicit QA/Release artifact side effects -> explicit producer/external-boundary graph semantics;
- candidate technique discoverability -> production-safe validated-only lookup;
- mutable/deprecated CI major tags -> pinned current CI substrate.

The remaining gaps are preserved as blockers rather than represented as completed capability.
