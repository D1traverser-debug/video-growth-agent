"""Counterexample-driven checks: structural correctness never implies generated-pixel QA."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from video_growth_agent.prompt_director import (
    PIXVERSE_V6, PromptPlanError, compile_file, compile_prompts, validate_plan,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name,frames,events,shots", [
    ("prompt_ip_5s.json", 150, 5, 3),
    ("prompt_ribbon_10s.json", 300, 10, 6),
])
def test_source_first_scenarios_are_mechanically_accountable(name, frames, events, shots):
    spec = load(name)
    result = validate_plan(spec)
    assert spec["brief"]["total_frames"] == frames
    assert result["source_event_count"] == events
    assert result["shot_count"] == shots
    assert result["duration_seconds"] == frames / 30
    output = compile_prompts(spec, "compare")
    assert output["visual_winner"] is None
    assert output["static_validation"]["assurance"].startswith("Static storyboard")
    assert output["routes"]["shotwise"]["status"] == "COMPILED"
    assert abs(sum(p["edit_duration_seconds"] for p in output["routes"]["shotwise"]["prompts"])
               - frames / 30) < 1e-9
    assert all(p["model_render_seconds"] >= p["edit_duration_seconds"]
               for p in output["routes"]["shotwise"]["prompts"])
    assert all(len(p["prompt"]) <= PIXVERSE_V6["max_prompt_characters"]
               for p in output["routes"]["shotwise"]["prompts"])


def test_original_raw_material_quote_is_non_negotiable():
    spec = load("prompt_ribbon_10s.json")
    spec["required_events"][0]["source_quote"] = "从未出现的原文描述"
    with pytest.raises(PromptPlanError, match="not found in raw"):
        validate_plan(spec)


def test_creative_inference_cannot_pass_for_source_quote():
    spec = load("prompt_ip_5s.json")
    spec["required_events"][-1]["source_quote"] = "圆形转场来自用户"
    with pytest.raises(PromptPlanError, match="must not masquerade"):
        validate_plan(spec)


def test_source_event_cannot_disappear_in_compressed_storyboard():
    spec = load("prompt_ribbon_10s.json")
    spec["shots"][-1]["event_ids"].remove("retie")
    with pytest.raises(PromptPlanError, match="SOURCE events missing"):
        validate_plan(spec)


@pytest.mark.parametrize("mutator", [
    lambda x: x["shots"][1].update(start_frame=49),
    lambda x: x["shots"][1].update(start_frame=47),
    lambda x: x["shots"][-1].update(end_frame=299),
    lambda x: x["shots"][0].update(end_frame=0),
])
def test_framing_gap_overlap_and_missing_end_are_rejected(mutator):
    spec = load("prompt_ribbon_10s.json")
    mutator(spec)
    with pytest.raises(PromptPlanError, match="frame gap/overlap|exact final frame"):
        validate_plan(spec)


def test_sound_sync_points_must_be_valid_frame_offsets():
    spec = load("prompt_ip_5s.json")
    spec["shots"][0]["audio"][0]["at_frame"] = 31
    with pytest.raises(PromptPlanError, match="outside its shot"):
        validate_plan(spec)


def test_camera_must_have_single_primary_move():
    spec = load("prompt_ip_5s.json")
    spec["shots"][0]["camera"]["move"] = "PUSH_IN+ORBIT+ZOOM"
    with pytest.raises(PromptPlanError, match="conflicting camera"):
        validate_plan(spec)


def test_creative_alternatives_must_be_distinct_and_record_rejection():
    spec = load("prompt_ip_5s.json")
    spec["alternatives"][1]["id"] = spec["alternatives"][0]["id"]
    with pytest.raises(PromptPlanError, match="duplicate concept"):
        validate_plan(spec)
    spec = load("prompt_ip_5s.json")
    spec["alternatives"] = spec["alternatives"][:1]
    with pytest.raises(PromptPlanError, match="at least two"):
        validate_plan(spec)


def test_pixverse_integer_length_is_separate_from_editorial_frame_duration():
    spec = load("prompt_ribbon_10s.json")
    report = compile_prompts(spec, "shotwise")["routes"]["shotwise"]
    assert report["prompts"][0]["edit_duration_seconds"] == 48 / 30
    assert report["prompts"][0]["model_render_seconds"] == 2
    assert report["prompts"][0]["trim_seconds"] == 0.4
    assert report["generation_seconds"] > report["final_edit_seconds"]


def test_cannot_claim_unverified_provider_or_excessive_onepass_duration():
    spec = load("prompt_ip_5s.json")
    spec["provider"]["model"] = "V99"
    with pytest.raises(PromptPlanError, match="no verified adapter"):
        compile_prompts(spec)
    spec = load("prompt_ribbon_10s.json")
    spec["brief"]["total_frames"] = 480
    spec["shots"][-1]["end_frame"] = 480
    report = compile_prompts(spec, "compare")
    assert report["routes"]["onepass"]["status"] == "BLOCKED"
    assert report["routes"]["shotwise"]["status"] == "COMPILED"


def test_shotwise_compiler_does_not_generate_unrequested_audio():
    spec = load("prompt_ip_5s.json")
    report = compile_file(FIXTURES / "prompt_ip_5s.json", "shotwise")
    assert spec["provider"]["native_audio"] is False
    assert report["visual_winner"] is None
    assert "aesthetic" not in str(report.get("visual_winner", ""))


def test_invalid_unknown_fields_fail_instead_of_being_ignored():
    spec = load("prompt_ip_5s.json")
    spec["shots"][0]["vague_magic"] = "add more cinematic feel"
    with pytest.raises(PromptPlanError, match="unknown"):
        validate_plan(spec)
