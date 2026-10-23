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

def _render_review_fixture(tmp_path):
    import json
    import subprocess
    from pathlib import Path
    plan = json.loads((Path(__file__).parent / "fixtures" / "prompt_ip_5s.json").read_text(encoding="utf-8"))
    plan_path = tmp_path / "director-plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    media = tmp_path / "synthetic-color-test-not-an-ai-film.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=0x345b8c:s=320x568:r=24:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(media),
    ], check=True)
    return plan, plan_path, media


def _directed_graph():
    from video_growth_agent.media_graph import MediaGraph, ContextRecord
    graph = MediaGraph()
    graph.add_context(ContextRecord("P1", "PROGRAM"))
    graph.add_context(ContextRecord("E1", "EPISODE", "P1"))
    graph.add_context(ContextRecord("SQ1", "SEQUENCE", "E1"))
    return graph


def test_director_take_registration_preserves_graph_lineage_without_quality_promotion(tmp_path):
    import json
    import copy
    import hashlib
    import pytest
    from video_growth_agent.media_qa import MediaQAChecker
    from video_growth_agent.media_graph import AssetRef, MediaGraphStore
    from video_growth_agent.plan_graph_bridge import (
        PlanGraphBridgeError, register_directed_take_observation,
    )
    if not MediaQAChecker.tools_available():
        pytest.skip("ffmpeg/ffprobe unavailable")
    original, plan_path, media = _render_review_fixture(tmp_path)
    graph = _directed_graph()

    def register(p, plan_version, take_version):
        return register_directed_take_observation(
            graph, plan=p, plan_uri=str(plan_path), media=str(media), context_id="SQ1",
            director_plan_id="directed-plan:SQ1", plan_version=plan_version,
            take_id="rendered-take:SQ1", take_version=take_version,
        )

    take_ref, packet = register(original, "p1", "t1")
    plan_ref = AssetRef("directed-plan:SQ1", "p1")
    assert graph.assets[take_ref].derived_from == (plan_ref,)
    assert graph.assets[take_ref].digest == "sha256:" + hashlib.sha256(media.read_bytes()).hexdigest()
    assert graph.asset_state(take_ref) == "CANDIDATE"
    assert graph.promoted_versions == {} and graph.decisions == {}
    assert graph.assets[take_ref].metadata["provider_execution_verified"] is False
    assert packet["assessment"] == "NOT_STARTED__REAL_MEDIA_BOUND"
    assert packet["timeline_alignment"] == "DURATION_MISMATCH__EDIT_CONFORM_REQUIRED"
    assert graph.evidence["media-inspection:" + take_ref.key()].metadata["quality_outcome"] == "NOT_REVIEWED"
    with pytest.raises(PlanGraphBridgeError, match="already registered"):
        register(original, "p1", "t1")
    changed = copy.deepcopy(original)
    changed["shots"][0]["composition"] += "; revised framing requires new observation"
    plan_path.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(PlanGraphBridgeError, match="immutable plan"):
        register(changed, "p1", "t2")
    next_ref, _ = register(changed, "p2", "t2")
    affected = graph.invalidate_downstream(plan_ref)
    assert take_ref in affected and next_ref not in affected
    assert graph.asset_state(take_ref) == "STALE"
    assert graph.asset_state(next_ref) == "CANDIDATE"
    graph_path = tmp_path / "graph.json"
    MediaGraphStore(graph_path).save(graph)
    restored = MediaGraphStore(graph_path).load()
    assert restored.assets[next_ref].digest == graph.assets[next_ref].digest
    assert restored.evidence["media-inspection:" + next_ref.key()].metadata["review_packet"]["first_pass_viewing"]["status"] == "NOT_EXECUTED"
    assert not restored.promoted_versions


def test_directed_take_cli_registers_in_existing_graph_and_refuses_overwrite(tmp_path):
    import json
    import subprocess
    import sys
    import pytest
    from video_growth_agent.media_qa import MediaQAChecker
    from video_growth_agent.media_graph import AssetRef, MediaGraphStore
    if not MediaQAChecker.tools_available():
        pytest.skip("ffmpeg/ffprobe unavailable")
    _, plan_file, media = _render_review_fixture(tmp_path)
    store = MediaGraphStore(tmp_path / "graph.json")
    store.save(_directed_graph())
    args = [
        sys.executable, "-m", "video_growth_agent.cli", "register-directed-take",
        str(store.path), str(plan_file), str(media), "--context-id", "SQ1",
        "--director-plan-id", "directed-plan:SQ1", "--plan-version", "v1",
        "--take-id", "candidate:SQ1", "--take-version", "t1",
    ]
    executed = subprocess.run(args, capture_output=True, text=True)
    assert executed.returncode == 0, executed.stderr
    payload = json.loads(executed.stdout)
    assert payload["state"] == "CANDIDATE"
    assert payload["quality_review"] == "NOT_STARTED"
    assert payload["provider_attribution"] == "NOT_VERIFIED"
    assert payload["promotion_authorized"] is False
    assert payload["review_packet"]["first_pass_viewing"]["responses"] is None
    assert payload["duration_alignment"] == "DURATION_MISMATCH__EDIT_CONFORM_REQUIRED"
    graph = store.load()
    ref = AssetRef("candidate:SQ1", "t1")
    assert graph.assets[ref].derived_from == (AssetRef("directed-plan:SQ1", "v1"),)
    assert not graph.promoted_versions
    before = store.path.read_bytes()
    repeated = subprocess.run(args, capture_output=True, text=True)
    assert repeated.returncode == 2
    assert "already registered" in repeated.stderr
    assert store.path.read_bytes() == before

    missing_context = subprocess.run(
        args[:-10] + ["--context-id", "missing", "--director-plan-id",
                       "different-plan", "--plan-version", "v1",
                       "--take-id", "other-take", "--take-version", "t1"],
        capture_output=True, text=True,
    )
    assert missing_context.returncode == 2
    assert "existing sequence/shot context" in missing_context.stderr
    assert store.path.read_bytes() == before
