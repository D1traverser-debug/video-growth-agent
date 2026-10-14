import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_uaos_skill_and_capability_profile_bind_execution_semantics():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))

    assert ".uaos/CAPABILITIES.json" in skill
    assert "handshake" in skill.lower()
    for term in ("DECLARED_ONLY", "HARNESS_WIRED", "SESSION_EXECUTABLE", "CHAT_BRIDGED", "ATTESTED_ISOLATED"):
        assert term in skill
        assert term in profile["assurance_taxonomy"]
    assert not (ROOT / "continuity").exists()
