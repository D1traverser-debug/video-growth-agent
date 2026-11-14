# CAOS Governance Takeover — Video Growth Agent

Date: 2026-11-14
Status: PROMOTED__MAINLINE_CI_VERIFIED
Video repository: `D1traverser-debug/video-growth-agent`
Base revision: `d44ea379f99a96f4a07ae021c35e7f094df7b29a`
Candidate branch: `migration/caos-video-governance-20261114`
Candidate PR: #25 — merged
Candidate head: `3d4b1d58b7f4f7617949154a2850bede0b478bab`
Mainline commit: `2d9b4ea5ab663155eb5ac8ef17b5568eff0d3882`
Mainline CI: run `43578752266` (#1520) — PASS
CAOS source repository: `D1traverser-debug/cognition-agent-os`
CAOS main revision at verification: `9686cedeb3fd8171ecf70eab33aaea641217b04a` (read-only; no files changed)

## Root cause

The Video repository still declared an active external parent controller in its root manifest and adapter. Its root operating skill, capability profile, coordination policy, product requirements, architecture docs, project-state identity fields and repository audit all depended on that binding. The repository audit explicitly failed if the parent manifest, adapter and capability profile were removed, while a dedicated test required those files to remain. Deleting only the visible directory would therefore leave a broken and internally contradictory Video system.

The capability profile also contained Video-owned production capabilities. Those are domain assets, not parent-controller code, and had to be migrated rather than discarded.

## Decision

CAOS is the external parent cognition/governance layer for Video work in the active ChatGPT session. The Video repository remains the sole authority for its business identities, project state, media graph, assets, editorial decisions, runtime and domain evolution.

The integration is deliberately `CHAT_GOVERNED_EXTERNAL`, with no CAOS runtime/API dependency and no copied CAOS implementation. CAOS source is read-only. IPOS remains the independent creative identity authority and does not acquire a CAOS runtime dependency.

## Migration actions

- Replaced the parent-bound manifest with a Video-owned domain manifest and explicit external CAOS governance boundary.
- Moved the Video capability inventory into `video_growth_agent/data/capabilities.json`, preserving Video-owned capability declarations and assurance taxonomy.
- Removed the active `.uaos/` adapter, manifest and capability profile, `UAOS_SKILL.md`, and the UAOS-specific test.
- Added `CAOS_VIDEO_ENTRY.md` and repointed the package skill to the CAOS-governed Video entry.
- Removed parent-controller identity and runtime-upcall assumptions from Video coordination and project state.
- Renamed the Video-native recovery/evolution classification so it no longer represents a parent control-plane dependency.
- Rebuilt repository audit expectations and tests around the new authority boundary.
- Preserved historical audit records and old Git refs as provenance; they are not active execution authorities.

## Preserved business state

- The integrated Program `ai-self-media-commercialization` and its four workstreams.
- The current IPOS R39 authority state, bundle schema, importer, shot binding, and fail-closed identity gates.
- The separation between IPOS creative canon and Video-side use/performance evidence.
- Core Video runtime `0.8.0` and specialized episode adapter bundle `0.7.0`.
- Existing project histories, asset provenance, business flywheel, editorial/production contracts and historical pilot evidence.

## Independent acceptance — passed

- Repository system audit: PASS on exact mainline commit `2d9b4ea5ab663155eb5ac8ef17b5568eff0d3882`.
- Full pytest suite: **193 passed**.
- Installed CLI smoke test outside the repository: PASS.
- Active UAOS artifacts absent from main: `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, `.uaos/MANIFEST.json`, `UAOS_SKILL.md`, and `tests/test_uaos_current.py`.
- Video-owned domain manifest, capability profile, coordination policy and CAOS entrypoint present.
- Integrated Program, four workstreams, IPOS standalone authority and Video runtime baseline preserved.
- CAOS source repository was not modified.

Historical UAOS terminology and paths may still appear in old evolution evidence and archived Git refs to preserve provenance. They are not active manifests, runtime dependencies, startup instructions or current test authorities.

## Scope limitation

This takeover completes the governance migration and repository acceptance. It does not claim a new video has been rendered or published, that IPOS has approved a character identity, or that audience/commercial outcomes have been achieved. Those remain separate business and production acceptance gates.
