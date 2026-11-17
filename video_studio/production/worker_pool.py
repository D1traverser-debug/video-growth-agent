from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Thread
from typing import Any

from ..engine import StudioEngine
from .executors import run_claimed_tool_task, tool_executor_for_task
from .registry import PRODUCTION_EXECUTORS


def _run_with_heartbeat(
    engine: StudioEngine, project_id: str, packet: dict[str, Any], *,
    lease_seconds: int, heartbeat_interval_seconds: float,
) -> dict[str, Any]:
    task_id = packet["task"]["task_id"]
    worker_id = packet["claim"]["worker_id"]
    claim_token = packet["claim"]["claim_token"]
    stop = Event()
    heartbeat_errors: list[Exception] = []

    def keep_lease_alive() -> None:
        while not stop.wait(heartbeat_interval_seconds):
            try:
                engine.heartbeat(project_id, task_id, worker_id, claim_token, lease_seconds)
            except Exception as exc:
                heartbeat_errors.append(exc)
                return

    heartbeat_thread = Thread(target=keep_lease_alive, name=f"vga-lease-{task_id}", daemon=True)
    heartbeat_thread.start()
    try:
        result = run_claimed_tool_task(engine, project_id, task_id, worker_id, claim_token)
    finally:
        stop.set()
        heartbeat_thread.join(timeout=max(1.0, heartbeat_interval_seconds + 1.0))

    if heartbeat_errors:
        current = next((item for item in engine.list_tasks(project_id) if item["task_id"] == task_id), None)
        # A heartbeat racing with the task's own atomic completion is harmless.
        # Any other lost lease means this worker no longer owns the execution.
        if current is None or current["status"] != "COMPLETED":
            raise RuntimeError(f"worker lease was lost while executing {task_id}: {heartbeat_errors[0]}")
    return result


