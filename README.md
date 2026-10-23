# Video Growth Agent

Executable AI-native media business domain owner under `D1traverser-debug/universal-agent-os@main`, integrating media growth, original digital IP, commercialization and provider-neutral audiovisual production.

## Current authority

- `UAOS_SKILL.md` — direct Video-domain operating entry.
- `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` — parent/common binding, identity boundary and capability ceiling.
- `docs/product_requirements.md` — current product requirements.
- `docs/media_business_os.md` — primary media-business architecture.
- `docs/architecture.md` — compact architecture/compatibility view.
- `docs/agent_operability_scenarios.md` — CURRENT_AGENT dogfood, failure/recovery and resume acceptance scenarios.
- `docs/provider_benchmark_protocol.md` — owner benchmark method for volatile provider quality/cost evidence.
- `projects/PROJECT_INDEX.json` — child-owned project/program discovery authority.
- `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json` — growth/IP/commercial/production feedback loops.
- `audits/EVOLUTION_INDEX.json` — canonical Video evolution-evidence entrypoint.
- `video_growth_agent/data/` — versioned legacy/specialized episode workflow, specialists and coordination resources.
- binary/media stores — evidence only when bound by stable refs/digests; never business authority by presence alone.

There is no active repository-local parent task index, lease/resume protocol or second cross-chat controller. UAOS router identity remains distinct from all Video business identities.

## Raw screenplay → H3 director flow

The director no longer requires the operator to invent a complete storyboard JSON before using the system.

```bash
# Generate a source-locked authoring task and all original clock/prose units; no provider call.
vga author-director tests/fixtures/ribbon_original_30s.txt --seconds 10 --source-ref user-quoted://full-30-second-ribbon-storyboard-2026-10-23

# Validate an actual model-produced director-plan JSON against the *exact* source
# and compile H3 Chinese prompts; fail on omitted source units, false quotes,
# contradictory timing, or dialogue/soundtrack policy violations.
vga author-director tests/fixtures/ribbon_original_30s.txt --seconds 10 --source-ref user-quoted://full-30-second-ribbon-storyboard-2026-10-23 --model-output tests/fixtures/prompt_ribbon_fullsource_10s.json

# Optional LIVE text-authoring-model invocation (NOT the H3 video model).
# Send the source to the configured provider ONLY with explicit API/spend approval.
# Set VIDEO_DIRECTOR_API_KEY in environment; do not put secrets in commands.
vga author-director tests/fixtures/ribbon_original_30s.txt --seconds 10 --execute-model --endpoint https://YOUR-PROVIDER/v1/chat/completions --model-name YOUR-TEXT-MODEL --approve-upload-cost --out-plan director.json
```

Complete 30-second source has 24 time-marked units including original overlapping clock intervals. A separate untimed original idea is handled as sentence-span units. The checksum/source identity and per-unit lexical event maps are verified; whether each event is *understandable to an actual viewer in 10 seconds* remains unverified until generated footage is reviewed. External model calls are opt-in, can incur cost, and permit zero retries by default.

## Cross-discipline craft iteration (uses existing roles and learning library)

There is no new video controller. The seven relevant roles already defined in the Video RoleRegistry (writer, director, storyboard artist, art director, editor, sound director, red team) can receive independent plan-review packets for substantial full-film work. Simple short prompts can skip this full-team overhead.

```bash
vga craft-round tests/fixtures/prompt_ribbon_fullsource_10s.json
vga craft-round tests/fixtures/prompt_ribbon_fullsource_10s.json --reviews submitted-reviews.json
vga craft-round revised-plan.json --previous old-plan.json --revision 2
vga techniques --tag review --include-candidates
```

The command **prepares** review requests but does not execute seven LLMs or attest seven humans reviewed a film. Reconciliation takes externally submitted role critiques, rejects wrong plan versions, forwards findings to the existing discipline owners and requires a new plan hash for edits. Actual media QA remains with existing MediaQA/reviewer attestation. Candidate techniques T-015/016/017 are additions to the **existing** TechniqueLibrary and are not production validated.

Research notes at `skills/video-growth-agent/references/craft-source-studies.md` examine nine first-party producer/editor/model/reliability sources with use cases, non-transferable defaults and falsifiable prototypes. See `self-learning.md` for the existing adoption authority. Reading a Skill does not mean its entire workflow should be copied, or that a provider's specific aesthetic becomes this studio's rule.

