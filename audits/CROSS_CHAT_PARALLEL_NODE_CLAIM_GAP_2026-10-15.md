# Cross-Chat Parallel Node Claim Gap — Video Domain

Date: 2026-10-15
Owner: `DOMAIN:video`
Evolution ID: `V-20261015-02-CROSS_CHAT_NODE_CLAIM_GAP`
Status: `OPEN_PARENT_GUIDANCE_REQUIRED`

## Trigger / symptom

The integrated Program currently exposes three independent READY nodes (`ip_h1_a2_upper_face`, `growth_baseline_and_topic_hypotheses`, `commercial_advertiser_map`). A user correctly asked whether separate inherited ChatGPT sessions can execute those nodes concurrently without duplicate ownership or state corruption.

The first response stopped at a manual workaround (explicitly assign one node per chat). That was an inherited Common Behavior execution failure: the detected problem should have triggered the UAOS problem-response and evolution floor instead of ending at recommendation-only guidance.

## Micro diagnosis

`video_growth_agent/program_orchestration.py` models logical dependency concurrency but does not model cross-session execution ownership. `ProgramRunState.node_status` has WAITING/READY/COMPLETED/FAILED/CANCELLED only; there is no claim/lease identity, renewal, expiry or stale-worker recovery. The file-backed `_save()` rewrites the whole state with `Path.write_text()` and has no compare-and-swap/version precondition.

Therefore logical DAG parallelism is not equivalent to safe multi-session execution concurrency.

This conflicts with the current product non-functional requirement `no write races on the same authoritative object` in `docs/product_requirements.md` when multiple ChatGPT/GitHub sessions attempt durable Program-state mutation.

## Macro / topology diagnosis

The missing mechanism spans three inherited/common concerns:

- `domain_internal_work_orchestration`: common orchestration semantics, domain-owned graph/state;
- `cross_chat_continuity_and_recovery`: domain business continuity across direct child sessions;
- `CHATGPT_GITHUB`: repository authority and CAS/normal GitHub concurrency controls.

Video must not create a second parent controller or a Video-only global scheduler protocol if the required claim/lease/CAS semantics are common across registered domains. Video should own node identities, business artifacts and decision state; UAOS should own only the reusable cross-domain concurrency semantics/host contract.

## Governing assumption challenged

Rejected assumption: “READY nodes in an acyclic DAG are automatically safe to execute from multiple independent chats.”

A DAG answers *what may run concurrently*; it does not answer *which worker owns a runnable node*, *how duplicate workers are excluded*, *how stale work is recovered*, or *how concurrent durable updates avoid lost writes*.

## External method evidence

Relevant external mechanisms reviewed:

- Kubernetes Lease objects coordinate shared activity and use renewal timestamps / expiry for liveness and leadership.
- Amazon SQS visibility timeout temporarily hides in-flight work from other consumers and makes it available again after timeout; long work can renew visibility.
- etcd transactions use atomic comparisons / revisions to implement compare-and-swap and protect keys from unintended concurrent updates.

Borrowed minimum properties, not vendor-specific implementations:

1. exclusive node claim token bound to an opaque worker/session identity;
2. finite lease with renewal/heartbeat and stale-claim recovery;
3. optimistic version/CAS protection for authoritative state mutation;
4. idempotent completion/result receipt bound to node + claim token;
5. different independent nodes may proceed concurrently without sharing one mutable write hotspot;
6. fan-in/reconciliation consumes committed node outputs, not private chat memory;
7. duplicate/stale completion is rejected rather than silently overwriting newer state.

## Scope / ownership decision

This is a common-capability/control-plane gap with a Video reproduction, not merely a Video prompt/workflow preference.

- Video may implement owner-native adapters after common semantics are defined.
- Video must not directly mutate UAOS authority from `DOMAIN:video`.
- A parent-guidance/common-capability upcall is required before promoting a durable generic claim/lease contract.

## Provisional safe behavior

Until the common contract is resolved, separate chats may research/produce node-local candidate artifacts when explicitly scoped to distinct node IDs, but they must not claim automatic task ownership or concurrently rewrite a shared Program state object. Reconciliation must reread current authority and merge committed artifacts with stale-write protection.

This is a degradation mode, not the desired final architecture.

## Required parent guidance

UAOS should determine the minimum host-neutral common contract for cross-chat runnable-node ownership, including:

- claim lifecycle (`READY -> CLAIMED/RUNNING -> COMPLETED|FAILED|RELEASED`);
- claim token / opaque executor identity;
- lease duration, renewal and expiry recovery;
- CAS / expected-version semantics at the persistent authority boundary;
- idempotent completion and duplicate/stale result rejection;
- relationship to `CHATGPT_GITHUB` SHA-based writes and `LOCAL` SQLite CAS;
- assurance/evidence contract for successful claim, renewal, completion and stale recovery;
- no-parent-microscheduler boundary: the child still owns graph/node/business state.

After parent semantics exist, Video should add an owner-native implementation plus trajectory tests covering two workers racing for one node, independent workers claiming different nodes, lease expiry/reclaim, stale completion rejection, and concurrent state reconciliation.

## Current terminal disposition

`BLOCKED_WITH_REASON` for full repair in this authority context: the missing reusable concurrency contract is parent/common scope and `DOMAIN:video` cannot directly mutate UAOS.

The domain-side repair executed now is durable problem/evolution capture plus a parent-guidance handoff. No new Video-only global concurrency protocol is promoted pending parent decision.
