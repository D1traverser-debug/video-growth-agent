import pytest

from video_growth_agent.editorial_interchange import (
    EditorialRoundTripReceipt,
    EditorAdapterCapability,
    InterchangeError,
    prepare_editorial_handoff,
    validate_roundtrip,
)
from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
)
from video_growth_agent.timeline import TimelineClip, TimelineSpec


def _graph_and_timeline():
    graph = MediaGraph()
    graph.add_context(ContextRecord("P", "PROGRAM"))
    graph.add_context(ContextRecord("E", "EPISODE", "P"))
    ref = AssetRef("clip", "v1")
    graph.add_asset(AssetVersion(ref, "E", "VIDEO", "file://clip.mp4", "digest-1"))
    graph.add_evidence(EvidenceRecord("EV", "ASSET", ref.key(), "quality_review", ("review://1",), "2026-10-15T00:00:00Z"))
    graph.add_decision(DecisionRecord("D", "PROMOTION", "director", (ref.key(),), ("criteria://shot",), ("EV",), "PROMOTE", "2026-10-15T00:00:00Z"))
    graph.promote_asset(ref, decision_id="D")
    timeline = TimelineSpec("T", "v1", "E", (TimelineClip("C", ref, "V1", 0, 0, 5),))
    return graph, timeline


def test_handoff_requires_current_executable_adapter():
    graph, timeline = _graph_and_timeline()
    adapter = EditorAdapterCapability("editor", "2026-10-15T00:00:00Z", False, frozenset({"otio"}), frozenset({"otio"}), True, ("cap://editor",))
    with pytest.raises(InterchangeError, match="not executable"):
        prepare_editorial_handoff(
            timeline=timeline,
            graph=graph,
            adapter=adapter,
            handoff_id="H1",
            interchange_format="otio",
            purpose="edit",
            source_refs=("timeline://v1",),
        )


def test_roundtrip_binds_exact_timeline_version():
    graph, timeline = _graph_and_timeline()
    adapter = EditorAdapterCapability("editor", "2026-10-15T00:00:00Z", True, frozenset({"otio"}), frozenset({"otio", "premiere"}), True, ("cap://editor",))
    handoff = prepare_editorial_handoff(
        timeline=timeline,
        graph=graph,
        adapter=adapter,
        handoff_id="H1",
        interchange_format="otio",
        purpose="external edit",
        source_refs=("timeline://v1",),
    )
    bad = EditorialRoundTripReceipt("H1", "editor", "wrong", "return://1", "digest-return", "premiere", "change://1", ("exec://1",))
    with pytest.raises(InterchangeError, match="wrong timeline version"):
        validate_roundtrip(handoff=handoff, adapter=adapter, receipt=bad)

    good = EditorialRoundTripReceipt("H1", "editor", "v1", "return://2", "digest-return-2", "premiere", "change://2", ("exec://2",))
    assert validate_roundtrip(handoff=handoff, adapter=adapter, receipt=good) == "ROUNDTRIP_VERIFIED"
