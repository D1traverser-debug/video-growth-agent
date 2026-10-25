"""Train a scene by actual independent reviewer, not a self-certifying quality metric."""
import json
from pathlib import Path
import subprocess

import pytest
from scripts import agent_war_v4_review as r


def request(tmp_path):
    q={"purpose": "blind_writer_scene_lesson01", "max_model_calls": 1,
       "story_path": str(r.LESSON01),
       "script_git_blob_sha": subprocess.check_output(
           ["git", "hash-object", str(r.ROOT / r.LESSON01)], text=True, cwd=r.ROOT).strip()}
    p=tmp_path/"request.json"
    p.write_text(json.dumps(q),encoding="utf-8")
    return p


def test_scene_only_and_real_role_without_author_notes(tmp_path):
    p=request(tmp_path)
    story,h=r.source(p)
    prompt,facts=r.build(p)
    assert "《到过》" in story and "登记员" in story
    assert len(story)>350
    assert "作者即时反例" not in prompt and "John August" not in prompt
    assert "旧21秒公告栏" not in prompt
    assert "廉价解法" not in prompt  # author-side critique not included
    assert "可直接问司机" in prompt
    assert "Story Editor" in prompt
    assert f"{h}" == facts["input_story_only_sha256"]
    assert facts["role_ref"].startswith("video_growth_agent/data/team.md#Story_Editor")


def test_stale_or_wrong_source_rejected(tmp_path):
    p=request(tmp_path)
    obj=json.loads(p.read_text())
    obj["script_git_blob_sha"]="0"*40
    p.write_text(json.dumps(obj))
    with pytest.raises(RuntimeError,match="source changed"):r.source(p)
    obj["script_git_blob_sha"]=subprocess.check_output(
       ["git", "hash-object", str(r.ROOT/r.LESSON01)],text=True,cwd=r.ROOT).strip()
    obj["purpose"]="blind_invented"
    p.write_text(json.dumps(obj))
    with pytest.raises(RuntimeError,match="exact authorized"):r.source(p)


def test_no_paid_inference_during_tests(monkeypatch,tmp_path):
    p=request(tmp_path)
    for n in ("GITHUB_TOKEN","GITHUB_RUN_ID","GITHUB_JOB"):monkeypatch.delenv(n,raising=False)
    def fail(_):raise AssertionError("must not invoke")
    monkeypatch.setattr(r,"live_copilot",fail)
    with pytest.raises(RuntimeError,match="real GitHub Actions"):
        r.execute(tmp_path/"output.json",p)
