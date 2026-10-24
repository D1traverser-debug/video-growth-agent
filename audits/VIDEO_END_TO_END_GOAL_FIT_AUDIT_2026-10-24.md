# Video system — end-to-end goal-fit and operational reliability audit

Date: 2026-10-24
Owner: DOMAIN:video
Scope: current Video 0.8 main baseline + PR #23 candidate, with user business outcome as the governing acceptance standard.
Status: OPEN — SYSTEM NOT END-TO-END ACCEPTED. This is a living factual audit under the existing Video Evolution Index, not a new controller or lifecycle registry.

## 0. Question, evidence and limits

The governing outcome is not a compilable prompt or a green CI. It is a usable AI-native media business system that independently studies appropriate original craft sources, understands the true user brief and evidence constraints, coordinates appropriate specialist decisions, prepares reusable IP/material references, selects a legal and economical production route, **actually makes films**, reviews played media for story/identity/motion/audio/technical quality, repairs rejected shots/takes, retains versioned causal learning, produces platform variants, and feeds observed growth/economic/commercial results back to decisions.

Reviewed source families: `docs/product_requirements.md` VR-01..VR-18 and `docs/media_business_os.md`; current integrated Program and `BUSINESS_FLYWHEEL.json`; PR #23 checkpoint/index; executable CLI, source/director/craft, media graph/plan bridge, editorial planning, production admissions, media QA, reviewer adapters, model routing, continuity, timeline/interchange, experiments, business metrics, legacy runtime and system audit; current tests and CI. No claim of a proof of **every line** or a universal correctness theorem. Unseen external assets, provider credentials and actual user video performances are **not** assumed to exist.

Evidence-level vocabulary:
- `TESTED_STRUCTURAL`: named executable owner contracts and negative cases exercised by CI; no external-film verdict.
- `PARTIAL_INTEGRATION`: working function(s) exist, but a necessary cross-boundary operator journey is not proven.
- `REAL_EXECUTION_NOT_SHOWN`: no provided first-hand provider/film/editor/publication proof; do not infer completed work.
- `UNVERIFIED`: claims exceed evidence, including semantic/aesthetic quality, broad generalization or current provider facts.

Prior green CI #39993894697 at HEAD cbc8040a: prompt 76 passed / 2 skipped; full 265 passed; packaged smoke and system audit. Those tests were not a real rendered film. The current PR HEAD, exact CI and counts must be rechecked on resume; later code commits are **not** covered by this historical result.

## 1. Whole-product objective → owned mechanism → demonstrated outcome

