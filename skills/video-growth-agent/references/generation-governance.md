# Generation Governance

Use this policy for any quality-critical image or video generation, including exploratory keyframes that may influence LOOKDEV or VISUAL_PREVIEW.

## No side-channel generation

Do not call an image/video generator directly from the conversational surface merely to "see what happens" when the output is part of an active durable production project. A quality-critical generator call must be backed by a generation brief and must not bypass the studio's maker/reviewer split.

Direct generation without this brief is process-invalid even if the pixels look good. It may not be promoted into LOOKDEV, VISUAL_PREVIEW, ASSET_BUILD or ROUGH_CUT.

## Mandatory generation brief

Before generation, record:

- narrative_job: what this shot/frame changes for the viewer;
- before_state;
- crossing_state or transformation mechanism;
- after_state;
- must_have;
- must_not_have;
- benchmark_refs;
- engine_route and why this engine is justified;
- quality_floor;
- stop_conditions: conditions that should cancel generation before spending credits;
- exact prompt or shot contract to be sent to the engine.

The prompt is subordinate to the brief. If the prompt contradicts any must_not_have item, weakens the required before/crossing/after transformation, or replaces a narrative action with generic UI/AI iconography, generation is blocked.

## Pre-generation challenge

For quality-critical visual work, run a pre-generation challenge before spending credits or presenting the image to the user:

1. Visual Designer creates the brief and candidate prompt.
2. Art/Creative critique asks whether the prompt itself is already drifting toward PPT, SaaS dashboard, floating cards, generic cyberpunk, cute AI mascots, empty neon, stock-photo office imagery or explanatory labels instead of cinematic action.
3. Red Team states the strongest reason this prompt is likely to generate the wrong movie.
4. Only unresolved-free briefs with verified execution evidence are allowed to reach the generation engine.

The reviewer must inspect the actual prompt, not merely the intended idea.

### Evidence boundary

`pre_generation_challenge` inside the brief is status and human-readable rationale only. A literal `PASS` written into that JSON is **not** proof that Art/Creative or Red Team actually executed.

Authorization evidence must be resolved outside the brief from the owner execution path and then bound back to the exact brief digest. At minimum, each required reviewer proof must bind:

- work-order identity;
- immutable review receipt reference;
- execution-attestation reference;
- executor and execution identity;
- provider run/request identity;
- context/trace correlation identity;
- review packet and result digests;
- exact generation-brief digest;
- inspectable proof reference.

Sibling challenge executions may not reuse execution/run/context/trace identities. The machine guard rejects an inline self-authored PASS when no externally resolved evidence bundle is supplied.

The current `generation_guard` validates completeness, prompt contradictions and evidence-bundle shape/digest binding. It does **not** itself prove that a referenced receipt exists or that an executor/provider is trusted. Those are owner-runtime/gateway responsibilities.

Until a single enforced quality-critical generation gateway resolves those receipts from authority and binds the subsequent provider call/artifact back to the authorization, generation remains fail-closed for promotable project media. Do not reinterpret a structurally valid brief as production authorization.

## Provider-evidence semantics

Do not describe locally supplied correlation IDs as provider-issued proof. Provider-issued request/run IDs and model identity, local context/trace IDs, raw request/response digests and durable proof references are different evidence classes. A provider adapter may enter the trusted executor registry only after its real API semantics and modality access are verified and the runtime can distinguish these classes truthfully.

## Post-generation rule

Generated output is evidence, not success. Compare actual pixels/playback with the brief and benchmark pack. If the image only communicates the concept because of labels, feature menus, logos, floating windows or an AI mascot, treat that as a likely visual-explanation failure unless those elements are specifically required by the story.

A failed output must feed back into the brief or technique library; do not simply rewrite the prompt ad hoc and retry.

## Dedicated improvement cell

When a recurring failure or capability gap appears:

- Production Methodologist owns scouting and mechanism distillation. It does not approve its own recommendation.
- Red Team attacks the proposed lesson and searches for counterexamples and self-deception.
- Evolution Engineer converts only accepted lessons into the smallest durable rule/test/config change and removes superseded mechanisms.

The scheduled LEARN pipeline is itself governed work. The base runtime must require its configured work orders; manually creating `learning_receipt` plus role PASS records cannot substitute for Methodologist/Evolution/Red-Team/Showrunner execution evidence.

This cell exists to prevent the executive producer from simultaneously creating, judging, learning and rewriting the system from one context.
