# AI-Native Media Business OS

Status: `PRODUCTION_0_7_0`
Owner: `DOMAIN:video`
Date: `2026-10-15`
Parent behavior dependency: `UAOS COMMON_BEHAVIOR_ASSURANCE >= 1.2.0`

## 1. Product definition

Video Growth Agent is not a collection of disconnected AI-video, growth, IP-design and sponsorship utilities. It is one AI-native media business operating system whose job is to turn durable audience insight and distinctive intellectual property into repeatable, high-quality media, measurable audience growth and commercially valuable rights/inventory.

The system must optimize a portfolio, not a clip:

`audience/problem evidence -> content portfolio -> IP/brand assets -> episode/series intent -> production -> platform variants -> audience/commercial outcomes -> learning -> revised portfolio/IP/production/commercial rules`

The four existing business workstreams remain useful ownership views, but they are coupled by explicit evidence edges:

- `MEDIA_GROWTH` discovers demand, packaging and audience response, then feeds topic allocation, IP salience and production investment.
- `ORIGINAL_DIGITAL_IP` creates distinctive reusable assets, character/world continuity and licensing value; it is measured by recognition and useful audience/commercial lift, not only visual preference.
- `COMMERCIALIZATION` maps sponsor/category fit, rights, offer architecture and brand outcomes; it constrains product-truth, rights and deliverables without silently dictating editorial conclusions.
- `PRODUCTION_SYSTEM` converts narrative intent and promoted assets into shots, sequences, timelines and platform variants under quality/cost/provenance controls.

Distribution, measurement and learning are cross-cutting loops, not a fifth silo.

## 2. Governing product objectives

Optimize the Pareto frontier across:

1. editorial truth and audience trust;
2. story/clarity/retention;
3. distinctive IP and brand recognition;
4. visual/audio craft and continuity;
5. sponsorability and reusable rights value;
6. cash cost and creator-hours per published minute;
7. iteration speed and recoverability;
8. platform fit and cross-platform reuse;
9. provenance, consent, rights and disclosure compliance;
10. durable learning rate.

No single proxy such as raw views, cinematic quality, cheapest credits or maximum AI-video percentage may dominate the system.

## 3. Core ontology

The executable production model is built from stable objects rather than a fixed vendor or role list.

### Context

Hierarchical creative/business context:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

A context may also carry a platform variant (`BILIBILI_MASTER`, `DOUYIN_SHORT`, `XHS_REAUTHOR`, `WECHAT_CHANNELS`, `YOUTUBE_LOCALIZED`) without duplicating the underlying source truth.

### Asset

An immutable or versioned media/business object with stable identity, digest, provenance, rights and acceptance state. Examples:

- character canon view;
- wardrobe/prop/environment reference;
- verified product footage;
- source document;
- image keyframe;
- generated video take;
- voice model/reference;
- sound scene;
- music cue;
- chart/diagram;
- timeline;
- sponsor offer/rights package;
- thumbnail/title candidate;
- performance receipt.

Originals are never destructively overwritten. A revision creates a new asset/version and records lineage.

### Task

A bounded transformation or decision that consumes explicit context/assets/evidence and emits assets/evidence/decisions. Tools/providers are replaceable executors of tasks.

### Evidence

Evidence is typed and bound to the exact subject/action/artifact/provider/time. Declaration is not execution proof. Volatile provider quality, price, availability and licensing claims need dated evidence and may expire.

### Decision

Promotion, rejection, route selection, commercial acceptance and release are explicit decisions with owner, criteria and evidence. Producer completion is never identical to approval.

## 4. Three planes

### 4.1 Business plane

Owns portfolio, series, audience hypotheses, IP strategy, sponsor inventory, offers, rights and measurement goals.

### 4.2 Creative/production plane

Owns story beats, shot intent, reference bundles, takes, edit/timeline, sound, QA and platform derivatives.

### 4.3 Assurance/evolution plane

