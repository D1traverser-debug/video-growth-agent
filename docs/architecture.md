# Video Growth Agent — Architecture

Status: `CANDIDATE_0_7_0`
Owner: `DOMAIN:video`
Primary product architecture: `docs/media_business_os.md`

## 1. Topology

`UAOS common control/governance -> directly selected Video domain -> child-owned Media Business Program -> business/creative contexts -> tasks/work orders -> versioned assets/evidence/decisions -> platform/commercial outcomes -> learning`

UAOS does not own Video business IDs/state. Video does not implement a second parent controller.

## 2. Architectural center

The 0.7 architecture is object/context centered, not stage/role centered.

Primary context hierarchy:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Primary shared objects:

- `Asset` / version / lineage;
- `Task` / work order;
- `Evidence`;
- `Decision`;
- `Rights/Consent`;
- `Cost`;
- `PlatformVariant`;
- `PerformanceReceipt`;
- `CommercialOutcomeReceipt`;
- `LearningCandidate`.

Roles and providers execute or review tasks; they are not the source of business truth.

## 3. Business hierarchy

`DOMAIN:video` is the one user-facing Video owner.

`projects/PROJECT_INDEX.json` discovers child business projects/programs. The default Program `ai-self-media-commercialization` integrates:

- `MEDIA_GROWTH`;
- `ORIGINAL_DIGITAL_IP`;
- `COMMERCIALIZATION`;
- `PRODUCTION_SYSTEM`.

Their cross-effects are explicit in `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json`; no workstream keeps a private duplicate of authoritative assets/decisions consumed elsewhere.

## 4. Production architecture

The canonical conceptual path is:

`EpisodeIntent -> ClaimAndSourceMap -> BeatMap -> ShotPlan -> ReferenceBundle -> Generation/AcquisitionPlan -> CandidateTakes -> Promotion -> SequenceAssembly -> MasterTimeline -> Sound -> QA -> PlatformVariants -> Release -> Outcomes -> Learning`

The existing `workflow.json` / `execution-plan.json` stage machine remains a supported execution/compatibility adapter for historical/current episode operations. It no longer defines the entire product ontology.

## 5. Provider/model boundary

`video_growth_agent/model_registry.py` is the new evidence-bound provider-neutral routing layer.

Provider observations carry:

- current availability/deprecation;
- dated capability evidence;
- quality vector;
- reference budgets;
- duration/resolution constraints;
- commercial-use/provenance semantics;
- price evidence;
- evidence freshness.

Routing is driven by `ShotRoutingRequest`. Exploration selects cheapest sufficient execution after hard gates; production prioritizes shot-specific quality utility after hard gates.

Named providers are replaceable observations, not architecture.

## 6. Shot/asset state and promotion

`video_growth_agent/production_os.py` separates three boundaries:

1. candidate generation admission;
2. candidate/take promotion to accepted project asset;
3. release admission.

This prevents two opposite failure modes:

- a candidate cannot silently become accepted/final because a file exists;
- unavailable release-grade reviewers cannot prevent every safe low-risk exploration from producing learnable candidates.

High/HERO/brand-truth promotion requires risk-proportional independent evidence. Release always binds final media/timeline, technical QA, rights, truth, provenance, disclosure/platform validation and release owner.

## 7. Product-truth boundary

`PRODUCT_TRUTH` shots require verified real/authorized product-reference routing. Synthetic media may explain invisible mechanisms or clearly framed hypothetical/future concepts, but it cannot masquerade as observed evidence of exact product appearance/UI/material/configuration/behavior.

Truth/rights constraints travel with the shot and asset, not only a global compliance checklist.

## 8. Asset continuity / original IP

Canon is a versioned graph covering identity geometry, expressions, wardrobe/props, color/material/light, voice/performance, signature motion, world grammar, distinctive visual/audio assets, allowed variants and rights/likeness constraints.

