# AI-Native Media Business OS

Status: `CANDIDATE_0_8_0`
Owner: `DOMAIN:video`
Date: `2026-10-15`
Parent behavior dependency: `UAOS COMMON_BEHAVIOR_ASSURANCE >= 1.2.0`
Architecture-experience dependency: `UAOS ARCHITECTURE_EXPERIENCE_POLICY >= 1.0.0`

## 1. Product definition

Video Growth Agent is one AI-native media business operating system. It must turn evidence about audience demand, editorial questions and distinctive IP into repeatable media, measurable growth, reusable rights/assets and commercial value without losing truth, provenance, continuity or recoverability.

The system optimizes a portfolio, not a clip:

`audience/problem evidence -> portfolio/series hypothesis -> editorial intent -> claims -> beats -> shots -> assets/takes -> timeline/platform variants -> audience/commercial outcomes -> experiments/learning -> revised portfolio/IP/production/commercial rules`

The four business workstreams remain ownership views, not silos:
- `MEDIA_GROWTH` — demand, packaging, audience evidence, series allocation;
- `ORIGINAL_DIGITAL_IP` — distinctive reusable identity/world/audio/visual assets and licensing value;
- `COMMERCIALIZATION` — sponsor/category fit, offers, rights, product-truth requirements and measurable brand/business outcomes;
- `PRODUCTION_SYSTEM` — editorial-plan realization into assets, shots, sequences, timelines, sound and delivery under quality/cost/provenance controls.

Their cross-effects are governed by `BUSINESS_FLYWHEEL.json`; none silently mutates another domain's canon or decision authority.

## 2. Governing objectives

Optimize the Pareto frontier across:
1. editorial truth and audience trust;
2. story/clarity/retention;
3. distinctive IP and recognition;
4. visual/audio craft and continuity;
5. sponsorability and reusable rights value;
6. cash cost and creator-hours per published minute;
7. iteration speed and recoverability;
8. platform fit and cross-platform reuse;
9. provenance, consent, rights and disclosure compliance;
10. durable learning rate.

No single proxy — views, CTR, cinematic quality, cheapest credits, highest model score or maximum AI-video percentage — may dominate the system.

## 3. Canonical objects and authority

### 3.1 Context

Creative/business hierarchy:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Platform variants remain derived contexts/edits rather than duplicated source truth.

### 3.2 Asset

Immutable/versioned media or business object with stable identity, digest, provenance, rights and acceptance state. Editorial plans, canon references, source documents, generated takes, real product assets, timelines, audio, diagrams, offers, thumbnails and outcome receipts can all be first-class assets.

No accepted original is destructively overwritten. A revision creates a new version and lineage.

### 3.3 Task

Bounded transformation/decision that consumes explicit context/assets/evidence and emits assets/evidence/decisions. Providers/editors are replaceable executors of tasks, not business authority.

### 3.4 Evidence

Evidence is typed and bound to the exact subject/action/artifact/provider/time. Declaration is not execution proof. Provider capability, price, availability, terms and quality evidence may expire.

### 3.5 Decision

Promotion, rejection, model route selection, sponsor acceptance and release are explicit decisions with owner, criteria and evidence. Producer completion is not approval.

### 3.6 Operator projection

`OperatorSnapshot` is a derived view for the current Agent: governing outcome, current focus, ready/blocked actions, stale evidence/assets, capability/budget risks and recovery refs.

It is **not** canonical business state and has no promotion/mutation/controller authority. It can always be rebuilt from owner authority.

## 4. Concern-driven views

The system does not privilege one architecture picture.

- ownership/dependency questions use authority/context/asset/dependency views;
- ordering/recovery/handoff questions use event/lifecycle/timeline views;
- route/product tradeoffs use Pareto/decision/quality-attribute evidence;
- Agent usability uses CURRENT_AGENT task/recovery walkthroughs.

Canonical dogfood scenarios: `docs/agent_operability_scenarios.md`.

## 5. Agent-operable editorial planning