def run_ready_tool_tasks(
    engine: StudioEngine, project_id: str, *, worker_prefix: str = "local-tool",
    max_workers: int = 2, lease_seconds: int = 900, max_rounds: int = 50,
    heartbeat_interval_seconds: float | None = None,
) -> dict[str, Any]:
    """Run only registered local tools; report every other executor as outstanding work."""
    if not 1 <= max_workers <= 16:
        raise ValueError("max_workers must be between 1 and 16")
    if not 1 <= max_rounds <= 500:
        raise ValueError("max_rounds must be between 1 and 500")
    if lease_seconds < 30 or lease_seconds > 86400:
        raise ValueError("lease_seconds must be between 30 and 86400")
    heartbeat_interval = heartbeat_interval_seconds or max(5.0, min(60.0, lease_seconds / 3.0))
    if heartbeat_interval <= 0 or heartbeat_interval >= lease_seconds:
        raise ValueError("heartbeat_interval_seconds must be positive and shorter than the lease")

    completed: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    claimed_total: list[dict[str, Any]] = []
    unregistered_by_id: dict[str, dict[str, Any]] = {}
    rounds = 0

    for round_number in range(1, max_rounds + 1):
        rounds = round_number
        tasks = engine.list_tasks(project_id)
        ready_tools = [item for item in tasks if item.get("status") == "READY" and item.get("executor") == "tool"]
        candidates = [item for item in ready_tools if tool_executor_for_task(item)]
        for item in ready_tools:
            if not tool_executor_for_task(item):
                unregistered_by_id[item["task_id"]] = {
                    "task_id": item["task_id"], "title": item.get("title"),
                    "kind": item.get("kind"), "requirements": item.get("requirements", {}),
                }
        if not candidates:
            break

        claims: list[dict[str, Any]] = []
        for index, task in enumerate(candidates[:max_workers], start=1):
            worker_id = f"{worker_prefix}-{round_number}-{index}"
            packet = engine.claim_next(project_id, worker_id, lease_seconds, executor="tool", task_id=task["task_id"])
            if packet:
                claims.append(packet)
                claimed_total.append({"task_id": task["task_id"], "worker_id": worker_id})
        if not claims:
            break

        with ThreadPoolExecutor(max_workers=len(claims), thread_name_prefix="vga-tool") as pool:
            futures = {
                pool.submit(
                    _run_with_heartbeat, engine, project_id, packet,
                    lease_seconds=lease_seconds,
                    heartbeat_interval_seconds=heartbeat_interval,
                ): packet for packet in claims
            }
            for future in as_completed(futures):
                packet = futures[future]
                try:
                    completed.append({"task_id": packet["task"]["task_id"], "result": future.result()})
                except Exception as exc:
                    failed.append({
                        "task_id": packet["task"]["task_id"],
                        "error_type": type(exc).__name__, "error": str(exc),
                    })

    remaining_tasks = engine.list_tasks(project_id)
    task_counts: dict[str, int] = {}
    ready_by_executor: dict[str, list[str]] = {}
    for item in remaining_tasks:
        state = item.get("status", "UNKNOWN")
        task_counts[state] = task_counts.get(state, 0) + 1
        if state == "READY":
            ready_by_executor.setdefault(item.get("executor", "unknown"), []).append(item["task_id"])
    remaining_ready = [
        {"task_id": item["task_id"], "title": item.get("title")}
        for item in remaining_tasks
        if item.get("status") == "READY" and item.get("executor") == "tool"
        and tool_executor_for_task(item)
    ]
    all_tasks_complete = bool(remaining_tasks) and all(item["status"] == "COMPLETED" for item in remaining_tasks)
    project_status = "TASK_GRAPH_COMPLETE" if all_tasks_complete else "IN_PROGRESS"

    if failed or task_counts.get("FAILED", 0):
        scheduler_status = "FAILED_TASKS"
        next_action = "Inspect failure records, compare root-cause hypotheses, and repair the smallest proven cause."
    elif unregistered_by_id:
        scheduler_status = "BLOCKED_UNREGISTERED_TOOL_EXECUTOR"
        next_action = "Register and verify a real executor for each unhandled tool task; do not mark it complete."
    elif remaining_ready:
        scheduler_status = "LOCAL_TOOL_WORK_PENDING"
        next_action = "Run another local tool round or increase worker capacity."
    elif all_tasks_complete:
        scheduler_status = "TASK_GRAPH_COMPLETE_NOT_RELEASED"
        next_action = "Run release-check against the exact final master; task completion is not release authorization."
    elif ready_by_executor.get("agent"):
        scheduler_status = "AWAITING_AGENT_WORK"
        next_action = "Dispatch the READY agent work packets; the local tool pool does not execute agent tasks."
    elif ready_by_executor.get("human"):
        scheduler_status = "AWAITING_HUMAN_WORK"
        next_action = "Obtain the required owner/human decision or review; do not synthesize an approval."
    elif ready_by_executor.get("external"):
        scheduler_status = "AWAITING_EXTERNAL_CAPABILITY"
        next_action = "Verify capability, rights, availability and cost; obtain owner authorization before paid execution."
    elif task_counts.get("WAITING_INPUT", 0):
        scheduler_status = "WAITING_INPUT"
        next_action = "Import or produce missing declared inputs, then refresh the graph."
    elif task_counts.get("BLOCKED", 0):
        scheduler_status = "BLOCKED_DEPENDENCIES"
        next_action = "Inspect failed or stale dependencies and reopen only after their causes are addressed."
    elif task_counts.get("RUNNING", 0):
        scheduler_status = "RUNNING_OTHER_WORKERS"
        next_action = "Wait for or inspect the active workers; do not duplicate their claims."
    elif task_counts.get("PENDING", 0):
        scheduler_status = "WAITING_DEPENDENCIES"
        next_action = "Inspect dependency state; READY/claim state is distinct from execution."
    elif not remaining_tasks:
        scheduler_status = "EMPTY_TASK_GRAPH"
        next_action = "Create a project-specific task graph from the outcome contract."
    else:
        scheduler_status = "NO_READY_WORK"
        next_action = "Inspect the durable resume snapshot for the next unresolved dependency."

    return {
        "project_id": project_id,
        "rounds": rounds,
        "max_workers": max_workers,
        "lease_seconds": lease_seconds,
        "claimed": claimed_total,
        "completed": completed,
        "failed": failed,
        "task_counts": task_counts,
        "ready_by_executor": ready_by_executor,
        "ready_tool_tasks_without_registered_executor": list(unregistered_by_id.values()),
        "remaining_ready_registered_tool_tasks": remaining_ready,
        "project_status": project_status,
        "scheduler_status": scheduler_status,
        "next_action": next_action,
        "release_authorized": False,
    }
