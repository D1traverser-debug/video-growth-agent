# Agentic Studio Architecture

## Why this exists
Role prompts alone are not sufficient isolation. A creator that immediately changes hats can carry intent, sunk-cost bias and self-justification into its own review. The studio therefore separates production, review and deterministic measurement at runtime.

## Architecture
Use the lowest coordination complexity that preserves independence:

1. **Executive Producer / orchestrator** — owns project state, dispatch, work orders, conflict routing and the single user-facing voice. It does not create craft artifacts and cannot override hard gates.
2. **Worker Agents** — produce research, scripts, storyboards, lookdev, motion, assets, edits and sound from explicit work orders. They receive only declared input artifacts.
3. **Reviewer Agents** — independently judge outputs from their professional loss function. Blind reviewers cannot see sibling verdicts or project approvals while reviewing.
4. **Review Panel + Meta Reviewer** — where audience diversity matters, multiple isolated reviewers report first; only then may a meta-reviewer synthesize their evidence. Do not use free-form group debate.
5. **Deterministic Tools** — ffprobe/FFmpeg/media measurements and other mechanically verifiable checks stay tools, not persona agents.

## Communication contract
Agents do not peer-chat. All handoffs go through versioned artifacts, SHA/digest identity, work-order state and immutable receipts. The next specialist reads the artifact, not the previous specialist's chain-of-thought or persuasive explanation.

## Independence contract
- A reviewer must not approve an artifact it produced.
- Separate implementation workers from department-head reviewers when self-review risk is material: visual designer vs art director, motion designer vs motion director, assistant editor vs editor, sound designer vs sound director.
- A blind review packet contains only required artifacts, role prompt, rubric and benchmark references. It excludes sibling verdicts.
- Audience panels review independently; meta-review runs only after all first-wave panel reviews complete.
- Majority vote is not a substitute for hard vetoes or evidence. A minority reviewer may block when its domain has veto authority.

## Review-proof invariant
A quality-critical artifact is not considered **reviewed** merely because an aggregate QA note exists.

For every required reviewer in the current workflow stage, persist a durable review receipt bound to the exact target artifact digest. At minimum the receipt must identify:

- project and stage;
- work-order id;
- reviewer agent id and approval role;
- target artifact digest;
- blind-review packet identity or equivalent evidence boundary;
- decision;
- role-specific findings;
- scorecard when configured;
- benchmark references when required;
- evidence references;
- timestamp.

Missing required receipt means `PROCESS_INVALID` and blocks the quality gate even when an aggregate score would otherwise pass.

## Anti-bypass rule
Quality-critical stages must execute through the configured `AgenticStudio` work-order runtime or an explicitly compatible runtime that produces the same evidence contract.

Ad-hoc/manual QA may diagnose defects, prototype a repair, or create exploratory evidence, but it **cannot** satisfy LOOKDEV, VISUAL_PREVIEW, ROUGH_CUT, TECH_QA, AUDIENCE_QA, BRAND_QA, RED_TEAM or RELEASE.

If an artifact was created or judged outside the work-order runtime:

1. label it exploration/previs/manual-diagnostic evidence;
2. do not describe it as having passed or completed the configured review process;
3. re-enter the correct stage and generate the full required receipt bundle before advancement.

The existence of role definitions, prompts, an execution plan or a summary scorecard is not evidence that the roles actually ran.

## Context and cost discipline
Registered Agent profiles are ephemeral capabilities, not permanently running personas. Invoke only the agents required by the current stage. Keep tool permissions and artifact inputs least-privileged. Parallelize only independent work; keep dependency-sensitive work serial.

Do not add agents merely to increase role count. Add a specialist only when it owns a distinct loss function, artifact, tool permission or veto. Otherwise improve the work contract, evidence packet, benchmark or deterministic guardrail.

## Producer arbitration
The Producer may resolve scheduling or conflicting soft recommendations, but cannot turn a deterministic FAIL, rights FAIL, factual FAIL, required craft FAIL or `PROCESS_INVALID` state into PASS. If reviewers disagree on a hard dimension, route the artifact back for revision or collect better evidence.

## Reflection contract
A failed candidate must produce structured learning evidence:

`OBSERVED FAILURE → ROOT CAUSE → COUNTERFACTUAL → REPAIR HYPOTHESIS → SMALLEST TEST → RESULT → ACCEPT/REJECT → RULE CHANGE`

Reflection that does not alter a rule, benchmark, work order, artifact, experiment or routing decision is commentary, not studio learning.

## Production rule
The team is not a chat room. It is an artifact pipeline:
`WORK ORDER → ISOLATED SPECIALIST → VERSIONED ARTIFACT → BLIND REVIEW → META/PRODUCER SYNTHESIS → GATE`.

The Executive Producer must separately control:

- **macro project state** — objective, stage, dependencies, budget, benchmark, current risk and next irreversible decision;
- **micro shot state** — shot contract, references, start/end states, engine, version, reviewer receipts and repair history.

Never confuse "the system has a rule" with "the rule was executed and evidenced".

This architecture is implemented in `video_growth_agent/studio_agents.py`, `video_growth_agent/data/agents.json`, and `video_growth_agent/data/execution-plan.json`.
