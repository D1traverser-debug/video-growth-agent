# Video Growth Agent — Product Requirements Baseline

Status: `CANDIDATE_0_6_0`
Date: `2026-10-15`
Owner: `DOMAIN:video`
Parent common-governance dependency: `UAOS 2.5.0 / COMMON_CAPABILITIES 1.6.0`

## 1. Product outcome

Video Growth Agent is one business domain for building and operating AI-native media products. It owns four cooperating workstreams:

1. `MEDIA_GROWTH` — positioning, topic portfolio, content system, audience growth and performance learning;
2. `ORIGINAL_DIGITAL_IP` — original character/IP research, design, canon assets and identity consistency;
3. `COMMERCIALIZATION` — sponsor fit, offer architecture, pricing/rights boundaries, brand integrations and repeat-buy economics;
4. `PRODUCTION_SYSTEM` — episode production, asset/generation routing, media QA, cost/runtime methods and reusable production techniques.

These workstreams belong to one domain and may belong to one integrated business Program. They are not separate UAOS Agents merely because their tasks differ.

## 2. Ownership and identity boundary

- UAOS owns cross-domain selection/governance and the reusable common cognition/evolution/product/orchestration method.
- Video Growth Agent owns all Video business project/program/workstream/subtask identities, business state, dependency graphs, decisions, media rules and artifacts.
- Parent controller/router identity is distinct from every Video business identity.
- Parent continuity may retain an opaque child reference; it must not create/adopt an equal Video project/program/subtask ID.
- `projects/PROJECT_INDEX.json` is the current child-owned project/program discovery authority.

## 3. Primary user journeys

### VR-01 Direct domain start
A fresh chat may select Video/AI video/original digital IP/AI self-media commercialization directly. After domain selection, normal business work runs in the Video work plane without a mandatory live UAOS business proxy.

### VR-02 Integrated self-media business Program
Generic requests such as `AI自媒体视频商业化`, `AI视频涨粉与商业化`, or `原创数字IP` may resolve to the default integrated Program `ai-self-media-commercialization` when the user does not provide a different exact child project reference.

The Program coordinates the four workstreams but preserves their independent status and blockers.

### VR-03 Exact historical project resume
Exact child project references win. `pilot-002` / legacy alias `video-growth:main` resumes Pilot 002 child state without converting that legacy alias into a UAOS parent task identity.

### VR-04 Parallel work
Independent subtasks run concurrently once their declared inputs are available. Example: audience/topic research, advertiser mapping and H1 character exploration may progress in parallel.

### VR-05 Dependency-bound work
A task waits only for declared dependencies and required artifacts. Example: identity-dependent brand assets may wait for character canon lock while topic research continues.

### VR-06 Competitive design/research candidates
When the correct answer is uncertain, create multiple candidates independently, evaluate them against declared criteria, then record an authorized selection/merge/rejection decision. A candidate cannot approve itself.

### VR-07 Consultation and negotiation
Specialists may provide advisory critiques. When viewpoints conflict, use bounded artifact rounds such as `proposal -> critique -> revision -> adjudication`; do not use unbounded peer chat.

### VR-08 Episode production
A formal episode continues to use the existing production workflow from intake through research, script, storyboard, lookdev, asset build, edit/sound, QA, release, performance and learning.

### VR-09 Failure and recovery
Review failure, stale upstream inputs, rejected media or unavailable hard capabilities must invalidate only affected downstream work and resume from the earliest owning dependency. Do not restart unrelated workstreams.

### VR-10 Problem cognition and evolution
Every detected problem inherits the current UAOS problem-response floor. Video business-rule evolution remains domain-owned; common/cross-domain changes upcall UAOS. One output or preference creates evidence/candidates, not automatic global promotion.

## 4. Workstream interaction model

A Program is not a single serial stage machine. It is a domain-owned graph of workstreams and subtasks.

Supported relations:
- serial dependency;
- independent parallel;
- fan-out/fan-in;
- consultative advice;
- competitive candidates;
- structured critique/revision;
- owner adjudication;
- review panel/quorum.

Every decision edge must remain mechanically inspectable through declared dependencies, artifact inputs and durable result/decision receipts.

## 5. Specialist model

The domain keeps one user-facing business owner (`executive_producer`). Ephemeral specialists are used only when work materially differs in tools, policy, context, craft or output/assurance contract.

Specialists exchange artifacts rather than free-form peer chat. Consultation is advisory. Selection authority must be explicit. Producer completion is not approval.

## 6. Functional requirement map

| Requirement | Owning surface | Acceptance evidence |
| --- | --- | --- |
| Child-owned project/program discovery | `projects/PROJECT_INDEX.json` | system audit + project-index tests |
| Integrated four-workstream Program | `projects/ai-self-media-commercialization/PROGRAM_STATE.json` | product/orchestration tests |
| Current business subtask graph | `projects/ai-self-media-commercialization/SUBTASK_GRAPH.json` | graph validation tests |
| Explicit runtime dependencies | `studio_agents.py::WorkOrder/ExecutionPlanner` | coordination tests |
| Legacy wave compatibility | `studio_agents.py::dispatch_stage` | existing + new regression tests |
| Competition/consult/adjudication semantics | `coordination-policy.json`, execution plan/task metadata | coordination contract tests |
| Artifact-only specialist handoffs | `agents.json`, `AgenticStudio.work_packet` | agentic-studio tests |
| Episode production workflow | `workflow.json`, `execution-plan.json` | system audit + trajectory tests |
| Original digital-IP continuity | integrated Program project files | current H1 state/review evidence |
| Commercial strategy | account/commercial artifacts under integrated Program | product requirement/decision evidence |
| Cognition/evolution inheritance | `.uaos/CAPABILITIES.json`, `UAOS_SKILL.md` | binding/architecture tests |

## 7. Non-functional requirements

- one Video business owner; no second domain controller/task-index/lease system;
- direct domain activation;
- no parent/child business ID equality;
- least-context packets and explicit artifact provenance;
- explicit acyclic dependencies;
- fail-closed hard capability and media-review gates;
- stale/rejected artifacts cannot silently return as accepted progress;
- same-context candidate diversity is not independent semantic verification;
- current project authority beats chat memory and repository search rank;
- workstream concurrency must not create write races on the same authoritative artifact.

## 8. Explicit non-goals

- Do not merge every Video project into one state file.
- Do not force the four workstreams into one serial episode workflow.
- Do not create a persistent Agent for every subtask.
- Do not allow unbounded specialist peer chat.
- Do not let consultation silently decide.
- Do not let UAOS mirror Video project/program/workstream/subtask state.
- Do not reinterpret historical rejected Pilot 002 artifacts as accepted progress.

## 9. Product completion criteria

Video 0.6.0 is internally ready when:
1. UAOS common contract 1.6.0 is live;
2. Video declares current cognition/evolution/product/orchestration inheritance;
3. the integrated Program owns all four workstreams without losing current H1/IP progress;
4. exact Pilot 002 resume remains possible under child-owned identity;
5. explicit dependency scheduling, parallelism, competition/adjudication and cycle rejection are mechanically tested;
6. old execution-plan behavior remains compatible where explicit dependencies are absent;
7. system audit, full pytest and installed-package smoke pass on final candidate and production;
8. UAOS parent Video business-task mirrors are retired only after child production is verified.
