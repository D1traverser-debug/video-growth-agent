# Video Growth Agent — Architecture

Status: `CANDIDATE_0_8_0`
Owner: `DOMAIN:video`
Primary product architecture: `docs/media_business_os.md`
Architecture-experience scenarios: `docs/agent_operability_scenarios.md`

## 1. Topology

`UAOS common control/governance -> directly selected Video domain -> child-owned Media Business Program -> editorial/business intent -> media contexts/assets/tasks/evidence/decisions -> platform/commercial outcomes -> experiments/learning`

UAOS does not own Video business identities/state. Video does not implement a second parent controller.

## 2. Concern views, not one universal diagram

Architecture representation follows the question:

- **authority/business structure** — Program/workstream/owner/context views;
- **editorial reasoning** — intent/claim/beat/shot dependency views;
- **media dependency/change impact** — MediaGraph asset/task/evidence/decision lineage;
- **cross-shot continuity** — dimension/rule links between shots;
- **temporal edit state** — TimelineSpec/track/clip/marker/variant views;
- **model choice** — operation constraints + calibrated quality vector/Pareto view;
- **growth learning** — hypothesis/variant/metric/outcome experiment view;
- **Agent usability/recovery** — derived OperatorSnapshot + scenario walkthrough.

Do not force spatial, sequence, DAG or state-machine notation where it does not answer the concern.

## 3. Context hierarchy

`Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take`

Core stable objects:
- Context;
- AssetVersion/lineage;
- Task;
- Evidence;
- Decision;
- Rights/Consent;
- Cost;
- PlatformVariant;
- Performance/Commercial receipts;
- LearningCandidate.

Current 0.8 editorial/operability objects extend this substrate rather than replace it.

## 4. Executable editorial bridge

`editorial_planning.py` owns:

`EpisodeIntent -> ClaimSpec -> BeatSpec -> ShotIntent -> EditorialPlan`

Factual/product-truth claims require evidence. Beats have explicit audience/narrative jobs and dependencies. Shots bind claims, truth/risk, allowed production modes, continuity/reference intent and a business/creative value vector.

`materialize_shot_contract()` crosses the explicit boundary into production and binds `editorial_plan_ref`, beat, claims, continuity and value into `ShotContract`.

`plan_graph_bridge.py` registers immutable EditorialPlan versions as MediaGraph assets. Production work can therefore bind and stale against exact upstream plan versions.

## 5. MediaGraph

`media_graph.py` remains the only canonical media dependency/lineage graph.

It owns stable Context/AssetVersion/Task/Evidence/Decision metadata, promotion pointers, persistence and downstream invalidation. 0.8 does **not** add a parallel dependency graph for story/editorial decisions; it inserts editorial-plan assets into the existing graph.

## 6. Shot/take production boundaries

`production_os.py` owns ShotContract/ReferenceBinding/Take and candidate-generation, promotion and release admission.

`generation admission != asset promotion != release admission`

Candidate generation can produce learnable material after current legal/capability/right/budget/truth gates. Promotion adds quality/continuity/truth/rights/risk-proportional evidence. Release remains fail-closed on final-media/timeline/QA/rights/truth/provenance/disclosure/platform validation and owner.

## 7. Cross-shot continuity

`continuity.py` owns explicit shot-to-shot continuity state:
- snapshot dimensions;
- `PRESERVE`, `EXPECT`, `ALLOW_CHANGE` rules;
- HARD/SOFT severity;
- dimension-level violations.

This prevents both under-specification (“same character, somehow”) and over-freezing (intentional wardrobe/location/time change mislabeled as drift).

## 8. Model/provider boundary

`model_registry.py` is provider-neutral and evidence-bound.

### Operation profiles

Capabilities are legal operation combinations, including mode, duration, resolution, reference budgets and source constraints. Provider names never become business rules.

### Quality observations

Quality binds value + rubric + calibration scope + uncertainty + evidence class/refs. Values from incompatible rubrics/scopes are not directly ranked.

### Routing

