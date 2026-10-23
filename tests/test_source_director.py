"""Original screenplay to director plan: source identity, timecodes, real import.

Tests use an injected text-authoring model stub, not fabricated production
movie/video evidence and not a claim of independent model-quality evaluation.
"""
from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
from pathlib import Path
from urllib.request import Request

import pytest

from video_growth_agent.prompt_director import PromptPlanError
from video_growth_agent.source_director import (
    accept_authoring_response, audit_authored_plan, author_with_model,
    build_compatible_chat_client, build_director_request, inventory_source,
    prepare_authoring_messages,
)

FIX = Path(__file__).parent / "fixtures"
ORIGINAL = FIX / "ribbon_original_30s.txt"
FULL = FIX / "prompt_ribbon_fullsource_10s.json"


def raw_plan_packet():
    source = ORIGINAL.read_text(encoding="utf-8")
    plan = json.loads(FULL.read_text(encoding="utf-8"))
    packet = build_director_request(
        source, target_seconds=10, fps=30, aspect_ratio="16:9",
        source_reference="user-quoted://full-30-second-ribbon-storyboard-2026-10-23",
    )
    return source, plan, packet


def test_original_30_second_script_has_24_measured_clock_units_and_overlap():
    source, plan, packet = raw_plan_packet()
    inv = inventory_source(source)
    assert len(source) == 959
    assert len(inv["source_digest"]) == 71
    assert inv["source_timing_unit_count"] == 24
    assert inv["nested_or_overlapping_clock_marks"] is True
    assert inv["source_timing_units"][0]["clock"] == [0, 5]
    assert inv["source_timing_units"][1]["clock"] == [0, 2]
    assert inv["source_timing_units"][-1]["clock"] == [28, 30]
    for unit in inv["source_timing_units"]:
        start, end = unit["source_span"]
        assert source[start:end] == unit["exact_excerpt"]
    assert source == plan["source"]["raw"]
    assert packet["source_contract"]["digest"] == inv["source_digest"]


def test_full_original_event_copies_cover_all_24_source_timed_units_but_not_media():
    _, plan, packet = raw_plan_packet()
    a = audit_authored_plan(packet, plan)
    assert a["unit_count"] == 24
    assert a["unanchored_units"] == []
    assert a["source_unit_anchor_fraction"] == 1
    assert a["timeline_valid"] is True
    assert a["independent_story_semantics_verified"] is False
    assert a["visual_model_execution_verified"] is False
    assert any("may not remain legible" in n for n in a["risk_notes"])


def test_model_output_cannot_substitute_source_or_change_timebase():
    _, plan, packet = raw_plan_packet()
    altered = copy.deepcopy(plan)
    altered["source"]["raw"] = altered["source"]["raw"].replace("黑色纱帘", "明亮舞台")
    with pytest.raises(PromptPlanError, match="altered or substituted"):
        audit_authored_plan(packet, altered)
    altered = copy.deepcopy(plan)
    altered["brief"]["total_frames"] = 301
    altered["shots"][-1]["end_frame"] = 301
    with pytest.raises(PromptPlanError, match="editorial timebase"):
        audit_authored_plan(packet, altered)
    altered = copy.deepcopy(plan)
    altered["provider"]["name"] = "OtherStudio"
    with pytest.raises(PromptPlanError, match="provider settings"):
        audit_authored_plan(packet, altered)


def test_original_source_gap_is_visible_even_if_remaining_events_are_tagged():
    _, plan, packet = raw_plan_packet()
    changed = copy.deepcopy(plan)
    for shot in changed["shots"]:
        shot["event_ids"] = [x for x in shot["event_ids"] if x != "source-unit-20"]
    changed["required_events"] = [
        x for x in changed["required_events"] if x["id"] != "source-unit-20"
    ]
    a = audit_authored_plan(packet, changed)
    assert "U020" in a["unanchored_units"]
    assert a["source_unit_anchor_fraction"] < 1
    assert a["independent_story_semantics_verified"] is False


def test_model_authoring_handoff_works_and_never_claims_rendered_media():
    source, plan, packet = raw_plan_packet()
    calls = []
    def fake_model(messages):
        calls.append(messages)
        return json.dumps(plan, ensure_ascii=False)
    result = author_with_model(packet, fake_model)
    assert len(calls) == 1
    assert calls[0][0]["role"] == "system"
    assert json.loads(calls[0][1]["content"].split("COMPLETE_SOURCE_AND_OUTPUT_CONTRACT:\n", 1)[1])["source_contract"]["raw"] == source
    assert result["source_audit"]["unanchored_units"] == []
    assert result["compiled"]["prompt_candidates"]["chinese"]["onepass"]["status"] == "COMPILED"
    assert result["compiled"]["visual_winner"] is None
    assert result["compiled"]["review_targets"]["assessment"] == "NOT_STARTED"


