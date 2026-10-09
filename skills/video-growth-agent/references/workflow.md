# Workflow Semantics

Machine-readable stage order and contracts live in `config/workflow.json`.

## Stage intent
- INTAKE: define task, constraints, platform, target viewer and evidence requirements; output `brief`.
- POSITIONING: confirm the topic strengthens the account's long-term commercial identity; output `positioning`.
- RESEARCH: collect enough evidence to understand the mechanism, not merely restate headlines; output `research_package`.
- RESEARCH_AUDIT: independently attack evidence quality and overclaiming.
- SCRIPT: create hook, narrative spine and payoff; output `script`.
- SCRIPT_AUDIT: test comprehension, retention and factual wording.
- STORYBOARD: convert claims into shots with explicit visual jobs; output `storyboard`.
- VISUAL_PREVIEW: render a short/high-risk sample before expensive full production; output `visual_preview`.
- ASSET_BUILD: build/gather approved assets and record rights/provenance; output `asset_manifest`.
- ROUGH_CUT: assemble timing and remove dead weight; output `rough_cut`.
- SOUND: design voice/music/SFX/silence as a coordinated layer; output `sound_mix`.
- TECH_QA: probe the real final candidate, record a hard-pass QA receipt and output `technical_qa`.
- AUDIENCE_QA: cold-viewer review after the actual cut exists.
- BRAND_QA: judge whether the work strengthens advertiser-facing identity.
- RED_TEAM: produce the strongest case against publishing; PASS requires at least three explicit objections/findings.
- RELEASE: requires final media reference + publish pack and deterministic machine guards.
- PERFORMANCE: capture real platform evidence after publication.
- LEARN: decide what becomes reusable knowledge, what remains local and what should be rejected.
- COMPLETE: durable project package exists.

## Three-part gate
Each stage has required artifacts, required role sign-offs and optional machine guards. Missing any one blocks progression.

## Downstream invalidation
Material changes to a stage invalidate all approvals at that stage and downstream. Examples: changing the thesis invalidates positioning/research/script onward; changing the script invalidates script approvals and downstream; replacing a final candidate after TECH_QA invalidates technical and later approval.
