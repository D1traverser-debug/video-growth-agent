from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class BusinessObjectError(ValueError):
    pass


@dataclass(frozen=True)
class ContentPortfolioItem:
    item_id: str
    series_id: str
    audience_hypothesis: str
    editorial_question: str
    strategic_fit: str
    topic_evidence_refs: tuple[str, ...]
    production_complexity_class: str
    commercial_adjacency_categories: tuple[str, ...] = ()
    distinctive_asset_opportunities: tuple[str, ...] = ()
    status: str = "CANDIDATE"

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.item_id,
                self.series_id,
                self.audience_hypothesis,
                self.editorial_question,
                self.strategic_fit,
                self.production_complexity_class,
                self.status,
            )
        ):
            raise BusinessObjectError("portfolio identity/hypothesis/question/fit/complexity/status are required")
        if not self.topic_evidence_refs:
            raise BusinessObjectError("portfolio item requires topic evidence")


@dataclass(frozen=True)
class DistinctiveAssetObservation:
    asset_id: str
    asset_version: str
    observation_scope: str
    metrics: Mapping[str, float]
    evidence_refs: tuple[str, ...]
    qualitative_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.asset_id.strip() or not self.asset_version.strip() or not self.observation_scope.strip():
            raise BusinessObjectError("distinctive asset identity/version/scope are required")
        if not self.evidence_refs and not self.qualitative_refs:
            raise BusinessObjectError("distinctive asset observation requires evidence")
        if any(float(value) < 0 for value in self.metrics.values()):
            raise BusinessObjectError("distinctive asset metrics cannot be negative")


@dataclass(frozen=True)
class CommercialFit:
    fit_id: str
    context_id: str
    advertiser_categories: tuple[str, ...]
    integration_surfaces: tuple[str, ...]
    product_truth_requirements: tuple[str, ...]
    prohibited_integration_forms: tuple[str, ...]
    measurement_plan_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    editorial_independence_required: bool = True

    def __post_init__(self) -> None:
        if not self.fit_id.strip() or not self.context_id.strip():
            raise BusinessObjectError("commercial fit identity/context are required")
        if not self.advertiser_categories:
            raise BusinessObjectError("commercial fit requires advertiser categories")
        if not self.integration_surfaces:
            raise BusinessObjectError("commercial fit requires integration surfaces")
        if not self.evidence_refs:
            raise BusinessObjectError("commercial fit requires evidence")
        if not self.editorial_independence_required:
            raise BusinessObjectError("commercial fit cannot disable editorial independence")


@dataclass(frozen=True)
class RightsPackage:
    package_id: str
    context_id: str
    organic_post: bool
    paid_media: bool = False
    whitelisting: bool = False
    cutdowns: bool = False
    duration_days: int | None = None
    territories: tuple[str, ...] = ()
    exclusivity_categories: tuple[str, ...] = ()
    usage_constraints: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.package_id.strip() or not self.context_id.strip():
            raise BusinessObjectError("rights package identity/context are required")
        if self.duration_days is not None and self.duration_days <= 0:
            raise BusinessObjectError("rights duration must be positive")
        if (self.paid_media or self.whitelisting or self.cutdowns or self.exclusivity_categories) and not self.evidence_refs:
            raise BusinessObjectError("expanded commercial rights require evidence refs")


@dataclass(frozen=True)
class CommercialOfferCandidate:
    offer_id: str
    fit_id: str
    rights_package_id: str
    deliverables: tuple[str, ...]
    production_uplift_cost_usd: float
    fee_usd: float | None
    pricing_evidence_refs: tuple[str, ...]
    status: str = "CANDIDATE"

    def __post_init__(self) -> None:
        if not self.offer_id.strip() or not self.fit_id.strip() or not self.rights_package_id.strip():
            raise BusinessObjectError("offer/fit/rights identities are required")
        if not self.deliverables:
            raise BusinessObjectError("offer requires deliverables")
        if self.production_uplift_cost_usd < 0:
            raise BusinessObjectError("production uplift cost cannot be negative")
        if self.fee_usd is not None and self.fee_usd < 0:
            raise BusinessObjectError("fee cannot be negative")
        if self.fee_usd is not None and not self.pricing_evidence_refs:
            raise BusinessObjectError("priced offer requires pricing evidence")

    @property
    def contribution_before_base_production_cost(self) -> float | None:
        if self.fee_usd is None:
            return None
        return self.fee_usd - self.production_uplift_cost_usd


@dataclass(frozen=True)
class BusinessHypothesisDecision:
    decision_id: str
    subject_ids: tuple[str, ...]
    owner: str
    decision: str
    evidence_refs: tuple[str, ...]
    counterexample_refs: tuple[str, ...] = ()
    followup_measurement_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.decision_id.strip() or not self.owner.strip() or not self.decision.strip():
            raise BusinessObjectError("business decision identity/owner/decision are required")
        if not self.subject_ids:
            raise BusinessObjectError("business decision requires subjects")
        if not self.evidence_refs:
            raise BusinessObjectError("business decision requires evidence")
