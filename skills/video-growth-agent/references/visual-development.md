# Visual Development and Shot Prototyping

Use this reference before expensive visual production. Its purpose is to turn an idea into approved production assets and proven shot language before the team spends effort on a full cut.

## 1. Proactive discovery is part of production
The user is not responsible for supplying the team with every useful tool, workflow or benchmark. During active production, the studio should proactively refresh the relevant landscape when the current quality bar is not met or a new capability could materially improve the work.

Inspect, where relevant:
- strong finished work in the same format;
- studio/creator production breakdowns;
- official model Skills and prompt guides;
- open-source pipelines and source code;
- current community workflows and failure reports.

Do not collect tools for novelty. Extract production principles, test them in a small sample, and only persist what survives review.

## 2. Separate exploration from the production line
Use a dual-track model:

- **Exploration track** — fast experiments, alternate visual directions, model tests, prompt variants, reference studies and risky ideas. Outputs are disposable until promoted.
- **Production track** — only approved references, shots and assets enter the authoritative project state.

A promising sandbox result does not silently become production truth. Promotion requires an explicit artifact version/digest and review.

This keeps experimentation cheap without contaminating the main pipeline with half-approved decisions.

## 3. Build reference assets before generating motion
Before full video generation, establish the references that later shots must inherit. Depending on the project, this can include:
- style / world bible;
- approved character or product references;
- recurring environment/location references;
- material, lighting and palette references;
- hero keyframes;
- first/last-frame anchors;
- camera/lens/composition rules;
- typography and graphic-language rules.

Treat these as **reference contracts**, not inspiration boards. For every important reference record:
- what the reference controls;
- which attributes must remain stable;
- which attributes may vary;
- which shots depend on it;
- the current approved artifact/version/digest.

When a reference changes materially, invalidate dependent approvals rather than relying on memory.

## 4. Route each shot to the engine that has the highest quality ceiling
Do not force one renderer to make the whole film.

Default routing guidance:

### Real interfaces / real products / factual screens
Prefer real screen capture, authorized/public product footage or faithful compositing. Do not generate fake UI when the real interface is the evidence.

### Cinematic people, locations, physical action, camera movement
Prefer a video-generation engine with reference/keyframe control. Where available, use image-to-video, first-frame, first+last-frame or full-reference modes so motion is constrained by approved visual anchors.

### Abstract mechanisms, data, typography, diagrams, UI-like explanatory layers
Prefer code motion / SVG / Manim / Remotion / compositing because deterministic layout and timing matter more than generative texture.

### Continuity-critical transitions
Prefer first+last frame, reference-video or context-continuation approaches. Explicitly define the observable path between states rather than asking a model for a vague "cinematic transition".

### Mixed shots
Hybrid compositing is the default professional answer: generated plate + deterministic graphics + real text/UI + sound design. Do not treat purity of engine as a quality goal.

## 5. Sample-first production rule
Do not build the whole video to discover whether the visual language works.

For quality-critical projects use this progression:

1. **Hero Frames** — at least hook, mechanism/reveal and payoff/end-state at near-final quality.
2. **Highest-risk Shot Probe** — choose the shot most likely to expose the visual system's weakness and make a real 4–8 second sample with representative sound.
3. **Second probe only if it tests a different failure mode** — e.g. human performance vs abstract mechanism, or continuity vs typography.
4. **Full production** — only after the probes pass the external benchmark and account release bar.

A shot probe is not a moving storyboard. It should use the intended production asset type and intended motion engine closely enough to reveal the real ceiling.

If the sample fails, fix the art direction, reference assets, engine or shot design first. Do not compensate by adding more shots.

## 6. Generate takes, then edit
Professional output should not depend on one generation being perfect.

For important generative shots:
- generate a small set of deliberate takes/variations when cost permits;
- vary one meaningful factor at a time (performance, camera, timing, motion path, not random everything);
- compare against the shot contract;
- select the strongest usable span, not necessarily the whole take;
- preserve rejected-take reasons when they teach a reusable lesson.

Editing is a creative selection layer, not merely assembly. A stronger cut assembled from the best portions of several takes is preferable to forcing one mediocre take to survive because it was expensive.

## 7. Prompt the full audiovisual shot, not just the picture
When using capable video models, describe the shot as a timed audiovisual event:
- composition and subject state;
- environment and lighting;
- observable actions/state changes;
- camera movement (type, amplitude, speed where relevant);
- keyframe/reference alignment;
- diegetic sound and physical SFX;
- dialogue/voice when applicable;
- non-diegetic music only when useful.

Prefer concrete observable details over adjectives such as "cinematic", "premium" or "beautiful".

For first/last-frame generation, explicitly describe the continuous path from the starting state to the ending state. For full-reference generation, track stable reference labels/roles so identity, environment, motion and audio sources do not drift silently.

## 8. Continuity lives above the generation model
A generator is a replaceable production engine. The project must preserve continuity independently through approved references, shot contracts, production memory and revision history.

When a better model appears, replace the engine without throwing away:
- script intent;
- shot list;
- world/character/product references;
- approved visual rules;
- previous revisions and rejection evidence.

## 9. Lessons distilled from external systems (2026-10 active scan)
The following systems informed this reference; the studio borrows principles, not protected creative assets or proprietary implementation:

- **DramaClaw** — dual-track main pipeline + infinite-canvas exploration, promotable assets, first-frame/storyboard discipline, identity/scene libraries, model-neutral routing, checkpointed production.
- **Toonflow** — decision/execution/supervision separation, ScriptAgent → ProductionAgent handoff, externalized Skill prompts, persistent structured asset graph, derivative asset identities.
- **MiniMax H3 official Skill** — explicit T2VA/I2VA/FL2VA/L2VA/Ref2VA modes, first/last-frame alignment, concrete camera motion grammar, integrated visual+audio timeline, reference-label retention analysis.
- **Utopai PAI** — production memory, approved character/world references, shot-level revision without discarding the project, review before paid render, multiple takes followed by editorial selection.
- **Pippit Nest** — useful example of delegating model routing/storyboarding to a specialized creative backend; treat it as an optional engine, not the studio's source of creative truth.
- **Current H3 community workflows** — long-form continuity benefits from explicit context frames/latents, color matching at seams, split low/high-resolution sampling, and separating generation from final editorial assembly.

These are evidence sources for method design, not mandatory dependencies.