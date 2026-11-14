# Video Local Programmatic Graphics Renderer — Candidate Audit

Date: 2026-11-14 (Asia/Shanghai)
Status: CANDIDATE_PR_OPEN__NOT_MERGED
PR: https://github.com/D1traverser-debug/video-growth-agent/pull/33
Candidate branch: `feat/video-local-programmatic-graphics-renderer-20261114`
Latest verified renderer and graph-transaction code head at this audit update: `a73a1f7ea1f4e6b3d314bfc213fd8e8f0efdb91d`

## 1. User/business problem

The Video production OS had deterministic media QA and shot/timeline governance, but no local executable visual-generation path for ordinary information shots. External AI image/video/audio routes remained declared-only without a trusted provider executor. As a result, a title card, metric, quote or explanatory chart could be planned but not actually rendered by the current runtime without a third-party generator.

## 2. Root causes and independent review defects

1. Missing local deterministic executor for non-character information graphics.
2. FFmpeg drawtext default expansion could interpret literal percent/expansion sequences in source-backed values.
3. MediaGraph candidate registration previously trusted asset/version identity without checking that the actual promoted source digest matched the ShotContract reference binding.
4. Text wrapping counted characters instead of measuring glyphs; long metrics could clip while technical QA still passed.
5. Chart rows used a fixed minimum vertical gap independent of point count and measured label height; a two-line sixth label could extend below a 640×640 frame while width-only layout evidence still passed.
6. The first candidate metadata update added an open evolution item without binding it to `current_problem_refs`; repository hygiene audit correctly failed closed. The reference was added and exact-head system audit now passes.
7. The graph validator checked only that a SHOT context existed, not that its actual parent chain resolved to the `ShotContract.sequence_id`; this allowed a candidate to claim the wrong sequence while registering under the graph's actual sequence.
8. FFmpeg rendered directly to the final destination after a non-atomic existence check; on a concurrent failure, cleanup could unlink a file published by another invocation. The renderer now writes to an invocation-private temp directory on the destination filesystem and atomically publishes with a no-replace hard link; cleanup only removes its own temp directory.
9. The CLI loaded a MediaGraph before rendering and saved that stale snapshot afterward. A concurrent reviewer/renderer update could be lost, and reference-promotion checks could be stale. MediaGraphStore now combines a cross-process file lock with SHA-256 optimistic revision checks; the CLI reloads, revalidates and registers inside a post-render transaction.
10. Receipt sidecars were written with `write_text()` after an earlier existence check. A competing writer could create a receipt path or symlink during rendering and have its file or target truncated. Receipt publication now uses a private temporary file and atomic no-replace hard-link publication.
11. The receipt hashed the mutable source font after rendering, while FFmpeg used a staged copy and layout measurement used the source path. A source-font replacement/removal could make the receipt inaccurate or fail after MP4 publication. Layout, rendering and digest now use one staged font snapshot.

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
- Chart rows are dynamically allocated between measured top/bottom boundaries. Label, value and bar heights/positions are checked against each row; two-line labels shrink to the available row height and impossible layouts fail before rendering.
- FFmpeg drawtext uses `expansion=none` for literal text fidelity.
- Source references require exact promoted MediaGraph versions and digest equality with the ShotContract; CLI preflight and graph registration use the same validator.
- The SHOT context's parent chain must resolve to the exact `ShotContract.sequence_id`, allowing only SHOT → SEQUENCE or SHOT → SCENE → SEQUENCE; both CLI preflight and registration use this shared fail-closed check.
- Output is a silent visual preview, registered only as `CANDIDATE`.
- No paid API, network access, AI footage/audio, observed real/product-truth claim, IPOS identity rendering, promotion or release authority.
- Existing output files and receipt sidecars are never overwritten. MP4 and JSON receipt are written privately and published by atomic no-replace hard links; conflicts and symlinks fail closed without following or deleting competing paths.
- The selected font is copied once into the invocation-private directory before measurement; layout, FFmpeg and `font_sha256` all use the same staged bytes.
- MediaGraph read/modify/write uses a cross-process lock and optimistic content revision. The CLI does a short locked reload → revalidate exact ancestry/promoted source versions/digests → register → atomic save after rendering. Stale snapshots fail rather than overwriting concurrent updates.

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
- concurrent reviewer update preservation and stale-snapshot rejection;
- concurrent source revocation blocks candidate registration;
- receipt-path symlink race preserves the symlink target;
- source font deletion/replacement after staging preserves exact font digest provenance;
- no-overwrite and receipt-tampering rejection.

Exact renderer/graph-transaction code head `a73a1f7ea1f4e6b3d314bfc213fd8e8f0efdb91d` passed both CI runs `43597564240` and `43597558421`: 262 tests, repository system hygiene audit, and installed CLI smoke all passed. Nine Codex inline findings are resolved, covering literal text expansion, exact source digests, horizontal metric fit, vertical chart-row fit, Sequence ancestry, concurrent MP4 ownership, concurrent MediaGraph lost updates, receipt symlink/overwrite races and staged-font provenance. Fresh full code and security reviews have been requested against this head; final approval is still pending.

## 7. Governance

- Video Growth Agent only.
- CAOS source repository/code/PRs are untouched.
- IPOS authority and canon remain unchanged.
- PR #33 is open and not merged. Candidate code is not production capability until exact-head CI, independent review and merge/mainline verification pass.
- This renderer does not unblock identity-dependent work and does not replace generative video providers.

## 8. Next action

Await and inspect the fresh full Codex code and security reviews against the verified head. If they introduce no findings, update the candidate handoff records, merge PR #33, then run mainline CI. Do not mark production-verified until the merged commit passes mainline CI.
