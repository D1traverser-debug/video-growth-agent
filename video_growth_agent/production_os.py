from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping


class ProductionAdmissionError(RuntimeError):
    pass


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(str(value).strip() for value in (values or ()) if str(value).strip())


TRUTH_MODES = {"SYNTHETIC", "EDITORIAL_REAL", "PRODUCT_TRUTH", "MIXED_DISCLOSED"}
ASSET_STATES = {"CANDIDATE", "SHORTLISTED", "PROMOTED", "REJECTED", "RETIRED"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "HERO", "BRAND_TRUTH"}


@dataclass(frozen=True)
class ReferenceBinding:
    asset_id: str
    version_id: str
    digest: str
    role: str
    rights_ref: str
    consent_ref: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("asset_id", "version_id", "digest", "role", "rights_ref"):
            if not str(getattr(self, field_name)).strip():
                raise ProductionAdmissionError(f"reference binding missing {field_name}")


@dataclass(frozen=True)
class ShotContract:
    shot_id: str
    sequence_id: str
    narrative_job: str
    duration_seconds: float
    truth_mode: str
    risk: str
    allowed_modes: frozenset[str]
    required_capabilities: frozenset[str]
    quality_targets: Mapping[str, float]
    references: tuple[ReferenceBinding, ...] = ()
    must_have: tuple[str, ...] = ()
    must_not_have: tuple[str, ...] = ()
    graceful_degradation: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    budget_usd: float | None = None
    disclosure_required: bool = False
    editorial_plan_ref: str = ""
    beat_id: str = ""
    source_claim_ids: tuple[str, ...] = ()
    continuity_ref: str = ""
    value_vector: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.shot_id.strip() or not self.sequence_id.strip() or not self.narrative_job.strip():
            raise ProductionAdmissionError("shot_id, sequence_id and narrative_job are required")
        if self.duration_seconds <= 0:
            raise ProductionAdmissionError("duration_seconds must be positive")
        if self.truth_mode not in TRUTH_MODES:
            raise ProductionAdmissionError(f"unsupported truth_mode: {self.truth_mode}")
        if self.risk not in RISK_LEVELS:
            raise ProductionAdmissionError(f"unsupported risk: {self.risk}")
        if not self.allowed_modes:
            raise ProductionAdmissionError("allowed_modes cannot be empty")
        if self.budget_usd is not None and self.budget_usd < 0:
            raise ProductionAdmissionError("budget_usd cannot be negative")
        for name, score in self.quality_targets.items():
            if not 0 <= float(score) <= 5:
                raise ProductionAdmissionError(f"quality target out of range: {name}={score}")
        for name, score in self.value_vector.items():
            if not 0 <= float(score) <= 5:
                raise ProductionAdmissionError(f"value vector out of range: {name}={score}")
        if self.truth_mode == "PRODUCT_TRUTH" and not self.references:
            raise ProductionAdmissionError("PRODUCT_TRUTH shots require verified reference bindings")
        if bool(self.editorial_plan_ref) != bool(self.beat_id):
            raise ProductionAdmissionError("editorial_plan_ref and beat_id must be supplied together")

    @property
    def editorially_traceable(self) -> bool:
        return bool(self.editorial_plan_ref and self.beat_id)


@dataclass(frozen=True)
class GenerationAdmission:
    shot_id: str
    lane: str
    provider_id: str
    route_evidence_refs: tuple[str, ...]
    rights_evidence_refs: tuple[str, ...]
    capability_evidence_refs: tuple[str, ...]
    budget_evidence_refs: tuple[str, ...]
    admitted: bool
    reasons: tuple[str, ...] = ()


