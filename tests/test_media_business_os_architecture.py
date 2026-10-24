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


def version_at_least(actual: str, minimum: str) -> bool:
    return tuple(int(part) for part in actual.split(".")) >= tuple(
        int(part) for part in minimum.split(".")
    )


def test_media_business_os_is_primary_architecture_and_legacy_stage_machine_is_adapter():
    manifest = load(".uaos/MANIFEST.json")
    plan = load("video_growth_agent/data/execution-plan.json")
    assert manifest["domain_authority"]["architecture"] == "docs/media_business_os.md"
    assert plan["policy"]["architecture_role"] == "LEGACY_AND_SPECIALIZED_EPISODE_EXECUTION_ADAPTER_UNDER_MEDIA_BUSINESS_OS"
    text = (ROOT / "docs/media_business_os.md").read_text(encoding="utf-8")
    assert "Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take" in text
    assert "The legacy stage/work-order engine remains a historical/specialized compatibility adapter" in text
    assert "Status: `PRODUCTION_0_8_0`" in text


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


def test_video_common_behavior_1_3_is_owner_native_and_evolution_is_discoverable_across_lifecycle():
    caps = load(".uaos/CAPABILITIES.json")
    evolution = load("audits/EVOLUTION_INDEX.json")
    assert version_at_least(caps["uaos_common_behavior_assurance_min"], "1.3.0")
    assert "ROOT_SCOPE_ADMISSION" in caps["common_behavior_realization"]
    assert "TYPED_EVOLUTION_DISPOSITION" in caps["common_behavior_realization"]
    assert evolution["owner"] == "DOMAIN:video"
    assert version_at_least(evolution["common_behavior_assurance_min"], "1.3.0")

    adoption_id = "V-20261016-03-COMMON-BEHAVIOR-1-3-ROOT-SCOPE-ADOPTION"
    resolved = {
        item.get("id"): item for item in evolution["recent_resolved_or_promoted"] if item.get("id")
    }

    if adoption_id in evolution["current_open_items"]:
        assert evolution["current_problem_refs"][adoption_id] == "video_growth_agent/owner_behavior_admission.py"
        candidate = evolution["current_candidate"]
        assert candidate["id"] == adoption_id
        assert candidate["status"].startswith("CANDIDATE_IMPLEMENTED")
        assert "CURRENT_AGENT_OPERABILITY_DOGFOOD" in candidate["selected_architecture"]
    else:
        # The 1.3 adoption was promoted; a later independent Video candidate
        # (for example PR #23) must not be mistaken for a reopened 1.3 adoption.
        candidate = evolution["current_candidate"]
        assert candidate is None or candidate.get("id") != adoption_id
        promoted = resolved[adoption_id]
        assert promoted["status"].startswith("PROMOTED__PRODUCTION_CI_VERIFIED")
        assert promoted["candidate_pr"] == 18
        assert promoted["candidate_final_head"] == "62181bfded6170e002ac1a6a155e1d2f3cf812bd"
        assert promoted["candidate_ci_run"] == 38831027488
        assert promoted["production_commit"] == "777f87f0257d7347092e12d0b7f78168eae80897"
        assert promoted["production_ci_run"] == 38831237031
        assert promoted["result"] == "PASS"

    current = resolved["V-20261015-02-AGENT_OPERABLE_MEDIA_OS"]
    assert current["status"] == "RESOLVED_PRODUCTION_0_8_0"
    assert current["release"] == "0.8.0"
    assert current["production_commit"] == "02d39d8e3609c6d988009f4bc5a7f5d0378128ec"
    assert current["production_ci_run"] == 38725890405
    prior = resolved["V-20261015-01-AI_NATIVE_MEDIA_BUSINESS_OS_REDESIGN"]
    assert prior["status"].startswith("RESOLVED_PRODUCTION_0_7_0")
    assert prior["release"] == "0.7.0"
    assert prior["production_commit"] == "ad51bb76188eb0184cf8434384109c5c1257a60c"
    assert prior["production_ci_run"] == 38690550495


def test_h1_business_cursor_is_preserved_during_system_rebuild():
    state = load("projects/ai-self-media-commercialization/PROGRAM_STATE.json")
    assert state["current_focus"] == "ORIGINAL_DIGITAL_IP/H1_SCULPTURAL_MASSING_V2"
    assert "A2 positive-morph upper-face edit" in state["current_next_action"]
    assert "must not advance this creative action automatically" in state["current_next_action"]
    assert state["workstreams"]["PRODUCTION_SYSTEM"]["status"] == "MEDIA_BUSINESS_OS_0_8_PRODUCTION_BASELINE"
