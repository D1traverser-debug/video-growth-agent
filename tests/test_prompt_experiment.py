"""Prompt dialect preregistration reuses canonical experiments, never fabricates media QA."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from video_growth_agent.prompt_director import PromptPlanError
from video_growth_agent.prompt_experiment import h3_dialect_study
from video_growth_agent.experiments import ExperimentPlan, ExperimentVariant

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("name", ["prompt_ip_5s.json", "prompt_ribbon_10s.json"])
def test_experiment_design_does_not_conflate_prompt_comparison_with_render_results(name):
    plan = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    result = h3_dialect_study(plan)
    e = result["experiment_plan"]
    assert result["quality_winner"] is None
    assert result["rendered_media_evidence"] == []
    assert result["source_scope"] == "EXCERPT"
    assert e["attribution_mode"] == "BUNDLED_PROMPT_POLICY_NOT_LANGUAGE_CAUSAL"
    assert e["guardrail_metrics"] == ("identity_continuity", "physical_contact_errors", "credits_spent")
    assert "at least" not in result["assurance"].lower()
    assert len(result["candidates"]) == 2
    assert all(item["prompt_digest"] for item in result["candidates"])
    assert len({item["prompt_digest"] for item in result["candidates"]}) == 2
    assert e["variants"][0]["fixed_variables"] == e["variants"][1]["fixed_variables"]
    assert e["variants"][0]["changed_variables"].keys() == e["variants"][1]["changed_variables"].keys()
    canonical = ExperimentPlan(
        experiment_id=e["experiment_id"], context_id=e["context_id"],
        hypothesis=e["hypothesis"],
        variants=tuple(ExperimentVariant(**v) for v in e["variants"]),
        primary_metric=e["primary_metric"], metric_semantics=e["metric_semantics"],
        guardrail_metrics=tuple(e["guardrail_metrics"]), attribution_mode=e["attribution_mode"],
        minimum_observation_rule=e["minimum_observation_rule"],
        stop_rules=tuple(e["stop_rules"]), evidence_refs=tuple(e["evidence_refs"]),
        state=e["state"],
    )
    assert canonical.state == "PLANNED"
    assert canonical.experiment_id == e["experiment_id"]
    assert h3_dialect_study(plan)["experiment_plan"] == e


def test_uncontrolled_provider_drift_is_rejected():
    plan = json.loads((FIXTURES / "prompt_ip_5s.json").read_text(encoding="utf-8"))
    pixverse = copy.deepcopy(plan)
    pixverse["provider"].update(name="PixVerse", model="V6", mode="T2V", native_audio=False)
    with pytest.raises(PromptPlanError, match="requires MiniMax H3"):
        h3_dialect_study(pixverse)
    with pytest.raises(PromptPlanError, match="onepass"):
        h3_dialect_study(plan, route="shotwise")


def test_real_cli_emits_experiment_contract_without_generating_video():
    p = subprocess.run([
        sys.executable, "-m", "video_growth_agent.cli", "direct-prompts",
        str(FIXTURES / "prompt_ribbon_10s.json"), "--study-h3-dialects"
    ], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    assert data["quality_winner"] is None
    assert data["experiment_plan"]["state"] == "PLANNED"
    assert data["candidates"][0]["prompt"].startswith("作品：《")
    assert data["candidates"][1]["prompt"].startswith("integrated_multimodal_description:")



def test_plain_output_is_copy_ready_and_refuses_ambiguous_compare_mode():
    sample = str(FIXTURES / "prompt_ribbon_10s.json")
    base = [sys.executable, "-m", "video_growth_agent.cli", "direct-prompts", sample, "--h3-style", "chinese"]
    good = subprocess.run(base + ["--route", "onepass", "--plain"], capture_output=True, text=True)
    assert good.returncode == 0, good.stderr
    assert good.stdout.startswith("作品：《红绸赴约")
    assert "逐时段分镜" in good.stdout
    assert not good.stdout.strip().startswith("{")
    bad = subprocess.run(base + ["--plain"], capture_output=True, text=True)
    assert bad.returncode != 0
    assert "--plain needs --route" in bad.stderr


def test_review_sheet_cli_is_unscored_even_when_source_events_are_tagged():
    sample = str(FIXTURES / "prompt_ribbon_10s.json")
    command = [sys.executable, "-m", "video_growth_agent.cli", "direct-prompts", sample, "--review-sheet"]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    sheet = json.loads(result.stdout)
    assert sheet["media_asset_ref"] is None
    assert sheet["assessment"] == "NOT_STARTED"
    assert sheet["reviewer_independence"] == "NOT_ESTABLISHED"
    assert len(sheet["shots"]) == 6
    assert all(s["actual_result"] == "UNREVIEWED" for s in sheet["shots"])
    mixed = subprocess.run(command + ["--plain"], capture_output=True, text=True)
    assert mixed.returncode != 0
    assert "mutually exclusive" in mixed.stderr



def test_auto_plain_outputs_distinct_unranked_prompt_candidates():
    path = str(FIXTURES / "prompt_ribbon_10s.json")
    result = subprocess.run([
        sys.executable, "-m", "video_growth_agent.cli", "direct-prompts",
        path, "--route", "onepass", "--plain",
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("=== CANDIDATE: ") == 3
    assert "=== CANDIDATE: LEAN ===" in result.stdout
    assert "=== CANDIDATE: CHINESE ===" in result.stdout
    assert "=== CANDIDATE: OFFICIAL ===" in result.stdout
    assert "逐时段分镜" in result.stdout
    assert "integrated_multimodal_description" in result.stdout
