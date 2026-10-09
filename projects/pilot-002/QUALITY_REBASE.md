# Pilot 002 — Quality Rebase

Status: ACTIVE / LOOKDEV  
Prior Release V4: **REJECTED BY USER FOR INSUFFICIENT QUALITY**  
Rule: do not publish V4 and do not reuse its RELEASE approvals.

## Why V4 failed despite passing internal gates

The failure was not encoding, facts, duration or audio loudness. Those were technically sound. The visible problem was a **craft ceiling**:

- too much of the image language still read as designed UI / motion-graphics abstraction rather than production-grade moving imagery;
- the visual world did not have enough asset richness, physical specificity, cinematography or memorable hero action;
- code/CSS motion was asked to carry too much of the aesthetic burden;
- the pipeline spent too much effort proving technical correctness after the core look was already below the desired bar;
- our visual preview did not force a fragment that genuinely represented final advertiser-facing quality.

Therefore V4 remains evidence and a rejected benchmark, not release authority.

## External learning distilled before rebuild

Sources being inspected include DramaClaw, Toonflow, Pippit Nest, MiniMax H3 Skill/docs, Utopai PAI, BigBanana AI Director, ComfyUI+H3 workflows and independently sourced professional previz / AI-filmmaking breakdowns.

Current candidate lessons:

1. **Script → assets/references → keyframes → motion**, not prompt → full video.
2. Lock reusable visual references before asking motion models to invent continuity.
3. Use first/last-frame control when a shot must land on a precise result.
4. Define a multimodal shot contract: composition, subject/object state, action, camera, timing, sound, reference roles.
5. Route each shot to the cheapest engine that can meet its hardest requirement; do not force one engine across the whole video.
6. Keep exploration variants separate from approved production assets.
7. Repair failed shots locally; do not restart approved context.
8. Judge model/tool economics by **accepted seconds**, not generated seconds.
9. A real sample reel must exist before a full build.

These remain candidates until our own sample passes.

## Rebuild strategy

Do not immediately remake the 59.5-second film. Build a **5–12 second near-final sample** first.

### Sample objective
Prove that the account can move beyond SaaS/PPT/code-demo aesthetics into advertiser-facing production craft while still explaining a mechanism clearly.

### Sample must test
- one immediate first-2-second hero image/action;
- one transition from familiar foreground behavior into a deeper mechanism/world;
- visibly richer assets/material/light/depth than V4;
- non-trivial camera movement or spatial change, not just scale/pan of flat cards;
- deliberate sound hit / ambience / silence relationship;
- typography that supports rather than dominates the shot;
- at least one shot whose start/end state can be explicitly controlled with keyframes or equivalent anchors.

### Engine routing to test
- **Code motion** only for typography/data/precise overlays where it is strongest.
- **Reference/keyframe-driven generative motion** for cinematic spatial shots when accessible within cost constraints.
- **High-quality still/reference assets + camera motion** where generative video adds no meaningful value.
- Preserve the ability to swap H3/other video engines; no vendor becomes architecture.

## PASS condition
The sample is viewed at normal speed beside the approved benchmark pack. It must satisfy the current VISUAL_PREVIEW scorecard, including:

- benchmark parity;
- sample final fidelity;
- advertiser showcase value;
- physical/spatial coherence;
- representative final language;
- picture/sound cohesion.

If any hard dimension is below 4/5, stay in sample iteration. Do not expand to the full film.

## Immediate next action
1. refresh the moving benchmark pack with superior examples;
2. choose one 5–12 second sequence that contains the hardest visual transition;
3. write the multimodal shot contract and reference bindings;
4. build the sample using the best available mixed-engine route;
5. review the actual rendered sample and either reject or promote the winning methods to validated techniques.
