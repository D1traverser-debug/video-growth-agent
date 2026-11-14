import json
from pathlib import Path

from video_growth_agent.editorial_packaging import (
    SEMANTIC_TESTS,
    audit_packaging,
    review_digest,
)

CASE = (Path(__file__).resolve().parents[1] / "projects" /
        "ai-self-media-commercialization" / "cases" / "jensen-alice-20261114.json")


def fixture():
    return json.loads(CASE.read_text(encoding="utf-8"))


def valid_review(case, item, reviewer_ref="reviewer://external-1"):
    return {
        "status": "PASS",
        "reviewer_kind": "HUMAN",
        "reviewer_ref": reviewer_ref,
        "evidence_ref": "receipt://external-copy-review",
        "copy_sha256": review_digest(case, item),
        "semantic_checks": {key: True for key in SEMANTIC_TESTS},
    }


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
    assert "copy[0]:fact_ref_missing_unknown_or_duplicate" in audit_packaging(case)["errors"]


def test_missing_visual_anchor_is_contract_error():
    case = fixture()
    case["platform_copies"][0]["visual_ids"] = ["not-an-asset"]
    assert "copy[0]:visual_ref_missing_unknown_or_duplicate" in audit_packaging(case)["errors"]


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


def test_public_copy_revision_invalidates_review():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    item["public_fields"]["post_text"] += " changed"
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_referenced_news_fact_change_invalidates_review():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    case["source_facts"][0]["claim"] += " changed"
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_referenced_visual_version_change_invalidates_review():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    case["visual_assets"][0]["sha256"] = "a" * 64
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_unreferenced_visual_does_not_invalidate_copy_review():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item)
    case["visual_assets"].append({
        "id": "V_UNREFERENCED",
        "truth_mode": "EDITORIAL_REAL",
        "source_ref": "owner-local://unrelated-broll.mp4",
        "sha256": "b" * 64,
        "rights_status": "VERIFIED",
        "rights_evidence_ref": "rights://unrelated",
    })
    result = audit_packaging(case)
    assert result["independent_human_reviews_recorded"] == 1
    assert "copy[0]:invalid_or_stale_independent_review" not in result["errors"]


def test_author_cannot_attest_own_editorial_copy():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item, case["author_ref"])
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_failed_counterfactual_cannot_be_signed_pass():
    case = fixture()
    item = case["platform_copies"][0]
    item["independent_review"] = valid_review(case, item)
    item["independent_review"]["semantic_checks"]["video_replacement_loses_meaning"] = False
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_claimed_reviews_never_override_real_release_gate():
    case = fixture()
    for index, item in enumerate(case["platform_copies"]):
        item["independent_review"] = valid_review(case, item, f"reviewer://external-{index}")
    result = audit_packaging(case)
    assert result["contract_valid"]
    assert result["independent_human_reviews_recorded"] == 7
    assert result["release_authorized"] is False
    assert result["semantic_quality_proven"] is False
    assert "master_timeline_version_unbound" in result["open_gates"]


def test_malformed_data_fails_closed():
    for case in (
        {},
        {"source_facts": "bad", "visual_assets": [7], "platform_copies": [None]},
        {"source_facts": [{}], "visual_assets": [{}], "platform_copies": [{}]},
        None,
        [],
    ):
        result = audit_packaging(case)
        assert result["status"] == "INVALID_CONTRACT"
        assert not result["release_authorized"]


def test_malformed_ids_and_enum_values_do_not_crash():
    case = fixture()
    case["source_facts"][0]["id"] = {"not": "hashable"}
    case["source_facts"][0]["classification"] = ["not", "a", "class"]
    case["visual_assets"][0]["id"] = ["not", "hashable"]
    case["visual_assets"][0]["truth_mode"] = {"not": "a mode"}
    case["platform_copies"][0]["platform"] = ["not", "a", "platform"]
    case["platform_copies"][0]["fact_ids"] = [{"bad": "reference"}]
    case["platform_copies"][0]["visual_ids"] = [["bad", "reference"]]
    case["platform_copies"][0]["independent_review"] = {"status": {"bad": "status"}}
    result = audit_packaging(case)
    assert result["status"] == "INVALID_CONTRACT"
    assert result["errors"]


def test_pass_review_digest_handles_malformed_source_containers():
    case = fixture()
    item = case["platform_copies"][0]
    case["source_facts"] = None
    case["visual_assets"] = None
    item["independent_review"] = valid_review(case, item)
    result = audit_packaging(case)
    assert result["status"] == "INVALID_CONTRACT"
    assert any("invalid_or_stale_independent_review" in x for x in result["errors"])


def test_each_platform_requires_its_native_public_fields():
    items = {x["platform"]: x for x in fixture()["platform_copies"]}
    assert fixture()["schema_version"] == "1.1"
    assert set(items["X"]["public_fields"]) == {"post_text"}
    assert set(items["TIKTOK"]["public_fields"]) == {"caption"}
    assert {"title", "description"} <= set(items["YOUTUBE"]["public_fields"])
    assert {"title", "note"} <= set(items["XIAOHONGSHU"]["public_fields"])
    assert {"short_title", "description"} <= set(items["WECHAT_CHANNELS"]["public_fields"])
    assert set(items["DOUYIN"]["public_fields"]) == {"caption"}


