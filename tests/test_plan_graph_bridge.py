from video_growth_agent.editorial_planning import BeatSpec, EditorialPlan, EpisodeIntent, ShotIntent
from video_growth_agent.media_graph import AssetVersion, ContextRecord, MediaGraph
from video_growth_agent.plan_graph_bridge import register_editorial_plan_asset


def _plan(version="v1"):
    intent = EpisodeIntent(
        "E1", "S1", "Explain clearly", "Why does this system behave this way?", "BILIBILI", 300,
        ("research://topic",), ("qualified_watch_time",), {"qualified_watch_time": "target audience minutes"},
    )
    beat = BeatSpec("B1", "E1", "explain mechanism", "understand", 30)
    shot = ShotIntent("SH1", "B1", "visualize mechanism", 5, "SYNTHETIC", "LOW", (), frozenset({"I2V"}))
    return EditorialPlan(intent, (), (beat,), (shot,), version)


def test_plan_version_is_a_first_class_media_graph_asset_and_stales_downstream():
    graph = MediaGraph()
    graph.add_context(ContextRecord("P", "PROGRAM"))
    graph.add_context(ContextRecord("E1", "EPISODE", "P"))
    plan_ref = register_editorial_plan_asset(graph, plan=_plan(), context_id="E1", uri="repo://episode/plan-v1.json")
    generated_ref = plan_ref.__class__("shot-output", "v1")
    graph.add_asset(
        AssetVersion(
            generated_ref,
            "E1",
            "VIDEO",
            "file://shot.mp4",
            "digest-shot",
            derived_from=(plan_ref,),
        )
    )
    affected = graph.invalidate_downstream(plan_ref)
    assert generated_ref in affected
    assert graph.asset_state(generated_ref) == "STALE"