Owns capability evidence, provenance, rights/disclosure, promotion gates, failure/repair receipts, experiments and durable learning.

These planes share object identities and evidence but do not duplicate authority.

## 5. Production graph: from story intent to release

The primary production graph is:

1. `EpisodeIntent`
2. `ClaimAndSourceMap`
3. `BeatMap`
4. `ShotPlan`
5. `ReferenceBundle`
6. `GenerationOrAcquisitionPlan`
7. `CandidateTakes`
8. `TakePromotion`
9. `SequenceAssembly`
10. `MasterTimeline`
11. `SoundScene/Mix`
12. `Technical + Semantic QA`
13. `PlatformVariantPlan`
14. `ReleaseCandidate`
15. `ReleaseReceipt`
16. `Performance/CommercialReceipt`
17. `LearningCandidate`

The legacy stage workflow remains a compatibility adapter for historical projects; it is no longer the conceptual center of the product.

## 6. Shot contract

Every generated/acquired shot carries at minimum:

- stable `shot_id` and owning sequence/context;
- narrative/explanatory job;
- expected duration and aspect/master crop policy;
- visual class and generation/acquisition modes allowed;
- must-have / must-not-have constraints;
- truth mode (`SYNTHETIC`, `EDITORIAL_REAL`, `PRODUCT_TRUTH`, `MIXED_DISCLOSED`);
- identity/continuity requirements;
- reference asset IDs/digests and intended role of each reference;
- camera/action/physics/audio/editability requirements;
- target quality vector rather than one scalar quality score;
- risk class (`LOW`, `MEDIUM`, `HIGH`, `HERO`, `BRAND_TRUTH`);
- cash/credit/latency/retry budget;
- graceful-degradation ladder;
- stop conditions;
- disclosure/provenance requirements.

## 7. Model capability registry

Providers/models are volatile execution substrates. The registry stores observed, dated evidence rather than permanent folklore.

Required capability dimensions include:

- T2V / I2V / V2V/edit / extend;
- first/last-frame support;
- image/video/audio reference support and budgets;
- character/subject consistency controls;
- style/environment/object reference controls;
- camera control;
- native audio/dialogue/SFX;
- max duration / resolution / frame rate / aspect ratios;
- masking/green-screen/product-placement/editing support;
- latency/concurrency/API availability/region constraints;
- quality vector with evidence date and benchmark/sample refs;
- price/credit model with evidence date;
- commercial-use/licensing/provenance semantics;
- provider availability and deprecation status.

Routing is capability-first. A provider name is never a business rule.

## 8. Routing and generation lanes

### Exploration lane

Goal: learn cheaply and quickly.

- cheapest sufficient engine/mode after hard capability, rights and truth gates;
- lower resolution and still/keyframe prototypes encouraged;
- candidate generation may proceed without isolated blind-review infrastructure when it cannot yet exist;
- outputs remain `CANDIDATE` and cannot silently enter canon/final media.

### Production lane

Goal: produce promotable assets.

- quality/continuity/truth first, then economics;
- route score is multi-dimensional and shot-specific;
- retries are budgeted and every retry is a new take, never an overwrite.

### Hero/brand-truth lane

Goal: protect the highest-value or highest-risk material.

- strongest admissible provider/real-asset route;
- independent review/attestation when the required capability is actually executable;
- verified real or authorized product media wins over synthetic approximation where factual product appearance/behavior is material.

## 9. Promotion instead of pre-generation paralysis

The old architecture over-coupled quality-critical generation to isolated pre-generation review. That can make the system unable to create a candidate when trusted reviewers are unavailable.

New rule:

`generation admission != asset promotion != release admission`

### Candidate generation admission

Requires:
- complete shot/reference contract;
- legal/current provider capability;
- input rights/consent;
- budget/retry allowance;
- truth policy compliance.

It may create a candidate even if high-assurance reviewers are unavailable.

### Promotion to accepted project asset

