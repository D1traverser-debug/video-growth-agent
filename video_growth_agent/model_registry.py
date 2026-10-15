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
class QualityObservation:
    """One calibrated quality observation for one benchmark/rubric scope.

    The numeric value is only directly comparable when rubric_id and
    calibration_scope match. Uncertainty is preserved instead of pretending that
    evaluator outputs are exact measurements.
    """

    value: float
    rubric_id: str
    calibration_scope: str
    uncertainty: float
    evidence_class: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.value) <= 5.0:
            raise RoutingError("quality observation value must be between 0 and 5")
        if not 0.0 <= float(self.uncertainty) <= 5.0:
            raise RoutingError("quality uncertainty must be between 0 and 5")
        if not self.rubric_id.strip() or not self.calibration_scope.strip() or not self.evidence_class.strip():
            raise RoutingError("quality observation requires rubric/calibration/evidence class")
        if not self.evidence_refs:
            raise RoutingError("quality observation requires evidence_refs")

    @property
    def lower_bound(self) -> float:
        return max(0.0, float(self.value) - float(self.uncertainty))

    @property
    def upper_bound(self) -> float:
        return min(5.0, float(self.value) + float(self.uncertainty))

    def comparable_with(self, other: "QualityObservation") -> bool:
        return (
            self.rubric_id == other.rubric_id
            and self.calibration_scope == other.calibration_scope
        )


@dataclass(frozen=True)
class OperationProfile:
    """A legal provider operation surface, not a flat capability claim.

    Providers may expose multiple profiles for the same model when duration,
    resolution, reference budgets or source requirements differ. This models
    conditional capabilities without hard-coding vendor names into business logic.
    """

    profile_id: str
    mode: str
    capabilities: frozenset[str]
    allowed_durations_seconds: frozenset[float] = field(default_factory=frozenset)
    min_duration_seconds: float | None = None
    max_duration_seconds: float | None = None
    resolutions: frozenset[str] = field(default_factory=frozenset)
    max_reference_images: int = 0
    max_reference_videos: int = 0
    max_reference_audio: int = 0
    allowed_source_origins: frozenset[str] = field(default_factory=frozenset)
    conditions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.profile_id.strip() or not self.mode.strip():
            raise RoutingError("operation profile requires profile_id and mode")
        if self.min_duration_seconds is not None and self.min_duration_seconds <= 0:
            raise RoutingError("min_duration_seconds must be positive")
        if self.max_duration_seconds is not None and self.max_duration_seconds <= 0:
            raise RoutingError("max_duration_seconds must be positive")
        if (
            self.min_duration_seconds is not None
            and self.max_duration_seconds is not None
            and self.min_duration_seconds > self.max_duration_seconds
        ):
            raise RoutingError("operation profile duration range is invalid")
        if any(float(value) <= 0 for value in self.allowed_durations_seconds):
            raise RoutingError("allowed durations must be positive")
        if min(self.max_reference_images, self.max_reference_videos, self.max_reference_audio) < 0:
            raise RoutingError("reference limits cannot be negative")

    def mismatch_reasons(self, request: "ShotRoutingRequest") -> tuple[str, ...]:
        reasons: list[str] = []
        if self.mode.upper() != request.operation_mode.upper():
            reasons.append("OPERATION_MODE_UNSUPPORTED")
        missing = request.required_capabilities.difference(self.capabilities)
        if missing:
            reasons.append("MISSING_CAPABILITIES:" + ",".join(sorted(missing)))
        duration = float(request.duration_seconds)
        if self.allowed_durations_seconds and duration not in self.allowed_durations_seconds:
            reasons.append("DURATION_COMBINATION_UNSUPPORTED")
        if self.min_duration_seconds is not None and duration < self.min_duration_seconds:
            reasons.append("DURATION_BELOW_PROFILE_MINIMUM")
        if self.max_duration_seconds is not None and duration > self.max_duration_seconds:
            reasons.append("DURATION_EXCEEDS_PROFILE_LIMIT")
        if request.required_resolution and self.resolutions and request.required_resolution not in self.resolutions:
            reasons.append("RESOLUTION_COMBINATION_UNSUPPORTED")
        if request.reference_images > self.max_reference_images:
            reasons.append("IMAGE_REFERENCE_BUDGET_EXCEEDED")
        if request.reference_videos > self.max_reference_videos:
            reasons.append("VIDEO_REFERENCE_BUDGET_EXCEEDED")
        if request.reference_audio > self.max_reference_audio:
            reasons.append("AUDIO_REFERENCE_BUDGET_EXCEEDED")
        if request.source_origin and self.allowed_source_origins and request.source_origin not in self.allowed_source_origins:
            reasons.append("SOURCE_ORIGIN_UNSUPPORTED")
        return tuple(reasons)


