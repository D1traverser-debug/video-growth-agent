# Video Growth Agent — Product Requirements Baseline

Status: `CANDIDATE_0_7_0`
Date: `2026-10-15`
Owner: `DOMAIN:video`
Parent dependencies: `UAOS COMMON_CAPABILITIES >= 1.6.0 / COMMON_BEHAVIOR_ASSURANCE >= 1.2.0`
Primary architecture ref: `docs/media_business_os.md`

## 1. Product outcome

Video Growth Agent is one AI-native media business operating system. It turns audience/problem evidence and distinctive IP into repeatable high-quality media, measurable growth, sponsor/rights value and durable production learning.

It owns four coupled business views:

1. `MEDIA_GROWTH` — portfolio, positioning, audience, packaging, distribution, performance and series learning;
2. `ORIGINAL_DIGITAL_IP` — character/world/visual/audio canon, distinctive assets, identity continuity and reusable rights value;
3. `COMMERCIALIZATION` — advertiser/category fit, native integration, offer/pricing/rights packages and business-outcome measurement;
4. `PRODUCTION_SYSTEM` — episode/shot/asset/timeline generation, acquisition, editing, QA, routing, cost and provenance.

These are not independent products. Cross-workstream evidence and decisions are explicit in the integrated Program and `BUSINESS_FLYWHEEL.json`.

## 2. Product objective vector

Do not optimize one proxy. Preserve separate evidence for:

- editorial/product truth and audience trust;
- retention/clarity/usefulness;
- distinctive-IP recognition and reuse;
- audiovisual craft/continuity;
- qualified audience growth;
- sponsorability/rights value/business outcomes;
- cash cost and creator-hours per published minute;
- iteration speed/recoverability;
- platform fit/cross-platform reuse;
- provenance/consent/rights/disclosure;
- durable learning rate.

Views, one scalar quality score, AI-video percentage or cheapest credits are never the global objective.

## 3. Identity and authority

- UAOS owns cross-domain selection/governance and common cognition/evolution/product/orchestration semantics.
- Video Growth Agent owns all Video business Program/Series/Episode/Sequence/Scene/Shot/Take identities, project state, assets, decisions and business rules.
- `projects/PROJECT_INDEX.json` is project discovery authority.
- The default integrated Program is `ai-self-media-commercialization`.
- UAOS may retain an opaque child reference only; it does not mirror Video business state.

## 4. Primary user journeys

### VR-01 Direct Video-domain start
A user can select AI video, original digital IP, media growth, sponsorship/commercialization or a concrete Video project and enter `DOMAIN:video` directly.

### VR-02 Integrated business Program
Generic AI-media/IP/commercial intents resolve to `ai-self-media-commercialization` unless an exact child project is supplied. Growth, IP, commercialization and production progress independently where no explicit dependency exists and feed each other through durable evidence/decision edges.

### VR-03 Exact historical project recovery
Exact child project/legacy aliases resolve inside Video. Historical projects keep their own accepted/rejected evidence; no legacy alias becomes a UAOS task identity.

### VR-04 Portfolio and series planning
The system can maintain topic/series candidates, audience hypotheses, distinctive assets, production economics and commercial adjacency without forcing a particular provider or episode format.

### VR-05 Shot/asset production
A story is decomposed into contexts and shot contracts. Every generated/acquired take binds the exact shot, input asset versions, provider observation, rights, cost and artifact digest.

### VR-06 Multimodal reference/edit workflow
Modern generation may consume image/video/audio references, keyframes, existing video, masks or other controls. The product models these as reference/asset contracts instead of provider-specific prompt folklore.

### VR-07 Exploration without unsafe promotion
Safe, rights-admitted candidate generation can proceed even when release-grade independent review is unavailable. Candidate existence never implies canon/final acceptance. Promotion and release are separate fail-closed decisions.

### VR-08 Non-destructive iteration
Edits, extensions, replacements, relighting, retiming and regenerations create derived assets/versions with lineage. Originals and historical receipts remain recoverable.

### VR-09 Platform-specific authorship
Bilibili long-form, Douyin/Channels/XHS short-form and future localized outputs are authored variants of one master story/asset graph. Short-form is not blind clip dumping.

### VR-10 Original IP as a business asset
Character/brand canon is assessed for structural consistency, recognizability, distinctive-asset value, storytelling usefulness, packaging effect, reusable rights and sponsor fit — not beauty alone.

