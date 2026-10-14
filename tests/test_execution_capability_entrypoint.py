import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_uaos_entry_and_capability_profile_require_current_session_handshake():
    skill = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    profile = json.loads((ROOT / ".uaos/CAPABILITIES.json").read_text(encoding="utf-8"))

    assert ".uaos/CAPABILITIES.json" in skill
    assert "current-session capability handshake" in skill.lower()
    assert profile["execution_readiness_contract"] == "2.0"
    assert profile["owner"] == "VIDEO_GROWTH_AGENT"
    assert profile["domain_id"] == "video"
    assert all(item["side_channel_allowed"] is False for item in profile["capabilities"])
