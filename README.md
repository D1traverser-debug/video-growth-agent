# Video Growth Agent

Standalone, outcome-driven Video Studio for research, creative development, parallel media production, audiovisual QA, release preparation and evidence-based learning. New Video work does not require CAOS.

## Current authority

- `STUDIO_ENTRY.md` — current standalone startup and operating entry for new Video work.
- `docs/standalone_video_studio.md` — Video-owned goal, decision, dynamic DAG, execution, artifact, review, failure and learning method.
- `video_studio/data/studio_manifest.json` — canonical standalone runtime and governance contract; no CAOS runtime/API/Skill dependency.
- `video_studio/engine.py`, `cli.py`, `media.py` — canonical standalone project state, concurrent task claims, artifact lineage and deterministic FFmpeg/FFprobe QA.
- `video_studio/adapters.py` — explicit, task-bound adapters for EditorialPlan, ShotContract, IPOS shot binding, IPOS continuity, MediaGraph bootstrap, Timeline, continuity, shot routing, business metrics, supplementary audio QA and deterministic local graphic rendering.
- `skills/video-growth-agent/SKILL.md` — self-contained Video-owned agent operating instructions.
- `CAOS_VIDEO_ENTRY.md`, `domain_manifest.json` and `capabilities.json` — retained for 0.8 compatibility/history; not startup dependencies for new Studio work.
- `docs/product_requirements.md` — historical 0.8 product-requirements baseline; new operating authority is the standalone contract.
- `docs/media_business_os.md` — 0.8 media-business domain reference; new execution/governance authority is standalone Video Studio.
- `docs/architecture.md` — historical 0.8 architecture reference.
- `docs/agent_operability_scenarios.md` — historical 0.8 operability scenarios; standalone operating rules live in the new Skill and contract.
- `docs/provider_benchmark_protocol.md` — owner benchmark method for volatile provider quality/cost evidence.
- `projects/PROJECT_INDEX.json` — child-owned project/program discovery authority.
- `projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json` — growth/IP/commercial/production feedback loops.
- `audits/EVOLUTION_INDEX.json` — canonical Video evolution-evidence entrypoint.
- `video_growth_agent/data/` — versioned legacy/specialized episode workflow, specialists and coordination resources.
- binary/media stores — evidence only when bound by stable refs/digests; never business authority by presence alone.

The new `video_studio` package owns its requirement interpretation, decision receipts, task graph, leases, artifact history, review receipts, root-cause repair, recovery and learning admission. `vga-studio` and `python -m video_studio` both enter this package; legacy import paths are compatibility shims. It has no parent task identity, no parent lease and no CAOS runtime/API/Skill dependency. The 0.8 controller, fixed-stage workflow and parent-governance surfaces are not loaded by `vga-studio`. Specialized domain modules are imported only through the explicit `video_studio.adapters` bridge when a task declares a verified adapter.

## Legacy Media Business OS 0.8.0 compatibility layer

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

The previous stage/work-order episode engine remains a historical 0.7/0.8 compatibility bundle. New projects use the dynamic task graph in `video_studio`; do not treat the old fixed stage sequence as the new Studio controller.

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
- `owner_behavior_admission.py` — legacy 0.8 Video-domain recovery, root-scope analysis, typed evolution and repair closure.

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

## Standalone cognition, dogfood and evolution

New Studio work uses the self-contained method in `docs/standalone_video_studio.md`: recover the real outcome; compare competing hypotheses and methods; use discriminating tests and counterevidence; execute a project-specific DAG; inspect exact artifact bytes; diagnose failures at the causal layer; independently replay repairs; and promote learning only with applicability, counterexamples and regression evidence. None of these operations calls CAOS.

The standalone release contract now records immutable input lineage, invalidates consumers on source replacement, requires rights evidence across used media lineage, enforces exact-digest FFmpeg/FFprobe QA (full decode, stream timing, true peak and black frames), supports attested human cold reads and requires three evidence-backed Red Team findings when configured. See `docs/standalone_video_studio.md` and the three outcome/task examples.\n\nThe following legacy 0.8 adapter continues to describe its historical CAOS-governed workflow for compatibility only. It is not the standalone Studio runtime.


### Integrated media-business program example

The program-level DAG covers MEDIA_GROWTH, ORIGINAL_DIGITAL_IP, COMMERCIALIZATION and PRODUCTION_SYSTEM. It keeps growth, advertiser mapping, production economics, provider benchmarking and fact research independent; IPOS identity work waits for the approved bundle; the Jensen/Alice media audit waits for exact source bytes; competitive commercial/topic/portfolio candidates fan out before human adjudication.

```bash
vga-studio --root ./studio-work init ai-self-media-commercialization --title "AI Self-Media Commercialization" --brief examples/ai-self-media-commercialization.brief.json
vga-studio --root ./studio-work plan ai-self-media-commercialization examples/ai-self-media-commercialization.tasks.json
vga-studio --root ./studio-work status ai-self-media-commercialization
```

### Run the standalone domain-adapter proof

This sample produces a silent, candidate-only title card with the real local renderer, then binds canonical FFmpeg/FFprobe QA to the exact registered MP4. It requires a local font file and evidence that the font may be used:

```bash
vga-studio --root ./studio-work init adapter-demo --title "Standalone adapter demo" --brief examples/standalone-domain-adapters.brief.json
vga-studio --root ./studio-work plan adapter-demo examples/standalone-domain-adapters.tasks.json
vga-studio --root ./studio-work import-asset adapter-demo rights-clearance ./font-license-evidence.txt --kind document --media-type text/plain --rights-status OWNED
vga-studio --root ./studio-work import-asset adapter-demo font-asset ./DejaVuSans.ttf --kind font --media-type font/ttf --rights-status LICENSED --metadata examples/adapter-demo-font.metadata.json
```

Claim and complete the authoring task with the exact EditorialPlan JSON, then use `run-adapter` for validation/materialization/rendering and `qa-media` for canonical technical QA. The renderer's receipt explicitly states that the output is silent, candidate-only and not release-authorized.

## Validation

After `pip install -e .`:

```bash
vga-studio --help
vga system-audit --repo-root .  # legacy 0.8 compatibility audit
pytest -q
```

The legacy system audit covers the historical 0.8 CAOS governance binding, Video business ownership, all canonical 0.8 runtime surfaces, agent-operability scenario presence, Media Business OS authorities, project/flywheel integrity, provider-neutral capability semantics, Program graph validity, absence of a parallel controller, artifact reachability, legacy-adapter bundle consistency, evolution discoverability and runtime-version consistency. It fails closed when a declared canonical runtime surface disappears or drifts.

CI success is validation evidence, not branch-protection enforcement unless GitHub separately reports branch protection/rulesets as enabled.

## Standalone IP Studio OS integration

The personal-IP character canon is owned by the independent IP Studio OS (IPOS); IPOS does not require a CAOS runtime/API call. The standalone program plan models the owner-approved IPOS Video Identity Bundle as an external versioned input and keeps identity-dependent tasks waiting until G2/G7/G8 and rights/provenance pass. The old `video_growth_agent.ip_identity` adapter remains a 0.8 capability reference; it is not silently treated as a verified standalone adapter. See `projects/ai-self-media-commercialization/IPOS_INTEGRATION_STATE.json`.