### VR-11 Commercial pre-production
When a sponsor/product is involved, commercial fit, rights, product-truth assets, integration surfaces, deliverables and measurement requirements are resolved early enough to affect production, while editorial conclusions remain independent.

### VR-12 Performance and learning
Platform, production and commercial outcomes are captured as separate typed receipts and can create scoped learning candidates. Provider observations expire; durable rules require evidence, counterexamples and tests/replay.

### VR-13 Problem recovery and system repair
Before asking the user for a recoverable dependency, Video attempts owner-native recovery. A confirmed repairable system problem with available authority/tooling must be repaired now or end with a concrete blocker/evidence-backed no-change, not a recommendation-only terminal.

## 5. Media-production ontology

Primary hierarchy:

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Shared object classes:

- `Asset` / asset version and lineage;
- `Task`;
- `Evidence`;
- `Decision`;
- `Rights/Consent`;
- `Cost`;
- `PlatformVariant`;
- `PerformanceReceipt`;
- `CommercialOutcomeReceipt`;
- `LearningCandidate`.

Stable IDs and artifact digests outrank file names/chat memory. `video_growth_agent/media_graph.py` is the canonical executable metadata graph for Context, AssetVersion, Task, Evidence and Decision records; promotion pointers and invalidation never erase historical versions.

## 6. Model/provider requirements

The runtime must be provider-neutral. Current provider observations are dated evidence, not permanent traits.

The capability registry must be able to express:

- T2V/I2V/V2V/edit/extend;
- first/last-frame controls;
- image/video/audio reference budgets;
- identity/style/object/environment controls;
- camera/action/physics controls;
- native audio/dialogue/SFX;
- duration/resolution/aspect/frame-rate constraints;
- latency/concurrency/region/API readiness;
- quality vector and evidence refs;
- current price/credit evidence;
- commercial-use/licensing/provenance semantics;
- availability/deprecation state.

Routing is shot-contract driven. Exploration is cheapest-sufficient after hard gates; production is quality-first after hard gates. Hero/brand-truth work may require stronger provenance/independent review.

## 7. Promotion and release requirements

### Candidate generation admission
Requires complete shot/reference contract, provider capability/availability evidence, rights/consent, truth-policy compatibility and budget/retry allowance.

### Asset promotion admission
Requires exact take/artifact identity, required quality-vector evidence, continuity evidence when relevant, rights/truth evidence and risk-proportional independent review.

### Release admission
Requires final-media digest, master timeline reference, technical QA, rights, claim/product truth, provenance, synthetic-content disclosure decision, platform validation and release owner.

Candidate/rejected/stale assets cannot silently return to accepted state.

## 8. Growth/distribution requirements

Platform variants carry their own hook/packaging/duration/aspect/CTA/experiment and metric semantics while preserving source lineage.

Capture provider-reported metrics where available, including exposure/play, CTR/cover-title diagnostics, early exits, watch time/completion, interaction, follow conversion, returning audience and commercial outcomes. Missing provider metrics remain unknown.

Packaging and content experiments need candidate identity and decision evidence; post-hoc storytelling from one viral result is not durable learning.

## 9. IP requirements

Canon can cover identity geometry, expressions, wardrobe/props, color/material/light grammar, voice/performance, motion/gesture, environment/world grammar, distinctive visual/audio motifs, allowed variants and rights/likeness constraints.

Every identity-sensitive shot binds exact canon versions. Canon changes invalidate only consuming downstream assets.

The Digital Observer/Narrator remains a reusable anchor, not a virtual presenter forced into every scene.

## 10. Commercial requirements

Every monetizable series/episode can carry `CommercialFit` and `RightsPackage` evidence covering advertiser adjacency, natural integration surfaces, product-truth requirements, deliverables, territories/duration/exclusivity/paid-media rights, production uplift, measurement and reuse/case-study value.

These business contracts are typed in `video_growth_agent/business_objects.py`; commercial fit cannot disable editorial independence and expanded/priced rights require evidence.

Pricing should learn from real audience, production cost, rights scope and outcomes rather than a single static rate card.

## 11. Truth, rights, provenance and disclosure

- Never fabricate observed product facts with synthetic media.
- Real-person likeness/voice reference requires authorization/consent evidence.
- Exact product/UI/material/behavior claims use verified real/brand assets or explicit non-evidentiary visualization framing.
- Preserve provider/output lineage and available Content Credentials/C2PA metadata.
- Release includes current platform-specific synthetic-content disclosure decision.

