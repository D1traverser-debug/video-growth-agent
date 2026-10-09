# Video Growth Agent｜Continuity Handoff

- task_id: `video-growth:main`
- display_name_zh: **AI视频涨粉与商业化**
- task_class: USER
- status: WAITING
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
Pilot 002《AI正在抢走“打开 App”这一步》已经完成最终 Release V4。内部 RELEASE Gate 为 PASS，当前权威成片为：

`/Video Growth Agent/Pilot 002/Release V4/Pilot002_FINAL_RELEASE_V4.mp4`

SHA-256：`eec364e8530067dbc87a08a9ccbf2dd6e6e8a5ab32fb87f648c794a4000628eb`

当前真实 stage：`RELEASE`。外部平台尚未发布，因此任务处于 `WAITING`，不得虚构进入 `PERFORMANCE`。

## Next action
等待用户将 Release V4 发布到所选目标平台。出现真实 live post ID/URL 后：
1. 验证发布对象对应当前 V4；
2. 进入 `PERFORMANCE`；
3. 获取平台真实可用指标并建立 `performance_receipt`；
4. 再进入 `LEARN`，把有效结论沉淀回 Technique Library / Skill。

不要重新执行已经完成的 Pilot 002 研究、脚本、LOOKDEV、Motion、声音或最终媒体 QA，除非权威成片/发布包发生变化。

## Compatibility migration
旧 handoff 保留了合法 task identity 和 owner，但缺 v3.3 元数据且 stage 已严重过期，因此本次判定为 `MIGRATABLE`。迁移只保留仍有效的用户要求、研究、证据与 artifacts；旧 `POSITIONING_BASELINE_READY` 不得作为恢复 stage 重放。

## Recovery evidence
- GitHub business authority: `D1traverser-debug/video-growth-agent@main`
- Pilot 002 Notion recovery page: `https://app.notion.com/p/3f4d54f04b1781fb8178eb3af79a8b40`
- Release V4 Library folder: `/Video Growth Agent/Pilot 002/Release V4/`

Full executable recovery state is in `CHECKPOINT.json`, not this prose handoff.
