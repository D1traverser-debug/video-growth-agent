from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Literal

from .models import utcnow_iso

CoordinationPattern = Literal[
    "SERIAL_DEPENDENCY",
    "INDEPENDENT_PARALLEL",
    "FAN_OUT_FAN_IN",
    "CONSULTATIVE_ADVICE",
    "COMPETITIVE_CANDIDATES",
    "STRUCTURED_CRITIQUE_AND_REVISION",
    "OWNER_ADJUDICATION",
    "QUORUM_OR_PANEL_REVIEW",
]
NodeStatus = Literal["WAITING", "READY", "COMPLETED", "FAILED", "CANCELLED"]

ALLOWED_PATTERNS = {
    "SERIAL_DEPENDENCY",
    "INDEPENDENT_PARALLEL",
    "FAN_OUT_FAN_IN",
    "CONSULTATIVE_ADVICE",
    "COMPETITIVE_CANDIDATES",
    "STRUCTURED_CRITIQUE_AND_REVISION",
    "OWNER_ADJUDICATION",
    "QUORUM_OR_PANEL_REVIEW",
}


@dataclass(frozen=True)
class ProgramNode:
    node_id: str
    workstream: str
    coordination: CoordinationPattern
    depends_on: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    decision_group: str | None = None
    consumes_group: str | None = None
    adjudicator: str | None = None
    decision_owner: str | None = None
    advisory_only: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProgramNode":
        known = {
            "id",
            "workstream",
            "coordination",
            "depends_on",
            "inputs",
            "outputs",
            "decision_group",
            "consumes_group",
            "adjudicator",
            "decision_owner",
            "advisory_only",
        }
        return cls(
            node_id=str(payload["id"]),
            workstream=str(payload["workstream"]),
            coordination=payload["coordination"],
            depends_on=tuple(str(item) for item in payload.get("depends_on", [])),
            inputs=tuple(str(item) for item in payload.get("inputs", [])),
            outputs=tuple(str(item) for item in payload.get("outputs", [])),
            decision_group=payload.get("decision_group"),
            consumes_group=payload.get("consumes_group"),
            adjudicator=payload.get("adjudicator"),
            decision_owner=payload.get("decision_owner"),
            advisory_only=bool(payload.get("advisory_only", False)),
            metadata={key: value for key, value in payload.items() if key not in known},
        )


@dataclass
class ProgramRunState:
    program_id: str
    node_status: dict[str, NodeStatus]
    node_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProgramRunState":
        return cls(
            program_id=str(payload["program_id"]),
            node_status=dict(payload.get("node_status", {})),
            node_results=dict(payload.get("node_results", {})),
            artifacts=dict(payload.get("artifacts", {})),
            decisions=list(payload.get("decisions", [])),
            updated_at=str(payload.get("updated_at") or utcnow_iso()),
        )


