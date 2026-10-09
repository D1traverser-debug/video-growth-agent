from video_growth_agent import Approval, ArtifactRecord, AssetRecord, ProjectState


def test_state_serialization_roundtrip():
    s = ProjectState("x")
    s.approvals["INTAKE"] = {"showrunner": Approval("showrunner", "PASS", findings=("a",))}
    s.artifacts["brief"] = ArtifactRecord("brief", "file://brief", "INTAKE", digest="abc")
    s.assets["asset"] = AssetRecord("asset", "file://a", "image", "OWNED")
    clone = ProjectState.from_dict(s.to_dict())
    assert clone.to_dict() == s.to_dict()