def admit_candidate_generation(
    shot: ShotContract,
    *,
    lane: str,
    provider_id: str,
    route_evidence_refs: Iterable[str] | None,
    rights_evidence_refs: Iterable[str] | None,
    capability_evidence_refs: Iterable[str] | None,
    budget_evidence_refs: Iterable[str] | None,
    provider_available: bool,
    commercial_use_admitted: bool,
    within_budget: bool,
    required_reference_rights_satisfied: bool,
) -> GenerationAdmission:
    """Candidate generation is allowed without release-grade reviewer infrastructure.

    The boundary here is legal/current execution readiness, truth and budget. Quality and
    high-assurance independent review are promotion/release concerns, not a prerequisite
    for learning from a candidate.
    """

    route_refs = _clean(route_evidence_refs)
    rights_refs = _clean(rights_evidence_refs)
    capability_refs = _clean(capability_evidence_refs)
    budget_refs = _clean(budget_evidence_refs)
    reasons: list[str] = []

    if not provider_id.strip():
        reasons.append("PROVIDER_ID_MISSING")
    if not provider_available:
        reasons.append("PROVIDER_UNAVAILABLE")
    if not commercial_use_admitted:
        reasons.append("COMMERCIAL_USE_NOT_ADMITTED")
    if not within_budget:
        reasons.append("SHOT_BUDGET_EXCEEDED")
    if not required_reference_rights_satisfied:
        reasons.append("REFERENCE_RIGHTS_OR_CONSENT_UNSATISFIED")
    if not route_refs:
        reasons.append("ROUTE_EVIDENCE_MISSING")
    if not rights_refs:
        reasons.append("RIGHTS_EVIDENCE_MISSING")
    if not capability_refs:
        reasons.append("CAPABILITY_EVIDENCE_MISSING")
    if not budget_refs:
        reasons.append("BUDGET_EVIDENCE_MISSING")

    if shot.truth_mode == "PRODUCT_TRUTH" and "REAL_OR_VERIFIED_PRODUCT_ASSET" not in shot.allowed_modes:
        reasons.append("PRODUCT_TRUTH_REQUIRES_REAL_OR_VERIFIED_PRODUCT_ROUTE")

    return GenerationAdmission(
        shot_id=shot.shot_id,
        lane=lane.upper(),
        provider_id=provider_id,
        route_evidence_refs=route_refs,
        rights_evidence_refs=rights_refs,
        capability_evidence_refs=capability_refs,
        budget_evidence_refs=budget_refs,
        admitted=not reasons,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True)
class TakeRecord:
    take_id: str
    shot_id: str
    artifact_ref: str
    artifact_digest: str
    provider_id: str
    generation_receipt_ref: str
    state: str = "CANDIDATE"
    parent_asset_refs: tuple[str, ...] = ()
    prompt_or_edit_digest: str = ""
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.state not in ASSET_STATES:
            raise ProductionAdmissionError(f"unsupported take state: {self.state}")
        for field_name in ("take_id", "shot_id", "artifact_ref", "artifact_digest", "provider_id", "generation_receipt_ref"):
            if not str(getattr(self, field_name)).strip():
                raise ProductionAdmissionError(f"take missing {field_name}")
        if self.cost_usd < 0:
            raise ProductionAdmissionError("take cost cannot be negative")


@dataclass(frozen=True)
class PromotionEvidence:
    quality_scores: Mapping[str, float]
    quality_evidence_refs: tuple[str, ...]
    continuity_evidence_refs: tuple[str, ...]
    rights_evidence_refs: tuple[str, ...]
    truth_evidence_refs: tuple[str, ...]
    independent_review_refs: tuple[str, ...] = ()
    technical_qa_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class PromotionDecision:
    take_id: str
    decision: str
    owner: str
    evidence_refs: tuple[str, ...]
    reasons: tuple[str, ...]


