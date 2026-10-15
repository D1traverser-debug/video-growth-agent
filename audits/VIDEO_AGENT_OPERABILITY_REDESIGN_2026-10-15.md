# Video Agent Operability Redesign — 2026-10-15

Status: `RESOLVED_PRODUCTION_0_8_0`
Owner: `DOMAIN:video`
Evolution ID: `V-20261015-02-AGENT_OPERABLE_MEDIA_OS`
Resolved at: `2026-10-15T19:15:03+08:00`
Parent method: UAOS Architecture Experience Evaluation 1.0 + Common Behavior Assurance 1.2

## Trigger

The Video architecture was challenged from lived use rather than static framework completeness: act as the current Video Agent and ask where it would lose state, choose a plausible-but-wrong action, fail to recover, or need hidden chat memory. Spatial/structural and sequential representations were treated as tools selected by concern rather than fixed requirements.

## Governing outcome

Make Video an AI-native media business operating system that a current Agent can understand, operate, recover and evolve across editorial planning, production, original IP, growth and commercialization without reconstructing key state in hidden reasoning.

## Baseline

Verified baseline before this evolution was Video 0.7.0 / Profile 8 at main `55f605e641671a513637ffb03b532c66335a2ad9`. 0.7 had already established MediaGraph, Shot/Take candidate-promotion-release boundaries, non-destructive timelines, typed business objects, provider-neutral routing intent, business outcomes, the Business Flywheel and owner-native Common Behavior. The H1/A2 creative cursor was explicitly outside this system-maintenance scope.

## CURRENT_AGENT dogfood and observed problems

Ten lived scenarios were walked: topic-to-episode, cross-shot IP continuity, upstream-plan change after generation, provider/API change, budget cut, sponsor insertion, external editor roundtrip, long-to-short re-authoring, interrupted-session resume, and post-publication learning. `docs/agent_operability_scenarios.md` is the durable acceptance surface.

The walk exposed eight material gaps:

1. **Editorial decision bridge was documentary, not executable.** Runtime became mechanical at ShotContract, so audience contract, claim evidence, beat function and shot-to-claim traceability could remain in Agent working memory.
2. **Cross-shot continuity was too implicit.** Asset identity existed, but hard identity preservation versus intentional world/wardrobe/light/time changes was not represented as explicit relationships.
3. **Quality vectors were re-collapsed at selection time.** The router stored dimensions but ranked production candidates through a weighted scalar, hiding non-substitutable tradeoffs and calibration differences.
4. **Provider capabilities were flat.** Feature presence could be mistaken for proof that a particular duration × resolution × reference × source-origin operation combination was legal.
5. **External-editor identity was missing.** Internal TimelineSpec existed, but project/composition identity, exact exported timeline version, asset digests and return receipts were not first-class. Read-only Descript dogfood against real prior Pilot projects confirmed this mattered operationally; no external project was mutated.
6. **Growth learning lacked preregistration semantics.** Hypothesis, changed variables, metric semantics, guardrails and no-clear-winner/inconclusive outcomes could be reconstructed after seeing results.
7. **Resume required excessive mental synthesis.** Authority existed, but there was no compact derived view of governing outcome, parallel-ready work, blockers, stale evidence and recovery refs.
8. **Method authority drift existed.** Production/cost and benchmark entrypoints still carried stale candidate labels after their surrounding architecture had advanced.

## Governing assumptions challenged

- “Executable low-level media objects are enough; the Agent can reconstruct editorial logic.” — rejected.
- “Vector storage is sufficient even if ranking is scalar.” — rejected.
- “Provider capability can be a flat boolean feature set.” — rejected for conditional combinations.
- “Internal timeline lineage makes editor project identity an implementation detail.” — rejected by connected-editor dogfood.
- “Metrics after publication are enough for learning.” — rejected when causal hypotheses and semantics can be authored post hoc.
- “One global next action is simpler.” — rejected because legitimate Program workstreams can be ready in parallel.
- “A universal sequence layer would solve operability.” — rejected; structural, temporal, causal and cognitive concerns require different representations.

## External method synthesis

The redesign reused stable properties rather than vendor recipes:

- MovieLabs/software-defined production: preserve narrative-to-production relationships and make change consequences traceable.
- Controlled/platform experiment methods: predeclare hypotheses/variants/metric semantics and allow no-clear-winner outcomes.
- Current provider documentation: use dated evidence for legal operation combinations and lifecycle; do not treat vendor documentation as owner quality ranking.
- Timeline/editor interchange practice: exchange versioned relationships/metadata without moving business authority into the editor.

