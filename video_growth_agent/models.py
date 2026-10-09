from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

Decision = Literal["PASS", "FAIL", "BLOCKED", "NOT_RUN"]
RightsStatus = Literal["OWNED", "AUTHORIZED", "LICENSED", "PUBLIC_DOMAIN", "UNKNOWN"]
QAStatus = Literal["PASS", "WARN", "FAIL", "N_A"]


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Approval:
    role: str
    decision: Decision
    notes: str = ""
    evidence: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    created_at: str = field(default_factory=utcnow_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Approval":
        return cls(role=data["role"], decision=data["decision"], notes=data.get("notes", ""), evidence=tuple(data.get("evidence", [])), findings=tuple(data.get("findings", [])), created_at=data.get("created_at") or utcnow_iso())


@dataclass(frozen=True)
class ArtifactRecord:
    name: str
    uri: str
    stage: str
    kind: str = "document"
    digest: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    recorded_at: str = field(default_factory=utcnow_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArtifactRecord":
        return cls(**data)


@dataclass(frozen=True)
class AssetRecord:
    asset_id: str
    uri: str
    asset_type: str
    rights_status: RightsStatus
    source_ref: str = ""
    license_ref: str = ""
    cost: float = 0.0
    used_in_final: bool = True
    notes: str = ""
    recorded_at: str = field(default_factory=utcnow_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetRecord":
        return cls(**data)


@dataclass(frozen=True)
class QACheck:
    check_id: str
    status: QAStatus
    details: str
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QACheck":
        return cls(check_id=data["check_id"], status=data["status"], details=data["details"], evidence=tuple(data.get("evidence", [])))


@dataclass(frozen=True)
class QAReport:
    media_uri: str
    checks: tuple[QACheck, ...]
    created_at: str = field(default_factory=utcnow_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def hard_pass(self) -> bool:
        return bool(self.checks) and all(check.status != "FAIL" for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["hard_pass"] = self.hard_pass
        return payload


@dataclass
class ProjectState:
    project_id: str
    stage: str = "INTAKE"
    approvals: dict[str, dict[str, Approval]] = field(default_factory=dict)
    artifacts: dict[str, ArtifactRecord] = field(default_factory=dict)
    assets: dict[str, AssetRecord] = field(default_factory=dict)
    qa_receipts: list[str] = field(default_factory=list)
    revision: int = 0
    invalidated_from: str | None = None
    updated_at: str = field(default_factory=utcnow_iso)

    def record(self, stage: str, approval: Approval) -> None:
        self.approvals.setdefault(stage, {})[approval.role] = approval
        self.touch()

    def touch(self) -> None:
        self.revision += 1
        self.updated_at = utcnow_iso()

    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id, "stage": self.stage, "approvals": {stage: {role: asdict(approval) for role, approval in roles.items()} for stage, roles in self.approvals.items()}, "artifacts": {name: asdict(item) for name, item in self.artifacts.items()}, "assets": {asset_id: asdict(item) for asset_id, item in self.assets.items()}, "qa_receipts": list(self.qa_receipts), "revision": self.revision, "invalidated_from": self.invalidated_from, "updated_at": self.updated_at}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectState":
        state = cls(project_id=data["project_id"], stage=data.get("stage", "INTAKE"), revision=int(data.get("revision", 0)), invalidated_from=data.get("invalidated_from"), updated_at=data.get("updated_at") or utcnow_iso())
        state.approvals = {stage: {role: Approval.from_dict(item) for role, item in roles.items()} for stage, roles in data.get("approvals", {}).items()}
        state.artifacts = {name: ArtifactRecord.from_dict(item) for name, item in data.get("artifacts", {}).items()}
        state.assets = {asset_id: AssetRecord.from_dict(item) for asset_id, item in data.get("assets", {}).items()}
        state.qa_receipts = list(data.get("qa_receipts", []))
        return state