## Focused prompt director (isolated candidate)

For a short AI film **prompt task**, use the original brief and run `vga direct-prompts` before invoking unrelated release/business process modules:

```bash
vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route compare   # defaults to auto: three unranked H3 candidates
vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route onepass --h3-style official
vga direct-prompts tests/fixtures/prompt_ip_5s.json --route compare
vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --study-h3-dialects
vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --route onepass --plain
vga direct-prompts tests/fixtures/prompt_ribbon_10s.json --review-sheet
```

Director plans must now supply `visual_language` for global art direction, including specific materials, color palette, world continuity, motivated light and render finish. Structured H3 prompts also preserve localized sound cues and explicit speaker/language/utterance markup, with an unscored per-shot review packet for real generated footage.

**One positive example is not a universal production template.** The owner reported a good H3 result for one dense Chinese 10-second storyboard, but did not establish a permanent style preference or controlled model winner. For H3, `--h3-style auto` (default) emits **three unranked alternatives**: concise causal (`lean`), dense Chinese shot list (`chinese`), and vendor-structured (`official`), without choosing an aesthetic winner. Explicit style flags remain for reproducible comparison. One-pass versus shotwise is assessed separately with generation/trim costs; PixVerse remains opt-in, never a blanket dismissal. Real video review, not syntax, decides which works for a particular scene.

The current skill is intentionally prompt-centric and does **not** reorganize or delete validated production/release modules. The older all-scope draft PR is not required for this prompt compiler.

## Runtime 0.8.0 candidate

Video 0.8 makes the media-business system operable from natural-language/editorial intent through production and learning rather than starting mechanically at the Shot layer.

The current executable chain is:

`EpisodeIntent -> ClaimSpec -> BeatSpec -> ShotIntent -> EditorialPlan -> ShotContract -> ModelRoutingDecision -> CandidateTake -> ContinuityAssessment -> Promotion -> Timeline -> Editor handoff/roundtrip -> PlatformVariant -> Release -> Experiment/Outcome -> LearningCandidate`

Linked state surfaces remain distinct:

1. **Media-business Program graph** — portfolio/growth/IP/commercial/production tasks and decisions.
2. **Editorial decision state** — episode intent, claims, beats, shot intents and immutable plan versions.
3. **Media context/asset graph** — `Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`, versioned assets, references, lineage, evidence and promotion.
4. **Continuity relations** — dimension-level preserve/expect/allowed-change state across shots.
5. **Editorial timeline/interchange** — non-destructive temporal assembly, platform variants and external-editor handoff/return identity.
6. **Experiment/outcome state** — pre-registered tests and typed growth/production/commercial observations.
7. **Operator projection** — recomputable current-Agent view of outcome, ready/blocking actions, stale evidence and recovery refs; never authority.

The previous stage/work-order episode engine remains a proven 0.7 compatibility adapter bundle. Its resource version may trail the 0.8 core while unchanged; the bundle must remain internally version-aligned and system-audit verified.

Core 0.8 runtime surfaces:

- `media_graph.py` — stable Context/AssetVersion/Task/Evidence/Decision identities, promotion pointers, persistence, lineage and downstream invalidation;
- `editorial_planning.py` — EpisodeIntent/Claim/Beat/ShotIntent/EditorialPlan and explicit materialization into production contracts;
- `plan_graph_bridge.py` — editorial-plan versions as MediaGraph upstream assets so revisions stale only affected descendants;
- `production_os.py` — editorial-traceable shot/reference/take contracts and generation/promotion/release admission;
- `continuity.py` — cross-shot dimension-level continuity contracts and assessments;
- `model_registry.py` — provider-neutral operation-profile legality plus rubric/calibration-bound, uncertainty-aware Pareto routing;
- `timeline.py` — editor-neutral non-destructive master/variant timeline metadata bound to promoted asset versions;
- `editorial_interchange.py` — external editor/NLE handoff and roundtrip receipts bound to timeline/project/composition identity;
- `experiments.py` — pre-registered hypothesis/variant/metric/guardrail/stop-rule contracts and causal-attribution boundaries;
- `business_objects.py` — typed content-portfolio, distinctive-asset, commercial-fit, rights-package, offer and business-decision objects;
- `business_metrics.py` — platform, production and commercial outcome receipts without one vanity score;
- `operator_view.py` — non-authoritative CURRENT_AGENT projection;
- `owner_behavior_admission.py` — UAOS Common Behavior 1.2 owner-native recovery/escalation/repair closure.

