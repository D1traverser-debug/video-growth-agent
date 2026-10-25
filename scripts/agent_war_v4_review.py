"""Run a ONE-session blind Story Editor review of original Agent War V4.

A triggered Action is an explicitly requested optional Copilot text inference;
ordinary pushes, tests and importing this module never spend model calls.
The output is separate AI critique, NOT an artistic or human-viewer acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from scripts.agent_war_cleanroom import team_method
from scripts.agent_war_copilot_runner import live_copilot

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("projects/ai-self-media-commercialization/creative_candidates/agent_war/DI_QI_CI_MEI_KAI_HUO_110S_V4_2026-10-24.md")
REQUEST = Path("audits/agent_war_single_reviews/REQUEST.json")
START = "## 人物与物理空间（一个地点）"
END = "## 原始要求及不同候选的取舍"
V6_STORY = Path("projects/ai-self-media-commercialization/creative_candidates/agent_war/JIN_RI_SHENG_LI_112S_V6_DIRECTOR_TREATMENT_2026-10-25.md")
V6_REQUEST = Path("audits/agent_war_single_reviews/REQUEST_V6.json")
LESSON01 = Path("skills/video-growth-agent/references/storycraft-research-2026-10-25/LESSON01_SCENE_DRAFT_2026-10-25.md")


def review_spec(req: dict) -> tuple[Path, str, str, str]:
    if req.get("purpose") == "blind_single_story_editor_v4" and req.get("story_path") == str(STORY):
        return STORY, START, END, "v4_story_editor"
    if req.get("purpose") == "blind_single_story_editor_v6" and req.get("story_path") == str(V6_STORY):
        return V6_STORY, "## 三位主角各自知道什么", "## 本稿真正要让观众完成的推断", "v6_story_editor"
    if req.get("purpose") == "blind_writer_scene_lesson01" and req.get("story_path") == str(LESSON01):
        return LESSON01, "## [BLIND_SCENE_START]", "## [BLIND_SCENE_END]", "writer_scene_lesson01"
    raise RuntimeError("missing exact authorized story/script version")
BRIEF = (
    "用户原始影视题材「Agent」×「战争」。必须以Agent为核心，"
    "影片必须真正有内容力、故事力、明确表达；暂定严格低于两分钟。"
    "文本与制作分离，未来视频生成可采用5或10秒单元。"
    "此处只审查故事，不决定画风或模型。"
)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source(request_path: Path = ROOT / REQUEST) -> tuple[str, str]:
    req = json.loads(request_path.read_text(encoding="utf-8"))
    if req.get("max_model_calls") != 1:
        raise RuntimeError("missing exact authorized single-session review request")
    story_path, start_tag, end_tag, _stage = review_spec(req)
    text = (ROOT / story_path).read_text(encoding="utf-8")
    requested_sha256 = req.get("full_script_sha256")
    requested_git_blob = req.get("script_git_blob_sha")
    if requested_sha256 is not None:
        matches_source = sha(text) == requested_sha256
    elif requested_git_blob is not None:
        git_blob = subprocess.check_output(
            ["git", "hash-object", str(ROOT / story_path)],
            cwd=ROOT, text=True,
        ).strip()
        matches_source = git_blob == requested_git_blob
    else:
        matches_source = False
    if not matches_source:
        raise RuntimeError("source changed since authorized review request")
    a, b = text.find(start_tag), text.find(end_tag)
    minimum = 350 if _stage == "writer_scene_lesson01" else 1800
    if a < 0 or b <= a or b - a < minimum:
        raise RuntimeError("cannot isolate complete scenes from author framing")
    story = text[a:b].strip()
    for forbidden in ("## 原始要求及不同候选", "## 在审稿前最危险", "## 作者自己必须提出的最严重反例", "## 本稿真正要让观众完成的推断"):
        if forbidden in story:
            raise RuntimeError("author pre-critique leaked to blind reviewer")
    return story, sha(story)


def build(request_path: Path = ROOT / REQUEST) -> tuple[str, dict]:
    story, script_hash = source(request_path)
    req = json.loads(request_path.read_text(encoding="utf-8"))
    story_path, _start, _end, stage = review_spec(req)
    method, method_ref = team_method("Story Editor")
    if stage == "writer_scene_lesson01":
        prompt = (
            "【当前独立角色：短场编剧训练审核者】\n" + method +
            "\n\n【任务】独立冷读以下一场45–50秒的虚构战时日常小场戏。"
            "目的不是审查Agent技术、政治观念或宣称有真人观看，而是检验学徒是否学会场景动作因果。"
            "不要读取或假定任何作者自评、研究笔记、过去剧本或更改建议；此处只给待检的场次。"
            "先按实际场面重述：谁在追求什么、发生哪一个行动选择、结尾情况如何真的变化。"
            "找至少四个实质性反证，特别是可直接问司机/登车记录、女人为什么请求盖章、"
            "凭证究竟能证明谁在何时做过什么、她的书写及结尾是否改变搜索行动、"
            "45秒可否演完。严厉区分缺乏证据和刻意留白；不要用临时不合理规定救戏，"
            "也不要逼它必须幽默、悲壮、Agent主体或完整短片。"
            "输出最强结构性漏洞、可实行的场次修订建议；结论限定"
            "SCENE_REJECT_OR_RETHINK / SCENE_STRUCTURAL_REWRITE / SCENE_PRACTICE_VIABLE。"
            "最后一种也不表示故事好、真人观众满意或整部影片可制作。"
            "\n\n【唯一场景文本，不含作者意见】\n" + story
        )
        return prompt, {"input_story_only_sha256": script_hash,
                        "full_script_sha256": sha((ROOT / story_path).read_text(encoding="utf-8")),
                        "role_ref": method_ref}
    prompt = (
        "【本次隔离执行的岗位规范；真实角色技能原文】\n" + method +
        "\n\n【原始创作委托】\n" + BRIEF +
        "\n\n【给真正独立故事编辑的具体任务】\n"
        "你不能阅读作者的主题宣言、备选方案、修稿记录和自我审查。"
        "先用观众语言复述实际发生的故事，而非作者声称的价值。"
        "独立检验每一次交锋如何导致下一步，对手是否有零成本赢法；"
        "对于人物与对手的每一个决策，验证是否存在更便宜的解法；"
        "特别检验换一个摄像角度、伪造画面、撤走旗杆、固定脚本、"
        "两位人类摄影师替换Agent能否不改变结局；"
        "检查兰姨为什么要撑棚、独立Agent是否反复自主观察与改变真实世界，"
        "红蓝双方是否各自明智、影片是否确有有趣的图像转义，"
        "112秒内观众是否能清楚理解动作因果与战时背景。"
        "给出最强的至少三个结构性反例、具体场次引用和下一轮修改优先级。"
        "结论只能用 REJECT_PREMISE、STRUCTURAL_REWRITE 或 ELIGIBLE_FOR_STORYBOARD；"
        "不因作者认真或影片题材而通融。不伪装成人类观众，也不为稿件自判通过。"
        "\n\n【仅供审查的原创故事与时码（不含作者自评）】\n" + story
    )
    return prompt, {"input_story_only_sha256": script_hash,
                    "full_script_sha256": sha((ROOT / story_path).read_text(encoding="utf-8")),
                    "role_ref": method_ref}


def verify(result_path: Path, request_path: Path = ROOT / REQUEST) -> dict:
    obj = json.loads(result_path.read_text(encoding="utf-8"))
    proof, body = obj.get("provenance") or {}, obj.get("model_output", "")
    _, facts = build(request_path)
    req = json.loads(request_path.read_text(encoding="utf-8"))
    _story, _start, _end, stage = review_spec(req)
    if (proof.get("stage") != stage or
            proof.get("input_story_only_sha256") != facts["input_story_only_sha256"] or
            proof.get("full_script_sha256") != facts["full_script_sha256"] or
            proof.get("provider") != "github-copilot-cli" or
            not proof.get("github_job") or not proof.get("github_run_id") or
            not proof.get("copilot_session_id") or
            not proof.get("provider_response_id") or
            proof.get("artistic_acceptance") is not False or
            proof.get("external_human_viewer_count") != 0 or
            not isinstance(body, str) or len(body.strip()) < 500 or
            proof.get("output_sha256") != sha(body)):
        raise RuntimeError("invalid provenance or incomplete actual blind critique")
    return obj


def execute(out: Path, request: Path = ROOT / REQUEST) -> None:
    if not (os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_RUN_ID") and os.getenv("GITHUB_JOB")):
        raise RuntimeError("separately executed Story Editor requires a real GitHub Actions session")
    prompt, facts = build(request)
    req = json.loads(request.read_text(encoding="utf-8"))
    _story, _start, _end, stage = review_spec(req)
    answer, meta, events = live_copilot(prompt)
    if len(answer.strip()) < 500:
        raise RuntimeError("incomplete independent narrative review")
    obj = {
        "provenance": {
            "stage": stage, "provider": "github-copilot-cli",
            "github_run_id": os.environ["GITHUB_RUN_ID"],
            "github_job": os.environ["GITHUB_JOB"],
            "source_commit_sha": os.getenv("GITHUB_SHA"),
            "provider_model": meta["provider_model"],
            "provider_response_id": meta["provider_response_id"],
            "copilot_session_id": meta["copilot_session_id"],
            "copilot_jsonl_sha256": meta["copilot_jsonl_sha256"],
            "prompt_sha256": sha(prompt),
            "output_sha256": sha(answer),
            **facts,
            "artistic_acceptance": False,
            "external_human_viewer_count": 0,
        },
        "model_output": answer, "usage": meta["copilot_result_usage"],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out.with_suffix(".jsonl").write_text(events, encoding="utf-8")
    verify(out, request)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--request", type=Path, default=ROOT / REQUEST)
    args = parser.parse_args()
    execute(args.out, args.request)
