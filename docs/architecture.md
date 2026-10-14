# Video Growth Agent — Architecture

Status: `CANDIDATE_0_6_0`
Owner: `DOMAIN:video`

## 1. Topology

`UAOS common control/governance -> directly selected Video domain -> child-owned Program/Project -> workstreams -> subtasks/work orders -> artifacts/decisions`

UAOS does not own Video project/program/workstream/subtask identities. Video does not implement a second UAOS controller.

## 2. Business hierarchy

### Domain
`DOMAIN:video` is the single Video business owner.

### Project / Program
A project is an independently resumable child business state. A Program may contain multiple cooperating workstreams. `projects/PROJECT_INDEX.json` discovers current child business states.

### Workstream
A workstream owns a coherent business objective and its local status, e.g. Media Growth, Original Digital IP, Commercialization or Production System.

### Subtask / work order
A subtask is the smallest schedulable unit. Runtime work orders bind executor, inputs, outputs, dependencies, coordination semantics and evidence.

## 3. Scheduling

Explicit `depends_on` edges are authoritative when present. A task is READY when:
1. every declared dependency is completed;
2. every required artifact input exists;
3. its hard capability/evidence preconditions are satisfied by the owning action path.

Tasks with no explicit dependency declaration retain the legacy wave rule for backward compatibility.

Dependency graphs must be acyclic. An unrelated task in an earlier wave cannot block a task that uses explicit dependencies and does not depend on it.

## 4. Coordination semantics

`coordination-policy.json` defines stable semantics. Runtime task metadata may declare:
- `coordination` — semantic relation/role;
- `depends_on` — exact prerequisite task IDs;
- `decision_group` — candidate set membership;
- `consumes_group` — candidate set consumed by synthesis/adjudication.

Competition is not peer conversation. Candidate tasks independently emit artifacts; critics review artifacts; revisions emit new artifacts; an authorized adjudicator records the selection/merge/rejection result.

Consultation produces advice/evidence but not implicit authorization.

## 5. Agent model

`executive_producer` remains the single user-facing domain owner and internal schedule/decision authority. Specialists are ephemeral and artifact-mediated. `peer_chat=false` remains an invariant.

Add specialists only for material tool, policy, craft, context, output or assurance differences. The architecture must not simulate diversity through cosmetic personas.

## 6. Integrated self-media Program

`projects/ai-self-media-commercialization` is the default integrated Program for generic AI-media growth/commercialization/original-IP intents. It contains four workstreams that can progress independently:
- `MEDIA_GROWTH`
- `ORIGINAL_DIGITAL_IP`
- `COMMERCIALIZATION`
- `PRODUCTION_SYSTEM`

The current H1 character work remains the active Original-IP cursor; integrating the Program does not reset or rewrite that evidence.

Generic phrase `AI视频涨粉与商业化` resolves here. Exact historical alias `video-growth:main` resolves to Pilot 002 only when explicitly requested.

## 7. Episode workflow

The canonical episode workflow remains a specialized production state machine. It is not replaced by the Program graph. Program work can create validated inputs for an episode; episodes still pass their existing stage gates.

## 8. Recovery and invalidation

An upstream artifact change retires/stales downstream work that consumed its digest. A failed/rejected candidate does not contaminate sibling workstreams. Recovery restarts the earliest owning dependency, not the entire Program.

## 9. Cognition/evolution

The domain consumes current UAOS hosted cognition/evolution policy. Every detected problem runs the mandatory research/reflection floor. Domain production/content/IP/commercial rules evolve inside Video with replay/regression evidence; shared orchestration semantics remain UAOS common authority.

## 10. Negative space

Forbidden:
- parent business-state mirrors for Video projects;
- repository-local cross-chat controller/lease protocol;
- unbounded peer-chat negotiation;
- hidden dependency edges;
- self-approval;
- global wave ordering overriding declared explicit dependencies;
- same-context candidate generation labelled independent verification.
