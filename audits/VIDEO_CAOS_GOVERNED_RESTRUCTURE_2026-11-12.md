# Video Growth Agent — CAOS-Governed Restructure and G2 Task Admission

Date: 2026-11-12  
Candidate: existing Draft PR #23, branch `refactor/prompt-director-core-20261023`  
Current production baseline: Video 0.8.0 on `main`  
CAOS write scope: NONE

## 1. Authority and scope

The user instructed that CAOS governance methods guide the Video system, while no CAOS code, comments, docs, Skills, branches, PRs or commits may be modified. The only write target is `D1traverser-debug/video-growth-agent`.

CAOS current main was observed at `9686cedeb3fd8171ecf70eab33aaea641217b04a`. Draft PR #63 is still open/unmerged and is not treated as production authority. The Video integration is read-only method adoption, not a live CAOS runtime connection.

## 2. Current business task recovered

The current foreground task is `ORIGINAL_DIGITAL_IP/G2_REBUILD_AFTER_R31_20261112`.

- G2 reset; no approved original character, identity anchor, avatar, production prompt or canon.
- R28-C/R29 and R31 candidates remain rejected evidence, not references.
- H1/S1+S3/A2 is superseded historical-only.
- The active G2 task is three structurally distinct routes, red-team comparison, contract-gated black-and-white three-column low-fidelity study and final user aesthetic adjudication.
- `红绸赴约` is a separate earlier video task and does not replace the current avatar G2 focus.

## 3. Verified systemic defects addressed in this candidate

1. The scheduler previously ignored graph-declared `SUPERSEDED`, `BLOCKED`, `execution_allowed=false` and `historical_only`; stale tasks could become READY.
2. The graph validator previously did not require unique upstream producers or dependency-ancestor lineage for every declared input artifact.
3. Downstream canon work had no executable guard requiring an explicit SELECT/MERGE decision; REJECT_ALL could still leave a downstream node apparently satisfiable.
4. The system audit hard-coded the retired H1/A2 cursor instead of validating consistency among current Program focus, manifest, child task state and graph.
5. The migration branch's task state and graph were not accepted as production truth; only current G2 authority files were recovered, not its broken scheduler/runtime changes.

## 4. Candidate changes

- ProgramGraph validates declared lifecycle eligibility, unique artifact producers and input dependency ancestry.
- ProgramOrchestrator keeps superseded/historical/blocked/disabled nodes out of READY, blocks downstream work after failed/blocked/superseded dependencies, validates decision outcomes and restricts fail/adjudication actions.
- The integrated task graph contains the current G2 route/counterreview/contract/study/review/user-decision chain, while preserving independent growth and commercialization work.
- Old H1 nodes remain explicit non-executable historical nodes.
- System audit checks current Program/manifest/IP checkpoint consistency and requires G2 gating.
- CAOS method adoption is documented separately from the existing UAOS adapter.

## 5. Verification status

This checkpoint records the intended repair and test coverage; it does not claim CI has passed.

- Previous 326-test/system-audit evidence belongs to older head `58278987fe82757427522ef8ecaab6c1d6b7f49b`, not the current PR head.
- PR #23 head before this restructure was `eda4de6b9ab1a92013f45c41a74659450f5f866b`; no matching-head check run was returned.
- Lifecycle and lineage tests are added for superseded/blocked/disabled readiness, missing/non-ancestor input producers, REJECT_ALL decision gating and fail-only-when-ready.
- Exact-head CI and system audit remain required after this commit.

## 6. Explicit non-claims / remaining work

Not proven:
- current exact-head CI;
- actual G2 route design research completion;
- actual image generation, prompt/seed receipt or visual quality;
- user selection/approval of a character;
- G3/G4/G5/G6 completion;
- actual video generation, playback, independent audience comprehension, publication, growth or commercial outcomes;
- a live CAOS runtime connection.

The candidate remains Draft and unpromoted until exact-head CI, repository audit, negative/neighbor tests and current G2 task evidence are inspected. A green CI will not close the real visual/media/business outcome.
