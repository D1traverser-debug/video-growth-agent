# Video Growth Agent — Product Requirements Baseline

Status: `CANDIDATE_0_8_0`
Date: `2026-10-15`
Owner: `DOMAIN:video`
Parent dependencies: `UAOS COMMON_CAPABILITIES >= 1.6.0 / COMMON_BEHAVIOR_ASSURANCE >= 1.2.0 / ARCHITECTURE_EXPERIENCE_POLICY >= 1.0.0`
Primary architecture ref: `docs/media_business_os.md`
Architecture experience ref: `docs/agent_operability_scenarios.md`

## 1. Product outcome

Video Growth Agent is one AI-native media business operating system. It turns evidence about audience needs, editorial questions and distinctive IP into repeatable high-quality media, measurable growth, sponsor/rights value and durable production learning.

It must be operable by a current Agent from durable state: the Agent can discover authority, understand the outcome, identify all admissible next actions, preserve editorial-to-production lineage, detect stale work, recover from failures/session interruption and distinguish comparable evidence from unresolved tradeoffs without relying on hidden chat memory.

Business views remain:
1. `MEDIA_GROWTH`;
2. `ORIGINAL_DIGITAL_IP`;
3. `COMMERCIALIZATION`;
4. `PRODUCTION_SYSTEM`.

They are coupled by explicit evidence/decision edges in the integrated Program and `BUSINESS_FLYWHEEL.json`, not by a hidden mega-controller.

## 2. Objective vector

Do not optimize one proxy. Preserve separate evidence for:
- editorial/product truth and audience trust;
- narrative clarity/retention/usefulness;
- distinctive-IP recognition and reuse;
- audiovisual craft and continuity;
- qualified audience growth;
- sponsorability/rights value/business outcomes;
- cash cost and creator-hours per published minute;
- iteration speed/recoverability;
- platform fit/cross-platform reuse;
- provenance/consent/rights/disclosure;
- durable learning rate.

Views, CTR, one scalar quality score, AI-video percentage or cheapest credits are never the global objective.

## 3. Identity and authority

- UAOS owns cross-domain selection/governance and common cognition/evolution/product/orchestration semantics.
- Video owns all Program/Series/Episode/Sequence/Scene/Shot/Take identities, business state, assets and domain decisions.
- `projects/PROJECT_INDEX.json` is project discovery authority.
- `ai-self-media-commercialization` remains the default integrated Program.
- UAOS may retain production verification/opaque child refs only; it does not mirror Video business state.
- `OperatorSnapshot` is a derived usability projection and never a new authority.

## 4. Primary user journeys

### VR-01 — Direct Video-domain start
Select AI video, original IP, media growth, commercialization or an exact child project and enter `DOMAIN:video` directly.

### VR-02 — Current-Agent recovery
A fresh/resumed Agent can reconstruct governing outcome, current focus, all ready/blocked actions, stale evidence/assets, capability/budget risks and recovery refs from durable Video authority without relying on conversational memory.

### VR-03 — Integrated Program
Growth, IP, commercialization and production can progress independently where no declared dependency exists and influence one another only through explicit evidence/decisions.

### VR-04 — Natural-language topic to executable editorial plan
A topic/goal becomes an `EpisodeIntent`, evidence-bound claims, ordered/dependent beats and shot intents before production routing. Facts/product truth cannot silently become visual assertions without evidence.

### VR-05 — Editorial plan to production
Every 0.8 production `ShotContract` binds the exact editorial-plan version, beat, claim lineage, truth/risk/value semantics and relevant continuity/reference state.

### VR-06 — Upstream revision impact
Editorial-plan versions are immutable assets in MediaGraph. A material upstream change can stale affected downstream production assets while preserving unaffected work and history.

### VR-07 — Original IP cross-shot continuity
Continuity is assessed by explicit dimensions and hard/soft preserve/expect/allow-change rules. Intentional changes are distinguishable from drift.

### VR-08 — Multimodal model routing
Current model/provider operations are represented as dated conditional operation profiles rather than flat provider folklore. Illegal duration/resolution/reference/source combinations fail admission.

