from video_growth_agent.engine_routing import (
    CostAwareShotRouter,
    EngineProfile,
    ShotRequest,
)


def engine(
    engine_id: str,
    *,
    quality: float,
    cost: float,
    capabilities: set[str] | None = None,
    available: bool = True,
    premium: bool = False,
    pool: str | None = None,
    units_per_second: float = 0.0,
    remaining: float | None = None,
    reserve: float = 0.0,
) -> EngineProfile:
    return EngineProfile(
        engine_id=engine_id,
        capabilities=frozenset(capabilities or {"i2v", "v2v"}),
        measured_quality=quality,
        estimated_cost_usd_per_second=cost,
        available=available,
        premium=premium,
        scarcity_pool=pool,
        scarcity_units_per_second=units_per_second,
        scarcity_units_remaining=remaining,
        scarcity_reserve=reserve,
    )


def request(*, lane: str = "exploration", risk: str = "medium", minimum_quality: float = 4.0) -> ShotRequest:
    return ShotRequest(
        shot_id="S07",
        required_capabilities=frozenset({"v2v"}),
        duration_seconds=4.0,
        minimum_quality=minimum_quality,
        lane=lane,  # type: ignore[arg-type]
        risk=risk,  # type: ignore[arg-type]
    )


def test_exploration_picks_cheapest_engine_that_still_clears_quality_floor():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high"),
        [
            engine("cheap", quality=4.1, cost=0.08),
            engine("premium", quality=4.8, cost=0.50, premium=True),
        ],
    )
    assert decision.selected_engine_id == "cheap"


def test_production_high_risk_is_quality_first_even_when_more_expensive():
    router = CostAwareShotRouter()
    decision = router.route(
        request(lane="production", risk="hero"),
        [
            engine("cheap", quality=4.2, cost=0.08),
            engine("premium", quality=4.8, cost=0.50, premium=True),
        ],
    )
    assert decision.selected_engine_id == "premium"


def test_cheap_engine_cannot_win_by_failing_quality_floor():
    router = CostAwareShotRouter()
    decision = router.route(
        request(risk="high", minimum_quality=4.0),
        [
            engine("too-cheap", quality=3.7, cost=0.01),
            engine("good", quality=4.2, cost=0.10),
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
            engine("offline", quality=5.0, cost=0.0, available=False),
            engine("wrong-mode", quality=5.0, cost=0.0, capabilities={"t2v"}),
            engine("usable", quality=4.1, cost=0.12),
        ],
    )
    assert decision.selected_engine_id == "usable"


def test_premium_pool_is_protected_from_ordinary_shots():
    router = CostAwareShotRouter()
    decision = router.route(
        request(lane="production", risk="medium"),
        [engine("premium", quality=5.0, cost=0.50, premium=True)],
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
    decision = router.route(req, [engine("premium", quality=4.8, cost=0.50, premium=True)])
    assert decision.selected_engine_id == "premium"


def test_scarcity_reserve_blocks_a_generation_that_would_exhaust_pool():
    router = CostAwareShotRouter()
    scarce = engine(
        "credit-pool",
        quality=4.8,
        cost=0.0,
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


def test_no_eligible_engine_fails_closed():
    router = CostAwareShotRouter()
    decision = router.route(
        request(),
        [engine("bad", quality=2.0, cost=0.0)],
    )
    assert decision.blocked
    assert decision.blocked_reason == "NO_ENGINE_MEETS_CAPABILITY_QUALITY_COST_POLICY"
