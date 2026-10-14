from importlib.metadata import version
from pathlib import Path

from video_growth_agent.system_audit import package_audit, repository_audit, run_system_audit

ROOT = Path(__file__).resolve().parents[1]


def test_package_harness_passes_current_runtime_contract():
    report = package_audit()
    assert report["pass"] is True, report
    expected = version("video-growth-agent")
    assert report["agent_registry_version"] == expected
    assert report["execution_plan_version"] == expected


def test_repository_harness_requires_uaos_and_rejects_retired_control_plane():
    report = repository_audit(ROOT)
    assert report["pass"] is True, report
    assert not (ROOT / "config").exists()
    assert not (ROOT / "continuity").exists()
    assert (ROOT / ".uaos/MANIFEST.json").is_file()
    assert (ROOT / ".uaos/ADAPTER.json").is_file()
    assert (ROOT / ".uaos/CAPABILITIES.json").is_file()
    assert (ROOT / "projects/pilot-002/PROGRAM_STATE.json").is_file()


def test_combined_system_audit_passes_repository_and_package():
    report = run_system_audit(ROOT)
    assert report["pass"] is True, report
    assert report["failures"] == []
