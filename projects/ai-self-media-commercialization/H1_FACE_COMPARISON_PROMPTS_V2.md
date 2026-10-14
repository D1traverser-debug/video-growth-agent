# H1 Face Comparison Prompts — V2

Status: READY_FOR_EXECUTION
Scope: H1 Face Primary Masses only
Purpose: compare five face architectures while holding all non-face variables constant.

## Execution protocol

- First pass is FRONT VIEW ONLY.
- Use one fresh image-generation conversation per candidate F1-F5 to avoid cross-contamination.
- Do not upload the certificate photo in the first pass. The morphology has already been extracted into structural language; this avoids collapsing back into a digital clone.
- Do not use the rejected Concept V1 as a reference.
- Keep all non-face variables identical across all five candidates.
- Generate one image per candidate.
- After all five are reviewed, advance only the leading 2-3 candidates to 3/4 view.

## Common base prompt

Create a neutral front-view character face study for an original young adult Chinese male digital-IP Human Core.

This is NOT a beauty portrait, fashion portrait, game-character promo, cosplay image, or final branded character. It is a facial-architecture comparison study.

Keep the entire image visually neutral so that only facial primary masses can be judged.

Subject baseline:
- Chinese adult male, visual age around mid-20s;
- believable human anatomy;
- calm neutral expression;
- adult, not adolescent;
- not muscular, not rugged, not hyper-masculine;
- no stylized fantasy anatomy.

Shared source-derived structure that must remain present in every candidate:
- moderately elongated soft-rectangular / oval overall face envelope, never a narrow V-face;
- visible cheek support around the zygomatic region;
- lower face tapers gradually, not sharply;
- compact rounded-blunt chin, not pointed and not lengthened;
- relatively horizontal brow-eye organization;
- moderate brow-to-eye compression rather than high arched beauty brows;
- eyes horizontally oriented with moderate-narrow vertical aperture and no aggressive fox-eye / villain-eye cant;
- balanced eye spacing;
- natural medium-width nose with moderate bridge and softly compact tip, not a razor-narrow CG nose;
- moderate mouth width, restrained lip contour;
- compact mouth-to-chin relationship;
- natural human asymmetry may exist but must not become a gimmick.

Rendering and presentation lock:
- front view, head and upper neck only;
- camera at eye level;
- approximately 85mm-equivalent portrait perspective;
- simple dark plain short hair with low volume, no fashionable haircut, no bangs designed as a signature;
- dark natural eyes;
- no cyan hair;
- no blue-violet irises;
- no glasses;
- no pixel accessories;
- no jewelry;
- no fashion styling;
- no visible costume design, only a plain dark crew-neck or neutral collar edge if needed;
- near-monochrome / very low-saturation neutral color treatment;
- simple mid-gray background;
- large soft frontal-side light, low contrast, enough to reveal brow, cheek, nose, jaw and chin planes;
- no rim light, no cinematic color grading, no dramatic shadow;
- realistic human skin volume with minimal texture, no makeup, no whitening, no beauty smoothing, no glossy skin;
- stylized realism only to the degree needed for clean form readability; do not turn the face into an anime or AAA-game beauty template.

The image must be useful for judging:
1. skull/face width-height balance;
2. brow plane;
3. eye-socket placement;
4. cheek mass;
5. jaw angle and width;
6. chin mass;
7. nose volume;
8. mouth-to-jaw relationship.

Do not optimize for conventional handsomeness. Optimize for coherent, memorable adult facial construction.

VARIANT-SPECIFIC ARCHITECTURE:
[INSERT ONE VARIANT BLOCK BELOW]

Output exactly one neutral front-view head study. No labels, no text, no collage, no second person.

## Variant blocks

### F1 — Same-Source Natural / control

Keep the shared source-derived structure close to its natural baseline.
- preserve moderate face length;
- preserve soft-rectangular/oval envelope;
- preserve existing cheek support without amplifying it;
- jaw remains soft but present;
- chin remains compact and rounded-blunt;
- eyes remain calm, horizontal and moderately narrow;
- nose and mouth remain natural and unoptimized;
- use only mild stylization.

Goal: establish the control sample with the strongest same-source structural resonance while still being an original character, not a portrait clone.

