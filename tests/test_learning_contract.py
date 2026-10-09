import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_quality_rubric_mirrors_package_and_requires_final_fidelity_sample():
    config = _load("config/quality-rubric.json")
    packaged = _load("video_growth_agent/data/quality-rubric.json")
    assert config == packaged

    preview = config["stages"]["VISUAL_PREVIEW"]
    contract = preview["prototype_contract"]
    assert contract["full_build_forbidden_before_pass"] is True
    assert contract["near_final_visual_fidelity"] is True
    assert contract["representative_motion"] is True
    assert contract["representative_sound_or_intentional_silence"] is True
    assert "sample_final_fidelity" in preview["roles"]["creative_director"]["dimensions"]
    assert "sample_represents_final_language" in preview["roles"]["director"]["dimensions"]


def test_external_learning_enters_technique_library_as_candidates_not_unearned_validation():
    config = _load("config/techniques.json")
    packaged = _load("video_growth_agent/data/techniques.json")
    assert config == packaged

    techniques = {item["id"]: item for item in config["techniques"]}
    for technique_id in ("T-008", "T-009", "T-010", "T-011", "T-012", "T-013", "T-014"):
        assert techniques[technique_id]["status"] == "candidate"

    assert techniques["T-012"]["name"] == "样片先行"