Requires evidence proportional to risk:
- artifact identity/digest;
- continuity/identity assessment where relevant;
- semantic/visual quality assessment;
- product-truth/rights checks where relevant;
- independent/attested review for declared high-assurance tiers when executable;
- explicit decision owner.

### Release admission

Requires final technical QA, rights/provenance, disclosure decision, approved claims/product truth, platform-specific deliverable validation and release owner approval.

No candidate, rejected take or stale artifact becomes accepted by file presence alone.

## 10. Asset continuity and IP canon

Character/IP consistency is an asset graph, not a prompt-memory problem.

Canon layers:

1. identity geometry / face-body structure;
2. expression range;
3. hair/wardrobe/prop vocabulary;
4. color/material/lighting grammar;
5. voice identity and performance envelope;
6. signature motion/gesture;
7. world/environment grammar;
8. distinctive brand assets and recurring visual/audio motifs;
9. allowed variants and forbidden drift;
10. commercial/licensing/likeness constraints.

Each shot binds exact canon versions. Updating canon invalidates only downstream assets that consumed the changed version.

IP promotion criteria include recognition, consistency, audience usefulness and commercial reuse — not merely subjective attractiveness.

## 11. Timeline and editing

The master editorial state is non-destructive and timeline-oriented, conceptually compatible with OpenTimelineIO:

- clips reference external assets rather than embedding truth into the timeline;
- tracks, transitions, markers, captions, audio and variant metadata remain separately addressable;
- generated extensions/retiming/replacements are new derived assets with lineage;
- a platform derivative is a transform of the master editorial/story state, not an unrelated project copy.

Descript/Premiere/DaVinci or future editors are tool adapters. No editor owns canonical business truth.

## 12. Audio system

Audio is a first-class scene asset:

- narrator/character voice canon;
- dialogue/performance intent;
- ambience;
- SFX;
- music;
- silence/dynamic contrast;
- multilingual localization;
- timing alignment and loudness/technical QA.

Native audiovisual generation may be used when it improves coherence, but important voice/music/rights assets remain independently versioned so the edit can be repaired or localized without regenerating the picture.

## 13. Growth and distribution

A single master story may produce multiple authored platform variants. Short-form is not automatic clip dumping.

For each variant, preserve:

- audience hypothesis;
- hook promise;
- title/thumbnail/cover candidate set;
- opening retention contract;
- target duration/pacing;
- safe areas/caption grammar;
- call-to-action;
- experiment ID;
- source master refs;
- platform metrics receipt.

Measurement distinguishes at least:

- exposure/impressions;
- cover/title CTR where available;
- 2/3-second exits and 5/30-second retention where available;
- average watch time and completion;
- follow conversion;
- saves/shares/comments/coins or platform equivalents;
- returning audience / series continuation;
- qualified audience signals;
- downstream sponsor/commerce outcomes when observable.

Platform metrics are provider-specific observations mapped into a stable internal metric ontology; unavailable fields remain unknown rather than fabricated.

## 14. Commercialization and rights

Commercialization begins during portfolio design, not after a video is finished.

Every episode/series can expose a `CommercialFit` object:

- advertiser categories genuinely adjacent to the topic/audience;
- integration surfaces that preserve editorial logic;
- product-truth requirements;
- prohibited claim/placement forms;
- required real/authorized assets;
- rights granted (organic post, paid media, whitelisting, cutdowns, duration, territory, exclusivity, reuse);
- production complexity uplift;
- measurement plan;
- case-study/reuse potential.

Offer architecture and pricing therefore consume real production-cost, audience and rights evidence instead of flat rate-card folklore.

Commercial success is measured across money and brand value, not only views: revenue/gross margin, repeat-buy probability, measurable brand/business outcomes, reusable assets/rights and audience trust impact.

## 15. Product-truth, provenance and disclosure

For factual products/real people/real events:

- do not synthesize evidence of a feature, interface, appearance or event and present it as observed reality;
- bind verified source/brand assets to the exact claim/shot;
- likeness and voice references require authorization/consent evidence;
- maintain provider/output provenance and, where available, Content Credentials/C2PA metadata;
- release includes an explicit synthetic-content disclosure decision per platform/current policy;
- AI disclosure is a compliance attribute, not a quality penalty.

