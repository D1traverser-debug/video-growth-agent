import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_produce_tasks_never_declare_approval_roles():
    plan = _load("video_growth_agent/data/execution-plan.json")
    offenders = []
    for stage, spec in plan["stages"].items():
        for task in spec.get("tasks", []):
            if task.get("type") == "produce" and task.get("approval_role"):
                offenders.append(f"{stage}/{task['id']}:{task['approval_role']}")
    assert offenders == []


def test_workflow_required_roles_are_review_roles_not_producer_roles():
    plan = _load("video_growth_agent/data/execution-plan.json")
    workflow = _load("video_growth_agent/data/workflow.json")
    workflow_by_stage = {stage["id"]: stage for stage in workflow["stages"]}

    for stage, spec in plan["stages"].items():
        required_roles = set(workflow_by_stage[stage].get("required_roles", []))
        review_roles = {
            task.get("approval_role")
            for task in spec.get("tasks", [])
            if task.get("type") in {"review", "meta_review"} and task.get("approval_role")
        }
        assert required_roles.issubset(review_roles), (stage, required_roles, review_roles)


def test_runtime_config_has_single_repository_authority():
    assert not (ROOT / "config").exists()
    for name in ("workflow.json", "roles.json", "quality-rubric.json", "techniques.json"):
        assert (ROOT / "video_growth_agent/data" / name).is_file()
