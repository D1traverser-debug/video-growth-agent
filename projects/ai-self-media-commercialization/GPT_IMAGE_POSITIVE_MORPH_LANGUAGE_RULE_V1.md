# GPT Image Positive Morph Language Rule — V1

Status: ACTIVE_PROJECT_METHOD
Scope: Human Core and later controlled character edits

## Why this rule exists

Negative-prompt-heavy instructions repeatedly produced weak, ambiguous or under-executed edits. GPT image editing is more reliable when the prompt specifies the exact visible target morphology and clearly names what remains fixed.

## Core rule

For controlled character edits, use this order:
1. identify the SINGLE source image / active face shell;
2. state the editing scope;
3. describe the desired geometry in positive observable terms;
4. state what geometry remains fixed;
5. give one concise output contract.

Do not lead with long `do not / avoid / no` lists.
Use exclusions only for one or two known catastrophic failure modes that cannot be expressed positively.

## Preferred language

Bad / abstract:
- more handsome
- premium
- not puppy eyes
- not thug-like
- do not look tired
- not K-pop

Good / visible:
- `upper lid margin forms a taut low arc with a shallow crease close to the lid edge`;
- `central upper-lid dome is flatter, producing a longer almond aperture`;
- `outer canthus terminates approximately level to slightly above the inner canthus`;
- `lower lid rises gently through the outer third and remains smooth`;
- `brow body sits slightly higher, increasing visible brow-eye clearance`;
- `inner two-thirds of brow are nearly horizontal; apex occurs near the lateral canthus; tail tapers cleanly`;
- `mouth corners remain relaxed and level with neutral lip closure`.

## Quantification rule

Use modest relative geometry only when useful:
- `horizontal eye length +4–7% visual effect`;
- `brow-eye clearance +5–10% relative to current`;
- `outer canthus ~1–2° positive relative to inner canthus`.

Treat these as visual targets, not physical measurements.

## Reference rule

If a face shell is already selected:
- edit from the selected face shell only;
- do not re-upload creator portrait unless structural ancestry specifically needs re-calibration;
- do not chain rejected edits as new bases;
- always return to the last accepted base for each controlled branch.

## H1 material rule

For pure geometry study:
- use matte-gray sculpt material;
- use a smooth neutral cranial cap or extremely low-information hair mass;
- do not let hairstyle encode social class, subculture or personality before H3 Hair Architecture.

## Expression-code rule

When a face produces an unwanted vibe such as `street-tough`, `puppy`, `tired`, `villain`, or `idol`, translate that vibe into geometry before prompting:
- brow height / angle;
- brow-eye clearance;
- eye aperture aspect ratio;
- upper-lid tension / crease height;
- lower-lid support;
- canthal relation;
- mouth-corner tension;
- hair silhouette contamination.

Never prompt the vibe label as the main instruction.
