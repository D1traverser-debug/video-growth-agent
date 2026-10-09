# Video Growth Agent

Executable Skill + orchestration system for low-cost, high-quality short-video creation, self-critique, commercialization and continuous improvement.

## Authority
- **GitHub `main`** — executable rules, prompts, gates, orchestration and tests.
- **Notion / Google Drive** — benchmark corpus, research, recovery notes and human-readable mirrors.
- **Project artifacts** — rendered media, QA evidence, source assets and performance receipts.

## Core idea
The agent behaves as a virtual production studio rather than one monolithic creator. Strategy, research, writing, retention, directing, art direction, storyboard, motion, asset sourcing, editing, sound, technical QA, commercial fit, compliance and red-team review have independent responsibilities and veto conditions.

A stage advances only when every required role signs `PASS`. One hard failure blocks progression; high average quality cannot compensate for false facts, bad rights, broken media or a severe retention/commercial defect.

## Structure
- `skills/video-growth-agent/SKILL.md` — executable operating contract.
- `skills/video-growth-agent/references/team.md` — independent role prompts and veto perspectives.
- `skills/video-growth-agent/references/` — progressive-load craft and governance references.
- `config/workflow.json` — machine-readable stage graph and required sign-offs.
- `config/roles.json` — prompt routing and veto conditions.
- `video_growth_agent/` — minimal fail-closed orchestrator.
- `tests/` — gate/invalidation tests.
- `projects/` — project-specific durable learnings; never treated as global truth automatically.

## Workflow
`INTAKE → POSITIONING → RESEARCH → RESEARCH_AUDIT → SCRIPT → SCRIPT_AUDIT → STORYBOARD → VISUAL_PREVIEW → ASSET_BUILD → ROUGH_CUT → SOUND → TECH_QA → AUDIENCE_QA → BRAND_QA → RED_TEAM → RELEASE → PERFORMANCE → LEARN → COMPLETE`

## Non-negotiable QA
Actual media must be rendered and inspected. “Code ran” and “agent says it reviewed” are not evidence. Probe video/audio streams independently, inspect final frames, audit sound after final encoding, and invalidate downstream approvals after material upstream changes.

## Cost rule
Prefer existing entitlements, local/open-source tools, code animation, screen capture and authorized assets. Paid generation is a targeted tool for shots where it creates real explanatory or retention value, not the default production engine.
