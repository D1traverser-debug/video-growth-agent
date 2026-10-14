# Production and Cost Strategy — V1

## Objective

Maximize AI-assisted visual production and reduce creator labor **without** building a cost structure in which every published second requires a premium video-generation model.

The account is not an "AI video account". AI is the production studio for a technology-business media product.

## Production target

Preferred mature state:

`research -> script -> shot plan -> visual classification -> image generation -> video routing -> voice/audio -> rough assembly -> QA -> human approval`

The creator should increasingly act as:
- editor-in-chief;
- director;
- approval gate;
- final quality controller;

rather than manually producing every asset.

## AI visual share vs premium-video share

These are separate metrics.

A finished episode may be 80–100% AI-originated / AI-composited visually while only a smaller fraction uses expensive full video generation.

Suggested starting allocation for a 6–10 minute episode:
- premium AI video / hero motion: 10–25%;
- ordinary I2V / lower-cost motion generation: 15–30%;
- AI stills + camera motion / parallax / local motion: 25–40%;
- motion graphics / diagrams / typography / code-driven visuals: 15–30%;
- verified real/brand/editorial product footage where truth requires it: variable, especially for sponsorship.

These are budgeting ranges, not hard doctrine.

## Shot classes

### S-class
Use strongest available video model when the shot is responsible for:
- opening stop-rate;
- major reveal;
- impossible cinematic concept;
- complex character action;
- signature transition;
- sponsor-defining hero moment.

### A-class
Use competent I2V / controlled video model when movement materially improves explanation or emotion but does not justify top-tier cost.

### B-class
Prefer:
- generated still;
- 2.5D motion;
- camera push/pan;
- depth/parallax;
- selective local movement;
- reusable environment or character asset.

### Information-class
Use:
- diagrams;
- animated charts;
- labels;
- interface abstraction;
- system schematics;
- typography and compositing.

These shots often explain more effectively than another cinematic generation.

## Model Router principle

Never bind the system to one vendor/model.

Routing fields should eventually include:
- shot_id;
- shot_type;
- duration;
- required_resolution;
- quality_class;
- character_consistency requirement;
- physics/action complexity;
- camera complexity;
- product-truth requirement;
- maximum cash/credit budget;
- retry_limit;
- preferred model;
- fallback model;
- graceful-degradation route.

Example fallback:

`premium video -> cheaper I2V -> local motion / 2.5D -> still + camera -> information graphic`

A failed four-second shot must not consume unlimited credits.

## Cost accounting

Track at minimum:

### Compute / cash
- image-generation count and cost;
- video-generation seconds and retries;
- model/provider;
- upscale/interpolation cost;
- voice/TTS cost;
- music/audio cost;
- LLM/research cost where material;
- storage/service cost.

### Human labor
- research review;
- script review;
- storyboard review;
- visual selection;
- character/lookdev approval;
- edit review;
- final QA.

### Waste
- rejected images;
- rejected videos;
- regenerated shots;
- abandoned scenes;
- over-budget attempts.

Primary operational metrics:
- cost per published minute;
- creator minutes per published minute;
- premium-video seconds per published minute;
- retry rate by model / shot type;
- reusable-asset rate.

## Resolution policy

Do not make native 4K generation a default requirement.

Preferred early production:
- generate at the lowest resolution that preserves the required shot quality;
- use 1080p as a normal master/output target where appropriate;
- upscale selectively;
- reserve native high-resolution generation for shots where detail actually survives platform delivery and materially affects quality.

## Product-truth boundary

For brand/product content, do not let generative imagery fabricate product facts.

Use authorized real imagery/footage or verified brand assets for:
- exact vehicle exterior/interior;
- real device ports/controls;
- UI and product interfaces;
- color/material claims;
- dimensions / configuration;
- demonstrated product behavior.

AI is strongly suited to:
- invisible mechanisms;
- compute/data flow;
- explanatory metaphors;
- future-use imagination clearly framed as such;
- industrial/process scenes that are impractical to film;
- transitions and cinematic world-building.

## Long-form production hypothesis

Primary Bilibili test format:
- 6–10 minutes;
- initially ~70–120 purposeful shots rather than blindly targeting 200+;
- 8–20 hero shots depending on topic and budget;
- high information density with cinematic peaks;
- strong visual continuity and recurring character/world assets.

The production goal is not to imitate another AIGC creator's shot count. It is to discover the minimum production complexity that reaches the desired public quality bar and remains economically repeatable.

## Human gates

Long-term preferred creator gates:
1. topic approval;
2. script / claim approval;
3. core look / hero-shot approval;
4. final-cut approval.

Everything else is an automation candidate once the task repeats and quality can be measured.

## Sponsor-specific mode

Normal episodes may be predominantly generated visuals.

When a concrete physical sponsor enters:
- insert verified real product footage/imagery at the truth-critical points;
- maintain the same channel visual grammar around the product;
- use AI to explain the technology around the product rather than generating false evidence of the product itself.

## Commercial viability test

Do not evaluate a topic only by views.

For each published episode, track:
- production cash cost;
- human labor;
- long-tail views;
- audience acquisition;
- sponsor category fit;
- integration opportunities;
- reuse value;
- rights value;
- follow-on topic potential.

A repeatable media system must improve **content gross margin and creator-hour efficiency** as it scales.
