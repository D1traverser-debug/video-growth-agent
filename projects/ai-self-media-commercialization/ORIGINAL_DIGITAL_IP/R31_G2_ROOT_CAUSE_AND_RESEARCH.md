# R31｜G2失败根因复核与角色设计／提示词方法修正

日期：2026-11-12
状态：研究复核完成；新角色合同与新生图提示词尚未批准；禁止继续随机生图。

## 0. 结论
上一轮没有按项目流程执行。失败不只是模型“没听提示词”，而是品牌概念、角色结构、图像任务类型、提示词编译、工具追溯和验收同时存在问题。R31不批准任何新头像，不把失败图升级为参考。

## 1. 项目治理根因
1. 主聊天未完整恢复根目录最新有效文件，错误地只读取头像工作室子目录中的部分文件，遗漏根目录需求与验收、任务分配、独立美术评审等权威文件。
2. 新聊天启动规则要求第一条回复只做研究和设计，不调用图像生成；上一轮却直接输出生成提示词并触发图像生成。
3. 任务责任基线规定当前主聊天是唯一 accountable owner，新聊天仅为可选生产工位；上一轮将提示词编译和出图责任转交给用户。
4. 先前根因记录已经指出：不能把未通过 G2 的形象拿去做 G3 表情精修；不能以“普通美型男性+配饰”冒充原创 IP。上一轮重复了同类错误。

## 2. 第一张候选的根因
- 画面技术完成度不错：方形、单人、构图完整，墨线／哑光色块／纸纹统一。
- 身份失败：头脸仍是高度常见的年轻动漫男性模板；脸部骨架、五官关系、发型、服装均没有足够原创结构。
- Split Current 被落实为夸张斜刘海分叉；它是普通发型上的装饰性变化，不是独立角色机制。
- 头部近正面、肩部近对称，缺少清晰动作意图、line of action、counterpose 和可读负空间。
- “敏锐、独立、温暖、机敏”等抽象人格词没有转译成可见面部动作和身体行为。
- 手绘墨线和纸纹只说明画法统一，不会自动生成原创身份。
- 标准 overshirt + T-shirt 组合没有角色专属性。

## 3. 第二张内部生成图的根因
- 仍然是胸像肖像任务，不是真正的低保真角色视觉开发。
- 虽写“短发、无刘海”，实际输出仍重复长而夸张的刘海，说明负面限制不足以压过模型的常见肖像先验。
- “回身观察者”把身份押在一次性姿态上。姿态能表达当前情绪，却不是稳定身份锚点；换角度、换表情、做数字人时无法承担身份。
- “胸像男性＋编辑插画＋深色头发＋自然微笑＋素色衬衫”仍是高频肖像组合，模型继续回归普通男性模板。
- 图像工具未提供可审计的最终逐字 prompt／seed／参考图回执；不能声称这是完全可复现的空白画布实验。输出相似可能来自模型先验，也可能受上下文影响，现有证据不能区分。

## 4. 提示词工程根因
1. 把品牌人格、角色设计、画风、材质、配色、服装、构图和禁止项一次性塞进长 prompt。
2. 用大量“不要普通动漫男／不要帅哥／不要某风格”替代正向可见几何定义。
3. 使用“原创、独特、有吸引力、成熟、聪明”等模型无法直接绘制的抽象目标。
4. 把头部轮廓等同于头发轮廓，未定义脸部骨架和头肩大形的差异化机制。
5. 没有先生成黑色剪影／低保真构造稿；直接要求墨线、纸纹、配色完成度肖像，模型自然输出成熟的常见头像模板。
6. 单张出图无法比较结构路线；没有预注册变量、基准组和失败判据。
7. 第二轮只改变姿态和头发描述，却没有改变任务表示方式、概念钩子和结构机制，因此不是有效根因修复。

## 5. 定向研究与可执行规则

