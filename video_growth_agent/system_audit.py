from __future__ import annotations

import hashlib
import json
import re
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .resources import data_path
from .roles import RoleRegistry
from .studio_agents import AgentRegistry, ExecutionPlanner
from .techniques import TechniqueLibrary

REQUIRED_ASSURANCE_TERMS = (
    "DECLARED_ONLY",
    "HARNESS_WIRED",
    "SESSION_EXECUTABLE",
    "CHAT_BRIDGED",
    "ATTESTED_ISOLATED",
)
CURRENT_GLOBAL_FILES = (
    "UAOS_SKILL.md",
    ".uaos/MANIFEST.json",
    ".uaos/ADAPTER.json",
    ".uaos/CAPABILITIES.json",
    "README.md",
)
RETIRED_ACTIVE_PATHS = ("continuity",)
VERSIONED_PROJECT_STATE_RE = re.compile(r"\b(?:sample|release)\s+v\d+\b", re.IGNORECASE)


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _package_version() -> str:
    try:
        return version("video-growth-agent")
    except PackageNotFoundError:
        return "UNINSTALLED_EDITABLE_SOURCE"


def _repo_runtime_version(root: Path) -> str:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["version"])


def _project_aliases(root: Path) -> set[str]:
    projects = root / "projects"
    if not projects.is_dir():
        return set()
    aliases: set[str] = set()
    for path in projects.iterdir():
        if not path.is_dir():
            continue
        slug = path.name.lower()
        aliases.add(slug)
        aliases.add(re.sub(r"[-_]+", " ", slug))
    return {alias for alias in aliases if alias}


