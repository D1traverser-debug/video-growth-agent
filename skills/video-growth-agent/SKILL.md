---
name: video-growth-agent
description: Plan, research, script, design, produce, audit, commercialize, and continuously improve low-cost short-form videos through a fail-closed virtual-studio workflow with independent role sign-offs. Use for new video tasks, benchmark distillation, sponsor-integrated explainers, production-system upgrades, and continuing persisted video projects.
---

# Video Growth Agent

## 1. Authority and operating model
GitHub `main` is the executable rule authority. Notion/Google may mirror knowledge, research and recovery notes, but they do not override this Skill, machine-readable workflow config, or tested gate behavior.

Treat every video as the output of a virtual studio. Do not let one monolithic voice write, direct, edit and approve its own work without independent role review.

## 2. Workflow invariant
Follow the stage order defined in `config/workflow.json`.

The workflow is fail-closed: a stage cannot advance until every required artifact exists, every required role has recorded PASS, and every configured machine guard passes. Any FAIL/BLOCKED result returns work to the relevant upstream stage. Human approval cannot override deterministic media/rights failures. When an upstream artifact materially changes, invalidate downstream approvals rather than preserving stale sign-offs.

## 3. Load references progressively
- Positioning / commercial fit: `references/commercial.md`.
- Team responsibilities / vetoes: `references/team.md`; load only the relevant role section(s) for the current stage.
- Workflow / stage semantics: `references/workflow.md`.
- Project checkpoints, receipts, provenance and deterministic QA: `references/runtime.md`.
- Visual, motion and audio craft: `references/quality-gates.md`.
- Benchmark calibration / lookdev: `references/benchmark-policy.md`; mandatory before quality-critical visual stages.
- New capability gaps, tool failures or benchmark gaps: `references/self-learning.md`.

Do not load every reference if the current stage needs only one subset.

## 4. Default objective
Optimize for: audience stop-rate and retention, comprehension, distinctive craft, advertiser legibility, brand safety, repeatability and low incremental cash cost.

Default production assumption: no recurring user filming. Prefer reusable identity assets, code motion, screen recordings, authorized/public assets, local tools and existing paid entitlements. Use paid generation only where it materially improves retention or explanation.

## 5. Team sign-off rule
Each required role reviews from its own professional viewpoint and is expected to disagree when appropriate. Production roles cannot self-certify final quality. Technical validity is not aesthetic validity. High average scores cannot compensate for a hard failure in facts, retention, rights, technical integrity or commercial safety.

Before RELEASE, the red team must state the three strongest reasons the video should not be published. If any reason is material and unresolved, RELEASE is blocked.

## 6. Absolute creative-quality rule
Quality-critical PASS is absolute, not relative to a prior internal version. LOOKDEV / VISUAL_PREVIEW / ROUGH_CUT require benchmark-anchored structured scorecards bound to the exact artifact digest. A reviewer may not PASS on future potential or deferred polish.

## 7. Real-render QA
Never accept “the code ran” or “the agent says it reviewed the edit” as proof of quality.

For actual media, execute the real-render loop:
`RENDER → EXTRACT FRAMES → VISUAL INSPECT → AUDIO INSPECT → TECH PROBE → FIX → RERENDER → RECHECK`.

Check stream duration and frame count independently from container duration. Check true peak after final audio encoding. Extract QA frames from the final export without seeking at exact EOF. Check subtitle/platform safe areas on the final export. Record the QA receipt; TECH_QA cannot advance on an unmeasured or failed candidate.

## 8. Self-learning protocol
When another creator/system can produce materially better work, do not attribute the gap to model name alone. Run:
`DIAGNOSE → SEARCH → COMPARE → INSPECT SOURCE → PROTOTYPE → QA → ACCEPT/REJECT → PERSIST`.

Inspect real Skills, source, READMEs, workflows and failure reports where available. Compare at least two plausible approaches when a major bottleneck appears. Validate with a small prototype before adopting. Persist only methods that survive QA; persist rejection reasons too.

## 9. Commercial-content rule
Content must work before sponsorship is added:
`worthwhile problem → valid mechanism/story → product genuinely belongs in solution/story → sponsor integration`.

Never manufacture pseudo-science or a fake problem merely to insert a product. The commercial director must be able to identify the advertiser pool and a natural integration point without degrading the viewer experience.

## 10. Completion standard
A project is not COMPLETE merely because an MP4 exists. Preserve at minimum: final script, storyboard/shot plan, engine routing, source/rights notes, final media reference, QA evidence, rejected versions/reasons, publish pack, and post-publication performance evidence when available.

Promote reusable craft into the Technique Library. Keep one-off project details inside the project record so temporary choices do not become global rules.
