# Video Growth Agent — System Self-Audit — 2026-10-10

Status: ACTIVE MAINTENANCE EVIDENCE  
Scope: owner/runtime governance only; no Pilot 002 business-stage advancement or media generation  
Trigger: explicit user request to apply the Universal Continuity critique–distill–learn–evolve system to the Video Growth Agent itself

## 1. Method

This was not an informal self-review. The pass followed the current Universal control-plane maintenance/evolution method:

`DETECT -> READ CURRENT AUTHORITY -> DIAGNOSE -> CHALLENGE INITIAL SOLUTION -> COMPARE ALTERNATIVES -> SEARCH FAILURE MODES -> PATCH MINIMUM AUTHORITY SURFACE -> ADD REGRESSION -> VALIDATE -> REREAD`

Current GitHub `main` authority was inspected across Skill, Continuity capability metadata, workflow/execution plan, agent registry, StudioRuntime, AgenticStudio, generation guard, reviewer adapters, execution attestation/trust registry, generation/reviewer governance and regression tests.

## 2. Strongest rejection reasons

### R1 — Inline pre-generation PASS could masquerade as execution

The generation brief embedded challenge decisions and the original machine guard accepted literal `PASS` plus notes. A caller could therefore hand-edit the JSON and satisfy the structural preflight without any reviewer work order, receipt, attestation or exact external evidence binding.

Disposition: **CONFIRMED DEFECT; HARDENED**.

### R2 — Base process enforcement was incomplete by construction

`execution-plan.json` defines governed work across almost every stage, but `StudioRuntime` previously process-enforced only a hard-coded subset. LEARN exposed the defect clearly: a caller could theoretically inject the required artifact and approvals and call the lower runtime path without executing Production Methodologist / Evolution Engineer work orders. The same architectural omission applied to any planned stage not on the hard-coded list.

Disposition: **CONFIRMED DEFECT; GENERALIZED FIX APPLIED**.

### R3 — Reviewer evidence classes could be overstated

Candidate provider adapters can expose real provider response/run/model evidence, while context/trace correlation fields may be owner-supplied. Treating every normalized attestation field as provider-issued would overstate proof strength.

Disposition: **CONFIRMED TRUST-MODEL GAP; TRUST REGISTRATION HARDENED, LIVE EXECUTOR STILL BLOCKED**.

### R4 — No executable isolated pre-generation reviewer resolver/gateway

The owner requires independent pre-generation challenge before promotable quality-critical image/video generation, but it still has no single executable path that dispatches isolated pregen reviewers, resolves their durable receipts/attestations, authorizes the exact brief/prompt and binds the subsequent generation call/artifact to that authorization.

Disposition: **CONFIRMED EXECUTION-WIRING GAP; REMAINS FAIL-CLOSED**.

### R5 — Art Director and Creative Director were collapsed into one pregen slot

The pre-generation brief used one `art_creative` verdict. That allowed one execution to stand in for two distinct professional authorities despite the studio's maker/reviewer and specialization principles.

Disposition: **CONFIRMED FALSE-SEPARATION DEFECT; SPLIT INTO THREE INDEPENDENT CHALLENGES: Art Director, Creative Director, Red Team**.

## 3. Candidate comparison

### Candidate A — Add more agents or more policy prose
Rejected. The system already had the necessary professional roles; the defects were enforcement and proof-boundary defects.

### Candidate B — Connect Gemini/OpenRouter first and call the review architecture solved
Rejected. Connectivity does not solve pregen authorization, runtime bypass, evidence provenance or independent-role semantics.

### Candidate C — Harden the existing runtime/evidence boundaries and add adversarial regressions
Accepted. It is the smallest approach that turns declarations into enforceable controls without increasing persona/policy sprawl.

## 4. Distilled reusable rules

1. **A role is not a control.** The lowest relevant runtime boundary must reject bypass.
2. **Status is not evidence.** A `PASS` value inside the artifact being approved cannot authorize itself.
3. **Configured work implies process proof.** If a stage has execution-plan tasks, the base runtime must require their work-order evidence; enforcement must be derived from the plan rather than a manually maintained stage list.
4. **Professional separation must survive into evidence.** Art Director and Creative Director cannot be merged into one approval identity merely for convenience.
5. **Proof classes remain distinct.** Provider-issued IDs, owner correlation IDs, artifact/request/result digests and durable receipt refs are different evidence classes.
6. **The learning system obeys its own governance.** Naming an artifact `learning_receipt` does not prove Methodologist/Evolution/Red-Team/Showrunner execution.
7. **Do not repair governance by multiplying personas.** Prefer runtime enforcement, immutable evidence binding and falsifying regression tests.
8. **Fail-closed blockers are useful truth.** An unavailable generation gateway or empty trusted-executor registry is safer than simulated independent review.

