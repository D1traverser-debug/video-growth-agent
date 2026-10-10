# Agentic Studio Architecture

## Purpose
Role prompts are not execution isolation. A creator that changes labels inside one context can carry intent, sunk-cost bias and self-justification into its own review. The studio therefore separates production, review and deterministic measurement at runtime.

## Architecture
Use the lowest coordination complexity that preserves independence:

1. **Executive Producer / orchestrator** owns project state, dispatch, work orders, conflict routing and the single user-facing voice. It does not create craft artifacts and cannot override hard gates.
2. **Worker Agents** produce declared artifacts from explicit work orders and least-context inputs.
3. **Reviewer Agents** judge actual outputs from distinct professional loss functions. Blind reviewers do not see sibling verdicts or project approvals.
4. **Review Panel + Meta Reviewer** is used only where audience diversity or synthesis is useful. First-wave reviewers execute independently before meta-review.
5. **Deterministic Tools** such as FFmpeg/ffprobe remain tools, not persona agents.

The executable registry and work-order plan are `video_growth_agent/data/agents.json` and `video_growth_agent/data/execution-plan.json`. Implementation lives in `video_growth_agent/studio_agents.py` and `video_growth_agent/runtime.py`.

## Capability declaration is not execution proof
The `tools` field on an Agent profile declares the capabilities that work order may require. It does not prove that the current chat/session/executor actually has those tools, credentials, media access or permissions. The owner capability handshake and execution evidence remain authoritative. Never infer execution readiness from an Agent profile alone.

## Communication contract
Agents do not peer-chat. Handoffs use versioned artifacts, exact digests, work-order state and immutable receipts. The next specialist reads the declared artifact packet, not another specialist's hidden reasoning or persuasive summary.

## Independence contract
- A producer cannot approve its own output merely because its work order completed.
- A reviewer must not approve an artifact it produced.
- Separate implementation workers from department-head reviewers when self-review risk is material.
- Blind review packets contain only declared inputs, role prompt, rubric and benchmark references; sibling verdicts are excluded.
- Majority vote never replaces a hard domain veto or missing evidence.

## Review-proof invariant
A quality-critical artifact is not **reviewed** because an aggregate note or role label exists. A valid critical review requires the configured work order, durable review receipt, exact artifact/input binding and any required execution attestation. Missing proof is `PROCESS_INVALID` and blocks advancement.

## Anti-bypass rule
Every stage with tasks in `video_growth_agent/data/execution-plan.json` is process-enforced at the base `StudioRuntime` boundary. Calling a lower-level runtime path cannot substitute manually created artifacts or approvals for the required work orders.

Ad-hoc/manual QA may diagnose defects or create exploratory evidence, but it cannot satisfy a governed stage unless it is re-entered through the evidence contract.

## Context and cost discipline
Registered Agent profiles are ephemeral capabilities, not permanently running personas. Invoke only the agents required by the current work order. Parallelize only independent work. Do not add agents merely to increase role count; add a specialist only when it owns a distinct artifact, loss function, permission boundary or veto.

## Producer arbitration
The Executive Producer may resolve scheduling and conflicting soft recommendations. It cannot turn a deterministic FAIL, rights FAIL, factual FAIL, required craft FAIL, missing execution proof or `PROCESS_INVALID` state into PASS.

## Reflection contract
A failed candidate should produce structured learning evidence:

`OBSERVED FAILURE -> ROOT CAUSE -> COUNTERFACTUAL -> REPAIR HYPOTHESIS -> SMALLEST TEST -> RESULT -> ACCEPT/REJECT -> RULE CHANGE`

Reflection that changes no rule, benchmark, work order, artifact, experiment or routing decision is commentary, not system learning.

## Production invariant
`WORK ORDER -> EXECUTOR -> VERSIONED ARTIFACT/RESULT -> INDEPENDENT REVIEW -> EVIDENCE BINDING -> GATE`

Never confuse "the system has a role or rule" with "that role or rule was executed and evidenced".
