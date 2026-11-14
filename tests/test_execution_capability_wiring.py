import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_caos_entry_and_video_capability_profile_bind_execution_semantics():
    skill = (ROOT / "CAOS_VIDEO_ENTRY.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "video_growth_agent/data/capabilities.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "video_growth_agent/data/domain_manifest.json").read_text(encoding="utf-8"))

    assert "CAOS" in skill
    assert "CHAT_GOVERNED_EXTERNAL" in skill
    assert "D1traverser-debug/cognition-agent-os" in skill
    assert "decision loop" in skill.lower()
    assert "execution loop" in skill.lower()
    assert manifest["governance"]["system"] == "CAOS"
    assert manifest["governance"]["runtime_dependency"] is False
    assert profile["governance_binding"]["mode"] == "CHAT_GOVERNED_EXTERNAL"
    assert "video_domain_problem_recovery_and_evolution_admission" in {
        item["capability_id"] for item in profile["capabilities"]
    }
    for term in ("DECLARED_ONLY", "HARNESS_WIRED", "SESSION_EXECUTABLE", "CHAT_BRIDGED", "ATTESTED_ISOLATED"):
        assert term in skill
        assert term in profile["assurance_taxonomy"]
    assert not (ROOT / ".uaos").exists()
    assert not (ROOT / "UAOS_SKILL.md").exists()
    assert not (ROOT / "continuity").exists()
