import pytest

from video_growth_agent.business_objects import (
    BusinessObjectError,
    CommercialFit,
    CommercialOfferCandidate,
    ContentPortfolioItem,
    DistinctiveAssetObservation,
    RightsPackage,
)


def test_portfolio_item_requires_real_topic_evidence_not_view_folklore():
    item = ContentPortfolioItem(
        item_id="topic-1",
        series_id="engineer-explains-world",
        audience_hypothesis="AI/chip/business audience values mechanism clarity",
        editorial_question="Where does AI datacenter money actually go?",
        strategic_fit="technology x business core pillar",
        topic_evidence_refs=("research://demand", "account://positioning"),
        production_complexity_class="MEDIUM",
        commercial_adjacency_categories=("cloud", "hardware"),
        distinctive_asset_opportunities=("system-map visual grammar",),
    )
    assert item.status == "CANDIDATE"


def test_distinctive_asset_observation_is_evidence_bound():
    observation = DistinctiveAssetObservation(
        asset_id="observer-face",
        asset_version="h1-v1",
        observation_scope="thumbnail experiment",
        metrics={"recognition_rate": 0.62, "ctr_delta": 0.08},
        evidence_refs=("experiment://thumbnail-12",),
    )
    assert observation.metrics["recognition_rate"] == 0.62


def test_commercial_fit_cannot_disable_editorial_independence():
    with pytest.raises(BusinessObjectError, match="editorial independence"):
        CommercialFit(
            fit_id="fit-1",
            context_id="series-1",
            advertiser_categories=("cloud",),
            integration_surfaces=("real product as case/tool",),
            product_truth_requirements=("verified UI footage",),
            prohibited_integration_forms=("guaranteed claim",),
            measurement_plan_refs=("measurement://plan",),
            evidence_refs=("research://advertiser-map",),
            editorial_independence_required=False,
        )


def test_expanded_rights_need_evidence_and_priced_offer_needs_pricing_evidence():
    with pytest.raises(BusinessObjectError, match="expanded commercial rights"):
        RightsPackage(
            package_id="rights-1",
            context_id="episode-1",
            organic_post=True,
            paid_media=True,
            duration_days=30,
        )

    rights = RightsPackage(
        package_id="rights-1",
        context_id="episode-1",
        organic_post=True,
        paid_media=True,
        cutdowns=True,
        duration_days=30,
        territories=("CN",),
        evidence_refs=("contract://rights",),
    )
    assert rights.paid_media is True

    offer = CommercialOfferCandidate(
        offer_id="offer-1",
        fit_id="fit-1",
        rights_package_id=rights.package_id,
        deliverables=("long-form integration", "short cutdown"),
        production_uplift_cost_usd=100,
        fee_usd=1000,
        pricing_evidence_refs=("pricing://benchmark", "cost://episode",),
    )
    assert offer.contribution_before_base_production_cost == 900