The executable editorial path is:

`EpisodeIntent -> ClaimSpec -> BeatSpec -> ShotIntent -> ShotContract`

### EpisodeIntent

Captures:
- audience contract;
- editorial question;
- target platform/duration;
- source/research evidence;
- desired outcomes and metric semantics;
- relevant IP/commercial context and constraints.

### ClaimSpec

Separates fact, analysis, hypothesis, opinion and product truth. Factual/product-truth claims require evidence before they can justify downstream production.

### BeatSpec

States each beat's narrative job, audience function, claims, dependencies, timing and tension/transition job. Beat dependencies must remain acyclic.

### ShotIntent

States what a shot must achieve visually/editorially before choosing a model:
- visual job;
- truth/risk mode;
- source claims;
- allowed production modes;
- continuity dimensions;
- reference intents;
- must-show/must-avoid;
- multi-dimensional business/creative value.

### EditorialPlan

Plans are immutable/versioned. Revisions carry a reason and expose impacted claims/beats/shots. Each durable plan version becomes an `EDITORIAL_PLAN` asset in MediaGraph so downstream work can bind exact upstream intent and stale correctly after changes.

## 6. Production graph

Current primary graph:

1. `EpisodeIntent`
2. `ClaimSpec / evidence map`
3. `BeatSpec`
4. `ShotIntent`
5. `EditorialPlan asset/version`
6. `ShotContract + ReferenceBinding`
7. `ModelRoutingDecision / acquisition decision`
8. `CandidateTakes`
9. `ContinuityAssessment + quality/truth/rights evidence`
10. `TakePromotion`
11. `SequenceAssembly`
12. `MasterTimeline`
13. `SoundScene/Mix`
14. `Technical + Semantic QA`
15. `EditorialHandoff / RoundTrip` when external editing is used
16. `PlatformVariantPlan`
17. `ReleaseCandidate`
18. `ReleaseReceipt`
19. `Experiment/Performance/CommercialReceipt`
20. `LearningCandidate`

The legacy stage/work-order engine remains a historical/specialized compatibility adapter, not the current product ontology.

## 7. Shot contract and value

Every production `ShotContract` carries:
- stable shot/sequence identity;
- exact `editorial_plan_ref`, beat and source-claim IDs on the 0.8 path;
- narrative/visual job;
- duration and truth/risk class;
- allowed modes and required capabilities;
- multi-dimensional quality floors;
- multi-dimensional value vector;
- exact reference versions/digests/rights;
- must-have/must-not-have;
- continuity ref;
- budget/retry/degradation/stop conditions;
- disclosure/provenance requirements.

A high-value shot may justify premium spend; that does not remove hard truth/rights/budget gates.

## 8. Continuity state

Continuity is dimension-level relationship state, not one similarity score.

`ContinuitySnapshot` records relevant state per shot. `ContinuityLink` declares dimension-specific rules:
- `PRESERVE` — carry prior value;
- `EXPECT` — require a declared target;
- `ALLOW_CHANGE` — intentional variation.

Each rule is `HARD` or `SOFT`.

Examples of dimensions:
- face/body identity;
- wardrobe/prop state;
- world/location/time;
- camera geography;
- lighting/material grammar;
- voice/performance;
- product truth;
- narrative state.

Intentional change must not be mislabeled as drift. Hard continuity failures block promotion when relevant.

## 9. Provider/model evidence model

Providers/models are volatile execution substrates. Current facts are dated observations.

### OperationProfile

Capability is expressed as legal operation combinations, not only flat booleans. One model may expose multiple profiles for different:
- T2V/I2V/V2V/edit/extend modes;
- duration sets/ranges;
- resolutions/aspect constraints;
- image/video/audio reference budgets;
- required source origins or operation conditions;
- supported controls.

This prevents false inferences such as “the model supports reference images, 1080p and extension, therefore every combination of them is valid.”

### QualityObservation

