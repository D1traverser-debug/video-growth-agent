# Video prompt & professional craft candidate — durable continuation

Updated: 2026-10-24
Status: `ACTIVE_CANDIDATE__NOT_PRODUCTION__LIVE_MEDIA_QA_OPEN`
Owner: `DOMAIN:video` (existing Video Evolution Index; **not** a second UAOS/controller/task index)
Candidate: [PR #23](https://github.com/D1traverser-debug/video-growth-agent/pull/23)
Branch: `refactor/prompt-director-core-20261023`
Base: `main@4632634e5133961b3280dcfc5bc211712c3a1c83`
Verified prior candidate head: `ebcaed9ecae6302d878e3a6ad62116aa311ac7da`
Prior green candidate CI: [#39974838896](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/39974838896), jobs `prompt-contract: 66 passed` and `test: 255 passed`; installed CLI smoke PASS. **This is a prior-commit result, not proof that subsequent checkpoint edits pass CI.**
Current branch SHA and latest CI **must be refreshed on every new session**. Never treat hardcoded hashes below as live current state.

## Recovery protocol: read this when user says "继续 video-growth-agent" in a new chat

1. Authenticate/read GitHub `D1traverser-debug/video-growth-agent`; first inspect `main`, [PR #23](https://github.com/D1traverser-debug/video-growth-agent/pull/23), candidate head, CI jobs and merged/closed state. Do not assume chat memory or this dated note is fresher than GitHub.
2. Respect Video domain entry `UAOS_SKILL.md` / `.uaos/MANIFEST.json` and canonical `audits/EVOLUTION_INDEX.json`. This note is **only the current Video candidate workstream evidence/next actions**, not cross-domain governance or a new parent task.
3. If PR #23 remains open/draft, operate on the **candidate branch**, not `main`. If merged, reconcile this record with main/official project state before any new modification. Do not reopen/merge the superseded broad PR #22.
4. Read only task-relevant files: `video_growth_agent/source_director.py`, `prompt_director.py`, `h3_prompt.py`, `prompt_experiment.py`, `craft_round.py`, `roles.py`, `techniques.py`, existing `experiments.py` / `production_os.py`, `video_growth_agent/data/roles.json`, `video_growth_agent/data/techniques.json`, `skills/video-growth-agent/references/self-learning.md`, `craft-source-studies.md`, `prompt-direction.md`; then inspect existing tests and the exact failure at hand.
5. After meaningful changes: update owning source/test and this evidence reference, run candidate CI, inspect failed logs, repair, repeat; record actual run ID, test counts, changes and gaps. The task should continue without repeatedly asking the user for already-given scope.

## Governing user outcome (DO NOT SUBSTITUTE A SIMPLER PROXY)

Build **one** capable AI-video system that researches first-party and professional cinematography/animation/story/edit/audio sources, selects methods *per story*, coordinates specialists, produces professional prompts/storyboards/assets/shots, learns from observed failures and actual screened footage, revises shot/take versions, verifies, and reuses lessons.

- **Not merely** a dense timed H3 prompt system, a prompt-template library, a team-role label collection, a repository file-count cleanup, an endless set of docs, or a 100%-green pytest suite.
- The owner reported one very good result from a specific H3/Hailuo Chinese 10s red-ribbon prompt and poor prior PixVerse output. This is **anecdotal context-specific output feedback**, **NOT** a universal style or model ranking. Never recanonize it.
- Original works/animation must not be burdened with fabricated external factual proof; real-world claims/products/finance and hybrid fiction still require evidence as appropriate.
- Research **original sources** before downstream summaries. Derive transferable mechanisms, use/avoid conditions, falsifiable prototypes, provenance; do not blindly clone third-party workflows or visual styles.
- Complex work may involve writer, director, art, storyboard, edit, sound and red-team input, but **do not make all seven mandatory for a trivial prompt**. Existing `RoleRegistry` is authority; do not duplicate the controller, learning engine, timelines, MediaGraph, or knowledge catalogue.
- Prior successful actions/rejected alternatives and their **why**, not just commands, should survive future chats. Delete ineffective/redundant parts with dependency evidence; preserve working runtime and failure evidence.
- Independent semantic correctness and actual quality are **not proven** by valid JSON, source quote matches, model-written self-ratings or test fixtures.

## Verified implementation, as of prior green CI (before this checkpoint)

1. `source_director.py`: raw timed or untimed user material → SHA-tied lexical source units → model-authored structured plan acceptance. Requires exact source, frame/aspect/model limits, known source audio constraints; rejects missing lexical source units. Model calls are **opt-in HTTPS with explicit upload/spend approval**; default zero extra paid revisions.
2. `prompt_director.py`: static-source linked narrative/shot contracts, frame indices, plan/source guards, per-shot UNREVIEWED targets; contract proof is not onscreen comprehension or full semantic correctness.
3. `h3_prompt.py`: H3 `auto` emits **unranked** `lean`, `chinese`, `official` candidate formulations; retains global art direction and timecoded SFX/music/voice. PixVerse is optional control, not a globally inferior engine verdict. Text-only H3 first/last/reference flows remain unavailable without bound assets.
4. `prompt_experiment.py`: reuse existing `ExperimentPlan` for comparison; variant prompts are fingerprinted; output winner NULL until real evidence. Language/format bundled comparison cannot attribute a difference to language alone.
5. `craft_round.py`: reuse existing `RoleRegistry` to pass **full original script**, all event source spans, shot timing, visual identity and alternative directions to seven **independent-first-pass task packets**; every packet defaults `NOT_EXECUTED`. Optional bounded seven text-LLM calls are simulated specialist critiques, not independent human/editorial review of video. Submitted plan-only critiques must cite exactly corresponding plan SHA and shot evidence, then route issues to their existing owners. New plan versions identify which issues changed/are still untouched; `CHANGED_NEEDS_REVIEW` is not FIXED. Media-quality review belongs with existing MediaQA/attestation.
6. `techniques.json`: T-015 (cross-role handoff), T-016 (matching graphic/action/audio cuts), T-017 (postmortem → falsifiable regression) are **candidate**, not validated. Existing LEARN stage controls promotion. `craft-source-studies.md` records nine **selected source studies**, specific inspected sections, non-transfers and cheap test hypotheses. This does **NOT** mean every resource in their original trees was read in full or its performance proven.
7. Removed verified duplicate/invalid historical material (4 files) with provenance, without dismantling the working 0.8 business runtime. Former large-scope PR #22 was closed, not merged.
8. Baseline static evidence: prior CI run 39974838896 passed all **66 prompt+craft tests** and **255 full repository tests**, system audit and installed CLI smoke. No money was spent on real provider calls or film rendering in these changes.

## Outstanding tasks, priority and proof obligation

**P0 — make the studio actually create and assess art, not merely validate operator-authored JSON.**
- Inspect the actual text-LLM authoring interface with a representative **real** authoring generation, using a configured provider only after explicit upload/cost authorization; no secret or paid-call inference. Compare resulting story alternatives, semantic omissions, cinematic usefulness, and completion against independent reference.
- Test adversarial sources beyond the 10s ribbon scenario: original fiction, long narrative, factual explainer with exact claims, brand/product film, action/cloth/hand contact, simple 5s IP hook. Validate that the model does not blindly inherit one genre or prompt density.
- Couple reference-board/character/scene asset binding and image-to-video routing to existing MediaGraph/production modules (do not fake unavailable image references); preserve identity, prop states and directed cut geometry.
- Generate **real representative H3 (and optional comparative provider) footage only with authorized provider access/spend**, save output files, seeds/parameters, timestamps, costs, model version and output digest. Blind viewer understanding, identity/action physics, editability, sound timing and relative quality must be assessed using actual playback.
- Compare `lean`, `chinese`, `official` along controlled scene-specific experiment axes. Avoid “H3 is best” or “Chinese is best” on one anecdote. Confirm what exactly matters, including model version/scene complexity.
- Define precise rejected-take diagnosis → minimal scene/shot repair → new plan/take version → reinspection → existing LEARN candidate update. A successful loop should improve real media, not merely increase files.
- Revisit and simplify candidate architecture after actual usage; prevent duplicative status/approval/governance layers.

**P1 — authentic professional learning and team operation.**
- Continue source-by-source study of original Skills and craft fundamentals, not just table-of-contents or summaries. Maintain provenance for what was actually examined, applicable mechanisms and unanswered research. Do not claim comprehensive mastery of nine entire sources.
- Exercise seven role-model critique calls and actual disagreement resolution on real plans only when authorized; otherwise explicitly mark them unexecuted. Role calls to one text model are not seven independent experts.
- Retain versioned work artifacts and evidence in the existing Video project/evolution authorities, not new session-specific controller. Track non-promotion until effects generalize and independent QA passes.

**P2 — promotion/cleanup:** PR #23 is intentionally draft and `main` unchanged. After criteria above are met (or an explicitly bounded architectural slice has owner-defined promotion criteria), review changed files individually, delete obsolete pieces, validate complete CI, and only then consider merge according to repo governance. Do not assert “system complete” because candidate tests pass.

## Operator commands (from repo candidate checkout)

```bash
vga author-director tests/fixtures/ribbon_original_30s.txt --seconds 10 --source-ref user-quoted://full-30-second-ribbon-storyboard-2026-10-23
vga author-director tests/fixtures/ribbon_original_30s.txt --seconds 10 --source-ref user-quoted://full-30-second-ribbon-storyboard-2026-10-23 --model-output tests/fixtures/prompt_ribbon_fullsource_10s.json
vga direct-prompts tests/fixtures/prompt_ribbon_fullsource_10s.json --route onepass --plain
vga direct-prompts tests/fixtures/prompt_ribbon_fullsource_10s.json --review-sheet
vga craft-round tests/fixtures/prompt_ribbon_fullsource_10s.json
vga techniques --tag review --include-candidates
pytest -q tests/test_prompt_director.py tests/test_prompt_experiment.py tests/test_source_director.py tests/test_craft_round.py
pytest -q
vga system-audit --repo-root .
```

The 30-second original used in the fixture is a repository transcription; the original owner-authored source must be checked against the true first-hand input before labeling *semantic* preservation proof. Its 24 lexical time spans are **not** evidence that the entire original film is perceived in 10 seconds.

## October 24 continuation — operator-path repair and artifact-bound review (candidate only)

Latest **verified code head before recording this checkpoint**: `a7d7d0084973fbbfdb7da01f9f97c07dafe5c7df`.
Actual GitHub Actions [#39987972345](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/39987972345) completed success at 2026-10-24 00:36:36 +08:00: `prompt-contract 67 passed`; full `test 260 passed`. Both jobs succeeded. This is evidence for the named SHA, **not automatically for later documentation commits**.

- **Operator contract defect repaired**: `vga author-director --out-plan` had serialized a literal backslash-n after the JSON document, so downstream tools could not parse the generated plan. Export now emits a real newline. A subprocess regression runs raw original -> imported authored plan -> exported valid JSON -> `direct-prompts` -> `craft-round`.
- **Historical test scope corrected**: prior Common Behavior 1.3 closure test wrongly forbade any future `current_candidate`. It now asserts only that the *1.3 adoption* is not reopened; the independent PR #23 Video candidate remains valid.
- **Existing QA integration, no shadow controller**: `video_growth_agent.media_qa.prepare_directed_media_review` combines the existing `build_shot_review_targets` sheet with the existing `MediaQAChecker` for **actual local file bytes**. `vga direct-prompts PLAN.json --review-sheet --media TAKE.mp4 [--frames-dir DIR]` binds a take SHA-256, byte length, full technical QA report, expected/observed duration mismatch, optional real frame samples, source plan SHA and an unexecuted neutral first-viewing questionnaire. Planned cut timecodes remain hypotheses until checked against playback.
- **Adversarial reality check**: the test feeds a 2-second **FFmpeg-generated synthetic color/audio clip** to a 5-second fictional plan; mismatch is explicitly detected. This is a *pipeline mechanics* fixture, not a video-model sample, creative success, independent review or a real viewer result.
- **Unresolved technical-QA defect**: the existing `MediaQAChecker._black_check` and long-silence detection can report `PASS` if an FFmpeg detector command exits nonzero without emitting detection lines. This was identified during source review. The attempted mutation to fix that path did **not** apply (operation blocked), so fail-closed detector semantics remain open; do not treat a clean technical QA report as incontrovertible.
- **Unresolved quality/evidence**: no paid H3/PixVerse clip, no complete source-to-model real generation, no model settings/seed/cost ledger, no blinded human/artistic assessment, no matched-scene policy experiment, no measured revision improvement, and no production promotion. Asset binding is local byte identity, **not** a `MediaGraph` asset registration or verified provider attribution.

**Recommended next evidence-supported work**: first confirm latest head CI after this metadata write; investigate the FFmpeg failure-status assurance issue in the owning MediaQA path when write authorization permits; next integrate bound take versions with existing MediaGraph and operator review/LEARN evidence without replicating their lifecycle. Await actual authorized video or provided clip for perceptual QA. Continue on PR #23 draft, leave `main` intact.

## Continued engineering — director plan → graph-backed real Take (2026-10-24)

**Implemented candidate head before metadata updates**: `1f8fd7ed9293888e073a7e239c175b3329269b18`. Still PR #23 Draft, `main` untouched; an implemented commit alone is not V&V. [Run #39991531116](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/39991531116) showed prompt-contract success and full-test job in progress at last inspection; refresh exact HEAD workflow before reporting an overall PASS.

**Actual change—not another controller/graph**: Existing `plan_graph_bridge.py` now registers one `DIRECTOR_PLAN` source asset and a derived `VIDEO_TAKE` candidate in the existing `MediaGraph`. It requires the *real local director plan file* to equal the plan content; verifies a canonical plan digest; inspects actual local video bytes using current `MediaQAChecker`; binds SHA-256, QA report, observed duration/mismatch and unexecuted per-shot review targets to an immutable `EvidenceRecord`. Missing project context, contradictory immutable plan version and duplicate Take version fail closed. No provider-run identity, visual quality, blind human review or promotion is asserted. Explicit `graph.invalidate_downstream(old_plan_ref)` makes descendants stale; newer plan versions are not automatically declared artistically better.

**Working operator entry** (requires a previously populated real MediaGraph with the specified Sequence/Shot context and actual local media):

```bash
vga register-directed-take GRAPH.json PLAN.json TAKE.mp4 \
  --context-id SQ1 \
  --director-plan-id directed-plan:SQ1 --plan-version p1 \
  --take-id rendered-take:SQ1 --take-version t1
```

CLI writes using existing `MediaGraphStore`, outputs the prepared review packet and explicitly `CANDIDATE / NOT_STARTED / NOT_VERIFIED`; it refuses to silently create a new graph or overwrite a take. Existing lighter `direct-prompts --review-sheet --media` path is unchanged.

**Reproduction**: `tests/test_plan_graph_bridge.py` adds a real FFmpeg synthetic-color/audio fixture (NOT a provider render or test of art) exercising exact file hash, plan/take link, version conflicts, evidence roundtrip, stale invalidation and no auto-promotion; CLI regression checks persistent graph and no overwrite on duplicate. These tests are not film-quality evidence.

**Remaining integration/quality gaps**: user-approved provider generation and genuine media artifact are absent from the repository (verified current git tree has no .mp4/.mov/.webm/.mkv). The bridge does not yet connect to a verified provider-issued run/seed/model/cost receipt, production `TakeRecord`/rights decision, independent motion+sound review attestation, experiment outcome, or LEARN promotion. Review evidence is metadata awaiting real footage and independent screening; a real take should not be admitted to release based on candidate registration. Known FFmpeg detector nonzero-exit false-PASS issue remains unresolved; prior attempted write to the detector path was blocked and was not retried through an alternate action. Future operator work must validate actual source files, QA error paths and context initialization; do not equate a successful test with production media.

**Next autonomously executable direction**: first inspect latest CI on current head and correct any failures, then reuse existing reviewer execution attestation and `TakeRecord` to bind authentic playback/verdict evidence; only actual authorized rendered footage may close semantic, visual and audio goals. Avoid inventing another QA lifecycle.

## Verified continuation — graph-backed Take intake and transitive freshness (2026-10-24)

**Current verified code head, prior to checkpoint bookkeeping**: `de5e94bb7b1f916ad7e282f12c401a7dde6e33e0`, PR #23 Draft and unmerged. Actual [Actions run #39993554389](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/39993554389) completed `success` on **that exact SHA** (UTC 2026-10-23 17:16:07): `prompt-contract 76 passed, 2 skipped` (skips are FFmpeg-real-media tests unavailable in the fast job), `test 265 passed`, system audit PASS, and packaged CLI smoke PASS. These are code/contract tests, not observed video quality or model effectiveness.

**Implemented since previous checkpoint**:
- `register_directed_take_observation` in existing `video_growth_agent/plan_graph_bridge.py` and CLI `vga register-directed-take` store a real locally inspected video candidate in the existing `MediaGraph` with `DIRECTOR_PLAN -> VIDEO_TAKE` versioned lineage, canonical plan SHA, source URI and byte digest, SHA-bound media inspection, and an evidence record containing the **unscored** review sheet. A stable Sequence/Shot context and explicit version identifiers are required. Missing/contradictory source, missing context and duplicate asset version reject. Registration never promotes a Take, attests model generation, or fabricates a viewer.
- `tests/test_plan_graph_bridge.py` now covers real local FFmpeg test-pattern files and graph persistence, exact SHA, duration discrepancy, deliberate old-plan invalidation, immutable identity, candidate-only state and CLI refusal to overwrite. A separate mock inspection checks graph contracts without falsely claiming physical media/FFmpeg coverage.
- **New failure-class remediation at the owning abstraction:** `MediaGraph.promote_asset` previously permitted `STALE` assets to be re-promoted, and would allow a still-`CANDIDATE` descendant of a stale plan when explicit invalidation had not propagated. It now blocks stale targets **and transitive stale/rejected/retired ancestors**. Regression tests reproduce both bypasses and verify legitimate fresh candidates retain existing promotion paths.
- Fast `prompt-contract` CI now includes MediaGraph and plan-bridge tests (FFmpeg-dependent tests skip only in this fast job; full job ran all 265 tests).

**Validated scope**: graph contracts, local generated test-pattern bytes and interface persistence; no vendor video was generated, no real viewers watched, no provider-issued run/seed/cost proofs, no independently verified storyboard semantics, no real revision quality uplift and no commercial observation. Stale eligibility repair is not a substitute for strict positive promotion evidence or existing independent reviewer attestation. PR #23 still must remain Draft until owner-defined review/promotion gates are met.

**Known open limitations**: the previous `MediaQAChecker` FFmpeg detector error-exit false-positive issue remains unmodified after operation-specific write denial; local media and plan paths stored in Graph must remain available or be migrated to durable storage; a `VIDEO_TAKE` asset is not yet a verified `production_os.TakeRecord` backed by a provider receipt; registered review sheets remain `NOT_EXECUTED` and cannot prove human viewing. Existing film review/provider attestation and LEARN owners should be reused for those subsequent capabilities.

**Autonomous next actions**: (1) refresh final CI after bookkeeping commits, (2) use authentic video take plus source/shot review to test actual perceptual semantics, (3) connect verified provider receipt/rights, TakeRecord and independent review to this graph lineage, (4) run controlled per-scene prompt A/B + rejected-take revision/learning without naming a quality winner until observed. No paid calls without approval.

## Whole-system goal-fit correction — 2026-10-24

**Governing user correction**: the task is to determine, engineer and verify whether the **whole Video system** achieves the user's actual AI-video, professional-craft, iterative improvement, reusable IP and business outcome—not to pursue a sequence of convenient isolated PR bug fixes or maximize test counts. No guarantee of universal zero defects can be honestly made. Reject an architecture-only, QA-count-only or report-only closure. Preserve working Video 0.8 owners, identify incomplete physical provider/external/editor/publishing operations, repair admitted system defects, and independently verify real outcomes.

**Primary cross-system source**: [Video end-to-end goal-fit audit](VIDEO_END_TO_END_GOAL_FIT_AUDIT_2026-10-24.md) covers all `docs/product_requirements.md` VR-01..VR-18, with actual owner modules, operator entrypoints, evidence classes, high-risk gaps, scenarios and release-level proof ladder. Its status remains OPEN; it is *not* a new authority or parallel controller. Distinguish procedural/structural controls from real independent film playback.

**Root findings**:
1. No evidenced physical end-to-end real provider render → verified downloaded media → actual motion/sound/story inspection → rejected shot repair → repeated comparative result → LEARN/platform/business feedback. Current authoring/prompts, plan critiques and Take import are useful but not equivalent to rendering.
2. `ProductionAdmission.evaluate_take_promotion` could accept low-risk Takes without any technical QA receipt; `MediaGraph` could return a previously promoted Take after its source plan was superseded if no explicit invalidation was called.
3. Two local owner state stores used fixed temp paths with no stale-writer protection, making concurrent edits/lost updates possible despite rename atomicity.
4. Green `vga system-audit` was at risk of being overstated as proof of user-goal completion; it is a static/config/runtime-invariant check only.
5. Existing unresolved: FFmpeg detector command nonzero-exit may falsely look clean (prior mutation blocked); provider authenticity/cost/asset SHA/budget and owner-trusted independent playback are not integrated; media storage portability and user business outcomes lack real receipts.

**Directly implemented on PR #23** (no parallel architecture):
- `media_graph.py`: effective transitive stale state in read paths, `current_promoted` and timeline consumers; preservation of history.
- `production_os.py`: technical-QA evidence ref required for promotion (string refs still need verified artifact binding).
- `checkpoint_io.py` shared by `MediaGraphStore` and legacy `ProjectStore`: per-file writer locks on supported local OS, unique temp, optimistic revision match, atomic replacement and explicit post-rename durability uncertainty. Tests exercise stale writers, concurrent commits and failed writes. No claim of multi-host distributed transactions.
- `system_audit.py`: `assurance_scope` explains precisely why passing static QA is not media/story/commercial quality; existing `pass` retained for compatibility.
- New/updated tests: `test_checkpoint_io.py`, `test_media_graph.py`, `test_production_os.py`, `test_agent_operable_media_os_trajectory.py`, `test_system_audit.py`.
- Relevant official first-party API verification: MiniMax `/v2/video_generation` plus `/v2/query/video_generation/{task_id}` and supported model/duration/resolution/modality combinations. **No real API call, cost, H3 clip or artistic comparison** was made.

**Prior tested code receipt, BEFORE this checkpoint metadata edit**: [GitHub Actions #40050305195](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/40050305195), exact SHA `2f47754ea0475fc54012bb99efb74b12fb05c4b4`: full **274 passed** with installed CLI smoke and system audit; fast contract **77 passed, 2 skipped**. Recheck final PR HEAD CI after checkpoint/index updates; never promote these prior counts as latest if HEAD differs.

**Required next substantive action**: implement and exercise the **existing owner's** lawful provider generation path with recorded intent/approval, version-bound reference inputs, current capability/budget checks, task submit/query/asset retrieval, receipt/cost/error recovery and physical media digest. Reuse Video ShotContract, ModelRouter and MediaGraph, not another video controller. Then real blind perceptual screen/shot-specific repair/LEARN and platform outcomes. No paid provider calls without explicit user approval. Independently address remaining FFmpeg technical detector risk and platform-specific storage recovery. PR #23 remains Draft/unmerged pending observed goal-level acceptance.

## Stop/restart integrity

- In a fresh chat, **never** silently state this work is finished, that CI is latest without checking, that a candidate technique is validated, that reviewers independently executed, or that a movie was produced if none exists.
- Next concrete self-directed work when no new authorization is available: improve source-contract conformance and test cases with non-paid fixtures, review source-study completeness, inspect existing MediaGraph integration; preserve the PR candidate.
- External blockers are limited to actual missing authorized media, paid generation permissions/credentials and any repo governance required for merge. They do not block unrelated safe coding, learning, research and CI cleanup.
- Every substantive progress/closure must update `audits/EVOLUTION_INDEX.json` and this current candidate checkpoint or supersede them through existing owner process; do not rely on a ChatGPT session to be the sole record.
