"""Independent original Agent/War film trials, with provenance-bound blind reviews.

This is an opt-in Copilot text-model runner; never executed by an ordinary CI push.
No result is artistic approval, a viewer test, or a generated video.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from scripts.agent_war_copilot_runner import live_copilot
from scripts.agent_war_v8_followup import scenes_only, verify_scene_sequence

BRIEF = (
    "原创动画电影的题材关键词是「Agent」与「战争」。故事、人物与戏剧质量优先；"
    "片长由叙事决定，不固定为60秒，也不受单次视频生成时长约束。"
    "任何世界、设定、故事、人物和画幅在正式审查前都不是已批准的。"
)
WRITER = (
    "【岗位：独立编剧／Writer】你只收到上面的原始委托和本次写作要求，"
    "没有既有故事、任何其他作者结论或历史审稿。不要猜测先前发生过什么。"
    "先构思三个在角色欲望、战争冲突和不可逆后果方面真正不同的故事发动机，"
    "用实际行动、反方利益和更简单替代选项分别检验；明确淘汰两案的最强理由。"
    "从剩余一案独立创作完整、连续、可拍摄的原创动画剧本：至少四场，"
    "以“### 第一场”这类独立场次标题标记，具象呈现每个重要人物主动争取的东西。"
    "Agent 必须做出真正自主、可被观众察觉且影响战争后果的决定，"
    "而非仅替人类操作已有装置。敌方、平民与委托者都可以拒绝、博弈和改变局势。"
    "以真实场面行动建立因果和约束，不靠末刻追加不能验证的设定，不预设牺牲式结局。"
    "不要写视频模型提示词、美术风格清单或自我验收 PASS。"
    "如果无法写成好故事就如实说明未通过，不虚构真人观众。"
)
REVIEWER = (
    "【岗位：独立故事编辑／Story Editor】你仅收到原始委托与一份不含作者说明的完整剧本。"
    "你不知道创作历史、其他竞争作品、作者的取舍说明、先前审稿或本次另一个剧本。"
    "先独立重建每位角色的真实欲望、每场的可见行动、选择和不可逆后果；"
    "严格测试 Agent 与两名具备相同资源的人类工作人员、遥控机器人、常规预测工具的可替代性。"
    "逐场提出至少五个可执行的更廉价替代行动，区分已被实际排除和作者仅声称不可行；"
    "检查敌人和平民有无主动选择、战争利益有无真实性、高潮的物理因果与尾声的责任。"
    "指出一个真正可能否决整案的根本性反例，不为篇幅或作者努力而妥协。"
    "最终只输出 REJECT_PREMISE、STRUCTURAL_REWRITE 或 ELIGIBLE_FOR_STORYBOARD 之一，"
    "并附具体场次事实；最后一种也不等于真人、故事板或电影质量通过。"
)
WRITER_A_TREATMENT = (
    "【创作角度 A：人物关系驱动】从一个有具体亲密关系、不能同时得到的愿望、"
    "以及战争中必须自己承担后果的自主选择起笔。Agent 的长期委托、"
    "对具体人的信任或背叛必须造成剧情变化；不要以设备故障直接制造两难。"
    "所有角色必须能以可见行动反对主角。可以改变设定和文体，"
    "这个角度是创作探索，不是指定已有故事。"
)
WRITER_B_TREATMENT = (
    "【创作角度 B：战争制度和对抗驱动】从战争中的两方真实集体目标、"
    "资源分配、相互误判、战术反制以及多名自主 Agent 的委托冲突起笔。"
    "找出没有 AI 自主代理关系便不会成立的战术或政治结果。"
    "允许艰难但不必必然牺牲，不以单一机械装置强迫选择。"
    "可以改变设定和文体，这个角度是创作探索，不是指定已有故事。"
)

ADJUDICATOR = (
    "【岗位：Story Editor 总编审／两案对比】下面是同一原始委托下，两次彼此隔离的"
    "真实 AI 编剧输出和各自隔离 AI 审稿原文。对照两条故事发动机、角色能动性、"
    "Agent 非替代性、对手行动、可拍性、故事张力与审稿反证。不要因为审稿写了"
    " ELIGIBLE_FOR_STORYBOARD 就自动通过。允许两个都否决；如有值得进一步验证的候选，"
    "明确需要何种下一步可看分镜和无背景观众复述观察。"
    "返回明确的比较结果与证据引用；不宣称真人评审或正式批准。"
)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


TEAM_METHOD_SOURCE = Path(__file__).resolve().parents[1] / "video_growth_agent/data/team.md"


def team_method(role: str) -> tuple[str, str]:
    """Read current Video owner role craft instructions, not previous film plots.

    Copilot is invoked with --no-custom-instructions and no repository tool
    access: only exact material explicitly embedded in the prompt is usable.
    """
    raw = TEAM_METHOD_SOURCE.read_text(encoding="utf-8")
    marker = "## " + role + "\n"
    start = raw.find(marker)
    if start < 0:
        raise RuntimeError(f"missing owner role method: {role}")
    end = raw.find("\n## ", start + len(marker))
    body = raw[start:(len(raw) if end < 0 else end)].strip()
    if len(body) < 300:
        raise RuntimeError(f"owner role method unexpectedly incomplete: {role}")
    return body, "video_growth_agent/data/team.md#" + role.replace(" ", "_") + "@sha256:" + sha(body)


def role_context(*roles: str) -> tuple[str, list[str]]:
    blocks, sources = [], []
    for role in roles:
        method, provenance = team_method(role)
        blocks.append(method)
        sources.append(provenance)
    return "\n\n".join(blocks), sources


def verified(path: Path, stage: str, run_id: str) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    proof, body = obj.get("provenance") or {}, obj.get("model_output")
    if (proof.get("stage") != stage or proof.get("github_run_id") != run_id
        or proof.get("provider") != "github-copilot-cli"
        or not proof.get("github_job") or not proof.get("copilot_session_id")
        or not proof.get("provider_response_id") or not isinstance(body, str)
        or sha(body) != proof.get("output_sha256")):
        raise RuntimeError(f"unverifiable stage: {stage}")
    if stage.startswith("writer_"):
        verify_scene_sequence(scenes_only(body, min_length=1500))
    elif len(body.strip()) < 250:
        raise RuntimeError(f"insufficient completed review: {stage}")
    return obj


def distinct(*receipts: dict) -> None:
    proofs = [r["provenance"] for r in receipts]
    for field in ("github_job", "copilot_session_id", "provider_response_id"):
        vals = [p[field] for p in proofs]
        if len(set(vals)) != len(vals):
            raise RuntimeError(f"independent roles share {field}")


def build(stage: str, run_id: str, previous: Path | None = None,
          evidence_dir: Path | None = None) -> tuple[str, list[str]]:
    if stage in ("writer_a", "writer_b"):
        method, refs = role_context("Writer")
        treatment = WRITER_A_TREATMENT if stage == "writer_a" else WRITER_B_TREATMENT
        lane = "RELATIONSHIP_FIRST" if stage == "writer_a" else "WAR_INSTITUTIONS_FIRST"
        return (BRIEF + "\n\n【当前项目已核验的岗位方法，不是旧故事素材】\n" +
                method + "\n\n" + WRITER + "\n\n" + treatment), ["original_user_brief", *refs, "craft_lane:" + lane]
    if stage in ("review_a", "review_b"):
        if previous is None:
            raise RuntimeError("blind review requires exact writer artifact")
        author = verified(previous, "writer_" + stage[-1], run_id)
        # Author's notes, treatment comparison and self-appraisal are omitted.
        script = scenes_only(author["model_output"], min_length=1500)
        method, refs = role_context("Story Editor")
        return (BRIEF + "\n\n【当前项目已核验的岗位方法，不是作者观点】\n" +
                method + "\n\n" + REVIEWER + "\n\n【完整剧本，供独立冷读】\n" + script), [sha(script), *refs]
    if stage == "adjudicate":
        if evidence_dir is None:
            raise RuntimeError("comparison requires four verified receipts")
        w_a = verified(evidence_dir / "writer_a.json", "writer_a", run_id)
        w_b = verified(evidence_dir / "writer_b.json", "writer_b", run_id)
        r_a = verified(evidence_dir / "review_a.json", "review_a", run_id)
        r_b = verified(evidence_dir / "review_b.json", "review_b", run_id)
        distinct(w_a, w_b, r_a, r_b)
        for label, w, r in (("a", w_a, r_a), ("b", w_b, r_b)):
            script = scenes_only(w["model_output"], min_length=1500)
            if r["provenance"].get("input_script_sha256") != sha(script):
                raise RuntimeError(f"review_{label} not bound to writer_{label} script")
        # This provenance is checked against actual structured receipts above;
        # make it observable to the judge without leaking the two writers'
        # preselection notes into their individual blind reviews.
        attest = [{"stage": obj["provenance"]["stage"],
                   "run": obj["provenance"]["github_run_id"],
                   "job": obj["provenance"]["github_job"],
                   "copilot_session_id": obj["provenance"]["copilot_session_id"],
                   "model": obj["provenance"].get("provider_model", "unspecified"),
                   "output_sha256": obj["provenance"]["output_sha256"]}
                  for obj in (w_a, w_b, r_a, r_b)]
        attest_text = json.dumps(attest, ensure_ascii=False, indent=2)
        packet = ""
        for label, w, r in (("A", w_a, r_a), ("B", w_b, r_b)):
            packet += (f"\n\n【候选{label}完整剧本】\n" + scenes_only(w["model_output"], min_length=1500)
                       + f"\n\n【候选{label}独立AI复审】\n" + r["model_output"])
        method, refs = role_context("Story Editor", "Director")
        return (BRIEF + "\n\n【现有专业岗位方法】\n" + method +
                "\n\n【隔离AI执行凭证：已由本地原始记录和哈希检验；"
                "不是人类独立审稿或艺术验收】\n" + attest_text +
                "\n\n" + ADJUDICATOR + packet), [sha(packet), sha(attest_text), *refs]
    raise ValueError(f"unknown stage {stage}")


def execute(stage: str, out: Path, previous: Path | None, evidence_dir: Path | None) -> dict:
    run_id, job = os.environ.get("GITHUB_RUN_ID", ""), os.environ.get("GITHUB_JOB", "")
    if not (os.environ.get("GITHUB_TOKEN") and run_id and job):
        raise RuntimeError("requires a real Actions Copilot job; no local silent paid execution")
    prompt, refs = build(stage, run_id, previous, evidence_dir)
    answer, meta, events = live_copilot(prompt)
    if stage.startswith("writer_"):
        verify_scene_sequence(scenes_only(answer, min_length=1500))
    elif len(answer.strip()) < 250:
        raise RuntimeError("completed critique is too short")
    digest = None
    if stage.startswith("review_"):
        writer = verified(previous, "writer_" + stage[-1], run_id)
        digest = sha(scenes_only(writer["model_output"], min_length=1500))
        if meta["copilot_session_id"] == writer["provenance"]["copilot_session_id"]:
            raise RuntimeError("author and blind reviewer share session")
    obj = {
        "provenance": {
            "stage": stage, "provider": "github-copilot-cli",
            "provider_model": meta["provider_model"],
            "provider_response_id": meta["provider_response_id"],
            "copilot_session_id": meta["copilot_session_id"],
            "github_run_id": run_id, "github_job": job,
            "source_commit_sha": os.environ.get("GITHUB_SHA", ""),
            "source_refs": refs, "prompt_sha256": sha(prompt),
            "input_script_sha256": digest, "output_sha256": sha(answer),
            "copilot_jsonl_sha256": meta["copilot_jsonl_sha256"],
            "external_human_viewer_count": 0, "artistic_acceptance": False,
        },
        "model_output": answer, "usage": meta["copilot_result_usage"],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out.with_suffix(".jsonl").write_text(events, encoding="utf-8")
    return obj


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--stage", required=True,
                   choices=["writer_a", "writer_b", "review_a", "review_b", "adjudicate"])
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--previous", type=Path)
    p.add_argument("--evidence-dir", type=Path)
    args = p.parse_args()
    execute(args.stage, args.out, args.previous, args.evidence_dir)
