import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def semver_at_least(actual: str, minimum: str) -> bool:
    left = tuple(int(part) for part in actual.split("."))
    right = tuple(int(part) for part in minimum.split("."))
    width = max(len(left), len(right))
    return left + (0,) * (width - len(left)) >= right + (0,) * (width - len(right))


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
    assert manifest["domain_authority"]["architecture"] == "docs/media_business_os.md"
    assert manifest["domain_authority"]["integrated_business_flywheel"] == "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json"
    assert manifest["runtime"]["program_orchestration"] == "video_growth_agent/program_orchestration.py"
    assert manifest["runtime"]["media_business_os"] == "video_growth_agent/production_os.py"

    # Capability/profile bindings are compatibility floors, not immutable release identities.
    assert caps["profile_version"] >= 10
    assert semver_at_least(caps["uaos_common_capabilities_contract_min"], "1.6.0")
    assert semver_at_least(caps["uaos_common_behavior_assurance_min"], "1.3.0")
    assert "domain_internal_work_orchestration" in caps["required_uaos_common_capabilities"]
    assert caps["uaos_deliberation_policy_ref"].endswith("config/DELIBERATION_POLICY.json")
    cognition = caps["hosted_cognition_semantics"]
    assert cognition == {
        "source": "CURRENT_UAOS_DELIBERATION_POLICY",
        "local_overrides": "NONE",
    }
    assert "problem_response_floor" not in cognition
    assert "problem_response_rule" not in cognition


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


def test_integrated_program_couples_four_business_workstreams_and_preserves_h1_cursor():
    program = load("projects/ai-self-media-commercialization/PROGRAM_STATE.json")
    flywheel = load("projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json")
    manifest = load("projects/ai-self-media-commercialization/PROJECT_MANIFEST.json")

    assert program["program_id"] == "ai-self-media-commercialization"
    assert program["owner"] == "VIDEO_GROWTH_AGENT"
    assert set(program["workstreams"]) == {
        "MEDIA_GROWTH",
        "ORIGINAL_DIGITAL_IP",
        "COMMERCIALIZATION",
        "PRODUCTION_SYSTEM",
    }
    assert program["business_flywheel_ref"].endswith("BUSINESS_FLYWHEEL.json")
    assert manifest["business_flywheel_ref"] == "BUSINESS_FLYWHEEL.json"
    assert program["current_focus"] == "ORIGINAL_DIGITAL_IP/H1_SCULPTURAL_MASSING_V2"
    assert "A2 positive-morph upper-face edit" in program["current_next_action"]
    assert "must not advance this creative action automatically" in program["current_next_action"]
    assert program["workstreams"]["MEDIA_GROWTH"]["blocked_by"] == []
    assert program["workstreams"]["COMMERCIALIZATION"]["blocked_by"] == []

    loop_ids = {item["id"] for item in flywheel["loops"]}
    assert {
        "AUDIENCE_TO_PORTFOLIO",
        "PORTFOLIO_TO_IP",
        "IP_TO_GROWTH",
        "PORTFOLIO_TO_COMMERCIAL",
        "COMMERCIAL_TO_PRODUCTION",
        "IP_TO_PRODUCTION",
        "PRODUCTION_TO_PORTFOLIO",
        "PERFORMANCE_TO_IP",
        "COMMERCIAL_OUTCOME_TO_OFFER",
        "ALL_OUTCOMES_TO_EVOLUTION",
    } <= loop_ids


def test_coordination_policy_separates_business_asset_and_timeline_graphs_and_promotion():
    policy = load("video_growth_agent/data/coordination-policy.json")
    assert policy["peer_chat_allowed"] is False
    assert policy["artifact_handoffs_required"] is True
    assert policy["dependency_model"]["cycle_policy"] == "REJECT_CONFIGURATION"
    assert policy["competition_contract"]["candidate_count_min"] == 2
    assert policy["competition_contract"]["decision_receipt_required"] is True
    assert policy["competition_contract"]["same_context_diversity_is_independent_verification"] is False
    assert policy["negotiation_contract"]["unbounded_peer_chat"] is False
    assert policy["negotiation_contract"]["implicit_authority_transfer"] is False
    assert policy["object_graph_semantics"] == "PROGRAM_BUSINESS_GRAPH__MEDIA_ASSET_CONTEXT_GRAPH__EDITORIAL_TIMELINE_ARE_DISTINCT_BUT_LINKED"
    candidate = policy["media_candidate_contract"]
    assert candidate["candidate_generation_is_acceptance"] is False
    assert candidate["promotion_decision_required_for_accepted_asset"] is True
    assert candidate["release_decision_separate_from_asset_promotion"] is True


def test_media_business_docs_reject_vendor_lockin_scalar_quality_and_stage_role_overfit():
    architecture = (ROOT / "docs" / "media_business_os.md").read_text(encoding="utf-8")
    requirements = (ROOT / "docs" / "product_requirements.md").read_text(encoding="utf-8")
    benchmark = (ROOT / "docs" / "provider_benchmark_protocol.md").read_text(encoding="utf-8")

    assert "Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take" in architecture
    assert "generation admission != asset promotion != release admission" in architecture
    assert "no single-vendor production lock-in" in architecture
    assert "Quality is not collapsed into one hidden weighted average" in architecture
    assert "Legacy work-order/attestation/QA" in requirements
    assert "Official documentation can establish" in benchmark
    assert "does **not** establish our production quality score" in benchmark


def test_pilot002_is_exact_historical_project_and_rejection_truth_survives_migration():
    pilot = load("projects/pilot-002/PROGRAM_STATE.json")
    assert pilot["project_id"] == "pilot-002"
    assert pilot["owner"] == "VIDEO_GROWTH_AGENT"
    assert "video-growth:main" in pilot["legacy_aliases"]
    assert "UAOS task identity" in pilot["legacy_alias_semantics"]
    assert "controller_authority" not in pilot
    assert "controller_task_ref" not in pilot
    assert pilot["stage_state"]["previous_release_candidate"] == "REJECTED_BY_USER_FOR_INSUFFICIENT_QUALITY"
    assert pilot["stage_state"]["previous_release_gate_valid"] is False
    assert "CANDIDATE_GENERATION_ALLOWED_ONLY_AFTER_CURRENT_0_7_ADMISSION" in pilot["stage_state"]["shot_a_status"]
    assert "PROMOTION_BLOCKED_UNTIL_REQUIRED_REVIEW" in pilot["stage_state"]["shot_d_status"]
