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

## Three-part gate
Each stage has required artifacts, required professional sign-offs and optional deterministic machine guards. Missing any required class blocks progression. Work-order/process proof is enforced separately by the base Runtime for every stage that declares execution-plan tasks.

## Downstream invalidation
Material upstream changes invalidate stale downstream approvals. Changing thesis, script, visual language or final media bytes must not preserve approvals that were bound to prior artifacts.