def _artifact_reachability_failures(workflow: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    available: set[str] = set()
    producer: dict[str, str] = {}
    plan_stages = plan.get("stages", {})
    for stage_spec in workflow.get("stages", []):
        stage = str(stage_spec.get("id") or "")
        stage_plan = plan_stages.get(stage)
        if not isinstance(stage_plan, dict):
            failures.append(f"execution_plan_stage_missing:{stage}")
            continue
        external_inputs = stage_plan.get("external_inputs", [])
        if not isinstance(external_inputs, list):
            failures.append(f"external_inputs_invalid:{stage}")
            external_inputs = []
        external = {str(name) for name in external_inputs}
        if external and not str(stage_plan.get("external_input_contract") or "").strip():
            failures.append(f"external_input_contract_missing:{stage}")
        stage_available = set(available) | external
        tasks = stage_plan.get("tasks", [])
        waves = sorted({int(task.get("wave", 0)) for task in tasks if isinstance(task, dict)})
        for wave in waves:
            wave_tasks = [task for task in tasks if isinstance(task, dict) and int(task.get("wave", 0)) == wave]
            wave_outputs: set[str] = set()
            for task in wave_tasks:
                task_id = str(task.get("id") or "")
                for input_name in task.get("inputs", []):
                    name = str(input_name)
                    if name not in stage_available:
                        failures.append(f"artifact_input_unreachable:{stage}/{task_id}:{name}")
                for output_name in task.get("outputs", []):
                    name = str(output_name)
                    if name in wave_outputs:
                        failures.append(f"artifact_duplicate_same_wave_output:{stage}:wave={wave}:{name}")
                    prior = producer.get(name)
                    if prior:
                        failures.append(f"artifact_multiple_producers:{name}:{prior},{stage}/{task_id}")
                    wave_outputs.add(name)
                    producer[name] = f"{stage}/{task_id}"
            stage_available.update(wave_outputs)
        required = {str(name) for name in stage_spec.get("required_artifacts", [])}
        for name in sorted(required - stage_available):
            failures.append(f"workflow_required_artifact_unreachable:{stage}:{name}")
        available = stage_available
    return failures


def _technique_failures() -> list[str]:
    failures: list[str] = []
    payload = _json(data_path("techniques.json"))
    policy = payload.get("policy", {})
    if policy.get("production_default") != "validated_only":
        failures.append("technique_production_default_not_validated_only")
    items = payload.get("techniques", [])
    valid_statuses = {"candidate", "validated", "retired", "rejected"}
    for item in items:
        technique_id = str(item.get("id") or "")
        status = str(item.get("status") or "candidate")
        origin = str(item.get("origin") or "").strip()
        refs = [str(ref).strip() for ref in item.get("evidence_refs", [])]
        if status not in valid_statuses:
            failures.append(f"technique_status_invalid:{technique_id}:{status}")
        if not origin:
            failures.append(f"technique_origin_missing:{technique_id}")
        if status == "validated" and not refs:
            failures.append(f"validated_technique_evidence_missing:{technique_id}")
        if origin == "historical_external_candidate":
            if not refs:
                failures.append(f"external_candidate_evidence_missing:{technique_id}")
            for ref in refs:
                if not (ref.startswith("skills/") or ref.startswith("projects/") or ref.startswith("https://")):
                    failures.append(f"external_candidate_evidence_not_durable:{technique_id}:{ref}")
    library = TechniqueLibrary()
    candidate_ids = {item.technique_id for item in library.techniques.values() if item.status == "candidate"}
    broad_tags = {tag for item in library.techniques.values() for tag in item.tags}
    leaked = {item.technique_id for item in library.find(broad_tags) if item.technique_id in candidate_ids}
    if leaked:
        failures.append("candidate_techniques_visible_by_default:" + ",".join(sorted(leaked)))
    return failures


def package_audit() -> dict[str, Any]:
    failures: list[str] = []
    agents = AgentRegistry()
    roles = RoleRegistry()
    planner = ExecutionPlanner(agents=agents)
    workflow = _json(data_path("workflow.json"))
    package_version = _package_version()

    failures.extend(f"agent_registry:{item}" for item in agents.validate())
    failures.extend(f"execution_plan:{item}" for item in planner.validate())
    failures.extend(f"role_registry:{item}" for item in roles.validate_workflow())
    failures.extend(_artifact_reachability_failures(workflow, planner.config))
    failures.extend(_technique_failures())

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

    if package_version != "UNINSTALLED_EDITABLE_SOURCE":
        if agents.config.get("version") != package_version:
            failures.append("agent_registry_package_version_drift")
        if planner.config.get("version") != package_version:
            failures.append("execution_plan_package_version_drift")

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
    runtime_version = _repo_runtime_version(root)

    if (root / "config").exists():
        failures.append("duplicate_root_config_authority_present")
    for retired in RETIRED_ACTIVE_PATHS:
        if (root / retired).exists():
            failures.append(f"retired_control_plane_returned:{retired}")

    for rel in CURRENT_GLOBAL_FILES:
        if not (root / rel).is_file():
            failures.append(f"current_global_file_missing:{rel}")

    skill_path = root / "UAOS_SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8") if skill_path.is_file() else ""
    if "current-session capability handshake" not in skill_text.lower():
        failures.append("uaos_skill_session_capability_handshake_missing")
    if "D1traverser-debug/universal-agent-os@main" not in skill_text:
        failures.append("uaos_skill_controller_binding_missing")

    capability_path = root / ".uaos/CAPABILITIES.json"
    if capability_path.is_file():
        capability_text = capability_path.read_text(encoding="utf-8")
        capability = _json(capability_path)
        for term in REQUIRED_ASSURANCE_TERMS:
            if term not in capability_text:
                failures.append(f"capability_assurance_term_missing:{term}")
        if capability.get("owner") != "VIDEO_GROWTH_AGENT":
            failures.append("uaos_capability_owner_drift")
        if capability.get("execution_readiness_contract") != "2.0":
            failures.append("uaos_execution_readiness_contract_drift")

    manifest_path = root / ".uaos/MANIFEST.json"
    if manifest_path.is_file():
        manifest = _json(manifest_path)
        if manifest.get("controller") != "D1traverser-debug/universal-agent-os@main":
            failures.append("uaos_manifest_controller_drift")
        if manifest.get("status") != "UAOS_CONTROL_PLANE_ACTIVE":
            failures.append("uaos_manifest_status_drift")
        if manifest.get("skill", {}).get("entrypoint") != "UAOS_SKILL.md":
            failures.append("uaos_manifest_skill_entrypoint_drift")
        if manifest.get("runtime", {}).get("version") != runtime_version:
            failures.append("uaos_manifest_runtime_version_drift")
        if manifest.get("runtime", {}).get("workflow") != "video_growth_agent/data/workflow.json":
            failures.append("uaos_manifest_workflow_authority_drift")
        if manifest.get("runtime", {}).get("system_audit") != "vga system-audit --repo-root .":
            failures.append("uaos_manifest_harness_entrypoint_drift")

    adapter_path = root / ".uaos/ADAPTER.json"
    if adapter_path.is_file():
        adapter = _json(adapter_path)
        if adapter.get("task_identity_authority") != "UAOS" or adapter.get("cross_chat_continuity_authority") != "UAOS":
            failures.append("uaos_adapter_control_authority_drift")
        if adapter.get("legacy_controller_compatibility") != "NONE":
            failures.append("uaos_adapter_legacy_compatibility_enabled")

    skill_team = root / "skills/video-growth-agent/references/team.md"
    packaged_team = root / "video_growth_agent/data/team.md"
    if not skill_team.is_file() or not packaged_team.is_file():
        failures.append("team_prompt_mirror_missing")
    elif skill_team.read_bytes() != packaged_team.read_bytes():
        failures.append("team_prompt_mirror_drift")

    global_docs = sorted((root / "skills/video-growth-agent").rglob("*.md"))
    global_docs.extend(root / rel for rel in CURRENT_GLOBAL_FILES if rel.endswith(".md"))
    project_aliases = _project_aliases(root)
    for path in global_docs:
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = str(path)
        if not path.is_file():
            failures.append(f"global_reference_missing:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        if any(stale in text for stale in ("config/workflow.json", "config/roles.json", "config/quality-rubric.json", "config/techniques.json")):
            failures.append(f"stale_root_config_reference:{rel}")
        for alias in sorted(project_aliases):
            if alias in lower:
                failures.append(f"project_state_pollution:{rel}:{alias}")
        match = VERSIONED_PROJECT_STATE_RE.search(text)
        if match:
            failures.append(f"project_version_state_pollution:{rel}:{match.group(0)}")

    program_state_path = root / "projects/pilot-002/PROGRAM_STATE.json"
    if not program_state_path.is_file():
        failures.append("pilot002_program_state_missing")
    else:
        program = _json(program_state_path)
        if program.get("program_id") != "video-growth:main":
            failures.append("pilot002_program_identity_drift")
        if program.get("runtime_version") != runtime_version:
            failures.append("pilot002_program_runtime_version_drift")
        if program.get("controller_authority") != "D1traverser-debug/universal-agent-os@main":
            failures.append("pilot002_program_controller_drift")
        serialized = json.dumps(program, ensure_ascii=False)
        for retired_marker in ("continuity_protocol_version", "resume_epoch", "active_lease", "Universal Continuity"):
            if retired_marker in serialized:
                failures.append(f"pilot002_program_legacy_control_marker:{retired_marker}")

    workflow = _json(root / "video_growth_agent/data/workflow.json")
    execution_plan = _json(root / "video_growth_agent/data/execution-plan.json")
    agents = _json(root / "video_growth_agent/data/agents.json")
    failures.extend(_artifact_reachability_failures(workflow, execution_plan))
    if execution_plan.get("version") != runtime_version:
        failures.append("execution_plan_repo_version_drift")
    if agents.get("version") != runtime_version:
        failures.append("agent_registry_repo_version_drift")

    return {
        "scope": "repository",
        "repo_root": str(root),
        "runtime_version": runtime_version,
        "failures": failures,
        "pass": not failures,
    }


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
