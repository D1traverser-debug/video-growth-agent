"""V6 one-session review: preserve isolation, exact script pin, no inference in CI."""
import hashlib
import json

import pytest

from scripts import agent_war_v4_review as reviewer


def make_request(tmp_path):
    source = (reviewer.ROOT / reviewer.V6_STORY).read_bytes()
    content = {
        "purpose": "blind_single_story_editor_v6",
        "max_model_calls": 1,
        "story_path": str(reviewer.V6_STORY),
        "full_script_sha256": hashlib.sha256(source).hexdigest(),
    }
    path = tmp_path / "request_v6.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def test_v6_only_independent_story_not_author_assessment(tmp_path):
    path = make_request(tmp_path)
    story, story_sha = reviewer.source(path)
    prompt, facts = reviewer.build(path)
    assert story_sha == facts["input_story_only_sha256"]
    assert "00:00–00:10" in story and "01:44–01:52" in story
    assert "兰姨" in story and "赤" in story and "蓝" in story
    assert "## 本稿真正要让观众完成的推断" not in prompt
    assert "## 作者自己必须提出的最严重反例" not in prompt
    assert "## 这次的实质选择" not in prompt
    assert "故事是否真有趣" not in prompt  # no author score is shipped
    assert "换一个摄像角度" in prompt
    assert "Story Editor" in prompt


def test_v6_blind_stale_or_unauthorized_requests_fail(tmp_path):
    path = make_request(tmp_path)
    data = json.loads(path.read_text())
    data["full_script_sha256"] = "0" * 64
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError, match="source changed"):
        reviewer.source(path)
    data["full_script_sha256"] = hashlib.sha256((reviewer.ROOT / reviewer.V6_STORY).read_bytes()).hexdigest()
    data["max_model_calls"] = 2
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError, match="exact authorized"):
        reviewer.source(path)
    data["max_model_calls"] = 1
    data["purpose"] = "invalid_v6"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(RuntimeError, match="exact authorized"):
        reviewer.source(path)


def test_v6_missing_model_run_context_prevents_api_use(tmp_path, monkeypatch):
    path = make_request(tmp_path)
    for key in ("GITHUB_TOKEN", "GITHUB_RUN_ID", "GITHUB_JOB"):
        monkeypatch.delenv(key, raising=False)
    def no_run(_prompt):
        raise AssertionError("model call must not happen in tests")
    monkeypatch.setattr(reviewer, "live_copilot", no_run)
    with pytest.raises(RuntimeError, match="real GitHub Actions"):
        reviewer.execute(tmp_path / "result.json", path)
