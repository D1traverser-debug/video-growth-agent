from __future__ import annotations

import json
from pathlib import Path
from .models import Approval, ProjectState

ROOT = Path(__file__).resolve().parents[1]


class GateBlocked(RuntimeError):
    pass


class StudioOrchestrator:
    def __init__(self, workflow_path: Path | None = None):
        path = workflow_path or ROOT / "config" / "workflow.json"
        self.workflow = json.loads(path.read_text(encoding="utf-8"))
        self.stages = self.workflow["stages"]
        self.index = {stage["id"]: i for i, stage in enumerate(self.stages)}

    def stage_spec(self, stage: str) -> dict:
        return self.stages[self.index[stage]]

    def required_roles(self, stage: str) -> list[str]:
        return list(self.stage_spec(stage).get("required_roles", []))

    def required_artifacts(self, stage: str) -> list[str]:
        return list(self.stage_spec(stage).get("required_artifacts", []))

    def sign(self, state: ProjectState, approval: Approval) -> None:
        if state.stage not in self.index:
            raise ValueError(f"Unknown stage: {state.stage}")
        if approval.role not in self.required_roles(state.stage):
            raise ValueError(f"Role {approval.role!r} is not required at stage {state.stage}")
        if state.stage == "RED_TEAM" and approval.role == "red_team" and approval.decision == "PASS":
            if len(approval.findings) < 3:
                raise ValueError("RED_TEAM PASS requires at least three explicit findings/objections")
        state.record(state.stage, approval)

    def gate_report(self, state: ProjectState) -> dict:
        required = self.required_roles(state.stage)
        got = state.approvals.get(state.stage, {})
        missing = [r for r in required if r not in got]
        failed = [r for r in required if r in got and got[r].decision in {"FAIL", "BLOCKED"}]
        not_passed = [r for r in required if r in got and got[r].decision != "PASS"]
        required_artifacts = self.required_artifacts(state.stage)
        missing_artifacts = [name for name in required_artifacts if name not in state.artifacts]
        return {
            "stage": state.stage,
            "required": required,
            "missing": missing,
            "failed": failed,
            "not_passed": not_passed,
            "required_artifacts": required_artifacts,
            "missing_artifacts": missing_artifacts,
            "pass": not missing and not not_passed and not missing_artifacts,
        }

    def advance(self, state: ProjectState) -> str:
        report = self.gate_report(state)
        if not report["pass"]:
            raise GateBlocked(json.dumps(report, ensure_ascii=False))
        i = self.index[state.stage]
        if i == len(self.stages) - 1:
            return state.stage
        state.stage = self.stages[i + 1]["id"]
        state.touch()
        return state.stage

    def invalidate_from(self, state: ProjectState, stage: str) -> None:
        if stage not in self.index:
            raise ValueError(stage)
        cutoff = self.index[stage]
        for key in list(state.approvals):
            if self.index.get(key, -1) >= cutoff:
                del state.approvals[key]
        state.stage = stage
        state.invalidated_from = stage
        state.touch()
