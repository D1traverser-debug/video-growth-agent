# Video 0.8 Agent-Operable Media OS — Resume Checkpoint

Status: `INTERRUPTED_CANDIDATE__RESUME_REQUIRED`
Owner: `DOMAIN:video`
Evolution: `V-20261015-02-AGENT_OPERABLE_MEDIA_OS`
PR: `#15 architecture: Video 0.8 agent-operable Media OS`
Branch: `feat/agent-operable-media-os-0-8-20261015`
Checkpoint time: `2026-10-15T18:48:00+08:00`
Production baseline remains: `Video 0.7.0`, main `55f605e641671a513637ffb03b532c66335a2ad9`
Creative cursor remains unchanged: `ORIGINAL_DIGITAL_IP / H1_SCULPTURAL_MASSING_V2 / A2 next`

## Resume rule

A new conversation resuming Video system architecture must NOT restart from production 0.7 as if no work exists and must NOT promote this candidate merely because substantial code exists.

Resume in this order:
1. read `audits/EVOLUTION_INDEX.json`;
2. read this checkpoint;
3. read `audits/VIDEO_AGENT_OPERABILITY_REDESIGN_2026-10-15.md`;
4. read `docs/agent_operability_scenarios.md`;
5. inspect current PR #15 head and its latest CI before any write;
6. continue only on `feat/agent-operable-media-os-0-8-20261015` or a deliberate successor candidate branch;
7. preserve H1/A2 creative state; system maintenance must not execute the creative next action.

## Governing user requirement recovered

Evaluate and improve the Video system from lived use by the current Agent, using any relevant learned skills/methods. Spatial frameworks and sequential construction are useful representations when appropriate, but neither is a mandatory universal architecture. The governing outcome is an architecture the Agent can actually understand, operate, recover and evolve across editorial planning, production, IP, growth and commercialization.

## Dogfood scenarios already used

1. natural-language topic -> executable episode;
2. digital-IP continuity across shots;
3. upstream claim/plan change after paid generation;
4. provider/model deprecation or conditional capability change;
5. budget cut mid-production;
6. sponsor enters after planning starts;
7. external editor/NLE handoff and roundtrip;
8. long-form master -> authored short-form variants;
9. interruption/resume;
10. published audience/business outcomes -> learning/evolution.

Full scenario authority: `docs/agent_operability_scenarios.md`.

## Problems already found

- `G1` Editorial reasoning existed in docs but runtime materially began at `ShotContract`; audience contract/claims/beats/shot-to-claim rationale were hidden in Agent working memory.
- `G2` Cross-shot continuity was implicit and could not distinguish hard-preserve dimensions from intentional change.
- `G3` `model_registry.py` stored quality vectors but selection re-collapsed them into weighted scalar `quality_utility`; cross-provider numeric comparability lacked rubric/calibration proof.
- `G4` Provider capability model was flat and could not express operation-specific combinations/constraints.
- `G5` Internal timeline lacked external editor project/composition identity and roundtrip receipts. Read-only Descript dogfood confirmed real Pilot projects/compositions make this operationally material. No external project was mutated.
- `G6` Growth learning lacked preregistered hypothesis/variable/metric/guardrail/stop-rule semantics and first-class inconclusive outcomes.
- `G7` Resume required mentally synthesizing many authority files; a compact derived non-authoritative operator projection was missing.
- `G8` method/status drift exists: `PRODUCTION_AND_COST_STRATEGY.md` still reported candidate 0.7, and provider benchmark status required reconciliation.

Primary causal audit: `audits/VIDEO_AGENT_OPERABILITY_REDESIGN_2026-10-15.md`.

## Candidate runtime already implemented

- `video_growth_agent/editorial_planning.py`
  - `EpisodeIntent`, `ClaimSpec`, `BeatSpec`, `ShotIntent`, versioned `EditorialPlan`;
  - evidence/truth checks, beat DAG, impact comparison;
  - explicit `materialize_shot_contract()` boundary.
- `video_growth_agent/plan_graph_bridge.py`
  - editorial-plan versions enter existing MediaGraph as upstream versioned assets so downstream invalidation can reuse one dependency graph.
- `video_growth_agent/production_os.py`
  - ShotContract now binds editorial plan / beat / source claim / continuity / value-vector context.
- `video_growth_agent/continuity.py`
  - dimension-level continuity rules rather than one opaque continuity score.
- `video_growth_agent/model_registry.py`
  - operation profiles for legal capability combinations;
  - evidence-bound `QualityObservation` with rubric/calibration scope/uncertainty;
  - hard floors use lower bounds;
  - production selection uses Pareto-front + explicit priority instead of weighted scalar collapse.
- `video_growth_agent/experiments.py`
  - preregistered hypothesis, changed/fixed variables, metric semantics, guardrails, observation/stop rules;
  - multi-variable test cannot claim single-variable causal attribution;
  - `NO_CLEAR_WINNER` / `INCONCLUSIVE` supported.
