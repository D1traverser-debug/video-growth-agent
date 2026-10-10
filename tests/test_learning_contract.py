import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_quality_rubric_requires_final_fidelity_sample():
    config = _load("video_growth_agent/data/quality-rubric.json")

    preview = config["stages"]["VISUAL_PREVIEW"]
    contract = preview["prototype_contract"]
    assert contract["full_build_forbidden_before_pass"] is True
    assert contract["near_final_visual_fidelity"] is True
    assert contract["representative_motion"] is True
    assert contract["representative_sound_or_intentional_silence"] is True
    assert "sample_final_fidelity" in preview["roles"]["creative_director"]["dimensions"]
    assert "sample_represents_final_language" in preview["roles"]["director"]["dimensions"]


def test_external_learning_enters_technique_library_as_candidates_not_unearned_validation():
    config = _load("video_growth_agent/data/techniques.json")

    techniques = {item["id"]: item for item in config["techniques"]}
    for technique_id in ("T-008", "T-009", "T-010", "T-011", "T-012", "T-013", "T-014"):
        assert techniques[technique_id]["status"] == "candidate"

    assert techniques["T-012"]["name"] == "样片先行"


def test_learn_stage_actually_schedules_declared_improvement_roles():
    plan = _load("video_growth_agent/data/execution-plan.json")
    learn = plan["stages"]["LEARN"]["tasks"]
    agents = [task.get("agent") for task in learn]
    assert agents == [
        "production_methodologist",
        "evolution_engineer",
        "red_team",
        "showrunner",
    ]

    by_id = {task["id"]: task for task in learn}
    assert by_id["learning_methodology"]["outputs"] == ["learning_candidate"]
    assert by_id["learning_evolution_candidate"]["inputs"] == ["learning_candidate"]
    assert by_id["learning_evolution_candidate"]["outputs"] == ["learning_receipt"]
    assert by_id["learning_red_team"]["inputs"] == ["learning_receipt"]
    assert by_id["learning_showrunner"]["inputs"] == ["learning_receipt"]


def test_learning_capability_distinguishes_evidence_pipeline_from_autonomous_promotion():
    profile = _load("continuity/EXECUTION_CAPABILITIES.json")
    caps = {item["capability_id"]: item for item in profile["capabilities"]}
    scheduled = caps["scheduled_learning_evidence_pipeline"]
    sidecar = caps["learning_evolution_sidecar"]

    assert scheduled["assurance_ceiling"] == "SESSION_EXECUTABLE"
    assert "Production Methodologist" in scheduled["invocation_path"]
    assert "Evolution Engineer" in scheduled["invocation_path"]
    assert sidecar["assurance_ceiling"] == "HARNESS_WIRED"
    assert any("do not themselves mutate GitHub production authority" in item for item in profile["known_owner_blockers"])


def test_evolution_engineer_is_candidate_builder_not_false_commit_proof():
    agents = _load("video_growth_agent/data/agents.json")["agents"]
    mandate = agents["evolution_engineer"]["mandate"]
    assert "candidate artifact" in mandate
    assert "not proof that production authority has changed" in mandate
    assert "owner maintenance path" in mandate
