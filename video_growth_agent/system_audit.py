from __future__ import annotations

import hashlib
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .resources import data_path
from .roles import RoleRegistry
from .studio_agents import AgentRegistry, ExecutionPlanner

PROJECT_MARKERS = ("Pilot 002", "Sample V2", "Release V4")
REQUIRED_ASSURANCE_TERMS = ("DECLARED_ONLY", "HARNESS_WIRED", "SESSION_EXECUTABLE", "CHAT_BRIDGED", "ATTESTED_ISOLATED")


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def package_audit() -> dict[str, Any]:
    failures: list[str] = []
    agents = AgentRegistry()
    roles = RoleRegistry()
    planner = ExecutionPlanner(agents=agents)
    workflow = _json(data_path("workflow.json"))

    failures.extend(f"agent_registry:{item}" for item in agents.validate())
    failures.extend(f"execution_plan:{item}" for item in planner.validate())
    failures.extend(f"role_registry:{item}" for item in roles.validate_workflow())

    principles = agents.config.get("principles", {})
    if principles.get("tool_labels_are_capability_requests_not_execution_proof") is not True:
        failures.append("agent_tool_labels_not_explicitly_declarative")

    workflow_stages = [item.get("id") for item in workflow.get("stages", [])]
    plan_stages = list(planner.config.get("stages", {}))
    if workflow_stages != plan_stages:
        failures.append("workflow_execution_plan_stage_order_drift")

    used_agents: set[str] = set()
    workflow_by_stage = {item["id"]: item for item in workflow.get("stages", []) if item.get("id")}
    for stage, spec in planner.config.get("stages", {}).items():
        review_roles: set[str] = set()
        for task in spec.get("tasks", []):
            if task.get("executor") == "agent" and task.get("agent"):
                used_agents.add(str(task["agent"]))
            if task.get("type") == "produce" and task.get("approval_role"):
                failures.append(f"producer_declares_approval_role:{stage}/{task.get('id')}")
            if task.get("type") in {"review", "meta_review"} and task.get("approval_role"):
                review_roles.add(str(task["approval_role"]))
        required = set(workflow_by_stage.get(stage, {}).get("required_roles", []))
        missing = sorted(required - review_roles)
        if missing:
            failures.append(f"workflow_required_role_without_review_task:{stage}:{','.join(missing)}")

    registered = set(agents.config.get("agents", {}))
    dead = sorted(registered - used_agents - {"executive_producer"})
    if dead:
        failures.append("unused_agent_profiles:" + ",".join(dead))

    role_cfg = _json(data_path("roles.json"))
    if role_cfg.get("prompt_source_local") != "team.md":
        failures.append("roles_prompt_source_local_not_explicit")
    if role_cfg.get("canonical_prompt_source") != "skills/video-growth-agent/references/team.md":
        failures.append("roles_canonical_prompt_source_not_explicit")

    try:
        package_version = version("video-growth-agent")
    except PackageNotFoundError:
        package_version = "UNINSTALLED_EDITABLE_SOURCE"

    return {
        "scope": "package",
        "package_version": package_version,
        "workflow_version": workflow.get("version"),
        "agent_registry_version": agents.config.get("version"),
        "execution_plan_version": planner.config.get("version"),
        "failures": failures,
        "pass": not failures,
    }


def repository_audit(repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    failures: list[str] = []

    if (root / "config").exists():
        failures.append("duplicate_root_config_authority_present")

    skill_path = root / "skills/video-growth-agent/SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
    if "session capability handshake" not in skill_text.lower():
        failures.append("skill_session_capability_handshake_missing")
    for term in REQUIRED_ASSURANCE_TERMS:
        if term not in skill_text:
            failures.append(f"skill_assurance_term_missing:{term}")

    skill_team = root / "skills/video-growth-agent/references/team.md"
    packaged_team = root / "video_growth_agent/data/team.md"
    if not skill_team.is_file() or not packaged_team.is_file():
        failures.append("team_prompt_mirror_missing")
    elif skill_team.read_bytes() != packaged_team.read_bytes():
        failures.append("team_prompt_mirror_drift")

    global_docs = sorted((root / "skills/video-growth-agent").rglob("*.md"))
    global_docs.extend([root / "continuity/TASK_INDEX.md", root / "README.md"])
    for path in global_docs:
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = str(path)
        if not path.is_file():
            failures.append(f"global_reference_missing:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if any(stale in text for stale in ("config/workflow.json", "config/roles.json", "config/quality-rubric.json", "config/techniques.json")):
            failures.append(f"stale_root_config_reference:{rel}")
        for marker in PROJECT_MARKERS:
            if marker in text:
                failures.append(f"project_state_pollution:{rel}:{marker}")

    architecture_path = root / "continuity/AGENT_MANIFEST.json"
    if not architecture_path.is_file():
        failures.append("agent_architecture_manifest_missing")
    else:
        architecture = _json(architecture_path)
        architecture_text = architecture_path.read_text(encoding="utf-8")
        if '"config/' in architecture_text or '"config"' in architecture_text:
            failures.append("agent_architecture_manifest_stale_config_authority")
        if architecture.get("runtime", {}).get("version") != "0.5.1":
            failures.append("agent_architecture_manifest_runtime_version_drift")
        if architecture.get("workflow", {}).get("state_authority_refs", [])[-1:] != ["video_growth_agent/data/workflow.json"]:
            failures.append("agent_architecture_manifest_workflow_authority_drift")
        if architecture.get("harness", {}).get("system_audit_entrypoint") != "vga system-audit --repo-root .":
            failures.append("agent_architecture_manifest_harness_entrypoint_drift")

    if (root / "continuity/CHECKPOINT_COMPACTION_PLAN.json").exists():
        failures.append("completed_or_staged_compaction_plan_still_present")

    checkpoint_path = root / "continuity/tasks/video-growth-main/CHECKPOINT.json"
    manifest_path = root / "continuity/tasks/video-growth-main/TASK_MANIFEST.json"
    if checkpoint_path.is_file():
        checkpoint = _json(checkpoint_path)
        if "preserved_user_requirements" in checkpoint:
            failures.append("checkpoint_contains_preserved_user_requirements_prose")
        if checkpoint.get("runtime_version") != "0.5.1":
            failures.append("checkpoint_runtime_version_drift")
    if manifest_path.is_file():
        manifest = _json(manifest_path)
        if manifest.get("runtime_version") != "0.5.1":
            failures.append("manifest_runtime_version_drift")
        expected_skill = f"skills/video-growth-agent/SKILL.md@{_git_blob_sha(skill_path)}" if skill_path.is_file() else None
        if manifest.get("skill_version") != expected_skill:
            failures.append("manifest_skill_version_pointer_drift")

    return {"scope": "repository", "repo_root": str(root), "failures": failures, "pass": not failures}


def run_system_audit(repo_root: Path | None = None) -> dict[str, Any]:
    package = package_audit()
    repository = repository_audit(repo_root) if repo_root is not None else None
    failures = list(package["failures"])
    if repository is not None:
        failures.extend(repository["failures"])
    return {
        "package": package,
        "repository": repository,
        "failures": failures,
        "pass": not failures,
    }