| Requirement | Owner/module | Actual currently supported | System-level verdict and missing proof |
|---|---|---|---|
| VR-01 enter selected Video domain | `UAOS_SKILL.md`, `.uaos/*`, project index | registered direct-domain pointers and structure | PARTIAL_INTEGRATION: actual native host dispatch not verified in every environment |
| VR-02 restore current context | evolution index, exact checkpoint, Program state, OperatorSnapshot | persistent refs and derived object snapshot | PARTIAL_INTEGRATION: unattended cross-session action recovery not tested end-to-end with real media |
| VR-03 integrated business Program | ProgramGraph, flywheel, portfolio/IP/production/commercial objects | independent workstreams and declarative evidence loops | PARTIAL_INTEGRATION: no actual audience/sponsor/provider data ingestion driving this flywheel |
| VR-04 natural input → truth-aware plan | source_director, editorial_planning | verbatim script protection, lexical spans, typed claim/beat/shot plan API | PARTIAL_INTEGRATION: director JSON authoring and native 0.8 EditorialPlan are not one validated, factual-source-backed live operator path; lexical quote != story comprehension |
| VR-05 plan → producible shots | prompt_director, ShotContract, plan_graph_bridge | frame-consistent prompts and versioned assets; contract materialization API | PARTIAL_INTEGRATION: source-author JSON can compile H3 prompts but has no proven reference/ShotContract/provider route/real render continuity |
| VR-06 revisions and downstream stale | media_graph and bridge | explicit invalidation; candidate transitive read/promotion protection under test | TESTED_STRUCTURAL for graph contracts, not real paid provider footage invalidation/recovery |
| VR-07 IP identity and continuity | continuity, H1 project, reference assets | typed continuity policies and H1 creative state | REAL_EXECUTION_NOT_SHOWN for repeatable cross-shot I2V character/prop geometry or independent review |
| VR-08 real provider routing | model_registry / generation admission | conditional operation profile and calibrated routing API | PARTIAL_INTEGRATION: no current authenticated provider generation, capability/legal combination or fresh output receipt through the operator path |
| VR-09 quality tradeoff | QualityObservation / benchmark protocol | multidimensional criteria and Pareto routing | UNVERIFIED for provider superiority / output quality; tests use constructed benchmark observations |
| VR-10 candidate generation | generation admission / candidate Take / media QA | admission decisions and inspected local-file registration | REAL_EXECUTION_NOT_SHOWN: candidate acceptance != a model render; no linked production executor/receipt in current CLI |
| VR-11 rejected-take repair | MediaGraph versions, craft_round, learning candidates | version/diff/reason structures, no automatic promotion | REAL_EXECUTION_NOT_SHOWN for observed failure → targeted regeneration → better screened result |
| VR-12 NLE roundtrip | timeline/editorial_interchange | handoff and receipt identity validation API | REAL_EXECUTION_NOT_SHOWN for executed external editor project, returned render and playback |
| VR-13 platform variants | platform contracts / TimelineSpec | authored derivative identity, hook contract, timeline links | REAL_EXECUTION_NOT_SHOWN for assembled final platform file, measured playback or platform compliance |
| VR-14 experiments | experiments / prompt_experiment | pre-registration and result types, fixed/changed-variable attribution rules | PARTIAL_INTEGRATION: no owner live A/B output, blinded viewer or platform observation; `conclude_experiment` accepts caller-supplied outcome (not a statistical verifier) |
| VR-15 original IP as business asset | canon/rights/recognition concepts | H1 design materials/constraints and reuse mechanics | REAL_EXECUTION_NOT_SHOWN for actually promoted 3-view canon, multi-video recognition or licensing value |
| VR-16 sponsor and truth | business_objects, ProductionAdmission | rights packages, product truth modes and gates | PARTIAL_INTEGRATION: no actual contract, verified product reference route, or accepted sponsor work |
| VR-17 outcome and learning | business_metrics, TechniqueLibrary, LEARN stage | typed receipts, candidate/validated techniques, plan-stage roles | REAL_EXECUTION_NOT_SHOWN for real film failure data, reproducible improvement and observed growth/business return |
| VR-18 recovery/system self-correction | system_audit, ProjectStore, MediaGraphStore, evolution | static CI, append-only graph intent, stage receipts and checkpoint | PARTIAL_INTEGRATION: repository tests do not establish crash, concurrent writers, corrupted state, stale provider responses or live-media replay recovery |

## 2. Mechanism-level root findings — prioritize before more prompt style work

### P0: The production cycle is not closed

Current CLI exposes `author-director` (optional paid *text* model), `direct-prompts` (prompt output), `craft-round` (plan critiques), `register-directed-take` (requires an existing media file), `qa-media` (mechanical checks), and legacy `init/status/sign/advance`. No evidence of a single production operator path which consumes an admitted ShotContract, binds legal references and route, invokes a video-generation executor, stores provider-issued model/run/mode/seed/cost provenance and media bytes, and sends the result through actual human/independent playback to revisions/LEARN. Writing yet another role workflow or declaring this as complete would be incorrect.

**Required acceptance:** one short original/animated scenario + one fact-sensitive explainer traverse authentic source/claim → plan → references → admitted provider render or explicitly blocked authorization → real media → observed QA → rejection/revision → improved or inconclusive re-review → reusable scoped lesson. Generate paid video only with explicit authorization, never fake real model results. Prove both success and relevant fail/recovery paths.