Reject if it becomes a beautified version of a real person, a K-idol face, or a generic game male.

### F2 — Blunt Analytical / leading candidate

Shift the facial architecture toward greater structural stability without making the face square or heavy.
- increase cheek-mass support slightly;
- preserve visible lateral support through the lower cheek and upper jaw;
- reduce lower-face taper compared with a beauty template;
- make the jaw feel more stable and less narrow;
- shorten and strengthen the chin mass slightly while keeping it rounded-blunt;
- keep eyes calm, horizontal and moderately narrow;
- keep nose volume natural and medium rather than refined or narrow;
- keep the mouth restrained and proportionate.

The face should feel intelligent, adult, grounded and difficult to replace with a generic handsome template.

Do NOT make him broad-faced, rugged, macho, older, stern, or square-jawed.

### F3 — Editorial Plane / leading candidate

Keep the source-derived envelope but clarify large facial planes rather than changing the proportions dramatically.
- brow plane should read more clearly;
- orbital depth should be slightly more legible;
- cheek plane should be cleaner and more sculptural while retaining cheek support;
- jaw plane should be more readable but not sharp;
- soft tissue should feel slightly leaner and more controlled;
- chin stays compact and blunt, never elongated;
- eye shape remains calm and horizontal;
- nose remains natural, not model-perfect;
- mouth remains quiet and restrained.

The result should have stronger photographic/editorial presence because of clear planes, not because of fashion-model beautification.

Reject if it becomes gaunt, severe, runway-mannequin-like, sharp-jawed, or conventionally luxury-model handsome.

### F4 — Compact Deadpan / leading candidate

Shift the face toward stronger low-expression readability and a slightly more compact lower-face rhythm.
- retain cheek width/support;
- slightly reduce the perceived vertical length of the lower face;
- keep the chin compact and rounded-blunt;
- reduce eye aperture slightly while preserving horizontal orientation;
- brow-eye distance may be slightly tighter than the control, but still human and natural;
- keep the mouth relaxed, low-drama and close to horizontal;
- keep nose volume natural and centered;
- preserve adult male credibility.

The face should read as calm, self-contained and naturally deadpan even before any acting is added.

Do NOT make him sleepy, sad, bored, expressionless like an android, or childishly cute.

### F5 — Controlled Uncanny Human / boundary experiment

Preserve fully believable human anatomy and the same-source face envelope, but introduce exactly ONE subtle proportion anomaly.

Choose only one of these anomaly strategies and keep all other facial relationships natural:
A. slightly tighter-than-usual brow-to-eye spacing while remaining believable;
OR
B. a subtly unusual cheek-to-chin transition where the cheek support remains strong and the compact chin arrives with a slightly unexpected rhythm.

Do not combine both anomaly strategies.
Do not alter eye color, skin, ears, nose, hair or any other feature to create strangeness.

The result should be recognizably human at first glance, with a faint second-look distinctiveness.

Reject if it reads alien, synthetic, uncanny-valley, fashion-experimental, or obviously stylized.

## Review rubric

Score each candidate 1-5 on:
- DISTINCTIVE_WITHOUT_BRANDING
- ADULT_MALE_CREDIBILITY
- SAME_SOURCE_RESONANCE
- ANTI_GENERIC_STRENGTH
- DEADPAN_COMPATIBILITY
- COMMERCIAL_TRUST
- AI_VIDEO_STABILITY
- CAN_SURVIVE_DARK_HAIR_DARK_EYES_NO_ACCESSORY

Automatic FAIL conditions:
- sharp V chin;
- generic K-idol / AAA male;
- beauty-ad skin or makeup;
- obvious clone of the creator;
- fantasy/alien anatomy;
- identity depends on hairstyle, lighting or accessory;
- exaggerated masculinity/ruggedness;
- adolescent/boyish read.

## Advance rule

Do not choose a winner from one attractive image.

After F1-F5 front views:
1. reject failures by structure first;
2. retain the top 2-3 architectures;
3. generate matching 3/4 studies for only those finalists;
4. if one architecture wins front but fails 3/4, it is not H1 PASS;
5. only after front + 3/4 coherence may the project lock one face architecture or a deliberate hybrid and proceed to H2 body archetype.
