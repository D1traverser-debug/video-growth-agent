from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Lane = Literal["exploration", "production"]
Risk = Literal["low", "medium", "high", "hero"]
_VALID_LANES = frozenset({"exploration", "production"})
_VALID_RISKS = frozenset({"low", "medium", "high", "hero"})


@dataclass(frozen=True)
class EngineProfile:
    """A routing-time view of one execution engine.

    Profiles are supplied by the caller rather than hard-coded here. Availability,
    price and measured quality are volatile evidence, not permanent model traits.
    """

    engine_id: str
    capabilities: frozenset[str]
    measured_quality: float | None
    available: bool = False
    premium: bool = False
    fixed_cost_usd: float = 0.0
    output_cost_usd_per_second: float = 0.0
    input_cost_usd_per_second: float = 0.0
    scarcity_pool: str | None = None
    scarcity_fixed_units: float = 0.0
    scarcity_units_per_second: float = 0.0
    scarcity_units_remaining: float | None = None
    scarcity_reserve: float = 0.0
    quality_evidence_refs: tuple[str, ...] = ()
    pricing_evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.engine_id:
            raise ValueError("engine_id is required")
        if self.measured_quality is not None and not 0.0 <= self.measured_quality <= 5.0:
            raise ValueError("measured_quality must be between 0 and 5")
        for value, label in (
            (self.fixed_cost_usd, "fixed cost"),
            (self.output_cost_usd_per_second, "output cost"),
            (self.input_cost_usd_per_second, "input cost"),
            (self.scarcity_fixed_units, "scarcity fixed units"),
            (self.scarcity_units_per_second, "scarcity units per second"),
            (self.scarcity_reserve, "scarcity reserve"),
        ):
            if value < 0:
                raise ValueError(f"{label} cannot be negative")
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
    input_media_seconds: float = 0.0
    allow_premium_override: bool = False

    def __post_init__(self) -> None:
        if not self.shot_id:
            raise ValueError("shot_id is required")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if self.input_media_seconds < 0:
            raise ValueError("input_media_seconds cannot be negative")
        if not 0.0 <= self.minimum_quality <= 5.0:
            raise ValueError("minimum_quality must be between 0 and 5")
        if self.lane not in _VALID_LANES:
            raise ValueError(f"unsupported lane: {self.lane}")
        if self.risk not in _VALID_RISKS:
            raise ValueError(f"unsupported risk: {self.risk}")


@dataclass(frozen=True)
class CandidateAssessment:
    engine_id: str
    eligible: bool
    reasons: tuple[str, ...]
    measured_quality: float | None
    estimated_cost_usd: float
    projected_scarcity_remaining: float | None
    quality_evidence_refs: tuple[str, ...] = ()
    pricing_evidence_refs: tuple[str, ...] = ()


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

    A cheap engine can never route around evidence, capability or quality gates.
    Exploration minimizes price among eligible candidates. Production maximizes
    measured quality first. Premium capacity is protected from ordinary shots.
    """

    premium_risks: frozenset[Risk] = field(default_factory=lambda: frozenset({"high", "hero"}))
    require_quality_evidence: bool = True
    require_pricing_evidence: bool = True

    def __post_init__(self) -> None:
        invalid = set(self.premium_risks).difference(_VALID_RISKS)
        if invalid:
            raise ValueError("unsupported premium risks: " + ",".join(sorted(invalid)))


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
        if engine.measured_quality is None:
            reasons.append("UNMEASURED_QUALITY")
        elif engine.measured_quality < request.minimum_quality:
            reasons.append("BELOW_QUALITY_FLOOR")
        if self.policy.require_quality_evidence and not engine.quality_evidence_refs:
            reasons.append("MISSING_QUALITY_EVIDENCE")
        if self.policy.require_pricing_evidence and not engine.pricing_evidence_refs:
            reasons.append("MISSING_PRICING_EVIDENCE")
        if (
            engine.premium
            and request.risk not in self.policy.premium_risks
            and not request.allow_premium_override
        ):
            reasons.append("PREMIUM_ENGINE_RESERVED_FOR_HIGH_RISK_SHOTS")

        estimated_cost = (
            engine.fixed_cost_usd
            + engine.output_cost_usd_per_second * request.duration_seconds
            + engine.input_cost_usd_per_second * request.input_media_seconds
        )
        projected_remaining: float | None = None
        if engine.scarcity_pool:
            assert engine.scarcity_units_remaining is not None
            projected_remaining = (
                engine.scarcity_units_remaining
                - engine.scarcity_fixed_units
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
            quality_evidence_refs=engine.quality_evidence_refs,
            pricing_evidence_refs=engine.pricing_evidence_refs,
        )

    def route(
        self,
        request: ShotRequest,
        engines: list[EngineProfile] | tuple[EngineProfile, ...],
    ) -> RoutingDecision:
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
                    -(item.measured_quality or 0.0),
                    item.engine_id,
                )
            )
        else:
            # Final production is quality-first. Cost only breaks quality ties.
            eligible.sort(
                key=lambda item: (
                    -(item.measured_quality or 0.0),
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
