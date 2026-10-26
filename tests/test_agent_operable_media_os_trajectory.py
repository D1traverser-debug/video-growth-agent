from datetime import datetime, timezone

from video_growth_agent.continuity import (
    ContinuityLink,
    ContinuityRule,
    ContinuitySnapshot,
    assess_continuity,
)
from video_growth_agent.editorial_interchange import (
    EditorialRoundTripReceipt,
    EditorAdapterCapability,
    prepare_editorial_handoff,
    validate_roundtrip,
)
from video_growth_agent.editorial_planning import (
    BeatSpec,
    ClaimSpec,
    EditorialPlan,
    EpisodeIntent,
    ShotIntent,
    materialize_shot_contract,
)
from video_growth_agent.experiments import (
    ExperimentPlan,
    ExperimentVariant,
    VariantObservation,
    conclude_experiment,
)
from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
)
from video_growth_agent.model_registry import (
    EvidenceBoundModelRouter,
    ModelObservation,
    OperationProfile,
    QualityObservation,
    ShotRoutingRequest,
)
from video_growth_agent.plan_graph_bridge import register_editorial_plan_asset
from video_growth_agent.production_os import (
    PromotionEvidence,
    TakeRecord,
    admit_candidate_generation,
    evaluate_take_promotion,
)
from video_growth_agent.timeline import TimelineClip, TimelineSpec


def _quality(value: float):
    return QualityObservation(
        value=value,
        rubric_id="video-quality-v1",
        calibration_scope="edge-explainer-v1",
        uncertainty=0.1,
        evidence_class="OWNER_BENCHMARK",
        evidence_refs=("benchmark://edge-explainer",),
    )


