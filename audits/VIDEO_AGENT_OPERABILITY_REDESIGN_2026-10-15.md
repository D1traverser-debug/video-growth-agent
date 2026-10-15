# Video Agent Operability Redesign — 2026-10-15

Status: `CANDIDATE_EVALUATION`
Owner: `DOMAIN:video`
Evolution ID: `V-20261015-02-AGENT_OPERABLE_MEDIA_OS`
Parent method: UAOS Architecture Experience Evaluation 1.0 + Common Behavior Assurance 1.2

## Trigger

User asked for Video architecture to be evaluated from lived use, not merely static framework completeness, and explicitly permitted using all relevant previously learned skills/methods. User examples such as spatial frameworks and sequence construction were treated as hints, not binding architecture requirements.

## Governing outcome

Make Video an AI-native media business operating system that a current Agent can actually understand, operate, recover and evolve across editorial planning, production, original IP, growth and commercialization without reconstructing key state in hidden chat memory.

## Baseline

Production baseline before this redesign:
- Video 0.7.0 / Profile 8;
- main `55f605e641671a513637ffb03b532c66335a2ad9`;
- production CI #565 PASS;
- H1/A2 creative cursor preserved and outside this maintenance scope.

0.7 correctly established:
- stable MediaGraph context/assets/evidence/decisions/tasks;
- ShotContract/Take candidate->promotion->release separation;
- non-destructive TimelineSpec;
- typed business/commercial objects;
- provider-neutral routing intent;
- vector business outcome receipts;
- Business Flywheel across growth/IP/commercial/production;
- owner-native Common Behavior admission and evolution evidence.

## CURRENT_AGENT dogfood

The current Agent walked the system as if executing ten real scenarios rather than reading module names only:
1. natural-language topic -> executable episode;
2. digital-IP continuity across shots;
3. upstream claim/plan change after paid generation;
4. provider/model deprecation or capability-combination change;
5. budget cut mid-production;
6. sponsor enters after planning starts;
7. external editor/NLE handoff and roundtrip;
8. long-form master -> authored short-form derivatives;
9. session interruption/resume;
10. published audience/business outcome -> learning/evolution.

Detailed walkthrough authority: `docs/agent_operability_scenarios.md`.

## Observed gaps

### G1 — Editorial decision bridge existed in documentation, not runtime

`docs/media_business_os.md` described:
`EpisodeIntent -> ClaimAndSourceMap -> BeatMap -> ShotPlan -> ...`

but current runtime began materially at `ShotContract`. The current Agent therefore had to keep audience contract, claims, argument order, beat function and shot-to-claim traceability in its own working memory.

Consequence: generated media could be technically well governed while the editorial reasoning that justified the shots remained under-specified and hard to recover.

### G2 — Cross-shot continuity remained too implicit

Asset identity/versioning existed, but “what must remain the same between these two shots?” remained distributed across canon, references and review judgment. A vague single continuity score cannot distinguish hard identity preservation from intentional changes in location, wardrobe, lighting or time.

### G3 — Model router re-collapsed a quality vector into a scalar

`model_registry.py` stored dimensional quality scores but production selection computed a hidden weighted-average `quality_utility` and sorted on it. This recreated the failure mode the architecture explicitly tried to avoid: non-substitutable identity/motion/camera/audio/editability tradeoffs could be erased by one arithmetic average.

It also allowed numeric comparisons without proving the scores came from the same rubric/calibration scope.

### G4 — Provider capabilities were flat when real APIs are conditional

Current provider documentation shows combinations matter. Example: modern video APIs may constrain reference images, duration, resolution, extension source/origin and other modes jointly. A flat set such as `IMAGE_REFERENCES + 1080P + EXTEND` does not prove the requested combination is legal.

Selected external evidence:
- Google/Veo current official documentation for operation/duration/resolution/reference constraints;
- Runway current API changelog as evidence of rapid model lifecycle/capability changes.

Architecture implication: provider facts belong in dated operation profiles, not business-code conditionals or permanent vendor branches.

### G5 — Timeline existed, editor handoff identity did not

`TimelineSpec` handled internal non-destructive assembly but had no first-class contract for external editor project/composition identity, exported interchange version, source asset digests or roundtrip receipt.

CURRENT_AGENT read-only dogfood against the connected Descript environment found real prior Pilot 001/002 projects, compositions and published artifacts. That confirmed that external project/composition identity is operationally material; “sent to editor” is not sufficient state.

No external project was mutated during this audit.

### G6 — Growth learning lacked preregistered experiment semantics

Business outcomes correctly remained a vector, but there was no typed object forcing hypothesis, changed variables, metric semantics, guardrails, observation/stop rule and `NO_CLEAR_WINNER`/`INCONCLUSIVE` outcomes to exist before interpretation.

External method evidence:
- current YouTube title/thumbnail testing explicitly optimizes overall watch time rather than CTR alone and may return no clear winner;
- controlled experiment methods distinguish single-variable attribution from multi-variable package tests.

### G7 — Current Agent had authority files, but no compact derived operating projection

A resumed Agent can read Program state, subtask graph, project progress, capability evidence and stale assets, but it still has to mentally synthesize “what outcomes matter, what actions are actually ready in parallel, what is blocked, what is stale, what evidence proves progress, where do I recover?”

A new controller would be wrong. The missing artifact is a derived, non-authoritative operator projection.

### G8 — Production/cost method authority drift

`projects/ai-self-media-commercialization/PRODUCTION_AND_COST_STRATEGY.md` still declared `CANDIDATE_MEDIA_BUSINESS_OS_0_7` although 0.7 was already production. `docs/provider_benchmark_protocol.md` similarly labeled the method `CANDIDATE_1.0` even though current architecture depended on it. This can mislead recovery Agents even when runtime is correct.

