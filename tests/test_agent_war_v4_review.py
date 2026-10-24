import hashlib
import json

import pytest

from scripts import agent_war_v4_review as m


def request(tmp_path):
    data = {
        "purpose": "blind_single_story_editor_v4",
        "max_model_calls": 1,
        "story_path": str(m.STORY),
        "full_script_sha256": hashlib.sha256((m.ROOT / m.STORY).read_bytes()).hexdigest(),
    }
    p = tmp_path / "request.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_current_script_only_and_independent_role_method(tmp_path):
    p = request(tmp_path)
    source, digest = m.source(p)
    prompt, facts = m.build(p)
    assert len(source) > 1800
    assert digest == facts["input_story_only_sha256"]
    assert "00:00–00:10" in prompt and "01:43–01:50" in prompt
    assert "## 原始要求及不同候选" not in prompt
    assert "## 在审稿前最危险" not in prompt
    assert "Story Editor" in prompt
    assert facts["role_ref"].startswith("video_growth_agent/data/team.md#Story_Editor")


def test_only_exact_source_and_one_call_accepted(tmp_path):
    p = request(tmp_path)
    data = json.loads(p.read_text())
    data["max_model_calls"] = 5
    p.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError, match="exact authorized"):
        m.source(p)
    data["max_model_calls"] = 1
    data["full_script_sha256"] = "0" * 64
    p.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError, match="source changed"):
        m.source(p)


def test_real_run_context_required_before_any_model_call(tmp_path, monkeypatch):
    for key in ("GITHUB_TOKEN", "GITHUB_RUN_ID", "GITHUB_JOB"):
        monkeypatch.delenv(key, raising=False)
    def fail(_prompt):
        raise AssertionError("no inference authorized")
    monkeypatch.setattr(m, "live_copilot", fail)
    with pytest.raises(RuntimeError, match="real GitHub Actions"):
        m.execute(tmp_path / "out.json", request(tmp_path))


def test_proof_binds_review_to_script_and_is_never_art_acceptance(tmp_path):
    p = request(tmp_path)
    prompt, info = m.build(p)
    body = "具体独立场次反证与结构修订" * 60
    result = {
        "provenance": {
            "stage": "v4_story_editor", "provider": "github-copilot-cli",
            "input_story_only_sha256": info["input_story_only_sha256"],
            "full_script_sha256": info["full_script_sha256"],
            "github_job": "v4_story_editor",
            "github_run_id": "real-run-id",
            "copilot_session_id": "isolated-session",
            "provider_response_id": "provider-msg",
            "output_sha256": m.sha(body),
            "artistic_acceptance": False,
            "external_human_viewer_count": 0,
        },
        "model_output": body,
    }
    output = tmp_path / "review.json"
    output.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    assert m.verify(output, p)["model_output"] == body
    result["provenance"]["full_script_sha256"] = "0" * 64
    output.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(RuntimeError, match="invalid provenance"):
        m.verify(output, p)
