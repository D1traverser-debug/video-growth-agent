# CAOS Governance Takeover — Video Growth Agent

Date: 2026-11-14
Status: CANDIDATE_IMPLEMENTED__EXACT_HEAD_CI_PENDING
Video repository: `D1traverser-debug/video-growth-agent`
Base revision: `d44ea379f99a96f4a07ae021c35e7f094df7b29a`
Working branch: `migration/caos-video-governance-20261114`
CAOS source repository: `D1traverser-debug/cognition-agent-os` (read-only; no files changed)

## Root cause

The Video repository still declared an active external parent controller in its root manifest and adapter. Its root operating skill, capability profile, coordination policy, product requirements, architecture docs, project-state identity fields and repository audit all depended on that binding. The repository audit explicitly failed if the parent manifest, adapter and capability profile were removed, while a dedicated test required those files to remain. Deleting only the visible directory would therefore leave a broken and internally contradictory Video system.

The capability profile also contained Video-owned production capabilities. Those are domain assets, not parent-controller code, and must be migrated rather than discarded.

## Decision

CAOS becomes the external parent cognition/governance layer for Video work in the active ChatGPT session. The Video repository remains the sole authority for its business identities, project state, media graph, assets, editorial decisions, runtime and domain evolution.

The integration is deliberately `CHAT_GOVERNED_EXTERNAL`, with no CAOS runtime/API dependency and no copied CAOS implementation. CAOS source remains read-only. IPOS remains the independent creative identity authority and does not acquire a CAOS runtime dependency.

## Migration actions

- Replace the parent-bound manifest with a Video-owned domain manifest and explicit external CAOS governance boundary.
- Move the capability inventory from the parent-namespaced directory into `video_growth_agent/data/capabilities.json`, preserving Video-owned capability declarations and assurance taxonomy.
- Remove the parent adapter and parent skill entry; add `CAOS_VIDEO_ENTRY.md` and repoint the package skill.
- Remove parent-controller identity semantics from the Program, project manifest, project index, and historical pilot state.
- Repoint the coordination policy to CAOS governance without creating a runtime upcall.
- Rename the Video-native recovery/evolution classification so it no longer represents a parent control-plane dependency.
- Rebuild repository audit expectations and tests around the new authority boundary.
- Preserve historical audit records and old Git refs as provenance; they are not active execution authorities.

## Preserved business state

- The integrated Program `ai-self-media-commercialization` and its four workstreams.
- The current IPOS R39 authority state, bundle schema, importer, shot binding, and fail-closed identity gates.
- The separation between IPOS creative canon and Video-side use/performance evidence.
- Core Video runtime `0.8.0` and specialized episode adapter bundle `0.7.0`.
- Existing project histories, asset provenance, business flywheel, editorial/production contracts and historical pilot evidence.

## Acceptance still required

- Run full repository tests and package/system audit on the exact candidate head.
- Verify the active docs and skill surfaces no longer route to the retired parent controller.
- Verify the Video capability profile and project state remain intact.
- Verify the CAOS repository main tree is unchanged.
- Verify the merged Video main branch and exact production CI before declaring the migration complete.

No claim of successful rendering, publishing, character approval, or real-world business outcome is made by this migration.
