# Video Growth Agent

Executable AI-video and growth domain owner under `D1traverser-debug/universal-agent-os@main`.

## Current authority
- `UAOS_SKILL.md` — current domain entry after UAOS routing.
- `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` — controller binding and current capability ceiling.
- `video_growth_agent/data/` — single machine-readable workflow/execution/agent resource authority.
- `skills/video-growth-agent/references/` — domain operating rules and progressively loaded references.
- `projects/` — project-local manifests, accepted state, design decisions and evidence.
- large media/artifact stores — binary evidence only when bound by stable refs/digests; never controller authority by presence alone.

There is no active repository-local task index, lease/resume epoch protocol or second cross-chat controller. Historical control-plane files live only in Git history.

## Runtime 0.5.2
The runtime provides atomic project checkpoints and event receipts, stage-scoped role prompts, downstream evidence invalidation, generation-aware work orders, producer/reviewer separation, execution attestation, asset provenance, deterministic FFmpeg/ffprobe QA, Technique Library admission, generation preflight guards, system-hygiene audit and the `vga` CLI.

Machine-readable workflow: `video_growth_agent/data/workflow.json`  
Execution plan: `video_growth_agent/data/execution-plan.json`  
Agent registry: `video_growth_agent/data/agents.json`

## Workflow
`INTAKE → POSITIONING → RESEARCH → RESEARCH_AUDIT → SCRIPT → SCRIPT_AUDIT → STORYBOARD → LOOKDEV → VISUAL_PREVIEW → ASSET_BUILD → ROUGH_CUT → SOUND → TECH_QA → AUDIENCE_QA → BRAND_QA → RED_TEAM → RELEASE → PERFORMANCE → LEARN → COMPLETE`

A governed stage advances only when required artifacts, work-order/process proof, applicable professional review PASS records and deterministic guards pass. Where isolation attestation is required, missing trusted execution proof blocks progression.

Producer completion is not approval. Role/config/tool labels are not proof of execution. Historical receipts prove what happened; they do not authorize a later work order.

## Capability and assurance boundary
Before a quality-critical action, the current session must handshake the exact required capability. The machine-readable ceilings and evidence contracts are in `.uaos/CAPABILITIES.json`.

`DECLARED_ONLY < HARNESS_WIRED < SESSION_EXECUTABLE`; `CHAT_BRIDGED` describes bounded chat execution and never implies independent-provider review; true isolated review requires `ATTESTED_ISOLATED` evidence.

Missing generation/review capability fails closed. It does not authorize a weaker SOP or fabricated artifact.

## Cost rule
Meet the quality, permission and evidence floor first; then minimize cost. Use included/free providers when adequate, and reserve scarce premium generation for high-risk/hero requirements. Paid or unknown-cost execution requires explicit authorization.

## Validation
After `pip install -e .`:

```bash
vga system-audit --repo-root .
pytest -q
```

The repository audit verifies UAOS binding, absence of the retired control plane, project-state isolation, artifact reachability, role/task consistency, Skill/package prompt parity, capability assurance semantics, technique admission and runtime-version consistency.

CI success is validation evidence, not branch-protection enforcement unless GitHub separately reports branch protection/rulesets as enabled.
