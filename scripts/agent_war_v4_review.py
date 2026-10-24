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
from pathlib import Path

from scripts.agent_war_cleanroom import team_method
from scripts.agent_war_copilot_runner import live_copilot

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("projects/ai-self-media-commercialization/creative_candidates/agent_war/DI_QI_CI_MEI_KAI_HUO_110S_V4_2026-10-24.md")
REQUEST = Path("audits/agent_war_single_reviews/REQUEST.json")
START = "## 人物与物理空间（一个地点）"
END = "## 原始要求及不同候选的取舍"
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
    if (req.get("max_model_calls") != 1 or req.get("story_path") != str(STORY)
            or req.get("purpose") != "blind_single_story_editor_v4"):
        raise RuntimeError("missing exact authorized single-session V4 review request")
    text = (ROOT / STORY).read_text(encoding="utf-8")
    if sha(text) != req.get("full_script_sha256"):
        raise RuntimeError("source changed since authorized review request")
    a, b = text.find(START), text.find(END)
    if a < 0 or b <= a or b - a < 1800:
        raise RuntimeError("cannot isolate complete scenes from author framing")
    story = text[a:b].strip()
    for forbidden in ("## 原始要求及不同候选", "## 在审稿前最危险"):
        if forbidden in story:
            raise RuntimeError("author pre-critique leaked to blind reviewer")
    return story, sha(story)


def build(request_path: Path = ROOT / REQUEST) -> tuple[str, dict]:
    story, script_hash = source(request_path)
    method, method_ref = team_method("Story Editor")
    prompt = (
        "【本次隔离执行的岗位规范；真实角色技能原文】\n" + method +
        "\n\n【原始创作委托】\n" + BRIEF +
        "\n\n【给真正独立故事编辑的具体任务】\n"
        "你不能阅读作者的主题宣言、备选方案、修稿记录和自我审查。"
        "先用观众语言复述实际发生的故事，而非作者声称的价值。"
        "独立检验每一次交锋如何导致下一步，对手是否有零成本赢法；"
        "为什么两套系统不抢先开火、是否只是预写触发器，两个具备同权人类"
        "是否可用类似步骤重现高潮，两个孩子是否主动改变结果，"
        "重要声画节奏在110秒内是否成立。"
        "给出最强的至少三个结构性反例、具体场次引用和下一轮修改优先级。"
        "结论只能用 REJECT_PREMISE、STRUCTURAL_REWRITE 或 ELIGIBLE_FOR_STORYBOARD；"
        "不因作者认真或影片题材而通融。不伪装成人类观众，也不为稿件自判通过。"
        "\n\n【仅供审查的V4原创故事与时码（不含作者自评）】\n" + story
    )
    return prompt, {"input_story_only_sha256": script_hash,
                    "full_script_sha256": sha((ROOT / STORY).read_text(encoding="utf-8")),
                    "role_ref": method_ref}


def verify(result_path: Path, request_path: Path = ROOT / REQUEST) -> dict:
    obj = json.loads(result_path.read_text(encoding="utf-8"))
    proof, body = obj.get("provenance") or {}, obj.get("model_output", "")
    _, facts = build(request_path)
    if (proof.get("stage") != "v4_story_editor" or
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
    answer, meta, events = live_copilot(prompt)
    if len(answer.strip()) < 500:
        raise RuntimeError("incomplete independent narrative review")
    obj = {
        "provenance": {
            "stage": "v4_story_editor", "provider": "github-copilot-cli",
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
    args = parser.parse_args()
    execute(args.out)
