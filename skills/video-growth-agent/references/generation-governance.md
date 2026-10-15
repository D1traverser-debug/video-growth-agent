# Generation Governance

Current architecture: `docs/media_business_os.md`  
Provider benchmark method: `docs/provider_benchmark_protocol.md`

## Core boundary

Generation is not one gate. Treat these as separate governed events:

1. **candidate generation admission**;
2. **promotion to an accepted/current/canon project asset**;
3. **release admission**.

A safe candidate may exist without being approved. An unavailable release-grade reviewer must not automatically make all exploration impossible. Conversely, a file that looks good may never become accepted/canon/final merely because it exists.

The historical strict `generation_guard` remains available for legacy/high-assurance paths that intentionally require pre-generation isolated review. It is no longer the universal prerequisite for every bounded candidate experiment.

## No ungoverned side-channel promotion

Do not call an image/video/audio generator and then silently mount the output into durable accepted project state.

Any durable candidate generation must bind:

- exact project/context/shot identity;
- exact reference asset IDs/digests and intended roles;
- rights/consent evidence;
- current provider/capability evidence;
- mode/parameter/prompt/edit contract digest;
- truth mode;
- budget/retry/stop conditions;
- resulting artifact ref/digest and generation receipt.

A direct current-session tool call may be a valid executor when the session capability is real and the candidate admission is recorded. It does not become independent review or final authorization by virtue of being inside ChatGPT.

## Candidate generation admission

Before spending credits or creating durable media, require:

- clear narrative/explanatory job;
- must-have / must-not-have constraints;
- allowed generation/acquisition modes;
- reference bindings;
- current provider/tool capability and availability;
- commercial-use/rights/consent admission where applicable;
- product-truth compatibility;
- cash/credit/retry budget;
- graceful-degradation and stop conditions.

Exploration may use lower resolution, still/keyframe prototypes and cheaper sufficient engines. Candidate outputs remain `CANDIDATE` until explicitly promoted.

## Shot/reference contract

For modern multimodal generation, a prompt is subordinate to the shot/reference contract. Capture as applicable:

- narrative job and world/beat state;
- duration/aspect/output target;
- image/video/audio reference roles;
- identity/continuity requirements;
- first/last-frame or keyframe requirements;
- camera/action/physics requirements;
- native audio/dialogue/SFX requirements;
- quality-vector floors;
- truth/risk class;
- budget and retry limit;
- stop conditions;
- exact provider request/prompt/edit digest.

Do not encode stable character/product/business truth only inside free-form prompt text.

## Provider evidence semantics

Provider/model capabilities, price, availability, terms and deprecation state are volatile observations. Official documentation can establish current supported controls/limits/terms; it does not establish our production quality score.

Production quality routing uses owner benchmark or exact production evidence bound to outputs. Provider-issued request/run IDs, local context/trace IDs, raw request/response digests and proof refs remain separate evidence classes.

## Promotion gate

Generated output is evidence, not success.

Promotion evaluates the exact take against the shot-specific quality vector and risk:

- identity/subject continuity;
- world/background consistency;
- temporal stability/flicker;
- motion/physics;
- shot/prompt adherence;
- camera execution;
- visual craft;
- audio sync/craft where relevant;
- editability/extension quality;
- truth/product fidelity;
- rights/provenance;
- platform/brand/IP constraints.

HIGH/HERO/BRAND_TRUTH assets require proportionate independent evidence when the policy says so. If `ATTESTED_ISOLATED` review is required but no trusted executor is actually available, promotion is blocked; the candidate may remain historical/exploration evidence.

Low-risk candidates may promote under a lighter declared evidence tier when their exact policy permits it.

## Legacy strict pre-generation challenge

Some historical projects or explicit high-assurance work may still invoke `generation_guard.py`.

When that path is selected, Art Director, Creative Director and Red Team review evidence must be resolved outside the brief and bound to its exact digest. Inline `PASS` text is never proof. Required execution/run/context/trace identities must remain distinct as configured.

Do not weaken that legacy path merely because the new architecture also supports a lighter candidate-only exploration path. These are different assurance contracts.

## Product-truth rule

For exact factual product appearance, UI, material, configuration or demonstrated behavior, synthetic media cannot serve as observed evidence. Use verified real/authorized product assets at truth-critical points or frame generated material explicitly as explanatory/hypothetical visualization.

Real-person likeness/voice references require consent/authorization evidence.

## Edit/modify/extend before regenerate

When a take is close and the current tool supports controlled modify/edit/extend/retime/local repair, compare expected acceptance cost with full regeneration. Preserve untargeted performance/camera/content when possible.

Every edit creates a derived asset/version with lineage; it never destructively overwrites the accepted original.

## Post-generation learning

A failed take must feed a typed failure taxonomy and, when material, a learning candidate. Do not keep rewriting prompts blindly while repeating the same mechanism.

Track:
- provider/model/mode;
- benchmark/shot archetype;
- cost/latency;
- retry/rejection reason;
- quality-vector failure;
- whether a different control/edit/degradation route solved it.

A useful provider-specific lesson is volatile and may expire. A durable production rule needs scope/generalization analysis, counterexamples and regression/replay evidence.

## Dedicated improvement cell

Production Methodologist scouts mechanisms and benchmarkable alternatives. Red Team searches for counterexamples/self-deception. Evolution Engineer proposes the smallest durable rule/test/config change and identifies what it supersedes. Owner promotion remains separate.

The improvement cell may recommend a provider benchmark or architectural repair, but it may not convert vendor marketing copy, one good generation or one viral episode directly into production doctrine.