### P0: Structural admission and real outcome assurance are different

`evaluate_take_promotion` historically allowed `PROMOTE` with no technical QA evidence. Candidate fixes require `technical_qa_refs`, but a supplied string ref is still not an independently validated SHA-bound result. `MediaGraph.promote_asset` only checks graph decision/state, not the whole specialist/right/truth/independent-playback production admission. These are **separate** owners currently requiring a real binding, not evidence of film clearance merely because graph `PROMOTED` was set. `admit_release` similarly validates declared refs, not their physical truth. Fast-fail with `UNVERIFIED` until source, media and review receipts are actually inspected.

### P0: Latest plan state must constrain reads and all release surfaces

Prior graph allowed a promoted child Take to remain discoverable until explicit invalidation, even after ancestor plan became stale. Candidate repair makes asset-state/current-promoted/timeline readers resolve effective transitive freshness and prohibits stale promotions. Preserve non-destructive history and validate this through release-facing timeline tests after final HEAD CI.

### P1: File and execution recovery

At audit intake, `MediaGraphStore` and legacy `ProjectStore` used fixed `.tmp` names with `os.replace`, exposing stale-write/lost-update risk. The PR now has shared `checkpoint_io.py` (file lock, unique temporary file, revision-CAS, fsync, explicit post-rename uncertainty) and two stores consume it. Tested on Linux for stale snapshots and simultaneous writers. Windows/network filesystems, event-log journaling, and multi-host asset durability remain unverified. Local media/plan paths may break after host switch; the directory does not itself preserve the underlying media bytes. No claim of durable distributed workflow or concurrent safety should be made until exercising power interruption, stale save, multiple process writes and missing/relinked assets.

### P1: Misleading quality-evidence proxies

- Source units are lexical spans and quoted coverage, not comprehension or video-semantic preservation.
- Seven prompts to one text model are simulated specialist perspectives, not seven independent certified human reviewers.
- FFmpeg-generated color/video samples test pipelines, not cinematic quality.
- A contact sheet cannot certify motion, timing, audio or audience comprehension.
- A reported `system-audit.pass` is a **code/config integrity** verdict, not a product-goal verdict.
- Media QA detects technical media defects; a known FFmpeg detector nonzero-exit issue can give false `PASS` and remains open because the earlier operation was blocked; do not silently mark it resolved.
- Story/director path defaults to 30 fps / 16:9; the integrated short-form production policy must remain context/platform-specific. Defaults cannot silently override an explicit portrait/24-fps target.

### P1: The real business flywheel is a defined hypothesis, not measured throughput

Business objects and ExperimentConclusion can represent outcomes. Current evidence does not prove platform publication, paid-media rights, factual product claims, per-video view/retention metrics, model cost/retry ROI, sponsor outcomes or cross-episode learning. The integration must preserve owner-chosen platform, truth class, commercial policy and evolving H1 creative cursor, not force every creative video through a complete sponsor or character workflow.

## 3. Architectural disposition and non-goals

Retain one Video domain and existing 0.8 native owners: EditorialPlan, MediaGraph, ShotContract, ModelRouter, Continuity, Timeline/Interchange, experiments, business metrics, quality/reviewer receipts, TechniqueLibrary/LEARN and OperatorSnapshot. Do **not** rebuild a controller, make seven roles mandatory, couple every episode to H1 completion, or promote the anecdotal H3 Chinese example to universal model/style policy.

Compared remediation options:
1. **Documentation-only / add pass tests** — insufficient: cannot create authentic film or prevent false approvals.
2. **Replace whole runtime** — unproven benefit; risks breaking protected Program state, prior API and vendor independence.
3. **Join and verify the existing owner boundaries, harden failures, then validate representative live workflows** — chosen. Production render adapters, receipts, QA and revision are incremental features of the existing architecture, not a second graph. No actual provider execution without approval.

