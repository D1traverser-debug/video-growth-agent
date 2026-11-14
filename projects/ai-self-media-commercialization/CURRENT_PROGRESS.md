# Current Progress — AI自媒体视频增长、商业化与原创数字IP

Updated: 2026-11-13
Status: ACTIVE_INTEGRATED_PROGRAM
Authority scope: PROGRAM_LOCAL_BUSINESS_AUTHORITY
Program state: PROGRAM_STATE.json
Subtask graph: SUBTASK_GRAPH.json

## Current authority reset

IP Studio OS (IPOS) is the sole creative authority for the user's personal-IP identity, character carrier, avatar, visual canon, voice/performance canon and reusable identity assets. IPOS runs independently and does not require a CAOS runtime/API/session. Video consumes its versioned export; it does not invoke CAOS or recreate the character design locally.

The authoritative IPOS state is R39:
- no approved character carrier, identity anchor, avatar or visual canon;
- G0 PASS;
- G1 cross-carrier/cross-medium research OPEN;
- G2 concept competition NOT_STARTED;
- G3–G9 BLOCKED;
- no video-ready IPOS bundle exists.

The previous Video-local H1/S1+S3/A2 face-shell path is superseded and historical. Its prompts and images must not be resumed, imported, or treated as approved references.

## IPOS-to-Video integration

The IPOS Video Identity Bundle contract (schema 1.0) and deterministic import adapter are merged to Video mainline:
- contract: video_growth_agent/data/ipos_video_identity_bundle.schema.json;
- adapter: video_growth_agent/ip_identity.py;
- integration state: IPOS_INTEGRATION_STATE.json;
- design/authority rules: docs/media_business_os.md and WORKFLOW_INTEGRATION.md.

The adapter validates owner approval, READY_FOR_VIDEO status, G2/G7/G8 PASS, usage rights, provenance, promoted visual references, and continuity rules. It imports exact asset versions/digests into MediaGraph, binds those refs to identity-dependent ShotContracts, supplies continuity snapshots/rules, and fails closed if approval/evidence is missing. New canon versions invalidate only downstream assets that consumed the old version.

