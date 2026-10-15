import pytest

from video_growth_agent.production_os import (
    GenerationAdmission,
    PlatformVariant,
    ProductionAdmissionError,
    PromotionEvidence,
    ReferenceBinding,
    ReleaseEvidence,
    ShotContract,
    TakeRecord,
    admit_candidate_generation,
    admit_release,
    evaluate_take_promotion,
)


def _shot(**overrides):
    base = dict(
        shot_id="S001",
        sequence_id="SEQ01",
        narrative_job="Reveal the invisible compute bottleneck",
        duration_seconds=5,
        truth_mode="SYNTHETIC",
        risk="HERO",
        allowed_modes=frozenset({"I2V", "STILL_MOTION"}),
        required_capabilities=frozenset({"I2V"}),
        quality_targets={"identity": 4.0, "motion": 3.5},
        must_have=("clear focal subject",),
        must_not_have=("unreadable labels",),
        graceful_degradation=("I2V", "STILL_MOTION"),
        stop_conditions=("three rejected takes",),
        budget_usd=12.0,
    )
    base.update(overrides)
    return ShotContract(**base)


def _take(**overrides):
    base = dict(
        take_id="S001-T01",
        shot_id="S001",
        artifact_ref="asset://S001-T01.mp4",
        artifact_digest="sha256:abc",
        provider_id="provider-a/model-x",
        generation_receipt_ref="receipt://gen-1",
        state="CANDIDATE",
        cost_usd=2.0,
    )
    base.update(overrides)
    return TakeRecord(**base)


def test_exploration_candidate_does_not_require_release_grade_blind_review():
    admission = admit_candidate_generation(
        _shot(),
        lane="EXPLORATION",
        provider_id="provider-a/model-x",
        route_evidence_refs=["route://1"],
        rights_evidence_refs=["rights://1"],
        capability_evidence_refs=["cap://1"],
        budget_evidence_refs=["budget://1"],
        provider_available=True,
        commercial_use_admitted=True,
        within_budget=True,
        required_reference_rights_satisfied=True,
    )
    assert isinstance(admission, GenerationAdmission)
    assert admission.admitted is True


def test_product_truth_requires_verified_real_route_and_reference():
    ref = ReferenceBinding(
        asset_id="product-photo",
        version_id="v1",
        digest="sha256:product",
        role="PRODUCT_TRUTH_REFERENCE",
        rights_ref="rights://brand",
    )
    shot = _shot(
        truth_mode="PRODUCT_TRUTH",
        risk="BRAND_TRUTH",
        references=(ref,),
        allowed_modes=frozenset({"I2V"}),
    )
    admission = admit_candidate_generation(
        shot,
        lane="PRODUCTION",
        provider_id="provider",
        route_evidence_refs=["route://1"],
        rights_evidence_refs=["rights://1"],
        capability_evidence_refs=["cap://1"],
        budget_evidence_refs=["budget://1"],
        provider_available=True,
        commercial_use_admitted=True,
        within_budget=True,
        required_reference_rights_satisfied=True,
    )
    assert admission.admitted is False
    assert "PRODUCT_TRUTH_REQUIRES_REAL_OR_VERIFIED_PRODUCT_ROUTE" in admission.reasons


def test_hero_take_cannot_promote_without_independent_review():
    evidence = PromotionEvidence(
        quality_scores={"identity": 4.5, "motion": 4.2},
        quality_evidence_refs=("quality://1",),
        continuity_evidence_refs=(),
        rights_evidence_refs=("rights://1",),
        truth_evidence_refs=(),
    )
    decision = evaluate_take_promotion(_shot(), _take(), evidence, decision_owner="creative_director")
    assert decision.decision == "REJECT"
    assert "INDEPENDENT_REVIEW_REQUIRED" in decision.reasons


def test_low_risk_take_can_promote_without_independent_review_when_quality_passes():
    shot = _shot(risk="LOW")
    evidence = PromotionEvidence(
        quality_scores={"identity": 4.5, "motion": 4.2},
        quality_evidence_refs=("quality://1",),
        continuity_evidence_refs=(),
        rights_evidence_refs=("rights://1",),
        truth_evidence_refs=(),
    )
    decision = evaluate_take_promotion(shot, _take(), evidence, decision_owner="director")
    assert decision.decision == "PROMOTE"


def test_release_is_separate_fail_closed_boundary():
    good = ReleaseEvidence(
        final_media_ref="asset://final.mp4",
        final_media_digest="sha256:final",
        master_timeline_ref="timeline://master-v7",
        technical_qa_refs=("qa://tech",),
        rights_refs=("rights://manifest",),
        claim_truth_refs=("truth://claims",),
        provenance_refs=("prov://manifest",),
        disclosure_decision_ref="disclosure://youtube-ai-yes",
        platform_validation_refs=("platform://bilibili-master",),
        release_owner="showrunner",
    )
    assert admit_release(good) == "RELEASE_ADMITTED"

    bad = ReleaseEvidence(
        final_media_ref="asset://final.mp4",
        final_media_digest="sha256:final",
        master_timeline_ref="timeline://master-v7",
        technical_qa_refs=(),
        rights_refs=("rights://manifest",),
        claim_truth_refs=("truth://claims",),
        provenance_refs=("prov://manifest",),
        disclosure_decision_ref="disclosure://1",
        platform_validation_refs=("platform://1",),
        release_owner="showrunner",
    )
    with pytest.raises(ProductionAdmissionError):
        admit_release(bad)


def test_platform_variant_requires_authored_packaging_candidates():
    variant = PlatformVariant(
        variant_id="ep1-douyin-v1",
        platform="DOUYIN",
        master_timeline_ref="timeline://ep1-master",
        source_episode_id="EP1",
        hook_contract="Resolve the mechanism promise within the opening seconds",
        target_duration_seconds=75,
        aspect_ratio="9:16",
        packaging_candidate_refs=("cover://a", "title://a"),
        metric_map={"short_early_exit": "provider_defined_early_exit"},
    )
    assert variant.platform == "DOUYIN"