## 4. Evidence ladder for system acceptance

| Stage | Required physical proof | Meaning when absent |
|---|---|---|
| A. Static and API | system audit, contract negatives, installed CLI, current HEAD CI | Code/config verified only |
| B. No-paid operator replay | actual CLI across sources and persisted graph, revision, crash/stale/concurrency injection, negative rights/budget paths | Execution mechanics proved only |
| C. Provider-bound output | authorized real provider call, current legal capabilities, request/response/run IDs, model/mode/seed when supported, cost, original outputs and SHA | Real render occurred; still not good |
| D. Perceptual/editorial | original source vs actual playback, blind non-self graders, frame/time-coded failures, identity, physics, emotional/narrative legibility and audio; independent execution attestations where required | Story/artistic quality evaluable, not automatically acceptable |
| E. Revisions and transfer | rejected attempt, causally targeted diff, matched comparison, external scene/genre counterexample, measured improvement/inconclusive result | Learning candidate supported, not automatically universal |
| F. Media business | actual edited platform master, release rights/truth/disclosure, audience and commercial receipts, cost per accepted shot/episode | User business objective measurable |

Only the pertinent gates may be applied for trivial prompt-only work; a full commercial episode must not skip material gates. No claim of universally zero defects: residual risks require evidence-bound state, explicit mitigation and fail-closed handling.

## 5. Next priorities and stop conditions

P0 fix release-facing freshness/read semantics and enforce a technical QA evidence precondition (candidate code under current CI). P0 then connect real ShotContract/route/generation executor provenance to the existing Take+review+LEARN chain; record `NOT_IMPLEMENTED` rather than making up production. P1 test persistent crash/restart/concurrent writes; harden real mechanical detectors when write admission permits. P1 use representative independent playback and targeted repair cycles; study only the first-party provider/media methods needed for the chosen next test. P2 prove platform and business feedback with actual receipts. Any user-uploaded original source/media and rights context remain task inputs, not claims inferred from old sample fixtures.

**Release/no-promotion rule:** PR #23 stays Draft; code CI can verify engineering improvements while whole user-goal status remains OPEN until stages C–F have relevant real evidence. The Video evolution index and this report remain supplemental evidence; `current_resume_ref` still points to the canonical PR #23 checkpoint.

## 6. Evidence and repair disposition

- **Cross-layer freshness**: candidate MediaGraph repairs apply effective transitive staleness on asset reads, current promoted pointers, and timeline consumers even if a caller forgets explicit propagation. Regression includes the previously promoted video after superseded plan.
- **Promotion floor**: candidate Production OS requires technical-QA evidence refs. A string ref alone does not prove inspected media; SHA/truth/rights and independent attestation remain required in the eventual live path.
- **Local persistence**: MediaGraphStore and ProjectStore now use one low-level CAS/lock/unique-temp primitive; regression includes two writers, a failed rename, and post-rename durability uncertainty. These are owner-local metadata guarantees, not distributed transaction or media storage guarantees.
- **Truthful audit result**: `system-audit.pass` remains compatible and explicitly reports its narrow static assurance scope. Real video, perceived story, cinematic craftsmanship and commercial outcomes are not attested by green CI.
- **First-party provider contract (studied, not executed)**: [MiniMax Create Video Generation](https://platform.minimax.io/docs/api-reference/video-generation-v2-create) defines `POST /v2/video_generation`, modality-specific legal input combinations, required model/resolution/duration and asynchronously issued task ID; [Query Task](https://platform.minimax.io/docs/api-reference/video-generation-v2-query) retrieves status and output URI. The future provider adapter must persist task identity before resuming, account for irreversible spend and failure recovery, validate reference mode and costs, and bind retrieved bytes to the owner graph. A compiled prompt is not a generated film.

**Critical remaining fact**: no authorized authentic provider execution or complete film review was performed; no unpaid offline test can prove observed scene quality or audience/business results. This is an active product-delivery risk, not a docs task.
