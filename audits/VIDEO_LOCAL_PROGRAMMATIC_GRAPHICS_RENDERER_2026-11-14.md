# Video Local Programmatic Graphics Renderer — Candidate Audit

Date: 2026-11-14 (Asia/Shanghai)
Status: CANDIDATE_PR_OPEN__NOT_MERGED
PR: https://github.com/D1traverser-debug/video-growth-agent/pull/33
Candidate branch: `feat/video-local-programmatic-graphics-renderer-20261114`
Latest recorded candidate head at audit creation: `ee6d17a634978522d1df40a773707cf8a487ec87`

## 1. User/business problem

The Video production OS had deterministic media QA and shot/timeline governance, but no local executable visual-generation path for ordinary information shots. External AI image/video/audio routes remained declared-only without a trusted provider executor. As a result, a title card, metric, quote or explanatory chart could be planned but not actually rendered by the current runtime without a third-party generator.

## 2. Root causes and independent review defects

1. Missing local deterministic executor for non-character information graphics.
2. FFmpeg drawtext default expansion could interpret literal percent/expansion sequences in source-backed values.
3. MediaGraph candidate registration previously trusted asset/version identity without checking that the actual promoted source digest matched the ShotContract reference binding.
4. Text wrapping counted characters instead of measuring glyphs; long metrics could clip while technical QA still passed.

## 3. Selected architecture

Add `video_growth_agent/programmatic_graphics.py` as a bounded local executor using FFmpeg for MP4 rendering and Pillow/FreeType only for actual font-metric measurement.

Supported visual kinds:
- TITLE_CARD
- QUOTE_CARD
- STAT_CARD
- BAR_CHART

Admission requires an explicit `PROGRAMMATIC_GRAPHICS` ShotContract mode, editorial-plan/beat binding, synthetic truth mode, disclosure requirement, and source-claim IDs for claim-backed stat/chart/quote content. IPOS identity-dependent shots and product-truth shots are explicitly rejected.

## 4. Integrity and safety boundaries

- Text is pixel-wrapped/fitted using the selected local font. Layout evidence records chosen font sizes, measured glyph widths and available pixel budgets. Unfit text fails before media output.
- FFmpeg drawtext uses `expansion=none` for literal text fidelity.
- Source references require exact promoted MediaGraph versions and digest equality with the ShotContract; CLI preflight and graph registration use the same validator.
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

Previously verified exact candidate head `dba8b105d62ba1708685edc87832736096473b33`: CI passed, 246 tests, system audit and installed CLI smoke. The current head adds the long chart-value regression and is awaiting exact-head CI and a fresh Codex review. Do not carry forward the 246 count as the current final count until the latest run is read.

## 7. Governance

- Video Growth Agent only.
- CAOS source repository/code/PRs are untouched.
- IPOS authority and canon remain unchanged.
- PR #33 is open and not merged. Candidate code is not production capability until exact-head CI, independent review and merge/mainline verification pass.
- This renderer does not unblock identity-dependent work and does not replace generative video providers.

## 8. Next action

Read exact-head CI for the latest PR commit, resolve any new independent review findings, obtain a clean Codex re-review, then merge only after all review threads are resolved. After merge, run mainline CI and update the candidate status to production-verified only if the merged commit passes.
