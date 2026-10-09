from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Decision = Literal["PASS", "FAIL", "BLOCKED", "NOT_RUN"]

@dataclass(frozen=True)
class Approval:
    role: str
    decision: Decision
    notes: str = ""
    evidence: tuple[str, ...] = ()

@dataclass
class ProjectState:
    project_id: str
    stage: str = "INTAKE"
    approvals: dict[str, dict[str, Approval]] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    invalidated_from: str | None = None

    def record(self, stage: str, approval: Approval) -> None:
        self.approvals.setdefault(stage, {})[approval.role] = approval