class ProgramGraph:
    """Domain-owned dependency and decision graph for cross-workstream business work."""

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.program_id = str(payload.get("program_id") or "")
        self.nodes = tuple(ProgramNode.from_dict(item) for item in payload.get("nodes", []))
        self.by_id = {node.node_id: node for node in self.nodes}
        errors = self.validate()
        if errors:
            raise ValueError("Invalid Program graph: " + "; ".join(errors))

    @classmethod
    def from_path(cls, path: Path) -> "ProgramGraph":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def decision_groups(self) -> dict[str, tuple[ProgramNode, ...]]:
        groups: dict[str, list[ProgramNode]] = {}
        for node in self.nodes:
            if node.decision_group:
                groups.setdefault(node.decision_group, []).append(node)
        return {key: tuple(value) for key, value in groups.items()}

    def validate(self) -> list[str]:
        errors: list[str] = []
        ids = [node.node_id for node in self.nodes]
        if not self.program_id:
            errors.append("program_id is required")
        if len(ids) != len(set(ids)):
            errors.append("node ids must be unique")
        for node in self.nodes:
            if node.coordination not in ALLOWED_PATTERNS:
                errors.append(f"{node.node_id}: unknown coordination {node.coordination!r}")
            if node.node_id in node.depends_on:
                errors.append(f"{node.node_id}: self dependency")
            for dependency in node.depends_on:
                if dependency not in self.by_id:
                    errors.append(f"{node.node_id}: unknown dependency {dependency}")
            if node.coordination == "CONSULTATIVE_ADVICE" and not node.advisory_only:
                errors.append(f"{node.node_id}: consultation must be advisory_only")
            if node.coordination == "OWNER_ADJUDICATION" and not node.adjudicator:
                errors.append(f"{node.node_id}: owner adjudication requires adjudicator")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            if node_id in visiting:
                errors.append(f"dependency cycle detected at {node_id}")
                return
            visiting.add(node_id)
            for dependency in self.by_id[node_id].depends_on:
                if dependency in self.by_id:
                    visit(dependency)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in self.by_id:
            visit(node_id)

        groups = self.decision_groups()
        for group, members in groups.items():
            if len(members) < 2:
                errors.append(f"decision_group {group}: requires at least two candidate nodes")
            if any(member.coordination != "COMPETITIVE_CANDIDATES" for member in members):
                errors.append(f"decision_group {group}: all members must be COMPETITIVE_CANDIDATES")

        for node in self.nodes:
            if not node.consumes_group:
                continue
            members = groups.get(node.consumes_group)
            if not members:
                errors.append(f"{node.node_id}: consumes unknown decision_group {node.consumes_group}")
                continue
            member_ids = {member.node_id for member in members}
            missing = sorted(member_ids - set(node.depends_on))
            if missing:
                errors.append(
                    f"{node.node_id}: adjudication/synthesis must depend on every candidate in {node.consumes_group}: {missing}"
                )
        return errors

    def downstream(self, node_id: str) -> set[str]:
        if node_id not in self.by_id:
            raise KeyError(node_id)
        found: set[str] = set()
        frontier = [node_id]
        while frontier:
            current = frontier.pop()
            for node in self.nodes:
                if current in node.depends_on and node.node_id not in found:
                    found.add(node.node_id)
                    frontier.append(node.node_id)
        return found


