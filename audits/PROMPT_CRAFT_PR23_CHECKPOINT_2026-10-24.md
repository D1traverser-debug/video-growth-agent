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

## Stop/restart integrity

- In a fresh chat, **never** silently state this work is finished, that CI is latest without checking, that a candidate technique is validated, that reviewers independently executed, or that a movie was produced if none exists.
- Next concrete self-directed work when no new authorization is available: improve source-contract conformance and test cases with non-paid fixtures, review source-study completeness, inspect existing MediaGraph integration; preserve the PR candidate.
- External blockers are limited to actual missing authorized media, paid generation permissions/credentials and any repo governance required for merge. They do not block unrelated safe coding, learning, research and CI cleanup.
- Every substantive progress/closure must update `audits/EVOLUTION_INDEX.json` and this current candidate checkpoint or supersede them through existing owner process; do not rely on a ChatGPT session to be the sole record.
