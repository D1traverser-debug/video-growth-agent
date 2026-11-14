import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_video_domain_has_one_external_caos_governance_binding():
    manifest = read_json("video_growth_agent/data/domain_manifest.json")
    capabilities = read_json("video_growth_agent/data/capabilities.json")
    coordination = read_json("video_growth_agent/data/coordination-policy.json")
    index = read_json("projects/PROJECT_INDEX.json")
    state = read_json("projects/ai-self-media-commercialization/PROGRAM_STATE.json")

    for binding in (
        manifest["governance"],
        capabilities["governance_binding"],
        coordination["governance_binding"],
        index["governance"],
    ):
        assert binding["system"] == "CAOS"
        assert binding["mode"] == "CHAT_GOVERNED_EXTERNAL"
        assert binding["runtime_dependency"] is False
        assert binding["source_mutation"] == "FORBIDDEN"

    assert manifest["skill"]["entrypoint"] == "CAOS_VIDEO_ENTRY.md"
    assert state["governance_mode"] == "CHAT_GOVERNED_EXTERNAL"
    assert state["caos_runtime_dependency"] is False
    assert "parent_identity_semantics" not in state
    assert "parent_reference_semantics" not in state


def test_legacy_parent_runtime_artifacts_are_removed_but_video_capabilities_survive():
    assert not (ROOT / ".uaos").exists()
    assert not (ROOT / "UAOS_SKILL.md").exists()
    assert not (ROOT / "tests/test_uaos_current.py").exists()
    profile = read_json("video_growth_agent/data/capabilities.json")
    capability_ids = {item["capability_id"] for item in profile["capabilities"]}
    assert "video_domain_problem_recovery_and_evolution_admission" in capability_ids
    assert len(capability_ids) >= 20
    assert profile["owner"] == "VIDEO_GROWTH_AGENT"
    assert profile["assurance_taxonomy"] == [
        "DECLARED_ONLY",
        "HARNESS_WIRED",
        "SESSION_EXECUTABLE",
        "CHAT_BRIDGED",
        "ATTESTED_ISOLATED",
    ]


def test_ipos_remains_standalone_and_does_not_depend_on_caos_runtime():
    integration = read_json("projects/ai-self-media-commercialization/IPOS_INTEGRATION_STATE.json")
    assert integration["authority"]["system"] == "IP_STUDIO_OS"
    assert integration["authority"]["standalone_execution"] is True
    assert integration["authority"]["caos_runtime_dependency"] is False
    assert integration["current_handoff"]["status"] == "NO_APPROVED_BUNDLE_AVAILABLE"


def test_active_video_entrypoints_do_not_route_to_legacy_parent():
    active_paths = (
        "CAOS_VIDEO_ENTRY.md",
        "README.md",
        "skills/video-growth-agent/SKILL.md",
        "docs/product_requirements.md",
        "docs/media_business_os.md",
        "docs/architecture.md",
        "docs/agent_operability_scenarios.md",
    )
    forbidden = ("universal-agent-os", "universal-continuity-agent", "UAOS_SKILL.md", ".uaos/")
    for rel in active_paths:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token.lower() not in text, f"{rel} still routes to {token}"
