"""D2 source pin and first-look-only feedback; no model calls in CI."""
import hashlib
import json
from pathlib import Path

import pytest
from scripts import agent_war_v4_review as reviewer


def req(tmp_path):
    data={
        "purpose":"blind_writer_scene_lesson01_revision",
        "max_model_calls":1,
        "story_path":str(reviewer.LESSON01_D2),
        "full_script_sha256":hashlib.sha256(
            (reviewer.ROOT/reviewer.LESSON01_D2).read_bytes()).hexdigest(),
    }
    p=tmp_path/"input.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_d2_source_only_not_author_self_critique(tmp_path):
    p=req(tmp_path)
    scene,h=reviewer.source(p)
    prompt,facts=reviewer.build(p)
    assert "四号车" in scene and "登记员" in scene and "女人" in scene
    assert "SCENE_STRUCTURAL_REWRITE" not in prompt
    assert "作者" not in scene
    assert "对照" not in scene and "最应该击败" not in scene
    assert "只对下方一份单独提供" in prompt
    assert facts["input_story_only_sha256"]==h


def test_d2_stale_source_and_two_calls_rejected(tmp_path):
    p=req(tmp_path)
    r=json.loads(p.read_text())
    r["full_script_sha256"]="0"*64
    p.write_text(json.dumps(r))
    with pytest.raises(RuntimeError,match="source changed"):reviewer.source(p)
    r["max_model_calls"]=2
    p.write_text(json.dumps(r))
    with pytest.raises(RuntimeError,match="exact authorized"):reviewer.source(p)