def test_current_agent_can_move_from_editorial_intent_to_roundtrip_and_learning_without_hidden_state():
    # Editorial reasoning is durable before provider choice.
    intent = EpisodeIntent(
        episode_id="EP-EDGE-01",
        series_id="engineer-world",
        audience_contract="Explain the mechanism without faking certainty",
        editorial_question="Why is AI inference moving toward the edge?",
        primary_platform="BILIBILI",
        target_duration_seconds=420,
        evidence_refs=("research://edge-inference",),
        desired_outcomes=("qualified_watch_time",),
        success_metric_semantics={"qualified_watch_time": "target-audience watch minutes"},
    )
    claim = ClaimSpec(
        claim_id="C1",
        statement="Moving inference closer to the device can reduce some network round trips.",
        claim_class="FACT",
        risk="MEDIUM",
        evidence_refs=("source://latency-study",),
    )
    beat = BeatSpec(
        beat_id="B1",
        episode_id=intent.episode_id,
        narrative_job="make the latency mechanism visible",
        audience_function="replace abstraction with a causal picture",
        target_duration_seconds=30,
        claim_ids=(claim.claim_id,),
    )
    shots = (
        ShotIntent(
            shot_id="S1",
            beat_id="B1",
            visual_job="establish the same device and user context",
            target_duration_seconds=5,
            truth_mode="SYNTHETIC",
            risk="LOW",
            source_claim_ids=(claim.claim_id,),
            allowed_production_modes=frozenset({"I2V"}),
            continuity_dimensions=("device_identity",),
            value_vector={"clarity": 3.5},
        ),
        ShotIntent(
            shot_id="S2",
            beat_id="B1",
            visual_job="show the round trip collapsing toward the device",
            target_duration_seconds=5,
            truth_mode="SYNTHETIC",
            risk="LOW",
            source_claim_ids=(claim.claim_id,),
            allowed_production_modes=frozenset({"I2V"}),
            continuity_dimensions=("device_identity",),
            value_vector={"clarity": 4.5, "retention": 3.5},
        ),
    )
    plan = EditorialPlan(intent, (claim,), (beat,), shots, "v1")

    # The exact plan version becomes an upstream MediaGraph asset.
    graph = MediaGraph()
    graph.add_context(ContextRecord("PROGRAM", "PROGRAM"))
    graph.add_context(ContextRecord(intent.episode_id, "EPISODE", "PROGRAM"))
    plan_ref = register_editorial_plan_asset(
        graph,
        plan=plan,
        context_id=intent.episode_id,
        uri="repo://episodes/edge/editorial-plan-v1.json",
        provenance_refs=("research://edge-inference",),
    )

    shot = materialize_shot_contract(
        plan,
        shot_id="S2",
        sequence_id="SEQ1",
        required_capabilities=frozenset({"I2V"}),
        quality_targets={"identity": 3.5, "motion": 3.0},
        continuity_ref="continuity://S1-S2",
        budget_usd=4.0,
    )
    assert shot.editorial_plan_ref == plan.plan_ref
    assert shot.source_claim_ids == ("C1",)

    # Provider choice is operation-specific and calibrated, not a remembered vendor default.
    profile = OperationProfile(
        profile_id="i2v-1080-5s",
        mode="I2V",
        capabilities=frozenset({"I2V"}),
        allowed_durations_seconds=frozenset({5.0}),
        resolutions=frozenset({"1080p"}),
    )
    engine = ModelObservation(
        engine_id="engine-a",
        observed_at="2026-10-15T00:00:00Z",
        capabilities=frozenset({"I2V"}),
        quality_scores={},
        quality_observations={"identity": _quality(4.4), "motion": _quality(4.2)},
        operation_profiles=(profile,),
        available=True,
        commercial_use_allowed=True,
        provenance_supported=True,
        output_cost_usd_per_second=0.25,
        quality_evidence_refs=("benchmark://edge-explainer",),
        pricing_evidence_refs=("pricing://engine-a",),
        terms_evidence_refs=("terms://engine-a",),
        availability_evidence_refs=("availability://engine-a",),
    )
    routing = EvidenceBoundModelRouter().route(
        ShotRoutingRequest(
            shot_id="S2",
            lane="PRODUCTION",
            risk="LOW",
            duration_seconds=5,
            operation_mode="I2V",
            require_operation_profile=True,
            required_capabilities=frozenset({"I2V"}),
            minimum_quality={"identity": 3.5, "motion": 3.0},
            quality_priorities=("identity", "motion"),
            quality_rubric_id="video-quality-v1",
            calibration_scope="edge-explainer-v1",
            required_resolution="1080p",
            max_cost_usd=4.0,
            require_provenance=True,
        ),
        [engine],
        now=datetime(2026, 10, 15, tzinfo=timezone.utc),
    )
    assert routing.selected_engine_id == "engine-a"

    admission = admit_candidate_generation(
        shot,
        lane="PRODUCTION",
        provider_id=routing.selected_engine_id or "",
        route_evidence_refs=("route://S2-v1",),
        rights_evidence_refs=("rights://episode",),
        capability_evidence_refs=("capability://engine-a/i2v-1080-5s",),
        budget_evidence_refs=("budget://S2",),
        provider_available=True,
        commercial_use_admitted=True,
        within_budget=True,
        required_reference_rights_satisfied=True,
    )
    assert admission.admitted is True

    # Continuity is evaluated as an explicit dimension, not prompt-memory similarity.
    continuity = assess_continuity(
        ContinuitySnapshot("S1", {"device_identity": "device-A"}, evidence_refs=("take://S1",)),
        ContinuitySnapshot("S2", {"device_identity": "device-A"}, evidence_refs=("take://S2",)),
        ContinuityLink(
            "S1",
            "S2",
            (ContinuityRule("device_identity", "HARD", "PRESERVE", reason="same causal demonstration"),),
            rationale_refs=("editorial-plan://EP-EDGE-01@v1",),
        ),
        evidence_refs=("continuity-review://S1-S2",),
    )
    assert continuity.hard_pass is True

    take = TakeRecord(
        take_id="S2-T1",
        shot_id="S2",
        artifact_ref="asset://S2-T1.mp4",
        artifact_digest="sha256:s2-t1",
        provider_id="engine-a",
        generation_receipt_ref="generation://S2-T1",
        cost_usd=1.25,
    )
    promotion = evaluate_take_promotion(
        shot,
        take,
        PromotionEvidence(
            quality_scores={"identity": 4.4, "motion": 4.2},
            quality_evidence_refs=("quality-review://S2-T1",),
            continuity_evidence_refs=("continuity-review://S1-S2",),
            rights_evidence_refs=("rights://episode",),
            truth_evidence_refs=(),
            technical_qa_refs=("qa://mechanical-check-S2-T1",),
        ),
        decision_owner="director",
    )
    assert promotion.decision == "PROMOTE"

    # Promotion enters the same graph and preserves plan lineage for later invalidation.
    take_ref = AssetRef("take:S2-T1", "v1")
    graph.add_asset(
        AssetVersion(
            take_ref,
            intent.episode_id,
            "VIDEO",
            take.artifact_ref,
            take.artifact_digest,
            derived_from=(plan_ref,),
            rights_refs=("rights://episode",),
            provenance_refs=(take.generation_receipt_ref,),
        )
    )
    graph.add_evidence(
        EvidenceRecord(
            "EV-S2-T1",
            "ASSET",
            take_ref.key(),
            "promotion_review",
            promotion.evidence_refs,
            "2026-10-15T00:10:00Z",
        )
    )
    graph.add_decision(
        DecisionRecord(
            "D-S2-T1",
            "PROMOTION",
            promotion.owner,
            (take_ref.key(),),
            ("criteria://S2",),
            ("EV-S2-T1",),
            promotion.decision,
            "2026-10-15T00:11:00Z",
        )
    )
    graph.promote_asset(take_ref, decision_id="D-S2-T1")

    # External editing is an identity-bound roundtrip over the canonical timeline.
    timeline = TimelineSpec(
        "EP-EDGE-01-MASTER",
        "v1",
        intent.episode_id,
        (TimelineClip("CLIP-S2", take_ref, "V1", 0, 0, 5),),
    )
    adapter = EditorAdapterCapability(
        "nle-adapter",
        "2026-10-15T00:12:00Z",
        True,
        frozenset({"otio"}),
        frozenset({"otio"}),
        True,
        ("capability://nle",),
    )
    handoff = prepare_editorial_handoff(
        timeline=timeline,
        graph=graph,
        adapter=adapter,
        handoff_id="H-EDGE-1",
        interchange_format="otio",
        purpose="editorial pacing pass",
        source_refs=("timeline://EP-EDGE-01-MASTER@v1",),
    )
    receipt = EditorialRoundTripReceipt(
        "H-EDGE-1",
        "nle-adapter",
        "v1",
        "timeline-return://EP-EDGE-01-MASTER@v2",
        "sha256:timeline-v2",
        "otio",
        "changes://pacing-pass",
        ("execution://nle-roundtrip",),
    )
    assert validate_roundtrip(handoff=handoff, adapter=adapter, receipt=receipt) == "ROUNDTRIP_VERIFIED"

    # Learning is pre-registered; an ambiguous result stays ambiguous.
    experiment = ExperimentPlan(
        experiment_id="EXP-EDGE-COVER-1",
        context_id=intent.episode_id,
        hypothesis="Cover B improves qualified watch time",
        variants=(
            ExperimentVariant("A", "cover://A", {"cover": "baseline"}),
            ExperimentVariant("B", "cover://B", {"cover": "mechanism-closeup"}),
        ),
        primary_metric="qualified_watch_time",
        metric_semantics={"qualified_watch_time": "target-audience watch minutes from experiment traffic"},
        guardrail_metrics=(),
        attribution_mode="SINGLE_VARIABLE_CAUSAL",
        minimum_observation_rule="platform experiment completion",
        stop_rules=("platform experiment concludes",),
        evidence_refs=("experiment-method://platform",),
    )
    conclusion = conclude_experiment(
        experiment,
        observations=(
            VariantObservation("A", {"qualified_watch_time": 100.0}, 1000, ("receipt://A",)),
            VariantObservation("B", {"qualified_watch_time": 101.0}, 1000, ("receipt://B",)),
        ),
        outcome="NO_CLEAR_WINNER",
        winning_variant_id=None,
        evidence_refs=("experiment-result://edge-cover-1",),
        inference="No clear winner; do not promote a cover rule.",
    )
    assert conclusion.winning_variant_id is None

    # A later editorial change can mechanically stale the promoted take via plan lineage.
    affected = graph.invalidate_downstream(plan_ref)
    assert take_ref in affected
    assert graph.asset_state(take_ref) == "STALE"
