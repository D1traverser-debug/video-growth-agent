"""Canonical Video workstream continuation remains inspectable across chats."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "audits/EVOLUTION_INDEX.json"
WORK_ID = "V-20261024-01-PROMPT-CRAFT-ITERATION-PR23"


def test_video_craft_candidate_has_one_canonical_resume_ref():
    doc = json.loads(CURRENT.read_text(encoding="utf-8"))
    assert doc["owner"] == "DOMAIN:video"
    assert WORK_ID in doc["current_open_items"]
    ref = doc["current_resume_ref"]
    assert ref == doc["current_problem_refs"][WORK_ID]
    assert ref == doc["current_candidate"]["resume_ref"]
    note = (ROOT / ref).read_text(encoding="utf-8")
    assert "PR #23" in note
    assert "real representative H3" in note
    assert "NOT_PRODUCTION" in note
    assert "No money was spent" in note


def test_no_unearned_promotion_and_existing_entrypoints_remain_authority():
    doc = json.loads(CURRENT.read_text(encoding="utf-8"))
    candidate = doc["current_candidate"]
    assert candidate["pr_number"] == 23
    assert candidate["promotion_authorized"] is False
    assert candidate["verified_prior_checks"]["all_tests_passed"] == 255
    assert candidate["verified_prior_checks"]["prompt_contract_passed"] == 66
    assert len(candidate["required_next_evidence"]) >= 4
    assert "LIVE_MEDIA" in doc["assurance"]
    for path in ("README.md", "UAOS_SKILL.md"):
        assert "audits/EVOLUTION_INDEX.json" in (ROOT / path).read_text(encoding="utf-8")
    assert "current_resume_ref" in (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    assert not (ROOT / "CURRENT_SYSTEM.json").exists()
