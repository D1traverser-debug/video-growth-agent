# Video Growth Agent — Product / Program Orchestration Audit

Date: 2026-10-15
Status: `CANDIDATE_EVALUATION`
Scope: Video Growth Agent 0.6.0 candidate + UAOS 2.5.0 / COMMON_CAPABILITIES 1.6.0 production

## Objective

Repair the Video-domain product topology so AI self-media growth/commercialization and original digital IP can operate as one integrated business Program without collapsing all work into one serial workflow, while adding a general domain-owned orchestration model for parallel, dependent, consultative, competitive and adjudicated subtasks.

## Initial findings

1. The repository already described one Video domain covering AI-video production, growth systems and original digital-IP incubation, but `projects/ai-self-media-commercialization` was still marked as an isolated future-import reference package.
2. That package already contained account positioning, audience/content strategy, monetization hierarchy, advertiser categories, sponsor principles and original-character strategy, so the isolation label contradicted the actual product definition.
3. UAOS held two Video business task/cursor records while the child repository separately held the same Video project truth. This duplicated ownership and repeated the parent/child identity-collapse class previously removed from Financial Writing.
4. The episode `AgenticStudio` already supported artifact-only specialist communication, producer/reviewer separation, review panels and coarse wave concurrency, but readiness was governed by a global lower-wave barrier. It could not express `C depends on A but not unfinished B`, general candidate competition or durable owner adjudication.
5. `system_audit.py` was actively protecting the old architecture by requiring Pilot 002 identity `video-growth:main` and UAOS controller business ownership.

## External method evidence

- OpenAI agent orchestration guidance supports a manager/agents-as-tools pattern when one owner must preserve unified control while bounded specialists handle work with different expertise/tools.
- OpenAI practical multi-agent guidance supports splitting specialists for meaningful tool/instruction/policy boundaries rather than cosmetic role proliferation.
- Anthropic multi-agent research architecture demonstrates orchestrator-worker decomposition and parallel subagents when tasks can be independently scoped, while synthesis/guardrails remain explicit.
- Google testing guidance warns against change-detector/brittle tests that freeze incidental implementation values instead of protecting intended behavior and contracts.

Borrowed properties:
1. one domain owner with bounded specialists;
2. explicit parallel decomposition where dependencies permit it;
3. artifact-mediated synthesis/adjudication rather than unbounded peer dialogue;
4. tests protect semantic contracts, not obsolete historical version constants.

## Governing assumptions challenged

- Rejected: growth/commercialization and original digital IP should remain permanently isolated because they began in different project folders.
- Rejected: integrating the business means one giant state file or one serial pipeline.
- Rejected: every internal concern requires a new persistent Agent.
- Rejected: negotiation should be free-form peer chat.
- Rejected: global wave order is sufficient for every dependency relation.
- Rejected: UAOS should mirror each child Video project/program identity and cursor.
- Rejected: Pilot 002 legacy alias `video-growth:main` should remain a parent task identity.

## Final candidate product topology

### Domain owner
`DOMAIN:video` is the single user-facing business owner.

### Default integrated Program
`ai-self-media-commercialization` is the default integrated Program for generic AI-media growth/commercialization/original-IP intent.

Workstreams:
- `MEDIA_GROWTH`
- `ORIGINAL_DIGITAL_IP`
- `COMMERCIALIZATION`
- `PRODUCTION_SYSTEM`

Each workstream may progress independently unless an explicit graph edge says otherwise.

### Historical projects
Pilot 002 remains an exact child-owned historical project. Its generation/reviewer blockers and rejected/process-invalid evidence remain intact. `video-growth:main` is retained only as a child-domain compatibility alias for exact historical resume.

### Episode production
The existing episode state machine remains a specialized production workflow. The new Program graph does not replace it; Program decisions/assets enter episode production only after explicit promotion and binding.

## Internal orchestration model

The domain runtime supports:
- serial dependency;
- independent parallel work;
- fan-out/fan-in;
- consultation;
- competitive candidates;
- structured critique/revision;
- owner adjudication;
- panel/quorum review.

A node is schedulable from its declared dependencies and runtime artifact inputs rather than an unrelated global barrier. Dependency cycles are rejected.

Consultation is advisory. Competition uses at least two candidate nodes in one decision group. An adjudicator consumes the complete candidate group and emits a durable SELECT/MERGE/REJECT_ALL receipt before dependent work proceeds.

Negotiation is represented as bounded artifact rounds. `peer_chat=false` remains a system invariant.

## Current Program state preserved

Original digital-IP foreground truth is unchanged:
- accepted base remains the original corrected S1+S3 strict-front gray sculpt;
- E1/E2/E3 remain inconclusive;
- A1 remains rejected;
- next IP action remains A2 positive-morph upper-face tuning from the accepted base.

New explicit parallel-ready work:
- H1/A2 upper-face work;
- growth baseline/topic hypotheses;
- advertiser/category mapping.

Character canon blocks only character-identity-dependent downstream assets; it does not block unrelated growth/commercial research.

## Candidate implementation

- UAOS 2.5.0 / common contract 1.6.0: common domain-internal orchestration semantics.
- Video package version 0.6.0 / capability profile 7 / minimum common contract 1.6.0.
- `docs/product_requirements.md` and `docs/architecture.md`: current Video product/architecture authority.
- `projects/PROJECT_INDEX.json`: child-owned project discovery authority.
- integrated Program: `PROGRAM_STATE.json` + `SUBTASK_GRAPH.json`.
- `video_growth_agent/program_orchestration.py`: domain business graph runtime.
- `video_growth_agent/data/coordination-policy.json`: coordination contract.
- `system_audit.py` and dedicated tests: architecture fitness/eval layer.

## Acceptance plan

Parent dependency:
- UAOS 2.5.0 / common 1.6.0 production exists and production CI passes.

Video candidate:
- full pytest PASS;
- `vga system-audit --repo-root .` PASS;
- Program graph cycle/parallel/competition/adjudication/invalidation tests PASS;
- direct-domain/binding/project-index/product architecture tests PASS;
- existing episode agentic-studio/review/generation/media tests remain PASS;
- installed wheel/system-audit smoke PASS;
- no second controller/continuity plane appears.

Promotion/closure:
1. promote Video 0.6.0 only after parent common 1.6.0 is live;
2. observe Video production CI and reread child authorities;
3. only then collapse UAOS's duplicated Video business task/cursor records to one router with optional opaque child reference;
4. rerun UAOS production CI and close the parent evolution with exact child evidence.

## Current assurance ceiling

`PARENT_COMMON_1_6_PRODUCTION_VERIFIED__VIDEO_0_6_CANDIDATE_VALIDATION_REQUIRED`.

Do not claim the Video integration/orchestration repair production-verified until the candidate, child production observation and parent router-collapse closure all pass.
