from datetime import datetime, timezone

from video_growth_agent.model_registry import (
    EvidenceBoundModelRouter,
    ModelObservation,
    OperationProfile,
    QualityObservation,
    ShotRoutingRequest,
)


def _quality(identity: float, motion: float, adherence: float = 4.0, *, scope: str = "B01+B02-v1"):
    return {
        "identity": QualityObservation(identity, "video-quality-v1", scope, 0.1, "OWNER_BENCHMARK", ("quality://identity",)),
        "motion": QualityObservation(motion, "video-quality-v1", scope, 0.1, "OWNER_BENCHMARK", ("quality://motion",)),
        "adherence": QualityObservation(adherence, "video-quality-v1", scope, 0.1, "OWNER_BENCHMARK", ("quality://adherence",)),
    }


def _profile(profile_id="i2v-1080", **overrides):
    base = dict(
        profile_id=profile_id,
        mode="I2V",
        capabilities=frozenset({"I2V", "IMAGE_REFERENCES", "NATIVE_AUDIO"}),
        allowed_durations_seconds=frozenset({5.0, 8.0}),
        resolutions=frozenset({"720p", "1080p"}),
        max_reference_images=3,
        max_reference_videos=0,
        max_reference_audio=1,
    )
    base.update(overrides)
    return OperationProfile(**base)


def _engine(engine_id: str, **overrides):
    base = dict(
        engine_id=engine_id,
        observed_at="2026-10-15T00:00:00Z",
        capabilities=frozenset({"I2V", "IMAGE_REFERENCES", "NATIVE_AUDIO"}),
        quality_scores={},
        quality_observations=_quality(4.0, 4.0),
        operation_profiles=(_profile(),),
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
        operation_mode="I2V",
        require_operation_profile=True,
        required_capabilities=frozenset({"I2V", "IMAGE_REFERENCES"}),
        minimum_quality={"identity": 3.5, "motion": 3.0},
        quality_priorities=("identity", "motion"),
        quality_rubric_id="video-quality-v1",
        calibration_scope="B01+B02-v1",
        required_resolution="1080p",
        reference_images=3,
        max_cost_usd=10.0,
        require_provenance=True,
        evidence_max_age_days=30,
    )
    base.update(overrides)
    return ShotRoutingRequest(**base)


def test_production_selects_pareto_dominant_calibrated_engine():
    router = EvidenceBoundModelRouter()
    cheap = _engine("cheap", output_cost_usd_per_second=0.05, quality_observations=_quality(3.8, 3.4))
    strong = _engine("strong", output_cost_usd_per_second=0.4, quality_observations=_quality(4.7, 4.5))
    decision = router.route(_request(), [cheap, strong], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.selected_engine_id == "strong"
    assert decision.pareto_front == ("strong",)


def test_tradeoff_uses_explicit_priority_not_hidden_weighted_average():
    router = EvidenceBoundModelRouter()
    identity_strong = _engine("identity", quality_observations=_quality(4.8, 3.5))
    motion_strong = _engine("motion", quality_observations=_quality(4.0, 4.8))
    decision = router.route(_request(quality_priorities=("identity", "motion")), [identity_strong, motion_strong], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert set(decision.pareto_front) == {"identity", "motion"}
    assert decision.selected_engine_id == "identity"

    blocked = router.route(_request(quality_priorities=()), [identity_strong, motion_strong], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert blocked.blocked_reason == "QUALITY_TRADEOFF_REQUIRES_DECLARED_PRIORITY"


def test_incomparable_quality_calibration_cannot_fake_a_ranking():
    router = EvidenceBoundModelRouter()
    incompatible = _engine("other-scope", quality_observations=_quality(4.9, 4.9, scope="different-pack"))
    decision = router.route(_request(), [incompatible], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.blocked
    assert "QUALITY_NOT_COMPARABLE:identity" in decision.assessments[0].reasons


def test_operation_profile_expresses_conditional_duration_resolution_reference_combinations():
    router = EvidenceBoundModelRouter()
    eight_second_reference_mode = _profile(
        profile_id="ref-1080-eight-only",
        allowed_durations_seconds=frozenset({8.0}),
        resolutions=frozenset({"1080p"}),
        max_reference_images=3,
    )
    engine = _engine("conditional", operation_profiles=(eight_second_reference_mode,))
    invalid = router.route(_request(duration_seconds=5), [engine], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert invalid.blocked
    assert "NO_OPERATION_PROFILE_MATCHES_REQUEST" in invalid.assessments[0].reasons

    valid = router.route(_request(duration_seconds=8), [engine], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert valid.selected_engine_id == "conditional"
    assert valid.assessments[0].operation_profile_id == "ref-1080-eight-only"


def test_exploration_routes_cheapest_sufficient_engine_after_hard_floors():
    router = EvidenceBoundModelRouter()
    cheap = _engine("cheap", output_cost_usd_per_second=0.05)
    strong = _engine("strong", output_cost_usd_per_second=0.4, quality_observations=_quality(4.8, 4.8))
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
    retired = _engine("retired", deprecated=True, quality_observations=_quality(5.0, 5.0, 5.0))
    decision = router.route(_request(), [retired], now=datetime(2026, 10, 15, tzinfo=timezone.utc))
    assert decision.blocked
    assert "ENGINE_DEPRECATED" in decision.assessments[0].reasons