## Integrated Media Business Program

Generic AI-video/media-growth/commercialization/original-IP requests resolve to `ai-self-media-commercialization` unless an exact child project is supplied.

The Program keeps four business views:
- `MEDIA_GROWTH`
- `ORIGINAL_DIGITAL_IP`
- `COMMERCIALIZATION`
- `PRODUCTION_SYSTEM`

They are evidence-coupled rather than isolated. Audience evidence changes portfolio hypotheses; portfolio/series strategy informs IP and advertiser fit; promoted IP assets affect packaging/recognition/production; commercial deliverables and rights can affect verified product-asset needs; production cost/retry/reuse evidence feeds future format investment. Editorial truth and audience trust remain hard constraints.

Historical Pilot projects remain separately resumable and retain their own adapter/runtime identity plus rejected/process-invalid evidence.

## Candidate -> promotion -> release

Safe exploration is not the same as approval.

- Candidate generation requires current capability, rights/consent, truth-policy and budget admission.
- An output remains `CANDIDATE` until explicit promotion evidence/owner decision exists.
- HIGH/HERO/BRAND_TRUTH promotion can require independent/attested review.
- Release remains fail-closed on final-media identity, technical QA, rights, claim/product truth, provenance, disclosure/platform validation and release authority.

## Provider/model strategy

No vendor is permanent architecture. Current provider/model facts are dated observations.

Capability is expressed by operation profile so a model cannot be treated as supporting every combination merely because its feature list separately mentions references, resolution or extension. Production quality evidence must bind compatible rubric/calibration scope and uncertainty. After hard capability/rights/terms/budget floors, production selection uses non-dominated quality vectors and explicit shot priorities rather than a hidden weighted-average authority.

Official vendor documentation establishes capabilities/limits/terms, not our quality ranking. Production observations require the stable benchmark pack in `docs/provider_benchmark_protocol.md` or exact production evidence.

## IP, growth, experiments and commercialization

IP is a reusable distinctive asset system, not only character aesthetics. Canon is versioned and can include structural identity, expression, wardrobe/props, color/material/light, voice/performance, gesture, world grammar and distinctive audio/visual motifs.

Platform derivatives preserve master lineage but re-author hook, packaging, pacing and conclusion for the destination platform. Material packaging/content/IP tests are pre-registered where causal learning matters; `NO_CLEAR_WINNER` and `INCONCLUSIVE` are valid outcomes and multivariable tests cannot masquerade as single-variable causality.

Commercial planning may begin before production when rights, sponsor deliverables, product-truth media or measurement alter the work. Sponsorship never overrides factual/editorial truth. Pricing learns from audience evidence, production cost, rights scope and real outcomes rather than a single static rate card.

## Capability and assurance boundary

Before generation/edit/review/QA/release, handshake the exact current-session capability required by the action. Repository declarations are ceilings, not execution proof.

`DECLARED_ONLY < HARNESS_WIRED < SESSION_EXECUTABLE`; `CHAT_BRIDGED` does not mean independent verification; true isolated assurance requires `ATTESTED_ISOLATED` evidence.

Missing a high-assurance reviewer blocks only operations that require that tier. Missing a real generation provider blocks the affected shot or activates its declared degradation path; it never authorizes fabricated execution.

## Cognition, dogfood and evolution

Video inherits UAOS common cognition, Common Behavior Assurance 1.2 and the Architecture Experience policy. Material architecture/Agent-experience changes are exercised through concern-appropriate structural/temporal/causal/cognitive views and CURRENT_AGENT scenarios rather than accepted from document completeness alone.

Video-specific media/growth/IP/commercial rules remain Video-owned. Cross-domain/common mechanisms upcall UAOS. Durable evolution requires causal history plus tests/replay and post-promotion observation.

## Validation

After `pip install -e .`:

```bash
vga system-audit --repo-root .
pytest -q
```

The system audit covers parent/common binding, Video business ownership, all canonical 0.8 runtime surfaces, agent-operability scenario presence, Media Business OS authorities, project/flywheel integrity, provider-neutral capability semantics, Program graph validity, absence of a parallel controller, artifact reachability, legacy-adapter bundle consistency, evolution discoverability and runtime-version consistency. It fails closed when a declared canonical runtime surface disappears or drifts.

CI success is validation evidence, not branch-protection enforcement unless GitHub separately reports branch protection/rulesets as enabled.
