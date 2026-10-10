---
name: video-growth-agent
description: Plan, research, script, design, produce, audit, commercialize, and continuously improve low-cost short-form videos through a fail-closed agentic-studio workflow with isolated specialist work orders and independent review. Use for new video tasks, benchmark distillation, sponsor-integrated explainers, production-system upgrades, and continuing persisted video projects.
---

# Video Growth Agent

## 1. Authority model
GitHub `main` is the executable authority. Runtime machine-readable resources live under `video_growth_agent/data/`; Python implementations live under `video_growth_agent/`; this Skill and its references explain operating semantics. Do not create a second active config authority elsewhere in the repository.

Before material durable production work, perform a **session capability handshake** by reading `continuity/EXECUTION_CAPABILITIES.json` and reconciling it with the tools actually available in the current session. The profile is the owner capability ceiling, not proof that the current executor actually has every declared tool, credential or media modality. Agent profile `tools` fields are capability requests only. A configured role, tool label or prompt is never execution proof.

Preserve the capability assurance taxonomy during routing: `DECLARED_ONLY` means configuration exists but execution is unavailable or unproven; `HARNESS_WIRED` means deterministic/control plumbing exists but does not prove a live executor; `SESSION_EXECUTABLE` means the current owner/session can execute the contract; `CHAT_BRIDGED` is only a degraded ordinary-specialist path through the current chat and is not independent execution; `ATTESTED_ISOLATED` is the ceiling required when blind multimodal independence must be proven. Never promote `CHAT_BRIDGED` evidence into `ATTESTED_ISOLATED` by role-switching inside one context.

Notion, Google Drive, Library and other stores may hold benchmarks, research, large media or recovery mirrors, but they do not override GitHub `main` unless the active task explicitly designates an exact external artifact as business evidence.

## 2. Fail-closed workflow
Follow `video_growth_agent/data/workflow.json` and `video_growth_agent/data/execution-plan.json`.

A governed stage advances only when all required conditions pass:
- required artifacts exist;
- configured work orders complete with valid provenance/evidence;
- every required approval role has an actual review/meta-review PASS;
- configured deterministic machine guards pass;
- any required execution attestation is valid.

Producer completion is not approval. Human/supervisor preference cannot override factual, rights, technical, process or required craft failures. Material upstream changes invalidate stale downstream approvals.

## 3. Agentic studio execution
Use `video_growth_agent/data/agents.json` for ephemeral specialist profiles and `video_growth_agent/studio_agents.py` for work-order execution.

- Executive Producer owns routing, state and arbitration; it does not create craft artifacts or waive hard gates.
- Worker Agents produce versioned artifacts from explicit least-context work orders.
- Reviewer Agents inspect actual artifacts independently from distinct professional loss functions.
- Blind reviewers do not see sibling verdicts before first-wave review.
- Deterministic measurements remain tools, not persona agents.
- Separate maker from approver where self-review risk is material.
- Do not add agents merely to increase role count; add a specialist only for a distinct artifact, loss function, permission boundary or veto.

Agents communicate through artifacts, exact digests, work-order state and immutable receipts, not peer chat. See `references/agent-studio.md`.

## 4. Progressive reference loading
Load only what the current work order needs:
- positioning/commercial fit: `references/commercial.md`
- role responsibilities/vetoes: `references/team.md`
- work-order isolation/evidence: `references/agent-studio.md`
- workflow semantics: `references/workflow.md`
- checkpoint/provenance/media evidence: `references/runtime.md`
- visual/motion/audio quality: `references/quality-gates.md`
- benchmark/lookdev calibration: `references/benchmark-policy.md`
- quality-critical generation governance: `references/generation-governance.md`
- external production methods/rationale: `references/production-intelligence.md`
- capability gaps and system learning: `references/self-learning.md`
- reviewer attestation/trust: `references/reviewer-execution-attestation.md`

Global references must contain portable mechanisms, not active project state. Project-specific failures, decisions and next actions belong under the project record and task continuity state.

