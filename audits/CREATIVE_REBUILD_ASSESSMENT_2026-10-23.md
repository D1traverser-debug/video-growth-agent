# Repository audit and creative-method reconstruction — 2026-10-23

**Scope:** `D1traverser-debug/video-growth-agent` only. Main at `4632634e5133961b3280dcfc5bc211712c3a1c83`. Candidate PR #22.

## 1. Honest evidence inventory

- Git tree returned `truncated=false`, with **162 Git blobs** and 1,068,561 reported bytes.
- All 162 paths were fetched and their returned blob SHAs matched the tree; JSON files were parsed as syntax checks where applicable.
- These facts establish exhaustive **retrieval and object integrity**, **not** an independent proof of per-line business or film semantics.
- Complete exact path/SHA ledger is `audits/FILE_AUDIT_LEDGER_2026-10-23.json`; every item intentionally states `semantic_proof=NOT_INDEPENDENTLY_PROVEN`.
- Pre-existing baseline offers 39 test files and 39 code/resource files under `video_growth_agent/`; the other files cover project state, candidate/rejected designs, older audits and Skill references.

## 2. Authority and existing working mechanisms

`README.md`, `UAOS_SKILL.md`, `.uaos/{ADAPTER,MANIFEST,CAPABILITIES}.json`, `docs/{architecture,media_business_os,product_requirements}.md` and current project state agree on one child-owned Video business plane. Existing Python runtime provides asset lineage, editorial plan, continuity, routing, timeline, external editing handoff, experiment and QA/release gates. This is a real partial implementation, not an empty doc skeleton.

**Do not preserve bad mechanisms by doctrine.** Avoiding a parallel controller is only a requirement to have a single explainable current authority after a chosen redesign. It does not forbid replacing or retiring that authority following objective migration and regression evidence.

## 3. Concrete gaps exposed by user scenarios

1. **Craft expressiveness gap:** `ShotIntent` has narrative job, target seconds and must-show; it does not model frame-accurate editing, focal lengths, subject blocking, physical transition geometry or cue timing. The legacy stage workflow's `STORYBOARD` artifact is unstructured and cannot validate that a requested 30s→10s compression still includes each important event.
2. **Unproved prompt-to-pixel jump:** roles in `agents.json` describe craft judges but do not ensure an independent human/vision review actually watched a given output. Such declarations cannot certify a 5s generation.
3. **Version/ontology load:** packaged legacy stage workflow at `workflow.json` version 0.3.1, specialized agents 0.7.0 and core runtime 0.8.0 have explicitly documented compatibility boundaries. Compatibility is not the same as usability; keep only as long as concrete scenarios prove each surface is useful.
4. **Fiction vs evidence policy:** `EpisodeIntent` currently requires `evidence_refs` even for creative-only episodes. Factual claims correctly require citations, but the global constraint should be tested on pure fiction and potentially decoupled; no speculative destructive edit in this PR.
5. **Capability vs execution:** `model_registry.py` models operation profiles, but the CLI previously exposed the legacy stage-driven interface rather than directed script-to-shot production. A declaration of provider support still does not prove duration, costs or per-frame adherence in practice.
6. **Independent assurance boundary:** CI/system audit checks code and state invariants, not artistic semantics for all 162 blobs. No automatic test proves emotion, originality, sound sync or actual frame content from metadata.

## 4. Competing options and present evidence

| Method | Structural execution | Best justified application | Current evidence |
| --- | --- | --- | --- |
| A. Single prompt / native V6 multi-shot | one prompt, integer-second model duration | 5s low-density concept exploration | prompt generated and structural checks only |
| B. Shotwise AI generation + frame timeline edit | one prompt per contract, integer-second clips trimmed in NLE | demanding 10s montage and handoffs | prompt generated, exact edit frames/event tags checked |
| C. Anchor-first keyframes + shotwise | reusable approved first/last/identity references | branded hero IP, constrained physical contact | studied as method, no render or benchmark yet |

