from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping

Lane = str
Risk = str


class RoutingError(ValueError):
    pass


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ModelObservation:
    """Dated, evidence-bound routing view of one current execution substrate.

    Provider/model facts are deliberately observations rather than permanent code truth.
    A later observation can replace this object without changing shot/business semantics.
    """

    engine_id: str
    observed_at: str
    capabilities: frozenset[str]
    quality_scores: Mapping[str, float]
    available: bool
    commercial_use_allowed: bool
    provenance_supported: bool = False
    deprecated: bool = False
    max_duration_seconds: float | None = None
    max_reference_images: int = 0
    max_reference_videos: int = 0
    max_reference_audio: int = 0
    resolutions: frozenset[str] = field(default_factory=frozenset)
    fixed_cost_usd: float = 0.0
    output_cost_usd_per_second: float = 0.0
    input_cost_usd_per_second: float = 0.0
    latency_class: str = "UNKNOWN"
    quality_evidence_refs: tuple[str, ...] = ()
    pricing_evidence_refs: tuple[str, ...] = ()
    terms_evidence_refs: tuple[str, ...] = ()
    availability_evidence_refs: tuple[str, ...] = ()
    valid_until: str | None = None

    def __post_init__(self) -> None:
        if not self.engine_id.strip():
            raise RoutingError("engine_id is required")
        _parse_time(self.observed_at)
        if self.valid_until:
            _parse_time(self.valid_until)
        for name, value in self.quality_scores.items():
            if not 0.0 <= float(value) <= 5.0:
                raise RoutingError(f"quality score out of range: {name}={value}")
        for value, label in (
            (self.fixed_cost_usd, "fixed cost"),
            (self.output_cost_usd_per_second, "output cost"),
            (self.input_cost_usd_per_second, "input cost"),
        ):
            if value < 0:
                raise RoutingError(f"{label} cannot be negative")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise RoutingError("max_duration_seconds must be positive")
        if min(self.max_reference_images, self.max_reference_videos, self.max_reference_audio) < 0:
            raise RoutingError("reference limits cannot be negative")

    def fresh(self, *, now: datetime | None = None, max_age_days: int = 30) -> bool:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        observed = _parse_time(self.observed_at)
        if self.valid_until and now > _parse_time(self.valid_until):
            return False
        return (now - observed).total_seconds() <= max_age_days * 86400


@dataclass(frozen=True)
class ShotRoutingRequest:
    shot_id: str
    lane: Lane
    risk: Risk
    duration_seconds: float
    required_capabilities: frozenset[str]
    minimum_quality: Mapping[str, float]
    quality_weights: Mapping[str, float]
    required_resolution: str | None = None
    reference_images: int = 0
    reference_videos: int = 0
    reference_audio: int = 0
    input_media_seconds: float = 0.0
    require_commercial_use: bool = True
    require_provenance: bool = False
    max_cost_usd: float | None = None
    evidence_max_age_days: int = 30

    def __post_init__(self) -> None:
        if not self.shot_id.strip():
            raise RoutingError("shot_id is required")
        if self.duration_seconds <= 0:
            raise RoutingError("duration_seconds must be positive")
        if self.input_media_seconds < 0:
            raise RoutingError("input_media_seconds cannot be negative")
        if min(self.reference_images, self.reference_videos, self.reference_audio) < 0:
            raise RoutingError("reference counts cannot be negative")
        if self.max_cost_usd is not None and self.max_cost_usd < 0:
            raise RoutingError("max_cost_usd cannot be negative")
        for name, floor in self.minimum_quality.items():
            if not 0.0 <= float(floor) <= 5.0:
                raise RoutingError(f"quality floor out of range: {name}={floor}")
        if any(float(weight) < 0 for weight in self.quality_weights.values()):
            raise RoutingError("quality weights cannot be negative")


@dataclass(frozen=True)
class ModelAssessment:
    engine_id: str
    eligible: bool
    reasons: tuple[str, ...]
    quality_utility: float
    estimated_cost_usd: float


@dataclass(frozen=True)
class ModelRoutingDecision:
    shot_id: str
    selected_engine_id: str | None
    assessments: tuple[ModelAssessment, ...]
    blocked_reason: str | None = None

    @property
    def blocked(self) -> bool:
        return self.selected_engine_id is None