def evaluate_take_promotion(
    shot: ShotContract,
    take: TakeRecord,
    evidence: PromotionEvidence,
    *,
    decision_owner: str,
    independent_review_required: bool | None = None,
) -> PromotionDecision:
    if take.shot_id != shot.shot_id:
        raise ProductionAdmissionError("take/shot identity mismatch")
    if take.state not in {"CANDIDATE", "SHORTLISTED"}:
        raise ProductionAdmissionError("only candidate/shortlisted takes may be promoted")
    if not decision_owner.strip():
        raise ProductionAdmissionError("decision owner is required")

    reasons: list[str] = []
    for dimension, floor in shot.quality_targets.items():
        score = evidence.quality_scores.get(dimension)
        if score is None:
            reasons.append(f"QUALITY_UNMEASURED:{dimension}")
        elif float(score) < float(floor):
            reasons.append(f"QUALITY_BELOW_TARGET:{dimension}")

    if not evidence.quality_evidence_refs:
        reasons.append("QUALITY_EVIDENCE_MISSING")
    if shot.references and not evidence.continuity_evidence_refs:
        reasons.append("CONTINUITY_EVIDENCE_MISSING")
    if not evidence.rights_evidence_refs:
        reasons.append("RIGHTS_EVIDENCE_MISSING")
    if shot.truth_mode in {"EDITORIAL_REAL", "PRODUCT_TRUTH", "MIXED_DISCLOSED"} and not evidence.truth_evidence_refs:
        reasons.append("TRUTH_EVIDENCE_MISSING")

    needs_independent = (
        shot.risk in {"HIGH", "HERO", "BRAND_TRUTH"}
        if independent_review_required is None
        else independent_review_required
    )
    if needs_independent and not evidence.independent_review_refs:
        reasons.append("INDEPENDENT_REVIEW_REQUIRED")

    all_refs = tuple(
        dict.fromkeys(
            evidence.quality_evidence_refs
            + evidence.continuity_evidence_refs
            + evidence.rights_evidence_refs
            + evidence.truth_evidence_refs
            + evidence.independent_review_refs
            + evidence.technical_qa_refs
        )
    )
    return PromotionDecision(
        take_id=take.take_id,
        decision="PROMOTE" if not reasons else "REJECT",
        owner=decision_owner,
        evidence_refs=all_refs,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True)
class ReleaseEvidence:
    final_media_ref: str
    final_media_digest: str
    master_timeline_ref: str
    technical_qa_refs: tuple[str, ...]
    rights_refs: tuple[str, ...]
    claim_truth_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    disclosure_decision_ref: str
    platform_validation_refs: tuple[str, ...]
    release_owner: str


def admit_release(evidence: ReleaseEvidence) -> str:
    missing: list[str] = []
    for field_name in (
        "final_media_ref",
        "final_media_digest",
        "master_timeline_ref",
        "disclosure_decision_ref",
        "release_owner",
    ):
        if not str(getattr(evidence, field_name)).strip():
            missing.append(field_name)
    for field_name in (
        "technical_qa_refs",
        "rights_refs",
        "claim_truth_refs",
        "provenance_refs",
        "platform_validation_refs",
    ):
        if not getattr(evidence, field_name):
            missing.append(field_name)
    if missing:
        raise ProductionAdmissionError("release denied: missing " + ",".join(missing))
    return "RELEASE_ADMITTED"


@dataclass(frozen=True)
class PlatformVariant:
    variant_id: str
    platform: str
    master_timeline_ref: str
    source_episode_id: str
    hook_contract: str
    target_duration_seconds: float
    aspect_ratio: str
    packaging_candidate_refs: tuple[str, ...]
    metric_map: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(
            str(value).strip()
            for value in (
                self.variant_id,
                self.platform,
                self.master_timeline_ref,
                self.source_episode_id,
                self.hook_contract,
                self.aspect_ratio,
            )
        ):
            raise ProductionAdmissionError("platform variant identity/contract fields are required")
        if self.target_duration_seconds <= 0:
            raise ProductionAdmissionError("target_duration_seconds must be positive")
        if not self.packaging_candidate_refs:
            raise ProductionAdmissionError("platform variant requires packaging candidates")
