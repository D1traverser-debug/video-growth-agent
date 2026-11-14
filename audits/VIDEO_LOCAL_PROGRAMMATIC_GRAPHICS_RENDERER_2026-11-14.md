# Video Local Programmatic Graphics Renderer — Candidate Audit

Date: 2026-11-14 (Asia/Shanghai)
Status: CANDIDATE_PR_OPEN__NOT_MERGED
PR: https://github.com/D1traverser-debug/video-growth-agent/pull/33
Candidate branch: `feat/video-local-programmatic-graphics-renderer-20261114`
Latest verified renderer code head at this audit update: `df580452c2eca46d9fd0d8b0646527395900e763`

## 1. User/business problem

The Video production OS had deterministic media QA and shot/timeline governance, but no local executable visual-generation path for ordinary information shots. External AI image/video/audio routes remained declared-only without a trusted provider executor. As a result, a title card, metric, quote or explanatory chart could be planned but not actually rendered by the current runtime without a third-party generator.

## 2. Root causes and independent review defects

1. Missing local deterministic executor for non-character information graphics.
2. FFmpeg drawtext default expansion could interpret literal percent/expansion sequences in source-backed values.
3. MediaGraph candidate registration previously trusted asset/version identity without checking that the actual promoted source digest matched the ShotContract reference binding.
4. Text wrapping counted characters instead of measuring glyphs; long metrics could clip while technical QA still passed.\n5. Chart rows used a fixed minimum vertical gap independent of point count and measured label height; a two-line sixth label could extend below a 640×640 frame while width-only layout evidence still passed.\n6. The first candidate metadata update added an open evolution item without binding it to `current_problem_refs`; repository hygiene audit correctly failed closed. The reference was added and exact-head system audit now passes.\n7. The graph validator checked only that a SHOT context existed, not that its actual parent chain resolved to the `ShotContract.sequence_id`; this allowed a candidate to claim the wrong sequence while registering under the graph's actual sequence.

## 3. Selected architecture

Add `video_growth_agent/programmatic_graphics.py` as a bounded local executor using FFmpeg for MP4 rendering and Pillow/FreeType only for actual font-metric measurement.

Supported visual kinds:
- TITLE_CARD
- QUOTE_CARD
- STAT_CARD
- BAR_CHART

Admission requires an explicit `PROGRAMMATIC_GRAPHICS` ShotContract mode, editorial-plan/beat binding, synthetic truth mode, disclosure requirement, and source-claim IDs for claim-backed stat/chart/quote content. IPOS identity-dependent shots and product-truth shots are explicitly rejected.

## 4. Integrity and safety boundaries

- Text is pixel-wrapped/fitted using the selected local font. Layout evidence records chosen font sizes, measured glyph widths and available pixel budgets. Unfit text fails before media output.\n- Chart rows are dynamically allocated between measured top/bottom boundaries. Label, value and bar heights/positions are checked against each row; two-line labels shrink to the available row height and impossible layouts fail before rendering.
- FFmpeg drawtext uses `expansion=none` for literal text fidelity.
- Source references require exact promoted MediaGraph versions and digest equality with the ShotContract; CLI preflight and graph registration use the same validator.\n- The SHOT context's parent chain must resolve to the exact `ShotContract.sequence_id`, allowing only SHOT → SEQUENCE or SHOT → SCENE → SEQUENCE; both CLI preflight and registration use this shared fail-closed check.
- Output is a silent visual preview, registered only as `CANDIDATE`.
- No paid API, network access, AI footage/audio, observed real/product-truth claim, IPOS identity rendering, promotion or release authority.
- Existing output files are never overwritten.

## 5. Implementation map

- `video_growth_agent/programmatic_graphics.py`
- `video_growth_agent/cli.py` — `vga render-graphic`
- `pyproject.toml` — Pillow dependency for local font metrics
- `video_growth_agent/data/capabilities.json`
- `video_growth_agent/data/domain_manifest.json`
- `tests/test_programmatic_graphics.py`
- `projects/ai-self-media-commercialization/samples/programmatic-graphics-request.example.json`
- operator README, production architecture, requirements, strategy, skill and scenario documentation

## 6. Verification

The candidate includes focused tests for:
- actual FFmpeg MP4 output and FFprobe/Media QA;
- CLI invocation and exact MediaGraph candidate registration;
- synthetic/product-truth/IPOS identity boundaries;
- exact promoted source version/digest binding;
- literal percentage handling;
- long portrait stat metric auto-fit and impossible-metric rejection;
- pixel-bounded title/subtitle layout;
- long bar-chart value auto-fit;
- no-overwrite and receipt-tampering rejection.

Exact renderer code head `df580452c2eca46d9fd0d8b0646527395900e763` passed both CI runs `43595226122` and `43595220908`: 252 tests, repository system hygiene audit, and installed CLI smoke all passed. Five Codex review threads are resolved, covering literal text expansion, exact source digests, horizontal metric fit, vertical chart-row fit and Sequence ancestry. A fresh full Codex review was requested against the latest head; final approval is still pending.

## 7. Governance

- Video Growth Agent only.
- CAOS source repository/code/PRs are untouched.
- IPOS authority and canon remain unchanged.
- PR #33 is open and not merged. Candidate code is not production capability until exact-head CI, independent review and merge/mainline verification pass.
- This renderer does not unblock identity-dependent work and does not replace generative video providers.

## 8. Next action

Await and inspect the fresh full Codex review against the verified head. If it introduces no findings, update the candidate handoff records, merge PR #33, then run mainline CI. Do not mark production-verified until the merged commit passes mainline CI.
