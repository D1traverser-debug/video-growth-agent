"""Cross-domain stage exercise: one source-only review, not artistic approval."""
import hashlib
import json

import pytest

from scripts import agent_war_v4_review as reviewer


def request(tmp_path):
    data = {
        "purpose": "blind_writer_scene_lesson02_theater",
        "max_model_calls": 1,
        "story_path": str(reviewer.LESSON02_THEATER_D3),
        "full_script_sha256": hashlib.sha256(
            (reviewer.ROOT / reviewer.LESSON02_THEATER_D3).read_bytes()
        ).hexdigest(),
    }
    path = tmp_path / "request_l02.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_theater_review_contains_only_scene_and_problems_not_author_assessment(tmp_path):
    req = request(tmp_path)
    scene, digest = reviewer.source(req)
    prompt, facts = reviewer.build(req)
    assert "梅" in scene and "安" in scene and "小辛" in scene
    assert "《月亮不升》" in scene
    assert "作者冷检" not in prompt
    assert "本轮技能迁移记录" not in prompt
    assert "角色的选择是不是只能靠作者安排" in prompt
    assert "SCENE_PRACTICE_VIABLE" in prompt
    assert digest == facts["input_story_only_sha256"]


def test_theater_review_rejects_stale_and_non_authorized_source(tmp_path):
    req = request(tmp_path)
    body = json.loads(req.read_text(encoding="utf-8"))
    body["full_script_sha256"] = "0" * 64
    req.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(RuntimeError, match="source changed"):
        reviewer.source(req)
    body["full_script_sha256"] = hashlib.sha256(
        (reviewer.ROOT / reviewer.LESSON02_THEATER_D3).read_bytes()
    ).hexdigest()
    body["purpose"] = "some_other_scenario"
    req.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(RuntimeError, match="exact authorized"):
        reviewer.source(req)
