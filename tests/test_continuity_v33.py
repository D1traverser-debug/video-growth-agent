import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "continuity" / "tasks" / "video-growth-main"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_owner_adapter_declares_v33_capabilities():
    adapter = load_json(ROOT / "continuity" / "OWNER_ADAPTER.json")
    assert adapter["schema_version"] == "3.3"
    assert adapter["owner"] == "VIDEO_GROWTH_AGENT"
    assert adapter["domain"] == "VIDEO_GROWTH"
    assert adapter["business_runtime_cutover"] is False
    for capability in (
        "list_resumable_tasks_metadata_only",
        "get_task_checkpoint_by_id",
        "compatibility_check",
        "resume_or_migrate_or_block",
        "single_writer_lease",
    ):
        assert adapter["capabilities"][capability] is True


def test_task_manifest_is_resumable_user_task_with_stable_identity():
    manifest = load_json(TASK_DIR / "TASK_MANIFEST.json")
    assert manifest["task_id"] == "video-growth:main"
    assert manifest["display_name_zh"] == "AI视频涨粉与商业化"
    assert manifest["task_class"] == "USER"
    assert manifest["domain"] == "VIDEO_GROWTH"
    assert manifest["recovery_owner"] == "VIDEO_GROWTH_AGENT"
    assert manifest["contract_version"] == "3.3"
    assert manifest["status"] in {"ACTIVE", "WAITING", "BLOCKED"}
    assert manifest["resume_eligible"] is True
    assert manifest["resume_visibility"] == "DEFAULT"
    assert manifest["checkpoint_ref"] == "continuity/tasks/video-growth-main/CHECKPOINT.json"
    assert manifest["resume_epoch"] >= 1
    assert manifest["active_lease"]["lease_id"]
    assert manifest["current_stage"] == "LOOKDEV"
    assert "rejected" in manifest["next_action"].lower()
    assert "distill" in manifest["next_action"].lower()


def test_checkpoint_matches_manifest_and_preserves_rejected_v4_as_history():
    manifest = load_json(TASK_DIR / "TASK_MANIFEST.json")
    checkpoint = load_json(TASK_DIR / "CHECKPOINT.json")
    assert checkpoint["task_id"] == manifest["task_id"]
    assert checkpoint["display_name_zh"] == manifest["display_name_zh"]
    assert checkpoint["contract_version"] == manifest["contract_version"]
    assert checkpoint["current_stage"] == manifest["current_stage"]
    assert checkpoint["status"] == manifest["status"]
    assert checkpoint["resume"]["resume_epoch"] == manifest["resume_epoch"]
    assert checkpoint["resume"]["active_lease_id"] == manifest["active_lease"]["lease_id"]
    assert checkpoint["stage_state"]["previous_release_candidate"] == "REJECTED_BY_USER_FOR_INSUFFICIENT_QUALITY"
    assert checkpoint["stage_state"]["previous_release_gate_valid"] is False
    assert checkpoint["stage_state"]["performance_stage_entered"] is False
    assert checkpoint["authoritative_artifacts"]["rejected_candidate_v4"]["sha256"] == (
        "eec364e8530067dbc87a08a9ccbf2dd6e6e8a5ab32fb87f648c794a4000628eb"
    )
    assert checkpoint["authoritative_artifacts"]["rejected_candidate_v4"]["status"] == "HISTORICAL_REJECTED_CANDIDATE"


def test_task_index_exposes_metadata_only_recovery_pointer():
    text = (ROOT / "continuity" / "TASK_INDEX.md").read_text(encoding="utf-8")
    assert "video-growth:main" in text
    assert "AI视频涨粉与商业化" in text
    assert "TASK_MANIFEST.json" in text
    assert "CHECKPOINT.json" in text
    assert "ACTIVE" in text
    assert "LOOKDEV" in text
