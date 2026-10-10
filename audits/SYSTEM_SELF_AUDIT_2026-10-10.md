# Video Growth Agent — System Self-Audit — 2026-10-10

Status: ACTIVE MAINTENANCE EVIDENCE  
Scope: owner/runtime governance only; no Pilot 002 business-stage advancement or media generation  
Trigger: explicit user request to apply the Universal Continuity critique–distill–learn–evolve system to the Video Growth Agent itself

## 1. Audit method

This pass used the current Universal Continuity maintenance/evolution method rather than an informal self-review:

`DETECT -> READ CURRENT AUTHORITY -> DIAGNOSE -> CHALLENGE INITIAL SOLUTION -> COMPARE ALTERNATIVES -> SEARCH FAILURE MODES -> PATCH MINIMUM AUTHORITY SURFACE -> ADD REGRESSION -> VALIDATE -> REREAD`

The audit read current GitHub `main` authority, including:

- `skills/video-growth-agent/SKILL.md`
- `continuity/EXECUTION_CAPABILITIES.json`
- `continuity/OWNER_ADAPTER.json`
- `video_growth_agent/studio_agents.py`
- `video_growth_agent/runtime.py`
- `video_growth_agent/generation_guard.py`
- `video_growth_agent/reviewer_providers.py`
- `video_growth_agent/execution_attestation.py`
- `video_growth_agent/data/execution-plan.json`
- `video_growth_agent/data/agents.json`
- relevant regression tests and Generation Governance / Reviewer Attestation references

## 2. Strongest rejection reasons against the current system

### R1 — Pre-generation PASS could be self-authored

The generation brief embedded `pre_generation_challenge` decisions and the machine guard previously accepted literal `PASS` plus notes as sufficient challenge state. No work-order receipt, executor attestation or exact external review evidence was required by `generation_guard.py`.

Failure mode:

1. edit the brief;
2. set `art_creative.decision = PASS`;
3. set `red_team.decision = PASS`;
4. structural guard accepts the challenge despite no independent reviewer execution.

This contradicted the owner invariant that role/config declarations are not execution proof.

Disposition: **CONFIRMED SYSTEM DEFECT**.

### R2 — LEARN could be bypassed at the lower runtime boundary

`execution-plan.json` correctly schedules:

`Production Methodologist -> Evolution Engineer -> Red Team -> Showrunner`

But `StudioRuntime.PROCESS_ENFORCED_STAGES` did not include `LEARN`. `AgenticStudio.advance()` checked work-order completion, while direct `StudioRuntime.advance()` did not require the LEARN work-order pipeline.

Failure mode:

- manually create `learning_receipt`;
- manually sign Red Team and Showrunner;
- call the lower runtime advance path;
- declared learning roles can be bypassed.

This was the same architectural class as the earlier visual-review bypass: policy stronger than base enforcement.

Disposition: **CONFIRMED SYSTEM DEFECT**.

### R3 — Reviewer evidence classes are not yet cleanly separated

The current Gemini adapter preserves provider-issued `responseId` / resolved model identity, but `context_id`, `trace_id` and `proof_ref` are supplied by the caller and echoed back. Therefore these fields are correlation/evidence metadata, not automatically provider-issued proof.

The current trust registry is empty, so this has not authorized production review. However the evidence vocabulary can overstate what a future provider actually proves if registration is done carelessly.

Disposition: **CONFIRMED TRUST-MODEL GAP; still fail-closed**.

### R4 — No executable isolated pre-generation reviewer work-order path yet

Generation Governance requires independent Art/Creative and Red Team challenge before promotable quality-critical generation. The current stage execution plan contains post-generation VISUAL_PREVIEW review work orders, but no owner-runtime path that resolves isolated pre-generation review receipts into generation authorization.

Therefore the current `quality_critical_generation_gateway` remains correctly declared `UNAVAILABLE`.

Disposition: **CONFIRMED EXECUTION-WIRING GAP; current generation must remain blocked**.

## 3. Candidate comparison

### Candidate A — Add more roles/policies