Identity-sensitive shots bind exact canon versions. Upstream canon changes stale/invalidate only consuming descendants. Historical rejected variants remain evidence but are never active canon.

IP performance can consume growth/commercial evidence through the business flywheel; aesthetic approval alone does not prove distinctive-asset value.

## 9. Timeline/edit architecture

Master editorial state is non-destructive and timeline-oriented, conceptually compatible with OpenTimelineIO. Media assets remain externally referenced and lineage-bound. Generated extensions/replacements/retimes are derived assets rather than destructive overwrites.

Descript, Premiere, DaVinci and future NLE/agent editors are adapters. None owns project/business authority.

## 10. Audio architecture

Audio is a first-class scene/timeline asset system: narration/character voice, dialogue performance, ambience, SFX, music, silence/dynamics, localization and timing. Native audiovisual generation may emit an initial coherent sound scene, but reusable/rights-critical audio can be separated/versioned for repair and localization.

## 11. Platform variants

One master story may create multiple authored derivatives. Each `PlatformVariant` binds source episode/master timeline plus platform-specific hook, duration, ratio, packaging candidates and metric map.

Variants preserve lineage but may rewrite opening/pacing/conclusion; simple clip dumping is not the default.

## 12. Business measurement

`business_metrics.py` stores platform, production and commercial outcomes as separate evidence classes and derives interpretable economics such as cost/creator-minutes per published minute, rejection rate and commercial gross margin.

There is deliberately no universal composite score. Portfolio decisions must inspect the outcome vector and strategic context.

## 13. Program scheduling and orchestration

Existing `program_orchestration.py` continues to schedule explicit dependencies and parallel-ready work. The Program graph controls business-task readiness; shot/asset routing controls media execution.

These are different graphs:

- Program/business graph: why/when a business task is ready;
- production context/asset graph: what media/evidence it consumes/emits;
- editorial timeline: temporal assembly of promoted media.

Do not collapse them into one giant DAG.

## 14. Coordination semantics

The domain still supports:

- serial dependency;
- independent parallel;
- fan-out/fan-in;
- consultation;
- competitive candidates;
- structured critique/revision;
- owner adjudication;
- panel/quorum review.

Competition uses independently inspectable candidate artifacts and explicit decision evidence. Consultation is advisory. `peer_chat=false` remains an invariant.

## 15. Common Behavior 1.2

`owner_behavior_admission.py` realizes UAOS common behavior in Video:

- recover available project/asset/work-order/context/external evidence before externalizing a recoverable dependency;
- use safe bounded provisional continuation when possible;
- a detected repairable problem with available authority/tooling cannot terminate as recommendation-only.

The domain will expose `audits/EVOLUTION_INDEX.json` as the canonical evolution evidence entrypoint; deeper causal audits stay owner-native.

## 16. Assurance layers

- `DECLARED_ONLY`: configured/known only;
- `HARNESS_WIRED`: deterministic guard/runtime path exists;
- `SESSION_EXECUTABLE`: exact capability works in current session;
- `CHAT_BRIDGED`: bounded current-chat execution, not independent proof;
- `ATTESTED_ISOLATED`: isolated execution bound to provider/run/context/trace/artifact evidence.

Architecture claims never exceed available evidence.

## 17. Recovery/invalidation

Upstream asset/version changes retire active downstream authorization while preserving immutable history. Regenerated work receives new take/work-order identity as appropriate. Recovery restarts the earliest owning dependency, not the whole Program.

## 18. Negative space

Forbidden:

- provider/vendor lock-in as architecture;
- giant prompt/chat memory as canon;
- destructive overwrite of accepted assets;
- candidate presence treated as approval;
- every candidate forced through release-grade review before it can exist;
- self-approval;
- parent Video business-state mirrors;
- hidden dependency edges;
- unbounded peer chat;
- one vanity metric as global objective;
- sponsorship overriding product/editorial truth;
- AI-video percentage as a success metric by itself.
