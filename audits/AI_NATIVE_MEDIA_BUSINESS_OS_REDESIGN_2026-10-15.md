# AI-Native Media Business OS — Global Redesign Audit

Date: 2026-10-15
Status: `CANDIDATE_IMPLEMENTATION`
Owner: `DOMAIN:video`
Scope: full product/architecture reconsideration of AI-video production + media growth + original digital IP + commercialization.

## 1. User mandate

Treat the system as greenfield if necessary. Learn broadly before modifying durable architecture. Classify and compare evidence, challenge inherited assumptions, preserve current valid business progress, and do not stop at recommendations when a governed repair can be executed.

This audit is intentionally broader than a video-model comparison. The product is a media business system whose production technology, audience growth, IP, rights, monetization and learning loops interact.

## 2. Existing production baseline inspected

Production baseline before redesign:

- repository `D1traverser-debug/video-growth-agent` main `2f2e45eed9175499c86081d00c080e4e7cf9d11f`;
- package/runtime `0.6.0`;
- capability profile `7`;
- production CI run `38622448588` / #469 PASS;
- default Program `ai-self-media-commercialization`;
- four workstreams already co-located: `MEDIA_GROWTH`, `ORIGINAL_DIGITAL_IP`, `COMMERCIALIZATION`, `PRODUCTION_SYSTEM`;
- current foreground IP work remains H1 A2 upper-face tuning; redesign must not silently advance or overwrite it.

### Existing strengths retained

- one Video domain/business owner;
- project/program/workstream/subtask identity separation from UAOS;
- artifact-only specialist handoffs and explicit adjudication;
- immutable receipts and invalidation concepts;
- fail-closed release/rights/technical QA;
- session capability assurance taxonomy;
- cost-aware shot router concept;
- product-truth boundary;
- system audit and CI hygiene;
- parallel workstream graph.

### Existing weaknesses challenged

1. The conceptual center remained a long fixed `stage -> role -> review` workflow rather than media objects and contexts.
2. Model routing used one scalar measured-quality value and a small capability set, while current video systems expose heterogeneous reference/edit/audio/keyframe controls.
3. Quality-critical generation was over-coupled to isolated pre-generation review. `trusted_executors` was empty, so the highest-value generation path could remain mechanically unusable even when safe candidate exploration was possible.
4. The four business workstreams shared a Program but had too few explicit feedback edges; they behaved more like adjacent departments than one business flywheel.
5. Growth measurement was described but not represented as a stable provider-specific receipt ontology.
6. IP was strong on character geometry/canon work but weakly connected to measurable distinctive-asset, series-recognition and commercial-rights outcomes.
7. Commercialization was defined as a workstream but needed stronger upstream links into deliverables, verified product assets, rights packages and measurement before production.
8. Video had inherited Common Capabilities but had not yet owner-natively adopted UAOS Common Behavior Assurance 1.2 (recover-before-user-escalation + repair-or-block closure + canonical evolution entrypoint).
9. Current docs still treated the episode stage machine as the canonical center rather than a compatibility/specialized execution adapter.

## 3. External knowledge classes researched

### A. Current generative-video capability evolution

#### Seedance 2.5 — ByteDance Seed, 2026-07-31
Official evidence:
- https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
- https://seed.bytedance.com/en/seedance2_5

Observed properties:
- up to 30s per generation plus multi-round extension;
- up to 30 image, 10 video and 10 audio references;
- reference-driven subject/scene/style/prop control;
- timestamp-level editing, green-screen/perspective/reference editing;
- joint audio-video generation.

Architecture consequence: a modern shot is a multimodal reference/edit contract, not just prompt + first image.

#### Veo 3.1 — Google DeepMind / Google Cloud
Official evidence:
- https://deepmind.google/models/veo/
- Google Cloud current pricing/model documentation

Observed properties:
- character/scene/object references;
- style reference;
- first/last frame;
- extend;
- camera control;
- audio support;
- multiple speed/quality/cost tiers in current Cloud surfaces.

Architecture consequence: route on shot capability/risk/economics, not provider identity.

#### Runway platform / Gen-4.5
Official evidence:
- https://dev.runwayml.com/endpoints/image_to_video
- https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5

Observed properties:
- current developer surface exposes multiple video providers through common endpoints;
- Gen-4.5 emphasizes prompt adherence, motion/camera choreography and T2V/I2V;
- pricing is per generated second on current surface.

Architecture consequence: provider/model abstraction is practical today; capability registry can outlive vendors.

#### Kling / WAN via current Runway developer surface
Evidence:
- current `runwayml/v1` model surfaces expose Kling 3/O3 and WAN 3 families with native audio/reference/keyframe/edit features.

Architecture consequence: reference budgets, audio, keyframes and video-edit modes must be first-class routing dimensions.

