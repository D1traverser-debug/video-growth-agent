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


def test_uaos_is_the_only_parent_controller_while_video_owns_business_identity():
    manifest = load_json(ROOT / ".uaos" / "MANIFEST.json")
    adapter = load_json(ROOT / ".uaos" / "ADAPTER.json")
    assert manifest["controller"] == "D1traverser-debug/universal-agent-os@main"
    assert manifest["status"] == "UAOS_CONTROL_PLANE_ACTIVE"
    assert manifest["skill"]["entrypoint"] == "UAOS_SKILL.md"
    assert manifest["runtime"]["version"] == runtime_version()

    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert adapter["domain_business_identity_authority"] == "VIDEO_GROWTH_AGENT"
    assert adapter["cross_chat_parent_continuity_authority"] == "UAOS_FOR_PARENT_OR_SELECTOR_CONTEXT"
    assert adapter["domain_business_continuity_authority"] == "VIDEO_GROWTH_AGENT"
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert "OPAQUE_CHILD_STATE_REFERENCE_ONLY" in adapter["parent_reference_semantics"]
    assert adapter["legacy_controller_compatibility"] == "NONE"
    assert adapter["old_lease_resume_protocol"] == "NOT_SUPPORTED"
    assert adapter["session_activation"].startswith("DIRECT_VIDEO_WORK_PLANE")
    assert not (ROOT / "continuity").exists()


def test_current_capability_profile_preserves_execution_contract_without_old_controller():
    profile = load_json(ROOT / ".uaos" / "CAPABILITIES.json")
    assert profile["execution_readiness_contract"] == "2.0"
    assert profile["owner"] == "VIDEO_GROWTH_AGENT"
    assert profile["profile_version"] == 7
    assert profile["uaos_common_capabilities_contract_min"] == "1.6.0"
    assert set(profile["assurance_taxonomy"]) == {
        "DECLARED_ONLY",
        "HARNESS_WIRED",
        "SESSION_EXECUTABLE",
        "CHAT_BRIDGED",
        "ATTESTED_ISOLATED",
    }
    ids = {item["capability_id"] for item in profile["capabilities"]}
    assert {
        "program_workstream_orchestration",
        "studio_work_order_orchestration",
        "ordinary_specialist_execution",
        "critical_blind_multimodal_review",
        "generation_preflight",
        "quality_critical_generation_gateway",
        "deterministic_media_qa",
        "asset_and_project_continuity",
        "learning_and_evolution",
        "domain_product_requirements_traceability",
    } <= ids
    gateway = next(item for item in profile["capabilities"] if item["capability_id"] == "quality_critical_generation_gateway")
    assert gateway["assurance_ceiling"] == "DECLARED_ONLY"
    assert gateway["executor_type"] == "UNAVAILABLE"
    assert gateway["safe_degraded_modes"] == []


def test_pilot002_program_state_preserves_business_truth_not_parent_control_protocol():
    state = load_json(PROGRAM_STATE)
    assert state["schema_version"] == "1.1"
    assert state["project_id"] == "pilot-002"
    assert state["owner"] == "VIDEO_GROWTH_AGENT"
    assert state["business_identity_authority"] == "projects/pilot-002/PROGRAM_STATE.json::project_id"
    assert "video-growth:main" in state["legacy_aliases"]
    assert "not a UAOS task identity" in state["legacy_alias_semantics"]
    assert state["runtime_version"] == runtime_version()
    assert state["status"] == "HOLD"
    assert state["resume_mode"] == "EXPLICIT_CHILD_PROJECT_REF"
    assert state["current_stage"] == "VISUAL_PREVIEW_PROCESS_REENTRY"
    assert state["stage_state"]["sample_v2_status"] == "PROCESS_INVALID_AND_VISUAL_FAIL"
    assert state["stage_state"]["production_trusted_reviewer_executors"] == "EMPTY_FAIL_CLOSED"
    assert state["stage_state"]["previous_release_gate_valid"] is False
    assert state["stage_state"]["quality_critical_generation_gateway"] == "UNAVAILABLE_FAIL_CLOSED"
    assert state["authoritative_artifacts"]["rejected_candidate_v4"]["sha256"] == "eec364e8530067dbc87a08a9ccbf2dd6e6e8a5ab32fb87f648c794a4000628eb"
    assert "controller_authority" not in state
    assert "controller_task_ref" not in state
    assert state["negative_space"]["uaos_controller_task_ref"] == "RETIRED_AS_BUSINESS_IDENTITY_AUTHORITY"
    assert state["negative_space"]["old_lease_resume_protocol"] == "NOT_SUPPORTED"


def test_generic_uaos_skill_routes_through_child_project_index_without_embedding_transient_project_state():
    text = (ROOT / "UAOS_SKILL.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "current-session capability handshake" in lower
    assert "universal-agent-os@main" in text
    assert "projects/project_index.json" in lower
    assert "exact historical child project references override generic routing" in lower
    assert "no parent/child id equality requirement" in lower
    assert "not unbounded peer chat" in lower
    assert "do not create a repository-local parent task index" in lower
    assert "h1_sculptural_massing" not in lower
    assert "a2 positive" not in lower
    assert "sample v2" not in lower
