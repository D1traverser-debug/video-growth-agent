from datetime import datetime, timezone

from video_growth_agent.model_registry import (
    EvidenceBoundModelRouter,
    ModelObservation,
    ShotRoutingRequest,
)


def _engine(engine_id: str, **overrides):
    base = dict(
        engine_id=engine_id,
        observed_at="2026-10-15T00:00:00Z",
        capabilities=frozenset({"I2V", "IMAGE_REFERENCES", "NATIVE_AUDIO"}),
        quality_scores={"identity": 4.0, "motion": 4.0, "adherence": 4.0},
        available=True,
        commercial_use_allowed=True,
        provenance_supported=True,
        max_duration_seconds=30,
        max_reference_images=30,
        max_reference_videos=10,
        max_reference_audio=10,
        resolutions=frozenset({"720p", "1080p"}),
        output_cost_usd_per_second=0.2,
        quality_evidence_refs=("quality://benchmark",),
        pricing_evidence_refs=("pricing://current",),
        terms_evidence_refs=("terms://commercial",),
        availability_evidence_refs=("availability://session",),
    )
    base.update(overrides)
    return ModelObservation(**base)


def _request(**overrides):
    base = dict(
        shot_id="S001",
        lane="PRODUCTION",
        risk="HERO",
        duration_seconds=5,
        required_capabilities=frozenset({"I2V", "IMAGE_REFERENCES"}),
        minimum_quality={"identity": 3.5, "motion": 3.0},
        quality_weights={"identity": 2.0, "motion": 1.0, "adherence": 1.0},
        required_resolution="1080p",
        reference_images=3,
        max_cost_usd=10.0,
        require_provenance=True,
        evidence_max_age_days=30,
    )
    base.update(overrides)
    return ShotRoutingRequest(**base)


def test_production_routes_quality_first_after_hard_gates():
    router = EvidenceBoundModelRouter()
    cheap = _engine("cheap", output_cost_usd_per_second=0.05, quality_scores={"identity": 3.7, "motion": 3.2, "adherence": 3.5})
    strong = _engine("strong", output_cost_usd_per_second=0.4, quality_scores={"identity": 4.7, "motion": 4.5, "adherence": 4.6})
    decision = router.route(_request(), [cheap, strong], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.selected_engine_id == "strong"


def test_exploration_routes_cheapest_sufficient_engine():
    router = EvidenceBoundModelRouter()
    cheap = _engine("cheap", output_cost_usd_per_second=0.05)
    strong = _engine("strong", output_cost_usd_per_second=0.4, quality_scores={"identity": 4.8, "motion": 4.8, "adherence": 4.8})
    decision = router.route(_request(lane="EXPLORATION", require_provenance=False), [strong, cheap], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.selected_engine_id == "cheap"


def test_stale_observation_is_not_execution_truth():
    router = EvidenceBoundModelRouter()
    stale = _engine("stale", observed_at="2026-08-01T00:00:00Z")
    decision = router.route(_request(), [stale], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.blocked
    assert "STALE_ENGINE_OBSERVATION" in decision.assessments[0].reasons


def test_provider_deprecation_blocks_even_if_quality_is_high():
    router = EvidenceBoundModelRouter()
    retired = _engine("retired", deprecated=True, quality_scores={"identity": 5.0, "motion": 5.0, "adherence": 5.0})
    decision = router.route(_request(), [retired], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.blocked
    assert "ENGINE_DEPRECATED" in decision.assessments[0].reasons


def test_reference_budget_and_commercial_terms_are_hard_gates():
    router = EvidenceBoundModelRouter()
    limited = _engine("limited", max_reference_images=1, commercial_use_allowed=False)
    decision = router.route(_request(reference_images=4), [limited], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.blocked
    reasons = decision.assessments[0].reasons
    assert "IMAGE_REFERENCE_BUDGET_EXCEEDED" in reasons
    assert "COMMERCIAL_USE_NOT_ADMITTED" in reasons
