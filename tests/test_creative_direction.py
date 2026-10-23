"""Independent structural/contract checks for creative plans; no fake model-quality assertions."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from video_growth_agent.creative_direction import (
    CraftSpecError,
    compile_from_file,
    compile_storyboard,
    validate_spec,
    verify_editorial_binding,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name,frames,shots,events", [
    ("creative_ip_5s.json", 150, 3, 5),
    ("creative_ribbon_10s.json", 300, 6, 13),
])
def test_divergent_film_ideas_preserve_planned_story_contract(name, frames, shots, events):
    plan = load(name)
    summary = validate_spec(plan)
    assert plan["duration_frames"] == frames
    assert summary["duration_seconds"] == frames / 30
    assert summary["shot_count"] == shots
    assert len(summary["event_to_shots"]) == events
    assert all(summary["event_to_shots"].values())
    result = compile_storyboard(plan, route="shotwise")
    assert len(result["prompts"]) == shots
    assert abs(sum(s["duration_seconds"] for s in result["prompts"]) - frames / 30) < 1e-9
    assert all(item["prompt"].startswith(plan["title"]) for item in result["prompts"])
    assert result["assurance"].startswith("Static structural validation")


def test_typed_editorial_plan_identity_and_beat_coverage():
    from dataclasses import replace
    from video_growth_agent.editorial_planning import (
        BeatSpec, EditorialPlan, EpisodeIntent, ShotIntent,
    )

    spec = load("creative_ip_5s.json")
    intent = EpisodeIntent(
        episode_id="ip-intro", series_id="personal-ip",
        audience_contract="five-second recognizable character bumper",
        editorial_question="Who controls the edit?",
        primary_platform="short-video",
        target_duration_seconds=5,
        evidence_refs=("user-brief://ip-intro",),
        desired_outcomes=("recognizable human and Shiba duo",),
        success_metric_semantics={"recognition": "post-view unaided recall"},
    )
    beats = tuple(
        BeatSpec(f"beat-{shot['id']}", "ip-intro", shot["action"],
                 "recognition", (shot["end_frame"] - shot["start_frame"]) / 30)
        for shot in spec["shots"]
    )
    source_shots = tuple(
        ShotIntent(shot["id"], f"beat-{shot['id']}", shot["action"],
                   (shot["end_frame"] - shot["start_frame"]) / 30,
                   "SYNTHETIC", "LOW", (), frozenset({"T2V"}))
        for shot in spec["shots"]
    )
    approved = EditorialPlan(intent, (), beats, source_shots, "v1")
    bound = verify_editorial_binding(spec, approved)
    assert bound["all_approved_beats_mapped"]
    assert bound["beat_count"] == 3

    with pytest.raises(CraftSpecError, match="does not match"):
        verify_editorial_binding(spec, replace(approved, plan_version="v2"))
    broken = copy.deepcopy(spec)
    broken["shots"][-1]["source_beat_ids"] = ["beat-IP1"]
    with pytest.raises(CraftSpecError, match="omitted from craft"):
        verify_editorial_binding(broken, approved)


def test_onepass_supports_simple_five_second_ip_case():
    result = compile_from_file(FIXTURES / "creative_ip_5s.json", route="onepass")
    assert len(result["prompts"]) == 1
    assert "Shiba" in result["prompts"][0]["prompt"]
    assert "0.00s" in result["prompts"][0]["prompt"]
    assert "5.00s" in result["prompts"][0]["prompt"]


def test_compression_rejects_omitted_required_story_event():
    plan = load("creative_ribbon_10s.json")
    plan["shots"][-1]["event_ids"].remove("tie")
    with pytest.raises(CraftSpecError, match="story events lost"):
        validate_spec(plan)


@pytest.mark.parametrize("edit", [
    lambda s: s["shots"][1].update(start_frame=40),
    lambda s: s["shots"][1].update(start_frame=10),
    lambda s: s["shots"][-1].update(end_frame=149),
])
def test_rejects_timeline_gap_overlap_and_short_end(edit):
    plan = load("creative_ip_5s.json")
    edit(plan)
    with pytest.raises(CraftSpecError, match="gaps|timeline must end"):
        validate_spec(plan)


def test_rejects_unexpected_semantic_fields_and_unknown_events():
    plan = load("creative_ip_5s.json")
    plan["shots"][0]["temporal_miracle"] = True
    with pytest.raises(CraftSpecError, match="unexpected fields"):
        validate_spec(plan)
    plan = load("creative_ip_5s.json")
    plan["shots"][0]["event_ids"].append("invented")
    with pytest.raises(CraftSpecError, match="unknown narrative event"):
        validate_spec(plan)


def test_rejects_prompt_overflow_without_silent_truncation():
    plan = load("creative_ip_5s.json")
    plan["generator"]["max_prompt_characters"] = 50
    with pytest.raises(CraftSpecError, match="exceeds"):
        compile_storyboard(plan, route="onepass")
    with pytest.raises(CraftSpecError, match="exceeds"):
        compile_storyboard(plan, route="shotwise")


def test_edit_frame_duration_is_not_falsely_passed_as_provider_duration():
    plan = load("creative_ribbon_10s.json")
    out = compile_storyboard(plan, route="shotwise")
    assert out["prompts"][0]["duration_seconds"] == 48 / 30
    assert out["prompts"][0]["generation_duration_seconds"] == 2
    assert "TIMING_POST_REQUIRED: generated integer-second clips need frame-accurate trims" in out["review_flags"]
    assert all(isinstance(p["generation_duration_seconds"], int) for p in out["prompts"])


def test_provider_duration_limit_fails_closed():
    plan = load("creative_ip_5s.json")
    plan["generator"]["provider"] = "OtherVendor"
    with pytest.raises(CraftSpecError, match="only dated PixVerse V6"):
        compile_storyboard(plan)
    plan["generator"]["provider"] = "PixVerse"
    plan["duration_frames"] = 510
    plan["shots"][-1]["end_frame"] = 510
    with pytest.raises(CraftSpecError, match="outside verified"):
        compile_storyboard(plan, route="onepass")


def test_never_confuses_sound_intent_with_generated_audio():
    plan = load("creative_ribbon_10s.json")
    result = compile_storyboard(plan)
    assert "SOUND_POST_REQUIRED: sonic cues must be produced in post" in result["review_flags"]
    assert not result["narrative_coverage"].get("generated_visuals_verified", False)


def test_approach_comparison_abstains_without_render_evidence():
    for fixture in ("creative_ip_5s.json", "creative_ribbon_10s.json"):
        comparison = compile_from_file(FIXTURES / fixture, route="compare")
        assert comparison["visual_quality_winner"] is None
        assert comparison["candidates"]["shotwise"]["status"] == "COMPILED"
        shotwise = comparison["candidates"]["shotwise"]
        assert shotwise["total_generated_seconds"] >= shotwise["total_edit_seconds"]
        assert comparison["planned_event_count"] == len(load(fixture)["required_story_events"])
        assert "onepass" in comparison["candidates"]


def test_cli_exposes_real_compilation_and_structural_errors(tmp_path):
    command = [sys.executable, "-m", "video_growth_agent.cli", "storyboard",
               str(FIXTURES / "creative_ip_5s.json"), "--route", "shotwise"]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["narrative_coverage"]["shot_count"] == 3

    invalid = load("creative_ip_5s.json")
    invalid["shots"][0]["end_frame"] = 31
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(invalid), encoding="utf-8")
    bad = subprocess.run(command[:4] + [str(path)], capture_output=True, text=True)
    assert bad.returncode == 2
    assert "storyboard error" in bad.stderr