### VR-09 — Calibrated quality tradeoff
Production quality comparisons require compatible rubric/calibration scope and preserve uncertainty. Hard floors apply before routing. Production selection uses Pareto/non-dominance plus explicit priorities, not a hidden weighted-average global score.

### VR-10 — Exploration without unsafe promotion
Safe rights/capability/budget/truth-admitted candidate generation can proceed without release-grade independent review. Candidate, promotion and release remain separate boundaries.

### VR-11 — Non-destructive iteration
Edits/extensions/replacements/regenerations create derived assets/versions with lineage; accepted originals remain recoverable.

### VR-12 — External editor handoff/roundtrip
Internal TimelineSpec can be handed to an executable editor/NLE adapter with exact timeline version, asset refs/digests and external project/composition identity. Returned edits require roundtrip execution/change evidence and become new versions rather than overwrites.

### VR-13 — Platform-specific authorship
Long/short/localized outputs are authored variants with master lineage; short-form is not blind clipping.

### VR-14 — Pre-registered media experiments
Material packaging/content experiments declare hypothesis, variants, changed/fixed variables, primary metric semantics, guardrails and observation/stop rules before interpretation. `NO_CLEAR_WINNER` and `INCONCLUSIVE` are valid results. Multi-variable tests cannot claim single-variable causality.

### VR-15 — Original IP as a business asset
Character/world/visual/audio canon is evaluated for consistency, recognizability, storytelling usefulness, packaging effect, rights/reuse and sponsor fit — not attractiveness alone.

### VR-16 — Commercial pre-production
Sponsor/product requirements enter early through explicit commercial fit, rights, claims, references and measurement contracts while editorial conclusions remain independent.

### VR-17 — Performance and learning
Platform, production and commercial outcomes remain separate receipts and may create scoped learning candidates. Durable rules require evidence, counterexamples and replay/regression rather than post-hoc storytelling from one hit.

### VR-18 — Problem recovery and system repair
Before asking the user for a recoverable dependency, Video attempts owner-native recovery. Confirmed repairable system gaps are repaired now or end with an actual blocker/evidence-backed no-change.

## 5. Canonical object model

