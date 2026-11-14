# CAOS Governance Entry — Video Growth Agent

Status: ACTIVE
Effective date: 2026-11-14
Domain: VIDEO_GROWTH
Repository: D1traverser-debug/video-growth-agent

## 1. Governance boundary

CAOS is the parent cognition and governance system for this Video domain. Its source repository is `D1traverser-debug/cognition-agent-os`. In the current ChatGPT workspace, use the installed CAOS skill `cognition-parent-chatgpt-intake` when available.

This file is a Video-owned domain entry and integration contract. It is not CAOS source code, does not copy CAOS implementation, and does not create a second parent controller.

**Hard boundary:** CAOS source is read-only for this work. Do not create, edit, delete, rename, merge, or otherwise mutate any CAOS repository code, files, documentation, branches, pull requests, configuration, releases, or installed skill assets.

Governance mode is `CHAT_GOVERNED_EXTERNAL`: CAOS governs reasoning and work discipline in the active ChatGPT session. The Video runtime has no CAOS runtime/API dependency and must not pretend that an automatic parent-runtime call, lease, task ID, or approval occurred.

## 2. Authority ownership

| Concern | Authority |
| --- | --- |
| Requirements interpretation, decision quality, root-cause investigation, research, alternative comparison, method challenge, execution discipline, independent acceptance and durable learning | CAOS governance in the active ChatGPT session |
| Video product requirements, Program/Series/Episode/Sequence/Scene/Shot/Take identities, workstreams, editorial truth, assets, evidence, decisions, production runtime, business outcomes and Video-domain evolution | Video Growth Agent |
| Personal-IP character identity, avatar, visual/voice/performance canon and identity rights | Independent IP Studio OS (IPOS) |
| Financial article semantics, sources, article state and article-production workflow | Separate financial-writing-agent |

CAOS does not become the owner of Video business objects or media assets. Video does not copy CAOS controllers, task ledgers, cognition code, or runtime services. Cross-domain decisions are reviewed through CAOS governance in the active session; no runtime upcall is fabricated.

IPOS remains standalone and does not require a CAOS runtime/API call. Video imports only an exact owner-approved IPOS Video Identity Bundle. No character identity is approved in the current IPOS state; identity-dependent production remains gated, while unrelated Video work may continue.

## 3. Current Video system state

- Default integrated Program: `ai-self-media-commercialization`.
- Current focus: `ORIGINAL_DIGITAL_IP/IPOS_CANONICAL_HANDOFF_V1`.
- IPOS R39: G0 PASS, G1 OPEN, G2 NOT STARTED; no approved identity anchor, avatar, or Video-ready bundle.
- The Video-side IPOS bundle importer and schema are present in the current Video mainline. Their exact production assurance must be read from the current Program state and CI; do not infer approval of a character bundle.
- The superseded Video-local H1/S1+S3/A2 face-shell route must not be resumed.
- Non-character growth, commercial research, editorial planning, provider evaluation and production-system work may proceed when their own dependencies are satisfied.
- `pilot-002` is a historical project and remains on HOLD unless the user explicitly reopens it.
- Core runtime baseline: `0.8.0`; specialized legacy episode adapter bundle: `0.7.0`.

The authoritative project resolver is `projects/PROJECT_INDEX.json`. The default Program's current authority is `projects/ai-self-media-commercialization/PROGRAM_STATE.json`, with `PROJECT_MANIFEST.json`, `SUBTASK_GRAPH.json`, `BUSINESS_FLYWHEEL.json`, `IPOS_INTEGRATION_STATE.json`, and `CURRENT_PROGRESS.md` as linked domain records. Read only the records needed for the current task; do not treat stale chat memory or a historical project note as current authority.

## 4. CAOS decision loop

Before committing to a solution:

1. Reconstruct the user's complete intended outcome, explicit requirements, prohibitions, constraints, examples, and unresolved decisions. Do not substitute a nearby task or overfit to the latest sentence.
2. Identify the actual authority and evidence for each material claim. Distinguish current state, historical evidence, recommendation, assumption, and unknown.
3. Enumerate competing explanations at the correct layers: local asset/tool, workflow, Video architecture, cross-cutting capability, CAOS governance, host/runtime, and user goal.
4. Test the selected explanation against supporting evidence and disconfirming evidence. For systemic or repeated failures, reassess the architecture and dogfood the current agent's real operating path.
5. Compare reuse, adaptation, replacement, removal, and new construction. Prefer the smallest complete architecture that satisfies the whole requirement without duplicating authority.
6. Challenge the proposed method again: verify that it fits this domain, preserves independent authorities, and does not introduce a new controller or hidden dependency.
7. Select a solution with explicit rationale, scope, risks, rollback path, and acceptance criteria.

## 5. Execution loop

1. Execute the selected solution; do not stop at a plan or explanatory report.
2. Preserve domain state and unrelated work. Make changes only within the explicitly authorized Video scope.
3. Validate syntax, schemas, references, package behavior, tests, and exact changed-file readback.
4. Independently test the user journey, failure/recovery path, and authority boundary—not only the code that was just written.
5. Use exact-head CI and production readback before calling a change complete. CI is evidence, not proof of real-world video generation, publishing, audience performance, or owner approval.
6. Record the decision, evidence, affected files, test results, unresolved limitations and next valid actions in the Video domain's canonical evolution record.

A task is not complete merely because a file was changed, a test was added, or a plan was written. Completion requires the requested outcome and all applicable independent acceptance checks.

## 6. Execution assurance vocabulary

Capability declarations are not execution proof. Preserve the assurance ladder:
`DECLARED_ONLY < HARNESS_WIRED < SESSION_EXECUTABLE`.
`CHAT_BRIDGED` does not mean independent verification. `ATTESTED_ISOLATED` requires evidence from a genuinely isolated execution/review path.

## 7. Production and safety constraints

- Do not default to real-person filming, identifiable likeness, or use of personal portrait assets.
- Do not start paid GPU, subscriptions, credits, or third-party uploads without explicit user approval.
- Preserve source provenance, rights, consent, version and digest information.
- Candidate generation, asset promotion, and release are separate gates.
- Rejected, stale, unapproved, or historical assets never become canon by being present in a folder.
- Never fabricate provider execution, render completion, independent review, CI success, publication, or business outcomes.
- Do not ask the user to repeat information already available in the current authoritative project state.

## 8. Startup protocol for a new Video task

When the user says “继续视频”, “继续视频制作”, or gives a Video-domain task:

1. Load the CAOS skill in the current ChatGPT workspace when available.
2. Read this file, `README.md`, `video_growth_agent/data/domain_manifest.json`, and `video_growth_agent/data/capabilities.json`.
3. Resolve the exact project through `projects/PROJECT_INDEX.json`.
4. Read that project's current manifest/state, current progress, graph and only the relevant domain requirements.
5. Inspect the actual current repository/branch/CI state before claiming progress.
6. Restate the task internally as acceptance criteria, then run the CAOS decision loop and execution loop.
7. Keep IPOS and financial-writing authority boundaries intact.

The Video repo remains independently runnable as a domain system. CAOS governance is an external reasoning/acceptance layer in the active session, not an automatic runtime integration.