@dataclass(frozen=True)
class ModelObservation:
    """Dated, evidence-bound routing view of one current execution substrate."""

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
    operation_profiles: tuple[OperationProfile, ...] = ()
    quality_observations: Mapping[str, QualityObservation] = field(default_factory=dict)

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
        profile_ids = [profile.profile_id for profile in self.operation_profiles]
        if len(profile_ids) != len(set(profile_ids)):
            raise RoutingError("operation profile IDs must be unique per engine")

    def fresh(self, *, now: datetime | None = None, max_age_days: int = 30) -> bool:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        observed = _parse_time(self.observed_at)
        if self.valid_until and now > _parse_time(self.valid_until):
            return False
        return (now - observed).total_seconds() <= max_age_days * 86400

    def matching_profiles(self, request: "ShotRoutingRequest") -> tuple[OperationProfile, ...]:
        return tuple(
            profile
            for profile in self.operation_profiles
            if not profile.mismatch_reasons(request)
        )


@dataclass(frozen=True)
class ShotRoutingRequest:
    shot_id: str
    lane: Lane
    risk: Risk
    duration_seconds: float
    required_capabilities: frozenset[str]
    minimum_quality: Mapping[str, float]
    quality_weights: Mapping[str, float] = field(default_factory=dict)  # compatibility only; never used for 0.8 ranking
    quality_priorities: tuple[str, ...] = ()
    quality_rubric_id: str | None = None
    calibration_scope: str | None = None
    operation_mode: str = "I2V"
    require_operation_profile: bool = False
    required_resolution: str | None = None
    reference_images: int = 0
    reference_videos: int = 0
    reference_audio: int = 0
    input_media_seconds: float = 0.0
    source_origin: str | None = None
    require_commercial_use: bool = True
    require_provenance: bool = False
    max_cost_usd: float | None = None
    evidence_max_age_days: int = 30

    def __post_init__(self) -> None:
        if not self.shot_id.strip() or not self.operation_mode.strip():
            raise RoutingError("shot_id and operation_mode are required")
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
        if self.quality_priorities and len(set(self.quality_priorities)) != len(self.quality_priorities):
            raise RoutingError("quality priorities must be unique")
        if bool(self.quality_rubric_id) != bool(self.calibration_scope):
            raise RoutingError("quality_rubric_id and calibration_scope must be supplied together")


@dataclass(frozen=True)
class ModelAssessment:
    engine_id: str
    eligible: bool
    reasons: tuple[str, ...]
    quality_utility: float
    estimated_cost_usd: float
    quality_vector: Mapping[str, float] = field(default_factory=dict)
    quality_lower_bounds: Mapping[str, float] = field(default_factory=dict)
    operation_profile_id: str | None = None
    calibration_scope: str | None = None


@dataclass(frozen=True)
class ModelRoutingDecision:
    shot_id: str
    selected_engine_id: str | None
    assessments: tuple[ModelAssessment, ...]
    blocked_reason: str | None = None
    pareto_front: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        return self.selected_engine_id is None


