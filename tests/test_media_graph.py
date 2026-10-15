import json
from pathlib import Path

import pytest

from video_growth_agent.media_graph import (
    AssetRef,
    AssetVersion,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
    MediaGraphError,
    MediaGraphStore,
    TaskRecord,
)


def _base_graph() -> MediaGraph:
    graph = MediaGraph()
    graph.add_context(ContextRecord("program", "PROGRAM"))
    graph.add_context(ContextRecord("episode-1", "EPISODE", "program"))
    graph.add_context(ContextRecord("seq-1", "SEQUENCE", "episode-1"))
    graph.add_context(ContextRecord("shot-1", "SHOT", "seq-1"))
    return graph


def test_asset_versions_are_append_only_and_promotion_is_decision_bound():
    graph = _base_graph()
    v1 = AssetVersion(
        ref=AssetRef("character-canon", "v1"),
        context_id="program",
        kind="CHARACTER_CANON",
        uri="asset://canon-v1",
        digest="sha256:v1",
        rights_refs=("rights://owner",),
    )
    graph.add_asset(v1)
    graph.add_evidence(
        EvidenceRecord(
            evidence_id="ev-1",
            subject_type="ASSET",
            subject_id=v1.ref.key(),
            action="CANON_REVIEW",
            refs=("review://canon-v1",),
            observed_at="2026-10-15T00:00:00Z",
        )
    )
    graph.add_decision(
        DecisionRecord(
            decision_id="dec-1",
            decision_type="ASSET_PROMOTION",
            owner="creative_director",
            subject_refs=(v1.ref.key(),),
            criteria_refs=("criteria://canon",),
            evidence_ids=("ev-1",),
            result="PROMOTE",
            decided_at="2026-10-15T00:01:00Z",
        )
    )
    graph.promote_asset(v1.ref, decision_id="dec-1")
    assert graph.asset_state(v1.ref) == "PROMOTED"
    assert graph.current_promoted("character-canon").ref == v1.ref

    with pytest.raises(MediaGraphError, match="already exists"):
        graph.add_asset(v1)


def test_new_promoted_version_stales_old_pointer_without_deleting_history():
    graph = _base_graph()
    for version in ("v1", "v2"):
        graph.add_asset(
            AssetVersion(
                ref=AssetRef("canon", version),
                context_id="program",
                kind="CANON",
                uri=f"asset://{version}",
                digest=f"sha256:{version}",
            )
        )
        graph.add_evidence(
            EvidenceRecord(
                evidence_id=f"ev-{version}",
                subject_type="ASSET",
                subject_id=f"canon@{version}",
                action="REVIEW",
                refs=(f"review://{version}",),
                observed_at="2026-10-15T00:00:00Z",
            )
        )
        graph.add_decision(
            DecisionRecord(
                decision_id=f"dec-{version}",
                decision_type="PROMOTION",
                owner="creative_director",
                subject_refs=(f"canon@{version}",),
                criteria_refs=("criteria://canon",),
                evidence_ids=(f"ev-{version}",),
                result="PROMOTE",
                decided_at="2026-10-15T00:01:00Z",
            )
        )
        graph.promote_asset(AssetRef("canon", version), decision_id=f"dec-{version}")

    assert graph.current_promoted("canon").ref == AssetRef("canon", "v2")
    assert graph.asset_state(AssetRef("canon", "v1")) == "STALE"
    assert AssetRef("canon", "v1") in graph.assets


def test_upstream_change_computes_and_applies_only_downstream_invalidation():
    graph = _base_graph()
    canon = AssetRef("canon", "v1")
    frame = AssetRef("keyframe", "v1")
    take = AssetRef("take", "v1")
    unrelated = AssetRef("research", "v1")
    graph.add_asset(AssetVersion(canon, "program", "CANON", "asset://canon", "sha256:canon"))
    graph.add_asset(AssetVersion(frame, "shot-1", "IMAGE", "asset://frame", "sha256:frame", derived_from=(canon,)))
    graph.add_asset(AssetVersion(take, "shot-1", "VIDEO", "asset://take", "sha256:take", derived_from=(frame,)))
    graph.add_asset(AssetVersion(unrelated, "episode-1", "DOCUMENT", "asset://research", "sha256:research"))

    affected = set(graph.invalidate_downstream(canon))
    assert affected == {frame, take}
    assert graph.asset_state(frame) == "STALE"
    assert graph.asset_state(take) == "STALE"
    assert graph.asset_state(unrelated) == "CANDIDATE"


def test_task_dependencies_and_asset_inputs_must_exist():
    graph = _base_graph()
    source = AssetRef("source", "v1")
    output = AssetRef("output", "v1")
    graph.add_asset(AssetVersion(source, "shot-1", "IMAGE", "asset://source", "sha256:source"))
    graph.add_asset(AssetVersion(output, "shot-1", "VIDEO", "asset://output", "sha256:output", derived_from=(source,)))
    graph.add_task(TaskRecord("generate", "shot-1", "I2V", input_assets=(source,), output_assets=(output,)))
    assert graph.tasks["generate"].input_assets == (source,)

    with pytest.raises(MediaGraphError, match="task dependencies missing"):
        graph.add_task(TaskRecord("review", "shot-1", "REVIEW", depends_on=("does-not-exist",)))


def test_graph_round_trip_persists_identity_lineage_decisions_and_pointers(tmp_path: Path):
    graph = _base_graph()
    asset = AssetVersion(
        ref=AssetRef("frame", "v1"),
        context_id="shot-1",
        kind="IMAGE",
        uri="asset://frame",
        digest="sha256:frame",
        rights_refs=("rights://1",),
    )
    graph.add_asset(asset)
    graph.add_evidence(EvidenceRecord("ev", "ASSET", asset.ref.key(), "REVIEW", ("review://1",), "2026-10-15T00:00:00Z"))
    graph.add_decision(DecisionRecord("dec", "PROMOTION", "art_director", (asset.ref.key(),), ("criteria://1",), ("ev",), "PROMOTE", "2026-10-15T00:01:00Z"))
    graph.promote_asset(asset.ref, decision_id="dec")

    path = tmp_path / "media-graph.json"
    store = MediaGraphStore(path)
    store.save(graph)
    restored = store.load()
    assert restored.current_promoted("frame").digest == "sha256:frame"
    assert restored.decisions["dec"].owner == "art_director"
    assert restored.contexts["shot-1"].parent_context_id == "seq-1"

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["promoted_versions"]["frame"] == "v1"
