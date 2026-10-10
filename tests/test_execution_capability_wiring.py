from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_and_continuity_index_reference_execution_capabilities():
    skill = (ROOT / "skills/video-growth-agent/SKILL.md").read_text(encoding="utf-8")
    index = (ROOT / "continuity/TASK_INDEX.md").read_text(encoding="utf-8")

    required_ref = "continuity/EXECUTION_CAPABILITIES.json"
    assert required_ref in skill
    assert required_ref in index
    assert "handshake" in skill.lower()
    assert "handshake" in index.lower()
    assert "chat_bridged" in skill.lower()
    assert "attested_isolated" in skill.lower()
