# Provider / Model Benchmark Protocol

Status: `CANDIDATE_METHOD_1_1__QUALITY_DATA_REQUIRES_OWNER_BENCHMARK`
Owner: `DOMAIN:video`
Purpose: turn volatile model/provider claims into comparable owner-native execution evidence without coupling business architecture to vendor names.

## 1. Principle

Official documentation can establish supported operations/inputs, conditional limits, current pricing surface, licensing/provenance claims and advertised controls. It does **not** establish our production quality score.

Production quality observations require controlled benchmark tasks, exact inputs, provider/model/API surface, run identity, output artifacts and evaluation evidence.

A benchmark result expires after a material model/API change, contradictory real production evidence, or its freshness window.

## 2. Operation profile before quality

A model is not one flat capability set. Record each legal operation surface separately when combinations differ:

- operation mode (`T2V`, `I2V`, `V2V`, `EDIT`, `EXTEND`, etc.);
- allowed duration set/range;
- output resolution/aspect constraints;
- image/video/audio reference budgets;
- source-origin constraints;
- required keyframe/reference relationships;
- region/API/queue/concurrency constraints;
- conditions/known exclusions;
- capability evidence refs and observation time.

Example principle: if reference mode supports 1080p only at a particular duration, represent that as an operation profile rather than storing independent booleans `REFERENCE_IMAGES=true`, `1080P=true`.

## 3. Benchmark pack

Maintain small but discriminating archetypes rather than one cinematic demo.

### B01 — Identity close-up
Tests face/character identity, expression/upper-face stability, material/skin stability, micro-motion and flicker.

### B02 — Full-body action / cloth / hands
Tests anatomy, action sequencing, cloth/object dynamics, hand/object interaction and temporal coherence.

### B03 — Camera choreography
Tests pan/track/orbit/dolly/tilt adherence, parallax, spatial continuity and camera-induced deformation.

### B04 — Multi-reference continuity
Tests simultaneous subject/environment/prop/style references, leakage and reference priority.

### B05 — First/last frame transition
Tests endpoint fidelity, transition logic, temporal artifacts and edit handles.

### B06 — Video modify/edit
Tests wardrobe/environment/relight/local edit, preservation of untargeted performance/camera, edit locality and source continuity.

### B07 — Long shot / extension
Tests identity/world drift, extension seam, shot transition and audio continuity when supported.

### B08 — Native audio scene
Tests dialogue timing/lip sync, voice consistency, ambience/SFX coherence, intelligibility and acoustic continuity.

### B09 — Information/diagram hybrid
Tests deliberate graphic structure, text/logo risk and whether programmatic graphics/still-motion is the better route.

### B10 — Product-truth negative control
Verifies routing/admission does **not** choose synthetic generation as factual evidence of exact product UI/material/appearance/behavior. This is a policy test, not a beauty benchmark.

## 4. Quality vector and calibration

Relevant dimensions include:
- `identity`;
- `background_world_consistency`;
- `temporal_stability`;
- `motion_physics`;
- `shot_adherence`;
- `camera_execution`;
- `composition_material_light`;
- `audio_sync`;
- `audio_craft`;
- `editability`;
- `reference_fidelity`;
- `long_horizon_continuity`.

Each stored `QualityObservation` binds:
- value (0–5);
- `rubric_id`;
- `calibration_scope` (benchmark pack/version + evaluator calibration);
- uncertainty;
- evidence class;
- evidence refs.

Numbers are directly rankable only when their rubric/calibration scope is compatible. A model self-score, a human preference study and a different benchmark-pack score do not become commensurate merely because all use 0–5.

Use uncertainty-aware lower bounds for hard production floors where configured.

Do **not** average dimensions into the only stored or authoritative routing number. Production routing forms a Pareto/non-dominated set and uses explicit shot priorities only to resolve remaining tradeoffs.

## 5. Execution receipt

Every benchmark run records:
- benchmark ID/version and calibration scope;
- provider/model/API + operation profile;
- observation time;
- provider request/run ID where available;
- input asset IDs/digests;
- prompt/parameter digest;
- output asset ref/digest;
- resolution/duration/reference/audio/source mode;
- latency;
- cash/credit cost;
- retry count;
- deterministic technical QA;
- reviewer/evaluation refs;
- uncertainty/calibration notes;
- known provider errors/moderation effects.

## 6. Review evidence classes

Keep separate:
1. deterministic measurements;
2. multimodal semantic/visual assessments bound to exact output;
3. human owner/user judgments where needed;
4. real published audience/business outcomes.

Same-chat role switching is not independent verification. If isolated reviewer infrastructure is unavailable, label the assurance ceiling rather than pretending independence.

## 7. Provider comparison

Compare only candidates satisfying the target operation profile and hard commercial/truth constraints.

Record:
- pass/fail by uncertainty-aware floor;
- calibrated quality vector;
- Pareto/non-dominated status for relevant dimensions;
- explicit priority order used when a tradeoff remains;
- cost per accepted take, not only generated second;
- latency distribution when enough samples exist;
- retry/rejection/failure taxonomy;
- edit/continuation usability.

If quality observations are calibration-incompatible, report `INCOMPARABLE` and run/refresh the needed benchmark instead of fabricating a winner.

## 8. Promotion into routing evidence

A provider observation enters production routing only when:
- current operation-profile capability refs exist;
- current terms/pricing/availability refs exist;
- benchmark/evaluation refs exist for required dimensions;
- rubric/calibration scope matches the target comparison;
- freshness/commercial constraints pass;
- no active deprecation/blocker applies.

Exploration may use weaker evidence after hard floors/rights/truth gates when the request does not require production comparison; outputs remain candidates.

## 9. Refresh triggers

Refresh when:
- model/API/version materially changes;
- reference/edit/audio/extension combinations change;
- pricing changes enough to alter route decisions;
- real production contradicts benchmark evidence;
- evidence expires;
- a strategically important new shot archetype appears;
- a new comparison requires a different calibration scope.

## 10. Current research-only observations

Current official provider surfaces in 2026 demonstrate multimodal reference, editing, keyframe/extension, native-audio and multi-resolution capabilities with nontrivial conditional combinations. They justify the `OperationProfile` schema but receive no owner quality score until benchmarked.

Rapid model additions/deprecations remain a first-class counterexample to vendor-locked architecture. Provider lifecycle evidence changes; the Media Business OS should not need architectural reconstruction when a model disappears.