## 5. Quality and production objective
Optimize for audience stop-rate and retention, comprehension, distinctive craft, advertiser legibility, brand safety, repeatability and low incremental cash cost.

Quality is a hard floor. Prefer existing entitlements, local/open-source tools, code motion, screen recordings, authorized/public assets and reusable identity assets. Use paid generation only when it materially improves the hardest quality requirement; cheap/free routing may never justify work below the accepted bar.

Quality-critical PASS is absolute, not relative to a rejected internal version. LOOKDEV, VISUAL_PREVIEW and ROUGH_CUT require benchmark-anchored judgment bound to exact artifact bytes/digests. A reviewer may not PASS on future potential or promised polish.

Before expensive full builds, prove the highest-risk assumption with a near-final sample. If the sample fragment itself would not be acceptable to show publicly, the full build is blocked.

## 6. Generation governance
Quality-critical image/video generation is governed work. Do not use a conversational generator call as an unreviewed side channel for promotable project media.

Before generation, create the required generation brief and run the separate pre-generation Art Director, Creative Director and Red Team challenge defined in `references/generation-governance.md`. Inline PASS strings are status only; authorization requires external verified evidence bound to the exact brief digest. A combined specialist label cannot satisfy separate professional authorities.

A structurally valid brief is not production authorization until the owner gateway can resolve the required evidence and bind the eventual provider call/output back to it. Missing gateway/executor capability remains fail-closed.

## 7. Real-render QA
Never accept “code ran”, “file exists” or “agent reviewed it” as final quality proof.

For actual media execute:
`RENDER -> EXTRACT FRAMES -> VISUAL INSPECT -> AUDIO INSPECT -> TECH PROBE -> FIX -> RERENDER -> RECHECK`.

Check actual stream durations/frame count, final encoded audio peaks, black frames, subtitle/platform safe areas and the exact final bytes after transcode/upscale/audio replacement. TECH_QA and RELEASE require current immutable media-QA evidence; stale candidate QA cannot certify changed media.

## 8. Learning and evolution
The studio owns discovery of better methods when quality, capability or evidence is insufficient. Use:
`DIAGNOSE -> SCOUT -> COMPARE -> INSPECT SOURCE -> DISTILL -> PROTOTYPE -> QA -> ACCEPT/REJECT -> PERSIST`.

Classify failures before mutating the global system: local execution, capability/tool gap, quality-standard gap, or systemic architecture gap. Prefer replacing/simplifying weak mechanisms over stacking new roles and prose.

Learning-source admission is default deny. Seeing conversation, browsing results, links, transcripts, examples or side-task material does not authorize durable learning. External material requires explicit learning admission/provenance under `references/self-learning.md`.

Production Methodologist owns method discovery/prototype design; Evolution Engineer proposes the smallest durable change; Red Team attacks it; owner maintenance applies accepted changes, removes superseded mechanisms where dependency-safe, runs regressions/evals and rereads authority before claiming promotion.

## 9. Commercial-content rule
Content must work before sponsorship is added:
`worthwhile problem -> valid mechanism/story -> product genuinely belongs -> sponsor integration`.

Never manufacture pseudo-science or a fake problem to create sponsor fit. Commercial review must identify a plausible advertiser pool and natural integration without degrading viewer value or safety.

## 10. Completion and hygiene
A project is not COMPLETE because an MP4 exists. Preserve required final artifacts, provenance, QA, reviewer/process evidence, publish pack, rejected-version reasons and performance evidence when available.

Promote only generalized verified craft into the Technique Library; keep one-off project choices in the project record. Fully superseded mechanisms that are not needed for recovery, regression or failure-learning should be removed rather than accumulated.

Run `vga system-audit --repo-root .` during system maintenance. Repository CI must run the same hygiene audit plus the full regression suite. A green CI report is evidence, not a branch-protection guarantee; promotion policy must still respect the repository's actual protection/ruleset state.
