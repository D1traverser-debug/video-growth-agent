"""Counterexample-driven checks: structural correctness never implies generated-pixel QA."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from video_growth_agent.prompt_director import (
    H3, PIXVERSE_V6, PromptPlanError, compile_file, compile_prompts, validate_plan,
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
    assert all(len(p["prompt"]) <= H3["max_prompt_characters"]
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


def test_h3_integer_minimum_length_is_separate_from_editorial_frame_duration():
    spec = load("prompt_ribbon_10s.json")
    report = compile_prompts(spec, "shotwise")["routes"]["shotwise"]
    assert report["prompts"][0]["edit_duration_seconds"] == 48 / 30
    assert report["prompts"][0]["model_render_seconds"] == 4
    assert abs(report["prompts"][0]["trim_seconds"] - 2.4) < 1e-9
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


def test_h3_native_sound_sections_do_not_invent_dialogue():
    spec = load("prompt_ip_5s.json")
    report = compile_file(FIXTURES / "prompt_ip_5s.json", "shotwise", h3_style="official")
    assert spec["provider"]["native_audio"] is True
    assert report["visual_winner"] is None
    for item in report["routes"]["shotwise"]["prompts"]:
        prompt = item["prompt"]
        assert prompt.startswith("integrated_multimodal_description: [Shot 1]")
        assert "\n\noverall_soundscape: " in prompt
        assert "\n\nnon_diegetic_music: " in prompt
        assert "<d>" not in prompt
        assert item["model_render_seconds"] >= 4


def test_invalid_unknown_fields_fail_instead_of_being_ignored():
    spec = load("prompt_ip_5s.json")
    spec["shots"][0]["vague_magic"] = "add more cinematic feel"
    with pytest.raises(PromptPlanError, match="unknown"):
        validate_plan(spec)



def test_h3_uses_local_cut_times_and_requires_edit_conform():
    output = compile_prompts(load("prompt_ribbon_10s.json"), "compare", h3_style="official")
    one = output["routes"]["onepass"]
    assert one["status"] == "COMPILED"
    assert "[Shot 2] At 00:01.600" in one["prompts"][0]["prompt"]
    assert one["generation_seconds"] == 10
    assert one["frame_rate_warning"] is not None
    shotwise = output["routes"]["shotwise"]
    assert shotwise["generation_seconds"] == 24
    assert shotwise["generation_to_edit_ratio"] == 2.4
    assert "[Shot 2] At " not in shotwise["prompts"][1]["prompt"]
    assert "hold the resulting pose" in shotwise["prompts"][1]["prompt"]


def test_vendor_comparison_keeps_directorial_plan_without_fake_causal_rating():
    h3 = load("prompt_ip_5s.json")
    pixverse = copy.deepcopy(h3)
    pixverse["provider"].update(name="PixVerse", model="V6", mode="T2V", native_audio=False)
    h3_out = compile_prompts(h3, "compare")
    pv_out = compile_prompts(pixverse, "compare")
    assert h3_out["static_validation"]["events_present_in_plan"] == pv_out["static_validation"]["events_present_in_plan"]
    assert h3_out["visual_winner"] is None
    assert pv_out["visual_winner"] is None
    assert h3_out["routes"]["onepass"]["generation_seconds"] == 5
    assert pv_out["routes"]["onepass"]["generation_seconds"] == 5
    assert h3_out["routes"]["shotwise"]["generation_seconds"] == 12
    assert pv_out["routes"]["shotwise"]["generation_seconds"] == 5


def test_unbound_h3_reference_mode_is_blocked_instead_of_hallucinating_assets():
    spec = load("prompt_ip_5s.json")
    spec["provider"]["mode"] = "Ref2VA"
    with pytest.raises(PromptPlanError, match="bound assets"):
        validate_plan(spec)



def test_owner_verified_chinese_storyboard_is_default_without_erasing_official_variant():
    spec = load("prompt_ribbon_10s.json")
    cn = compile_prompts(spec, route="onepass")
    official = compile_prompts(spec, route="onepass", h3_style="official")
    assert cn["h3_prompt_dialect"] == "chinese"
    cn_text = cn["routes"]["onepass"]["prompts"][0]["prompt"]
    en_text = official["routes"]["onepass"]["prompts"][0]["prompt"]
    assert "逐时段分镜" in cn_text
    assert "红绸赴约" in cn_text
    assert "integrated_multimodal_description" in en_text
    assert "overall_soundscape" in en_text
    assert "non_diegetic_music" in en_text
    assert cn_text != en_text
    assert cn["static_validation"] == official["static_validation"]
    assert cn["visual_winner"] is None and official["visual_winner"] is None