Each quality dimension binds:
- value;
- rubric ID;
- calibration scope/benchmark pack;
- uncertainty;
- evidence class;
- evidence refs.

A number from a different rubric/calibration scope is not directly comparable merely because both are 0–5.

Official vendor documentation establishes current capabilities/limits/terms. It does not establish owner production-quality ranking.

## 10. Routing semantics

### Hard gates first

Current availability, deprecation, operation-profile legality, rights/terms, provenance when required, evidence freshness, quality floors and shot budget are hard gates.

### Exploration

Cheapest sufficient route after hard gates. Output remains candidate.

### Production

Quality is not collapsed into one hidden weighted average.

- compare calibrated uncertainty-aware quality lower bounds;
- form the non-dominated/Pareto front across relevant dimensions;
- if one candidate dominates, select it;
- if tradeoffs remain, use explicit shot/portfolio quality priority order;
- if no priority resolves a material tradeoff, surface the decision rather than fabricate a universal score.

Legacy scalar router remains a compatibility module only and is not exported as the current top-level routing API.

## 11. Candidate -> promotion -> release

`generation admission != asset promotion != release admission`

Candidate generation requires current legal/capability/right/budget/truth admission but not release-grade review. Candidate existence is learnable evidence, not acceptance.

Promotion requires evidence proportional to risk: artifact identity, quality, continuity, rights/truth, technical QA and independent/attested review where declared and executable.

Release remains fail-closed on final-media identity/digest, master timeline, QA, rights, claim/product truth, provenance, disclosure/platform validation and release owner.

No file becomes accepted by presence alone.

## 12. MediaGraph and change propagation

MediaGraph remains the single stable lineage/dependency substrate. Do not create a parallel “story graph” solely for 0.8.

Editorial-plan versions are registered as immutable upstream assets. Shot/tasks/generated assets bind exact plan/reference versions. When an upstream accepted plan/reference becomes stale or is superseded, existing downstream invalidation identifies affected work while preserving unaffected assets and historical versions.

## 13. Timeline and editor interchange

The internal master remains a non-destructive `TimelineSpec` referencing promoted asset versions.

External editors/NLEs are adapters, not authority.

`EditorialHandoff` binds:
- exact timeline ID/version;
- source asset refs/digests;
- interchange format;
- current adapter capability evidence;
- purpose;
- external project/composition identity where applicable.

`EditorialRoundTripReceipt` binds the returned artifact to the originating handoff/timeline/external project/composition and includes execution/change-summary evidence.

A returned edit becomes a new reviewed timeline/version; it never silently overwrites the master.

## 14. Audio

Audio is first-class and independently versionable: narrator/character voice canon, dialogue/performance, ambience, SFX, music, silence/dynamics, localization, timing/loudness QA.

Native audiovisual generation may improve coherence but does not erase independent rights/voice/music provenance or repairability.

## 15. Platform variants and experiments

Short-form derivatives are re-authored variants, not blind clips.

Each variant preserves source master lineage and declares hook promise, pacing/duration, packaging candidates, caption/safe-area/CTA and metric semantics.

Growth learning uses `ExperimentPlan` where material:
- hypothesis written before result interpretation;
- exact variants and changed/fixed variables;
- primary metric semantics and guardrails;
- minimum observation and stop rules;
- evidence refs.

`WINNER`, `NO_CLEAR_WINNER`, `INCONCLUSIVE` and `STOPPED_GUARDRAIL` are valid conclusions. A multivariable package test may be useful but cannot claim single-variable causality.

## 16. Business outcomes

Platform, production and commercial receipts remain separate evidence classes. No vanity aggregate score replaces the outcome vector.

Examples:
- impressions/exposure;
- watch-time/retention/completion with platform-specific semantics;
- follow/save/share/comment/returning-audience signals;
- qualified audience indicators;
- cash/credits/creator-minutes/retries/cost per accepted shot/published minute;
- sponsor revenue/gross margin/repeat purchase/brand result/rights reuse;
- IP recognition/distinctive-asset usefulness.

