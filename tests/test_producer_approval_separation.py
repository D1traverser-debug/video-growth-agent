import json
from pathlib import Path

import pytest

from video_growth_agent import AgentRegistry, ExecutionPlanner, ProjectStore, StudioOrchestrator, StudioRuntime
from video_growth_agent.studio_agents import AgenticStudio


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


def test_planner_rejects_approval_role_on_non_review_task(tmp_path):
    config = {
        "version": "test",
        "stages": {
            "INTAKE": {
                "mode": "serial",
                "tasks": [
                    {
                        "id": "bad-producer",
                        "executor": "agent",
                        "agent": "showrunner",
                        "type": "produce",
                        "inputs": [],
                        "outputs": ["brief"],
                        "approval_role": "showrunner",
                        "wave": 1,
                    }
                ],
            }
        },
    }
    path = tmp_path / "bad-plan.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    planner = ExecutionPlanner(
        config_path=path,
        agents=AgentRegistry(),
        orchestrator=StudioOrchestrator(),
    )
    assert any("approval_role is forbidden for non-review task type" in item for item in planner.validate())


def test_complete_work_rejects_tampered_producer_approval_role_before_artifact_write(tmp_path):
    rt = StudioRuntime(store=ProjectStore(tmp_path / "projects"))
    studio = AgenticStudio(runtime=rt)
    rt.create_project("tampered")
    studio.dispatch_stage("tampered")

    order_path = tmp_path / "projects" / "tampered" / "work_orders" / "INTAKE" / "intake.json"
    payload = json.loads(order_path.read_text(encoding="utf-8"))
    payload["approval_role"] = "showrunner"
    order_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Non-review work orders cannot declare approval_role"):
        studio.complete_work(
            "tampered",
            "intake",
            outputs={"brief": {"uri": "file://brief.md", "kind": "document", "digest": "brief"}},
        )
    assert "brief" not in rt.state("tampered").artifacts


def test_packaged_and_config_workflow_remain_identical():
    assert _load("video_growth_agent/data/workflow.json") == _load("config/workflow.json")