#### Luma Ray3 Modify
Official evidence:
- https://lumalabs.ai/news/ray3-modify

Observed properties:
- video modification;
- keyframe and character reference controls;
- wardrobe/environment/relighting/product-placement use cases.

Architecture consequence: post-generation edit/modify is a normal production task; regeneration-from-zero must not be the default repair.

#### Sora lifecycle counterexample
Official evidence:
- OpenAI Sora discontinuation documentation (web/app stopped 2026-04-26; API stopped 2026-09-24).

Architecture consequence: no business rule may depend on a named provider/model remaining alive. Provider lifecycle/deprecation is routing evidence.

### B. Image/audio/editing production

#### Seed Audio 1.0 — 2026-07-20
Official evidence:
- https://seed.bytedance.com/en/blog/from-speech-to-audio-creation-introducing-the-seed-audio-1-0-audio-creation-model

Observed properties:
- scene-level speech/SFX/ambience generation;
- dialogue timing control;
- voice identity/performance consistency;
- multilingual generation.

Architecture consequence: audio is a scene asset system, not a late single-file voiceover step.

#### ElevenCreative Studio / Descript Underlord
Official evidence:
- ElevenLabs Studio documentation/current product surface;
- Descript 2026 Underlord documentation.

Observed properties:
- transcript/prompt-first editing plus timeline;
- voice/music/SFX/caption/media composition;
- agentic edit actions;
- export/interchange workflows.

Architecture consequence: editors are replaceable adapters over canonical asset/timeline state.

#### Adobe Firefly / Premiere
Official evidence:
- Adobe Firefly commercial-safety documentation;
- Premiere Generative Extend documentation (updated 2026-09).

Observed properties:
- commercially oriented training/licensing position;
- generative extension inside a non-linear edit;
- generated sections are labeled.

Architecture consequence: commercial-use/terms/provenance and editability belong in model/asset evidence, not assumptions.

### C. Professional media-pipeline architecture

#### MovieLabs 2030 Vision / Ontology for Media Creation
Official evidence:
- https://movielabs.com/the-2030-vision/
- https://movielabs.com/ontology-for-media-creation/
- https://movielabs.com/the-2030-vision-white-paper-section-3-3/

Borrowed stable properties:
- Task, Asset, Participant, Context and relationships as shared production concepts;
- stable identifiers;
- non-destructive workflows;
- interoperable common interfaces/data/metadata;
- tools/services should be swappable without rebuilding the whole pipeline;
- structured data enables automation.

#### OpenTimelineIO
Official evidence:
- https://opentimelineio.readthedocs.io/

Borrowed stable properties:
- timeline/track/clip/transition/marker metadata;
- media referenced externally rather than embedded as hidden editorial truth;
- interchange/adapters rather than editor lock-in.

Architecture consequence: Video OS should own canonical object/timeline metadata while Descript/Premiere/Resolve/etc. remain adapters.

### D. AI-video quality evaluation

#### VBench
Evidence:
- CVPR 2024 VBench paper and benchmark family.

Borrowed stable properties:
- temporal quality is separable into subject consistency, background consistency, flicker/dynamics etc.;
- frame-level quality is distinct from temporal quality.

Architecture consequence: remove the idea that one `measured_quality` score is sufficient for production routing.

### E. Growth, creator effectiveness and brand/IP

#### Kantar Marketing Trends 2026 / distinctive assets
Official evidence:
- Kantar Marketing Trends 2026;
- Kantar distinctive brand-assets material.

Observed properties:
- creator investment is rising but business/brand effectiveness matters more than vanity metrics;
- coherent cross-channel ideas and long-term creative platforms matter;
- distinctive assets act as recognition shortcuts and should be deliberately built/measured.

Architecture consequence:
- IP is a measurable distinctive-asset system, not only a character-modeling project;
- growth, IP and commercial strategy share a long-term creative platform.

#### IAB creator-economy measurement 2026
Official evidence:
- https://www.iab.com/guidelines/creator-economy-as-is-measurement-landscape/
- IAB 2025 Creator Economy Ad Spend & Strategy report.

Observed properties:
- creator spend is material and measurement remains fragmented;
- enterprise spend needs better pricing, verification and outcome measurement.

Architecture consequence: commercial receipts need rights, cost, outcome and repeat-buy evidence, not view counts alone.

### F. Platform metrics/disclosure/provenance

#### YouTube synthetic-content disclosure
Official evidence:
- https://support.google.com/youtube/answer/14328491
- YouTube 2026 disclosure updates.

Observed properties:
- realistic materially AI-generated/altered content may require disclosure;
- disclosure itself does not inherently remove monetization eligibility;
- C2PA metadata may propagate disclosure.

#### C2PA / Adobe Content Credentials
Official evidence:
- Adobe Content Credentials documentation;
- C2PA ecosystem.

