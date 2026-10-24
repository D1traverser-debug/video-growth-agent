"""Ten separate research cards remain accessible; this is not an art-quality test."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDIES = ROOT / "skills/video-growth-agent/references/storycraft-research-2026-10-25"


def test_studies_are_individually_accessible_and_distinct():
    index = json.loads((STUDIES / "STUDY_INDEX.json").read_text(encoding="utf-8"))
    assert index["entry_count"] == len(index["entries"]) == 10
    assert len({e["id"] for e in index["entries"]}) == 10
    assert len({e["source_url"] for e in index["entries"]}) == 10
    assert len({e["document_ref"] for e in index["entries"]}) == 10
    for entry in index["entries"]:
        assert entry["source_url"].startswith("https://")
        assert entry["transferable_mechanism"]
        assert entry["diagnose_when"]
        assert entry["required_work_product"]
        document = ROOT / entry["document_ref"]
        assert document.is_file(), entry["id"]
        text = document.read_text(encoding="utf-8")
        assert entry["source_url"] in text, entry["id"]
        assert "V5" in text, entry["id"]
        assert len(text) > 850, entry["id"]


def test_cross_study_diagnosis_remains_unapproved():
    readme = (STUDIES / "README.md").read_text(encoding="utf-8")
    evaluation = (STUDIES / "V5-CASE-REASSESSMENT.md").read_text(encoding="utf-8")
    for number in range(1, 11):
        assert f"K{number:02d}" in readme
        assert f"K{number:02d}" in evaluation
    assert "ARTISTIC_PREMISE_NOT_READY" in evaluation
    assert "未完成真人" in evaluation