Hard gates precede optimization. Exploration selects cheapest sufficient execution. Production compares uncertainty-aware quality lower bounds, forms the Pareto front, then uses explicit shot priorities only when tradeoffs remain. No hidden weighted-average quality becomes the current production authority.

`engine_routing.py` remains legacy compatibility only and is no longer a current top-level package export.

## 9. Timeline and external editor boundary

`timeline.py` owns non-destructive editor-neutral timeline versions referencing promoted media assets.

`editorial_interchange.py` owns external handoff/roundtrip evidence:
- exact internal timeline version;
- source asset refs/digests;
- interchange format;
- current adapter capability evidence;
- external project/composition identity when applicable;
- returned edit identity/digest/change/execution receipts.

External editors never own canonical business truth and never silently overwrite the master.

## 10. Growth experiment boundary

`experiments.py` owns preregistered media experiments:
- hypothesis;
- variants;
- changed/fixed variables;
- primary metric semantics/guardrails;
- observation/stop rules;
- evidence;
- winner/no-clear-winner/inconclusive/guardrail-stop conclusions.

Multi-variable package tests are permitted but cannot claim single-variable causality.

## 11. Business objects and outcomes

`business_objects.py` owns typed portfolio, distinctive-asset, commercial-fit, rights, offer and business-hypothesis objects.

`business_metrics.py` owns platform, production and commercial outcome receipts. There is no universal composite business score.

Business flywheel edges define legitimate cross-workstream evidence/decision influence; they do not create hidden state mutation.

## 12. Current-Agent operating projection

`operator_view.py` derives an `OperatorSnapshot` from owner state. It can expose:
- governing outcome/current focus;
- READY/BLOCKED/WAITING/OPTIONAL/DONE actions;
- expected progress evidence;
- pending decisions;
- stale assets/evidence;
- capability/budget blockers;
- resume/recovery refs.

It cannot promote, mutate canon, change Program authority or create a single artificial “global next action” when parallel work is legitimately ready.

## 13. Original IP/canon

Canon remains versioned assets/evidence covering identity geometry, expressions, wardrobe/props, material/light grammar, voice/performance, signature motion, world grammar, distinctive visual/audio motifs, allowed variants and rights/likeness constraints.

Identity-sensitive shots bind exact canon versions plus explicit continuity dimensions. Canon changes stale only consuming descendants.

## 14. Program orchestration vs production graph vs timeline

Keep these distinct:
- Program graph — why/when a business task is ready;
- editorial plan — what the episode is arguing/showing and why;
- MediaGraph — which assets/tasks/evidence/decisions depend on what;
- continuity links — what state should change/persist between shots;
- timeline — temporal assembly of promoted media;
- experiment plan — what causal/product hypothesis is being tested;
- operator projection — how a current Agent sees the actionable surface.

Do not collapse them into one giant DAG or one mega-state machine.

## 15. Common Behavior and architecture experience

`owner_behavior_admission.py` realizes recover-before-escalate and repair-or-block semantics.

Material architecture/experience changes also use UAOS architecture-experience semantics: separate user goals from examples, select views by concern, walk primary/failure/recovery/resume scenarios and dogfood from the current Agent perspective before promotion.

Canonical Video scenarios live in `docs/agent_operability_scenarios.md`.

## 16. Assurance

Assurance terms remain:
- `DECLARED_ONLY`;
- `HARNESS_WIRED`;
- `SESSION_EXECUTABLE`;
- `CHAT_BRIDGED`;
- `ATTESTED_ISOLATED`.

Repository/CI checks must fail closed if declared current 0.8 runtime surfaces, entrypoints, version bindings or protected H1 state drift.

## 17. Protected state and negative space

Forbidden:
- provider lock-in as architecture;
- chat/prompt memory as canon;
- destructive overwrite of accepted assets;
- candidate presence as approval;
- self-approval;
- hidden scalar quality/business authority;
- flat capability claim as proof of every conditional operation;
- operator projection as second controller;
- duplicated Video business state in UAOS;
- sponsorship overriding truth;
- architecture maintenance auto-advancing H1/A2 creative work.
