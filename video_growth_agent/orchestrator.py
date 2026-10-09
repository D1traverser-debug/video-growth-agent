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

    def required_roles(self, stage: str) -> list[str]:
        return list(self.stages[self.index[stage]].get("required_roles", []))

    def sign(self, state: ProjectState, approval: Approval) -> None:
        if state.stage not in self.index:
            raise ValueError(f"Unknown stage: {state.stage}")
        state.record(state.stage, approval)

    def gate_report(self, state: ProjectState) -> dict:
        required = self.required_roles(state.stage)
        got = state.approvals.get(state.stage, {})
        missing = [r for r in required if r not in got]
        failed = [r for r in required if r in got and got[r].decision in {"FAIL", "BLOCKED"}]
        not_passed = [r for r in required if r in got and got[r].decision != "PASS"]
        return {
            "stage": state.stage,
            "required": required,
            "missing": missing,
            "failed": failed,
            "not_passed": not_passed,
            "pass": not missing and not not_passed,
        }

    def advance(self, state: ProjectState) -> str:
        report = self.gate_report(state)
        if not report["pass"]:
            raise GateBlocked(json.dumps(report, ensure_ascii=False))
        i = self.index[state.stage]
        if i == len(self.stages) - 1:
            return state.stage
        state.stage = self.stages[i + 1]["id"]
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
