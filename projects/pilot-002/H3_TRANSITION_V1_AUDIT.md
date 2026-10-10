# Pilot 002 — H3 Transition V1 Audit

Status: **VISUAL FAIL / DO NOT PROMOTE**  
Stage: VISUAL_PREVIEW_PROCESS_REENTRY  
Artifact role: paid diagnostic experiment only

## Artifact / execution

- Engine: MiniMax H3 through connected vidIQ
- Duration: 4 s
- Resolution: 768p generation, subsequently composed to 1080×1920 for QA transport
- Generation cost: 60 vidIQ credits
- Original generation job: `job_15eed248-dfaf-4353-a9a5-16979c30cc49`
- Existing result was inspected as actual rendered media through a browser-capable QA path; it was not judged from the prompt or model name.

## What is actually visible

The rendered clip is a dark futuristic industrial corridor with a conveyor system carrying a box-like object. The environment has metallic surfaces, overhead lighting and visible depth. Across the 4 seconds, the dominant motion is the transported object/conveyor movement. Camera state, environment, lighting language and material world remain broadly consistent. No meaningful readable text is visible.

## Why it fails the shot contract

The target contract was:

`human/manual app operation → screen-plane break → deeper agent/service world → prepared result`

The actual H3 output instead reads as:

`already-inside-backend-world → object travels through same backend-world`

Therefore it fails the most important transformation requirement even though the environment is more cinematic than Sample V2's schematic backend.

### Hard findings

| Dimension | Result | Finding |
|---|---|---|
| World-state change | **FAIL** | opening and ending remain in essentially the same industrial world |
| Human → agent contrast | **FAIL** | no familiar human/manual foreground survives into the generated shot |
| Transformation causality | **FAIL** | transport is visible, but crossing from manual UI into autonomous backend is not |
| Camera / spatial progression | **FAIL** | depth exists, but camera state is too static to make the transition feel consequential |
| Material richness | **PARTIAL PASS** | metallic corridor has more physical weight than V2's schematic service tunnel |
| Hero moment | **FAIL** | no decisive reveal or materially different payoff composition |
| Generic AI/SaaS avoidance | **PASS** | does not read as dashboard/cards/glass UI |

Overall: **REJECT AS V3 SHOT**.

## Root cause

The generation request over-weighted the desired backend material world and under-constrained the required before/after state discontinuity. H3 produced a coherent scene but solved the wrong problem: it rendered a backend transport shot, not a world-transition shot.

## Repair rule promoted from this failure

A transition shot is invalid unless the artifact itself visibly proves at least three distinct states:

1. **BEFORE** — familiar human/manual/app-scale state;
2. **CROSSING** — an irreversible visual event that breaks the old operating surface;
3. **AFTER** — a materially, spatially and compositionally different agent/background state.

Motion inside one world cannot substitute for a world transition.

For generative video, the next attempt must use explicit endpoint control (first/last frame or equivalent reference-state binding) rather than prose alone whenever the before/after states are both non-negotiable.

## Cost consequence

Because this 4-second diagnostic consumed 60 vidIQ credits, vidIQ H3 is not approved as a general exploration engine. It remains eligible only for high-risk / hero seconds after cheaper state-locking exploration has already proven the composition and transition logic.
