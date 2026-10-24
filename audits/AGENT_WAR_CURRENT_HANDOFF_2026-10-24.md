# Agent × 战争电影项目 — 当前总纲、事实状态与新对话无缝继承

> **工程续接补充（2026-10-24）**：本次已在 Draft PR #23 提交 `a7bfb8e1fd5d51e9422b68a78b5668a29f551020`，新增原始 brief 双路编剧／隔离审稿／比较的可选工作流；CI #40080535290 已 294 passed，未执行新的 Copilot 生成，旧剧本最后判定仍为 `REJECT_PREMISE`。详见 `audits/PROMPT_CRAFT_PR23_CHECKPOINT_2026-10-24.md` 最新顶部记录。新模型任务仅在核实额度费用并获授权后明确触发，不能把静态代码 PASS 当作故事质量 PASS。

> **此页是当前事实入口，不是新创作方案。** 本文只记录已证实的用户委托、真实执行、创作淘汰结果和继续工作条件。旧故事、提示词、过期运行记录都不能覆盖本文与 `audits/EVOLUTION_INDEX.json` 中的最新事实。未来继续前，请核实 GitHub PR 分支 HEAD 与最近一次 Actions，绝不能凭聊天里的最后一句推测“已经完成”。

## 1. 正确任务归属与不可漂移总纲

- 用户原始创意 brief：**「Agent」「战争」**；要求创造一部有独特世界、有情节、有真正人物冲突的原创动画电影。用户明确表示：**故事质量第一，不局限 60 秒，不考虑生成额度是否划算**。不允许把生产模型一次生成 10 秒当作电影的节拍。
- 本任务挂在现有 **AI 视频自媒体商业化／Video Growth Agent** 项目下，不单独再造多 Agent 操作系统。沿用真实的 `writer`、`story_editor`、`director`、`storyboard_artist`、`editor`、`production_methodologist`，以及现成的 Github Actions Copilot CLI 执行器与证据门禁。**不要让用户每次重新写专业提示词、手动粘贴给其他 AI。**
- 用户认可的工作方式不是不停加大方案，而是**更深的创造与反驳**：顶尖从业者未被要求却会做什么；从未经 AI 消化的原始材料开始；具体方法/工具；与作者、用户无关的检验证据。这四问写进岗位，但答案必须变成可辨认的人物行为、战时利益、场面调度和可反驳的成片观察。
- 影视创作边界：世界观不是独立的设定百科；镜头前可见的规则、行动和后果决定故事。每名重要角色（含敌对军方和平民）有自己要争取的东西、可执行选择及实际损失。**Agent 的自主委派、任务执行、记忆/上下文分叉、受限权限等特性必须真正改变战争后果**；若换成两个人类工作人员、遥控机器人或普通预测软件可无差别替换主角，就不得以“Agent 独特电影”宣称通过。
- 既有媒体工作习惯：成片暂以 **9:16、1080×1920、24fps、I2V优先、单镜头5–6秒、声音后期统一** 作为短视频账号的可用默认基线；但此处当前电影概念开发曾采用 **16:9 横向 H3**，两者属于不同交付语境。**本片正式分辨率/画幅仍未被用户重新确认，不得为了迎合旧默认而擅自改剧本**。先把故事做好，之后依据发行渠道与视觉语法确定交付。
- H1 原创数字 IP 角色／三视图、其他媒体素材与原有 Program 工作流**均不得被本故事回合擅自覆盖**。本项目故事还**未获用户正式批准**。

## 2. 技术与创作权威：以后从这些确切位置恢复

- GitHub：`D1traverser-debug/video-growth-agent`
- 当前工作分支：`refactor/prompt-director-core-20261023`
- **Draft PR #23**：`https://github.com/D1traverser-debug/video-growth-agent/pull/23`，未合并到 `main`。
- 全局项目入口：`audits/EVOLUTION_INDEX.json`（`current_candidate`、`current_resume_ref`、`story_review_assurance`）
- 本轮累计操作记录：`audits/PROMPT_CRAFT_PR23_CHECKPOINT_2026-10-24.md`
- **本文件**：`audits/AGENT_WAR_CURRENT_HANDOFF_2026-10-24.md`（新对话先读）。
- 现有角色职责：`video_growth_agent/data/team.md`；审稿信任门禁：`video_growth_agent/data/executors.json`、`video_growth_agent/execution_attestation.py`。
- 已经在 GitHub Actions 实际成功运行的模型入口：`scripts/agent_war_copilot_runner.py` 和 `scripts/agent_war_v8_followup.py`；工作流：`.github/workflows/agent-war-story-room.yml`、`.github/workflows/agent-war-v8-followup.yml`。**GitHub Models 旧 API 已停用**，不要退回它。Copilot CLI 的分离任务是真实模型调用，仍不是互不相关的真人专家。
- 存档并发冲突已有恢复证据：`.github/workflows/agent-war-recover-archived-review.yml`，恢复 run `40076202379` **SUCCESS**；后续 `agent-war-v8-followup.yml` 改成 rebase + 安全 fast-forward 重试，不可 force push。