Rejected.

Reason: the system already has the right professional separation. More role names would increase declaration surface without closing execution bypasses.

### Candidate B — Connect Gemini/OpenRouter first and call the reviewer problem solved

Rejected.

Reason: provider connectivity alone does not solve generation authorization, receipt binding, LEARN runtime bypass, or truthful provider/local evidence semantics.

### Candidate C — Harden existing execution boundaries and make evidence authority explicit

Accepted.

Reason: smallest change with direct failure containment. It preserves existing role architecture while forcing declared specialist work to leave executable proof.

## 4. Distilled reusable lessons

1. **A role is not a control.** A control exists only when the lowest relevant runtime boundary rejects bypass.
2. **Status is not evidence.** `PASS` in a project JSON is state/reporting; authorization must resolve durable execution evidence outside the artifact being approved.
3. **Proof classes must remain distinct.** Provider-issued IDs, local correlation IDs, artifact digests and durable receipt refs must not be rhetorically collapsed into one "trace" claim.
4. **The learning system must obey its own learning rules.** Methodologist/Evolution/Red-Team/Showrunner execution cannot be optional merely because the output is named `learning_receipt`.
5. **Do not fix governance defects by adding personas.** Prefer runtime enforcement, immutable evidence binding and regression tests.
6. **Fail-closed blockers are useful truth.** An unavailable generation gateway or empty trusted-executor registry is safer than a simulated multi-agent PASS.

## 5. Applied evolution in this pass

### Patch A — LEARN base-runtime enforcement

`video_growth_agent/runtime.py`

- added `LEARN` to `PROCESS_ENFORCED_STAGES`;
- direct `StudioRuntime.advance()` can no longer bypass configured LEARN work orders.

Regression:

`tests/test_learning_runtime_enforcement.py`

- constructs the previous bypass explicitly;
- manually supplies `learning_receipt` and required role approvals;
- requires the base runtime to reject advancement because Methodologist/Evolution work orders are absent.

### Patch B — Generation challenge evidence moved outside the brief

`video_growth_agent/generation_guard.py`

- generation brief authoring contract now has a stable digest;
- inline challenge `PASS` is no longer sufficient authorization;
- `assert_generation_brief()` requires an externally resolved verified challenge bundle;
- each required review proof must bind work order, review receipt, attestation, executor/execution identity, provider run, context/trace correlation, packet/result digests, exact brief digest and proof ref;
- sibling challenge identities cannot be reused.

Regression:

`tests/test_generation_guard.py`

- self-authored inline PASS without external evidence fails;
- exact brief digest mismatch fails;
- context reuse across required challenge executions fails;
- properly bound independent test evidence passes the structural authorization guard.

### Patch C — Governance language corrected

`skills/video-growth-agent/references/generation-governance.md`

- distinguishes inline status from execution proof;
- states explicitly that the current guard validates evidence shape/binding but does not resolve receipt existence/trust itself;
- keeps the single enforced generation gateway as a hard blocker until implemented;
- distinguishes provider-issued proof from local correlation IDs;
- states that LEARN is governed work and cannot be satisfied by manual artifact/signature injection.

## 6. What is deliberately NOT claimed fixed

1. A single enforced quality-critical generation gateway is still not implemented.
2. No production multimodal reviewer executor is registered; `trusted_executors` remains empty.
3. Gemini/OpenRouter adapters are still candidates, not trusted production executors.
4. The runtime still needs an executable isolated pre-generation reviewer work-order/receipt resolver before Shot A/D can be authorized.
5. Provider-proof semantics need an end-to-end live proof record before trust registration. In particular, locally supplied context/trace identifiers must not be described as provider-issued unless the provider actually issues/verifies them.

These are blockers, not reasons to weaken the gate.

## 7. Business-state boundary

This audit does not change the Pilot 002 business stage or execute its next action. `video-growth:main` remains at `VISUAL_PREVIEW_PROCESS_REENTRY`; the 59.5-second rebuild remains frozen and quality-critical generation remains fail-closed.
