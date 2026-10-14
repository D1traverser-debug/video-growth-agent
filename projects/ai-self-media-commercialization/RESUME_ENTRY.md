# Resume Entry — AI自媒体视频商业化与原创数字IP

Status: ACTIVE_DESIGN_INCUBATION  
Scope: PROJECT_LOCAL_ONLY  
Continuity task: NO

## Canonical resume phrases

In a new ChatGPT conversation, use one of the following explicit continuation requests:

- `继承 AI自媒体视频商业化与原创数字IP，继续打磨角色细节。`
- `继承 ai-self-media-commercialization，继续 CHARACTER_CONCEPT_DESIGN_V1。`
- `继续原创数字IP设计，读取 AI视频系统里的 ai-self-media-commercialization 独立项目，不要进入 video-growth:main 或 Pilot 002。`

If the next work is specifically about the character, the preferred phrase is:

> `继承 AI自媒体视频商业化与原创数字IP，继续打磨原创男性数字IP。先读取 PROJECT_MANIFEST.json、CURRENT_PROGRESS.md、CHARACTER_DESIGN_BIBLE_V1.md 和 DECISION_LOG.md，再从当前 next_action 继续；不要把它并入 video-growth:main / Pilot 002。`

## Required entry order

On continuation, recover the project in this order:

1. `PROJECT_MANIFEST.json` — project identity, isolation boundary, scan metadata, current stage and next action.
2. `CURRENT_PROGRESS.md` — concise current checkpoint and accepted/rejected directions.
3. `CHARACTER_DESIGN_BIBLE_V1.md` — current character design authority when character work is requested.
4. `DECISION_LOG.md` — rejection history and anti-regression guardrails.
5. `CONCEPT_GENERATION_PROMPT_V1.md` — only when generating/refining the first concept image.
6. Load `ACCOUNT_POSITIONING.md`, `PRODUCTION_AND_COST_STRATEGY.md`, or `WORKFLOW_INTEGRATION.md` only when the requested work activates those areas.

Do not preload unrelated Pilot 001 / Pilot 002 project state.

## Current continuation target

Current stage: `CHARACTER_CONCEPT_DESIGN_V1`

Current next action:
- produce one full-body concept from the current design authority;
- judge large-form identity first: silhouette, face architecture, hair masses, pixel-sunglasses contradiction, primary costume architecture, deadpan identity, motif fusion and commercial compatibility;
- if large-form PASS, refine the same identity through controlled edits instead of random resampling;
- after identity convergence, build Canon Face, Canon Full Body, turnarounds, expression sheet, accessory/costume sheets and Brand Visual Bible.

## Isolation invariant

This project is reusable system-resident project material inside the Video Growth repository, but it is not an active continuity task and is not a child/subtask of `video-growth:main`, `pilot-001`, or `pilot-002`.

A future production project may explicitly import selected outputs through the normal Video Growth workflow. No automatic stage promotion, gate bypass, blocker change or task-state mutation is allowed.
