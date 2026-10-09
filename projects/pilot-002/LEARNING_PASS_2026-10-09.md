# Pilot 002 — Learning Pass 2026-10-09

Status: PERSISTED / CANDIDATE METHODS ONLY

This pass was triggered because the rejected V4 showed that role count and technical gate coverage did not guarantee advertiser-facing visual quality. The objective is to learn production-control mechanisms, not collect vendor names.

## Sources inspected

- ByteDance Seedance 2.0 official launch / model page
- MiniMax H3 official repository and open-source documentation
- ComfyUI + H3 production-orchestrator/community workflows
- DramaClaw
- Utopai Studios PAI / PAI-Pro
- Tencent WorkRally
- Pippit Nest / pippit-skills
- Vibemotion
- Claude Opus 5.5 code-rendered motion-design workflows
- Narrator AI CLI Skill

## Transferable mechanisms

### 1. Shot object, not chat turn
WorkRally and production-oriented tools treat each shot as a durable object with references, engine configuration, output, status and repair history. Pilot 002 must do the same. A failed visual layer or shot must be repairable without rerunning the whole film.

### 2. Exploration lane and production lane
DramaClaw/PAI-style workflows separate broad exploration from approved production state. Interesting generations remain disposable until promoted. Approved references, keyframes and timing must not drift silently.

### 3. First/last-state control
MiniMax H3 FL2VA and similar frame-constrained modes formalize the idea that important shots should have declared start and end states. For Pilot 002, the foreground desk/app state and the final backend/result state should be locked before asking a video engine to invent the transition.

### 4. Multimodal reference routing
Seedance 2.0 and H3 support image/video/audio reference roles. References must be bound to one declared function: identity/material, composition, camera/motion, rhythm/audio, or endpoint. Do not dump references into a model without role semantics.

### 5. Director / router owns model choice
Pippit Nest and similar routers keep model-selection complexity below the user-facing brief. The studio should route each shot to the cheapest engine that satisfies the hardest requirement; the user should not become a per-shot prompt engineer.

### 6. Deterministic render remains a specialist tool
Recent Opus 5.5 / HTML / Playwright / FFmpeg workflows show that code rendering is strong for exact typography, data, overlays, repeatable camera paths and frame-perfect timing. It should not be the sole source of cinematic material richness. Use it as a deterministic layer around generative or real media.

### 7. Human-visible timeline / project state
Vibemotion and PAI emphasize that AI changes should land in an inspectable project/timeline rather than disappear into a black-box response. Production state needs real artifacts and version history.

### 8. Batch narration / packaging belongs downstream
Narrator AI CLI-style automation is useful for high-volume narration, BGM, templating and assembly after the visual language is validated. It is not a substitute for lookdev or shot quality.

## Pilot 002 routing consequence

Use the deterministic Sample V2 only as timing/spatial previs. The next visual repair should:

1. preserve the 10.22 s timing contract;
2. lock an opening human/work keyframe and an ending backend/result keyframe;
3. route the high-risk transition to Seedance 2.x or MiniMax H3 (or an equivalent engine) using first/last or reference control;
4. keep code-rendered captions/data/precise overlays as a separate compositing layer;
5. review the actual rendered V3 at normal speed against the benchmark pack;
6. only promote a method to the Technique Library after the sample passes every hard VISUAL_PREVIEW dimension.

## Cost rule

No new recurring paid tool should be required merely to test the method. Prefer existing user entitlements, limited free credits, local/open workflows, or per-shot spending only after the keyframe/render plan is approved. Track cost per accepted second, not per generated second.
