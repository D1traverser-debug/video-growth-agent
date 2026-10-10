from video_growth_agent import Approval, ArtifactRecord, AssetRecord, ProjectState


def test_state_serialization_roundtrip():
    s = ProjectState("x")
    s.approvals["INTAKE"] = {"showrunner": Approval("showrunner", "PASS", findings=("a",))}
    s.artifacts["brief"] = ArtifactRecord("brief", "file://brief", "INTAKE", digest="abc")
    s.assets["asset"] = AssetRecord("asset", "file://a", "image", "OWNED")
    clone = ProjectState.from_dict(s.to_dict())
    assert clone.to_dict() == s.to_dict()


def test_packaged_runtime_resources_are_single_repository_authority():
    import json
    from pathlib import Path
    from video_growth_agent.resources import data_path

    root = Path(__file__).resolve().parents[1]
    assert not (root / "config").exists()
    for name in ("roles.json", "workflow.json", "techniques.json", "quality-rubric.json"):
        payload = json.loads(data_path(name).read_text(encoding="utf-8"))
        assert isinstance(payload, dict) and payload
    assert data_path("team.md").read_text(encoding="utf-8") == (
        root / "skills/video-growth-agent/references/team.md"
    ).read_text(encoding="utf-8")