def test_wrong_platform_fields_fail_before_editorial_promotion():
    case = fixture()
    case["platform_copies"][0]["public_fields"] = {"title": "X does not have a video title"}
    assert "copy[0]:platform_public_fields_missing_or_invalid" in audit_packaging(case)["errors"]


def test_cover_change_invalidates_youtube_review():
    case = fixture()
    youtube = next(x for x in case["platform_copies"] if x["platform"] == "YOUTUBE")
    youtube["independent_review"] = valid_review(case, youtube)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    youtube["public_fields"]["cover_text"] += " updated"
    assert "copy[2]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_platform_synthetic_disclosure_only_applies_to_referenced_visuals():
    case = fixture()
    real_visual = {
        "id": "V_REAL",
        "truth_mode": "EDITORIAL_REAL",
        "source_ref": "owner-local://licensed-real-broll.mp4",
        "sha256": "c" * 64,
        "rights_status": "VERIFIED",
        "rights_evidence_ref": "rights://real-broll",
    }
    case["visual_assets"].append(real_visual)
    real_copy = case["platform_copies"][0]
    real_copy["visual_ids"] = ["V_REAL"]
    result = audit_packaging(case)
    assert "copy[0]:platform_synthetic_disclosure_receipt_open" not in result["open_gates"]
    assert any(x.startswith("copy[1]:platform_synthetic_disclosure_receipt_open") for x in result["open_gates"])


def test_synthetic_disclosure_receipt_is_required_for_each_copy_using_synthetic_visual():
    case = fixture()
    result = audit_packaging(case)
    assert "copy[0]:platform_synthetic_disclosure_receipt_open" in result["open_gates"]
    case["platform_copies"][0]["synthetic_upload_disclosure_ref"] = "upload-receipt://x"
    assert "copy[0]:platform_synthetic_disclosure_receipt_open" not in audit_packaging(case)["open_gates"]


def test_v1_0_legacy_text_is_bound_to_review_digest():
    case = fixture()
    case["schema_version"] = "1.0"
    item = case["platform_copies"][0]
    item["title"], item["body"] = "legacy title", "legacy body"
    item.pop("public_fields")
    item["independent_review"] = valid_review(case, item)
    assert audit_packaging(case)["independent_human_reviews_recorded"] == 1
    item["title"] += " changed"
    assert "copy[0]:invalid_or_stale_independent_review" in audit_packaging(case)["errors"]


def test_mixed_legacy_and_native_fields_are_rejected():
    case = fixture()
    case["schema_version"] = "1.0"
    item = case["platform_copies"][0]
    item["title"], item["body"] = "legacy title", "legacy body"
    assert "copy[0]:legacy_case_mixes_native_public_fields" in audit_packaging(case)["errors"]


def test_legacy_case_remains_readable_but_warns_against_blind_upload():
    case = fixture()
    case["schema_version"] = "1.0"
    for item in case["platform_copies"]:
        item["title"], item["body"] = "legacy title", "legacy body"
        item.pop("public_fields")
    report = audit_packaging(case)
    assert report["contract_valid"]
    assert "legacy_v1_0_copy_needs_platform_native_fields" in report["warnings"]
    assert report["release_authorized"] is False


def test_case_is_discoverable_in_active_video_business_graph():
    from video_growth_agent.program_orchestration import ProgramGraph
    graph_path = CASE.parent.parent / "SUBTASK_GRAPH.json"
    graph = ProgramGraph.from_path(graph_path)
    node = graph.by_id["topic_satire_editorial_packaging"]
    assert graph.program_id == "ai-self-media-commercialization"
    assert node.workstream == "MEDIA_GROWTH"
    assert node.coordination == "INDEPENDENT_PARALLEL"
    assert node.depends_on == ()
    assert node.metadata["no_ipos_identity_dependency"] is True
    assert "cases/jensen-alice-20261114.json" in node.metadata["authority_inputs"]


def test_program_orchestrator_exposes_packaging_work_without_ipos_bundle():
    from video_growth_agent.program_orchestration import ProgramOrchestrator
    graph_path = CASE.parent.parent / "SUBTASK_GRAPH.json"
    scheduler = ProgramOrchestrator.from_paths(graph_path)
    ready_ids = {node.node_id for node in scheduler.ready()}
    assert "topic_satire_editorial_packaging" in ready_ids
    packet = scheduler.packet("topic_satire_editorial_packaging")
    assert packet["inputs"] == {}
    assert packet["node"]["workstream"] == "MEDIA_GROWTH"
    assert audit_packaging(fixture())["release_authorized"] is False


def test_packaging_cli_runs_without_loading_project_runtime(capsys):
    from video_growth_agent.cli import main
    assert main(["audit-packaging", str(CASE)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "EDITORIAL_CANDIDATE_GATES_OPEN"
    assert not report["release_authorized"]