### 角色设计
- Toon Boom Character Design 01：先研究人物背景、文化、年龄、职业、性格、好坏特质、情绪角色和制作媒介，再开始造型。
- Toon Boom Character Design 02：先决定比例和形状；用曲线与直线组合、有不对称性的 forceful shapes；先做 rough drafts，再做多版本 silhouette 测试；选择结构后才清稿、上色和细化。
- Toon Boom Character Design 03：角色通过后才制作 turnaround、action poses、expression sheets。
- Animation Mentor：姿态审查看 meaning、silhouette、line of action、contrapposto；避免身体对称、轴线平行画框、动作藏在轮廓内部；用负空间建立可读性。
- Appeal 不是“画得漂亮”，而是清晰设计秩序加有目的的变化／惊喜；精致、写实或复杂不等于有吸引力。
- Microsoft 动画原则：姿态和身体动作避免镜像对称；角色性格可由简单形状、姿势和习惯传达。

### 图像提示词
- Google DeepMind Nano Banana 提示指南：明确 subject、pose/action、composition、style；先说清楚可见对象和动作，再逐步迭代。
- OpenAI 图像生成提示指南：具体描述形状、材料、构图、人物身体范围、视线和动作；调试从干净基线开始，每次只改一个变量。
- 本项目提示词必须先定义可见结构，不先定义“高级风格”。负面约束只守边界，不承担创造角色的任务。

## 6. 修正后的 G2 流程
1. G0 恢复品牌目标与所有有效纠错，锁定跨英文 X／中文财经科技／未来视频的长期人格张力。
2. G1 研究完成后形成“观察→设计规则→本项目应用→反例”的证据链。
3. G2 写出三个真正不同的构造逻辑；差异必须体现在头颅／脸部／颈肩结构、形状语法、情绪机制和媒介，而不是同一个帅哥换发型。
4. 每条路线先制作黑白大形或低保真剪影；先检查纯黑剪影、正负形、头肩关系、48/96px 可读性。
5. 反方审查：去掉颜色、材质、服装、配饰后是否仍然独特；换表情／视角后是否保留身份。
6. 选中结构方向后才进入 G3 表情；G4 确定媒介、颜色、服装；G5 编译模型专用 prompt；G6 生成；G7 独立验收。
7. 结构失败返回 G2，不做美化、超分或局部修补。

## 7. 本轮明确撤销
- 撤销 Split-Current Observer 作为已选方向的资格。
- 撤销 Turnback Observer 作为主身份方向的资格；姿态不能独自承担稳定身份。
- 用户上传的第一张候选与本聊天生成的第二张图均为失败证据，不得作为身份或风格参考。
- 撤销上一轮“20/30”作为完整验收分数的有效性：未完成独立黑色剪影和实际 48px 检查，不能把该数字当作严格 QA。
- 不批准任何头像、角色锚点、G3、G4、G5 或 G6。

## 8. 下一步
当前主聊天继续负责。先完成三条真正不同的 G2 角色构造路线比较及反方审查，再选一条写成可画的造型合同。未完成该合同前不再启动新图像生成。

## 9. 参考资料
- Toon Boom, Character Design 01: https://helpcentre.toonboom.com/hc/en-ca/articles/57133659664531-Character-Design-01-Researching-the-character
- Toon Boom, Character Design 02: https://helpcentre.toonboom.com/hc/en-ca/articles/57134336047123-Character-Design-02-Creating-the-design
- Toon Boom, Character Design 03: https://helpcentre.toonboom.com/hc/en-ca/articles/57134612631955-Character-Design-03-Finalizing-the-character-sheets
- Animation Mentor, Building Appealing Character Poses: https://www.animationmentor.com/blog/tutorial-building-appealing-character-poses-for-animation/
- Animation Mentor, Visual Development Principles of Design: https://www.animationmentor.com/workshops/visual-development-principles-of-design/
- Animation Mentor, Appeal: https://www.animationmentor.com/blog/appeal-the-12-basic-principles-of-animation/
- Microsoft Learn, Animation Principles: https://learn.microsoft.com/en-us/windows/win32/lwef/animation-principles
- Google DeepMind, Gemini Image prompt guide: https://deepmind.google/models/gemini-image/prompt-guide/
- Google, Nano Banana Pro prompting tips: https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- OpenAI Cookbook, GPT Image Generation Prompting Guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
