import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_STATE = ROOT / "projects" / "pilot-002" / "PROGRAM_STATE.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_version() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def test_uaos_is_the_only_current_cross_chat_controller_surface():
    manifest = load_json(ROOT / ".uaos" / "MANIFEST.json")
    adapter = load_json(ROOT / ".uaos" / "ADAPTER.json")
    assert manifest["controller"] == "D1traverser-debug/universal-agent-os@main"
    assert manifest["status"] == "UAOS_CONTROL_PLANE_ACTIVE"
    assert manifest["skill"]["entrypoint"] == "UAOS_SKILL.md"
    assert manifest["runtime"]["version"] == runtime_version()
    assert adapter["task_identity_authority"] == "UAOS"
    assert adapter["cross_chat_continuity_authority"] == "UAOS"
    assert adapter["legacy_controller_compatibility"] == "NONE"
    assert adapter["old_lease_resume_protocol"] == "NOT_SUPPORTED"
    assert not (ROOT / "continuity").exists()


def test_current_capability_profile_preserves_execution_contract_without_old_controller():
    profile = load_json(ROOT / ".uaos" / "CAPABILITIES.json")
    assert profile["execution_readiness_contract"] == "2.0"
    assert profile["owner"] == "VIDEO_GROWTH_AGENT"
    assert set(profile["assurance_taxonomy"]) == {
        "DECLARED_ONLY",
        "HARNESS_WIRED",
        "SESSION_EXECUTABLE",
        "CHAT_BRIDGED",
        "ATTESTED_ISOLATED",
    }
    ids = {item["capability_id"] for item in profile["capabilities"]}
    assert {
        "studio_work_order_orchestration",
        "ordinary_specialist_execution",
        "critical_blind_multimodal_review",
        "generation_preflight",
        "quality_critical_generation_gateway",
        "deterministic_media_qa",
        "asset_and_project_continuity",
        "learning_and_evolution",
    } <= ids
    gateway = next(item for item in profile["capabilities"] if item["capability_id"] == "quality_critical_generation_gateway")
    assert gateway["assurance_ceiling"] == "DECLARED_ONLY"
    assert gateway["executor_type"] == "UNAVAILABLE"
    assert gateway["safe_degraded_modes"] == []


def test_pilot002_program_state_preserves_business_truth_not_control_protocol():
    state = load_json(PROGRAM_STATE)
    assert state["schema_version"] == "1.0-uaos"
    assert state["program_id"] == "video-growth:main"
    assert state["controller_authority"] == "D1traverser-debug/universal-agent-os@main"
    assert state["controller_task_ref"] == "state/tasks/video-growth-main.json"
    assert state["runtime_version"] == runtime_version()
    assert state["status"] == "HOLD"
    assert state["resume_mode"] == "EXPLICIT_ONLY_VIA_UAOS"
    assert state["current_stage"] == "VISUAL_PREVIEW_PROCESS_REENTRY"
    assert state["stage_state"]["sample_v2_status"] == "PROCESS_INVALID_AND_VISUAL_FAIL"
    assert state["stage_state"]["production_trusted_reviewer_executors"] == "EMPTY_FAIL_CLOSED"
    assert state["stage_state"]["previous_release_gate_valid"] is False
    assert state["authoritative_artifacts"]["rejected_candidate_v4"]["sha256"] == "eec364e8530067dbc87a08a9ccbf2dd6e6e8a5ab32fb87f648c794a4000628eb"
    serialized = json.dumps(state, ensure_ascii=False)
    for retired in ("continuity_protocol_version", "resume_epoch", "active_lease", "Universal Continuity"):
        assert retired not in serialized


def test_generic_uaos_skill_has_no_project_state_pollution():
    text = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "current-session capability handshake" in lower
    assert "universal-agent-os@main" in text
    assert "ai-self-media-commercialization" not in lower
    assert "pilot-001" not in lower
    assert "pilot-002" not in lower
    assert "resume epoch" in lower
    assert "do not create" in lower