## Governing assumptions challenged

1. **“If low-level media objects are executable, the Agent can reconstruct editorial planning.”** Rejected. Hidden reconstruction creates recovery and traceability risk.
2. **“A multidimensional score remains multidimensional if only storage is vectorized.”** Rejected. Selection semantics also must remain vector-aware.
3. **“A provider capability can be represented as a boolean feature set.”** Rejected for conditional combinations.
4. **“Internal timeline lineage is enough; external editor state is operational detail.”** Rejected by real connected-editor dogfood.
5. **“Post-publication metrics are enough to learn.”** Rejected when hypotheses/metric semantics are defined after results.
6. **“One global next action simplifies operation.”** Rejected because the integrated Program intentionally supports parallel ready workstreams.
7. **“Adding a universal sequence layer would solve lived-operability.”** Rejected. Representation must follow the concern; sequence/timeline is useful for temporal concerns but not sufficient for authority, causal tradeoffs or cognitive use.

## External method synthesis

### MovieLabs OMC / software-defined production

Useful principle retained:
- Narrative information should connect to Production elements rather than disappear before production;
- Context, Task, Asset and Participant relationships make dependencies and consequences of change explicit;
- upstream narrative changes can propagate to affected downstream production work.

Adaptation here:
- use Video's existing MediaGraph instead of copying MovieLabs ontology wholesale;
- add editorial-plan versions as first-class upstream assets and bind production outputs to exact versions.

### Platform experiment methods

Useful principle retained:
- predeclare measurable hypotheses/variants/metric semantics;
- allow inconclusive/no-clear-winner results;
- avoid treating CTR or one vanity metric as the sole objective.

### Provider documentation

Useful principle retained:
- official docs establish current capability/limits/terms, not owner production-quality ranking;
- conditional combinations and provider lifecycle must be represented explicitly;
- quality remains owner benchmark evidence.

### Editor interchange

Useful principle retained:
- timeline interchange is metadata/relationship exchange, not media-authority duplication;
- external adapter capability must be current-session evidence, not repository declaration alone.

## Candidate architecture

Selected six bridges:

1. `editorial_planning.py`
   - `EpisodeIntent`, `ClaimSpec`, `BeatSpec`, `ShotIntent`, immutable `EditorialPlan`;
   - fact/product-truth evidence gates, beat DAG, shot traceability;
   - explicit materialization into `ShotContract`.

2. `continuity.py`
   - dimension-level hard/soft preserve/expect/allow-change rules;
   - continuity becomes explicit relationship evidence, not one vague score.

3. `model_registry.py` 0.8 semantics
   - `OperationProfile` models legal capability combinations;
   - `QualityObservation` binds score, rubric, calibration scope, uncertainty, evidence class/refs;
   - hard floors use uncertainty-aware lower bounds;
   - production forms a Pareto front and uses explicit priorities rather than hidden weighted averages.

4. `experiments.py`
   - preregistered hypotheses, changed/fixed variables, metric semantics, guardrails, observation/stop rules;
   - single-variable causal attribution is mechanically rejected when multiple variables change;
   - no-clear-winner/inconclusive are first-class outcomes.

5. `editorial_interchange.py`
   - exact internal timeline version, asset refs/digests, adapter capability, external project/composition identity and roundtrip receipt.

6. `operator_view.py`
   - derived governing outcome/current focus/ready+blocked actions/stale evidence/budget/capability/recovery projection;
   - explicitly no promotion/mutation/controller authority.

Supporting bridge:
- `plan_graph_bridge.py` registers immutable editorial-plan versions as MediaGraph assets so existing downstream invalidation mechanics can be reused rather than creating another dependency graph.

## Rejected alternatives

### R1 — Documentation-only repair
Rejected because the original gap was specifically that documentation described intent/beat/shot concepts but runtime did not preserve them.

### R2 — Universal fixed sequence/workflow layer
Rejected because the user's mention of sequence was illustrative and because structural, temporal, causal and cognitive concerns need different views.

### R3 — Keep weighted quality utility but store vectors alongside it
Rejected because the actual selection decision would remain scalar even if the database looked multidimensional.

### R4 — Vendor-specific provider subclasses in business code
Rejected because provider APIs/pricing/lifecycles change quickly and would couple business architecture to vendors.

### R5 — Make OperatorSnapshot a new canonical state/controller
Rejected because it would create a shadow authority. It is a recomputable projection only.

### R6 — Force every growth test to isolate exactly one variable
Rejected. Package/creative multivariate tests are useful; they simply cannot claim single-variable causal attribution.

## Verification trajectory so far

- candidate branch created from verified production main before material writes;
- runtime/test candidate opened as PR #15;
- first full candidate CI #589 passed system hygiene audit, full pytest and installed CLI smoke test;
- full architecture/profile/version/system-audit reconciliation is still pending and therefore this evolution remains candidate/open.

## Non-goals / protected state

- do not execute H1/A2 image editing during system maintenance;
- do not change accepted/rejected IP creative decisions;
- do not make any provider a permanent default;
- do not claim owner quality rankings before benchmarks exist;
- do not convert the operator projection into a second business authority;
- do not auto-publish or mutate external editor projects as part of architecture dogfood.

## Next candidate checks

1. update system audit to fail closed if 0.8 current surfaces disappear;
2. update product/architecture/Skill/Manifest/Capabilities/runtime version coherently;
3. add scenario-level trajectory tests across editorial plan -> production -> graph invalidation -> operator recovery;
4. rerun full CI on latest head;
5. reverse-audit docs vs runtime for residual 0.7/candidate authority drift;
6. only then promote through controlled merge + production CI + closure evidence + UAOS parent observation refresh.
