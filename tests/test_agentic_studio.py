import pytest

from video_growth_agent import ArtifactRecord, GateBlocked, ProjectStore, StudioRuntime
from video_growth_agent.studio_agents import AgentRegistry, AgenticStudio, ExecutionPlanner


def make_studio(tmp_path):
    runtime = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    runtime.create_project("p1", title="test")
    return AgenticStudio(runtime=runtime)


def set_stage(studio, stage, artifacts=()):
    state = studio.runtime.state("p1")
    state.stage = stage
    for name in artifacts:
        state.artifacts[name] = ArtifactRecord(
            name=name,
            uri=f"/tmp/{name}",
            stage=stage,
            digest=f"digest-{name}",
            metadata={},
        )
    studio.runtime.store.save(state)


def test_agent_registry_is_isolated_and_single_voice():
    reg = AgentRegistry()
    assert reg.validate() == []
    assert reg.get("executive_producer").user_voice is True
    assert reg.get("visual_designer").role is None
    assert reg.config["principles"]["peer_chat"] is False
    assert reg.config["principles"]["hard_gate_override"] is False


def test_execution_plan_valid_and_tools_are_not_agents():
    planner = ExecutionPlanner()
    assert planner.validate() == []
    assert set(planner.config["stages"]) == set(planner.orchestrator.index)
    qa = planner.stage("TECH_QA")["tasks"][0]
    assert qa["executor"] == "tool"
    assert qa["tool"] == "ffmpeg_ffprobe"
    assert qa.get("agent") is None
    assert any(t["id"] == "final_conform" for t in planner.stage("SOUND")["tasks"])


def test_lookdev_separates_builder_from_approvers():
    planner = ExecutionPlanner()
    tasks = planner.stage("LOOKDEV")["tasks"]
    builder = next(t for t in tasks if t["type"] == "produce")
    reviewers = [t for t in tasks if t["type"] == "review"]
    assert builder["agent"] == "visual_designer"
    assert {t["agent"] for t in reviewers} == {"art_director", "creative_director"}
    assert builder["agent"] not in {t["agent"] for t in reviewers}


def test_work_packet_is_least_context_and_blind(tmp_path):
    studio = make_studio(tmp_path)
    set_stage(studio, "LOOKDEV", ["storyboard", "script", "research_package", "secret_unrelated"])
    orders = studio.dispatch_stage("p1")
    build = next(o for o in orders if o.task_id == "lookdev_build")
    assert build.status == "READY"
    packet = studio.work_packet("p1", "lookdev_build")
    assert set(packet["inputs"]) == {"storyboard", "script", "research_package"}
    assert "secret_unrelated" not in packet["inputs"]

    studio.complete_work(
        "p1",
        "lookdev_build",
        outputs={
            "benchmark_pack": {"uri": "/tmp/bench", "digest": "b1"},
            "style_bible": {"uri": "/tmp/style", "digest": "s1"},
            "hero_frames": {"uri": "/tmp/heroes", "digest": "h1"},
        },
    )
    studio.dispatch_stage("p1")
    review = studio.work_packet("p1", "art_lookdev")
    assert review["project_approvals_hidden"] is True
    assert "approvals" not in review
    assert set(review["inputs"]) == {"benchmark_pack", "style_bible", "hero_frames"}


def test_reviewer_cannot_review_own_artifact(tmp_path):
    studio = make_studio(tmp_path)
    set_stage(studio, "LOOKDEV", ["storyboard", "script", "research_package"])
    studio.dispatch_stage("p1")
    studio.complete_work(
        "p1",
        "lookdev_build",
        outputs={
            "benchmark_pack": {"uri": "/tmp/bench", "digest": "b1"},
            "style_bible": {"uri": "/tmp/style", "digest": "s1"},
            "hero_frames": {"uri": "/tmp/heroes", "digest": "h1"},
        },
    )
    state = studio.runtime.state("p1")
    hero = state.artifacts["hero_frames"]
    state.artifacts["hero_frames"] = ArtifactRecord(
        name=hero.name,
        uri=hero.uri,
        stage=hero.stage,
        kind=hero.kind,
        digest=hero.digest,
        metadata={**hero.metadata, "produced_by_agent": "art_director"},
    )
    studio.runtime.store.save(state)
    studio.dispatch_stage("p1")
    with pytest.raises(ValueError, match="Self-review forbidden"):
        studio.submit_review("p1", "art_lookdev", "FAIL", notes="self review should be blocked")


def test_panel_reviews_are_hidden_until_meta_review(tmp_path):
    studio = make_studio(tmp_path)
    set_stage(studio, "AUDIENCE_QA", ["final_candidate"])
    studio.dispatch_stage("p1")
    cold = studio.work_packet("p1", "cold_view")
    assert cold["project_approvals_hidden"] is True
    assert "panel_reviews" not in cold

    for task in ("cold_view", "target_view", "advertiser_view"):
        studio.submit_review("p1", task, "PASS", notes="panel result", evidence=("final-frame-review",))
    studio.dispatch_stage("p1")
    meta = studio.work_packet("p1", "retention_meta")
    assert len(meta["panel_reviews"]) == 3
    assert {x["reviewer"] for x in meta["panel_reviews"]} == {
        "cold_viewer",
        "target_viewer",
        "advertiser_viewer",
    }


def test_only_declared_agent_can_sign_assigned_role(tmp_path):
    studio = make_studio(tmp_path)
    for _, spec in studio.planner.config["stages"].items():
        for task in spec["tasks"]:
            if task.get("approval_role") and task["executor"] == "agent":
                assert studio.agents.get(task["agent"]).role == task["approval_role"]


def test_agentic_advance_blocks_incomplete_work_orders(tmp_path):
    studio = make_studio(tmp_path)
    studio.dispatch_stage("p1")
    with pytest.raises(GateBlocked, match="incomplete_work_orders"):
        studio.advance("p1")

    studio.complete_work(
        "p1",
        "intake",
        outputs={"brief": {"uri": "/tmp/brief.md", "digest": "brief1"}},
    )
    assert studio.advance("p1") == "POSITIONING"
