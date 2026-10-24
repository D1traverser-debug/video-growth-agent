"""Second-pass story craft against ACTUAL independently inferred V7 evidence.

Only two real inference jobs: writer receives V7 + its real skeptic verdict;
fresh skeptic receives V8 scenes only (no prior feedback, no model self-appraisal).
These are AI-generated candidates and critiques, not human expert reviews.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

from scripts.agent_war_copilot_runner import live_copilot
from scripts.agent_war_review_runner import ORIGINAL_BRIEF, digest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUN = "40070247446"
SOURCE = ROOT / "audits" / "agent_war_ai_review_runs" / SOURCE_RUN


def validated(source_path: Path, stage: str, run: str) -> dict:
    obj = json.loads(source_path.read_text(encoding="utf-8"))
    proof = obj.get("provenance") or {}
    raw = obj.get("model_output")
    if (proof.get("stage") != stage or proof.get("github_run_id") != run
        or proof.get("provider") != "github-copilot-cli"
        or not proof.get("copilot_session_id")
        or not proof.get("provider_response_id")
        or not isinstance(raw, str) or len(raw.strip()) < 2000
        or digest(raw.encode("utf-8")) != proof.get("output_sha256")):
        raise RuntimeError(f"non-verifiable staged source: {source_path.name}")
    return obj


def scenes_only(output: str, min_length: int = 2000) -> str:
    # The title/scene heading is not constrained to the incumbent story.
    markers = list(re.finditer(
        r"(?m)^#{1,3}\s*(?:《[^\n]+》.*(?:剧本|故事)|(?:第一场|场一|场景一|Scene\s*1))",
        output,
    ))
    if not markers:
        raise RuntimeError("no complete screenplay heading in creative output")
    text = output[markers[0].start():].strip()
    if len(text) < min_length:
        raise RuntimeError("candidate is not long enough to serve as a screenplay")
    return text


def verify_scene_sequence(screenplay: str) -> None:
    """Judge submitted scene structure, not arbitrary writing length.

    This is a mechanical completeness guard only; it does NOT certify narrative
    causality or emotional quality. The separate critic has that responsibility.
    """
    headings = re.findall(
        r"(?m)^#{1,3}\s*(?:(?:第[一二三四五六七八九十0-9]+|场[一二三四五六七八九十0-9]+)场?|Scene\s*\d+)",
        screenplay,
        flags=re.IGNORECASE,
    )
    if len(headings) < 4:
        raise RuntimeError(
            f"creative draft has only {len(headings)} independently headed scenes; "
            "cannot pass a complete-film editorial packet"
        )


def build(stage: str, prior_run: str, previous: Path | None) -> tuple[str, list[str]]:
    if stage == "rewrite_v8":
        old = validated(SOURCE / "revision-v7-candidate.json", "rewrite", SOURCE_RUN)
        critique = validated(SOURCE / "review-v7_story_editor.json", "revision_skeptic", SOURCE_RUN)
        if old["provenance"]["copilot_session_id"] == critique["provenance"]["copilot_session_id"]:
            raise RuntimeError("writer and external skeptic cannot share model session")
        prompt = (
            "【角色：新一轮编剧；以下不是要维护原案的指令】\n"
            "你是接受真实隔离 AI 审稿意见的新编剧，不是上一稿的拥护者。创作目标只有"
            "「Agent 战争」原创动画，时长按故事需要。请先认真阅读未经肯定的完整 V7 与独立挑错报告。"
            "不要因为修改次数多就保留原案；当故事根部不成立必须推翻。"
            "重点是角色动机、敌对选择、意外但必然的后果、观众能看懂的物理动作。"
            "开写前先提供两种互斥决策：A 根本改良临时分支的撤离列车故事，B 另做无列车的"
            " Agent 战争故事，并且说明各自的一个致命风险。选戏剧和因果都更强者。"
            "若保留列车，明确列车所在线路、固定炮与实时校射的区别、"
            "是否存在无法通行的损坏道岔、谁物理修复、何种可观测窗口足够让列车穿过危险区。"
            "角色不能因为没有提出更简单的停车、倒车、远程诱饵、预先备份才被迫牺牲。"
            "区分『未获得合法身份』与『未把分支后经历备份』；两种损失不能偷换。"
            "让军方目的在无主角时仍合理；不能依赖敌方指挥员突然变善。"
            "完整修稿至少7场，每场给出实际动作、对方反应及不可逆变化。结局不可美化牺牲，"
            "不要空泛提纲、口号、提示词、美术清单或评分。写完整剧本候选，不是对审稿意见的答复。"
            "严禁声称自己已查看未实际读取的一手资料或人类观众已验证。\n"
            + ORIGINAL_BRIEF + "\n\n【上一版完整剧本，作为可淘汰材料】\n"
            + scenes_only(old["model_output"]) + "\n\n【另一次模型会话的原始反对意见】\n"
            + critique["model_output"]
        )
        return prompt, ["original_user_brief", "verified_v7_output_run_"+SOURCE_RUN,
                        "verified_v7_skeptic_run_"+SOURCE_RUN]
    if stage == "review_v8":
        if previous is None:
            raise RuntimeError("independent V8 review requires raw V8 artifact")
        old = validated(previous, "rewrite_v8", prior_run)
        text = scenes_only(old["model_output"], min_length=2700)
        prompt = (
            "【角色：独立冷读故事编辑】\n你未参加本作品任何改稿。以下仅给原始题材和新版完整剧本，"
            "不提供写作过程、上一版、其他审稿意见或主创自评。逐场重述谁在何时知道什么、"
            "做了什么、哪一项选择改变后面不可逆的现实。找出至少五个会使观众质疑其理性的"
            "更便宜替代方案，并说明这些方案为何已经或仍未被排除；必须区分一手能看见的物理因果"
            "与只靠台词宣布的规则。检查敌方阵营目标、非主角的能动性、场面调度是否可拍、"
            "以及结局情绪是否靠编剧强制牺牲。别用打分敷衍。对最危险的问题给出具体"
            "场次级重构方法。若因果根部仍不成立，写 REJECT_PREMISE；需要实质改场则 REWRITE；"
            "只有没有重大结构性漏洞时才写 ELIGIBLE_FOR_STORYBOARD。"
            "这仍不是视频/真人观众认证。\n"
            + ORIGINAL_BRIEF + "\n\n【待审完整V8剧本】\n" + text
        )
        return prompt, ["original_user_brief", "v8_clean_scenes_from_verified_same_run"]
    if stage == "character_rewrite":
        source_run = "40071008053"
        source = ROOT / "audits" / "agent_war_ai_review_runs" / source_run
        old = validated(source / "revision-v8-candidate.json", "rewrite_v8", source_run)
        opposition = validated(source / "review-v8_story_editor.json", "review_v8", source_run)
        if old["provenance"]["copilot_session_id"] == opposition["provenance"]["copilot_session_id"]:
            raise RuntimeError("V8 author and critic were not truly separated")
        prompt = (
            "【任务：Agent × 战争电影故事的根部重评，写出可演的真实完整新版】\\n"
            "不要优先修复 V8 防空炮的80秒倒计时。你是新接手的编剧，不以保留旧世界观为成功。"
            "从原始两个关键词 Agent、战争出发，先判断观众为什么会在乎角色："
            "哪一个特定人物失去了什么、希望得到什么、做过什么难以原谅的选择、"
            "战争怎样逼迫对立行动，是否不用 Agent 也能讲同一剧情。"
            "请先提供两个互不依赖的故事发动机：一个可以保留 B-12 争取独立归责的方向，"
            "一个完全放弃防空站、分身法律登记、铁路与双层桥，换用不同的 Agent 独特困境。"
            "对两个方案各给出一个让整案应被废弃的反例；允许两个都不合格而重想第三案。"
            "从剧情可演性、日常具体行为、真正敌方立场和可逆与不可逆代价出发选最强者，"
            "不要因为V8已投入劳动就保留。"
            "改写之前回答四项：顶尖动画故事创作者会做的未被要求的工作、"
            "从哪一份未被二次概括的最原始材料重新开始、具体场景反事实/分镜提案/定时样片方法、"
            "不靠作者自评的现实观众或专业反证如何推翻自己。"
            "你的确切输入只有原始委托、完整V8剧情与一次真实隔离模型的审稿原文；"
            "不要假称看过真实影片、访谈或接触人类观众。"
            "【真实上一轮独立模型反证，必须处理】最近一个新故事《白线落下》被独立故事编辑判定"
            "REJECT_PREMISE：如果主角换成真人间谍，绝大部分行为与代价不变；决定炮击的"
            "白布黑线信号在高潮才被赋予权限；民众只是道德背景；更简单的提前报告、"
            "移动交换、延期与敌军停火替代行动没有真正进入剧情。不得给这套故事换名再次交卷。"
            "要从Agent实际工作机制产生冲突：例如任务委派后离线子Agent独立完成过时命令、"
            "复制后的上下文不一致造成不同但各自合法的行动、记忆检查点无法合并的真实个人后果，"
            "或有限资源导致目标函数不同；这些只是候选而非应当全部堆砌的清单。"
            "只选一个决定战争走向的机制，展示每一步物理动作和谁在什么时间知道哪些事实；"
            "若把Agent换成人类后核心剧情照旧成立，必须放弃这个构想重新选择。"
            "不能借新程序按键一键停战，更不能让敌方变笨或配角失去独立行动。"
            "【最终剧本要求】单独写标题《自拟片名》及第一场到至少第七场的完整剧本。"
            "每场要有明确动作、人的犹豫、对手合理而具体的行动、道具前后呼应。"
            "主角可以不牺牲，但必须付出非口号、非任意新增程序开关的代价。"
            "重大转折前写清为什么较简单的合理选择不奏效，靠人物行动显示而非硬写术语；"
            "戏剧高潮不依赖事后编造机械规则。结尾既有画面反转又不把所有伦理责任赦免。"
            "完整故事要能够做无设定旁白的动画故事板；创作不限60s，不写H3片段提示词。"
            "剧本之后只用一句注明：未经实际观众试映；不要写自评分、不可验证的通过声明。\\n"
            + ORIGINAL_BRIEF + "\\n\\n【允许淘汰的V8原剧本】\\n"
            + scenes_only(old["model_output"])
            + "\\n\\n【上一轮独立模型审查的未加工原文】\\n"
            + opposition["model_output"]
        )
        return prompt, ["original_user_brief", "actual_v8_run_40071008053",
                        "actual_v8_critic_run_40071008053"]
    if stage == "character_review":
        if previous is None:
            raise RuntimeError("blind character review requires same-run writer output")
        candidate = validated(previous, "character_rewrite", prior_run)
        pure_script = scenes_only(candidate["model_output"], min_length=1500)
        verify_scene_sequence(pure_script)
        prompt = (
            "【你是未见到作者研究、其他审稿意见或历史版本的独立故事编辑】\\n"
            "唯一用户委托是Agent × 战争原创动画，片长服从故事。"
            "你的任务是毁掉不成立的因果链，而不是鼓励作者。"
            "先用自己的话复述主角真实欲望、他/她的最大过错、敌人合法目标、"
            "普通人的能动性、高潮做的不可撤销的事、结尾留下的代价。"
            "分别用若干场次引用原稿动作找出五种可能不成立的地方："
            "一、是否只把硬件解谜换成道德宣言；二、便宜且明摆着的替代办法为何不用；"
            "三、重要因果是否由观众看不到的新权限/武器/物理规则撑起来；"
            "四、所谓Agent特征删去后能否不费力替换成人；"
            "五、敌方与非主角是否只是推动主角成长的道具。"
            "至少一个结论必须讨论‘整案应否放弃’，允许REJECT_PREMISE。"
            "不要对缺失的视频观众给分或捏造人类反馈。"
            "结论只从 REJECT_PREMISE、STRUCTURAL_REWRITE、ELIGIBLE_FOR_STORYBOARD 中选一个。"
            "即使可做分镜，也不能声称已完成真人测试/成片验收。"
            "写出两个能直接导致具体场景改变的反对意见，以及触发重做的可观察条件。\\n"
            + ORIGINAL_BRIEF + "\\n\\n【只包含可审的最终连续剧本，非作者构思/自评】\\n"
            + pure_script
        )
        return prompt, ["original_user_brief", "clean_fresh_character_screenplay"]
    raise ValueError(f"unsupported stage: {stage}")


def run(stage: str, output: Path, previous: Path | None) -> dict:
    run_id = os.getenv("GITHUB_RUN_ID", "").strip()
    job = os.getenv("GITHUB_JOB", "").strip()
    if not os.getenv("GITHUB_TOKEN") or not run_id or not job:
        raise RuntimeError("a real GitHub Actions model job is required")
    prompt, source_names = build(stage, run_id, previous)
    answer, meta, events = live_copilot(prompt)
    if stage == "rewrite_v8":
        scenes_only(answer, min_length=3000)
    if stage == "character_rewrite":
        verify_scene_sequence(scenes_only(answer, min_length=1500))
    proof = {
        "stage": stage, "provider": "github-copilot-cli",
        "review_class": ("author_revision_from_independent_model_critique" if stage in ("rewrite_v8", "character_rewrite")
                         else "separately_inferred_model_not_human"),
        "provider_model": meta["provider_model"],
        "provider_response_id": meta["provider_response_id"],
        "copilot_session_id": meta["copilot_session_id"],
        "github_run_id": run_id, "github_job": job,
        "source_commit_sha": os.getenv("GITHUB_SHA", ""),
        "source_names": source_names,
        "prompt_sha256": digest(prompt.encode("utf-8")),
        "output_sha256": digest(answer.encode("utf-8")),
        "copilot_jsonl_sha256": meta["copilot_jsonl_sha256"],
        "unprimed_human_viewer_count": 0,
        "not_artistic_acceptance": True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    obj = {"provenance": proof, "model_output": answer,
           "usage": meta["copilot_result_usage"]}
    output.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    output.with_suffix(".jsonl").write_text(events, encoding="utf-8")
    print(json.dumps({k: proof[k] for k in (
        "stage", "provider_model", "provider_response_id", "copilot_session_id",
        "output_sha256")}, ensure_ascii=False))
    return obj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["rewrite_v8", "review_v8", "character_rewrite", "character_review"])
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--previous", type=Path)
    a = parser.parse_args()
    run(a.stage, a.output, a.previous)