Current integration assurance: MERGED_TO_MAIN__CI_VERIFIED (PR #24; merge commit d44ea379f99a96f4a07ae021c35e7f094df7b29a; mainline CI run 43578752266 on commit 2d9b4ea5ab663155eb5ac8ef17b5568eff0d3882 PASS: 193 tests, repository system audit and installed CLI smoke). This verifies the adapter/schema code contract only. Current IPOS bundle state: NO_APPROVED_BUNDLE_AVAILABLE; no character identity or real bundle import is approved.

## Production-system baseline

Media Business OS 0.8.0 remains the last verified production baseline. The IPOS bridge adapter/schema is merged to main and its code contract passed mainline CI; this does not approve an identity bundle or unblock identity-dependent shots. Existing production capabilities remain:
- versioned editorial planning and claim/beat/shot traceability;
- MediaGraph asset identity, immutable versions, evidence, decisions and downstream invalidation;
- ShotContract, generation admission, take promotion and release gates;
- dimension-level continuity;
- operation-specific model routing;
- non-destructive timeline and editor interchange;
- experiments, outcome receipts and learning.

## Current workstream state

- MEDIA_GROWTH: baseline metrics, topic/series hypotheses and packaging research can proceed.
- ORIGINAL_DIGITAL_IP: canon authority is external IPOS; Video waits for a valid export and owns usage/performance evidence only.
- COMMERCIALIZATION: advertiser mapping, sponsor fit, offers, rights and measurement research can proceed.
- PRODUCTION_SYSTEM: continue non-character production, provider benchmarking, deterministic QA and bridge validation.

## Active Program graph

- growth_baseline_and_topic_hypotheses;
- commercial_advertiser_map;
- ipos_identity_bundle_import (waits for external artifact ipos_video_identity_bundle);
- ip_identity_shot_binding_validation (waits for successful import);
- identity-dependent brand assets wait for shot-binding validation.

Only declared dependencies block work. No character canon is required for unrelated topic/audience/commercial/provider research or explicitly non-character video.

## Acceptance and release status

The bridge is not complete merely because files or a PR exist. Required evidence:
1. contract/schema validation;
2. parser and fail-closed tests;
3. exact MediaGraph import and idempotence;
4. canon-version downstream invalidation;
5. ShotContract and continuity binding;
6. non-character work remains unblocked;
7. exact mainline CI passes;
8. post-merge production CI passes before marking production verified.

## Historical archive

The former 2026-10-15 H1 face-shell/A2 work remains in its original files for provenance and audit only. It is superseded by IPOS R39 and is not the current creative task. Pilot 002 remains a separate historical child project; rejected/process-invalid artifacts are not accepted inputs here.

## Parallel production-system candidate — local programmatic graphics

Updated: 2026-11-14 20:04+08:00

A bounded local graphics renderer is under review in PR #33:
- audit: `audits/VIDEO_LOCAL_PROGRAMMATIC_GRAPHICS_RENDERER_2026-11-14.md`;
- implementation: `video_growth_agent/programmatic_graphics.py`;
- CLI: `vga render-graphic REQUEST.json --output candidate.mp4 [--graph MediaGraph.json]`;
- supports title/quote/stat cards and bar charts for explicitly admitted non-character information shots;
- FFmpeg renders a silent MP4; Pillow/FreeType measures the actual selected font so all text is pixel-fitted, and unfit text fails before output;
- source references require exact promoted MediaGraph versions and digest matches;
- optional MediaGraph registration remains CANDIDATE only; no promotion/release authority;
- no paid provider, network call, AI cinematic footage, product-truth or IPOS identity substitution.

PR #33 is OPEN and NOT MERGED. Exact head at this checkpoint: `77a41072c88151a3e78e975cda7ae731b9cc997d` (audit/handoff update after renderer tests). The prior exact head `dba8b105d62ba1708685edc87832736096473b33` passed CI with 246 tests, system audit and installed CLI smoke. Subsequent additions include a long chart-value fit test; exact-head CI and fresh Codex review are pending. Do not call this production-verified or merge until exact-head CI and independent review pass.

The first two Codex findings (literal drawtext expansion; source digest mismatch) are fixed and their review threads resolved. The third finding (long metric clipping) is addressed with pixel-based measurement, adaptive sizing, a receipt layout record and fail-before-output tests; its thread awaits final verification/review.

CAOS and IPOS remain unchanged. IPOS R39 remains the sole identity authority; no approved bundle exists.

### Candidate verification correction — 2026-11-14

The local graphics candidate now also dynamically allocates chart rows from the available vertical region and measures each label/value/bar height against its row. A 640×640 six-row chart with a two-line sixth label is rendered in regression coverage; impossible row layouts fail before output. This closes the fourth Codex finding (vertical label clipping).

Exact code head `c70b8f32e24aa9e79306989f16ebbc46b233745c` passed CI runs `43594450643` and `43594445342`: 249 tests, repository system hygiene audit, and installed CLI smoke. Four Codex review threads are resolved. A fresh full Codex review was requested against that head and is pending. PR #33 remains open and unmerged; do not mark production-ready until fresh review, merge and mainline CI all pass.

### Candidate lineage correction — 2026-11-14

A fifth Codex finding exposed that candidate registration validated the existence of a SHOT context but not its actual Sequence ancestry. The shared `validate_shot_graph_bindings()` now requires the SHOT parent chain to resolve to the exact `ShotContract.sequence_id`, accepting SHOT → SEQUENCE or SHOT → SCENE → SEQUENCE only. CLI preflight and MediaGraph registration both call the same validator. Regression coverage verifies mismatch rejection, registration rejection, valid SCENE intermediary and CLI fail-closed behavior.

Exact renderer code head `df580452c2eca46d9fd0d8b0646527395900e763` passed CI runs `43595226122` and `43595220908`: 252 tests, system hygiene audit and installed CLI smoke. Five Codex inline findings are resolved. A fresh full review was requested; PR #33 remains open/unmerged and not production-authorized pending that review and mainline CI.

### Concurrent-output ownership correction — 2026-11-14

A sixth Codex finding exposed a race: an FFmpeg failure could unlink a destination file created by another concurrent invocation after the initial existence check. The renderer now writes only into an invocation-private temporary directory under the destination filesystem, performs QA there, and publishes with an atomic no-replace hard link. Cleanup removes only the private temporary directory. A competing destination is preserved both on FFmpeg failure and on publication race. The QA receipt now points to the published MP4.

Exact renderer code head `16b2c17cd6ca503cca056be626d4402a547f3899` passed CI runs `43596038209` and `43596033964`: 255 tests, repository system hygiene audit and installed CLI smoke. Six Codex findings are fixed and all six inline threads are resolved. Fresh full code and security reviews have been requested. PR #33 remains open/unmerged and not production-authorized.