## 12. Audio requirements

Audio is first-class: narration/character voice, dialogue performance, ambience, SFX, music, silence/dynamics, localization, timing and technical QA. Native audiovisual generation may be used, but important reusable voice/music/rights assets remain independently versioned where repair/localization requires it.

## 13. Economics requirements

Track at least:

- provider/model/mode;
- generated seconds and attempts;
- rejected retries;
- cash/credits;
- creator/reviewer minutes;
- premium-model seconds;
- reusable-asset use count;
- cost per accepted shot;
- cost and creator-minutes per published minute;
- marginal platform-variant cost;
- commercial revenue/direct cost/rights revenue/gross margin when applicable.

Premium compute is allocated by expected audience/IP/commercial value and shot risk, not uniformly by duration.

## 14. Quality requirements

Quality remains vector-valued. Relevant dimensions include subject/identity consistency, world/background consistency, flicker/temporal stability, motion/physics, prompt/shot adherence, composition/light/material, camera execution, audio sync/sound craft, editability/continuation, narrative clarity, brand distinctiveness, truth and platform packaging fitness.

Machine metrics, multimodal reviewers and human/business outcomes are separate evidence classes.

## 15. Legacy compatibility

The existing episode stage workflow/work-order runtime remains supported for historical projects and can serve as one execution adapter. It is no longer the sole conceptual product architecture. Existing Pilot/H1 state and immutable receipts remain preserved.

## 16. Functional requirement map

| Requirement | Owning surface | Acceptance evidence |
| --- | --- | --- |
| Product architecture | `docs/media_business_os.md` | architecture tests + audit |
| Business flywheel | `BUSINESS_FLYWHEEL.json` | schema/invariant tests |
| Canonical media context/asset/evidence/decision graph | `media_graph.py` | identity/lineage/promotion/invalidation/persistence tests |
| Shot/reference/take/promotion/release | `production_os.py` | admission tests |
| Non-destructive master/platform timeline | `timeline.py` | exact promoted-asset refs + derivation/variant-lineage tests |
| Growth/IP/commercial shared typed objects | `business_objects.py` | portfolio/distinctive-asset/commercial-fit/rights/offer tests |
| Provider-neutral model evidence | `model_registry.py` | routing trajectory tests |
| Vector business outcomes | `business_metrics.py` | metric tests |
| Common Behavior 1.2 | `owner_behavior_admission.py` | recovery/closure trajectory tests |
| Canonical evolution evidence | `audits/EVOLUTION_INDEX.json` | architecture audit |
| Existing Program graph | `PROGRAM_STATE.json` + `SUBTASK_GRAPH.json` | orchestration tests |
| Existing work-order/attestation/QA | current runtime modules | regression suite |
| Packaging/install + canonical runtime integrity | package + `system_audit.py` + CI | fail-closed system audit, pytest, installed smoke |

## 17. Non-functional requirements

- one Video business owner; no parallel controller;
- direct domain activation;
- stable identifiers and non-destructive asset lineage;
- provider/model replaceability;
- current-enough capability/price/terms evidence;
- no self-approval;
- fail-closed promotion/release, not exploration paralysis;
- explicit cross-workstream evidence flows;
- no hidden prompt-memory authority;
- no global optimization by one vanity metric;
- no write races on the same authoritative object;
- business state stays child-owned.

## 18. Product completion criteria for 0.7.0

1. New media-business architecture and business flywheel are durable and discoverable.
2. Canonical MediaGraph, non-destructive Timeline and shared growth/IP/commercial business objects are executable and tested.
3. Provider-neutral quality-vector routing is executable and trajectory-tested.
4. Candidate-generation, asset-promotion and release boundaries are distinct and tested.
5. Product-truth/rights/provenance/disclosure stay fail-closed where they matter.
6. Common Behavior 1.2 is owner-natively executable and tested.
7. Existing 0.6 work-order/attestation/QA/project/orchestration tests remain green.
8. System audit fails closed if any declared canonical 0.7 runtime surface disappears or drifts.
9. system audit, full pytest and installed-package smoke pass on candidate and production.
10. Canonical evolution index preserves causal redesign evidence.
11. Production reread verifies version/binding/evidence.
12. UAOS parent observation is refreshed only after child production evidence passes.

Post-promotion live assurance remains open for real episode growth/IP/commercial outcomes; code/tests cannot substitute for published-media results.
