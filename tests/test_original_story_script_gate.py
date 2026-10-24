"""Regression for SCRIPT_AUDIT -> production boundary on original narrative."""
from dataclasses import replace
import hashlib

import pytest

from video_growth_agent.editorial_planning import (
    BeatSpec, EditorialPlan, EditorialPlanningError, EpisodeIntent,
    ScriptAuditReceipt, ShotIntent, materialize_shot_contract,
)

SCRIPT = "original-fiction://agent-war/v4"
DIGEST = hashlib.sha256("this exact current script version".encode()).hexdigest()


def plan(*, ip_role="ORIGINAL_NARRATIVE", digest=DIGEST, version="v4"):
    intent = EpisodeIntent(
        episode_id="agent-war", series_id="agent-war-series",
        audience_contract="Understand agents' autonomous choices",
        editorial_question="What makes a war agent responsible?",
        primary_platform="SHORT_FILM", target_duration_seconds=100,
        evidence_refs=("original-brief://agent-war", "script-ref:" + SCRIPT,
                       "script-sha256:" + digest),
        desired_outcomes=("story_comprehension",),
        success_metric_semantics={"story_comprehension": "cold-viewer recalled causal choices"},
        ip_role=ip_role,
    )
    beat = BeatSpec("b1", "agent-war", "agent chooses", "stakes clear", 6)
    shot = ShotIntent("s1", "b1", "visible autonomous act", 5,
                      "SYNTHETIC", "LOW", (), frozenset({"I2V"}))
    return EditorialPlan(intent, (), (beat,), (shot,), version)


def evidence(**changes):
    return replace(ScriptAuditReceipt(
        episode_id="agent-war", script_ref=SCRIPT,
        script_sha256=DIGEST, plan_version="v4",
        verdict="STORYBOARD_CANDIDATE",
        writer_session_id="writer-session-independent-1",
        reviewer_session_id="reviewer-session-independent-2",
        reviewer_execution_ref="actions://real-execution-session-2",
        review_result_ref="audits://real-reviewed-output-v4",
        review_mode="ATTESTED_ISOLATED_AI",
    ), **changes)


def materialize(p, receipt=None):
    return materialize_shot_contract(
        p, shot_id="s1", sequence_id="seq-1",
        required_capabilities=frozenset({"image-to-video"}),
        quality_targets={}, script_audit=receipt,
    )


def test_original_fiction_without_story_review_cannot_become_production_shot():
    with pytest.raises(EditorialPlanningError, match="requires SCRIPT_AUDIT"):
        materialize(plan())


@pytest.mark.parametrize("change,pattern", [
    ({"verdict": "STORY_REVISION_REQUIRED"}, "not passed"),
    ({"review_mode": "SELF_CRITIQUE"}, "separately executed"),
    ({"plan_version": "v3"}, "version mismatch"),
    ({"episode_id": "other"}, "version mismatch"),
    ({"script_sha256": "0" * 64}, "current script"),
    ({"script_ref": "older script"}, "current script"),
    ({"reviewer_session_id": "writer-session-independent-1"}, "independent"),
    ({"reviewer_execution_ref": ""}, "independent"),
    ({"review_result_ref": ""}, "independent"),
])
def test_rejected_forged_or_stale_reviews_cannot_unblock(change, pattern):
    with pytest.raises(EditorialPlanningError, match=pattern):
        materialize(plan(), evidence(**change))


def test_same_review_not_reusable_after_script_changes():
    with pytest.raises(EditorialPlanningError, match="current script"):
        materialize(plan(digest="a" * 64), evidence())


def test_distinct_source_bound_review_can_unlock_production_shot_contract():
    shot = materialize(plan(), evidence())
    assert shot.editorial_plan_ref == "editorial-plan://agent-war@v4"
    assert shot.beat_id == "b1"


def test_existing_nonfiction_and_exploration_unchanged():
    shot = materialize(plan(ip_role="OPTIONAL"))
    assert shot.shot_id == "s1"


def test_story_review_is_not_artistically_tested_by_ci():
    """A structurally valid receipt is not a real audience or truth guarantee."""
    assert evidence().verdict == "STORYBOARD_CANDIDATE"
