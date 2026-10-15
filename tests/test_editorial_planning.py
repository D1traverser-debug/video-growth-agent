import pytest

from video_growth_agent.editorial_planning import (
    BeatSpec,
    ClaimSpec,
    EditorialPlan,
    EditorialPlanningError,
    EpisodeIntent,
    ShotIntent,
)


def _intent():
    return EpisodeIntent(
        episode_id="E001",
        series_id="engineer-world",
        audience_contract="Explain one system clearly without faking certainty",
        editorial_question="Why does AI inference move toward the edge?",
        primary_platform="BILIBILI",
        target_duration_seconds=480,
        evidence_refs=("research://topic",),
        desired_outcomes=("qualified_watch_time", "follow_conversion"),
        success_metric_semantics={"qualified_watch_time": "minutes from target-audience viewers"},
    )


def test_fact_claim_requires_evidence():
    with pytest.raises(EditorialPlanningError, match="FACT claim requires evidence_refs"):
        ClaimSpec("C1", "A factual statement", "FACT", "MEDIUM")


def test_product_truth_shot_must_bind_product_truth_claim():
    intent = _intent()
    claim = ClaimSpec("C1", "Analytical framing", "ANALYSIS", "MEDIUM")
    beat = BeatSpec("B1", intent.episode_id, "open the mechanism", "create curiosity", 30, claim_ids=("C1",))
    shot = ShotIntent(
        "S1", "B1", "show exact sponsor UI", 5, "PRODUCT_TRUTH", "BRAND_TRUTH",
        source_claim_ids=("C1",), allowed_production_modes=frozenset({"REAL_ASSET"}),
    )
    with pytest.raises(EditorialPlanningError, match="PRODUCT_TRUTH shot"):
        EditorialPlan(intent, (claim,), (beat,), (shot,), "v1")


def test_beat_dependency_cycle_is_rejected():
    intent = _intent()
    b1 = BeatSpec("B1", intent.episode_id, "one", "one", 20, depends_on=("B2",))
    b2 = BeatSpec("B2", intent.episode_id, "two", "two", 20, depends_on=("B1",))
    s1 = ShotIntent("S1", "B1", "one", 5, "SYNTHETIC", "LOW", (), frozenset({"I2V"}))
    s2 = ShotIntent("S2", "B2", "two", 5, "SYNTHETIC", "LOW", (), frozenset({"I2V"}))
    with pytest.raises(EditorialPlanningError, match="cycle"):
        EditorialPlan(intent, (), (b1, b2), (s1, s2), "v1")


def test_every_beat_must_have_a_production_expression():
    intent = _intent()
    b1 = BeatSpec("B1", intent.episode_id, "one", "one", 20)
    b2 = BeatSpec("B2", intent.episode_id, "two", "two", 20, depends_on=("B1",))
    s1 = ShotIntent("S1", "B1", "one", 5, "SYNTHETIC", "LOW", (), frozenset({"I2V"}))
    with pytest.raises(EditorialPlanningError, match="beats without shots"):
        EditorialPlan(intent, (), (b1, b2), (s1,), "v1")


def test_plan_revision_reports_changed_claim_beat_and_shot_ids():
    intent = _intent()
    c1 = ClaimSpec("C1", "v1 analysis", "ANALYSIS", "MEDIUM")
    b1 = BeatSpec("B1", intent.episode_id, "mechanism v1", "clarify", 20, claim_ids=("C1",))
    s1 = ShotIntent("S1", "B1", "visual v1", 5, "SYNTHETIC", "LOW", ("C1",), frozenset({"I2V"}))
    first = EditorialPlan(intent, (c1,), (b1,), (s1,), "v1")

    c2 = ClaimSpec("C1", "v2 analysis", "ANALYSIS", "MEDIUM")
    b2 = BeatSpec("B1", intent.episode_id, "mechanism v2", "clarify", 25, claim_ids=("C1",))
    s2 = ShotIntent("S1", "B1", "visual v2", 6, "SYNTHETIC", "LOW", ("C1",), frozenset({"I2V"}))
    second = first.derive(plan_version="v2", revision_reason="research changed", claims=(c2,), beats=(b2,), shots=(s2,))
    impact = first.impact_of_revision(second)
    assert impact["changed_claim_ids"] == ("C1",)
    assert impact["changed_beat_ids"] == ("B1",)
    assert impact["changed_shot_ids"] == ("S1",)
