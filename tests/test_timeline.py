import pytest

from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
)
from video_growth_agent.timeline import (
    TimelineClip,
    TimelineError,
    TimelineSpec,
    assert_platform_variant_lineage,
)


def _graph_with_promoted_asset() -> tuple[MediaGraph, AssetRef]:
    graph = MediaGraph()
    graph.add_context(ContextRecord("program", "PROGRAM"))
    graph.add_context(ContextRecord("episode", "EPISODE", "program"))
    ref = AssetRef("take", "v1")
    graph.add_asset(AssetVersion(ref, "episode", "VIDEO", "asset://take", "sha256:take"))
    graph.add_evidence(EvidenceRecord("ev", "ASSET", ref.key(), "REVIEW", ("review://take",), "2026-10-15T00:00:00Z"))
    graph.add_decision(DecisionRecord("dec", "PROMOTION", "director", (ref.key(),), ("criteria://shot",), ("ev",), "PROMOTE", "2026-10-15T00:01:00Z"))
    graph.promote_asset(ref, decision_id="dec")
    return graph, ref


def test_master_timeline_requires_promoted_assets():
    graph, ref = _graph_with_promoted_asset()
    timeline = TimelineSpec(
        timeline_id="ep-master",
        version_id="v1",
        context_id="episode",
        clips=(TimelineClip("c1", ref, "V1", 0, 0, 5),),
    )
    timeline.validate_against_graph(graph)
    assert timeline.duration_seconds == 5


def test_candidate_asset_cannot_silently_enter_master_timeline():
    graph = MediaGraph()
    graph.add_context(ContextRecord("program", "PROGRAM"))
    graph.add_context(ContextRecord("episode", "EPISODE", "program"))
    ref = AssetRef("candidate", "v1")
    graph.add_asset(AssetVersion(ref, "episode", "VIDEO", "asset://candidate", "sha256:candidate"))
    timeline = TimelineSpec("master", "v1", "episode", (TimelineClip("c1", ref, "V1", 0, 0, 5),))
    with pytest.raises(TimelineError, match="not promoted"):
        timeline.validate_against_graph(graph)


def test_platform_variant_is_non_destructive_authored_derivative():
    graph, ref = _graph_with_promoted_asset()
    master = TimelineSpec("ep-master", "v1", "episode", (TimelineClip("c1", ref, "V1", 0, 0, 5),))
    variant = master.derive(
        version_id="douyin-v1",
        edit_reason="rewrite opening and pacing for short-form feed consumption",
    )
    assert master.version_id == "v1"
    assert variant.version_id == "douyin-v1"
    assert variant.derived_from_version == "v1"
    assert_platform_variant_lineage(master=master, variant=variant, platform="DOUYIN")
