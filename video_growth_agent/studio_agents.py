from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Literal

from .models import ArtifactRecord, QAReport, ProjectState, utcnow_iso
from .orchestrator import StudioOrchestrator
from .resources import data_path
from .roles import RoleRegistry
from .runtime import StudioRuntime

AgentKind = Literal["worker", "reviewer", "supervisor"]
TaskType = Literal["produce", "review", "meta_review", "measure"]
OrderStatus = Literal["WAITING", "READY", "COMPLETED", "FAILED", "CANCELLED"]


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    kind: AgentKind
    role: str | None
    mandate: str
    tools: tuple[str, ...]
    user_voice: bool = False
    prompt: str = ""


@dataclass
class WorkOrder:
    work_order_id: str
    project_id: str
    stage: str
    task_id: str
    executor: str
    task_type: TaskType
    wave: int
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    agent_id: str | None = None
    tool: str | None = None
    approval_role: str | None = None
    blind: bool = False
    status: OrderStatus = "WAITING"
    result: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow_iso)
    updated_at: str = field(default_factory=utcnow_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkOrder":
        payload = dict(payload)
        payload["inputs"] = tuple(payload.get("inputs", ()))
        payload["outputs"] = tuple(payload.get("outputs", ()))
        return cls(**payload)


class AgentRegistry:
    """On-demand specialist definitions. Registration does not mean persistent execution."""

    def __init__(self, config_path: Path | None = None, roles: RoleRegistry | None = None):
        self.path = config_path or data_path("agents.json")
        self.config = json.loads(self.path.read_text(encoding="utf-8"))
        self.roles = roles or RoleRegistry()

    def get(self, agent_id: str) -> AgentSpec:
        raw = self.config["agents"].get(agent_id)
        if raw is None:
            raise KeyError(f"Unknown agent: {agent_id}")
        role = raw.get("role")
        role_prompt = self.roles.get(role).prompt if role else ""
        mandate = str(raw.get("mandate", "")).strip()
        prompt = "\n\n".join(x for x in (mandate, role_prompt) if x)
        return AgentSpec(
            agent_id=agent_id,
            kind=raw["kind"],
            role=role,
            mandate=mandate,
            tools=tuple(raw.get("tools", [])),
            user_voice=bool(raw.get("user_voice", False)),
            prompt=prompt,
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        voices: list[str] = []
        for agent_id in self.config.get("agents", {}):
            try:
                spec = self.get(agent_id)
            except (KeyError, ValueError) as exc:
                errors.append(f"{agent_id}: {exc}")
                continue
            if spec.user_voice:
                voices.append(agent_id)
        if voices != ["executive_producer"]:
            errors.append(f"single_user_voice must be executive_producer, got {voices}")
        principles = self.config.get("principles", {})
        if principles.get("peer_chat") is not False:
            errors.append("peer_chat must be false")
        if principles.get("artifact_handoffs_only") is not True:
            errors.append("artifact_handoffs_only must be true")
        if principles.get("hard_gate_override") is not False:
            errors.append("hard_gate_override must be false")
        return errors


class ExecutionPlanner:
    DETERMINISTIC_TOOLS = {"ffmpeg_ffprobe"}

    def __init__(
        self,
        config_path: Path | None = None,
        agents: AgentRegistry | None = None,
        orchestrator: StudioOrchestrator | None = None,
    ):
        self.path = config_path or data_path("execution-plan.json")
        self.config = json.loads(self.path.read_text(encoding="utf-8"))
        self.agents = agents or AgentRegistry()
        self.orchestrator = orchestrator or StudioOrchestrator()

    def stage(self, stage: str) -> dict[str, Any]:
        spec = self.config.get("stages", {}).get(stage)
        if spec is None:
            return {"mode": "deterministic_or_manual", "tasks": []}
        return spec

    def validate(self) -> list[str]:
        errors = self.agents.validate()
        workflow_stages = set(self.orchestrator.index)
        for stage, spec in self.config.get("stages", {}).items():
            if stage not in workflow_stages:
                errors.append(f"execution plan references unknown stage {stage}")
            task_ids: set[str] = set()
            for task in spec.get("tasks", []):
                task_id = task.get("id")
                if not task_id or task_id in task_ids:
                    errors.append(f"{stage}: duplicate/missing task id {task_id!r}")
                task_ids.add(task_id)
                task_type = task.get("type")
                approval_role = task.get("approval_role")
                if approval_role and task_type not in {"review", "meta_review"}:
                    errors.append(
                        f"{stage}/{task_id}: approval_role is forbidden for non-review task type {task_type!r}"
                    )
                executor = task.get("executor")
                if executor == "agent":
                    agent_id = task.get("agent")
                    try:
                        agent = self.agents.get(agent_id)
                    except (KeyError, ValueError) as exc:
                        errors.append(f"{stage}/{task_id}: {exc}")
                        continue
                    if approval_role and agent.role != approval_role:
                        errors.append(
                            f"{stage}/{task_id}: agent {agent_id} role {agent.role!r} "
                            f"cannot sign {approval_role!r}"
                        )
                    if task_type in {"review", "meta_review"} and agent.kind == "worker":
                        errors.append(f"{stage}/{task_id}: worker agent cannot be reviewer")
                    if task_type == "produce" and agent.kind == "reviewer":
                        errors.append(f"{stage}/{task_id}: reviewer-only agent cannot be producer")
                elif executor == "tool":
                    if task.get("tool") not in self.DETERMINISTIC_TOOLS:
                        errors.append(f"{stage}/{task_id}: unknown deterministic tool {task.get('tool')}")
                    if task.get("tool") == "ffmpeg_ffprobe":
                        if task_type != "measure":
                            errors.append(f"{stage}/{task_id}: ffmpeg_ffprobe must be a measure task")
                        if len(task.get("outputs", [])) != 1:
                            errors.append(f"{stage}/{task_id}: ffmpeg_ffprobe must declare exactly one QA output")
                else:
                    errors.append(f"{stage}/{task_id}: executor must be agent or tool")
                if int(task.get("wave", 0)) < 1:
                    errors.append(f"{stage}/{task_id}: wave must be >= 1")
        return errors


class AgenticStudio:
    """Producer-controlled work-order runtime with isolated specialists and blind review."""

    def __init__(
        self,
        runtime: StudioRuntime | None = None,
        agents: AgentRegistry | None = None,
        planner: ExecutionPlanner | None = None,
    ):
        self.runtime = runtime or StudioRuntime()
        self.agents = agents or AgentRegistry(roles=self.runtime.roles)
        self.planner = planner or ExecutionPlanner(agents=self.agents, orchestrator=self.runtime.orchestrator)
        errors = self.planner.validate()
        if errors:
            raise ValueError("Invalid agent studio configuration: " + "; ".join(errors))

    def _stage_dir(self, project_id: str, stage: str) -> Path:
        path = self.runtime.store.project_dir(project_id) / "work_orders" / stage
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _order_path(self, project_id: str, stage: str, task_id: str) -> Path:
        return self._stage_dir(project_id, stage) / f"{task_id}.json"

    def _load_order(self, project_id: str, stage: str, task_id: str) -> WorkOrder:
        path = self._order_path(project_id, stage, task_id)
        if not path.exists():
            raise FileNotFoundError(path)
        return WorkOrder.from_dict(json.loads(path.read_text(encoding="utf-8")))

    @staticmethod
    def _save_order(path: Path, order: WorkOrder) -> None:
        order.updated_at = utcnow_iso()
        path.write_text(json.dumps(order.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _input_digests(state: ProjectState, inputs: tuple[str, ...] | list[str]) -> dict[str, str | None]:
        return {
            name: state.artifacts[name].digest if name in state.artifacts else None
            for name in inputs
        }

    def _new_order(self, state: ProjectState, task: dict[str, Any]) -> WorkOrder:
        return WorkOrder(
            work_order_id=f"{state.project_id}:{state.stage}:{task['id']}:r{state.revision}",
            project_id=state.project_id,
            stage=state.stage,
            task_id=task["id"],
            executor=task["executor"],
            task_type=task["type"],
            wave=int(task["wave"]),
            inputs=tuple(task.get("inputs", [])),
            outputs=tuple(task.get("outputs", [])),
            agent_id=task.get("agent"),
            tool=task.get("tool"),
            approval_role=task.get("approval_role"),
            blind=bool(task.get("blind", False)),
        )

    def _completed_order_stale(self, state: ProjectState, order: WorkOrder, task: dict[str, Any]) -> str | None:
        expected_contract = {
            "executor": task.get("executor"),
            "task_type": task.get("type"),
            "wave": int(task.get("wave", 0)),
            "inputs": tuple(task.get("inputs", [])),
            "outputs": tuple(task.get("outputs", [])),
            "agent_id": task.get("agent"),
            "tool": task.get("tool"),
            "approval_role": task.get("approval_role"),
            "blind": bool(task.get("blind", False)),
        }
        actual_contract = {
            "executor": order.executor,
            "task_type": order.task_type,
            "wave": order.wave,
            "inputs": order.inputs,
            "outputs": order.outputs,
            "agent_id": order.agent_id,
            "tool": order.tool,
            "approval_role": order.approval_role,
            "blind": order.blind,
        }
        if actual_contract != expected_contract:
            return "task_contract_changed"
        if order.status != "COMPLETED":
            return None
        input_digests = order.result.get("input_digests") if isinstance(order.result, dict) else None
        current = self._input_digests(state, order.inputs)
        if not isinstance(input_digests, dict):
            return "input_digest_binding_missing"
        if input_digests != current:
            return "input_digest_changed"
        for output_name in order.outputs:
            artifact = state.artifacts.get(output_name)
            if artifact is None:
                return f"output_retired:{output_name}"
            if artifact.metadata.get("work_order_id") != order.work_order_id:
                return f"output_provenance_changed:{output_name}"
        return None

    def dispatch_stage(self, project_id: str) -> list[WorkOrder]:
        state = self.runtime.state(project_id)
        stage = state.stage
        tasks = list(self.planner.stage(stage).get("tasks", []))
        orders: list[WorkOrder] = []
        for task in tasks:
            path = self._order_path(project_id, stage, task["id"])
            order: WorkOrder
            if path.exists():
                order = WorkOrder.from_dict(json.loads(path.read_text(encoding="utf-8")))
                stale_reason = self._completed_order_stale(state, order, task)
                if stale_reason:
                    self.runtime.store.append_receipt(
                        project_id,
                        "WORK_ORDER_RETIRED",
                        {
                            "stage": stage,
                            "task_id": task["id"],
                            "work_order_id": order.work_order_id,
                            "reason": stale_reason,
                        },
                    )
                    order = self._new_order(state, task)
            else:
                order = self._new_order(state, task)
            orders.append(order)

        for order in orders:
            if order.status in {"COMPLETED", "FAILED", "CANCELLED"}:
                continue
            lower = [other for other in orders if other.wave < order.wave]
            lower_done = all(other.status == "COMPLETED" for other in lower)
            inputs_ready = all(name in state.artifacts for name in order.inputs)
            order.status = "READY" if lower_done and inputs_ready else "WAITING"
            self._save_order(self._order_path(project_id, stage, order.task_id), order)
        return orders

    def ready(self, project_id: str) -> list[WorkOrder]:
        return [order for order in self.dispatch_stage(project_id) if order.status == "READY"]

    def advance(self, project_id: str) -> str:
        """Advance only when the stage work-order contract and base gate both pass."""
        orders = self.dispatch_stage(project_id)
        incomplete = [order.task_id for order in orders if order.status != "COMPLETED"]
        if incomplete:
            from .orchestrator import GateBlocked
            raise GateBlocked(
                json.dumps(
                    {
                        "stage": self.runtime.state(project_id).stage,
                        "agent_work_orders_complete": False,
                        "incomplete_work_orders": incomplete,
                    },
                    ensure_ascii=False,
                )
            )
        return self.runtime.advance(project_id)

    def work_packet(self, project_id: str, task_id: str) -> dict[str, Any]:
        state = self.runtime.state(project_id)
        order = self._load_order(project_id, state.stage, task_id)
        if order.status != "READY":
            raise RuntimeError(f"Work order {task_id} is {order.status}, not READY")
        artifacts = {name: asdict(state.artifacts[name]) for name in order.inputs if name in state.artifacts}
        packet: dict[str, Any] = {
            "project_id": project_id,
            "stage": state.stage,
            "work_order": order.to_dict(),
            "inputs": artifacts,
            "peer_chat_allowed": False,
            "project_approvals_hidden": order.task_type == "review" and order.blind,
        }
        if order.executor == "agent":
            agent = self.agents.get(order.agent_id or "")
            packet["agent"] = asdict(agent)
            packet["prompt"] = agent.prompt
        else:
            packet["tool_contract"] = {
                "tool": order.tool,
                "instruction": (
                    "Run deterministic ffmpeg/ffprobe QA against the declared media input and complete this work order through complete_media_qa; do not fabricate a QA artifact."
                    if order.tool == "ffmpeg_ffprobe"
                    else "Run deterministically and return measured evidence only."
                ),
                "declared_outputs": list(order.outputs),
            }
        if order.task_type == "meta_review":
            packet["panel_reviews"] = self._panel_reviews(project_id, state.stage, before_wave=order.wave)
        return packet

    def _panel_reviews(self, project_id: str, stage: str, before_wave: int) -> list[dict[str, Any]]:
        reviews: list[dict[str, Any]] = []
        for task in self.planner.stage(stage).get("tasks", []):
            if int(task.get("wave", 0)) >= before_wave:
                continue
            if task.get("type") != "review" or task.get("approval_role"):
                continue
            path = self._order_path(project_id, stage, task["id"])
            if not path.exists():
                continue
            order = WorkOrder.from_dict(json.loads(path.read_text(encoding="utf-8")))
            if order.status == "COMPLETED":
                reviews.append({"reviewer": order.agent_id, "result": order.result})
        return reviews

    def complete_work(
        self,
        project_id: str,
        task_id: str,
        outputs: dict[str, dict[str, Any]] | None = None,
        result: dict[str, Any] | None = None,
    ) -> WorkOrder:
        state = self.runtime.state(project_id)
        order = self._load_order(project_id, state.stage, task_id)
        if order.status != "READY":
            raise RuntimeError(f"Work order {task_id} is {order.status}, not READY")
        if order.task_type in {"review", "meta_review"}:
            raise ValueError("Use submit_review for review work orders")
        if order.approval_role:
            raise ValueError("Non-review work orders cannot declare approval_role")
        if order.executor == "tool" and order.tool == "ffmpeg_ffprobe":
            raise ValueError("Use complete_media_qa for ffmpeg_ffprobe measure work orders")
        provided = set((outputs or {}).keys())
        expected = set(order.outputs)
        if provided != expected:
            raise ValueError(f"Expected outputs {sorted(expected)}, got {sorted(provided)}")
        input_digests = self._input_digests(state, order.inputs)
        producer = order.agent_id if order.executor == "agent" else f"tool:{order.tool}"
        for name, payload in (outputs or {}).items():
            metadata = dict(payload.get("metadata", {}))
            metadata.update({"produced_by_agent": producer, "work_order_id": order.work_order_id})
            self.runtime.record_artifact(
                project_id,
                name=name,
                uri=payload["uri"],
                stage=state.stage,
                kind=payload.get("kind", "document"),
                digest=payload.get("digest"),
                metadata=metadata,
            )
        order.status = "COMPLETED"
        order.result = {**(result or {}), "input_digests": input_digests}
        self._save_order(self._order_path(project_id, state.stage, task_id), order)
        self.runtime.store.append_receipt(project_id, "WORK_ORDER_COMPLETED", {"work_order": order.to_dict()})
        return order

    def complete_media_qa(self, project_id: str, task_id: str, report: QAReport) -> WorkOrder:
        state = self.runtime.state(project_id)
        order = self._load_order(project_id, state.stage, task_id)
        if order.status != "READY":
            raise RuntimeError(f"Work order {task_id} is {order.status}, not READY")
        if order.executor != "tool" or order.tool != "ffmpeg_ffprobe" or order.task_type != "measure":
            raise ValueError("Work order is not an ffmpeg_ffprobe measure task")
        if len(order.outputs) != 1:
            raise ValueError("ffmpeg_ffprobe measure work order must declare exactly one QA output")
        input_digests = self._input_digests(state, order.inputs)
        receipt = self.runtime.record_qa(
            project_id,
            report,
            artifact_name=order.outputs[0],
            stage=state.stage,
            work_order_id=order.work_order_id,
            producer=f"tool:{order.tool}",
        )
        order.status = "COMPLETED"
        order.result = {
            "input_digests": input_digests,
            "qa_receipt": receipt,
            "hard_pass": report.hard_pass,
            "media_uri": report.media_uri,
        }
        self._save_order(self._order_path(project_id, state.stage, task_id), order)
        self.runtime.store.append_receipt(project_id, "WORK_ORDER_COMPLETED", {"work_order": order.to_dict()})
        return order

    def submit_review(
        self,
        project_id: str,
        task_id: str,
        decision: str,
        *,
        notes: str = "",
        evidence: tuple[str, ...] = (),
        findings: tuple[str, ...] = (),
        scorecard: dict[str, float] | None = None,
        benchmark_refs: tuple[str, ...] = (),
        target_digest: str | None = None,
    ) -> WorkOrder:
        state = self.runtime.state(project_id)
        order = self._load_order(project_id, state.stage, task_id)
        if order.status != "READY":
            raise RuntimeError(f"Work order {task_id} is {order.status}, not READY")
        if order.executor != "agent" or order.task_type not in {"review", "meta_review"}:
            raise ValueError("Work order is not an agent review")
        agent = self.agents.get(order.agent_id or "")
        input_digests: dict[str, str | None] = {}
        for name in order.inputs:
            artifact = state.artifacts.get(name)
            if artifact:
                input_digests[name] = artifact.digest
                if artifact.metadata.get("produced_by_agent") == agent.agent_id:
                    raise ValueError(f"Self-review forbidden: {agent.agent_id} produced input artifact {name}")
        result = {
            "decision": decision,
            "notes": notes,
            "evidence": list(evidence),
            "findings": list(findings),
            "scorecard": scorecard or {},
            "benchmark_refs": list(benchmark_refs),
            "target_digest": target_digest,
            "input_digests": input_digests,
        }
        if order.approval_role:
            if agent.role != order.approval_role:
                raise ValueError(f"Agent {agent.agent_id} role {agent.role!r} cannot sign {order.approval_role!r}")
            self.runtime.sign(
                project_id,
                role=order.approval_role,
                decision=decision,
                notes=notes,
                evidence=evidence,
                findings=findings,
                scorecard=scorecard,
                benchmark_refs=benchmark_refs,
                target_digest=target_digest,
                blind_review=order.blind,
            )
        else:
            self.runtime.store.append_receipt(
                project_id,
                "PANEL_REVIEW",
                {"stage": state.stage, "agent_id": agent.agent_id, "blind": order.blind, "result": result},
            )
        order.status = "COMPLETED"
        order.result = result
        self._save_order(self._order_path(project_id, state.stage, task_id), order)
        self.runtime.store.append_receipt(
            project_id,
            "WORK_ORDER_REVIEW_COMPLETED",
            {
                "work_order_id": order.work_order_id,
                "stage": state.stage,
                "task_id": order.task_id,
                "agent_id": agent.agent_id,
                "approval_role": order.approval_role,
                "blind": order.blind,
                "input_digests": input_digests,
                "result": result,
            },
        )
        return order

    def fail_work(self, project_id: str, task_id: str, reason: str) -> WorkOrder:
        state = self.runtime.state(project_id)
        order = self._load_order(project_id, state.stage, task_id)
        order.status = "FAILED"
        order.result = {"reason": reason}
        self._save_order(self._order_path(project_id, state.stage, task_id), order)
        self.runtime.store.append_receipt(
            project_id,
            "WORK_ORDER_FAILED",
            {"work_order": order.to_dict(), "reason": reason},
        )
        return order