class EvidenceBoundModelRouter:
    """Route by hard constraints plus calibrated vector evidence.

    0.8 deliberately does not collapse production quality into one hidden weighted
    average. Exploration is cheapest-sufficient after hard floors. Production forms
    a Pareto frontier and uses explicitly declared quality priorities only when a
    trade-off remains.
    """

    def assess(
        self,
        request: ShotRoutingRequest,
        engine: ModelObservation,
        *,
        now: datetime | None = None,
    ) -> ModelAssessment:
        reasons: list[str] = []
        profile_id: str | None = None
        if not engine.available:
            reasons.append("ENGINE_UNAVAILABLE")
        if engine.deprecated:
            reasons.append("ENGINE_DEPRECATED")
        if not engine.fresh(now=now, max_age_days=request.evidence_max_age_days):
            reasons.append("STALE_ENGINE_OBSERVATION")

        if request.require_operation_profile:
            matching = engine.matching_profiles(request)
            if not matching:
                reasons.append("NO_OPERATION_PROFILE_MATCHES_REQUEST")
            else:
                profile_id = sorted(profile.profile_id for profile in matching)[0]
        else:
            missing = request.required_capabilities.difference(engine.capabilities)
            if missing:
                reasons.append("MISSING_CAPABILITIES:" + ",".join(sorted(missing)))
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

        if request.require_commercial_use and not engine.commercial_use_allowed:
            reasons.append("COMMERCIAL_USE_NOT_ADMITTED")
        if request.require_provenance and not engine.provenance_supported:
            reasons.append("PROVENANCE_REQUIRED")

        quality_vector: dict[str, float] = {}
        lower_bounds: dict[str, float] = {}
        calibrated = bool(request.quality_rubric_id and request.calibration_scope)
        for dimension, floor in request.minimum_quality.items():
            observation = engine.quality_observations.get(dimension)
            if calibrated:
                if observation is None:
                    reasons.append(f"QUALITY_UNMEASURED:{dimension}")
                    continue
                if (
                    observation.rubric_id != request.quality_rubric_id
                    or observation.calibration_scope != request.calibration_scope
                ):
                    reasons.append(f"QUALITY_NOT_COMPARABLE:{dimension}")
                    continue
                quality_vector[dimension] = float(observation.value)
                lower_bounds[dimension] = observation.lower_bound
                if observation.lower_bound < float(floor):
                    reasons.append(f"QUALITY_LOWER_BOUND_BELOW_FLOOR:{dimension}")
            else:
                observed = engine.quality_scores.get(dimension)
                if observed is None:
                    reasons.append(f"QUALITY_UNMEASURED:{dimension}")
                else:
                    quality_vector[dimension] = float(observed)
                    lower_bounds[dimension] = float(observed)
                    if float(observed) < float(floor):
                        reasons.append(f"QUALITY_BELOW_FLOOR:{dimension}")

        if not engine.quality_evidence_refs and not engine.quality_observations:
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

        # Kept only for backwards-compatible observability; it is not used for 0.8 selection.
        utility = sum(quality_vector.values()) / len(quality_vector) if quality_vector else 0.0
        return ModelAssessment(
            engine_id=engine.engine_id,
            eligible=not reasons,
            reasons=tuple(reasons),
            quality_utility=utility,
            estimated_cost_usd=estimated_cost,
            quality_vector=quality_vector,
            quality_lower_bounds=lower_bounds,
            operation_profile_id=profile_id,
            calibration_scope=request.calibration_scope,
        )

    @staticmethod
    def _dominates(left: ModelAssessment, right: ModelAssessment, dimensions: tuple[str, ...]) -> bool:
        if not dimensions:
            return False
        left_values = [left.quality_lower_bounds.get(dimension) for dimension in dimensions]
        right_values = [right.quality_lower_bounds.get(dimension) for dimension in dimensions]
        if any(value is None for value in left_values + right_values):
            return False
        return all(l >= r for l, r in zip(left_values, right_values)) and any(
            l > r for l, r in zip(left_values, right_values)
        )

    def _pareto_front(
        self,
        assessments: list[ModelAssessment],
        dimensions: tuple[str, ...],
    ) -> list[ModelAssessment]:
        return [
            candidate
            for candidate in assessments
            if not any(
                other.engine_id != candidate.engine_id
                and self._dominates(other, candidate, dimensions)
                for other in assessments
            )
        ]

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
            eligible.sort(key=lambda item: (item.estimated_cost_usd, item.engine_id))
            return ModelRoutingDecision(
                shot_id=request.shot_id,
                selected_engine_id=eligible[0].engine_id,
                assessments=assessments,
                pareto_front=tuple(item.engine_id for item in eligible),
            )

        dimensions = request.quality_priorities or tuple(request.minimum_quality)
        front = self._pareto_front(eligible, dimensions)
        if len(front) == 1:
            selected = front[0]
        else:
            if not request.quality_priorities:
                return ModelRoutingDecision(
                    shot_id=request.shot_id,
                    selected_engine_id=None,
                    assessments=assessments,
                    blocked_reason="QUALITY_TRADEOFF_REQUIRES_DECLARED_PRIORITY",
                    pareto_front=tuple(sorted(item.engine_id for item in front)),
                )
            front.sort(
                key=lambda item: tuple(
                    -float(item.quality_lower_bounds.get(dimension, -1.0))
                    for dimension in request.quality_priorities
                ) + (item.estimated_cost_usd, item.engine_id)
            )
            selected = front[0]

        return ModelRoutingDecision(
            shot_id=request.shot_id,
            selected_engine_id=selected.engine_id,
            assessments=assessments,
            pareto_front=tuple(sorted(item.engine_id for item in front)),
        )
