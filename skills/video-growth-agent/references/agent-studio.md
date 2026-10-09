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

## Context and cost discipline
Registered Agent profiles are ephemeral capabilities, not permanently running personas. Invoke only the agents required by the current stage. Keep tool permissions and artifact inputs least-privileged. Parallelize only independent work; keep dependency-sensitive work serial.

## Producer arbitration
The Producer may resolve scheduling or conflicting soft recommendations, but cannot turn a deterministic FAIL, rights FAIL, factual FAIL, or required craft FAIL into PASS. If reviewers disagree on a hard dimension, route the artifact back for revision or collect better evidence.

## Production rule
The team is not a chat room. It is an artifact pipeline:
`WORK ORDER → ISOLATED SPECIALIST → VERSIONED ARTIFACT → BLIND REVIEW → META/PRODUCER SYNTHESIS → GATE`.

This architecture is implemented in `video_growth_agent/studio_agents.py`, `video_growth_agent/data/agents.json`, and `video_growth_agent/data/execution-plan.json`.
