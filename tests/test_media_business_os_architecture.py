import json
from pathlib import Path

from video_growth_agent import (
    EvidenceBoundModelRouter,
    ShotContract,
    admit_candidate_generation,
    evaluate_take_promotion,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_media_business_os_is_primary_architecture_and_legacy_stage_machine_is_adapter():
    manifest = load(".uaos/MANIFEST.json")
    plan = load("video_growth_agent/data/execution-plan.json")
    assert manifest["domain_authority"]["architecture"] == "docs/media_business_os.md"
    assert plan["policy"]["architecture_role"] == "LEGACY_AND_SPECIALIZED_EPISODE_EXECUTION_ADAPTER_UNDER_MEDIA_BUSINESS_OS"
    text = (ROOT / "docs/media_business_os.md").read_text(encoding="utf-8")
    assert "Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take" in text
    assert "The legacy stage/work-order engine remains a historical/specialized compatibility adapter" in text
    assert "Status: `CANDIDATE_0_8_0`" in text


def test_current_program_has_explicit_cross_workstream_flywheel():
    flywheel = load("projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json")
    loop_ids = {item["id"] for item in flywheel["loops"]}
    assert "IP_TO_GROWTH" in loop_ids
    assert "COMMERCIAL_TO_PRODUCTION" in loop_ids
    assert "PRODUCTION_TO_PORTFOLIO" in loop_ids
    assert "COMMERCIAL_OUTCOME_TO_OFFER" in loop_ids
    assert "ALL_OUTCOMES_TO_EVOLUTION" in loop_ids
    assert any("No single metric" in item for item in flywheel["invariants"])


def test_provider_architecture_is_capability_evidence_based_not_named_default():
    caps = load(".uaos/CAPABILITIES.json")
    router = next(item for item in caps["capabilities"] if item["capability_id"] == "evidence_bound_model_routing")
    assert router["executor_ref"].startswith("video_growth_agent/model_registry.py")
    assert "current_provider_observations" in router["required_tools"]
    assert EvidenceBoundModelRouter
    benchmark = (ROOT / "docs/provider_benchmark_protocol.md").read_text(encoding="utf-8")
    assert "does **not** establish our production quality score" in benchmark


def test_candidate_generation_promotion_release_are_three_distinct_api_boundaries():
    assert ShotContract
    assert admit_candidate_generation
    assert evaluate_take_promotion
    text = (ROOT / "docs/media_business_os.md").read_text(encoding="utf-8")
    assert "generation admission != asset promotion != release admission" in text


def test_video_common_behavior_1_2_is_owner_native_and_evolution_is_discoverable():
    caps = load(".uaos/CAPABILITIES.json")
    evolution = load("audits/EVOLUTION_INDEX.json")
    assert caps["uaos_common_behavior_assurance_min"] == "1.2.0"
    assert caps["common_behavior_realization"] == "OWNER_NATIVE_RECOVERY_RECEIPT__USER_ESCALATION_ADMISSION__PROBLEM_REPAIR_OR_BLOCK_CLOSURE"
    assert evolution["owner"] == "DOMAIN:video"
    assert evolution["common_behavior_assurance_min"] == "1.2.0"
    assert evolution["current_open_items"] == ["V-20261015-02-AGENT_OPERABLE_MEDIA_OS"]
    assert evolution["current_problem_refs"] == {
        "V-20261015-02-AGENT_OPERABLE_MEDIA_OS": "audits/VIDEO_AGENT_OPERABILITY_REDESIGN_2026-10-15.md"
    }
    resolved = {
        item.get("id"): item for item in evolution["recent_resolved_or_promoted"] if item.get("id")
    }
    item = resolved["V-20261015-01-AI_NATIVE_MEDIA_BUSINESS_OS_REDESIGN"]
    assert item["status"] == "RESOLVED_PRODUCTION_0_7_0"
    assert item["release"] == "0.7.0"
    assert item["production_commit"] == "ad51bb76188eb0184cf8434384109c5c1257a60c"
    assert item["production_ci_run"] == 38690550495


def test_h1_business_cursor_is_preserved_during_system_rebuild():
    state = load("projects/ai-self-media-commercialization/PROGRAM_STATE.json")
    assert state["current_focus"] == "ORIGINAL_DIGITAL_IP/H1_SCULPTURAL_MASSING_V2"
    assert "A2 positive-morph upper-face edit" in state["current_next_action"]
    assert "must not advance this creative action automatically" in state["current_next_action"]
    assert state["workstreams"]["PRODUCTION_SYSTEM"]["status"] == "ACTIVE_MEDIA_BUSINESS_OS_0_7_PRODUCTION"
