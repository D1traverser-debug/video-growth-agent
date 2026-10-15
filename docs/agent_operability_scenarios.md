# Video Agent Operability Scenarios — 0.8 Candidate

Status: `CANDIDATE_0_8`
Owner: `DOMAIN:video`
Parent method: `UAOS config/ARCHITECTURE_EXPERIENCE_POLICY.json`

## Purpose

This is an architecture-experience test surface, not a second workflow controller. It is the owner-native `CURRENT_AGENT` dogfood acceptance surface required for material Video architecture and Agent-experience changes.

The Video system is considered operable only when a current Agent can recover the governing goal, discover current authority, choose a valid next action, observe progress, diagnose failure, and resume without relying on hidden chat memory. User examples are evidence/hints unless explicitly locked as requirements.

Representations are selected by concern:
- structural ownership/dependency -> authority/context/asset/dependency views;
- ordering/recovery/handoff -> lifecycle/event/timeline views;
- why one option wins -> tradeoff/causal/quality-attribute evidence;
- whether an Agent can actually use the system -> task/cognitive/recovery walkthrough.

No diagram family is mandatory by itself.

## Scenario 1 — Natural-language idea to executable episode

**Actor goal:** turn “做一期为什么AI推理正在往端侧走” into a production-ready episode without inventing claims or jumping straight to prompts.

Expected path:
`EpisodeIntent -> ClaimSpec -> BeatSpec -> ShotIntent -> ShotContract`.

Progress evidence:
- audience contract and editorial question exist;
- factual/product-truth claims carry evidence;
- every beat has a production expression;
- every production ShotContract binds the editorial plan version/beat/claim lineage.

Failure modes:
- topic becomes a shot list with no argument;
- factual claim has no evidence;
- current Agent has to remember which shot supports which claim.

Recovery:
- reopen the editorial plan, not generated prompts;
- revise the plan immutably and inspect impacted claims/beats/shots;
- stale downstream assets through MediaGraph lineage when the old plan changes materially.

## Scenario 2 — Digital IP across multiple shots

**Actor goal:** preserve only the continuity dimensions that matter while allowing intentional variation.

Expected path:
`Canon/ref assets -> ContinuitySnapshot -> ContinuityLink/Rule -> Take review`.

Progress evidence:
- hard vs soft continuity dimensions are explicit;
- intentional time/location/wardrobe changes are not mislabeled as drift;
- identity or other hard preservation failures are observable before promotion.

Failure modes:
- “same character” is treated as one vague score;
- every visual difference becomes an error;
- continuity is judged from memory rather than state.

Recovery:
- inspect dimension-level violations and reference/canon evidence;
- regenerate/edit only the affected shot or dimension where possible.

## Scenario 3 — Upstream research/claim/plan changes after generation

**Actor goal:** know which paid/generated work became stale.

Expected path:
- each editorial plan version is a first-class `EDITORIAL_PLAN` asset in MediaGraph;
- production assets/tasks bind exact upstream plan/reference versions;
- invalidation propagates through existing MediaGraph lineage.

Progress evidence:
- old versions remain auditable;
- affected downstream assets become `STALE` rather than silently remaining current.

Failure mode:
- Agent manually searches filenames/prompts to guess what to redo.

Recovery:
- follow graph invalidation closure; preserve unaffected work.

## Scenario 4 — Provider/model deprecation, API change or capability combination change

**Actor goal:** reroute without rewriting the business architecture or assuming a flat “model supports X” boolean.

Expected path:
`dated ModelObservation -> OperationProfile -> calibrated QualityObservation -> ShotRoutingRequest -> Pareto/priority decision`.

Progress evidence:
- operation-specific duration/resolution/reference/source constraints are checked;
- stale/deprecated observations fail closed;
- production quality comparisons use the same rubric/calibration scope;
- no hidden weighted-average decides a multidimensional production tradeoff.

Failure modes:
- 1080p/reference/extension combination is assumed legal because each feature exists separately;
- self-evaluation score from one rubric numerically beats owner benchmark score from another;
- cheapest/most fashionable vendor becomes default doctrine.

Recovery:
- refresh exact provider observation/benchmark;
- use declared graceful degradation or block the affected shot only.

## Scenario 5 — Budget is cut mid-production

**Actor goal:** reduce spend without globally lowering quality or destroying the episode thesis.

