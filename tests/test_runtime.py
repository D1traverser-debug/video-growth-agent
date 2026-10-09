from pathlib import Path
import pytest

from video_growth_agent import Approval, ArtifactRecord, AssetRecord, GateBlocked, ProjectStore, StudioRuntime


def runtime(tmp_path: Path) -> StudioRuntime:
    return StudioRuntime(store=ProjectStore(tmp_path / "projects"))


def test_project_checkpoint_roundtrip_and_receipts(tmp_path):
    rt = runtime(tmp_path); state = rt.create_project("pilot-x", title="test"); assert state.stage == "INTAKE"
    rt.record_artifact("pilot-x", "brief", "file://brief.md", "INTAKE", digest="a1")
    receipt = rt.sign("pilot-x", "showrunner", "PASS", "brief is viable", ("file://brief.md",))
    assert (tmp_path / "projects" / "pilot-x" / receipt).exists(); assert rt.advance("pilot-x") == "POSITIONING"
    loaded = rt.state("pilot-x"); assert loaded.approvals["INTAKE"]["showrunner"].decision == "PASS"
    events = (tmp_path / "projects" / "pilot-x" / "events.jsonl").read_text(encoding="utf-8").strip().splitlines(); assert len(events) >= 4


def test_changed_upstream_artifact_invalidates_downstream(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); rt.record_artifact("p", "brief", "file://brief-v1", "INTAKE", digest="1"); rt.sign("p", "showrunner", "PASS"); rt.advance("p")
    rt.record_artifact("p", "brief", "file://brief-v2", "INTAKE", digest="2")
    state = rt.state("p"); assert state.stage == "INTAKE"; assert state.approvals == {}; assert state.invalidated_from == "INTAKE"


def test_unknown_final_rights_are_exposed(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p")
    rt.record_asset("p", AssetRecord("a1", "file://asset", "image", "UNKNOWN", used_in_final=True)); rt.record_asset("p", AssetRecord("a2", "file://owned", "image", "OWNED", used_in_final=True))
    assert rt.unknown_final_rights("p") == ["a1"]


def test_current_prompts_are_stage_scoped(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); prompts = rt.current_prompts("p")
    assert set(prompts) == {"showrunner"}; assert "Protect the account" in prompts["showrunner"]


def _force_release_state(rt, project_id: str):
    state = rt.state(project_id); state.stage = "RELEASE"
    state.artifacts["final_media"] = ArtifactRecord("final_media", "file://final.mp4", "RELEASE", kind="media")
    state.artifacts["publish_pack"] = ArtifactRecord("publish_pack", "file://publish.md", "RELEASE")
    state.artifacts["technical_qa"] = ArtifactRecord("technical_qa", "receipts/qa.json", "TECH_QA", kind="qa_report", metadata={"hard_pass": True})
    rt.store.save(state)


def test_release_machine_guard_blocks_unknown_rights(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); _force_release_state(rt, "p")
    rt.record_asset("p", AssetRecord("unknown", "file://x", "image", "UNKNOWN", used_in_final=True))
    state = rt.state("p"); state.stage = "RELEASE"; state.approvals["RELEASE"] = {"showrunner": Approval("showrunner", "PASS")}; rt.store.save(state)
    report = rt.gate_report("p"); assert not report["pass"]; assert any(item.startswith("no_unknown_final_rights") for item in report["machine_failures"])
    with pytest.raises(GateBlocked): rt.advance("p")


def test_tech_qa_machine_guard_requires_hard_pass_receipt(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); state = rt.state("p"); state.stage = "TECH_QA"
    state.artifacts["final_candidate"] = ArtifactRecord("final_candidate", "file://candidate.mp4", "TECH_QA", kind="media")
    state.artifacts["technical_qa"] = ArtifactRecord("technical_qa", "receipts/qa.json", "TECH_QA", kind="qa_report", metadata={"hard_pass": False})
    state.approvals["TECH_QA"] = {"technical_director": Approval("technical_director", "PASS")}; rt.store.save(state)
    assert rt.gate_report("p")["machine_failures"] == ["latest_media_qa_hard_pass"]
    with pytest.raises(GateBlocked): rt.advance("p")
