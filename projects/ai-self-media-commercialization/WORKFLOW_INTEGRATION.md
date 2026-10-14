# Workflow Integration Notes

## Purpose

This package is **not an active continuity task** and does not inherit the state of `video-growth:main` or Pilot 002.

It is a project-local reference package designed so a future Video Growth project can explicitly import the useful parts without contaminating unrelated tasks.

## Discovery

The repository hygiene system dynamically derives project aliases from `projects/*`. Keeping this package as a direct sibling under `projects/` makes it visible to repository-level project scanning while preserving isolation from existing Pilot folders.

Machine-readable discovery metadata lives in `PROJECT_MANIFEST.json`.

## Import policy

Default: **no automatic promotion**.

A future project may explicitly import only the artifacts it needs.

Recommended mapping into the existing Video Growth workflow:

### INTAKE / POSITIONING
Potential inputs:
- `ACCOUNT_POSITIONING.md`;
- target audience;
- content pillars;
- channel role;
- commercial adjacency;
- platform strategy.

### RESEARCH / RESEARCH_AUDIT
Use this package only for account-level framing and known boundaries.
Do not treat it as factual evidence for episode-specific claims.
Every episode must perform fresh evidence collection and claim verification.

### SCRIPT / SCRIPT_AUDIT
Portable editorial principles:
- mechanism before hype;
- explain rules/incentives/bugs/human behavior;
- build narrative tension rather than listing facts;
- sponsorship must belong naturally to the story.

### STORYBOARD
Import:
- character narrative function;
- deadpan staging rules;
- high-resolution vs low-resolution anomaly contrast;
- visual motif hierarchy.

### LOOKDEV
Primary inputs:
- `CHARACTER_DESIGN_BIBLE_V1.md`;
- accepted concept/character images once available;
- future visual-bible assets;
- palette/material/cinematography rules.

### VISUAL_PREVIEW
Use project-local concept references only when the active future project has explicitly adopted them.
Quality-critical generation still follows the owner's current generation-governance and review requirements.
This package must not be used to bypass those gates.

### ASSET_BUILD
Future reusable assets may include:
- character canon face/body reference;
- hair reference;
- costume turnaround;
- sunglasses asset;
- Pixel→Scale motif;
- color palette;
- logo/watermark;
- intro/outro/section-card templates;
- reusable environment/look references.

### ROUGH_CUT / SOUND
Potential identity rules:
- restrained narrator/character performance;
- calm visual rhythm against absurd subject matter;
- character reaction amplitude remains lower than environment intensity.

### BRAND_QA
Import:
- target advertiser pools;
- product-truth boundary;
- natural integration principle;
- distinction between publishing fee and usage/paid-media rights.

### PERFORMANCE / LEARN
Do not promote project-local preferences into global Technique Library solely because they were used.
Only verified generalized techniques should enter the owner's learning/evolution path under current admission rules.

## Character-asset authority rule

Before the character is formally locked:
- no random generated image becomes authority merely because it looks good;
- rejected photoreal/cosplay/generic-game-character outputs remain historical references only;
- large-form concept approval comes before face/hair/costume turnarounds;
- after identity lock, later images should be controlled edits / reference-bound outputs rather than identity re-rolls.

## Future suggested asset tree

When the concept passes, extend this folder rather than mixing assets into Pilot 002:

```text
projects/ai-self-media-commercialization/
  PROJECT_MANIFEST.json
  README.md
  ACCOUNT_POSITIONING.md
  CHARACTER_DESIGN_BIBLE_V1.md
  CONCEPT_GENERATION_PROMPT_V1.md
  PRODUCTION_AND_COST_STRATEGY.md
  WORKFLOW_INTEGRATION.md
  DECISION_LOG.md
  character/
    canon/
    hair/
    costume/
    accessory/
    expressions/
    turnarounds/
  brand/
    visual-bible/
    logo/
    banner/
    thumbnails/
    intro-outro/
  research/
  episode-pilots/
```

Binary images/video do not need to be committed blindly to Git. Store stable refs/digests/authorized asset locations according to the owner artifact policy when the production phase begins.

## Non-interference rule

This project must not:
- write to `continuity/tasks/video-growth-main/*` for its own progress;
- change Pilot 002 stage/gates/blockers;
- reuse Pilot 002 rejected candidates as accepted evidence;
- alter global Skill/runtime policy merely to accommodate local character preferences;
- enter the global Technique Library without explicit verified learning promotion.