class ProgramOrchestrator:
    """Persistable domain business scheduler. It is not a parent/controller task registry."""

    def __init__(self, graph: ProgramGraph, state_path: Path | None = None):
        self.graph = graph
        self.state_path = state_path
        if state_path and state_path.exists():
            self.state = ProgramRunState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
            if self.state.program_id != graph.program_id:
                raise ValueError("Program state program_id does not match graph")
        else:
            self.state = ProgramRunState(
                program_id=graph.program_id,
                node_status={node.node_id: "WAITING" for node in graph.nodes},
            )
        self._reconcile_ready()

    @classmethod
    def from_paths(cls, graph_path: Path, state_path: Path | None = None) -> "ProgramOrchestrator":
        return cls(ProgramGraph.from_path(graph_path), state_path=state_path)

    def _save(self) -> None:
        self.state.updated_at = utcnow_iso()
        if self.state_path:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(
                json.dumps(self.state.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _requirements_satisfied(self, node: ProgramNode) -> bool:
        if not all(self.state.node_status.get(dep) == "COMPLETED" for dep in node.depends_on):
            return False
        return all(name in self.state.artifacts for name in node.inputs)

    def _reconcile_ready(self) -> None:
        for node in self.graph.nodes:
            status = self.state.node_status.get(node.node_id, "WAITING")
            if status in {"COMPLETED", "FAILED", "CANCELLED"}:
                continue
            self.state.node_status[node.node_id] = "READY" if self._requirements_satisfied(node) else "WAITING"
        self._save()

    def ready(self) -> tuple[ProgramNode, ...]:
        self._reconcile_ready()
        return tuple(node for node in self.graph.nodes if self.state.node_status[node.node_id] == "READY")

    def packet(self, node_id: str) -> dict[str, Any]:
        self._reconcile_ready()
        node = self.graph.by_id[node_id]
        if self.state.node_status[node_id] != "READY":
            raise RuntimeError(f"Program node {node_id} is {self.state.node_status[node_id]}, not READY")
        return {
            "program_id": self.graph.program_id,
            "node": asdict(node),
            "inputs": {name: self.state.artifacts[name] for name in node.inputs},
            "dependency_results": {
                dep: self.state.node_results.get(dep, {}) for dep in node.depends_on
            },
            "candidate_group": self._candidate_group_payload(node.consumes_group),
            "peer_chat_allowed": False,
        }

    def _candidate_group_payload(self, group: str | None) -> list[dict[str, Any]]:
        if not group:
            return []
        members = self.graph.decision_groups().get(group, ())
        return [
            {
                "node_id": member.node_id,
                "result": self.state.node_results.get(member.node_id, {}),
                "outputs": {name: self.state.artifacts.get(name) for name in member.outputs},
            }
            for member in members
        ]

    def complete(
        self,
        node_id: str,
        *,
        outputs: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
    ) -> ProgramRunState:
        self._reconcile_ready()
        node = self.graph.by_id[node_id]
        if self.state.node_status[node_id] != "READY":
            raise RuntimeError(f"Program node {node_id} is {self.state.node_status[node_id]}, not READY")
        if node.coordination == "OWNER_ADJUDICATION":
            raise ValueError("Use adjudicate for OWNER_ADJUDICATION nodes")
        provided = set((outputs or {}).keys())
        expected = set(node.outputs)
        if provided != expected:
            raise ValueError(f"Expected outputs {sorted(expected)}, got {sorted(provided)}")
        for name, value in (outputs or {}).items():
            self.state.artifacts[name] = {
                "value": value,
                "produced_by_node": node_id,
                "workstream": node.workstream,
            }
        self.state.node_results[node_id] = dict(result or {})
        self.state.node_status[node_id] = "COMPLETED"
        self._reconcile_ready()
        return self.state

    def adjudicate(
        self,
        node_id: str,
        *,
        decision: Literal["SELECT", "MERGE", "REJECT_ALL"],
        selected_candidate_ids: tuple[str, ...] = (),
        rationale: str,
        outputs: dict[str, Any],
    ) -> ProgramRunState:
        self._reconcile_ready()
        node = self.graph.by_id[node_id]
        if node.coordination != "OWNER_ADJUDICATION":
            raise ValueError("Node is not OWNER_ADJUDICATION")
        if self.state.node_status[node_id] != "READY":
            raise RuntimeError(f"Program node {node_id} is {self.state.node_status[node_id]}, not READY")
        if not node.consumes_group:
            raise ValueError("OWNER_ADJUDICATION node must consume a decision_group")
        candidates = {member.node_id for member in self.graph.decision_groups()[node.consumes_group]}
        selected = set(selected_candidate_ids)
        if not selected <= candidates:
            raise ValueError("selected_candidate_ids contains a node outside the consumed decision_group")
        if decision in {"SELECT", "MERGE"} and not selected:
            raise ValueError(f"{decision} requires selected_candidate_ids")
        if decision == "SELECT" and len(selected) != 1:
            raise ValueError("SELECT requires exactly one candidate")
        provided = set(outputs)
        expected = set(node.outputs)
        if provided != expected:
            raise ValueError(f"Expected outputs {sorted(expected)}, got {sorted(provided)}")
        receipt = {
            "node_id": node_id,
            "adjudicator": node.adjudicator,
            "decision_group": node.consumes_group,
            "decision": decision,
            "selected_candidate_ids": list(selected_candidate_ids),
            "rationale": rationale,
            "candidate_results": self._candidate_group_payload(node.consumes_group),
            "decided_at": utcnow_iso(),
        }
        for name, value in outputs.items():
            self.state.artifacts[name] = {
                "value": value,
                "produced_by_node": node_id,
                "workstream": node.workstream,
                "decision_receipt": receipt,
            }
        self.state.node_results[node_id] = receipt
        self.state.decisions.append(receipt)
        self.state.node_status[node_id] = "COMPLETED"
        self._reconcile_ready()
        return self.state

    def fail(self, node_id: str, reason: str) -> ProgramRunState:
        if node_id not in self.graph.by_id:
            raise KeyError(node_id)
        self.state.node_status[node_id] = "FAILED"
        self.state.node_results[node_id] = {"reason": reason, "failed_at": utcnow_iso()}
        self._reconcile_ready()
        return self.state

    def invalidate_from(self, node_id: str, reason: str) -> ProgramRunState:
        affected = {node_id} | self.graph.downstream(node_id)
        produced = {
            output
            for affected_id in affected
            for output in self.graph.by_id[affected_id].outputs
        }
        for affected_id in affected:
            self.state.node_status[affected_id] = "WAITING"
            self.state.node_results.pop(affected_id, None)
        for output in produced:
            self.state.artifacts.pop(output, None)
        self.state.decisions = [
            receipt for receipt in self.state.decisions if receipt.get("node_id") not in affected
        ]
        self.state.node_results[node_id] = {
            "invalidated": True,
            "reason": reason,
            "invalidated_at": utcnow_iso(),
        }
        self._reconcile_ready()
        return self.state
