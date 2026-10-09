# Video Growth Agent

Executable Skill + virtual-studio runtime for low-cost, high-quality short-video creation, self-critique, commercialization and continuous improvement.

## Authority
- **GitHub `main`** — executable rules, role prompts, stage contracts, project checkpoint semantics, QA code and tests.
- **Notion / Google Drive** — benchmark corpus, market research, recovery notes and human-readable mirrors.
- **Project artifacts** — rendered media, source assets and large binary evidence; GitHub stores their references/receipts rather than pretending every binary belongs in git.

## Core idea
The agent behaves as a production studio rather than one monolithic creator. Strategy, research, writing, retention, directing, art direction, storyboard, motion, asset sourcing, editing, sound, technical QA, commercial fit, compliance and red-team review have independent responsibilities and veto conditions.

A stage advances only when:
1. every required artifact exists;
2. every required professional role signs `PASS`;
3. stage-specific machine guards pass.

One hard failure blocks progression. Average quality cannot compensate for false facts, unknown rights, broken media, weak retention or unsafe commercial fit.

## Runtime
`video_growth_agent/` now provides:
- atomic project checkpoints under `projects/<project-id>/state.json`;
- immutable JSON receipts + append-only `events.jsonl`;
- stage-scoped role prompt loading;
- artifact revision invalidation;
- asset provenance/rights records;
- real FFmpeg/ffprobe media QA;
- Technique Library routing;
- CLI entrypoint `vga`.

Useful commands after `pip install -e .`:
```bash
vga init pilot-002 --title "..."
vga status pilot-002
vga prompts pilot-002
vga artifact pilot-002 brief file://brief.md INTAKE
vga sign pilot-002 showrunner PASS --evidence file://brief.md
vga advance pilot-002
vga qa-media final.mp4 --frames-dir qa-frames
vga techniques --tag mechanism --max-cost 2 --validated-only
```

## Workflow
`INTAKE → POSITIONING → RESEARCH → RESEARCH_AUDIT → SCRIPT → SCRIPT_AUDIT → STORYBOARD → VISUAL_PREVIEW → ASSET_BUILD → ROUGH_CUT → SOUND → TECH_QA → AUDIENCE_QA → BRAND_QA → RED_TEAM → RELEASE → PERFORMANCE → LEARN → COMPLETE`

`config/workflow.json` is machine-readable and declares required roles, required artifacts and machine guards for each stage.

## Hard machine vetoes
- `TECH_QA`: cannot advance unless the latest recorded media QA is a hard pass.
- `RELEASE`: cannot advance if final-used assets still have `UNKNOWN` rights or if media QA is not a hard pass.
- `RED_TEAM`: a PASS requires at least three explicit objections/findings, so “looks fine” is not a valid red-team review.

## Real media QA
Actual media is inspected, not inferred from the editing project. The QA module checks independent video/audio stream durations, resolution/FPS/frame count, integrated loudness/true peak after final encoding, long silence, long black frames, and safe non-EOF extraction of review frames from the real export.

## Cost rule
Prefer existing entitlements, local/open-source tools, code animation, screen capture and authorized assets. Paid generation is a targeted tool for shots where it creates real explanatory or retention value, not the default production engine.

## Validation
CI installs the package, installs FFmpeg, runs the full pytest suite including a real generated MP4 QA test, and smoke-tests the CLI. “Code imported” is not sufficient evidence.
