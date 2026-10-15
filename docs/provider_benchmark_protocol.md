# Provider / Model Benchmark Protocol

Status: `CANDIDATE_1.0`
Owner: `DOMAIN:video`
Purpose: turn volatile model/provider claims into comparable owner-native execution evidence without coupling business architecture to vendor names.

## 1. Principle

Official documentation can establish supported inputs, limits, price surface, licensing/provenance claims and advertised controls. It does **not** establish our production quality score.

Production quality observations require the same benchmark tasks, exact inputs, current provider/model/version, run identity, output artifacts and review/evaluation evidence.

A benchmark result expires when a material model/version/API change occurs or when its configured freshness window expires.

## 2. Benchmark pack

Maintain small but discriminating shot archetypes rather than one cinematic demo.

### B01 — Identity close-up
Tests:
- face/character identity preservation;
- expression control;
- upper-face/eye stability;
- skin/material stability;
- micro-motion and flicker.

Inputs:
- fixed canon front/3Q references;
- fixed lighting/camera contract;
- neutral motion prompt.

### B02 — Full-body action / cloth / hands
Tests:
- anatomy;
- action sequencing;
- cloth/object dynamics;
- hand/object interaction;
- temporal coherence.

### B03 — Camera choreography
Tests:
- pan/track/orbit/dolly/tilt instruction adherence;
- foreground/background parallax;
- spatial continuity;
- camera-induced deformation.

### B04 — Multi-reference continuity
Tests:
- subject + environment + prop + style simultaneous reference use;
- wrong-reference leakage;
- reference priority/instruction following.

### B05 — First/last frame transition
Tests:
- endpoint fidelity;
- transition logic;
- temporal artifacts;
- usable edit handles.

### B06 — Video modify/edit
Tests:
- wardrobe/environment/relight/local edit;
- preservation of untargeted performance and camera;
- edit locality;
- source temporal continuity.

### B07 — Long shot / extension
Tests:
- identity/world drift with duration;
- shot transition continuity;
- audio continuity where supported;
- extension seam quality.

### B08 — Native audio scene
Tests:
- dialogue timing/lip sync;
- voice consistency;
- ambience/SFX coherence;
- intelligibility and acoustic continuity.

### B09 — Information/diagram hybrid
Tests:
- ability to preserve deliberate graphic structure;
- text/logo risk;
- whether the correct route should instead be programmatic graphics/still-motion.

### B10 — Product-truth negative control
Purpose:
- verify the router does **not** choose synthetic generation as factual evidence for exact product UI/material/appearance/behavior.

This is a policy/admission test, not a beauty benchmark.

## 3. Quality vector

Score each relevant dimension 0–5 with artifact-bound evidence:

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

Do not average dimensions into the only stored number. Shot routing applies its own weights/floors.

## 4. Execution receipt

Every benchmark run records:

- benchmark ID/version;
- provider/model/API surface;
- exact observation time;
- provider request/run ID where available;
- input asset IDs/digests;
- exact prompt/parameter digest;
- output asset ref/digest;
- resolution/duration/audio mode;
- generation time/latency;
- cash/credit cost;
- retry count;
- deterministic technical QA;
- reviewer/evaluation refs;
- known provider errors or moderation effects.

## 5. Review strategy

Use three evidence classes separately:

1. deterministic measurements (duration, dimensions, media integrity, loudness etc.);
2. multimodal semantic/visual assessment bound to exact output;
3. human owner judgment for final production utility when needed.

Same-chat role switching is not independent verification. When isolated reviewer infrastructure is unavailable, mark assurance honestly and keep the result below `ATTESTED_ISOLATED`.

## 6. Provider comparison

Compare only models that satisfy hard input/output/commercial constraints for the benchmark. Record:

- pass/fail by required quality floor;
- quality vector;
- cost per accepted take, not only cost per generated second;
- median/percentile latency where enough samples exist;
- retry/rejection rate;
- failure taxonomy;
- usable edit/continuation rate.

The cheapest generated second can be more expensive in production if rejection/retry is high.

## 7. Promotion into routing evidence

A provider observation may enter production routing only when:

- current capability/terms/pricing/availability refs exist;
- benchmark output/evaluation refs exist for dimensions required by the target shot class;
- freshness policy is satisfied;
- commercial-use requirements are satisfied;
- no active deprecation/blocker applies.

Exploration may use weaker quality evidence when the request has no production quality floor, but outputs remain candidates.

## 8. Refresh triggers

Refresh a benchmark when:

- provider/model major/minor version materially changes;
- API adds/removes important reference/edit/audio behavior;
- price changes enough to alter routing;
- a real production failure contradicts the benchmark;
- benchmark evidence exceeds the configured freshness window;
- a new shot archetype becomes strategically important.

## 9. Current research-only observations

As of 2026-10-15, external official/current surfaces show major capability classes across Seedance 2.5, Veo 3.1, Runway Gen-4.5, WAN 3, Kling O3/3, Luma Ray3 Modify and modern audio/editing systems. These observations justify the registry schema but do not receive owner quality scores until benchmarked.

The prior Sora lifecycle is retained as a provider-deprecation counterexample: a model/product may disappear while the production architecture must remain usable.