def test_llm_bad_json_is_rejected_not_repaired_by_guessing():
    _, plan, packet = raw_plan_packet()
    with pytest.raises(PromptPlanError, match="bare JSON"):
        accept_authoring_response(packet, "Here is your plan:\n" + json.dumps(plan))
    with pytest.raises(PromptPlanError, match="bare JSON"):
        accept_authoring_response(packet, "~~~json\n" + json.dumps(plan) + "\n~~~")


def test_network_path_is_explicitly_opt_in_and_secrets_do_not_leak(monkeypatch):
    for bad_url in ("http://text-provider.test/v1/chat/completions",
                    "https://user:pass@text-provider.test/v1/chat/completions"):
        with pytest.raises(PromptPlanError, match="HTTPS"):
            build_compatible_chat_client(endpoint=bad_url, model_name="test", api_key="SECRET", approved=True)
    with pytest.raises(PromptPlanError, match="approval"):
        build_compatible_chat_client(
            endpoint="https://text-provider.test/v1/chat/completions",
            model_name="test", api_key="SECRET", approved=False,
        )
    body = json.dumps({"choices": [{"message": {"content": '{"version": 1}'}}]}).encode("utf-8")
    calls = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self, limit): return body
    def fake_open(req, timeout):
        assert isinstance(req, Request)
        assert req.get_header("Authorization") == "Bearer SECRET"
        calls.append(json.loads(req.data.decode("utf-8")))
        return Response()
    monkeypatch.setattr("urllib.request.urlopen", fake_open)
    completion = build_compatible_chat_client(
        endpoint="https://text-provider.test/v1/chat/completions",
        model_name="author-v1", api_key="SECRET", approved=True,
    )
    assert completion([{"role": "user", "content": "scene"}]) == '{"version": 1}'
    assert calls[0]["model"] == "author-v1"
    assert calls[0]["messages"][0]["content"] == "scene"


