import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_video_owns_business_identity_and_parent_reference_is_opaque():
    adapter = load(".uaos/ADAPTER.json")
    manifest = load(".uaos/MANIFEST.json")
    caps = load(".uaos/CAPABILITIES.json")

    assert adapter["controller_task_identity_authority"] == "UAOS"
    assert adapter["domain_business_identity_authority"] == "VIDEO_GROWTH_AGENT"
    assert "NO_EQUALITY_REQUIREMENT" in adapter["identity_boundary"]
    assert "OPAQUE_CHILD_STATE_REFERENCE_ONLY" in adapter["parent_reference_semantics"]
    assert adapter["session_activation"].startswith("DIRECT_VIDEO_WORK_PLANE")

    assert manifest["domain_authority"]["project_index"] == "projects/PROJECT_INDEX.json"
    assert manifest["domain_authority"]["product_requirements"] == "docs/product_requirements.md"
    assert manifest["runtime"]["program_orchestration"] == "video_growth_agent/program_orchestration.py"

    assert caps["profile_version"] == 7
    assert caps["uaos_common_capabilities_contract_min"] == "1.6.0"
    assert "domain_internal_work_orchestration" in caps["required_uaos_common_capabilities"]
    assert caps["hosted_cognition_semantics"]["problem_response_floor"] == [
        "MICRO_DIAGNOSIS",
        "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
        "GOVERNING_ASSUMPTION_CHALLENGE",
        "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
    ]


def test_generic_growth_commercialization_and_ip_intents_converge_on_integrated_program():
    index = load("projects/PROJECT_INDEX.json")
    assert index["authority"] == "VIDEO_GROWTH_AGENT"
    assert index["default_project_id"] == "ai-self-media-commercialization"
    by_id = {item["project_id"]: item for item in index["projects"]}

    integrated = by_id["ai-self-media-commercialization"]
    aliases = set(integrated["aliases"])
    assert {"AI自媒体视频商业化", "AI视频涨粉与商业化", "原创数字IP"} <= aliases
    assert integrated["default_for_generic_domain_intent"] is True

    pilot = by_id["pilot-002"]
    assert "video-growth:main" in pilot["aliases"]
    assert pilot["default_for_generic_domain_intent"] is False
    assert "not a UAOS task identity" in pilot["legacy_alias_semantics"]


def test_integrated_program_has_four_independent_business_workstreams_and_preserves_h1():
    program = load("projects/ai-self-media-commercialization/PROGRAM_STATE.json")
    assert program["program_id"] == "ai-self-media-commercialization"
    assert program["owner"] == "VIDEO_GROWTH_AGENT"
    assert set(program["workstreams"]) == {
        "MEDIA_GROWTH",
        "ORIGINAL_DIGITAL_IP",
        "COMMERCIALIZATION",
        "PRODUCTION_SYSTEM",
    }
    assert program["current_focus"] == "ORIGINAL_DIGITAL_IP/H1_SCULPTURAL_MASSING_V2"
    assert "A2 positive-morph upper-face edit" in program["current_next_action"]
    assert program["workstreams"]["MEDIA_GROWTH"]["blocked_by"] == []
    assert program["workstreams"]["COMMERCIALIZATION"]["blocked_by"] == []


def test_coordination_policy_requires_bounded_artifact_mediated_decision_work():
    policy = load("video_growth_agent/data/coordination-policy.json")
    assert policy["peer_chat_allowed"] is False
    assert policy["artifact_handoffs_required"] is True
    assert policy["dependency_model"]["cycle_policy"] == "REJECT_CONFIGURATION"
    assert policy["competition_contract"]["candidate_count_min"] == 2
    assert policy["competition_contract"]["decision_receipt_required"] is True
    assert policy["competition_contract"]["same_context_diversity_is_independent_verification"] is False
    assert policy["negotiation_contract"]["unbounded_peer_chat"] is False
    assert policy["negotiation_contract"]["implicit_authority_transfer"] is False


def test_pilot002_is_exact_child_historical_project_not_parent_task():
    pilot = load("projects/pilot-002/PROGRAM_STATE.json")
    assert pilot["project_id"] == "pilot-002"
    assert pilot["owner"] == "VIDEO_GROWTH_AGENT"
    assert "video-growth:main" in pilot["legacy_aliases"]
    assert "UAOS task identity" in pilot["legacy_alias_semantics"]
    assert "controller_authority" not in pilot
    assert "controller_task_ref" not in pilot
    assert pilot["stage_state"]["previous_release_candidate"] == "REJECTED_BY_USER_FOR_INSUFFICIENT_QUALITY"
    assert pilot["stage_state"]["quality_critical_generation_gateway"] == "UNAVAILABLE_FAIL_CLOSED"
