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
    assert manifest["binding"]["common_behavior_assurance_min"] == "1.3.0"
    assert manifest["runtime"]["version"] == runtime_version() == "0.8.0"
    assert manifest["runtime"]["media_graph"] == "video_growth_agent/media_graph.py"
    assert manifest["runtime"]["editorial_planning"] == "video_growth_agent/editorial_planning.py"
    assert manifest["runtime"]["plan_graph_bridge"] == "video_growth_agent/plan_graph_bridge.py"
    assert manifest["runtime"]["media_business_os"] == "video_growth_agent/production_os.py"
    assert manifest["runtime"]["continuity"] == "video_growth_agent/continuity.py"
    assert manifest["runtime"]["timeline"] == "video_growth_agent/timeline.py"
    assert manifest["runtime"]["editorial_interchange"] == "video_growth_agent/editorial_interchange.py"
    assert manifest["runtime"]["experiments"] == "video_growth_agent/experiments.py"
    assert manifest["runtime"]["business_objects"] == "video_growth_agent/business_objects.py"
    assert manifest["runtime"]["model_registry"] == "video_growth_agent/model_registry.py"
    assert manifest["runtime"]["operator_view"] == "video_growth_agent/operator_view.py"
    assert manifest["runtime"]["root_scope_admission"].endswith("require_root_scope_admission")
    assert manifest["runtime"]["legacy_adapter_bundle_version"] == "0.7.0"
    assert manifest["domain_authority"]["architecture"] == "docs/media_business_os.md"
    assert manifest["domain_authority"]["agent_operability_scenarios"] == "docs/agent_operability_scenarios.md"
    assert manifest["domain_authority"]["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"

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


def test_current_capability_profile_exposes_agent_operable_media_os_and_common_behavior_1_3():
    profile = load_json(ROOT / ".uaos" / "CAPABILITIES.json")
    assert profile["execution_readiness_contract"] == "2.0"
    assert profile["owner"] == "VIDEO_GROWTH_AGENT"
    assert profile["profile_version"] >= 10
    assert profile["uaos_common_capabilities_contract_min"] == "1.6.0"
    assert profile["uaos_common_behavior_assurance_min"] == "1.3.0"
    assert "ROOT_SCOPE_ADMISSION" in profile["common_behavior_realization"]
    assert "TYPED_EVOLUTION_DISPOSITION" in profile["common_behavior_realization"]
    assert profile["canonical_evolution_entrypoint"] == "audits/EVOLUTION_INDEX.json"
    assert profile["agent_operability_scenarios_ref"] == "docs/agent_operability_scenarios.md"
    assert set(profile["assurance_taxonomy"]) == {
        "DECLARED_ONLY",
        "HARNESS_WIRED",
        "SESSION_EXECUTABLE",
        "CHAT_BRIDGED",
        "ATTESTED_ISOLATED",
    }
    ids = {item["capability_id"] for item in profile["capabilities"]}
    assert {
        "media_business_program_orchestration",
        "canonical_media_graph",
        "editorial_planning_and_traceability",
        "shot_asset_production_os",
        "cross_shot_continuity",
        "non_destructive_editorial_timeline",
        "editor_interchange_roundtrip",
        "shared_growth_ip_commercial_objects",
        "evidence_bound_model_routing",
        "experiment_governance",
        "business_outcome_measurement",
        "current_agent_operator_projection",
        "owner_common_behavior_admission",
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
    owner_behavior = next(item for item in profile["capabilities"] if item["capability_id"] == "owner_common_behavior_admission")
    contract = " ".join(owner_behavior["evidence_contract"])
    assert "root-scope receipt" in contract
    assert "typed evolution disposition" in contract
    assert "current-agent operability/dogfood evidence" in contract
    gateway = next(item for item in profile["capabilities"] if item["capability_id"] == "quality_critical_generation_gateway")
    assert gateway["assurance_ceiling"] == "DECLARED_ONLY"
    assert gateway["executor_type"] == "CURRENT_SESSION_EXTERNAL_MEDIA_CAPABILITY"
    assert gateway["safe_degraded_modes"] == ["BLOCK_ONLY_AFFECTED_SHOT_OR_USE_DECLARED_GRACEFUL_DEGRADATION"]


def test_pilot002_preserves_rejection_truth_and_remains_legacy_adapter_project():
    state = load_json(PROGRAM_STATE)
    manifest = load_json(ROOT / ".uaos" / "MANIFEST.json")
    assert state["schema_version"] == "1.2"
    assert state["project_id"] == "pilot-002"
    assert state["owner"] == "VIDEO_GROWTH_AGENT"
    assert state["business_identity_authority"] == "projects/pilot-002/PROGRAM_STATE.json::project_id"
    assert "video-growth:main" in state["legacy_aliases"]
    assert "not a UAOS task identity" in state["legacy_alias_semantics"]
    assert state["runtime_version"] == manifest["runtime"]["legacy_adapter_bundle_version"] == "0.7.0"
    assert state["status"] == "HOLD"
    assert state["resume_mode"] == "EXPLICIT_CHILD_PROJECT_REF"
    assert state["current_stage"] == "VISUAL_PREVIEW_PROCESS_REENTRY"
    assert state["stage_state"]["sample_v2_status"] == "PROCESS_INVALID_AND_VISUAL_FAIL"
    assert state["stage_state"]["production_trusted_reviewer_executors"] == "EMPTY_ATTESTED_ISOLATED_TIER_UNAVAILABLE"
    assert state["stage_state"]["previous_release_gate_valid"] is False
    assert "CANDIDATE_GENERATION_ALLOWED_ONLY_AFTER_CURRENT_0_7_ADMISSION" in state["stage_state"]["shot_a_status"]
    assert "PROMOTION_BLOCKED_UNTIL_REQUIRED_REVIEW" in state["stage_state"]["shot_d_status"]
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
    assert "candidate generation, project-asset promotion and release are separate boundaries" in lower
    assert "common behavior 1.3" in lower
    assert "root-scope receipt" in lower
    assert "typed evolution disposition" in lower
    assert "audits/evolution_index.json" in lower
    assert "h1_sculptural_massing" not in lower
    assert "a2 positive" not in lower
    assert "sample v2" not in lower
