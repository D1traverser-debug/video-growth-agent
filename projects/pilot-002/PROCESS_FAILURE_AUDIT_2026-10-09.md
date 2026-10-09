# Pilot 002 — Process Failure Audit — 2026-10-09

Status: **PROCESS FAILURE / FAIL CLOSED**

## Executive conclusion

Sample V2 was a real rendered artifact and its visual QA correctly returned FAIL, but it was **not reviewed through the configured agent-studio execution contract**. Therefore the prior wording that it had been "reviewed according to process" was inaccurate.

The failure is governance, not merely taste.

## Contract that should have executed

At `VISUAL_PREVIEW`, the configured workflow requires independent review by:

- creative_director
- art_director
- motion_director
- director
- retention_editor

The execution plan requires blind first-wave reviews, artifact-only handoffs, no peer chat, and completion through `AgenticStudio` work orders before stage advancement.

## Evidence found

Persisted Sample V2 evidence contains:

- rendered MP4
- contact sheet
- one aggregate `QA.md`
- checksum file
- one aggregate GitHub sample record

No durable per-role review receipts were found for the five required VISUAL_PREVIEW reviewers.

## Root causes

1. **Runtime bypass** — the sample was produced and assessed on an ad-hoc path instead of through `AgenticStudio.dispatch_stage / work_packet / submit_review / advance`.
2. **Orchestrator self-review contamination** — one coordinating intelligence synthesized craft judgments that should have been isolated specialist reviews.
3. **Role-count illusion** — having role definitions and an execution plan was mistaken for actually executing those roles.
4. **Evidence weakness** — a single aggregate scorecard looked rigorous but could not prove reviewer independence, least-context review, or role-specific loss functions.
5. **Benchmark incompleteness** — the benchmark pack was strong in motion/brand/explanation work but did not yet include a formal feature-film cinematography/editing benchmark lane.
6. **Learning breadth without closure** — many external tools/workflows were inspected, but candidate methods were not always tied to a falsifiable production experiment and acceptance/rejection receipt.
7. **No anti-bypass tripwire** — the system allowed a manually produced artifact to be described as reviewed even though the work-order runtime had not generated receipts.

## Corrective actions

### A. Review-proof invariant
A quality-critical artifact is not "reviewed" unless every required review work order has a durable receipt bound to the exact artifact digest. Missing receipt = `PROCESS_INVALID`, regardless of aggregate score.

### B. No manual quality-gate substitution
Ad-hoc/manual QA may diagnose defects but can never satisfy LOOKDEV, VISUAL_PREVIEW, ROUGH_CUT, TECH_QA, BRAND_QA, RED_TEAM or RELEASE gates.

### C. Independent reviewer bundle
For every quality-critical candidate persist:

- artifact digest
- reviewer role + agent id
- blind-review packet digest
- decision
- scorecard
- findings
- benchmark refs
- evidence refs
- timestamp

Meta-review may run only after all required first-wave reviews are complete.

### D. Reflection loop
After every failed candidate, create a structured failure memory:

`OBSERVED FAILURE → ROOT CAUSE → COUNTERFACTUAL → REPAIR HYPOTHESIS → SMALLEST TEST → RESULT → ACCEPT/REJECT → RULE CHANGE`

Reflection that does not change a rule, benchmark, work order, artifact, or experiment is commentary, not learning.

### E. Cinematic benchmark lane
Add film-language references alongside motion/brand benchmarks. Calibrate at minimum:

- human-scale blocking and screen interaction
- lens / shot-size progression
- material weight and practical-light logic
- spatial reveal / world transition
- editorial rhythm and sound-image causality

Use feature-film references as grammar calibration, never visual cloning.

### F. Agent-management principle
Do not increase agent count by default. Add a specialist only when it owns a distinct loss function, artifact, tool permission or veto. Otherwise improve the work contract, evidence packet or deterministic guardrail.

### G. Sample V2 disposition
Sample V2 remains useful only as timing/spatial previs. Its visual FAIL remains valid, but its prior aggregate QA is **not a valid substitute for required role reviews**. Sample V3 must re-enter through the formal VISUAL_PREVIEW work-order path.

## Management-level lesson

The studio needs two separate control planes:

1. **Project / macro control** — objective, stage, dependencies, budget, benchmark, current risk, next irreversible decision.
2. **Shot / micro control** — shot contract, references, endpoints, engine, version, reviewer receipts, repair history.

The Executive Producer must manage both planes and must never confuse "the system has a rule" with "the rule was executed and evidenced".
