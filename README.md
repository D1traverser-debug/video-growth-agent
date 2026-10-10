# Video Growth Agent

Executable Skill + agentic-studio runtime for high-quality short-video creation, independent review, commercialization and continuous improvement.

## Authority
- **GitHub `main`** — executable rules, runtime resources, role prompts, stage contracts, checkpoint semantics, QA code and tests.
- **`video_growth_agent/data/`** — the single machine-readable runtime resource authority. Do not maintain a second root config mirror.
- **`skills/video-growth-agent/`** — operating semantics and progressively loaded references.
- **Project artifacts** — rendered media, source assets and large binary evidence; GitHub stores stable refs/digests/receipts rather than pretending every binary belongs in git.
- Notion / Drive / Library are non-authoritative by default unless an active task names an exact artifact as evidence.

## Runtime 0.5.1
The runtime provides:
- atomic project checkpoints and immutable event receipts;
- stage-scoped role prompt loading;
- artifact revision invalidation;
- work-order/process proof derived from the execution plan;
- producer/reviewer separation;
- blind reviewer evidence and optional provider-backed execution attestation;
- asset provenance/rights records;
- real FFmpeg/ffprobe media QA;
- Technique Library routing;
- generation preflight guards;
- executable system-hygiene audit;
- CLI entrypoint `vga`.

Machine-readable workflow: `video_growth_agent/data/workflow.json`  
Execution plan: `video_growth_agent/data/execution-plan.json`  
Agent registry: `video_growth_agent/data/agents.json`

## Core gate
A governed stage advances only when required artifacts, configured work-order/process proof, required professional review PASS records, and deterministic machine guards all pass. Where isolation attestation is required, missing trusted execution proof blocks progression.

Producer completion is not approval. A role/config/tool label is not proof that the role or tool actually executed.

## Useful commands
After `pip install -e .`:

```bash
vga init pilot-x --title "..."
vga status pilot-x
vga prompts pilot-x
vga review-packet pilot-x art_director
vga qa-media final.mp4 --frames-dir qa-frames
vga techniques --tag mechanism --max-cost 2 --validated-only
vga system-audit --repo-root .
```

`vga system-audit` without `--repo-root` checks installed-package invariants. With a repository root it additionally checks authority duplication, Skill/package prompt drift, global-reference project pollution, Continuity hygiene and runtime-version drift.

## Workflow
`INTAKE → POSITIONING → RESEARCH → RESEARCH_AUDIT → SCRIPT → SCRIPT_AUDIT → STORYBOARD → LOOKDEV → VISUAL_PREVIEW → ASSET_BUILD → ROUGH_CUT → SOUND → TECH_QA → AUDIENCE_QA → BRAND_QA → RED_TEAM → RELEASE → PERFORMANCE → LEARN → COMPLETE`

## Quality-critical controls
- LOOKDEV / VISUAL_PREVIEW / ROUGH_CUT use benchmark-anchored structured quality review.
- Critical blind review cannot claim independence without required execution evidence.
- Quality-critical generation requires an exact generation brief and separate Art Director / Creative Director / Red Team challenge evidence; inline PASS is not authorization.
- TECH_QA trusts actual media measurements, not a handwritten QA artifact.
- RELEASE rejects unknown final rights and stale/failing media QA.

## Cost rule
Capability and quality thresholds are mandatory. Minimize cost only after the required quality ceiling is plausible. Use scarce premium generation for high-risk/hero requirements rather than blind exploration.

## Validation and promotion
CI installs the package and FFmpeg, runs `vga system-audit --repo-root .`, executes the full pytest suite, then smoke-tests the installed CLI outside the repository. A green run is required evidence for maintenance promotion.

Repository branch protection/rulesets are a separate GitHub control. CI success must never be described as branch-protection enforcement unless GitHub actually reports that protection is enabled.
