# GPT Images Prompting Method — V2

Status: ACTIVE_PROJECT_METHOD
Scope: project-local only
Purpose: adapt character-design generation to GPT Images / ChatGPT image-generation behavior rather than generic diffusion-model prompt habits.

## 1. Core model assumption

There is no special secret syntax required. GPT image models are instruction-following multimodal models and respond best to clear natural-language intent, visible details, composition, style and constraints.

Project rule:
- do not write Stable-Diffusion-style keyword soup;
- do not assume weighted-token syntax;
- do not use giant negative-prompt dumps as the primary control method;
- use concise natural language with explicit task purpose and visible design differences.

## 2. Prompt hierarchy for this project

For a new generation, structure prompts as:
1. TASK / intended use;
2. SUBJECT baseline;
3. COMPOSITION / viewpoint;
4. VISIBLE design variables under test;
5. RENDER / light / material only as needed for fair comparison;
6. MUST KEEP / MUST NOT INTRODUCE constraints;
7. OUTPUT contract.

For complex character-design studies, short labeled sections are preferred over one unbroken paragraph.

## 3. Keep comparison prompts minimal

When comparing F1-F5 face architectures:
- keep one short common base prompt identical;
- vary only the face-architecture block;
- do not include downstream lore, wardrobe, pixel DNA, Shiba-carp motifs or Presentation Modes;
- do not describe hidden details that cannot affect the current gate.

Reason:
Long prompts can work, but they increase confounds and make it harder to determine which instruction produced which visual difference.

## 4. Reference-image policy

OpenAI guidance supports multiple images but recommends a small set with explicit roles.

Project rule:
- H1 first-pass front-face comparison: no reference image uploaded to the generator; use morphology extracted from the certificate portrait;
- H1 finalists / later identity lock: use a small set of real-face references only when same-source resonance needs to be verified;
- label images by role, e.g. `Image 1 = neutral front morphology reference`, `Image 2 = left 3/4 reference`;
- never feed pixel avatar, real portrait and Shiba-carp image together during Human Core face construction;
- do not let a style image silently become an anatomy reference.

## 5. Edit-first convergence after selection

Once one face architecture passes:
- stop regenerating unrelated identities;
- use targeted edits;
- state: `Change only X. Keep face identity, skull shape, camera, lighting, expression and all other features unchanged.`
- adjust one design variable at a time.

This applies later to hair, grooming, eyewear and wardrobe.

## 6. Model-facing language

Prefer observable language:
- `slightly wider cheek mass`;
- `compact blunt chin`;
- `horizontal eye orientation`;
- `low-contrast soft frontal-side light`.

Avoid relying on abstract labels alone:
- `smart`;
- `premium`;
- `meme`;
- `cinematic`;
- `advanced`.

Abstract intent may be included only when followed by visible implementation.

## 7. Camera language

Camera and lens terms are appearance cues, not exact physical guarantees.
Use them to stabilize comparison, not as scientific measurement.

For H1:
- eye-level;
- front view first;
- neutral portrait perspective around classic portrait range;
- same framing and background for every candidate.

## 8. Negative constraints

Use a short, high-value exclusion set only for predictable failure modes.

For H1 the priority exclusions are:
- no V-shaped pointed chin;
- no K-idol / generic AAA handsome template;
- no beauty-ad makeup/skin;
- no fantasy anatomy;
- no branded hair/accessory/clothing.

Do not enumerate dozens of unrelated exclusions.

## 9. Iteration protocol

GPT Images should be debugged with small targeted revisions.

Process:
1. generate base candidate;
2. identify one structural failure;
3. issue one targeted correction;
4. explicitly preserve everything else;
5. compare before/after;
6. only then make another change.

Do not respond to a bad face with a complete rewritten character prompt.

## 10. Photo acquisition policy

Current H1 can proceed with the existing certificate portrait because morphology has already been extracted.

Additional photos are optional now but valuable before final Human Core lock:

Face set:
- neutral unfiltered front;
- left 3/4;
- right 3/4;
- one clean side profile, preferably both sides if convenient;
- eye-level, neutral expression, natural diffuse light;
- no beauty filter, heavy makeup or wide-angle selfie distortion;
- simple hair pulled/kept away enough to reveal face outline and ears where possible.

Body set for H2/H9, only if convenient:
- front / side / back full-body;
- plain fitted T-shirt or close-fitting top and simple straight/fitted trousers;
- flat shoes or barefoot;
- neutral stance, arms relaxed;
- rear camera, avoid ultra-wide, enough distance to minimize perspective distortion.

The body set is for plausibility/proportion reference, not literal likeness replication.

## 11. Current H1 prompt compression rule

The existing detailed H1 prompt file remains a design specification, but generator-facing prompts should be compiled down to a shorter form:
- 1 task sentence;
- 1 common anatomy paragraph;
- 1 variant paragraph;
- 1 presentation/constraint paragraph.

Do not paste the full design Bible into GPT Images.

## Official OpenAI guidance basis

- OpenAI Academy — Creating images with ChatGPT: clear descriptive prompts, often 1–3 sentences; specify purpose/subject/action/style; use framing/light/constraints when material; improve through small targeted revisions; use small, explicitly-role-labeled reference sets.
- OpenAI Image Prompting Guide — define intended result, composition, visible details and constraints; labeled sections are useful for complex prompts; prompt format can be natural language/structured as long as maintainable; iterate instead of overloading; camera specs are visual cues rather than exact simulation.
- OpenAI Image Generation Guide — for precise edits, describe the edit directly and preserve unchanged elements; multi-turn image editing is supported.
