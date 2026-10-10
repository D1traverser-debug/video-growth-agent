# Production Intelligence — Distilled External Methods

## Status and admission boundary
This file stores portable mechanisms distilled from external production systems. It is not a vendor recommendation list and it is not project state.

Some entries predate the current learning-source admission contract. They may remain as **historical rationale** for already-existing candidate techniques, but they must not be treated as fresh authorization for new durable mutations. Any new promotion or material extension must satisfy `self-learning.md`: explicit source admission, provenance, comparison, falsifiable prototype and QA.

Transient conversation material or a merely user-supplied link is not a durable learning source by itself.

## Evidence hierarchy
Prefer:
1. official documentation / first-party source or Skill;
2. first-party production breakdown with visible outputs;
3. credible creator comparison with disclosed process and failure evidence;
4. community reports for failure discovery, never as sole proof.

Distill mechanism, evidence, transfer boundary and falsifiable prototype. A vendor name never becomes architecture by itself.

## DramaClaw — stateful and resumable pipelines
Primary reference: `https://github.com/dramaclaw/dramaclaw`

Portable mechanisms:
- pipeline/status is execution truth; chat history is not;
- init/resume behavior is explicit;
- launched work does not masquerade as completed work;
- current breakpoint and generated artifacts are recoverable;
- specialized references are loaded progressively.

Transfer: keep durable stage truth in project state; resume from exact work breakpoints; separate launch, completion and evidence.

## Toonflow — exploration separated from production
Primary reference: `https://github.com/HBAI-Ltd/Toonflow-app`

Portable mechanisms:
- alternatives coexist without overwriting approved state;
- model/provider choice is replaceable while project context persists;
- node/asset relationships expose dependencies.

Transfer: maintain disposable exploration and governed production lanes; promote only selected artifacts; preserve rejected variants as evidence without letting them mutate approved assets.

## Pippit Nest — coherent creative routing
Primary reference: `https://github.com/Pippit-dev/pippit-skills`

Portable mechanisms:
- one coherent creative brief survives underneath model/tool routing;
- the user is not forced to become a per-shot prompt engineer;
- generation, publishing and analytics form one lifecycle.

Transfer: preserve one authoritative brief, hide unnecessary routing complexity from the user, and route publication evidence back into PERFORMANCE/LEARN.

## MiniMax H3 — reference-aware audiovisual shot contracts
Primary reference: `https://github.com/MiniMax-AI/MiniMax-H3`

Portable mechanisms:
- explicit generation modes encode what is actually anchored;
- first/last frames constrain important endpoint states;
- shot contracts combine composition, action, camera, timing, sound and reference roles;
- references should have declared functions rather than vague influence.

Transfer: lock important endpoints, bind each reference to identity/material/setting/composition/motion/camera/sound, and preserve invariants across revisions. Model-specific syntax remains replaceable.

## Utopai PAI — approval-driven production assistance
Primary references: `https://www.utopaistudios.com/en/pai` and `https://www.utopaistudios.com/en/blog/what-is-pai`

Portable mechanisms:
- story is decomposed into reusable production entities before expensive generation;
- approved references persist;
- camera/staging/keyframe alternatives are compared before more compute;
- paid rendering follows keyframe/render-plan approval;
- failed shots can be repaired without discarding approved context.

Transfer: lock reusable references before expensive motion, revise at shot level, and keep Creative Director authority separate from generation tooling.

## BigBanana AI Director — Script → Asset → Keyframe → Video
Primary reference: `https://github.com/shuyu-labs/BigBanana-AI-Director`

Portable mechanisms:
- assets and keyframes constrain generation before video spend;
- framing grids/contact sheets cheaply compare alternatives;
- shot workbenches preserve narrative/action/context;
- prompt/reference/version history supports upstream diagnosis.

Transfer: build reusable assets only when recurrence justifies them, use cheap candidate framing before final generation, and debug brief/asset/keyframe problems before rerunning a model.

## Distilled candidate techniques
These mechanisms are represented in the executable Technique Library and remain candidates until this studio's own representative sample survives QA:

1. asset-first reference locking;
2. first/last-frame control;
3. audiovisual shot contracts;
4. shot-to-engine routing by hardest requirement;
5. prototype low, finish high;
6. shot-level repair;
7. exploration lane → production lane;
8. accepted-seconds economics.

The executable Technique Library at `video_growth_agent/data/techniques.json` is the runtime source. This document is rationale/reference material, not a second technique registry.