Architecture consequence: disclosure/provenance is release metadata and lineage evidence.

#### Platform analytics
Stable design rule:
- Bilibili, Douyin, Xiaohongshu, WeChat Channels, YouTube expose different metric names/windows;
- provider-specific metrics must map into an internal ontology with explicit semantics;
- unsupported/unavailable metrics remain unknown rather than inferred.

## 4. Governing assumptions rejected

1. Rejected: the best architecture is a fixed linear pipeline because filmmaking is staged.
   - Reason: production stages exist, but modern AI work repeatedly loops at shot/asset level and independent business workstreams progress concurrently.

2. Rejected: more reviewer roles automatically means higher quality.
   - Reason: roles without real independent execution are declarative; over-gating can block learning and output.

3. Rejected: every quality-critical candidate must have release-grade independent review before generation.
   - Reason: exploration must be able to produce bounded candidates; fail-closed belongs at promotion/release boundaries proportional to risk.

4. Rejected: one quality number is sufficient for engine choice.
   - Reason: identity consistency, motion, prompt adherence, physics, camera, audio, editability and truth have different importance per shot.

5. Rejected: the best current model should be the system default forever.
   - Reason: capabilities/prices/provider lifecycle are volatile; Sora discontinuation is a direct counterexample.

6. Rejected: IP is a cosmetic layer after content strategy.
   - Reason: distinctive assets influence recognition, series memory, packaging, reusable rights and sponsor value.

7. Rejected: commercialization begins after audience growth.
   - Reason: rights, product-truth media, custom deliverables and measurement requirements can change production design; editorial conclusions remain independent.

8. Rejected: growth equals views.
   - Reason: retention, qualified audience, conversion, saves/shares, repeat viewing, brand outcomes and economics carry different information.

9. Rejected: cross-platform means clipping one master into shorter lengths.
   - Reason: packaging, opening, pacing and conclusion must be re-authored for each consumption context while preserving lineage.

10. Rejected: AI-video share should be maximized.
    - Reason: information graphics, verified real footage, still-motion, programmatic graphics and reused assets often explain better and cost less.

## 5. Selected product architecture

Selected architecture: `AI_NATIVE_MEDIA_BUSINESS_OS_0_7`.

Core hierarchy:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Cross-cutting object classes:

`Asset / Task / Evidence / Decision / Rights / Cost / PlatformVariant / PerformanceReceipt / LearningCandidate`.

Business loops are durable in `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json`.

Production semantics are durable in `docs/media_business_os.md` and executable modules:

- `video_growth_agent/model_registry.py`;
- `video_growth_agent/production_os.py`;
- `video_growth_agent/business_metrics.py`;
- `video_growth_agent/owner_behavior_admission.py`.

## 6. Migration strategy

Do not erase proven 0.6 mechanisms merely because the conceptual center changes.

Retain as compatibility/support surfaces:
- current `workflow.json` and execution-plan for historical episode projects;
- existing work-order/attestation/runtime/QA mechanisms;
- project-store immutable receipts;
- current H1/IP progress;
- program orchestration graph;
- historical audits/rejected evidence.

Promote the new object/shot/business architecture as the primary conceptual authority, then migrate execution paths incrementally behind tests. This avoids a big-bang deletion that destroys validated recovery semantics.

## 7. Candidate acceptance criteria

1. Existing system audit remains green; old hard gates are not weakened for historical paths.
2. Existing pytest remains green.
3. New model-registry tests prove current evidence, deprecation, reference budgets, commercial terms and quality vectors affect routing.
4. New production tests prove candidate generation != promotion != release.
5. Product-truth cannot be satisfied by an unverified synthetic route.
6. High-risk/HERO promotion requires independent review evidence; low-risk exploration can proceed without unavailable release-grade reviewer infrastructure.
7. New business metrics remain vector-valued and do not collapse into one vanity score.
8. Video Common Behavior 1.2 behavior is trajectory-tested: recover before asking user; repair-or-block closure.
9. New evolution entrypoint exposes the redesign and deeper causal audit.
10. Package/install smoke proves new public modules ship.
11. Candidate CI then production CI must pass before parent UAOS observation is refreshed.

## 8. Remaining assurance boundary before promotion

This candidate can mechanically verify architecture, routing semantics, admissions and package integrity. It cannot by itself prove one specific provider will outperform another on the user's real content, nor can it prove live account growth/sponsor outcomes before real episodes exist.

Therefore provider quality observations remain dated/replaceable and the post-promotion business assurance ceiling will be:

`EXECUTABLE_MEDIA_BUSINESS_OS_AND_TRAJECTORY_VERIFIED__LIVE_EPISODE_GROWTH_IP_COMMERCIAL_OUTCOME_OBSERVATION_OPEN`.
