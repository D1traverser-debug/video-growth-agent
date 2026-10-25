# 故事创作训练｜固定学习闭环的第一轮实际执行（2026-10-25）

**严格区分**：这是 Writer 的基本功训练，不是 Agent×战争新剧本；也不是新流程。权威方法是 `skills/video-growth-agent/references/storycraft-research-2026-10-25/LEARNING_AND_CREATIVE_PRACTICE_PROTOCOL.md`；影片生产仍来自 `video_growth_agent/data/workflow.json` 的兼容阶段及 `UAOS_SKILL.md` 的现役视频产物关系。

## 原始任务与本轮缺陷
用户要我继续按固定方法**实际学习、写、批判、重写，并保证跨对话继承**。以前错误做法是每次产出新剧本/新框架，但没有一轮真实可追溯的独立反馈与效果比较。
**本次唯一训练缺陷**：旧21秒公告栏练习为了“有人物冲突”发明一颗图钉、湿名单和用水壶烘纸，普通喊话/找夹子就能替代；人物行动未造成值得留下的场景变化。

## ①–③直接学习的原始材料（未冒称课程已报名）
- John August `How to write a scene`，2007，https://johnaugust.com/2007/write-scene 。本轮直接核读11项步骤中“不可删的动作”“去掉多余角色”“三个开场”“作者在脑内排演”“写初稿”；不是从助手旧摘要重述。
- John August `Rewriting based on other people's notes`，2004，https://johnaugust.com/2004/rewriting-based-on-other-peoples-notes 。核读“重写是拆行为/场次，不是润色；找到批评背后的失败而不是照单执行意见”。
- Sundance Collab `Crafting Your Short Film Screenplay`，官方**课程纲要**，https://collab.sundance.org/catalog/Crafting-Your-Short-Film-Screenplay/December-2026 。核读Week4 objectives, obstacles & given circumstances，以及Week5 intention vs tactics和Week8 rewrites；**没有进入付费课程或取得证书**。
- Pixar/Khan Academy `The Art of Storytelling`，https://www.khanacademy.org/computing/pixar/storytelling 。核读Storyboarding/Pitching/Feedback章节目录、公开Activity 1 Pitching中粗分镜→对他人实际讲述→取得反馈的要求；**未请真人听演/见真人看片**。
- 战时寻亲知识：https://missingpersons.icrc.org/families 和 https://missingpersons.icrc.org/search-process 。核读“fate与whereabouts差异”“最后已知旅程需要核实”，并把战争小镇、票号17、四号车、机构流程全部声明**创作虚构**，没有将人道机构报告当作虚构车站的正式政策。

## ④第一份可看的完整短场
`skills/video-growth-agent/references/storycraft-research-2026-10-25/LESSON01_SCENE_DRAFT_2026-10-25.md`。剧本《到过》D1约45–50秒。女人拿17号领票凭证，登记员拒盖未经核实的“已登车”章；结尾女人仍没有可实行下一步。
**场景入口学习**：John August的方法实际用于三种开场比较，选择从票据和照片入场；旧图钉/干纸逻辑全部舍弃。

## ⑤–⑥一轮真实独立评审与实质重写
- 一次单独Copilot模型实际执行 GitHub Actions #`40175894907`，`audits/agent_war_single_reviews/40175894907/story_editor.json` 与相邻raw JSONL；来源哈希和 reviewer session/response 提供于JSON，模型输入**仅为D1场次+现有Story Editor专业岗位方法+待检任务**，没有作者研究/自评。**SCENE_STRUCTURAL_REWRITE**，premiumRequests=1，真人观众0。
- 独立审稿指出：为什么不问司机/查别的名单，印章为什么变成入站凭据，领取票据与人身份不匹配，写字/存根没有让女人真正开始寻找，“接着找”口号无实际行动。
- **实际新稿 D2**：`skills/video-growth-agent/references/storycraft-research-2026-10-25/LESSON01_SCENE_REVISION_D2_2026-10-25.md`，剧本约52秒。完全删除“不合理盖章需求”；把三栏“领票/预配四号车/登车未核”分别实体化；登记员确实联系车辆调度员，由下一站核实登车；女人主动留下联系方式与明确追索桌位。事件改变是“虚假的确定性→可操作的后续核对”。
- **D2没有经真人/视听实验**，有可能因母亲留唯一票据、过度便利的调度规则、结尾虚假悬念而失败。这些是**先于D2审稿作者自己找到的风险**，不能被先给评审。

## ⑥ D2的隔离复审（目前发起，执行结果应从后续记录覆盖）
本次对新剧本请求 **`audits/agent_war_single_reviews/REQUEST.json`**：`purpose=blind_writer_scene_lesson01_revision`，`max_model_calls=1`，剧本Git blob source pin。`scripts/agent_war_v4_review.py` 沿用原来的隔离Copilot reviewer工具、`.github/workflows/agent-war-single-story-review.yml` 沿用旧的单次外部审稿Action；独立模型只读纯D2场次，完全看不到D1、D1结果、作者自评。**这是待审查的证据点，不是审稿已通过。**

## ⑦学习结果怎么保留与未来怎么继承
本轮确实从“一看情节好像有意思”推进为：针对特定廉价反例换掉造成问题的**人物目的、实际动作、证据种类与结果**，不去编造禁令挽救最喜欢的图钉。然而这只能证明**行为方式改变**，不证明作品有趣/深刻/可观看，未来不能宣称艺术PASS。D2审稿出来后须补本文件再确认下一轮最有价值的技能缺口。

## 稳定恢复点
下个对话的权威入口是 `audits/EVOLUTION_INDEX.json` 的 `current_resume_ref` 和当前PR#23分支；本文件是本次 Writer **训练证据**，不是另一个全局控制器。恢复顺序：先读PR head+主分支状态→当前EVOLUTION_INDEX→本文件→D2源码+真实复审结果→依据它的实际反证继续。不要重新调换为“必须幽默/必须反战”，也不要重启V1–V6视频或编写V7。
