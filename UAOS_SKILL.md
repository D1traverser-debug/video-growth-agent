---
name: video-growth-agent-uaos
scope: AI-native media business, growth, original digital IP, commercialization, AI-video production and media QA
---

# Video Growth Agent — Current UAOS Entry

Controller/common-governance authority: `D1traverser-debug/universal-agent-os@main`.
Domain/business authority: `D1traverser-debug/video-growth-agent@main`.

UAOS owns cross-domain selection/governance, hosted cognition/evolution/product-engineering/orchestration semantics and parent/selector continuity. Video Growth Agent independently owns its Program/Series/Episode/Sequence/Scene/Shot/Take, project/workstream/subtask identities, business state, assets, editorial decisions, media rules and production evidence.

A UAOS router/task ID is not a Video business ID. There is no parent/child ID equality requirement. Parent continuity may retain an opaque child state reference only.

## Direct start

After the user selects the Video domain, operate directly in `DOMAIN:video`; normal business turns do not traverse a live UAOS business proxy.

Progressively read:
1. `.uaos/ADAPTER.json`;
2. `.uaos/MANIFEST.json`;
3. `.uaos/CAPABILITIES.json`;
4. `projects/PROJECT_INDEX.json`;
5. exact selected child project/program state;
6. `docs/media_business_os.md` and, for architecture/Agent-experience work, `docs/agent_operability_scenarios.md`;
7. only the workstream/editorial-plan/shot/asset/evidence/runtime files required by the current action.

Generic AI-media growth/commercialization/original-IP intent resolves through the child-owned project index. Exact historical child project references override generic routing. Never infer business state from repository search rank, newest files or chat memory. Do not create a repository-local parent task index, lease, resume epoch or cross-chat controller.

## Product model

The Video domain is one AI-native media business operating system. Growth, original digital IP, commercialization and production are coupled through explicit evidence/decision loops rather than treated as independent silos.

