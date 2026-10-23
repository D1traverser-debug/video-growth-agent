# AI Video Prompt Director — source-first production craft

**Purpose:** a small, testable method for designing and comparing short-film prompts. Not another Agent, task hierarchy, approvals system, or parallel Video governor. The user explicitly prioritizes excellent *director-ready prompts* over business process expansion. All paid rendering remains outside this module.

## Inputs are not already-processed prompting folklore

Study in this order:
1. **Original human intent or full original script/reference footage.** Keep exact wording, distinguish verbatim source spans from derived events. A quoted creator prompt is a *secondary copy*, not proof of original authorship. Preserve context, exact story beats and requested pacing; infer only separately labeled ideas.
2. **First-party professional practice.** Director story/behavior first; cinematography derives framing, lens, light and blocking from the dramatic action; editor plans motivation, eye trace, cut direction, match-action/shape/audio; sound designer specifies physical events versus score. Avoid defaulting every creator to neon finance UI or cyberpunk.
3. **First-party provider skill/API.** MiniMax official [H3 skill](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing), specifically `references/base-en.txt` and `ref-en.txt`. H3 API [source](https://platform.minimax.io/docs/api-reference/video-generation-v2-create) specifies T2VA vs first/last/Ref2VA roles, legal 4–15s integer duration, native 24fps, native audio and optional 2K. PixVerse [V6 source](https://docs.pixverse.ai/PixVerse-V6-User-Guide-3373e99bf35080dfa9d8c44f30fde3bc) permits 1–15s and 5,000 characters. **Do not substitute third-party resellers' distinct API quirks for official vendor behavior.**
4. **Real generated footage and operator feedback** with original prompt, actual model (base/fast variants distinguished), input frame/reference, UI version, duration, aspect, resolution and optional seed/credits. An unsupported generic “great” score is not a calibrated quality observation.
5. **Editorial interchange** follows existing `timeline.py` / `editorial_interchange.py`. [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) is an optional future interchange adapter, not the canonical media graph.

## Visual reasoning sequence (derive, don't pick style up front)

- **Audience and intent:** one-sentence “what should be understood/felt in the final frame?”
- **Narrative causality:** required beats, physical trigger, visible consequence, reaction, payoff. An event tag in a JSON plan only proves *planned* retention, never perceived meaning.
- **Competing treatments:** minimum two materially different concepts with their failure modes. E.g. physical match-cut montage vs dense sci-fi screen reveal, or ribbon-caused teleport cut vs continuous long take.
- **Look development:** choose appropriate style *after* narrative (traditional painterly 3A, realistic film, comic, space opera, stop-motion, etc.); anchor palette, materials, skin/fur, light motivation, production design.
- **Shot planning:** half-open integer edit frames; composition, subject space, action start/trigger/finish, camera framing/focal length/single move/intent, lighting source/angle/reaction, transition bridge, cue events, continuity. Lens numbers must change framing or perspective, not serve as decorative words.
- **Cross-department review:** director (causality), cinematographer (readable blocking), art director (anchors), animator/VFX (physical dynamics), editor (transition match frames), sound designer (sync stems), producer (cost), QA (actual replay).
- **Model-specific emitters:** retain a successful user-tested Chinese dense-timestamp prompt as default for H3 while also generating the official first-party three-field variant. **No fabricated winner.**
- **Independent outcomes:** structural tests -> actual H3/PixVerse renders -> blind review and rewatch -> score/rank -> save artifact refs and recurring failure patterns -> promote technique only after varied prompts and titles pass.

## The two H3 prompt dialects are deliberate controlled variables

**Chinese complete storyboard (default `--h3-style chinese`)**: the user specifically reports very good H3/Hailuo results from a detailed Chinese 10s timecoded romantic scene prompt. This is direct user experience but without supplied rendered file/seed/parameter logs, so it is **USER_REPORTED_POSITIVE, unblinded and not yet reproducible**. Preserve that style and compare instead of replacing it blindly.

**Official `--h3-style official`**: MiniMax H3 `h3-prompt-writing` base T2VA structure:
```text
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:01.500, ...
overall_soundscape: ...
non_diegetic_music: ...
```
Use the official English descriptions as the *target for model-authored rewriting*, preserve spoken/visible words verbatim. The code emitter currently preserves source wording (may remain Chinese in English-labelled fields); it is not a learned translation model. Any claim of native English compliance requires an explicit rewrite/review step.

The user reports PixVerse results as poor, but it is not a controlled head-to-head test against H3 because the model, prompting style and perhaps other conditions changed. PixVerse stays an opt-in baseline and must not be default authority.

## Route choice is a hypothesis, not a religion

- **H3 one-pass** (5s original IP or 10s complete storyline): zero unnecessary trim, multi-shot syntax, native sound; useful initial baseline especially given positive user feedback.
- **H3 shotwise** (tight/critical individual shots): finer local regeneration but native clips have a **4s minimum**. Six 1.6s edited shots in a 10s film become 24s of generated footage; trim and asset continuity costs are real. Do not blindly choose this just because it contains more commands.
- **PixVerse one-pass/shotwise**: official V6 1s minimum, but this user's qualitative outcome is negative so it is lower priority until comparison shows a specific advantage.
- **Reference/keyframe-based H3** can improve identity/pose constraints *in principle*; deliberately blocked by current code until actual reference files, rights, roles and first/last mapping are validated. Do not fake `<Picture 1>` without material inputs.
- **Heavy frame-accurate transitions**: rendered clip -> NLE match cut. Adobe [match-cut reference](https://www.adobe.com/creativecloud/video/discover/match-cut.html) separates graphic, action and auditory matching; strict visual geometry requires real edit verification.

## Rejected visual prompt converted into a reusable rule

The former `CONCEPT_GENERATION_PROMPT_V1.md` (source provenance retained in the integrated project's retired-document records) was explicitly **rejected** after its rendered blue-hair/techwear character became a generic game-ad male. The independent project-local failure audit and active `DESIGN_RESEARCH_METHOD_V2.md` explain why: elaborate eyelid asymmetry, decorative stitching, small icons, accessory easter eggs and extra adjectives were specified **before** the actor's silhouette, facial masses, body volume, costume mass, and narrative behavior were established.

**Transferable film-direction rule:** test primary figure silhouette at thumbnail scale, face mass/expressive direction without the signature colors, and costume as a single large shape **before** microtexture or CG surface effects. For each signature motif, demand a visible impact on blocking, silhouette or motion, not a hidden explanatory label. The prompt is rejected if a different generic digital actor could fulfil it unchanged. Convert failure into a concise counterexample in the prompt-comparison notes; do not resurrect the entire rejected character recipe as active source truth.

## Pre-registered H3 prompt experiment (reuse, not another controller)

For a directly copyable H3 Chinese prompt without a JSON envelope, run `vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route onepass --plain`. The output is candidate text only; source fidelity and media quality still require human review.

Run `vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --study-h3-dialects`. The CLI now returns one `ExperimentPlan` from the **existing** `video_growth_agent.experiments` module, two immutably fingerprinted generated prompts and explicit fixed variables (storyboard, duration, aspect ratio, model, source digest). No render is triggered and no winner exists.

The single varied factor is a **bundle called prompt_rendering_policy**. It changes natural language *and* document structure, so any future difference cannot be causally attributed to language or structure alone. First compare paired H3 outputs under identical UI/model parameters, then repeat on the distinct 5s IP fixture. Record actual clips, operator spend, blind story comprehension, identity continuity, physical interaction failures and independently observable frame evidence before promoting any default. To isolate language or structure, authorize an additional factorial experiment.

### Cleaned historical authority

The obsolete interrupted 0.7→0.8 recovery checkpoint was retired after production 0.8 had already been merged and proven; canonical 0.8 closure retains its blob provenance, while `EVOLUTION_INDEX.json` no longer links a false active-resume instruction. Historical audits with unique fault reproduction remain retained, because removing them would destroy evidence that tests by themselves do not preserve. The rejected V1 aesthetic prompt and wrong-image H1 pass were deleted previously, with causality converted into active design rules and exact Git tombstones.

## Falsification & gates

`vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route compare --h3-style chinese`

`vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route compare --h3-style official`

`vga direct-prompts tests/fixtures/prompt_ip_5s.json --route compare`

Static proof checks: exact frame union, monotonic cut times, source-excerpt literal coverage, unique alternatives, main camera move, valid sound cue placement, provider duration bounds, output length. **Not proven**: original full text was exhaustively imported; narrative semantics were read by actual viewers; the model followed camera/scene; video audio sync; visual quality; superiority of H3 over PixVerse.

Blind QA requires at least independent viewer(s) who did not see the intended prompt and judge whether they can accurately describe the story; annotated timecodes for each missing or bad event; physical plausibility; recognizability of main IP; continuity; perceived motion; soundtrack; editing rhythm. Report **inconclusive** rather than assert artistic PASS from programmatic contract alone.

## Scope rule

This skill is limited to prompt direction. Do **not** bring the financial claim evidence, monetization, release gates or unrelated MediaGraph refactoring into simple prompt creation, and do not delete their existing code simply because this project currently prioritizes prompts. A separately evidenced migration plan is required before destructive change.
