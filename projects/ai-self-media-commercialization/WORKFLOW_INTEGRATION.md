# Workflow Integration — Media Business Program

Current product architecture: `../../docs/media_business_os.md`  
Current Program flywheel: `BUSINESS_FLYWHEEL.json`

## Purpose

`ai-self-media-commercialization` is the default integrated Video-domain Media Business Program for growth, commercialization, original digital IP and reusable audiovisual production capability.

It is a Video-owned Program governed externally by CAOS; it has no CAOS runtime/API dependency and does not inherit a parent task identity. Pilot 001/002 remain separate historical child projects; rejected/process-invalid Pilot evidence never becomes accepted Program input by proximity.

## Workstream ownership

### MEDIA_GROWTH
Owns positioning, audience/problem hypotheses, topic/series portfolio, packaging/distribution experiments, platform receipts and growth learning.

### ORIGINAL_DIGITAL_IP
IPOS (IP Studio OS) externally owns creative identity, character canon, avatar, approved visual/voice/performance assets and identity rights. The Video workstream owns video-specific usage plans, recognition hypotheses, performance observations and production requirements. It cannot create or mutate the IPOS canon; it sends evidence-bearing learning candidates back to IPOS.

### COMMERCIALIZATION
Owns advertiser/category mapping, commercial-fit evidence, native integration constraints, offers/pricing/rights packages, measurement and repeat-buy learning.

### PRODUCTION_SYSTEM
Owns provider-neutral shot/reference/take execution, asset lineage/promotion, timeline/audio/QA/release, cost/runtime evidence and validated production methods.

## Business flywheel

The workstreams are not merely parallel. `BUSINESS_FLYWHEEL.json` defines explicit evidence/decision loops such as:

- audience/performance -> portfolio/series decisions;
- portfolio/series -> IP/distinctive-asset plan;
- promoted IP -> packaging/recognition hypotheses and production references;
- portfolio/audience -> advertiser/commercial-fit candidates;
- commercial deliverables/rights/product truth -> production requirements;
- production cost/retry/reuse -> future format/portfolio investment;
- platform/IP/commercial/production outcomes -> bounded evolution candidates.

Cross-workstream influence never means hidden prompt context or authority duplication. Consumers reference exact authoritative assets/decisions/evidence.

## Program orchestration

`SUBTASK_GRAPH.json` remains the current business-task dependency authority:

- independent work may proceed in parallel;
- declared dependency edges block only affected nodes;
- advisory consultation does not decide;
- competing candidates require explicit criteria and owner adjudication;
- negotiation uses bounded artifact rounds;
- project/program outputs become accepted assets only through explicit promotion.

The business Program graph is not the editorial timeline and not the media asset graph. These are linked but distinct structures.

## Media production integration

The primary 0.7 conceptual production path is:

`EpisodeIntent -> ClaimAndSourceMap -> BeatMap -> ShotPlan -> ReferenceBundle -> Generation/AcquisitionPlan -> CandidateTakes -> TakePromotion -> SequenceAssembly -> MasterTimeline -> Sound -> QA -> PlatformVariants -> Release -> Outcomes -> Learning`.

The historical `workflow.json` / `execution-plan.json` stage machine remains a supported execution adapter for current/historical episode operations.

### Candidate generation

Can proceed when the exact shot/reference/provider/rights/truth/budget admission passes. Candidate output does not create acceptance.

For non-character information shots, `PROGRAMMATIC_GRAPHICS` is a locally executable FFmpeg route for title/quote cards, metrics and bar charts. It is explicitly synthetic, requires the exact ShotContract/EditorialPlan/beat and source-claim bindings, and emits a silent candidate plus technical receipt. With an existing MediaGraph SHOT context it registers a CANDIDATE AssetVersion; it never promotes or releases. It is not a substitute for cinematic AI video, factual product imagery, IPOS canon, or final sound.

### Asset promotion

