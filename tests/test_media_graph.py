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

def test_invalidated_take_cannot_be_promoted_even_with_later_positive_decision():
    """A previously valid review receipt cannot revive obsolete plan descendants."""
    graph = _base_graph()
    plan = AssetRef("director-plan", "p1")
    take = AssetRef("take", "t1")
    graph.add_asset(AssetVersion(plan, "episode-1", "EDITORIAL_PLAN", "plan://p1", "sha256:p1"))
    graph.add_asset(AssetVersion(take, "shot-1", "VIDEO_TAKE", "take://t1", "sha256:t1", derived_from=(plan,)))
    graph.add_evidence(EvidenceRecord(
        "review-old-take", "ASSET", take.key(), "REVIEW",
        ("report://observed-t1",), "2026-10-24T01:00:00Z",
    ))
    graph.add_decision(DecisionRecord(
        "accept-stale", "ASSET_PROMOTION", "editor",
        (take.key(),), ("criteria://shot-quality",),
        ("review-old-take",), "PROMOTE", "2026-10-24T01:01:00Z",
    ))
    affected = graph.invalidate_downstream(plan)
    assert take in affected
    assert graph.asset_state(take) == "STALE"
    with pytest.raises(MediaGraphError, match="stale"):
        graph.promote_asset(take, decision_id="accept-stale")
    assert graph.current_promoted("take") is None
    assert graph.asset_state(take) == "STALE"

def test_promotion_rejects_transitive_obsolete_plan_even_without_stale_propagation():
    """The promote gate must not depend on every caller invalidating descendants first."""
    graph = _base_graph()
    old = AssetRef("director-plan", "p1")
    new = AssetRef("director-plan", "p2")
    frame = AssetRef("planned-frame", "f1")
    take = AssetRef("rendered-take", "t1")
    graph.add_asset(AssetVersion(old, "episode-1", "DIRECTOR_PLAN", "plan://p1", "sha256:p1"))
    graph.add_asset(AssetVersion(new, "episode-1", "DIRECTOR_PLAN", "plan://p2", "sha256:p2"))
    graph.add_asset(AssetVersion(frame, "shot-1", "IMAGE", "frame://f1", "sha256:f1", derived_from=(old,)))
    graph.add_asset(AssetVersion(take, "shot-1", "VIDEO_TAKE", "take://t1", "sha256:t1", derived_from=(frame,)))

    for ref in (old, new, take):
        evidence_id = "review:" + ref.key()
        decision_id = "promote:" + ref.key()
        graph.add_evidence(EvidenceRecord(
            evidence_id, "ASSET", ref.key(), "REVIEW", ("review://test-" + ref.key(),),
            "2026-10-24T02:00:00Z",
        ))
        graph.add_decision(DecisionRecord(
            decision_id, "ASSET_PROMOTION", "editor", (ref.key(),),
            ("criteria://test",), (evidence_id,), "PROMOTE", "2026-10-24T02:01:00Z",
        ))
    graph.promote_asset(old, decision_id="promote:" + old.key())
    graph.promote_asset(new, decision_id="promote:" + new.key())
    assert graph.asset_state(old) == "STALE"
    assert graph.asset_state(take) == "STALE"  # effective state needs no invalidation call
    with pytest.raises(MediaGraphError, match="stale"):
        graph.promote_asset(take, decision_id="promote:" + take.key())
    assert graph.current_promoted("rendered-take") is None



def test_promoted_take_becomes_unavailable_after_plan_supersession_without_propagation():
    """Release-facing current and timeline queries cannot see a stale selected Take."""
    from video_growth_agent.timeline import TimelineClip, TimelineSpec, TimelineError

    graph = _base_graph()
    plan_old = AssetRef("plan", "v1")
    plan_new = AssetRef("plan", "v2")
    take = AssetRef("take", "v1")
    graph.add_asset(AssetVersion(plan_old, "episode-1", "DIRECTOR_PLAN", "plan://old", "sha256:old"))
    graph.add_asset(AssetVersion(plan_new, "episode-1", "DIRECTOR_PLAN", "plan://new", "sha256:new"))
    graph.add_asset(AssetVersion(take, "shot-1", "VIDEO_TAKE", "asset://take", "sha256:take", derived_from=(plan_old,)))

    for ref in (plan_old, plan_new, take):
        eid = "e:" + ref.key()
        did = "d:" + ref.key()
        graph.add_evidence(EvidenceRecord(eid, "ASSET", ref.key(), "REVIEW", ("proof://" + ref.key(),), "2026-10-24T00:00:00Z"))
        graph.add_decision(DecisionRecord(
            did, "PROMOTION", "editor", (ref.key(),), ("criteria://review",),
            (eid,), "PROMOTE", "2026-10-24T00:01:00Z",
        ))
    graph.promote_asset(plan_old, decision_id="d:" + plan_old.key())
    graph.promote_asset(take, decision_id="d:" + take.key())
    timeline = TimelineSpec("master", "v1", "episode-1", (TimelineClip("clip", take, "V", 0, 0, 5),))
    timeline.validate_against_graph(graph)
    assert graph.current_promoted("take").ref == take

    # Deliberately omit invalidate_downstream(plan_old). Readers must remain safe.
    graph.promote_asset(plan_new, decision_id="d:" + plan_new.key())
    assert graph.asset_state(take) == "STALE"
    assert graph.current_promoted("take") is None
    with pytest.raises(TimelineError, match="not promoted"):
        timeline.validate_against_graph(graph)
    # History is retained for diagnosis and rollback planning.
    assert take in graph.assets
