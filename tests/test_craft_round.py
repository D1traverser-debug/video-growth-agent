"""Cross-craft collaboration is an auditable proposal, never pretend review."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from video_growth_agent.craft_round import (
    CraftReviewError, REVIEWERS, next_revision_diff,
    prepare_craft_round, reconcile_craft_round,
)
from video_growth_agent.prompt_director import PromptPlanError
from video_growth_agent.techniques import TechniqueLibrary

FIX = Path(__file__).parent / "fixtures"


def load(name="prompt_ribbon_fullsource_10s.json"):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def reviews_for(packet):
    return [{
        "reviewer_role": order["reviewer_role"],
        "source_plan_digest": packet["source_plan_digest"],
        "verdict": "ACCEPT_PLAN",
        "artifact_ref": f"test-only://mock-plan-review/{order['reviewer_role']}",
        "observed_scope": "PLAN_ONLY",
        "review_method": "synthetic in unit test; no actual agent or reviewer executed",
        "findings": [],
    } for order in packet["orders"]]


def complaint(*, category="EDIT", shot="R3", severity="MAJOR"):
    return {
        "shot_id": shot,
        "category": category,
        "severity": severity,
        "observation": "The cut may hide ribbon's physical contact",
        "evidence_ref": "source-plan://shot/R3:action/trigger",
        "change_request": "Leave the index/middle finger catch readable in the edit",
    }


@pytest.mark.parametrize("name", ["prompt_ribbon_fullsource_10s.json", "prompt_ip_5s.json"])
def test_existing_roles_prepare_unexecuted_independent_review_packets(name):
    packet = prepare_craft_round(load(name))
    assert len(packet["orders"]) == 7
    assert {x["reviewer_role"] for x in packet["orders"]} == set(REVIEWERS)
    assert all(o["status"] == "NOT_EXECUTED" for o in packet["orders"])
    assert all(o["review_input"]["other_reviewers_opinions"] is None for o in packet["orders"])
    assert all(o["role_mandate"] and o["source_plan_digest"] == packet["source_plan_digest"]
               for o in packet["orders"])
    assert packet["execution_status"] == "PREPARED_NOT_REVIEWED"
    assert {x["id"] for x in packet["candidate_techniques"]} >= {"T-015", "T-016", "T-017"}
    assert all(x["status"] == "candidate" for x in packet["candidate_techniques"]
               if x["id"] in {"T-015", "T-016", "T-017"})
    assert prepare_craft_round(load(name))["source_plan_digest"] == packet["source_plan_digest"]


def test_handoff_routes_contradictory_edit_sound_art_feedback_to_distinct_owners():
    packet = prepare_craft_round(load())
    submitted = reviews_for(packet)
    for role, item in [
        ("editor", complaint(category="EDIT")),
        ("sound_director", complaint(category="SOUND")),
        ("art_director", complaint(category="ART")),
    ]:
        review = next(x for x in submitted if x["reviewer_role"] == role)
        review["verdict"] = "REVISE_PLAN"
        review["findings"].append(item)
    report = reconcile_craft_round(packet, submitted)
    assert report["status"] == "REVISION_REQUIRED"
    assert report["showrunner_resolution_required"] is True
    assert report["artifact_promotion"] == "NOT_AUTHORIZED"
    assert report["learning_promotion"] == "NOT_AUTHORIZED"
    assert {x["assigned_owner"] for x in report["issues"]} == {
        "editor", "sound_director", "art_director",
    }
    assert report["reviewer_independence"] == "NOT_ESTABLISHED"


def test_mock_reviews_never_prove_people_executed_independent_assessment():
    packet = prepare_craft_round(load())
    report = reconcile_craft_round(packet, reviews_for(packet))
    assert report["status"] == "PLAN_REVIEW_REPORTED_CLEAN__INDEPENDENCE_NOT_ESTABLISHED"
    assert report["artifact_promotion"] == "NOT_AUTHORIZED"
    assert report["reviewer_independence"] == "NOT_ESTABLISHED"


def test_plan_version_and_duplicate_review_fail_closed():
    packet = prepare_craft_round(load())
    submitted = reviews_for(packet)
    submitted[0]["source_plan_digest"] = "sha256:forged"
    with pytest.raises(CraftReviewError, match="wrong plan version"):
        reconcile_craft_round(packet, submitted)
    submitted = reviews_for(packet)
    submitted[1]["reviewer_role"] = submitted[0]["reviewer_role"]
    with pytest.raises(CraftReviewError, match="duplicated"):
        reconcile_craft_round(packet, submitted)
    with pytest.raises(CraftReviewError, match="one report"):
        reconcile_craft_round(packet, submitted[:-1])


def test_false_rendered_media_report_blocked_and_no_empty_veto():
    packet = prepare_craft_round(load())
    submitted = reviews_for(packet)
    submitted[0]["observed_scope"] = "RENDERED_MEDIA"
    with pytest.raises(CraftReviewError, match="existing video review"):
        reconcile_craft_round(packet, submitted)
    submitted = reviews_for(packet)
    submitted[0]["verdict"] = "BLOCKED"
    with pytest.raises(CraftReviewError, match="falsifiable findings"):
        reconcile_craft_round(packet, submitted)
    submitted[0]["findings"] = [complaint()]
    submitted[0]["findings"][0]["evidence_ref"] = "TODO"
    with pytest.raises(CraftReviewError, match="evidence"):
        reconcile_craft_round(packet, submitted)


def test_finding_shot_integrity_prevents_misrouted_change():
    packet = prepare_craft_round(load())
    submitted = reviews_for(packet)
    submitted[0]["verdict"] = "REVISE_PLAN"
    submitted[0]["findings"] = [complaint(shot="HALLUCINATED_SHOT")]
    with pytest.raises(CraftReviewError, match="unknown shot"):
        reconcile_craft_round(packet, submitted)


def test_revision_trace_preserves_source_identity_and_never_claims_improvement():
    original = load()
    changed = copy.deepcopy(original)
    changed["shots"][2]["transition"]["bridge"] += " (keep hand contact visible)"
    result = next_revision_diff(original, changed)
    assert result["from_digest"] != result["to_digest"]
    assert result["shot_changes"] == [{"shot_id": "R3", "action": "CHANGED"}]
    assert result["next_review_required"] is True
    assert "not automatically approved" in result["verification"]
    with pytest.raises(CraftReviewError, match="did not change"):
        next_revision_diff(original, original)
    swapped = copy.deepcopy(changed)
    swapped["source"]["raw"] += " injected fiction"
    with pytest.raises(CraftReviewError, match="source must not change"):
        next_revision_diff(original, swapped)
    changed["source"]["reference"] = "fake://source"
    with pytest.raises(CraftReviewError, match="source must not change"):
        next_revision_diff(original, changed)


def test_cli_prepares_craft_role_packets_without_automatically_reviewing():
    cmd = [sys.executable, "-m", "video_growth_agent.cli",
           "craft-round", str(FIX / "prompt_ip_5s.json")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    packet = json.loads(result.stdout)["packet"]
    assert len(packet["orders"]) == 7
    assert packet["execution_status"] == "PREPARED_NOT_REVIEWED"


def test_learning_candidates_use_existing_library_not_new_registry():
    lib = TechniqueLibrary()
    for ref in ("T-015", "T-016", "T-017"):
        tech = lib.get(ref)
        assert tech.status == "candidate"
        assert tech.use_when and tech.avoid_when
        assert tech.evidence_refs
    assert {x.technique_id for x in lib.find(
        {"review", "revision", "editing"}, validated_only=True
    )}.isdisjoint({"T-015", "T-016", "T-017"})