## 16. Economics

Track by episode, sequence, shot, provider and reusable asset:

- cash/credits;
- compute seconds;
- retries and rejected takes;
- human review/creator minutes;
- latency/wait time;
- premium-model seconds;
- reuse count;
- cost per accepted shot;
- cost and creator-minutes per published minute;
- marginal cost of platform variants;
- revenue/gross margin when commercialized.

Budgeting is portfolio-aware: spend premium capacity where it materially changes audience, IP or commercial value, not uniformly across seconds.

## 17. Quality/evaluation model

Quality is a vector, not one 1–5 number. At minimum:

- subject/identity consistency;
- background/world consistency;
- temporal stability/flicker;
- motion/physics plausibility;
- prompt/shot-intent adherence;
- composition/lighting/material craft;
- camera execution;
- audio/dialogue sync and sound-scene quality;
- editability/continuation quality;
- narrative clarity;
- brand/IP distinctiveness;
- factual/product truth;
- platform packaging fitness.

Machine metrics, multimodal reviewers and human/business outcomes are different evidence classes. None silently substitutes for another.

## 18. Learning and evolution

Every production or business result can emit a learning candidate, but durable rules require scoped evidence.

Learning hierarchy:

`take -> shot pattern -> episode -> series -> portfolio/domain rule`

Promotion requires repeated or high-signal evidence, counterexamples and a regression/replay plan. Provider observations expire; durable business/creative mechanisms may persist when validated.

The domain exposes one canonical evolution index with deeper causal audit refs. Material problems preserve symptom -> diagnosis -> challenged assumption -> alternatives/failures -> repair -> verification -> remaining uncertainty.

## 19. Owner-native Common Behavior 1.2 realization

Before asking the user for a recoverable Video dependency, inspect current project authority, promoted assets/decisions, work-order/receipt history, connected/current context and useful external evidence. If a bounded provisional path is safe, continue under explicit uncertainty.

A detected repairable Video system problem must end in:

- `REPAIR_EXECUTED`,
- `BLOCKED_WITH_REASON`, or
- `NO_CHANGE_WITH_EVIDENCE`.

Recommendation-only closure is invalid when the owner has authority and capability to perform the repair now.

## 20. Architectural non-goals

- no single-vendor production lock-in;
- no giant prompt as source of truth;
- no destructive overwrite of accepted assets;
- no requirement that every shot use generative video;
- no requirement that every candidate pass release-grade review before it can exist;
- no role/persona proliferation as a substitute for capability;
- no second cross-chat controller;
- no duplicated project truth in UAOS;
- no business success definition based on views alone;
- no commercial optimization that overrides product truth or audience trust.

## 21. External method basis

The design deliberately borrows stable properties, not vendor-specific recipes, from:

- MovieLabs 2030 Vision / Ontology for Media Creation: Task, Asset, Participant, Context, stable identifiers, interoperable non-destructive software-defined workflows;
- OpenTimelineIO: timeline/track/clip/transition metadata with media referenced externally;
- current multimodal video systems (Veo 3.1, Seedance 2.5, Kling/WAN/Runway surfaces, Luma Modify): reference-rich generation, keyframes, editing, extension, native audio and replaceable providers;
- VBench: disentangled temporal/subject/background/flicker and frame-level quality rather than one undifferentiated quality score;
- Kantar/IAB creator research: long-term creative platforms, distinctive assets and accountable business/brand measurement rather than isolated creator posts and vanity metrics;
- C2PA/Content Credentials and current platform disclosure policies: provenance/disclosure as release metadata;
- modern NLE/agent editors: editing tool is an adapter over canonical assets/timeline, not the business authority.

These references inform architecture. Current provider features/prices remain volatile evidence in the capability registry and are not frozen into this document as permanent truths.
