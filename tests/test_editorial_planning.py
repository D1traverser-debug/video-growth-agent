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



def test_pure_fiction_can_start_without_fake_research_citations():
    pure_fiction = EpisodeIntent(
        episode_id="F001",
        series_id="fiction-short",
        audience_contract="Viewers of poetic animated shorts",
        editorial_question="Can a silk ribbon connect two people?",
        primary_platform="short-video",
        target_duration_seconds=10,
        evidence_refs=(),
        desired_outcomes=("complete visual narrative",),
        success_metric_semantics={"comprehension": "can retell the story"},
        constraints=("EDITORIAL_MODE:FICTIONAL",),
    )
    assert pure_fiction.constraints == ("EDITORIAL_MODE:FICTIONAL",)
    beat = BeatSpec("B1", pure_fiction.episode_id, "ribbon starts the story", "trigger", 10)
    shot = ShotIntent("S1", "B1", "ribbon flies from female to male hand", 10, "SYNTHETIC", "LOW", (), frozenset({"T2V"}))
    assert EditorialPlan(pure_fiction, (), (beat,), (shot,), "v1").intent == pure_fiction


@pytest.mark.parametrize("editorial_mode", ["FACTUAL", "HYBRID"])
def test_non_fictional_editorial_modes_reject_missing_evidence(editorial_mode):
    with pytest.raises(EditorialPlanningError, match="requires evidence_refs"):
        EpisodeIntent(
            episode_id="E002", series_id="research-series",
            audience_contract="fact-seeking viewers",
            editorial_question="What happened?",
            primary_platform="BILIBILI",
            target_duration_seconds=30,
            evidence_refs=(),
            desired_outcomes=("accurate public explainer",),
            success_metric_semantics={"accuracy": "claim verification"},
            constraints=(f"EDITORIAL_MODE:{editorial_mode}",),
        )


def test_fiction_mode_does_not_exempt_factual_claim_evidence():
    fiction = EpisodeIntent(
        episode_id="F002", series_id="creative-documentary",
        audience_contract="viewers", editorial_question="A fictional scene with a factual fact",
        primary_platform="short-video", target_duration_seconds=5,
        evidence_refs=(), desired_outcomes=("engagement",),
        success_metric_semantics={"retention": "view duration"},
        constraints=("EDITORIAL_MODE:FICTIONAL",),
    )
    with pytest.raises(EditorialPlanningError, match="FACT claim requires evidence_refs"):
        ClaimSpec("C1", "Stock exchange rules are real", "FACT", "HIGH")
    with pytest.raises(EditorialPlanningError, match="invalid or repeated EDITORIAL_MODE constraint"):
        EpisodeIntent(
            episode_id=fiction.episode_id, series_id=fiction.series_id,
            audience_contract=fiction.audience_contract, editorial_question=fiction.editorial_question,
            primary_platform=fiction.primary_platform, target_duration_seconds=fiction.target_duration_seconds,
            evidence_refs=(), desired_outcomes=fiction.desired_outcomes,
            success_metric_semantics=fiction.success_metric_semantics, constraints=("EDITORIAL_MODE:MADE_UP_MODE",),
        )
