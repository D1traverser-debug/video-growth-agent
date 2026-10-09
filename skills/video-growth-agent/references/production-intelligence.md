# Production Intelligence — Distilled External Methods

Purpose: convert external tools, studios, Skills and workflows into portable production methods. This is not a vendor recommendation list. A method becomes validated for this studio only after a representative sample survives our own QA.

## Evidence hierarchy

1. official documentation / first-party Skill / source code;
2. first-party production breakdown with visible outputs;
3. credible creator comparison with disclosed process and failures;
4. community discussion used for failure discovery, never as sole proof.

Record the source, the mechanism, what transfers, what does not, and the prototype needed before adoption.

---

## DramaClaw — stateful pipeline and resumable production
Primary evidence: `https://github.com/dramaclaw/dramaclaw`

Observed mechanisms:
- pipeline/status is execution truth; chat history is not;
- init/resume/episode behavior is split into playbooks rather than one giant prompt;
- asynchronous production steps are explicit and do not masquerade as completed work;
- project state and generated artifacts are recoverable at the current breakpoint;
- skills route to progressively loaded references rather than loading the entire system every turn.

Transfer to Video Growth:
- keep business stage truth in project/checkpoint artifacts;
- make production recover from the exact shot/sample/build breakpoint;
- do not claim downstream completion because a task was only launched;
- use small playbook/reference surfaces for specialized production work.

Do not copy:
- DramaClaw's one-write-per-turn interaction constraint is product-specific and should not become a universal video rule.

## Toonflow — exploration canvas separated from production decisions
Primary evidence: `https://github.com/HBAI-Ltd/Toonflow-app`

Observed mechanisms:
- script, characters, scenes, images and video clips coexist on an infinite canvas;
- workflow is node/asset oriented rather than a linear chat transcript;
- model providers and plugins are replaceable; project context survives provider choice;
- the canvas makes alternatives visible side by side instead of overwriting the current production state.

Transfer to Video Growth:
- maintain an **exploration lane** for references, moodboards, variants and engine tests;
- promote only selected artifacts into the **production lane**;
- preserve rejected variants as evidence without allowing them to silently mutate approved production assets;
- visualize shot/asset dependencies when a project becomes too complex for a linear list.

Do not copy:
- an infinite canvas is UI, not quality. It does not replace benchmark review or final media QA.

## Pippit Nest — central creative router, not a collection of manual sub-prompts
Primary evidence: `https://github.com/Pippit-dev/pippit-skills`

Observed mechanisms:
- Nest owns creative interpretation, model choice, storyboarding and workflow routing;
- a creative request stays one coherent task/thread rather than being prematurely fragmented;
- thread continuity is preserved across clarification and refinement;
- generation, publishing and analytics are treated as a connected lifecycle.

Transfer to Video Growth:
- the Producer should preserve one coherent creative brief and route work underneath it;
- avoid making the user act as prompt engineer for every shot;
- keep model-routing complexity behind the studio unless the decision materially affects cost/rights/quality;
- connect published-post evidence back to PERFORMANCE/LEARN rather than ending at export.

Do not copy:
- a black-box router cannot be aesthetic authority; all generated results still pass our benchmark and real-render gates.

## MiniMax H3 — audiovisual shot contract and reference-aware generation
Primary evidence: `https://github.com/MiniMax-AI/MiniMax-H3`

Observed mechanisms:
- distinct T2VA/I2VA/FL2VA/L2VA/Ref2VA modes encode what is actually anchored;
- first/last frames can constrain a shot's beginning/end instead of leaving both to prompt luck;
- prompts describe composition, subjects, environment, actions, camera, exact timing and sound in one contract;
- `overall_soundscape` and `non_diegetic_music` are planned explicitly rather than treated as late decoration;
- reference labels distinguish subjects, concrete frame anchors, structural video references and audio references;
- full-reference mode contains retention analysis: what is fully preserved, partly preserved, transferred or only weakly referenced.

