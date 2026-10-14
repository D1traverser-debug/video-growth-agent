# Video Growth Agent

Executable AI-media growth, original digital-IP, commercialization and production domain owner under `D1traverser-debug/universal-agent-os@main`.

## Current authority
- `UAOS_SKILL.md` — direct Video-domain entry after domain selection.
- `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json` — parent/common binding, identity boundary and current capability ceiling.
- `docs/product_requirements.md`, `docs/architecture.md` — current Video product and architecture authority.
- `projects/PROJECT_INDEX.json` — child-owned project/program discovery authority.
- `projects/` — exact child business state, workstream/subtask graphs, accepted decisions and evidence.
- `video_growth_agent/data/` — machine-readable episode workflow, specialist and coordination resources.
- `skills/video-growth-agent/references/` — domain operating rules and progressively loaded references.
- large media/artifact stores — binary evidence only when bound by stable refs/digests; never controller authority by presence alone.

There is no active repository-local parent task index, lease/resume epoch protocol or second cross-chat controller. A UAOS router identity is distinct from every Video project/program/workstream/subtask identity.

## Runtime 0.6.0

Video 0.6.0 has two complementary execution layers:

1. **Program/workstream graph runtime** — `ProgramGraph` / `ProgramOrchestrator` model explicit child-owned business dependencies, parallel work, candidate competition, consultation, synthesis/adjudication, persistence and targeted downstream invalidation.
2. **Episode production runtime** — the existing stage/work-order engine continues to run production from intake through release/performance/learning with producer/reviewer separation and hard media gates.

Machine-readable resources:
- Program coordination: `video_growth_agent/data/coordination-policy.json`
- Episode workflow: `video_growth_agent/data/workflow.json`
- Episode execution plan: `video_growth_agent/data/execution-plan.json`
- Specialist registry: `video_growth_agent/data/agents.json`

## Integrated AI-media Program

Generic AI self-media growth/commercialization/original-IP requests resolve through `projects/PROJECT_INDEX.json` to the default integrated Program unless the user supplies an exact different child project reference.

The Program contains four cooperating workstreams:
- `MEDIA_GROWTH`
- `ORIGINAL_DIGITAL_IP`
- `COMMERCIALIZATION`
- `PRODUCTION_SYSTEM`

They are not one serial pipeline. Explicit dependencies decide what blocks what. Independent work can progress concurrently. Competition uses multiple inspectable candidates and an authorized adjudicator; consultation remains advisory; negotiation uses bounded artifact rounds rather than peer chat.

Historical Pilot projects remain separately resumable child states and are not collapsed into the integrated Program.

## Episode workflow

`INTAKE → POSITIONING → RESEARCH → RESEARCH_AUDIT → SCRIPT → SCRIPT_AUDIT → STORYBOARD → LOOKDEV → VISUAL_PREVIEW → ASSET_BUILD → ROUGH_CUT → SOUND → TECH_QA → AUDIENCE_QA → BRAND_QA → RED_TEAM → RELEASE → PERFORMANCE → LEARN → COMPLETE`

A governed stage advances only when required artifacts, work-order/process proof, applicable professional review PASS records and deterministic guards pass. Where isolation attestation is required, missing trusted execution proof blocks progression.

Producer completion is not approval. Role/config/tool labels are not proof of execution. Historical receipts prove what happened; they do not authorize a later work order.

## Capability and assurance boundary

Before a quality-critical action, the current session must handshake the exact required capability. The machine-readable ceilings and evidence contracts are in `.uaos/CAPABILITIES.json`.

`DECLARED_ONLY < HARNESS_WIRED < SESSION_EXECUTABLE`; `CHAT_BRIDGED` describes bounded chat execution and never implies independent-provider review; true isolated review requires `ATTESTED_ISOLATED` evidence.

Missing generation/review capability fails closed. It does not authorize a weaker SOP or fabricated artifact.

## Cognition and evolution

Video inherits current UAOS hosted cognition, product-governance and domain-internal orchestration semantics. Every detected problem triggers research plus macro/topology and governing-assumption reflection. Video-specific business evolution remains Video-owned; common/cross-domain evolution remains UAOS-owned.

Same-context candidate generation can increase search diversity but is not independent semantic verification.

## Cost rule

Meet the quality, permission and evidence floor first; then minimize cost. Use included/free providers when adequate, and reserve scarce premium generation for high-risk/hero requirements. Paid or unknown-cost execution requires explicit authorization.

## Validation

After `pip install -e .`:

```bash
vga system-audit --repo-root .
pytest -q
```

The repository audit verifies parent/common binding, child business-identity ownership, project-index integrity, Program graph validity, absence of a parallel controller, artifact reachability, specialist/task consistency, capability assurance semantics, technique admission and runtime-version consistency.

CI success is validation evidence, not branch-protection enforcement unless GitHub separately reports branch protection/rulesets as enabled.