- `video_growth_agent/editorial_interchange.py`
  - internal timeline/version + asset digests + adapter evidence + external project/composition identity + roundtrip receipt.
- `video_growth_agent/operator_view.py`
  - derived current-Agent operating projection; intentionally non-authoritative and unable to promote/mutate business truth.
- package top-level current routing surface was adjusted so legacy scalar router remains compatibility code rather than the preferred public entry.

New tests already added for the new modules and counterexamples.

## External method evidence already used

- MovieLabs software-defined production / OMC concepts: narrative information must connect into production elements and dependency relationships should expose downstream consequence of upstream change.
- current provider documentation: operation/capability combinations are conditional and volatile; official docs establish limits/capabilities, not owner quality ranking.
- YouTube current experiment semantics: evaluation cannot be reduced to CTR alone and may produce no clear winner.
- real connected Descript read-only dogfood: prior Pilot 001/002 projects/compositions/published QA exist, confirming external editor identity must be explicit.

Do not turn any one external ontology/tool/provider into architecture authority.

## Verification history

Early runtime candidate head `b5d7da1c4a7f851319b9a2304470f53a5ab48ca4`:
- PR CI `#589 / run 38721670861` passed system hygiene audit, full pytest and installed CLI smoke.

Later head before this checkpoint: `9bc5abad9dd91e2970dc17f19fcc3bef7dcb8bc9`.
Latest CI at interruption: `#603 / run 38722504017` = `FAIL`.
Important: system hygiene audit still passed. Pytest result was `176 passed, 3 failed`; installed CLI smoke was skipped because pytest failed.

The three failures are reconciliation/contract failures, not evidence that the new runtime modules crashed:
1. `tests/test_media_business_os_architecture.py::test_media_business_os_is_primary_architecture_and_legacy_stage_machine_is_adapter`
   - new `docs/media_business_os.md` no longer contains exact legacy assertion text `The legacy stage workflow remains a compatibility adapter`.
2. `tests/test_media_business_os_architecture.py::test_video_common_behavior_1_2_is_owner_native_and_resolved_evolution_is_discoverable`
   - old test asserts `current_open_items == []`, which conflicts with the intentionally open 0.8 evolution item.
3. `tests/test_video_product_architecture.py::test_media_business_docs_reject_vendor_lockin_scalar_quality_and_stage_role_overfit`
   - new architecture text no longer contains exact phrase `Quality is a vector` although the new router is more strongly vector-aware.

Do not hide these by deleting the open evolution item or weakening the architectural invariant. Reconcile the tests/document wording according to current semantics.

## Work intentionally NOT finished

At interruption, do NOT treat 0.8 as production. Remaining candidate work includes:

1. reconcile the three latest CI failures semantically;
2. finish `system_audit.py` 0.8 fail-closed coverage for every newly canonical runtime surface;
3. add/finish end-to-end trajectory tests spanning editorial plan -> ShotContract -> MediaGraph lineage/invalidation -> operator recovery;
4. reconcile current docs and authority labels, including residual 0.7/candidate method drift such as `PRODUCTION_AND_COST_STRATEGY.md`;
5. coherently update release/profile bindings only when candidate is ready: `pyproject.toml`, package data versions, `.uaos/MANIFEST.json`, `.uaos/CAPABILITIES.json`, `UAOS_SKILL.md`, README/product/architecture refs and any system audit expectations;
6. rerun full candidate CI on the actual latest head;
7. perform reverse audit: docs <-> runtime <-> capability declarations <-> tests;
8. controlled merge only after candidate is green and architecture-experience audit passes;
9. after merge, verify production/main CI and production reread;
10. close evolution evidence and then refresh UAOS parent observation. Parent must not claim 0.8 before child production evidence exists.

## Protected invariants / do-not-do

- Do not execute or advance A2/H1 creative work as part of system architecture maintenance.
- Do not overwrite accepted/rejected IP evidence.
- Do not make OperatorSnapshot a controller or source of truth.
- Do not create another dependency graph when MediaGraph lineage can represent the dependency.
- Do not restore hidden weighted quality as the production selector merely to simplify tests.
- Do not hard-code a provider as a permanent default.
- Do not claim quality ranking from vendor marketing/docs without owner benchmark evidence.
- Do not mutate external editor projects merely for architecture testing.
- Do not merge PR #15 while latest candidate CI is red.

## Exact next action

First action on resume: fetch PR #15 latest head and latest workflow run, then fix the three semantic reconciliation failures above on the candidate branch without changing the creative cursor. After that, rerun CI before continuing version/profile/promotion work.

## Resume phrase for user

`继承 视频系统 0.8。读取 video-growth-agent PR #15、audits/VIDEO_0_8_RESUME_CHECKPOINT_2026-10-15.md、EVOLUTION_INDEX 和 VIDEO_AGENT_OPERABILITY_REDESIGN_2026-10-15.md，从最新 CI 失败断点继续；不要推进 H1/A2。`
