"""Deletion regression tests: no zombie authorities, no loss of repair provenance."""
import json
from pathlib import Path

from video_growth_agent.resources import data_path
from video_growth_agent.roles import RoleRegistry

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects/ai-self-media-commercialization"


def test_roles_have_one_runtime_prompt_source():
    roles = json.loads(data_path("roles.json").read_text(encoding="utf-8"))
    assert roles["canonical_prompt_source"] == "video_growth_agent/data/team.md"
    assert not (ROOT / "skills/video-growth-agent/references/team.md").exists()
    assert data_path("team.md").is_file()
    registry = RoleRegistry()
    assert registry.get("director").prompt
    assert registry.get("creative_director").prompt


def test_wrong_input_provisional_pass_is_retired_not_hidden():
    manifest = json.loads((PROJECT / "PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    removed = "H1_S13_HYBRID_FRONT_REVIEW_2026-10-14.md"
    corrected = "H1_S13_HYBRID_FRONT_REVIEW_CORRECTED_2026-10-14.md"
    assert not (PROJECT / removed).exists()
    assert (PROJECT / corrected).exists()
    tombstones = {x["path"]: x for x in manifest["retired_documents"]}
    assert tombstones[removed]["active_decision"] is False
    assert tombstones[removed]["replaced_by"] == corrected
    assert tombstones[removed]["git_blob_sha"]
    text = (PROJECT / corrected).read_text(encoding="utf-8")
    assert "wrongly uploaded image" in text
    assert "Do not use that earlier pass as authority" in text


def test_rejected_character_prompt_replaced_by_active_design_method():
    manifest = json.loads((PROJECT / "PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    name = "CONCEPT_GENERATION_PROMPT_V1.md"
    assert not (PROJECT / name).exists()
    tombstones = {x["path"]: x for x in manifest["retired_documents"]}
    assert tombstones[name]["active_decision"] is False
    assert tombstones[name]["replaced_by"] == "DESIGN_RESEARCH_METHOD_V2.md"
    for filename in ("DESIGN_RESEARCH_METHOD_V2.md", "CONCEPT_V1_FAILURE_AUDIT_2026-10-14.md"):
        assert (PROJECT / filename).exists()
    current_skill = (ROOT / "skills/video-growth-agent/references/prompt-direction.md").read_text(encoding="utf-8")
    assert "primary figure silhouette" in current_skill