def test_command_line_raw_script_packet_and_strict_model_import(tmp_path):
    source, plan, _ = raw_plan_packet()
    base = [sys.executable, "-m", "video_growth_agent.cli", "author-director",
            str(ORIGINAL), "--seconds", "10", "--source-ref",
            "user-quoted://full-30-second-ribbon-storyboard-2026-10-23"]
    packet = subprocess.run(base, text=True, capture_output=True)
    assert packet.returncode == 0, packet.stderr
    ready = json.loads(packet.stdout)
    assert ready["status"] == "AUTHORING_PACKET_READY"
    assert ready["packet"]["source_inventory"]["source_timing_unit_count"] == 24

    model_output = tmp_path / "authored-plan.json"
    model_output.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(base + ["--model-output", str(model_output)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    product = json.loads(result.stdout)
    assert product["source_audit"]["source_unit_anchor_fraction"] == 1
    assert product["compiled"]["prompt_candidates"]["chinese"]["onepass"]["status"] == "COMPILED"
    assert product["compiled"]["visual_winner"] is None

    no_auth = subprocess.run(base + ["--execute-model", "--endpoint",
                             "https://api.example.com/v1/chat/completions",
                             "--model-name", "test"], text=True, capture_output=True)
    assert no_auth.returncode == 2
    assert "API credential is missing" in no_auth.stderr


def test_missing_original_unit_blocks_model_acceptance_and_bounded_retry_repairs():
    _, plan, packet = raw_plan_packet()
    broken = copy.deepcopy(plan)
    broken["required_events"] = [e for e in broken["required_events"] if e["id"] != "source-unit-20"]
    for shot in broken["shots"]:
        shot["event_ids"] = [x for x in shot["event_ids"] if x != "source-unit-20"]
    with pytest.raises(PromptPlanError, match="original source passages lack"):
        accept_authoring_response(packet, json.dumps(broken, ensure_ascii=False))
    attempts = []
    def correcting_model(messages):
        attempts.append(messages)
        return json.dumps(broken if len(attempts) == 1 else plan, ensure_ascii=False)
    corrected = author_with_model(packet, correcting_model, max_revisions=1)
    assert corrected["authoring_attempts"] == 2
    assert len(attempts) == 2
    assert "U020" in attempts[1][-1]["content"]
    with pytest.raises(PromptPlanError, match="original source passages lack"):
        author_with_model(packet, lambda _: json.dumps(broken, ensure_ascii=False), max_revisions=0)


def test_importing_an_excerpt_plan_for_full_original_fails_explicitly():
    _, _, packet = raw_plan_packet()
    excerpt = json.loads((FIX / "prompt_ribbon_10s.json").read_text(encoding="utf-8"))
    with pytest.raises(PromptPlanError, match="altered or substituted"):
        accept_authoring_response(packet, json.dumps(excerpt, ensure_ascii=False))


def test_complete_original_music_only_contract_blocks_unrequested_foley_or_voice():
    _, plan, packet = raw_plan_packet()
    assert audit_authored_plan(packet, plan)["timeline_valid"]
    adjusted = copy.deepcopy(plan)
    adjusted["shots"][0]["audio"].append({
        "at_frame": 0, "category": "SFX", "description": "clapping"
    })
    with pytest.raises(PromptPlanError, match="background-music-only"):
        audit_authored_plan(packet, adjusted)
    adjusted = copy.deepcopy(plan)
    adjusted["shots"][0]["audio"].append({
        "at_frame": 0, "category": "VOICE", "description": "dramatic whisper",
        "speaker": "S1", "language": "Mandarin", "spoken_text": "缘分"
    })
    with pytest.raises(PromptPlanError, match="no dialogue"):
        audit_authored_plan(packet, adjusted)
    notes = audit_authored_plan(packet, plan)["risk_notes"]
    assert any("SOURCE_AUDIO_CONFLICT" in note for note in notes)


def test_untimed_original_idea_uses_same_authoring_pipeline_without_false_clock():
    original_fixture = json.loads((FIX / "prompt_ip_5s.json").read_text(encoding="utf-8"))
    raw = original_fixture["source"]["raw"]
    packet = build_director_request(
        raw, target_seconds=5, aspect_ratio="9:16",
        source_reference=original_fixture["source"]["reference"],
        source_type=original_fixture["source"]["type"],
    )
    units = packet["source_inventory"]
    assert units["source_timing_unit_count"] == 0
    assert units["source_unit_count"] == 4
    assert not units["nested_or_overlapping_clock_marks"]
    assert all(unit["kind"] == "UNTIMED_SOURCE_SENTENCE" for unit in units["source_timing_units"])
    assert all(raw[u["source_span"][0]:u["source_span"][1]] == u["exact_excerpt"]
               for u in units["source_timing_units"])
    fixture = copy.deepcopy(original_fixture)
    fixture["source"]["completeness"] = "FULL"
    report = accept_authoring_response(packet, json.dumps(fixture, ensure_ascii=False))
    assert report["source_audit"]["unanchored_units"] == []
    assert report["compiled"]["prompt_candidates"]["chinese"]["onepass"]["status"] == "COMPILED"
    assert report["compiled"]["visual_winner"] is None
def test_exported_authored_plan_round_trips_into_prompt_and_crew_cli(tmp_path):
    """Exercise the real operator path: raw source -> imported plan -> two consumers.

    JSON validation of stdout alone misses corruption on the --out-plan file.
    """
    _, plan, _ = raw_plan_packet()
    model_output = tmp_path / "model-returned-plan.json"
    model_output.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    saved = tmp_path / "operator-plan.json"
    author = subprocess.run([
        sys.executable, "-m", "video_growth_agent.cli",
        "author-director", str(ORIGINAL), "--seconds", "10",
        "--source-ref", "user-quoted://full-30-second-ribbon-storyboard-2026-10-23",
        "--model-output", str(model_output), "--out-plan", str(saved),
    ], capture_output=True, text=True)
    assert author.returncode == 0, author.stderr
    contents = saved.read_text(encoding="utf-8")
    assert contents.endswith("\n") and not contents.endswith("\\n")
    assert json.loads(contents) == plan

    prompts = subprocess.run([
        sys.executable, "-m", "video_growth_agent.cli",
        "direct-prompts", str(saved), "--route", "onepass",
        "--h3-style", "lean",
    ], capture_output=True, text=True)
    assert prompts.returncode == 0, prompts.stderr
    assert json.loads(prompts.stdout)["routes"]["onepass"]["status"] == "COMPILED"

    crew = subprocess.run([
        sys.executable, "-m", "video_growth_agent.cli",
        "craft-round", str(saved),
    ], capture_output=True, text=True)
    assert crew.returncode == 0, crew.stderr
    assert json.loads(crew.stdout)["packet"]["execution_status"] == "PREPARED_NOT_REVIEWED"