Transfer to Video Growth:
- use first/last-frame or reference-driven control for shots whose destination state matters;
- write a structured audiovisual shot brief before sending a shot to any generative engine;
- bind each reference to one declared function: identity, material, setting, composition, motion, camera or sound;
- include sound intent at shot-design time;
- record what must remain invariant across revisions.

Do not copy:
- H3 syntax is model-specific. Preserve the semantic contract while translating to other engines.

## ComfyUI + H3 — workflow modularity and inspectable generation graphs
Secondary evidence: user-provided Zhihu tutorial `https://zhuanlan.zhihu.com/p/2070647870223655002`

Observed mechanisms:
- video generation is a graph of model + text encoder + VAE + workflow, not one magical model file;
- components can be inspected/replaced independently;
- beginner templates lower setup cost but final quality still depends on shot/camera language;
- local high-end video generation has meaningful VRAM/RAM cost.

Transfer to Video Growth:
- reason about generation as replaceable modules, not brand names;
- keep engine routing explicit enough that a failed component can be swapped;
- do not choose a local model merely because weights are free; compute/time cost counts.

## Utopai PAI — production-assistive, approval-driven filmmaking
Primary evidence: `https://www.utopaistudios.com/en/pai` and `https://www.utopaistudios.com/en/blog/what-is-pai`

Observed mechanisms:
- script is broken into characters, locations, props, scenes and shots before generation;
- approved character/location references persist into later shots;
- teams compare camera/staging/keyframe variations before committing more compute;
- paid render happens after keyframe/render-plan approval;
- one shot can be revised without discarding approved project context;
- project memory includes story, assets, production status and collaborator feedback;
- system is explicitly human-directed rather than autonomous taste authority.

Transfer to Video Growth:
- lock reusable project references before expensive shot generation;
- revise at shot level rather than restarting the film;
- make approved lookdev assets and shot decisions persistent inputs to later work;
- use AI as production assistance while Creative Director retains taste authority.

## BigBanana AI Director — Script → Asset → Keyframe
Primary evidence: `https://github.com/shuyu-labs/BigBanana-AI-Director`

Observed mechanisms:
- rejects slot-machine generation in favor of `Script → Asset → Keyframe → Video`;
- character sheets, wardrobe variants, scene concepts and props are reusable constraints;
- start/end keyframes give tighter motion-state control;
- nine-grid storyboard preview explores angles before expensive full frames;
- shot workbench keeps narrative/action/context visible per shot;
- prompt history and rollback support cross-stage debugging.

Transfer to Video Growth:
- build reusable visual assets only where recurrence justifies them;
- use cheap candidate framing grids / contact sheets before final shot generation;
- store prompt/reference/version provenance for keeper shots;
- diagnose an unstable output upstream (asset/keyframe/brief) before blindly rerunning the model.

## Cross-source production rules accepted as candidates

These are **candidate techniques** until our own sample passes:

1. **Asset-first reference locking** — approve identity/style/product/location references before expensive motion.
2. **First/last-frame control** — define important shot endpoints before asking a model to invent the path.
3. **Audiovisual shot contract** — composition + action + camera + timing + sound + reference roles in one brief.
4. **Shot-to-engine routing** — route by the hardest requirement, not by a favorite model.
5. **Prototype low, finish high** — validate staging/continuity/motion at the cheapest quality that can answer the decision; only upscale/generate final after approval.
6. **Shot-level repair** — regenerate or revise the broken shot while preserving approved context.
7. **Exploration lane → production lane** — variants stay disposable until selected; approved production assets do not silently drift.
8. **Accepted-seconds economics** — evaluate model cost by usable/accepted seconds, not headline price per generated second.

## Current Pilot 002 implication

Release V4 is a rejected quality sample, not an authority to publish. The next build should not start with a full 60-second render.

Before full rebuild:
1. create a fresh benchmark pack using superior moving work, not only stills;
2. lock a more cinematic asset/material system;
3. identify 1–2 highest-risk shots;
4. create a 5–12 second near-final prototype with picture + motion + sound intent;
5. compare side-by-side against the benchmark at normal playback speed;
6. only after PASS route the remaining shots to the cheapest suitable engines.