## 3. 已真实执行的创作与独立 AI 否决，不得反复重走同一死路

| 顺序 | 实际候选 | 真实来源/审稿判断 | 核心被否决的原因 |
|---|---|---|---|
| 早期 | `第17号漏洞`、`不可竣工` 等 | 旧 `audits/AGENT_WAR_*.md` | 世界观/人物因果不够强，没有被用户批准 |
| V6 | `《断面》` | `projects/ai-self-media-commercialization/creative_candidates/agent_war/DUANMIAN_SCREENPLAY_V6_2026-10-24.md` | 主创自己通过多岗位模拟后仍存在机械桥梁高潮、廉价伦理结论等问题；不是独立人类审查 |
| V7 | `《临时编号》` | `audits/agent_war_ai_review_runs/40070247446/` | 铁路线路受损却仍通过；仅中断一次炮火校射不等于安全；分支法律身份与记忆备份被混淆；复审要求 REWRITE |
| V8 | `《不在册》` | `audits/agent_war_ai_review_runs/40071008053/` | 80秒防空重启和几乎立刻开火互相矛盾；战术简单替代方案没排除；审核 REWRITE |
| 其后 | `《白线落下》` | `40072307965` 真实 Copilot 人物故事回合 | 实际是普通人类间谍故事换 Agent 名称；审稿 REJECT_PREMISE |
| 其后 | `《两次点名》` | `40073765790` | 两名人类拿不同名单即可重演多数情节，教师才是人物选择者；审稿 STRUCTURAL_REWRITE |
| 其后 | `《西泄口》` | [run 40075431401](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/40075431401)，原始结果后由 `40076202379` 恢复写回 | 小机器人进窄闸只是机械身体特技，换成人或遥控机基本成立；闸轮单次操作物理法则未铺垫；**REJECT_PREMISE** |
| 其后 | `《余线》` | [run 40076350289](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/40076350289) | 六组无人机预测仍是辅助工具，发射器直接断开、清道岔等更便宜操作未排除；审稿 **STRUCTURAL_REWRITE** |
| **当前最新** | **`《白灯不等人》`** | [run 40077050738](https://github.com/D1traverser-debug/video-growth-agent/actions/runs/40077050738)，**全部三项作业 SUCCESS：创作、另一会话的审稿、存档** | 铁路调度 Agent `织机` 操作三处联锁、将敌方轨道车导入岔线致平民伊娃重伤；普通人类信号员+现场铁路工可以复现动作；没有证明为何不能停车/封锁/等待，Agent 缺乏自身欲望；**独立 AI 结论 `REJECT_PREMISE`** |

**当前最原始、可复核的最新证据**（必须先读全文，不要靠本表代替）：
- 完整新稿：`audits/agent_war_ai_review_runs/40077050738/STORY_CORE_CANDIDATE_UNAPPROVED.md`
- 完整独立 AI 复审：`audits/agent_war_ai_review_runs/40077050738/STORY_CORE_INDEPENDENT_AI_CRITIQUE.md`
- 同路径下 `story-core-candidate.json`、`review-story_core_editor.json` 与对应 `.jsonl`：记录真实 `github_run_id`、不同 `github_job` 和 `copilot_session_id`、`provider_response_id` 及 SHA256。
- 对应软件 CI：run `40077054091`，测试 job 和 prompt-contract job **SUCCESS**；实测 **289 passed**。**这只证实软件，不证实电影质量。**
- 最新模型执行：两个 Copilot 会话，**同一工具商的不同会话**，不等于独立的人类编剧或不同模型家族之间的真正多元审查。真实人类无背景观众数 `0`；可播放动态故事板 `0`；视频生成/正式影片 `0`。

## 4. 最近一次明确且可证伪的创作结论

《白灯不等人》审稿者明确表示：`REJECT_PREMISE`。不建议通过加“信号员进不去”“电机只动一次”“Agent必须开锁”之类的任意新限制继续修该铁路故事。敌方洛恩有可理解目的，但这不能替代主角 `织机` 对目标的主动坚持、冲突和后果。平民伊娃受伤后需要真正作为人物行动，而非仅用于令 Agent 背负罪责。**已有故事目前都未达到用户期待；不把版本号递增解释为质量累积。**

失败范式已经重复：`危险设施 + Agent替人操作 + 两难牺牲 + AI写审稿报告`。下一轮必须**先改变创作起点**，不应继续依赖同一机关类型：
- 从原始双关键词与真实战争中的多方动机出发，允许写出与铁路、桥、冷却液、洪水、防空炮、战时点名完全无关的不同故事。
- 首先展示某一个 Agent 自主委派/执行导致 **无法及时取消、无法以两位普通人原样替代的责任纠葛**，且它对人物真正有个人代价。提出至少一个真的会让故事弃案的反证。
- 不为抽象口号或便于审稿增加电影中看不见的协议、后台判断、权限开关。争议必须能被导演从可拍的动作与相互阻挠中展示出来。
- 分工仍由现有 `writer` 提出不同的、戏剧发动机；`story_editor` 在独立上下文中只读完整新稿与用户原始 brief，执行低成本替代行动、人物能动性、战争现实利益与 Agent 必需性反证；导演在可看故事板阶段验证具体空间、因果、表演与信息量。
- **没有故事板和无背景观众实际复述前，不宣称“故事质量PASS”。** 不要自动合并 PR、不修改 H1 创作状态，不未经明确允许调用付费视频生成额度。

## 5. 新对话直接执行的 SOP（不用重复询问用户）

**启动指令**：用户可以只说「继承 Agent 战争」「继续视频」「继续」，助手应当：
1. 读取 `audits/EVOLUTION_INDEX.json` 的 `current_resume_ref` 和此 handoff，核实 Github Draft PR #23 当前 HEAD、最新 GitHub Actions 完成/失败情况。尊重之后可能产生的更高版本结果；**本文件是快照，不得覆盖未来的新事实**。
2. **先读最新原始完整剧本与完整原始复审**（上节两路径），区分创作事实、独立 AI 运行凭证、人类观众缺失的证据。
3. 不向用户发送“请你复制给 Codex 的提示词”；直接让**已有 GitHub Agent / Actions**执行一个真正不同的编剧挑战、隔离审稿，使用已证明有效的 Copilot CLI，不再建立冗余 Agent。
4. **对失败保持失败**：新结果不成立则主动改变故事引擎，避免重复有限手段“硬件设备操控牺牲”模板；从人物利益、相互对抗的物理动作和 Agent 决策内核继续，保存原始反证，不靠更长剧本掩盖原因。
5. 每次新实际成果在回复之前至少更新 `audits/EVOLUTION_INDEX.json` + `audits/PROMPT_CRAFT_PR23_CHECKPOINT_2026-10-24.md`，将事实证据链接和阻塞、下一步骤保存；勿凭 chat memory 接续。PR 一直保持 Draft，用户未批准不能 merge。
6. 如果将来需要独立**人类**观众证据，先制作真实可播放的粗故事板并做无背景复述，不可由同一 AI 模拟观众后写 `PASS`。

## 6. 当前清晰的完成与未完成状态

**已完成（工程层）**：使用 Copilot CLI 实际运行作者、独立 AI 审稿和存档；修复过模型 API 停用、不同会话凭证、归档并发、Python 语法与过期测试引用；最新 run `40077050738` 的 writer/editor/archive 3 个 jobs 全成功，最新验证 CI 289 passed。

**明确未完成（创作层）**：世界观与首片方案未正式被用户接受；最后新稿 `《白灯不等人》` 被真实 AI 审稿 `REJECT_PREMISE`；未形成真正可看的完整故事板、正式短片或真人冷观众证据。

**继续工作必须解决的问题**：在不扩建系统、不让用户重复操作、无 60 秒硬框的前提下，由现有岗位找到一个 **Agent 的自主行动使战争人物之间的利益冲突发生不可替代改变** 的原创故事，不靠编造不便替代的机械装置来过审。
