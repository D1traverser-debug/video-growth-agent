import json
from pathlib import Path

from video_growth_agent.editorial_packaging import audit_packaging, copy_digest, SEMANTIC_TESTS

CASE = (Path(__file__).resolve().parents[1] / "projects" /
        "ai-self-media-commercialization" / "cases" / "jensen-alice-20261114.json")

def fixture():
    return json.loads(CASE.read_text(encoding="utf-8"))

def test_seven_platform_example_valid_but_not_release_ready():
    result = audit_packaging(fixture())
    assert result["contract_valid"], result["errors"]
    assert result["platform_count"] == 7
    assert result["status"] == "EDITORIAL_CANDIDATE_GATES_OPEN"
    assert result["release_authorized"] is False
    assert result["semantic_quality_proven"] is False
    assert any("media_identity_unverified" in x for x in result["open_gates"])

def test_platform_candidates_are_not_seven_synonymous_templates():
    items = fixture()["platform_copies"]
    assert len({x["editorial_angle"] for x in items}) >= 4
    assert len({x["humor_mechanism"] for x in items}) >= 4
    assert all(x["news_counterfactual"] and x["video_counterfactual"] for x in items)

def test_missing_news_anchor_is_contract_error():
    case = fixture()
    case["platform_copies"][0]["fact_ids"] = ["not-a-fact"]
    assert "copy[0]:fact_ref_missing_or_unknown" in audit_packaging(case)["errors"]

def test_missing_visual_anchor_is_contract_error():
    case = fixture()
    case["platform_copies"][0]["visual_ids"] = ["not-an-asset"]
    assert "copy[0]:visual_ref_missing_or_unknown" in audit_packaging(case)["errors"]

def test_fiction_is_not_real_news():
    case = fixture()
    case["fiction_is_not_real_world_evidence"] = False
    assert "fiction_news_boundary_missing" in audit_packaging(case)["errors"]

def test_unverified_allegation_remains_attributed():
    case = fixture()
    case["platform_copies"][0]["fact_ids"].append("F4")
    assert "copy[0]:allegation_framing_not_protected" in audit_packaging(case)["errors"]
    case["platform_copies"][0]["allegation_framing"] = "ATTRIBUTED_UNVERIFIED"
    assert "copy[0]:allegation_framing_not_protected" not in audit_packaging(case)["errors"]

def test_model_self_review_never_counts_as_independent_human():
    case = fixture()
    case["platform_copies"][0]["independent_review"] = {"status": "MODEL_PLAN_ONLY"}
    result = audit_packaging(case)
    assert result["independent_human_reviews_recorded"] == 0
    assert "copy[0]:semantic_review_open" in result["open_gates"]

def valid_review(item):
    return {
        "status": "PASS", "reviewer_kind": "HUMAN",
        "reviewer_ref": "reviewer://external-1",
        "evidence_ref": "receipt://external-copy-review",
        "copy_sha256": copy_digest(item),
        "semantic_checks": {key: True for key in SEMANTIC_TESTS},
    }

def test_copy_revision_invalidates_review_digest():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(item)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    item["title"] += " changed"
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]

def test_author_cannot_attest_own_editorial_copy():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(item)
    item["independent_review"]["reviewer_ref"] = case["author_ref"]
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]

def test_failed_counterfactual_cannot_be_signed_pass():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(item)
    item["independent_review"]["semantic_checks"]["video_replacement_loses_meaning"] = False
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]

def test_claimed_reviews_never_override_real_release_gate():
    case = fixture()
    for index, item in enumerate(case["platform_copies"]):
        item["independent_review"] = valid_review(item)
        item["independent_review"]["reviewer_ref"] = f"reviewer://external-{index}"
    result = audit_packaging(case)
    assert result["contract_valid"]
    assert result["independent_human_reviews_recorded"] == 7
    assert result["release_authorized"] is False
    assert result["semantic_quality_proven"] is False
    assert "master_timeline_version_unbound" in result["open_gates"]

def test_malformed_data_fails_closed():
    for case in ({}, {"source_facts": "bad", "visual_assets": [7], "platform_copies": [None]},
                 {"source_facts": [{}], "visual_assets": [{}], "platform_copies": [{}]}):
        result = audit_packaging(case)
        assert result["status"] == "INVALID_CONTRACT"
        assert not result["release_authorized"]
