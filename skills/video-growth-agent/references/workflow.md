# Workflow Semantics

Machine-readable stage order and gate contracts live in `video_growth_agent/data/workflow.json`. This packaged resource is the runtime authority; do not maintain a second root-level config mirror.

## Stage intent
- INTAKE: define task, constraints, platform, target viewer and evidence requirements; output `brief`.
- POSITIONING: confirm the topic strengthens the account's long-term commercial identity; output `positioning`.
- RESEARCH: collect enough evidence to understand the mechanism, not merely restate headlines; output `research_package`.
- RESEARCH_AUDIT: independently attack evidence quality and overclaiming.
- SCRIPT: create hook, narrative spine and payoff; output `script`.
- SCRIPT_AUDIT: test comprehension, retention and factual wording.
- STORYBOARD: convert claims into shots with explicit visual jobs; output `storyboard`.
- LOOKDEV: calibrate against benchmark pack and prove near-final art direction with `style_bible` + `hero_frames`; no full animation before this passes.
- VISUAL_PREVIEW: render the highest-risk motion sample plus contact sheet; structured benchmark-anchored quality scorecards are mandatory.
- ASSET_BUILD: build/gather approved assets and record rights/provenance; output `asset_manifest`.
- ROUGH_CUT: assemble timing and remove dead weight; output `rough_cut`.
- SOUND: design voice/music/SFX/silence as a coordinated layer; output `sound_mix` and conform `final_candidate`.
- TECH_QA: probe the real final candidate, record a hard-pass QA receipt and output `technical_qa`.
- AUDIENCE_QA: independent audience perspectives followed by configured meta-review.
- BRAND_QA: judge whether the work strengthens advertiser-facing identity.
- RED_TEAM: produce the strongest case against publishing; PASS requires at least three explicit objections/findings.
- RELEASE: requires final media reference + publish pack and deterministic machine guards.
- PERFORMANCE: capture real platform evidence after publication.
- LEARN: decide what becomes reusable knowledge, what remains local and what should be rejected.
- COMPLETE: durable project package exists.

## Story-first commissioning and generation-mode selection (2026-10-24 owner correction)

**User outcome overrides the generator's clip length.** A 60-second film is a 60-second story, not six unrelated 10-second descriptions. The current short-film route MUST execute existing SCRIPT → SCRIPT_AUDIT → STORYBOARD / story-reel review before LOOKDEV or prompts. This is an application of existing stage authority, not a new controller, required review role, magic numeric artistic score or a vendor-specific global standard.

### SCRIPT: content before expensive generation

For an original narrative rather than a transcription, formulate competing *story premises* when real alternatives would improve the brief. Before drafting prompts, give each viable premise an observable opening event, a character with a concrete want and a costly/meaningful choice, a rule/constraint, escalating and causally linked attempts, a genuine reveal/reversal, a consequence and a final image that changes the meaning of the opening. A sacrifice/death/resurrection shortcut with no earned character desire or meaningful consequence should not pass by default. Separate **theme** (what the story expresses) from **plot** (what visibly happens). Preserve required platform, aspect, duration, cost and rights/truth rules; don't invent user preferences such as a mandatory moral, robot protagonist or 3D style.

### SCRIPT_AUDIT: human-understandable narrative gate

Test comprehension and dramatic necessity *before* converting script to model jargon:
- Explain the full film in a 1–2 sentence logline and a causal paragraph; viewers should be able to infer want, obstacle, changed belief/choice and payoff from visible/audible beats.
- Identify weak stakes, predictable or consequence-free twists, unexplained mechanics, coincidence and redundant beats; **rewrite** rather than padding with camera adjectives.
- Stress-test with still-storyboard/animatic: remove unnecessary captions/dialogue and confirm causal comprehension with cold viewers when available. Simulated AI role feedback is a candidate critique, not proof of independent human reception.
- The reviewer reports `STORY_REVISION_REQUIRED` or `STORY_READY_FOR_STORYBOARD` with specific reasons, not an invented numeric PASS score. Neither a quoted-source coverage check nor a prompt compiler is an artistic acceptance gate.