class EvidenceBoundModelRouter:
    """Route shots by current capability evidence, quality vector and economics.

    Exploration is cost-first after hard floors. Production is quality-first.
    Hero/brand-truth work can demand stronger provenance through the request.
    """

    def assess(
        self,
        request: ShotRoutingRequest,
        engine: ModelObservation,
        *,
        now: datetime | None = None,
    ) -> ModelAssessment:
        reasons: list[str] = []
        if not engine.available:
            reasons.append("ENGINE_UNAVAILABLE")
        if engine.deprecated:
            reasons.append("ENGINE_DEPRECATED")
        if not engine.fresh(now=now, max_age_days=request.evidence_max_age_days):
            reasons.append("STALE_ENGINE_OBSERVATION")

        missing = request.required_capabilities.difference(engine.capabilities)
        if missing:
            reasons.append("MISSING_CAPABILITIES:" + ",".join(sorted(missing)))

        if request.require_commercial_use and not engine.commercial_use_allowed:
            reasons.append("COMMERCIAL_USE_NOT_ADMITTED")
        if request.require_provenance and not engine.provenance_supported:
            reasons.append("PROVENANCE_REQUIRED")
        if request.required_resolution and request.required_resolution not in engine.resolutions:
            reasons.append("RESOLUTION_UNSUPPORTED")
        if engine.max_duration_seconds is not None and request.duration_seconds > engine.max_duration_seconds:
            reasons.append("DURATION_EXCEEDS_ENGINE_LIMIT")
        if request.reference_images > engine.max_reference_images:
            reasons.append("IMAGE_REFERENCE_BUDGET_EXCEEDED")
        if request.reference_videos > engine.max_reference_videos:
            reasons.append("VIDEO_REFERENCE_BUDGET_EXCEEDED")
        if request.reference_audio > engine.max_reference_audio:
            reasons.append("AUDIO_REFERENCE_BUDGET_EXCEEDED")

        for dimension, floor in request.minimum_quality.items():
            observed = engine.quality_scores.get(dimension)
            if observed is None:
                reasons.append(f"QUALITY_UNMEASURED:{dimension}")
            elif float(observed) < float(floor):
                reasons.append(f"QUALITY_BELOW_FLOOR:{dimension}")

        if not engine.quality_evidence_refs:
            reasons.append("MISSING_QUALITY_EVIDENCE")
        if not engine.pricing_evidence_refs:
            reasons.append("MISSING_PRICING_EVIDENCE")
        if request.require_commercial_use and not engine.terms_evidence_refs:
            reasons.append("MISSING_TERMS_EVIDENCE")
        if not engine.availability_evidence_refs:
            reasons.append("MISSING_AVAILABILITY_EVIDENCE")

        estimated_cost = (
            engine.fixed_cost_usd
            + engine.output_cost_usd_per_second * request.duration_seconds
            + engine.input_cost_usd_per_second * request.input_media_seconds
        )
        if request.max_cost_usd is not None and estimated_cost > request.max_cost_usd:
            reasons.append("SHOT_BUDGET_EXCEEDED")

        weighted_sum = 0.0
        total_weight = 0.0
        for dimension, weight in request.quality_weights.items():
            weight = float(weight)
            if weight <= 0:
                continue
            score = engine.quality_scores.get(dimension)
            if score is None:
                continue
            weighted_sum += float(score) * weight
            total_weight += weight
        utility = weighted_sum / total_weight if total_weight else 0.0

        return ModelAssessment(
            engine_id=engine.engine_id,
            eligible=not reasons,
            reasons=tuple(reasons),
            quality_utility=utility,
            estimated_cost_usd=estimated_cost,
        )

    def route(
        self,
        request: ShotRoutingRequest,
        engines: list[ModelObservation] | tuple[ModelObservation, ...],
        *,
        now: datetime | None = None,
    ) -> ModelRoutingDecision:
        assessments = tuple(self.assess(request, engine, now=now) for engine in engines)
        eligible = [item for item in assessments if item.eligible]
        if not eligible:
            return ModelRoutingDecision(
                shot_id=request.shot_id,
                selected_engine_id=None,
                assessments=assessments,
                blocked_reason="NO_CURRENT_ENGINE_MEETS_SHOT_CONTRACT",
            )

        if request.lane.upper() == "EXPLORATION":
            eligible.sort(key=lambda item: (item.estimated_cost_usd, -item.quality_utility, item.engine_id))
        else:
            eligible.sort(key=lambda item: (-item.quality_utility, item.estimated_cost_usd, item.engine_id))

        return ModelRoutingDecision(
            shot_id=request.shot_id,
            selected_engine_id=eligible[0].engine_id,
            assessments=assessments,
        )
