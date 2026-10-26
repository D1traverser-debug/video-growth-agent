from importlib.metadata import version
from pathlib import Path
import shutil

from video_growth_agent.system_audit import package_audit, repository_audit, run_system_audit

ROOT = Path(__file__).resolve().parents[1]


def test_package_harness_passes_current_runtime_contract():
    report = package_audit()
    assert report["pass"] is True, report
    expected = version("video-growth-agent")
    assert expected == "0.8.0"
    assert report["legacy_adapter_bundle_version"] == "0.7.0"
    assert report["agent_registry_version"] == report["execution_plan_version"]
    assert report["execution_plan_version"] == report["coordination_policy_version"]


def test_repository_harness_requires_uaos_and_rejects_retired_control_plane():
    report = repository_audit(ROOT)
    assert report["pass"] is True, report
    assert report["runtime_version"] == "0.8.0"
    assert report["legacy_adapter_bundle_version"] == "0.7.0"
    assert not (ROOT / "config").exists()
    assert not (ROOT / "continuity").exists()
    assert (ROOT / ".uaos/MANIFEST.json").is_file()
    assert (ROOT / ".uaos/ADAPTER.json").is_file()
    assert (ROOT / ".uaos/CAPABILITIES.json").is_file()
    assert (ROOT / "projects/pilot-002/PROGRAM_STATE.json").is_file()
    for rel in (
        "video_growth_agent/media_graph.py",
        "video_growth_agent/editorial_planning.py",
        "video_growth_agent/plan_graph_bridge.py",
        "video_growth_agent/production_os.py",
        "video_growth_agent/continuity.py",
        "video_growth_agent/model_registry.py",
        "video_growth_agent/timeline.py",
        "video_growth_agent/editorial_interchange.py",
        "video_growth_agent/experiments.py",
        "video_growth_agent/business_objects.py",
        "video_growth_agent/business_metrics.py",
        "video_growth_agent/operator_view.py",
        "video_growth_agent/owner_behavior_admission.py",
    ):
        assert (ROOT / rel).is_file(), rel


def test_repository_harness_fails_closed_when_canonical_media_runtime_is_missing(tmp_path):
    shadow = tmp_path / "repo"
    shutil.copytree(
        ROOT,
        shadow,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
    )
    missing = shadow / "video_growth_agent/editorial_planning.py"
    missing.unlink()
    report = repository_audit(shadow)
    assert report["pass"] is False
    assert "media_business_runtime_missing:video_growth_agent/editorial_planning.py" in report["failures"]


def test_combined_system_audit_passes_repository_and_package():
    report = run_system_audit(ROOT)
    assert report["pass"] is True, report
    assert report["failures"] == []


def test_green_system_audit_does_not_attest_an_actual_film_or_user_business_goal():
    from video_growth_agent.system_audit import run_system_audit
    report = run_system_audit()
    scope = report["assurance_scope"]
    assert scope["goal_achievement_verdict"] == "NOT_ASSESSED_BY_STATIC_AUDIT"
    assert "AUTHENTIC_MODEL_GENERATION" in scope["does_not_certify"]
    assert "FILM_SEMANTIC_OR_ARTISTIC_QUALITY" in scope["does_not_certify"]
    assert "REAL_PLATFORM_GROWTH_OR_COMMERCIAL_RESULTS" in scope["does_not_certify"]
    assert scope["goal_fit_evidence_ref"].endswith("VIDEO_END_TO_END_GOAL_FIT_AUDIT_2026-10-24.md")