## Implemented architecture

Video 0.8 adds these owner-native bridges:

1. `editorial_planning.py` — `EpisodeIntent`, `ClaimSpec`, `BeatSpec`, `ShotIntent`, immutable `EditorialPlan`, evidence gates and explicit ShotContract materialization.
2. `plan_graph_bridge.py` — EditorialPlan versions become upstream MediaGraph assets so existing invalidation semantics stale only consuming descendants.
3. `continuity.py` — dimension-level `PRESERVE` / `EXPECT` / `ALLOW_CHANGE`, hard/soft rules and assessments.
4. `model_registry.py` — operation profiles, rubric/calibration-bound `QualityObservation`, uncertainty-aware floors, Pareto/non-dominated production selection and explicit priority resolution.
5. `experiments.py` — preregistered hypotheses, changed/fixed variables, metric semantics, guardrails, stop/observation rules and explicit inconclusive/no-clear-winner outcomes.
6. `editorial_interchange.py` — timeline/version/asset-digest/external-project-composition-bound handoff and roundtrip receipts.
7. `operator_view.py` — recomputable non-authoritative projection of outcome/focus/ready+blocked actions/stale evidence/risks/recovery; no promotion, mutation or controller authority.
8. `production_os.py` — ShotContract carries exact editorial plan/beat/claim/continuity/value lineage.

The historical/specialized work-order engine remains an explicit versioned 0.7 compatibility bundle. It was not falsely relabeled 0.8 because its contract did not change. System audit now validates internal adapter-bundle alignment and compatibility with the 0.8 core.

## Rejected alternatives and failed paths

- Documentation-only repair was rejected because the original failure was precisely that conceptual planning was not runtime state.
- A universal fixed sequence layer was rejected because representation must follow the concern.
- Keeping the hidden weighted quality utility while storing vectors was rejected because selection would still be scalar.
- Vendor-specific business-code branches were rejected because providers are volatile execution substrates.
- Making OperatorSnapshot canonical state was rejected because it would create a shadow controller.
- Forcing every experiment to isolate one variable was rejected; multivariate tests are allowed but cannot claim single-variable causality.

Candidate hardening also preserved several implementation failures rather than rewriting them out:
- CI `38722504017`: system audit passed, but 3 brittle legacy assertions treated old documentation phrases and an always-empty evolution list as architecture truth.
- CI `38723241908`: one remaining legacy literal assertion failed after the first repair.
- CI `38724742019`: system audit and 179 tests passed, but installed-package smoke still incorrectly required the unchanged 0.7 legacy adapter version to equal core package 0.8.0.

Those failures changed the architecture assurance itself: tests now assert semantic invariants, active evolution items are valid when they resolve to durable refs, and the legacy adapter bundle is explicitly versioned and audited rather than cosmetically relabeled.

## Final verification and promotion

Candidate PR: `#15`
Candidate head: `50bc4a74d7c641875c9625626d5c4634b97ba1fd`
Candidate CI: `38725408205` / #649 — PASS

Candidate gate passed:
- system hygiene audit;
- 180-test pytest suite including `tests/test_agent_operable_media_os_trajectory.py`;
- installed-package CLI smoke outside the repository.

Controlled production merge:
- production commit: `02d39d8e3609c6d988009f4bc5a7f5d0378128ec`;
- main production CI: `38725890405` / #650 — PASS;
- production CI passed system audit, full tests and installed-package smoke.

The end-to-end CURRENT_AGENT trajectory proves one episode can carry durable editorial intent/claim/beat/shot lineage through operation-specific routing, candidate admission, continuity assessment, promotion, MediaGraph lineage, timeline/editor roundtrip, experiment interpretation and later upstream invalidation without hidden state being the only connective tissue.

## Protected state / non-goals

- H1/A2 image editing was not executed or advanced.
- Accepted/rejected IP creative decisions were not changed.
- No provider became a permanent default or received an unevidenced quality ranking.
- Operator projection did not become authority.
- No external editor project was mutated during architecture dogfood.
- Future live published-episode growth/IP/commercial outcomes remain runtime observations; their absence does not reopen implementation completion.

## Result

`V-20261015-02-AGENT_OPERABLE_MEDIA_OS` is resolved. Video 0.8.0 is the verified production core. The current Agent now has durable creative-decision state, explicit continuity, condition-aware provider routing, editor roundtrip identity, preregistered experimentation, recomputable operating context and an end-to-end recovery/invalidation path, while preserving the existing Program/business/asset authorities and the 0.7 compatibility adapter bundle.
