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
        source_run = "40073765790"
        source = ROOT / "audits" / "agent_war_ai_review_runs" / source_run
        old = validated(source / "story-core-candidate.json", "character_rewrite", source_run)
        opposition = validated(source / "review-story_core_editor.json", "character_review", source_run)
        if old["provenance"]["copilot_session_id"] == opposition["provenance"]["copilot_session_id"]:
            raise RuntimeError("earlier creative author and independent critic share a model session")
        prompt = (
            "【任务：Agent × 战争原创短篇电影；对旧案拥有直接废弃权，写真实完整电影剧情】\n"
            "原始要求仅 Agent 与战争，故事优先，不固定60秒、不按生成视频单次时长切剧情。"
            "你将看到已被另一个模型审稿否决的《两次点名》与该审稿原文。"
            "评审说它本质仍是两个人拿不同名单、被切断通信；教师苏禾做了决定，"
            "Agent 诺只是辅助；孩子传话、信使、铃声等便宜办法没试；"
            "离线副实例明明能感知眼前人却被强行写成认错目标，主机断线后又知道位置。"
            "这些不是表面文字问题。你有权完全弃案，甚至不必保留学校、复制、名单。"
            "【开写之前必须做的事实工作】先从原始题材提炼一个"
            "人类无法原样替代、且可用两个可拍的物理动作展示的 Agent 专属战争机制；"
            "对这个机制给出操作和身份/时间/信息边界及必然代价，不能突然添加总控密钥。"
            "分别以敌对指挥官、被救平民、受委派 Agent 的立场说出各自真实利益，"
            "再做反事实：把 Agent 换成两名人类同事；发短信/找信使；撤退/等待；"
            "预备份、复制更多实例、取消任务是否轻易就能解决？如果是，必须换机制。"
            "必须在场景里让真正合理的替代行动被尝试或因已经建立的约束不可行，"
            "不能用作者口号‘不可能’顶替演出的事实。"
            "列出两个不同故事发动机，明确废弃其中一个的最强证据。"
            "【主剧本】之后另起独立小标题《自拟片名》，写至少七场"
            "有具体人物表演、对手行动、物理地图、冲突升级、前置道具和结尾余波的连续故事。"
            "必须让 Agent 而非人类监督者做一个会给具体他人带来不可逆损害的自主选择，"
            "让对手不是为了推动主角成长而存在；不求所有人认错，不制造先验友好敌人。"
            "尽量以可视镜头和行动而不是投影UI术语交代机制，故事核心即使无旁白仍能成立。"
            "不能用读者看不见的幕后信息或最后一分钟新协议救场。"
            "时长由表演决定；不要虚构真人试映。"
            "最后只写‘未经真实观众或动态故事板验证’，不写自我评分或外部验收合格。\n"
            + ORIGINAL_BRIEF + "\n\n【已否决的上一完整剧本：可全部放弃】\n"
            + scenes_only(old["model_output"])
            + "\n\n【另一 Copilot 会话对该稿的完整独立审稿反证】\n"
            + opposition["model_output"]
        )
        return prompt, ["original_user_brief", "actual_character_story_run_40073765790",
                        "actual_character_story_critic_run_40073765790"]
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
            "同时作严格替换试验：把主人公换成两名人类工作人员并给他们相同通信设备，"
            "若战场行动依旧相同，则直接判为结构性失败；把人类替代方案逐场指出。"
            "重大剧情转折必须引用已经出现的可观察动作或前置物理规则作为证据，"
            "不接受最后一刻的授权键与‘程序就是这样规定的’。"
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