Pixar's primary teaching materials cover wants/needs, obstacles, character arc, stakes, story spine, visual language, film grammar, and iterative storyboard-pitch-feedback/storyreels: https://www.khanacademy.org/computing/pixar/storytelling and https://www.khanacademy.org/partners/pixar.

### STORYBOARD: author the 60-second timeline before chunking it

Allocate beats by what viewers need to understand and feel; do not preallocate six 10-second 'chapters' merely because a provider can output 10-second clips. Specify for each beat: dramatic question, new information, motivation/choice, shot scale, spatial relationship, character/prop state, sound, intended edit point, and explicit continuity reference. Build a silent still storyboard or rough timed animatic first. A cinematic 60-second film may need 10–20 short editing shots even if the render service uses 6–10 generator jobs. Generate handles/alternates when feasible; six accepted 10-second clips is a minimum, not a guarantee of usable 60-second runtime.

### Shot-by-shot mode selection using available UI and current model evidence

For the *specific* user screenshot from 2026-10-24 the selected tab is `文生视频`, the visible four tabs are `文生视频 / 图生视频 / 首尾帧 / 参考图生视频`, and selected constraints are **H3 / 720p / 10 seconds / 16:9 / generate audio on**. Locked 1080p/15s/30s/60s controls and displayed 'free' flag are local UI observations, NOT an official API price, model-wide technical constraint, or verified capability in the other tabs. Each switched tab must be checked for model/settings/availability before advising a real generation.

Mode advice, not a rigid universal rule:
- Text-to-video (T2VA): initial independent atmosphere, no exact known character/frame dependency, quick concept exploration. Weak choice for recurrent-character continuity.
- First-frame I2VA (`图生视频`): an approved exact 16:9 character/scene composition is the start; image anchors identity and layout, text directs motion. Obtain that keyframe by **text-to-image → image review/adjustment → image-to-video** when no approved art exists. Text-to-image is an upstream workflow step, not a fifth video tab.
- First-to-last FL2VA (`首尾帧`): beginning AND ending compositions are known and reachable by a plausible continuous action or controlled environmental transformation. Describe the physical intermediate motion; avoid implausible morphing or requiring arbitrary hard scene changes between distant pictures.
- Reference mode Ref2VA (`参考图生视频` UI): use approved identity/style/prop/environment reference images when precise starting frame is unnecessary; H3 API can additionally accept video/audio references where **that actual UI** exposes them. Do not promise that reference images can be simultaneously attached to first/last frames; some hosts make these alternate input modes.
- Clip-to-clip continuation: use a validated preceding endpoint as the next start **only for a continuous action**. For a deliberate cinematic cut, author a separate new shot keyframe using the same approved style/character bible instead of mechanically reusing the last frame. Cross-shot matching requires review of silhouette, wardrobe, color, geometry, scene layout and prop states regardless of mode.

MiniMax primary sources: https://platform.minimax.io/docs/guides/video-generation ; https://www.minimax.io/news/minimax-h3-open-source ; https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md . H3 modes are genuinely distinct; first/last references encode timestamp anchoring, not universal appearance protection. See `prompt-direction.md` and `craft-source-studies.md` for the existing prompt/craft owners. Vendor-native syntax belongs *after* the selected story/mode is approved.

### VIDEO QA: story as seen by audience, not as intended in text

Review the **actual playable result** and compare against story-reel rather than congratulating a beautiful still: can a cold viewer infer motivation, turning point and payoff without reading the source? Record timecoded evidence for drift, physical-action coherence, false continuity, pacing, sound and bad reveal; map each to the owned shot, generation reference and candidate repair. Technical FFmpeg PASS, role-completion receipt, or a model producing 10 seconds does not certify a good story. Evaluate revised actual videos and preserve failed takes; record only scoped learning from matched outcomes.

## Three-part gate
Each stage has required artifacts, required professional sign-offs and optional deterministic machine guards. Missing any required class blocks progression. Work-order/process proof is enforced separately by the base Runtime for every stage that declares execution-plan tasks.

## Downstream invalidation
Material upstream changes invalidate stale downstream approvals. Changing thesis, script, visual language or final media bytes must not preserve approvals that were bound to prior artifacts.
