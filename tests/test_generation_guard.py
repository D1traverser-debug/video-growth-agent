import pytest

from video_growth_agent.generation_guard import assert_generation_brief, generation_brief_failures


def valid_brief():
    return {
        "narrative_job": "Show manual work before the operating surface breaks into delegated execution.",
        "before_state": "Human hand actively switches between physical device surfaces.",
        "crossing_state": "The operating plane physically ruptures and depth relationship changes.",
        "after_state": "The task has left the user-facing app plane and entered a different service world.",
        "must_have": ["human-scale physical interaction", "one dominant focal event"],
        "must_not_have": ["AI mascot", "floating feature menu", "SaaS dashboard"],
        "benchmark_refs": ["CINEMATIC_BENCHMARK_LANE", "SAMPLE_V3_SHOT_REPAIR_MATRIX"],
        "engine_route": "static keyframe exploration first; premium video only after endpoints pass",
        "quality_floor": 4,
        "stop_conditions": ["prompt drifts to explanatory UI", "world states are not distinct"],
        "prompt_blocklist": ["robot", "AI assistant", "floating panels", "dashboard", "feature list"],
        "literal_forbidden_prompt_terms": ["robot", "dashboard"],
        "exact_prompt": "Cinematic macro photograph of a real hand moving between a laptop trackpad and a phone on a tactile desk, practical light, shallow depth, photographed perspective, no explanatory text.",
        "pre_generation_challenge": {
            "art_creative": {"decision": "PASS", "notes": "Prompt preserves a photographed human/manual state and avoids explanatory interface language."},
            "red_team": {"decision": "PASS", "notes": "Strongest failure risk is stock-office genericism; constrained by macro physical action and single focal event."},
        },
    }


def test_valid_generation_brief_passes():
    brief = valid_brief()
    assert generation_brief_failures(brief) == []
    assert_generation_brief(brief)


def test_blocked_prompt_term_fails_before_generation():
    brief = valid_brief()
    brief["exact_prompt"] += " A cute AI assistant robot appears beside a floating dashboard."
    failures = generation_brief_failures(brief)
    assert "prompt_contains_blocked_term:robot" in failures
    assert "prompt_contains_blocked_term:AI assistant" in failures
    assert "prompt_contains_blocked_term:dashboard" in failures
    with pytest.raises(ValueError):
        assert_generation_brief(brief)


def test_missing_pre_generation_challenge_fails_closed():
    brief = valid_brief()
    del brief["pre_generation_challenge"]
    assert "pre_generation_challenge_missing" in generation_brief_failures(brief)


def test_identical_before_after_state_fails():
    brief = valid_brief()
    brief["after_state"] = brief["before_state"]
    assert "world_state_not_distinct:before=after" in generation_brief_failures(brief)