Hierarchy:
`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Core object families:
- `Context`;
- `AssetVersion`/lineage;
- `Task`;
- `Evidence`;
- `Decision`;
- `EpisodeIntent` / `ClaimSpec` / `BeatSpec` / `ShotIntent` / `EditorialPlan`;
- `ShotContract` / `ReferenceBinding` / `TakeRecord`;
- `ContinuitySnapshot` / `ContinuityLink` / `ContinuityAssessment`;
- `TimelineSpec` / `EditorialHandoff` / `EditorialRoundTripReceipt`;
- `OperationProfile` / `QualityObservation` / `ModelRoutingDecision`;
- `ExperimentPlan` / `ExperimentConclusion`;
- shared growth/IP/commercial objects and outcome receipts;
- derived `OperatorSnapshot`.

Stable IDs/digests/versions outrank filenames and chat memory.

## 6. Editorial planning requirements

- Episode intent declares audience contract, editorial question, platform/duration, evidence, desired outcomes and metric semantics.
- Factual/product-truth claims require evidence.
- Beat dependencies are acyclic and every beat has at least one production expression.
- Shot intents state visual job, truth/risk, source claims, allowed modes, value vector and relevant continuity/reference intent.
- Plans are immutable/versioned; revisions carry reasons and expose changed claims/beats/shots.
- Durable plan versions become MediaGraph assets so production lineage can be invalidated selectively.

## 7. Provider/model requirements

The capability registry must express operation-specific legal combinations, including mode, duration, resolution, reference budgets, source origin/conditions and supported controls.

Quality observations must bind:
- value;
- rubric ID;
- calibration scope;
- uncertainty;
- evidence class/refs.

Official documentation can establish supported operations/limits/terms/availability, but only owner benchmark/production evidence establishes owner quality values.

Routing requirements:
- current availability/deprecation/freshness hard gates;
- operation-profile compatibility hard gate;
- commercial/provenance/right requirements hard gate;
- uncertainty-aware quality floors;
- budget hard gate;
- exploration = cheapest sufficient;
- production = Pareto/non-dominated quality evidence, then explicit priorities if needed;
- unresolved material tradeoff without declared priority must remain visible rather than be hidden in one scalar.

The old scalar router may remain importable as a legacy compatibility module but is not part of the current top-level API.

## 8. Production, promotion and release

Candidate generation admission requires complete production contract, current route/capability evidence, rights/consent, truth-policy compatibility and budget evidence.

Asset promotion requires exact take/artifact identity, quality, continuity when relevant, rights/truth, technical QA and risk-proportional independent review.

Release requires final-media digest, master timeline, QA, rights, claim/product truth, provenance, disclosure/platform validation and release owner.

Candidate/rejected/stale assets cannot silently return to accepted state.

## 9. Continuity requirements

- Continuity is dimension-level state, not a universal similarity score.
- Rules support `PRESERVE`, `EXPECT`, `ALLOW_CHANGE` and hard/soft severity.
- Missing source values for a required preserve relation are observable failures.
- Identity/world/wardrobe/prop/camera/light/audio/product/narrative-state dimensions may be tracked independently.
- Canon/ref changes stale only consuming downstream work through MediaGraph lineage.

## 10. Timeline/editor requirements

- Master timeline is non-destructive and references promoted asset versions.
- Platform variants derive from explicit master versions.
- External editors are adapters; they never own canonical business truth.
- Handoffs bind timeline version, source asset refs/digests, format, purpose, capability evidence and external project/composition identity when applicable.
- Roundtrip receipts must bind the originating handoff/version/adapter/project/composition and execution evidence.

## 11. Growth/experiment requirements

- Platform variants declare authored hook/packaging/duration/aspect/CTA and stable metric semantics.
- Pre-registered experiments distinguish single-variable causal tests from multi-variable package tests.
- Observation/stop rules exist before result interpretation.
- `WINNER`, `NO_CLEAR_WINNER`, `INCONCLUSIVE`, `STOPPED_GUARDRAIL` are valid conclusions.
- One viral result is not durable policy by itself.

## 12. IP requirements

Canon may cover geometry, expressions, wardrobe/props, color/material/light grammar, voice/performance, motion/gesture, environment/world grammar, distinctive motifs, allowed variants and rights/likeness constraints.

Identity-sensitive shots bind exact canon versions and explicit continuity dimensions. The recurring Digital Observer/Narrator remains a reusable anchor, not a forced presenter in every scene.

## 13. Commercial/truth requirements

CommercialFit/RightsPackage evidence covers advertiser adjacency, natural integration, product-truth requirements, deliverables, territories/duration/exclusivity/paid-media rights, production uplift, measurement and reuse/case-study value.

- sponsorship never overrides editorial truth;
- factual product/UI/material/behavior claims use verified source/brand assets or clearly non-evidentiary visualization;
- real-person likeness/voice requires consent/rights evidence;
- available provenance/C2PA/Content Credentials are preserved;
- release carries current platform disclosure decision.

## 14. Economics requirements

Track provider/model/mode, generated/input seconds, retries/rejections, cash/credits, creator/reviewer minutes, latency, reuse, cost per accepted shot/published minute, platform-variant marginal cost and commercial margin where available.

Budget changes are resolved from shot narrative/value/risk/degradation evidence and accepted-take economics rather than a universal fixed premium percentage.

## 15. CURRENT_AGENT operability requirements

For architecture/experience changes, apply the relevant scenarios in `docs/agent_operability_scenarios.md`.

The Agent must be able to answer from durable evidence:
1. what outcome is being served;
2. what is authoritative now;
3. which actions are ready, blocked, waiting or legitimately parallel;
4. what progress evidence each ready action must produce;
5. what is stale or capability/budget constrained;
6. how to recover after failure/session interruption;
7. which quality evidence is comparable and which remains a tradeoff;
8. whether a user statement is a requirement/constraint versus an illustrative example.

Operator projections remain derived and non-authoritative.

## 16. Functional requirement map

| Requirement | Owning surface | Acceptance evidence |
| --- | --- | --- |
| Product architecture | `docs/media_business_os.md` | architecture/system-audit tests |
| Agent-operability scenarios | `docs/agent_operability_scenarios.md` | dogfood/trajectory tests |
| Business flywheel | `BUSINESS_FLYWHEEL.json` | schema/invariant tests |
| Media context/asset/evidence/decision graph | `media_graph.py` | lineage/promotion/invalidation tests |
| Editorial intent/claims/beats/shots | `editorial_planning.py` | editorial admission/revision tests |
| Editorial plan -> graph lineage | `plan_graph_bridge.py` | downstream stale propagation test |
| Shot/reference/take/promotion/release | `production_os.py` | admission tests |
| Cross-shot continuity | `continuity.py` | preserve/expect/allow-change tests |
| Conditional provider + calibrated vector routing | `model_registry.py` | operation/Pareto/calibration trajectory tests |
| Non-destructive timeline | `timeline.py` | promoted-asset/derivation tests |
| External editor interchange | `editorial_interchange.py` | handoff/roundtrip identity tests |
| Pre-registered experiments | `experiments.py` | attribution/outcome tests |
| Growth/IP/commercial shared objects | `business_objects.py` | business object tests |
| Vector business outcomes | `business_metrics.py` | metric tests |
| Current-Agent projection | `operator_view.py` | readiness/blocker/resume tests |
| Common Behavior 1.2 | `owner_behavior_admission.py` | recovery/closure trajectory tests |
| Canonical evolution | `audits/EVOLUTION_INDEX.json` | audit/index tests |
| Existing Program graph | `PROGRAM_STATE.json` + `SUBTASK_GRAPH.json` | orchestration tests |
| Legacy work-order/attestation/QA | current runtime modules | regression suite |
| Packaging/install/current architecture integrity | package + CI audit/tests | system audit, pytest, installed smoke |

## 17. Non-functional requirements

- one Video business owner; no parallel controller;
- direct domain activation;
- stable identifiers/non-destructive lineage;
- provider/editor replaceability;
- current-enough capability/price/terms evidence;
- no self-approval;
- fail-closed promotion/release without exploration paralysis;
- explicit cross-workstream evidence flows;
- no hidden prompt/chat-memory authority;
- no hidden scalar business/quality objective;
- no write races on the same authoritative object;
- business state stays child-owned.

## 18. Candidate completion criteria for 0.8.0

1. Editorial intent->claim->beat->shot planning is executable and traceable into ShotContract.
2. Editorial-plan versions participate in MediaGraph lineage/invalidation.
3. Cross-shot continuity state distinguishes hard/soft and intentional change.
4. Model routing represents conditional operation profiles and calibrated uncertainty-aware quality; production selection has no hidden scalar collapse.
5. External editor handoff/roundtrip binds exact internal/external identities.
6. Material media experiments are pre-registerable and cannot fabricate single-variable causality or a winner.
7. Current-Agent operator projection is useful but mechanically non-authoritative.
8. CURRENT_AGENT dogfood scenarios cover primary success, failure/recovery, resume, requirement change, external-tool handoff and outcome learning.
9. 0.7 asset/timeline/business/behavior/work-order/QA guarantees remain green.
10. System/architecture tests fail closed if declared 0.8 current surfaces disappear or drift.
11. Product/Skill/Manifest/Capabilities/runtime version/Program system status are internally consistent.
12. H1/A2 creative cursor is unchanged by architecture maintenance.
13. Candidate full CI + installed smoke pass.
14. Controlled promotion is followed by production-main CI and production reread.
15. Evolution closes with stable event-style production evidence; UAOS parent observation is refreshed only after child production is verified.

Live published-video audience/IP/commercial outcomes remain real-world observations and are not fabricated by code/tests.