Requires exact artifact identity/digest, shot-specific quality evidence, continuity/truth/rights evidence and risk-proportional independent review.

### Release

Requires final-media/timeline identity, technical QA, rights, claim/product truth, provenance, disclosure/platform validation and release-owner evidence.

## Current parallelism

Current IPOS R39 G1 research and non-character Video work may run in parallel with:

- growth baseline / pilot-topic hypothesis work;
- advertiser mapping / commercial-fit research;
- provider benchmark/system research that does not claim a new provider production ranking without owner benchmark evidence.

Character canon blocks only identity-dependent outputs. It does not block unrelated topic/audience/commercial/provider-method work.

## Original-IP authority and IPOS video bridge

IP Studio OS (IPOS) is the sole creative authority for the creator's character identity, avatar, approved visual canon, voice/performance canon, and reusable identity assets. IPOS is an independent system and must be able to complete research, design, rendering, QA, correction, versioning, and export without invoking CAOS or requiring a CAOS runtime/API/session.

The Video system does not maintain a competing character bible or reconstruct canon from old prompts. It consumes a portable IPOS Video Identity Bundle (schema_version: 1.0) through video_growth_agent.ip_identity. The bundle carries owner approval, gate evidence, exact asset versions/digests, rights/provenance, video-use permission, identity invariants, forbidden drift, and continuity dimensions/rules.

Import is fail-closed for identity-dependent shots: owner approval, G2/G7/G8 PASS, video-use permission, promoted visual references, rights, and provenance must all be present. The imported bundle and assets are registered in MediaGraph as immutable assets with IPOS retained as external decision authority. Each identity-dependent ShotContract binds the exact bundle, approval and reference versions. The adapter never promotes an unapproved concept or an image merely because it exists.

A canon update creates a new version. Only descendants that consumed the superseded IPOS version are invalidated; unrelated shots and workstreams remain intact. If no approved bundle is available, character-identity shots are blocked, while non-character production and independent research continue.

The current IPOS R39 state is authoritative: no character carrier or identity anchor is approved; G1 research remains open and G2 concept competition has not started. The previous Video-local H1/S1+S3/A2 face-shell route is historical and superseded. It must not be resumed or used as a reference. No approved bundle is available for import yet.

IP learning may consume recognition/growth/commercial evidence, but performance signals do not directly rewrite IPOS canon. Proposed canon changes are sent back to IPOS as evidence-bearing learning candidates; only IPOS and the owner approval process can change the authoritative identity.

## Commercial integration

Commercialization can affect production before an episode is finished when it changes:

- required verified product assets;
- integration surface/timing;
- platform deliverables/cutdowns;
- licensing/paid-media/territory/exclusivity rights;
- production complexity;
- measurement plan.

It may not override factual/editorial conclusions, product truth, audience trust, rights or hard QA.

## Platform variants

A platform variant is derived from the master story/asset graph but owns its hook, packaging, pacing, duration, aspect, CTA/experiment and metric semantics. Douyin/XHS/Channels variants are re-authored; they are not automatic excerpts of the Bilibili master.

## Performance / Learn

Performance feeds the Program as typed evidence:

- provider-specific platform metrics with declared semantics;
- production economics/retry/reuse;
- IP/distinctive-asset signals;
- commercial revenue/gross-margin/brand/repeat-buy outcomes when available;
- qualitative audience/business evidence.

These remain separate evidence classes. One episode does not automatically rewrite global technique, canon, provider ranking, offer pricing or Program policy.

## Non-interference

This Program must not:

- rewrite Pilot 001/002 state except through explicit project maintenance/resume;
- use rejected Pilot candidates as accepted evidence;
- weaken historical strict runtime gates to make old paths pass;
- force release-grade review onto every safe candidate experiment;
- auto-promote local preferences or vendor demos into production rules;
- create a repository-local parent controller or mirror CAOS governance task identities;
- optimize one vanity metric as the global business objective.
