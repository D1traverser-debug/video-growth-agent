import json
from pathlib import Path

import pytest

from video_growth_agent import Approval, ArtifactRecord, AssetRecord, GateBlocked, ProjectStore, StudioRuntime


def runtime(tmp_path: Path) -> StudioRuntime:
    return StudioRuntime(store=ProjectStore(tmp_path / "projects"))


def test_project_checkpoint_roundtrip_and_receipts(tmp_path):
    rt = runtime(tmp_path)
    state = rt.create_project("pilot-x", title="test")
    assert state.stage == "INTAKE"
    rt.record_artifact("pilot-x", "brief", "file://brief.md", "INTAKE", digest="a1")
    receipt = rt.sign("pilot-x", "showrunner", "PASS", "brief is viable", ("file://brief.md",))
    assert (tmp_path / "projects" / "pilot-x" / receipt).exists()
    assert rt.advance("pilot-x") == "POSITIONING"
    loaded = rt.state("pilot-x")
    assert loaded.stage == "POSITIONING"
    assert loaded.approvals["INTAKE"]["showrunner"].decision == "PASS"
    events = (tmp_path / "projects" / "pilot-x" / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(events) >= 4


def test_changed_upstream_artifact_invalidates_downstream(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); rt.record_artifact("p", "brief", "file://brief-v1", "INTAKE", digest="1"); rt.sign("p", "showrunner", "PASS"); rt.advance("p"); assert rt.state("p").stage == "POSITIONING"; rt.record_artifact("p", "brief", "file://brief-v2", "INTAKE", digest="2")
    state = rt.state("p"); assert state.stage == "INTAKE"; assert state.approvals == {}; assert state.invalidated_from == "INTAKE"


def test_unknown_final_rights_are_exposed(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); rt.record_asset("p", AssetRecord("a1", "file://asset", "image", "UNKNOWN", used_in_final=True)); rt.record_asset("p", AssetRecord("a2", "file://owned", "image", "OWNED", used_in_final=True)); assert rt.unknown_final_rights("p") == ["a1"]


def test_current_prompts_are_stage_scoped(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); prompts = rt.current_prompts("p"); assert set(prompts) == {"showrunner"}; assert "Protect the account" in prompts["showrunner"]


def _record_fake_qa_receipt(rt, project_id: str, media_uri: str, hard_pass: bool, sha256: str | None = None):
    from video_growth_agent import QACheck, QAReport
    statuses = {"video_stream":"PASS","stream_duration_match":"PASS","true_peak":"PASS" if hard_pass else "FAIL","black_frames":"PASS"}
    checks = tuple(QACheck(check_id, status, "test") for check_id, status in statuses.items())
    metadata = {"checker":"ffmpeg-ffprobe-v0.2"}
    if sha256: metadata["sha256"] = sha256
    return rt.record_qa(project_id, QAReport(media_uri=media_uri, checks=checks, metadata=metadata))


def _force_release_state(rt, project_id: str, qa_media_uri: str = "file://final.mp4"):
    state = rt.state(project_id); state.stage = "RELEASE"; state.artifacts["final_media"] = ArtifactRecord("final_media", "file://final.mp4", "RELEASE", kind="media"); state.artifacts["publish_pack"] = ArtifactRecord("publish_pack", "file://publish.md", "RELEASE"); rt.store.save(state); _record_fake_qa_receipt(rt, project_id, qa_media_uri, True); state = rt.state(project_id); state.stage = "RELEASE"; rt.store.save(state)


def test_release_machine_guard_blocks_unknown_rights(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); _force_release_state(rt, "p"); rt.record_asset("p", AssetRecord("unknown", "file://x", "image", "UNKNOWN", used_in_final=True)); state = rt.state("p"); state.stage = "RELEASE"; state.approvals["RELEASE"] = {"showrunner": Approval("showrunner", "PASS")}; rt.store.save(state); report = rt.gate_report("p"); assert not report["pass"]; assert any(item.startswith("no_unknown_final_rights") for item in report["machine_failures"])
    with pytest.raises(GateBlocked): rt.advance("p")


def test_tech_qa_machine_guard_requires_hard_pass_receipt(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); state = rt.state("p"); state.stage = "TECH_QA"; state.artifacts["final_candidate"] = ArtifactRecord("final_candidate", "file://candidate.mp4", "TECH_QA", kind="media"); state.approvals["TECH_QA"] = {"technical_director": Approval("technical_director", "PASS")}; rt.store.save(state); _record_fake_qa_receipt(rt, "p", "file://candidate.mp4", False); state = rt.state("p"); state.stage = "TECH_QA"; rt.store.save(state); assert rt.gate_report("p")["machine_failures"] == ["latest_media_qa_hard_pass"]
    with pytest.raises(GateBlocked): rt.advance("p")


def test_release_requires_qa_of_actual_final_media_not_old_candidate(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); _force_release_state(rt, "p", qa_media_uri="file://candidate-before-transcode.mp4"); state = rt.state("p"); state.approvals["RELEASE"] = {"showrunner": Approval("showrunner", "PASS")}; rt.store.save(state); report = rt.gate_report("p"); assert "latest_media_qa_target_mismatch:final_media" in report["machine_failures"]
    with pytest.raises(GateBlocked): rt.advance("p")


def test_manual_technical_qa_artifact_cannot_forge_machine_pass(tmp_path):
    rt = runtime(tmp_path); rt.create_project("p"); state = rt.state("p"); state.stage = "TECH_QA"; state.artifacts["final_candidate"] = ArtifactRecord("final_candidate", "file://candidate.mp4", "TECH_QA", kind="media"); state.artifacts["technical_qa"] = ArtifactRecord("technical_qa", "fake.json", "TECH_QA", kind="qa_report", metadata={"hard_pass": True}); state.approvals["TECH_QA"] = {"technical_director": Approval("technical_director", "PASS")}; rt.store.save(state); assert rt.gate_report("p")["machine_failures"] == ["latest_media_qa_hard_pass"]


def test_release_accepts_digest_match_when_persistent_uri_differs(tmp_path):
    from video_growth_agent import QACheck, QAReport
    rt = runtime(tmp_path); rt.create_project("digest"); state = rt.state("digest"); state.stage = "RELEASE"; state.artifacts["final_media"] = ArtifactRecord("final_media", "library://final", "RELEASE", kind="media", digest="abc123"); state.artifacts["publish_pack"] = ArtifactRecord("publish_pack", "file://publish.md", "RELEASE"); state.approvals["RELEASE"] = {"showrunner": Approval("showrunner", "PASS")}; rt.store.save(state); rt.record_qa("digest", QAReport(media_uri="/mnt/data/materialized-final.mp4", checks=tuple(QACheck(check_id, "PASS", "test") for check_id in ("video_stream", "stream_duration_match", "true_peak", "black_frames")), metadata={"checker": "ffmpeg-ffprobe-v0.2", "sha256": "abc123"})); state = rt.state("digest"); state.stage = "RELEASE"; rt.store.save(state); assert rt.gate_report("digest")["machine_failures"] == []


def test_default_project_store_never_targets_installed_package(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path); monkeypatch.delenv("VGA_PROJECTS_DIR", raising=False); store = ProjectStore(); assert store.root == tmp_path / "projects"


def test_empty_or_untrusted_qa_receipt_cannot_pass_machine_gate(tmp_path):
    from video_growth_agent import QAReport
    rt = runtime(tmp_path); rt.create_project("untrusted"); state = rt.state("untrusted"); state.stage = "TECH_QA"; state.artifacts["final_candidate"] = ArtifactRecord("final_candidate", "file://candidate.mp4", "TECH_QA", kind="media"); state.approvals["TECH_QA"] = {"technical_director": Approval("technical_director", "PASS")}; rt.store.save(state); rt.record_qa("untrusted", QAReport(media_uri="file://candidate.mp4", checks=())); state = rt.state("untrusted"); state.stage = "TECH_QA"; rt.store.save(state); assert "latest_media_qa_hard_pass" in rt.gate_report("untrusted")["machine_failures"]


def test_digest_target_does_not_fall_back_to_uri_when_qa_has_no_digest(tmp_path):
    rt = runtime(tmp_path); rt.create_project("digest-required"); state = rt.state("digest-required"); state.stage = "RELEASE"; state.artifacts["final_media"] = ArtifactRecord("final_media", "file://same.mp4", "RELEASE", kind="media", digest="expected"); state.artifacts["publish_pack"] = ArtifactRecord("publish_pack", "file://publish.md", "RELEASE"); state.approvals["RELEASE"] = {"showrunner": Approval("showrunner", "PASS")}; rt.store.save(state); _record_fake_qa_receipt(rt, "digest-required", "file://same.mp4", True); state = rt.state("digest-required"); state.stage = "RELEASE"; rt.store.save(state); assert "latest_media_qa_target_mismatch:final_media" in rt.gate_report("digest-required")["machine_failures"]


def _force_visual_preview_state(rt, project_id: str, digest: str = "preview-digest"):
    state = rt.state(project_id); state.stage = "VISUAL_PREVIEW"; state.artifacts["visual_preview"] = ArtifactRecord("visual_preview", "file://preview.mp4", "VISUAL_PREVIEW", kind="media", digest=digest); state.artifacts["visual_contact_sheet"] = ArtifactRecord("visual_contact_sheet", "file://contact.jpg", "VISUAL_PREVIEW", kind="image", digest="contact-digest"); rt.store.save(state)


def _quality_scores_for(role: str):
    dims = {
        "creative_director": ["benchmark_parity", "distinctiveness", "advertiser_showcase", "overall_craft", "sample_final_fidelity", "picture_sound_cohesion"],
        "art_director": ["composition_hierarchy", "material_light_depth", "typography", "visual_consistency"],
        "motion_director": ["motion_craft", "easing_stagger", "camera_depth", "motion_explains", "physicality_or_spatial_coherence"],
        "director": ["narrative_visual_arc", "shot_scale_contrast", "reveal_payoff", "emotion_rhythm", "sample_represents_final_language"],
        "retention_editor": ["first_2s_stop", "visual_reset_frequency", "silent_comprehension", "dead_zone_risk"],
    }[role]
    return {d: 4.5 for d in dims}


def test_visual_quality_gate_requires_blind_digest_benchmarks_and_scores(tmp_path):
    rt = runtime(tmp_path); rt.create_project("visual"); _force_visual_preview_state(rt, "visual"); roles = ["creative_director","art_director","motion_director","director","retention_editor"]
    for role in roles:
        rt.sign("visual", role, "PASS", notes="current rendered artifact meets the bar", evidence=("file://preview.mp4","file://contact.jpg"), findings=("current pixels inspected",), scorecard=_quality_scores_for(role), benchmark_refs=("ref://format","ref://craft","ref://explanation"), target_digest="preview-digest", blind_review=True)
    assert rt.gate_report("visual")["pass"]


def test_visual_quality_gate_rejects_deferred_potential_pass(tmp_path):
    rt = runtime(tmp_path); rt.create_project("defer"); _force_visual_preview_state(rt, "defer"); roles = ["creative_director","art_director","motion_director","director","retention_editor"]
    for role in roles:
        note = "正式资产阶段继续强化材质即可" if role == "art_director" else "current rendered artifact meets the bar"
        rt.sign("defer", role, "PASS", notes=note, evidence=("file://preview.mp4","file://contact.jpg"), scorecard=_quality_scores_for(role), benchmark_refs=("ref://format","ref://craft","ref://explanation"), target_digest="preview-digest", blind_review=True)
    report = rt.gate_report("defer"); assert not report["pass"]; assert any(x.startswith("quality_deferred_pass_language:art_director") for x in report["machine_failures"])


def test_visual_quality_gate_rejects_below_reference_score(tmp_path):
    rt = runtime(tmp_path); rt.create_project("low"); _force_visual_preview_state(rt, "low"); roles = ["creative_director","art_director","motion_director","director","retention_editor"]
    for role in roles:
        scores = _quality_scores_for(role)
        if role == "creative_director": scores["benchmark_parity"] = 3.0
        rt.sign("low", role, "PASS", notes="judged current render", evidence=("file://preview.mp4","file://contact.jpg"), scorecard=scores, benchmark_refs=("ref://format","ref://craft","ref://explanation"), target_digest="preview-digest", blind_review=True)
    report = rt.gate_report("low"); assert not report["pass"]; assert any("quality_score_below_floor:creative_director:benchmark_parity" in x for x in report["machine_failures"])


def test_review_packet_hides_prior_verdicts(tmp_path):
    rt = runtime(tmp_path); rt.create_project("packet"); _force_visual_preview_state(rt, "packet"); packet = rt.review_packet("packet", "art_director"); assert packet["prior_role_verdicts_hidden"] is True; assert "approvals" not in packet; assert packet["quality_rubric"]["target_artifact"] == "visual_preview"