Required views:
- ShotIntent value vector and narrative job;
- ShotContract risk/quality floors/graceful degradation;
- accepted-take cost/retry evidence;
- operator budget risks.

Progress evidence:
- information/support shots can degrade differently from hero/product-truth shots;
- reductions preserve hard truth, rights and continuity constraints;
- decision cites accepted-take economics, not only nominal provider $/second.

Failure mode:
- one fixed “premium-video percentage” is applied to every episode.

Recovery:
- reroute scoped shots using their declared degradation paths and current model evidence.

## Scenario 6 — Sponsor enters after editorial planning started

**Actor goal:** integrate commercial requirements without silently rewriting editorial truth.

Expected path:
`CommercialFit/RightsPackage -> affected ClaimSpec/ShotIntent/ReferenceBinding -> revised EditorialPlan -> production impact`.

Progress evidence:
- exact product-truth claims bind verified brand/real references;
- rights/usage scope is explicit;
- unaffected editorial beats remain intact.

Failure mode:
- sponsorship is injected as an untracked mid-roll instruction or synthetic media impersonates factual product evidence.

Recovery:
- revise only affected claims/shots, invalidate downstream assets, and re-run truth/rights gates.

## Scenario 7 — External editor/NLE handoff and roundtrip

**Actor goal:** leave the internal timeline without losing exact source identity or returning edits to the wrong project/composition.

Expected path:
`TimelineSpec -> EditorialHandoff -> external project/composition -> EditorialRoundTripReceipt -> new timeline/version review`.

Progress evidence:
- exact timeline version, asset refs/digests, interchange format and external identities are bound;
- current-session adapter capability is evidenced;
- returned edit has execution and change-summary receipts.

Failure mode:
- “exported to editor” is treated as success with no way to know which project/version came back.

Recovery:
- reject mismatched roundtrip receipts; preserve old master and import returned edit as a new version.

## Scenario 8 — Long-form master becomes short-form variants

**Actor goal:** re-author hook/pacing/conclusion while preserving source lineage.

Expected path:
`MasterTimeline -> PlatformVariant contract -> derived TimelineSpec -> packaging experiment`.

Progress evidence:
- variant binds master version;
- new hook/packaging is explicit, not blind clipping;
- platform metrics use declared semantics.

Failure mode:
- short videos become arbitrary excerpts and results cannot teach the long-form system anything.

Recovery:
- treat derivative as a new authored variant with its own experiment/outcome receipt.

## Scenario 9 — Session interruption / new Agent resumes

**Actor goal:** continue correctly without hidden conversational memory.

Expected path:
`PROJECT_INDEX -> Program authority -> workstream state -> OperatorSnapshot/resume refs -> exact action authority`.

Progress evidence:
- operator projection shows governing outcome, current focus, all ready actions, blockers, stale evidence and recovery refs;
- the projection has no mutation/promotion authority of its own.

Failure modes:
- Agent assumes one global next action despite legitimate parallel work;
- old Pilot state or cached provider facts anchor the resumed session.

Recovery:
- reread owner authority and rebuild the projection from current records.

## Scenario 10 — Published results change future decisions

**Actor goal:** learn from audience/business outcomes without post-hoc storytelling.

Expected path:
`pre-registered ExperimentPlan -> platform/production/commercial receipts -> ExperimentConclusion -> scoped LearningCandidate -> replay/challenge -> durable rule if justified`.

Progress evidence:
- hypothesis, changed variables, metric semantics and stop/observation rules existed before interpretation;
- `NO_CLEAR_WINNER` and `INCONCLUSIVE` are valid outcomes;
- multi-variable tests cannot claim single-variable causality.

Failure mode:
- one viral episode becomes a universal rule after the fact.

Recovery:
- downgrade to observation/candidate, design a discriminating follow-up experiment, and keep durable policy unchanged until promotion evidence exists.

## Current-Agent acceptance criteria

A material Video architecture change is not complete merely because code/tests exist. For the concerns it changes, the current Agent must be able to answer from durable evidence:
1. What outcome am I serving?
2. What is authoritative right now?
3. What actions are currently valid, including parallel actions?
4. What evidence will show progress?
5. What could fail or become stale?
6. How do I recover without losing provenance or authority?
7. Which values are truly comparable and which are tradeoffs?
8. Did a user example remain a hint rather than silently becoming doctrine?
