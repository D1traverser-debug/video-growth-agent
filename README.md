# Video Growth Agent

Executable AI-native media business domain owner under `D1traverser-debug/universal-agent-os@main`, integrating media growth, original digital IP, commercialization and provider-neutral audiovisual production.

## Current authority

- `UAOS_SKILL.md` — direct Video-domain operating entry.
- `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` — parent/common binding, identity boundary and capability ceiling.
- `docs/product_requirements.md` — current product requirements.
- `docs/media_business_os.md` — primary media-business architecture.
- `docs/architecture.md` — compact architecture/compatibility view.
- `docs/provider_benchmark_protocol.md` — owner benchmark method for volatile provider quality/cost evidence.
- `projects/PROJECT_INDEX.json` — child-owned project/program discovery authority.
- `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json` — growth/IP/commercial/production feedback loops.
- `audits/EVOLUTION_INDEX.json` — canonical Video evolution-evidence entrypoint.
- `video_growth_agent/data/` — legacy/specialized episode workflow, specialists and coordination resources.
- binary/media stores — evidence only when bound by stable refs/digests; never business authority by presence alone.

There is no active repository-local parent task index, lease/resume protocol or second cross-chat controller. UAOS router identity remains distinct from all Video business identities.

## Runtime 0.7.0

Video 0.7.0 uses three linked but distinct operational graphs:

1. **Media-business Program graph** — portfolio/growth/IP/commercial/production tasks and decisions.
2. **Media context/asset graph** — `Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`, versioned assets, references, lineage, evidence and promotion.
3. **Editorial timeline** — non-destructive temporal assembly and platform variants.

The previous stage/work-order episode engine is retained as a proven execution/compatibility adapter. It is not the entire product ontology.

Core runtime surfaces:

- `media_graph.py` — stable Context/AssetVersion/Task/Evidence/Decision identities, promotion pointers, persistence, lineage and downstream invalidation;
- `production_os.py` — shot/reference/take contracts, candidate-generation admission, asset promotion and release admission;
- `timeline.py` — editor-neutral non-destructive master/variant timeline metadata bound to exact promoted asset versions;
- `business_objects.py` — typed content-portfolio, distinctive-asset, commercial-fit, rights-package, offer and business-decision objects;
- `model_registry.py` — provider-neutral, dated capability/quality/cost/terms routing;
- `business_metrics.py` — platform, production and commercial outcome receipts without one vanity score;
- `owner_behavior_admission.py` — UAOS Common Behavior 1.2 owner-native recovery/escalation/repair closure.

## Integrated Media Business Program

Generic AI-video/media-growth/commercialization/original-IP requests resolve to `ai-self-media-commercialization` unless an exact child project is supplied.

The Program keeps four business views:
- `MEDIA_GROWTH`
- `ORIGINAL_DIGITAL_IP`
- `COMMERCIALIZATION`
- `PRODUCTION_SYSTEM`

They are evidence-coupled rather than isolated. Audience evidence changes portfolio hypotheses; portfolio/series strategy informs IP and advertiser fit; promoted IP assets affect packaging/recognition/production; commercial deliverables and rights can affect verified product-asset needs; production cost/retry/reuse evidence feeds future format investment. Editorial truth and audience trust remain hard constraints.

Historical Pilot projects remain separately resumable and keep rejected/process-invalid evidence.

## Candidate -> promotion -> release

Safe exploration is not the same as approval.

- Candidate generation requires current capability, rights/consent, truth-policy and budget admission.
- An output remains `CANDIDATE` until explicit promotion evidence/owner decision exists.
- HIGH/HERO/BRAND_TRUTH promotion can require independent/attested review.
- Release remains fail-closed on final-media identity, technical QA, rights, claim/product truth, provenance, disclosure/platform validation and release authority.

This avoids both unsafe auto-promotion and the old failure mode where unavailable release-grade reviewers could prevent every learnable candidate from existing.

## Provider/model strategy

No vendor is permanent architecture. Current provider/model facts are dated observations.

The router can reason about generation/edit mode, reference budgets, identity/continuity, camera/action/audio, duration/resolution, quality-vector floors, current availability/deprecation, commercial terms/provenance, price and latency.

Official vendor documentation establishes capabilities/limits/terms, not our quality ranking. Production quality scores require the stable benchmark pack in `docs/provider_benchmark_protocol.md` or exact production evidence.

## IP, growth and commercialization

IP is a reusable distinctive asset system, not only character aesthetics. Canon is versioned and can include structural identity, expression, wardrobe/props, color/material/light, voice/performance, gesture, world grammar and distinctive audio/visual motifs.

Platform derivatives preserve master lineage but re-author hook, packaging, pacing and conclusion for the destination platform; short-form is not blind clipping.

Commercial planning may begin before production when rights, sponsor deliverables, product-truth media or measurement alter the work. Sponsorship never overrides factual/editorial truth. Pricing learns from audience evidence, production cost, rights scope and real outcomes rather than a single static rate card.

## Capability and assurance boundary

Before generation/edit/review/QA/release, handshake the exact current-session capability required by the action. Repository declarations are ceilings, not execution proof.

`DECLARED_ONLY < HARNESS_WIRED < SESSION_EXECUTABLE`; `CHAT_BRIDGED` does not mean independent verification; true isolated assurance requires `ATTESTED_ISOLATED` evidence.

Missing a high-assurance reviewer blocks only operations that require that tier. Missing a real generation provider blocks the affected shot or activates its declared degradation path; it never authorizes fabricated execution.

## Cognition and evolution

Video inherits UAOS common cognition and Common Behavior Assurance 1.2. It must recover current authority/evidence before asking the user for a plausibly recoverable dependency. A repairable system problem with available authority/tooling cannot stop at a recommendation; it must be repaired, concretely blocked or preserved with evidence-backed no-change.

Video-specific media/growth/IP/commercial rules remain Video-owned. Cross-domain/common mechanisms upcall UAOS. Durable evolution requires causal history plus tests/replay and post-promotion observation.

## Validation

After `pip install -e .`:

```bash
vga system-audit --repo-root .
pytest -q
```

The system audit covers parent/common binding, Video business ownership, all canonical 0.7 runtime surfaces, Media Business OS authorities, project/flywheel integrity, provider-neutral capability semantics, Program graph validity, absence of a parallel controller, artifact reachability, specialist/task consistency, evolution discoverability and runtime-version consistency. It fails closed when a declared canonical runtime surface disappears or drifts.

CI success is validation evidence, not branch-protection enforcement unless GitHub separately reports branch protection/rulesets as enabled.