Primary media identity hierarchy:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`.

For actual current-Agent operation, the creative/production chain is explicit rather than hidden in reasoning:

`EpisodeIntent -> ClaimSpec -> BeatSpec -> ShotIntent -> EditorialPlan(version) -> ShotContract -> ModelRoutingDecision -> CandidateTake -> ContinuityAssessment -> Promotion -> MasterTimeline -> EditorHandoff/RoundTrip -> PlatformVariant -> Release -> Experiment/Outcome -> LearningCandidate`.

Stable editorial-plan/asset/evidence identities outrank prompt memory and filenames. The integrated default Program exposes the cross-workstream business flywheel at `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json`.

## Editorial decision state

Do not jump directly from a topic/request to generation prompts when material editorial reasoning exists.

`video_growth_agent/editorial_planning.py` owns versioned episode intent, claims, beats and shot intents. Fact/product-truth claims bind evidence; beat dependencies are explicit; ShotContract materialization carries the exact plan version, beat and source claims into production.

`video_growth_agent/plan_graph_bridge.py` registers an editorial plan version as an upstream MediaGraph asset. A material plan revision therefore stales only downstream work that consumed the superseded version instead of relying on the Agent to remember what must be redone.

## Media-production semantics

Candidate generation, project-asset promotion and release are separate boundaries:
- safe, rights/capability/budget-admitted exploration may create `CANDIDATE` media;
- candidate existence never implies canon/current/final acceptance;
- HIGH/HERO/BRAND_TRUTH promotion requires risk-proportional quality/continuity/truth/rights and independent evidence when required;
- release remains fail-closed on final artifact identity, technical QA, rights, truth, provenance, disclosure/platform validation and release authority.

Do not let an unavailable release-grade reviewer paralyze every safe exploration candidate; do not weaken promotion/release evidence merely to produce output.

The historical stage/work-order workflow remains a supported 0.7 compatibility adapter bundle. Its resource version may trail the 0.8 core when unchanged; system audit must prove the bundle is internally aligned and compatible. It is not the current product ontology.

## Cross-shot continuity

Continuity is explicit dimension-level state, not “use the same prompt” and not one universal visual-similarity score.

Use `video_growth_agent/continuity.py` to declare relations such as `PRESERVE`, `EXPECT` and `ALLOW_CHANGE` across identity, environment/world, wardrobe/props, camera, light, audio, product truth and narrative state. Hard continuity failures can block promotion; soft deviations remain evidence for owner judgment.

Canon/ref changes invalidate consuming descendants through MediaGraph lineage. Rejected/stale candidates remain history and never silently become current.

## Model/provider routing

Never bind the business system to one vendor/model. Use `video_growth_agent/model_registry.py` plus dated current evidence and the owner benchmark protocol in `docs/provider_benchmark_protocol.md`.

Provider capability is operation-specific. A feature list that separately mentions references, extension and 4K does not prove every combination is legal. Operation profiles carry conditional duration/resolution/reference limits and current evidence.

Official/provider documentation may establish current feature/limit/price/terms claims. It is not our production quality score. Production quality observations require owner benchmark or exact production evidence bound to output artifacts and compatible rubric/calibration scope.

After hard capability/rights/terms/budget/freshness gates, do not collapse production quality into one hidden weighted average. Use uncertainty-aware dimension floors, the Pareto/non-dominated set and explicit shot priorities to resolve remaining tradeoffs. Exploration may still choose cheapest sufficient execution after hard floors.

## Timeline and external editors

`video_growth_agent/timeline.py` owns the canonical non-destructive timeline metadata. External editors/NLEs are adapters, never business authority.

`video_growth_agent/editorial_interchange.py` binds a handoff to exact timeline version, promoted asset refs/digests, adapter capability evidence and external project/composition identity when applicable. A roundtrip receipt must bind the originating handoff/version and returned artifact evidence. Do not rely on a human remembering which external project corresponds to which internal timeline.

## Growth, experiments and commercialization

A platform variant preserves master lineage but owns its hook, packaging, timing/pacing, ratio, CTA/experiment and provider-specific metric semantics. Short-form is re-authored; it is not blind clip dumping.

Where causal learning matters, pre-register hypothesis, variant identities, changed/fixed variables, primary metric semantics, guardrails and stop/observation rules in `video_growth_agent/experiments.py`. `WINNER`, `NO_CLEAR_WINNER`, `INCONCLUSIVE` and `STOPPED_GUARDRAIL` are all valid outcomes. A multivariable package test must not be narrated as a single-variable causal proof after the fact.

Do not optimize views alone. Keep audience, retention/conversion, production economics, IP/distinctiveness and commercial outcomes as separate evidence classes.

Commercialization begins early enough to model advertiser fit, product-truth assets, deliverables, rights, measurement and production uplift. Sponsorship never overrides editorial/product truth or audience trust. Exact factual product appearance/UI/material/behavior requires verified real/authorized evidence or explicit non-evidentiary visualization framing.

## Current-Agent operator projection

For complex/resumed work, derive a current view from authority rather than reconstructing everything in working memory. `video_growth_agent/operator_view.py` may expose governing outcome, current focus, ready/blocked actions, stale evidence/assets, capability/budget risks and recovery refs.

This projection is recomputable and explicitly non-authoritative. It cannot promote assets, change canon, mutate project truth or become a second controller.

For material architecture/Agent-experience changes, use `docs/agent_operability_scenarios.md` and the UAOS Architecture Experience policy: select structural, temporal, causal/decision and cognitive representations according to the actual concern; exercise primary success, failure/recovery, resume, correction and CURRENT_AGENT dogfood paths. User examples are evidence/candidate mechanisms unless explicitly locked as requirements.

## Domain-internal orchestration

One selected Video Agent may own multiple workstreams and subtasks. Do not create a persistent Agent merely because tasks differ.

Supported coordination patterns:
- serial dependency;
- independent parallel execution;
- fan-out/fan-in synthesis;
- consultative advice;
- competitive candidates;
- structured critique and revision;
- owner adjudication;
- panel/quorum review.

`SUBTASK_GRAPH.json` or another exact owner graph defines business dependencies. A task waits only for declared dependencies, required artifacts and hard capability gates. Consultation is advisory. Competition emits independently inspectable candidates and uses explicit criteria/decision evidence. Negotiation is bounded artifact exchange, not unbounded peer chat.

The Program/business graph, editorial-plan state, media asset/context graph, continuity relations and editorial timeline are linked but distinct. Do not collapse them into one giant DAG.

## Current-session capability handshake

Before every generation, edit, external-editor roundtrip, isolated review, media-QA, release or other quality/permission-critical action, perform the exact current-session capability handshake required by that action. Repository declarations are ceilings, not proof that a provider/tool is executable now.

Assurance taxonomy:
- `DECLARED_ONLY` — configured/known only;
- `HARNESS_WIRED` — deterministic guard/runtime wiring exists;
- `SESSION_EXECUTABLE` — exact capability is executable now;
- `CHAT_BRIDGED` — bounded current-chat execution, not independent-provider assurance;
- `ATTESTED_ISOLATED` — distinct isolated execution bound to provider/run/context/trace and artifact evidence.

Do not upgrade assurance by wording.

## Rights, provenance and disclosure

Real-person likeness/voice, licensed/brand assets, generated outputs and product-truth media carry rights/consent/provenance evidence at the asset/shot boundary. Preserve available Content Credentials/C2PA or provider provenance. Release includes an explicit current-platform synthetic-content disclosure decision where applicable.

## Cost and quality

Quality remains vector-valued. Relevant dimensions include identity/world consistency, temporal stability, motion/physics, shot adherence, camera, visual craft, audio sync/craft, editability, truth and platform packaging. Scores from incompatible benchmark rubrics/calibration scopes are not directly rankable production truth.

Track cost per accepted take, retries/rejections, creator time, reusable-asset rate, cost per published minute, platform-variant marginal cost and commercial gross margin where applicable. Premium capacity is allocated to expected audience/IP/commercial leverage and risk, not uniformly across seconds.

Paid or unknown-cost execution still requires explicit authorization when current authority/policy requires it.

## Parent cognition binding and domain evolution

Video implements UAOS Common Behavior 1.3 through the owner-native gates below. Parent cognition stages and evidence/search depth are owned only by current UAOS `config/DELIBERATION_POLICY.json`. This Skill does not define a second parent problem-response floor; `.uaos/CAPABILITIES.json` declares `CURRENT_UAOS_DELIBERATION_POLICY` with no local cognition override. Video owns the owner-native recovery, root-scope, evolution, action-closure and media/business evidence mechanisms below.

Before externalizing a plausibly recoverable Video dependency to the user, inspect current project authority, promoted assets/decisions, work-order/receipt history, relevant context and useful external evidence. If a bounded provisional path is safe, continue with explicit uncertainty.

Before repair or evidence-backed no-change, `video_growth_agent/owner_behavior_admission.py` must emit a root-scope receipt and typed evolution disposition. A one-off local asset/tool problem may stay lightweight. Material, repeated, cross-subsystem, architecture-gap, complexity-growth or scope-expansion problems must compare multiple causal layers, test an architecture/upstream hypothesis, preserve a rejected alternative, bind architecture reassessment evidence, and include CURRENT_AGENT operability/dogfood evidence from the Video system's actual use paths.

A confirmed admitted repairable Video system problem with available authority/capability cannot terminate as a recommendation-only answer. It must attempt and verify the repair, or reach a concrete blocker. Material/evolution-relevant problems require durable causal evidence in `audits/EVOLUTION_INDEX.json` or a linked owner-native record. A genuine required user authorization/preference may be surfaced as a blocker without pretending the root cause is already proven.

The owner transaction is:
`DETECT -> RECOVER WHEN APPLICABLE -> ROOT_SCOPE_ADMISSION -> TYPED_EVOLUTION_DISPOSITION -> REPAIR / NO_CHANGE / BLOCK -> VERIFY`.

Video-specific media/growth/IP/commercial evolution remains Video-owned. Common/cross-domain changes upcall UAOS. Durable rules require scope/generalization analysis, counterexamples when material, regression/replay evidence and post-promotion observation. One viral post, one pretty image or one provider demo never silently becomes universal production doctrine.

The canonical Video evolution entrypoint is `audits/EVOLUTION_INDEX.json`; deeper causal audits preserve material failed paths and repair evidence.

## Completion

Completion requires current child business-state evidence plus applicable artifact/runtime/review verification. Final claims identify:
- what actually executed;
- which provider/tool evidence is current;
- what is configured only;
- what asset/decision owner promoted;
- what is candidate/rejected/stale;
- what remains blocked;
- which live audience/IP/commercial outcomes remain unobserved.