Prompt generation under A/B is an **executed tooling comparison**, but not a quality comparison of resulting media. C is not implemented as an engine adapter and cannot be scored honestly. No paid provider was used. Selection remains context-sensitive rather than one globally winning route.

## 5. Changes in this draft

- `creative_direction.py`: framed craft specification with strict fields, story-event inventory, continuity annotations, per-shot actions/camera/lighting/transitions/audio cues, exact half-open integer frame segments, prompt-limit errors and legal integer PixVerse V6 render durations.
- `vga storyboard FILE --route onepass|shotwise|compare`: generated shot packets or side-by-side contract statistics; never self-awards film quality.
- Two opposed fixtures: Shiba creator-IP 5s (150 frames) vs red-ribbon love story 10s (300 frames) with explicit retained event inventories.
- Negative tests for missing story events, gaps, overlaps, bad IDs, overflow, unsupported provider adapter, provider timing and absent execution assurance.
- Professional craft Skill with producer/director/cinematography/editor/VFX/sound division, alternative creation strategies, cost and failure method.
- Existing business/runtime/source authority left intact; only Video repo modified. No provider spend.

## 6. Independent evidence still required before calling it complete

- Run PR CI including all original tests, audit and installed CLI smoke (see PR check results).
- Verify story referent with a real immutable `EditorialPlan`, not only a declared URI; strengthen typed integration.
- Assess human readable/shots-at-beat comprehension with actual generated sample frames (external capability/credits authorization required for non-free API).
- Attempt mutation/regression tests of existing legacy stage/orchestration to decide retire/migrate rather than assume it is correct.
- Audit files by **claims and invariants**, not by “pass” stamp on every read line: each architectural statement must link to executable contract test, counterexample or externally observed artifact.
- Compare post-production handoff via existing `timeline.py` and `editorial_interchange.py` against professional OTIO contract without importing a duplicate NLE state.

## 7. Primary source research and transfer limits

- PixVerse V6 official guide: https://docs.pixverse.ai/PixVerse-V6-User-Guide-3373e99bf35080dfa9d8c44f30fde3bc (web mode 5,000 characters, integer 1–15s, multi-shot, native audio).
- PixVerse V6 prompt experience: https://pixverse.ai/en/blog/pixverse-v6-ai-video-generator-review (physically observable prompt instructions and retry evidence).
- Adobe Match Cut: https://www.adobe.com/creativecloud/video/discover/match-cut.html (graphic/action/audio match classes).
- ASWF OpenTimelineIO: https://github.com/AcademySoftwareFoundation/OpenTimelineIO (timeline interchange, not a media container).
- Netflix studio asset delivery: https://studiopartner.netflix.net/studio/backlot-imf-delivery (technical media integrity and downstream acceptance separation).
- Repository existing `production-intelligence.md` already lists DramaClaw, Toonflow, H3, Utopai and BigBanana; they are compared by portable mechanisms, not by copying a vendor's entire stack.

**Assertion discipline:** semantic correctness is scoped to an invariant whose proof is independently inspectable; corpus integrity and test success must not be reported as 162 independent semantic proofs.

## 8. Independent lineage counterexample and repair

Line inspection of `video_growth_agent/media_graph.py` exposed a concrete causal bug: promoting `canon@v2` marked `canon@v1` stale but did not automatically stale a promoted keyframe and video take still derived from `canon@v1`. A separate manual `invalidate_downstream` method existed, but promotion did not invoke its effect. Likewise `promote_asset` allowed re-promoting a previously STALE asset with its old decision because its state guard only forbade REJECTED/RETIRED.

**Repair candidate in PR #22:** replacement promotion automatically stales old-version consumers, removes their promoted pointers, and blocks re-promotion of STALE versions. The traversal does not invalidate the newly approved replacement even when its provenance explicitly derives from the superseded version. A `test_media_graph` counterexample tests both causal descendant invalidation and legitimate new-lineage preservation; stale re-promotion must fail closed.

This is a genuinely identified runtime failure mode, unlike restating a quality gate. It still requires complete CI regression confirmation on the latest PR head and does not demonstrate that all other MediaGraph paths are correct.