## 5. Applied evolution

### Patch A — Process proof now covers every planned stage

`video_growth_agent/runtime.py`

- removed the fragile hard-coded process-enforced stage list;
- process enforcement is now derived from `execution-plan.json`;
- every stage with configured tasks requires work-order proof at the base `StudioRuntime` boundary;
- only a valid no-task/terminal stage is exempt.

Regressions:

- `tests/test_learning_runtime_enforcement.py` constructs the former LEARN bypass with manually injected artifact/approvals and requires rejection;
- `tests/test_process_enforcement_scope.py` proves that even INTAKE cannot be advanced through the lower runtime with a manually injected brief/approval and no work order.

### Patch B — Pre-generation PASS is evidence-bound

`video_growth_agent/generation_guard.py`

- the generation authoring contract has an exact stable digest;
- inline challenge status is not authorization;
- an externally resolved verified challenge bundle is mandatory;
- each proof binds work order, review receipt, attestation, executor/execution identity, provider run, context/trace correlation, packet/result digests, exact brief digest and proof ref;
- sibling review identities cannot be reused.

Regressions in `tests/test_generation_guard.py` reject:

- inline self-authored PASS with no evidence bundle;
- wrong brief digest;
- reused execution context;
- legacy combined `art_creative` evidence standing in for two reviewers.

### Patch C — Art / Creative / Red Team are three independent pregen authorities

The hard gate now requires:

- `art_director`
- `creative_director`
- `red_team`

`projects/pilot-002/SAMPLE_V3_GENERATION_BRIEF.json` and `SAMPLE_V3_SHOT_D_GENERATION_BRIEF.json` were updated only in their governance challenge fields. All three remain `BLOCKED_PENDING_ISOLATED_EXECUTION`; creative shot content was not advanced or regenerated.

### Patch D — Trusted executor registrations must declare evidence semantics

`video_growth_agent/execution_attestation.py` and `video_growth_agent/data/executors.json`

A future trusted executor must explicitly declare:

- whether provider run/request identity is provider-issued/inspectable;
- whether context/trace fields are provider-issued or owner correlation;
- proof-ref class;
- actual isolation mechanism.

Missing or invalid semantics fail closed. Production `trusted_executors` remains empty.

Regression: `tests/test_execution_identity_semantics.py` rejects an executor whose evidence-source semantics are absent or falsely classified.

### Patch E — Capability/governance truth was refreshed

- `continuity/EXECUTION_CAPABILITIES.json` profile advanced to v4 and now describes the generalized base-runtime process gate, three independent pregen reviewer evidence requirements and truthful provider/local identity separation.
- `skills/video-growth-agent/references/generation-governance.md` now explicitly forbids the combined Art/Creative shortcut.
- `skills/video-growth-agent/references/reviewer-execution-attestation.md` separates provider-issued evidence from owner-local correlation identity.

## 6. Remaining hard blockers

The audit does **not** claim these are solved:

1. `quality_critical_generation_gateway` is still not implemented as one enforced runtime gateway.
2. Production `trusted_executors` is still empty; no real multimodal reviewer can yet authorize the critical gate.
3. The owner still lacks the executable isolated pre-generation reviewer work-order/receipt resolver that produces the three evidence bundles consumed by the generation guard.
4. Gemini/OpenRouter remain candidate adapters only; live modality, isolation and exact provider-proof semantics must be demonstrated before trust registration.
5. Mid-stage/repeated-failure learning has owner sidecar methodology but no fully universal automatic event-trigger execution path.

These remain blockers; none is converted into a paper PASS.

## 7. Business-state boundary

This audit did not execute the Pilot 002 business `next_action`, did not generate media and did not advance the video stage. `video-growth:main` remains `VISUAL_PREVIEW_PROCESS_REENTRY`; Shot A/D remain blocked, and the 59.5-second rebuild remains frozen.

## 8. Validation status

The code/regression changes are committed to `main`. Final validation is the repository CI run on the final self-audit head; this section must only be marked PASS after that run completes successfully and the authoritative owner/continuity state is re-read.
