"""Agent War GitHub Actions story-room integrity tests.

These checks are offline; they prove source separation and fail-closed logic,
NOT a real external model review or any viewer judgment.
"""
import json
from pathlib import Path

import pytest

from scripts import agent_war_review_runner as runner


def test_premise_challenger_receives_original_brief_without_v6():
    messages, sources = runner.build_messages("premise_challenger")
    assert sources == ["original_user_brief"]
    user = messages[1]["content"]
    assert "Agent" in user and "战争" in user
    assert "K-9" not in user and "A-6" not in user
    assert "M-0" not in user and "断面" not in user


def test_editor_gets_clean_complete_v6_not_authors_verdict():
    script = runner.SCRIPT_PATH.read_text(encoding="utf-8")
    messages, sources = runner.build_messages("story_editor", script_text=script)
    assert sources == ["original_user_brief", "v6_clean_full_script"]
    payload = messages[1]["content"]
    assert "场一｜旧桥的早班" in payload
    assert "场八｜没有命令的下一道工序" in payload
    assert "K-9" in payload and "A-6" in payload and "M-0" in payload
    assert "作者自审结论" not in payload
    assert "V5" not in payload


def _receipt(stage, job, run_id="run42", response_id="response-a"):
    text = "这是独立模型运行返回的剧本批评与替代剧情。" * 20
    return {
        "provenance": {
            "stage": stage, "github_run_id": run_id,
            "github_job": job, "provider_response_id": response_id,
            "review_class": "separately_inferred_model_not_human",
            "output_sha256": runner.digest(text.encode("utf-8")),
        },
        "model_output": text,
    }


def test_review_receipts_require_actual_run_and_digest(tmp_path):
    p = tmp_path / "review.json"
    p.write_text(json.dumps(_receipt("story_editor", "editor")), encoding="utf-8")
    actual = runner.read_actual_review(p, "story_editor", "run42")
    assert actual["provenance"]["github_job"] == "editor"
    with pytest.raises(ValueError, match="non-verifiable"):
        runner.read_actual_review(p, "story_editor", "another_run")
    forged = _receipt("story_editor", "editor")
    forged["provenance"]["output_sha256"] = "invented"
    p.write_text(json.dumps(forged), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        runner.read_actual_review(p, "story_editor", "run42")


def test_rewrite_rejects_same_job_or_same_provider_response(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_RUN_ID", "run42")
    monkeypatch.setenv("GITHUB_JOB", "rewrite")
    a = _receipt("premise_challenger", "same-job", response_id="run-1")
    e = _receipt("story_editor", "same-job", response_id="run-2")
    (tmp_path / "review-premise_challenger.json").write_text(json.dumps(a), encoding="utf-8")
    (tmp_path / "review-story_editor.json").write_text(json.dumps(e), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot share an execution job"):
        runner.run_stage("rewrite", "dummy", tmp_path / "v7.json", "openai/gpt-4.1", tmp_path)
    e["provenance"]["github_job"] = "editor-job"
    e["provenance"]["provider_response_id"] = "run-1"
    (tmp_path / "review-story_editor.json").write_text(json.dumps(e), encoding="utf-8")
    with pytest.raises(ValueError, match="same model response"):
        runner.run_stage("rewrite", "dummy", tmp_path / "v7.json", "openai/gpt-4.1", tmp_path)
    assert not (tmp_path / "v7.json").exists()


def test_text_plain_null_inference_fails_closed(monkeypatch):
    import io

    class NullResponse:
        status = 200
        headers = {"Content-Type": "text/plain"}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return b"null"

    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setattr(runner.urllib.request, "urlopen", lambda *a, **kw: NullResponse())
    with pytest.raises(RuntimeError, match="no external review was performed"):
        runner.infer([{"role": "user", "content": "draft"}], "dummy", "openai/gpt-4.1", 128)
