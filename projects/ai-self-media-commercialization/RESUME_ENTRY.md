# Resume Entry — AI自媒体视频增长、商业化与原创数字IP

Status: ACTIVE_INTEGRATED_MEDIA_BUSINESS_PROGRAM
Owner: DOMAIN:video
Program ID: ai-self-media-commercialization

## Canonical resume phrases

- AI自媒体视频商业化
- AI视频涨粉与商业化
- 原创数字IP
- 原创数字IP设计
- ai-self-media-commercialization

## Current authority model

IP Studio OS (IPOS) is the sole creative authority for the user's personal-IP identity, character carrier, avatar, visual canon, voice/performance canon and reusable identity assets. IPOS is an independent system: it completes its own research, strategy, character design, prompt compilation, authorized rendering, QA, correction, versioning and export. It does not need to invoke CAOS or depend on a CAOS runtime/API/session.

The Video system is a downstream production consumer and evidence contributor. It does not create a competing character bible, revive a video-local face design, or rewrite IPOS canon. The interface is the portable IPOS Video Identity Bundle (schema 1.0), imported locally by video_growth_agent.ip_identity into MediaGraph and bound to ShotContract and continuity.

## Current IPOS truth — R39

Canonical sources:
- IPOS private Library: /个人ip创作/头像工作室/CURRENT_STATE.json
- IPOS private Library: /个人ip创作/头像工作室/TASK_ASSIGNMENT_CURRENT.md
- Video-side mirror of integration status: IPOS_INTEGRATION_STATE.json

Current state:
- No approved character carrier, identity anchor, avatar, visual canon or video-ready bundle exists.
- G0 PASS; G1 cross-carrier/cross-medium research OPEN; G2 NOT_STARTED; G3–G9 BLOCKED.
- No character-identity shot may bypass the IPOS approval contract.
- The previous Video-local H1/S1+S3/A2 face-shell route is historical and superseded. Do not resume it, import it, use its prompts, or treat its assets as references.

## Current Video integration state

- Contract: video_growth_agent/data/ipos_video_identity_bundle.schema.json, schema_version 1.0.
- Adapter: video_growth_agent/ip_identity.py.
- Runtime targets: MediaGraph immutable asset import, ShotContract reference binding, continuity rules/snapshots, and fail-closed generation admission.
- Version changes invalidate only downstream assets/tasks that consumed the superseded IPOS asset version.
- Current bundle state: NO_APPROVED_BUNDLE_AVAILABLE.
- Merged to main via PR #24 (merge commit d44ea379f99a96f4a07ae021c35e7f094df7b29a). Mainline CI run 43578752266 (#1520) on commit 2d9b4ea5ab663155eb5ac8ef17b5568eff0d3882 passed: 193 tests, repository system audit and installed CLI smoke. This verifies code/contract only; no approved IPOS bundle exists.

## Required entry order

1. projects/PROJECT_INDEX.json
2. projects/ai-self-media-commercialization/PROJECT_MANIFEST.json
3. projects/ai-self-media-commercialization/PROGRAM_STATE.json
4. projects/ai-self-media-commercialization/SUBTASK_GRAPH.json
5. projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json
6. projects/ai-self-media-commercialization/IPOS_INTEGRATION_STATE.json
7. projects/ai-self-media-commercialization/CURRENT_PROGRESS.md
8. docs/media_business_os.md
9. Only the action-specific workstream and production files needed next.

## Current next actions

1. Continue IPOS R39 G1 research. When an owner-approved READY_FOR_VIDEO bundle arrives, run deterministic import and shot-binding acceptance; do not report identity approval before bundle evidence exists.
2. Continue growth baseline/topic work and advertiser mapping in parallel.
3. Keep identity-dependent shots waiting until IPOS exports an owner-approved READY_FOR_VIDEO bundle with G2/G7/G8 PASS, rights, provenance and exact promoted visual assets.
4. On bundle arrival, validate, import, bind exact refs, and record the import receipt. Never auto-approve the identity.
5. When IPOS emits a newer canon version, stale only descendants that consumed the old version; preserve unrelated work.

## Program invariants

- Workstreams progress independently unless SUBTASK_GRAPH declares a dependency.
- IPOS owns identity canon; Video owns shot usage, production, continuity assessment, media lineage, release and outcome evidence.
- Performance signals may create an IPOS learning candidate but never directly mutate canon.
- No CAOS runtime/API call is required for IPOS execution or the IPOS-to-Video handoff.
- Candidate generation, promotion and release remain separate gates.
- A document, prompt, image file or successful tool call is not proof of approval.

## Historical records

The former H1/S1+S3/A2 face-shell work, its research and prompts remain in the repository for audit/history only. They are not active instructions or valid canon references. Pilot 001/002 remain separate historical child projects.

## Parallel non-character short-form editorial work

EDITORIAL_PACKAGING.md defines source-and-visual semantic QA; cases/jensen-alice-20261114.json contains seven editorial candidates. Run vga audit-packaging on the case before any human review. The episode has no current video bytes/digest, rights readback, EditorialPlan/master-timeline binding, actual platform-disclosure receipt or independent human semantic acceptance. These are OPEN and must not be represented as a production-ready or published episode. This parallel task does not change the IPOS owner approval gate.

## Parallel Video production candidate — local graphics renderer (2026-11-14)

Read `audits/VIDEO_LOCAL_PROGRAMMATIC_GRAPHICS_RENDERER_2026-11-14.md` before continuing this task.

PR #33 is OPEN and NOT MERGED. It adds a local FFmpeg route for non-character title/quote/stat cards and bar charts, with Pillow-based pixel measurement for all text. The route requires explicit ShotContract permission, editorial/beat/source-claim binding, synthetic truth mode and disclosure. Optional MediaGraph registration requires exact promoted source versions with matching digests and keeps the output CANDIDATE only. It is silent; no AI footage/audio, product-truth, IPOS identity, promotion or release.

Last known fully green exact head before the latest chart-value test/audit handoff was `dba8b105d62ba1708685edc87832736096473b33` (246 tests, system audit and installed CLI smoke). Latest branch head has moved; rerun/read exact-head CI before merge. The first two Codex threads are resolved; the metric-clipping thread has a documented fix and needs final exact-head verification plus fresh Codex review. Do not state PR #33 is merged or production-ready.

CAOS source and IPOS repository/state must remain untouched.

### Local graphics renderer — latest verification (2026-11-14)

The candidate now fixes both horizontal and vertical text clipping. Chart rows are allocated dynamically, each row's label/value/bar geometry is measured and checked, and a 640×640 six-row chart with a two-line final label is covered by a real FFmpeg regression test. An impossible row layout fails before rendering.

Verified code head: `c70b8f32e24aa9e79306989f16ebbc46b233745c`. Exact-head CI runs `43594450643` and `43594445342` passed: 249 tests, system audit and installed CLI smoke. All four inline Codex threads are resolved; a fresh full Codex review is requested and pending. PR #33 is still OPEN/NOT MERGED. Read `audits/VIDEO_LOCAL_PROGRAMMATIC_GRAPHICS_RENDERER_2026-11-14.md` before further action. No CAOS/IPOS source or canon changes.
