import pytest

from video_growth_agent.engine_routing import (
    CostAwareShotRouter,
    EngineProfile,
    ShotRequest,
)


def engine(
    engine_id: str,
    *,
    quality: float | None,
    output_cost: float = 0.0,
    fixed_cost: float = 0.0,
    input_cost: float = 0.0,
    capabilities: set[str] | None = None,
    available: bool = True,
    premium: bool = False,
    pool: str | None = None,
    scarcity_fixed: float = 0.0,
    units_per_second: float = 0.0,
    remaining: float | None = None,
    reserve: float = 0.0,
    evidenced: bool = True,
) -> EngineProfile:
    return EngineProfile(
        engine_id=engine_id,
        capabilities=frozenset(capabilities or {"i2v", "v2v"}),
        measured_quality=quality,
        fixed_cost_usd=fixed_cost,
        output_cost_usd_per_second=output_cost,
        input_cost_usd_per_second=input_cost,
        available=available,
        premium=premium,
        scarcity_pool=pool,
        scarcity_fixed_units=scarcity_fixed,
        scarcity_units_per_second=units_per_second,
        scarcity_units_remaining=remaining,
        scarcity_reserve=reserve,
        quality_evidence_refs=("benchmark://test",) if evidenced else (),
        pricing_evidence_refs=("pricing://test",) if evidenced else (),
    )


def request(
    *,
    lane: str = "exploration",
    risk: str = "medium",
    minimum_quality: float = 4.0,
    input_media_seconds: float = 0.0,
) -> ShotRequest:
    return ShotRequest(
        shot_id="S07",
        required_capabilities=frozenset({"v2v"}),
        duration_seconds=4.0,
        input_media_seconds=input_media_seconds,
        minimum_quality=minimum_quality,
        lane=lane,  # type: ignore[arg-type]
        risk=risk,  # type: ignore[arg-type]
    )


def test_exploration_picks_cheapest_engine_that_still_clears_quality_floor():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high"),
        [
            engine("cheap", quality=4.1, output_cost=0.08),
            engine("premium", quality=4.8, output_cost=0.50, premium=True),
        ],
    )
    assert decision.selected_engine_id == "cheap"


def test_production_high_risk_is_quality_first_even_when_more_expensive():
    router = CostAwareShotRouter()
    decision = router.route(
        request(lane="production", risk="hero"),
        [
            engine("cheap", quality=4.2, output_cost=0.08),
            engine("premium", quality=4.8, output_cost=0.50, premium=True),
        ],
    )
    assert decision.selected_engine_id == "premium"


def test_cheap_engine_cannot_win_by_failing_quality_floor():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high", minimum_quality=4.0),
        [
            engine("too-cheap", quality=3.7, output_cost=0.01),
            engine("good", quality=4.2, output_cost=0.10),
        ],
    )
    assert decision.selected_engine_id == "good"
    failed = next(item for item in decision.assessments if item.engine_id == "too-cheap")
    assert "BELOW_QUALITY_FLOOR" in failed.reasons


def test_unavailable_or_incapable_engine_is_never_selected():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high"),
        [
            engine("offline", quality=5.0, available=False),
            engine("wrong-mode", quality=5.0, capabilities={"t2v"}),
            engine("usable", quality=4.1, output_cost=0.12),
        ],
    )
    assert decision.selected_engine_id == "usable"


def test_unmeasured_quality_fails_closed():
    router = CostAwareShotRouter()
    decision = router.route(request(risk="high"), [engine("unknown", quality=None)])
    assert decision.blocked
    assert "UNMEASURED_QUALITY" in decision.assessments[0].reasons


def test_missing_quality_or_price_evidence_fails_closed():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high"),
        [engine("claims-only", quality=5.0, output_cost=0.0, evidenced=False)],
    )
    assert decision.blocked
    reasons = decision.assessments[0].reasons
    assert "MISSING_QUALITY_EVIDENCE" in reasons
    assert "MISSING_PRICING_EVIDENCE" in reasons


def test_fixed_plus_input_plus_output_billing_is_estimated():
    router = CostAwareShotRouter()
    billed = engine(
        "mixed-billing",
        quality=4.5,
        fixed_cost=0.10,
        input_cost=0.08,
        output_cost=0.08,
    )
    decision = router.route(request(risk="high", input_media_seconds=4.0), [billed])
    assert decision.selected_engine_id == "mixed-billing"
    assert decision.assessments[0].estimated_cost_usd == pytest.approx(0.74)


def test_fixed_price_engine_is_supported():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high"),
        [
            engine("fixed-cheap", quality=4.1, fixed_cost=0.025),
            engine("per-second", quality=4.1, output_cost=0.08),
        ],
    )
    assert decision.selected_engine_id == "fixed-cheap"
    assert decision.assessments[0].estimated_cost_usd == pytest.approx(0.025)


def test_premium_pool_is_protected_from_ordinary_shots():
    router = CostAwareShotRouter()
    decision = router.route(
        request(lane="production", risk="medium"),
        [engine("premium", quality=5.0, output_cost=0.50, premium=True)],
    )
    assert decision.blocked
    assert "PREMIUM_ENGINE_RESERVED_FOR_HIGH_RISK_SHOTS" in decision.assessments[0].reasons


def test_explicit_override_can_use_premium_for_non_high_risk_shot():
    router = CostAwareShotRouter()
    req = ShotRequest(
        shot_id="S08",
        required_capabilities=frozenset({"v2v"}),
        duration_seconds=4,
        minimum_quality=4.5,
        lane="production",
        risk="medium",
        allow_premium_override=True,
    )
    decision = router.route(
        req,
        [engine("premium", quality=4.8, output_cost=0.50, premium=True)],
    )
    assert decision.selected_engine_id == "premium"


def test_scarcity_reserve_blocks_a_generation_that_would_exhaust_pool():
    router = CostAwareShotRouter()
    scarce = engine(
        "credit-pool",
        quality=4.8,
        premium=True,
        pool="monthly-credits",
        units_per_second=15.0,
        remaining=78.0,
        reserve=30.0,
    )
    decision = router.route(request(lane="production", risk="hero"), [scarce])
    assert decision.blocked
    assert decision.assessments[0].projected_scarcity_remaining == 18.0
    assert "SCARCITY_RESERVE_WOULD_BE_BREACHED" in decision.assessments[0].reasons


def test_scarcity_supports_fixed_and_per_second_units():
    router = CostAwareShotRouter()
    scarce = engine(
        "hybrid-pool",
        quality=4.5,
        premium=True,
        pool="credits",
        scarcity_fixed=5.0,
        units_per_second=2.0,
        remaining=40.0,
        reserve=20.0,
    )
    decision = router.route(request(lane="production", risk="hero"), [scarce])
    assert decision.selected_engine_id == "hybrid-pool"
    assert decision.assessments[0].projected_scarcity_remaining == 27.0


def test_no_eligible_engine_fails_closed():
    router = CostAwareShotRouter()
    decision = router.route(
        request(),
        [engine("bad", quality=2.0)],
    )
    assert decision.blocked
    assert decision.blocked_reason == "NO_ENGINE_MEETS_CAPABILITY_QUALITY_COST_POLICY"


def test_invalid_lane_or_risk_is_rejected_at_contract_boundary():
    with pytest.raises(ValueError, match="unsupported lane"):
        request(lane="ad-hoc")
    with pytest.raises(ValueError, match="unsupported risk"):
        request(risk="whatever")
