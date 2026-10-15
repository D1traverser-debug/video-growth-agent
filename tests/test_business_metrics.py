from video_growth_agent.business_metrics import (
    CommercialOutcome,
    EpisodeOutcomeReceipt,
    PlatformPerformanceReceipt,
    ProductionEconomics,
)


def test_outcome_vector_does_not_collapse_business_into_one_score():
    platform = PlatformPerformanceReceipt(
        platform="BILIBILI",
        variant_id="ep1-master",
        raw_metrics={"play": 1000.0, "follow_conversion": 0.03},
        metric_semantics={
            "play": "platform_reported_play_count",
            "follow_conversion": "platform_reported_play_to_follow_ratio",
        },
        evidence_refs=("platform://receipt",),
        observed_at="2026-10-15T00:00:00Z",
    )
    production = ProductionEconomics(
        published_minutes=8,
        cash_cost_usd=80,
        creator_minutes=240,
        generated_video_seconds=180,
        premium_video_seconds=60,
        generation_attempts=30,
        rejected_generation_attempts=9,
        accepted_generated_assets=21,
        reused_asset_uses=8,
    )
    commercial = CommercialOutcome(
        revenue_usd=500,
        direct_cost_usd=100,
        rights_revenue_usd=50,
        repeat_buy_signal="POSITIVE",
        brand_outcome_metrics={"brand_lift": 0.08},
        evidence_refs=("commercial://receipt",),
    )
    outcome = EpisodeOutcomeReceipt(
        episode_id="EP1",
        platform_receipts=(platform,),
        production=production,
        commercial=commercial,
        qualitative_evidence_refs=("comments://sample",),
    )
    vector = outcome.objective_vector()
    assert "score" not in vector
    assert vector["production"]["cost_per_published_minute"] == 10
    assert vector["commercial"]["gross_margin_usd"] == 450
