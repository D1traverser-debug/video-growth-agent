# Video Growth Agent｜Continuity Handoff

- task_id: `video-growth:main`
- display_name_zh: **AI视频涨粉与商业化**
- task_class: USER
- status: ACTIVE
- resume_visibility: DEFAULT
- owner: `VIDEO_GROWTH_AGENT`
- domain: `VIDEO_GROWTH`
- contract: Universal Continuity `v3.3`
- runtime: Video Growth Agent `0.4.0`
- manifest: `continuity/tasks/video-growth-main/TASK_MANIFEST.json`
- checkpoint: `continuity/tasks/video-growth-main/CHECKPOINT.json`

## Goal
以尽量零新增成本/极低成本建立 AI 视频增长与商业化内容机器：涨粉 → IP/信任 → 商单/广告/合作 → 可持续商业化。

## Current execution truth
Pilot 002《AI正在抢走“打开 App”这一步》的 Release V4 已完成技术/内容制作，但用户明确判定**整体质量仍不够**。因此此前 `RELEASE READY / WOULD PUBLISH` 判断已失效，V4 只能作为历史失败/对照样本，禁止直接进入发布或 PERFORMANCE。

当前真实 stage：`LOOKDEV`，状态 `ACTIVE`。

## Current learning/rebuild batch
必须主动蒸馏并验证：
- DramaClaw
- Pippit
- Toonflow workflow
- MiniMax H3
- Utopai Studios / PAI
- 用户提供的知乎 ComfyUI + MiniMax H3 教程
- 助手自行找到的优秀 AI filmmaking / motion-design 作品、源码、工作流和社区经验

目标不是堆工具名，而是区分：
1. 可直接采用的生产工具；
2. 应蒸馏进 Skill / Technique Library 的制作方法；
3. 只适合某些镜头的生成引擎；
4. 不值得采用或成本/质量不合适的方案。

## Next action
完成这轮外部学习和 benchmark 重建，把验证有效的方法持久化进 GitHub Skill / Technique Library / benchmark policy；随后重新制作 Pilot 002 的 LOOKDEV / Motion，并且只有在新的绝对质量 Gate 通过后才生成新的 release candidate。

## Historical evidence
被否决的 V4：
`/Video Growth Agent/Pilot 002/Release V4/Pilot002_FINAL_RELEASE_V4.mp4`

SHA-256：`eec364e8530067dbc87a08a9ccbf2dd6e6e8a5ab32fb87f648c794a4000628eb`

保留它是为了学习失败原因，不得恢复为发布 authority。

Full executable recovery state is in `CHECKPOINT.json`, not this prose handoff.