Unknown provider metrics remain unknown.

## 17. Commercialization and product truth

Commercial planning can start before production when rights, sponsor deliverables, exact product assets or measurement alter the episode.

Sponsor requirements enter through explicit CommercialFit/RightsPackage/Claim/Shot/Reference contracts. Sponsorship never overrides editorial/factual truth.

For factual products/real people/real events:
- do not synthesize evidence and present it as observed reality;
- bind verified source/brand assets to exact claims/shots;
- likeness/voice use requires rights/consent evidence;
- maintain provenance/C2PA/Content Credentials where available;
- release carries an explicit synthetic-content disclosure decision.

## 18. Economics

Track actual accepted-production economics, not just nominal model price:
- generation/input cost;
- retries/rejections;
- latency;
- creator/reviewer minutes;
- cost per accepted shot;
- cost per published minute;
- reuse count/value;
- marginal platform-variant cost;
- commercial revenue/gross margin.

Budget cuts are handled shot-by-shot from narrative/value/risk/degradation evidence, not a universal fixed premium percentage.

## 19. Learning and evolution

Production/business outcomes may emit learning candidates; durable rules require scoped evidence, counterexamples and replay/regression.

Learning hierarchy:
`take -> shot pattern -> episode/experiment -> series -> portfolio/domain rule`

Material problems preserve symptom -> diagnosis -> governing assumption challenge -> external method evidence -> alternatives/rejected paths -> repair -> verification -> uncertainty/follow-up.

Canonical evolution entrypoint: `audits/EVOLUTION_INDEX.json`.

## 20. CURRENT_AGENT operability

For material Video architecture/experience work, run the relevant scenarios in `docs/agent_operability_scenarios.md`.

The current Agent must be able to recover from durable evidence:
1. governing outcome;
2. current owner authority;
3. all ready actions, including legitimate parallel actions;
4. actual blockers and stale evidence/assets;
5. expected progress evidence;
6. recovery path after failure/session interruption;
7. comparable vs non-comparable quality evidence;
8. the distinction between user goals/constraints and illustrative examples.

`OperatorSnapshot` is the recomputable projection that helps make this legible; it never becomes a second controller.

## 21. Owner-native Common Behavior 1.2

Before asking the user for a plausibly recoverable Video dependency, inspect current authority/assets/decisions/receipts/connected context and useful external evidence. Continue provisionally when safe and label uncertainty.

A confirmed repairable Video system problem with available authority/capability cannot end as recommendation-only. It must resolve to `REPAIR_EXECUTED`, `BLOCKED_WITH_REASON`, or `NO_CHANGE_WITH_EVIDENCE`.

## 22. Non-goals

- no single-vendor production lock-in;
- no giant prompt as source of truth;
- no hidden scalar quality authority;
- no flat capability claim treated as proof of every operation combination;
- no destructive overwrite of accepted assets;
- no requirement that every shot be generative video;
- no requirement that every candidate pass release-grade review before existing;
- no operator projection as a second controller;
- no automatic mutation of external editor projects during architecture audit;
- no duplicated Video business truth in UAOS;
- no commercial optimization that overrides product truth or audience trust.

## 23. External method basis

Stable properties are adapted from, not copied wholesale from:
- MovieLabs Ontology for Media Creation / software-defined workflows: narrative-to-production relationships, Context/Task/Asset relationships, stable identifiers and change consequence propagation;
- OpenTimelineIO/editor interchange patterns: non-destructive timeline metadata and external media references;
- current video-provider documentation: conditional multimodal generation/edit/reference/extension capabilities and rapid model lifecycle;
- current platform experiment methods such as YouTube title/thumbnail tests: watch-time-aware evaluation and explicit no-clear-winner outcomes;
- C2PA/Content Credentials: provenance/disclosure metadata;
- current connected editor capabilities: real external project/composition identities and timeline export/roundtrip surfaces.

Provider features/prices remain volatile evidence in the registry. Architecture keeps business/editorial semantics stable while execution substrates change.
