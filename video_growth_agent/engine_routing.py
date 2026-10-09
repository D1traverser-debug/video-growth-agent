from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Lane = Literal["exploration", "production"]
Risk = Literal["low", "medium", "high", "hero"]


@dataclass(frozen=True)
class EngineProfile:
    """A routing-time view of one execution engine.

    Profiles are deliberately supplied by the caller instead of being hard-coded in
    the router. Price, availability and measured quality are runtime evidence and can
    change independently of policy.
    """

    engine_id: str
    capabilities: frozenset[str]
    measured_quality: float
    estimated_cost_usd_per_second: float
    available: bool = False
    premium: bool = False
    scarcity_pool: str | None = None
    scarcity_units_per_second: float = 0.0
    scarcity_units_remaining: float | None = None
    scarcity_reserve: float = 0.0
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.engine_id:
            raise ValueError("engine_id is required")
        if not 0.0 <= self.measured_quality <= 5.0:
            raise ValueError("measured_quality must be between 0 and 5")
        if self.estimated_cost_usd_per_second < 0:
            raise ValueError("estimated cost cannot be negative")
        if self.scarcity_units_per_second < 0:
            raise ValueError("scarcity units per second cannot be negative")
        if self.scarcity_reserve < 0:
            raise ValueError("scarcity reserve cannot be negative")
        if self.scarcity_units_remaining is not None and self.scarcity_units_remaining < 0:
            raise ValueError("scarcity remaining cannot be negative")
        if self.scarcity_pool and self.scarcity_units_remaining is None:
            raise ValueError("scarcity pools require scarcity_units_remaining")


@dataclass(frozen=True)
class ShotRequest:
    shot_id: str
    required_capabilities: frozenset[str]
    duration_seconds: float
    minimum_quality: float
    lane: Lane
    risk: Risk
    allow_premium_override: bool = False

    def __post_init__(self) -> None:
        if not self.shot_id:
            raise ValueError("shot_id is required")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if not 0.0 <= self.minimum_quality <= 5.0:
            raise ValueError("minimum_quality must be between 0 and 5")


@dataclass(frozen=True)
class CandidateAssessment:
    engine_id: str
    eligible: bool
    reasons: tuple[str, ...]
    measured_quality: float
    estimated_cost_usd: float
    projected_scarcity_remaining: float | None
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoutingDecision:
    shot_id: str
    lane: Lane
    risk: Risk
    selected_engine_id: str | None
    assessments: tuple[CandidateAssessment, ...]
    blocked_reason: str | None = None

    @property
    def blocked(self) -> bool:
        return self.selected_engine_id is None


@dataclass(frozen=True)
class RoutingPolicy:
    """Quality-gated economics for shot-level routing.

    - A cheaper engine never wins by failing the shot's minimum quality/capability bar.
    - Premium engines are protected from ordinary shots by default.
    - Exploration optimizes cost only *after* quality/capability eligibility.
    - Production optimizes measured quality first, then cost.
    """

    premium_risks: frozenset[Risk] = field(default_factory=lambda: frozenset({"high", "hero"}))


class CostAwareShotRouter:
    def __init__(self, policy: RoutingPolicy | None = None):
        self.policy = policy or RoutingPolicy()

    def assess(self, request: ShotRequest, engine: EngineProfile) -> CandidateAssessment:
        reasons: list[str] = []
        missing = request.required_capabilities.difference(engine.capabilities)
        if not engine.available:
            reasons.append("ENGINE_UNAVAILABLE")
        if missing:
            reasons.append("MISSING_CAPABILITIES:" + ",".join(sorted(missing)))
        if engine.measured_quality < request.minimum_quality:
            reasons.append("BELOW_QUALITY_FLOOR")
        if (
            engine.premium
            and request.risk not in self.policy.premium_risks
            and not request.allow_premium_override
        ):
            reasons.append("PREMIUM_ENGINE_RESERVED_FOR_HIGH_RISK_SHOTS")

        estimated_cost = engine.estimated_cost_usd_per_second * request.duration_seconds
        projected_remaining: float | None = None
        if engine.scarcity_pool:
            assert engine.scarcity_units_remaining is not None
            projected_remaining = (
                engine.scarcity_units_remaining
                - engine.scarcity_units_per_second * request.duration_seconds
            )
            if projected_remaining < engine.scarcity_reserve:
                reasons.append("SCARCITY_RESERVE_WOULD_BE_BREACHED")

        return CandidateAssessment(
            engine_id=engine.engine_id,
            eligible=not reasons,
            reasons=tuple(reasons),
            measured_quality=engine.measured_quality,
            estimated_cost_usd=estimated_cost,
            projected_scarcity_remaining=projected_remaining,
            evidence_refs=engine.evidence_refs,
        )

    def route(self, request: ShotRequest, engines: list[EngineProfile] | tuple[EngineProfile, ...]) -> RoutingDecision:
        assessments = tuple(self.assess(request, engine) for engine in engines)
        eligible = [item for item in assessments if item.eligible]
        if not eligible:
            return RoutingDecision(
                shot_id=request.shot_id,
                lane=request.lane,
                risk=request.risk,
                selected_engine_id=None,
                assessments=assessments,
                blocked_reason="NO_ENGINE_MEETS_CAPABILITY_QUALITY_COST_POLICY",
            )

        if request.lane == "exploration":
            # Cheapest sufficient experiment first. Quality breaks cost ties.
            eligible.sort(
                key=lambda item: (
                    item.estimated_cost_usd,
                    -item.measured_quality,
                    item.engine_id,
                )
            )
        else:
            # Final production is quality-first. Cost only breaks quality ties.
            eligible.sort(
                key=lambda item: (
                    -item.measured_quality,
                    item.estimated_cost_usd,
                    item.engine_id,
                )
            )

        return RoutingDecision(
            shot_id=request.shot_id,
            lane=request.lane,
            risk=request.risk,
            selected_engine_id=eligible[0].engine_id,
            assessments=assessments,
        )
