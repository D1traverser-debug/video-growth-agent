import pytest

from video_growth_agent.generation_guard import (
    assert_generation_brief,
    generation_brief_digest,
    generation_brief_failures,
)


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
            "art_director": {
                "decision": "PASS",
                "notes": "Physical materials, practical lighting and single-focal composition meet the art-direction contract.",
            },
            "creative_director": {
                "decision": "PASS",
                "notes": "The frame communicates manual-work friction as a narrative event rather than a technology concept poster.",
            },
            "red_team": {
                "decision": "PASS",
                "notes": "Strongest failure risk is stock-office genericism; constrained by macro physical action and single focal event.",
            },
        },
    }


def verified_challenges(brief):
    digest = generation_brief_digest(brief)

    def proof(role: str):
        return {
            "decision": "PASS",
            "work_order_id": f"pilot:PREGEN:{role}",
            "review_receipt_ref": f"receipts/{role}.json",
            "attestation_ref": f"receipts/{role}-attestation.json",
            "executor_id": f"executor-{role}",
            "execution_id": f"exec-{role}",
            "provider_run_id": f"run-{role}",
            "context_id": f"ctx-{role}",
            "trace_id": f"trace-{role}",
            "packet_digest": f"packet-{role}",
            "result_digest": f"result-{role}",
            "brief_digest": digest,
            "proof_ref": f"provider-proof://{role}",
        }

    return {role: proof(role) for role in ("art_director", "creative_director", "red_team")}


def test_valid_generation_brief_requires_external_verified_challenge_bundle():
    brief = valid_brief()
    failures = generation_brief_failures(brief)
    assert "verified_pre_generation_review_evidence_missing" in failures
    with pytest.raises(ValueError, match="verified_pre_generation_review_evidence_missing"):
        assert_generation_brief(brief)


def test_valid_generation_brief_with_bound_independent_receipts_passes():
    brief = valid_brief()
    verified = verified_challenges(brief)
    assert generation_brief_failures(brief, verified_challenges=verified) == []
    assert_generation_brief(brief, verified_challenges=verified)


def test_blocked_prompt_term_fails_before_generation():
    brief = valid_brief()
    brief["exact_prompt"] += " A cute AI assistant robot appears beside a floating dashboard."
    verified = verified_challenges(brief)
    failures = generation_brief_failures(brief, verified_challenges=verified)
    assert "prompt_contains_blocked_term:robot" in failures
    assert "prompt_contains_blocked_term:AI assistant" in failures
    assert "prompt_contains_blocked_term:dashboard" in failures
    with pytest.raises(ValueError):
        assert_generation_brief(brief, verified_challenges=verified)


def test_missing_pre_generation_challenge_fails_closed():
    brief = valid_brief()
    del brief["pre_generation_challenge"]
    failures = generation_brief_failures(brief, verified_challenges=verified_challenges(brief))
    assert "pre_generation_challenge_missing" in failures


def test_identical_before_after_state_fails():
    brief = valid_brief()
    brief["after_state"] = brief["before_state"]
    failures = generation_brief_failures(brief, verified_challenges=verified_challenges(brief))
    assert "world_state_not_distinct:before=after" in failures


def test_inline_pass_cannot_masquerade_as_executed_review():
    brief = valid_brief()
    failures = generation_brief_failures(brief)
    assert "verified_pre_generation_review_evidence_missing" in failures


def test_old_combined_art_creative_slot_cannot_replace_two_specialists():
    brief = valid_brief()
    brief["pre_generation_challenge"] = {
        "art_creative": {
            "decision": "PASS",
            "notes": "One combined reviewer must not count as Art Director plus Creative Director.",
        },
        "red_team": brief["pre_generation_challenge"]["red_team"],
    }
    verified = verified_challenges(brief)
    verified["art_creative"] = verified.pop("art_director")
    verified.pop("creative_director")
    failures = generation_brief_failures(brief, verified_challenges=verified)
    assert "pre_generation_challenge_missing:art_director" in failures
    assert "pre_generation_challenge_missing:creative_director" in failures
    assert "verified_pre_generation_review_missing:art_director" in failures
    assert "verified_pre_generation_review_missing:creative_director" in failures


def test_verified_challenge_must_bind_exact_brief_digest():
    brief = valid_brief()
    verified = verified_challenges(brief)
    verified["red_team"]["brief_digest"] = "wrong-digest"
    failures = generation_brief_failures(brief, verified_challenges=verified)
    assert "verified_pre_generation_review_brief_digest_mismatch:red_team" in failures


def test_verified_challenge_cannot_reuse_execution_context():
    brief = valid_brief()
    verified = verified_challenges(brief)
    verified["red_team"]["context_id"] = verified["art_director"]["context_id"]
    failures = generation_brief_failures(brief, verified_challenges=verified)
    assert any(item.startswith("verified_pre_generation_review_identity_reused:context_id:") for item in failures)
