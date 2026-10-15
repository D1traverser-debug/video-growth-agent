from __future__ import annotations

import hashlib
import json
import re
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .program_orchestration import ProgramGraph, ProgramOrchestrator
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
    "docs/product_requirements.md",
    "docs/media_business_os.md",
    "docs/architecture.md",
    "docs/provider_benchmark_protocol.md",
    "projects/PROJECT_INDEX.json",
    "audits/EVOLUTION_INDEX.json",
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
            wave_tasks = [
                task
                for task in tasks
                if isinstance(task, dict) and int(task.get("wave", 0)) == wave
            ]
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
                        failures.append(
                            f"artifact_duplicate_same_wave_output:{stage}:wave={wave}:{name}"
                        )
                    prior = producer.get(name)
                    if prior:
                        failures.append(
                            f"artifact_multiple_producers:{name}:{prior},{stage}/{task_id}"
                        )
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
                if not (
                    ref.startswith("skills/")
                    or ref.startswith("projects/")
                    or ref.startswith("https://")
                ):
                    failures.append(
                        f"external_candidate_evidence_not_durable:{technique_id}:{ref}"
                    )
    library = TechniqueLibrary()
    candidate_ids = {
        item.technique_id for item in library.techniques.values() if item.status == "candidate"
    }
    broad_tags = {tag for item in library.techniques.values() for tag in item.tags}
    leaked = {
        item.technique_id
        for item in library.find(broad_tags)
        if item.technique_id in candidate_ids
    }
    if leaked:
        failures.append("candidate_techniques_visible_by_default:" + ",".join(sorted(leaked)))
    return failures


def package_audit() -> dict[str, Any]:
    failures: list[str] = []
    agents = AgentRegistry()
    roles = RoleRegistry()
    planner = ExecutionPlanner(agents=agents)
    workflow = _json(data_path("workflow.json"))
    coordination = _json(data_path("coordination-policy.json"))
    package_version = _package_version()

    failures.extend(f"agent_registry:{item}" for item in agents.validate())
    failures.extend(f"execution_plan:{item}" for item in planner.validate())
    failures.extend(f"role_registry:{item}" for item in roles.validate_workflow())
    failures.extend(_artifact_reachability_failures(workflow, planner.config))
    failures.extend(_technique_failures())

    principles = agents.config.get("principles", {})
    if principles.get("tool_labels_are_capability_requests_not_execution_proof") is not True:
        failures.append("agent_tool_labels_not_explicitly_declarative")
    if principles.get("peer_chat") is not False:
        failures.append("agent_peer_chat_enabled")
    if coordination.get("peer_chat_allowed") is not False:
        failures.append("coordination_peer_chat_enabled")
    if coordination.get("artifact_handoffs_required") is not True:
        failures.append("coordination_artifact_handoffs_not_required")
    if coordination.get("media_candidate_contract", {}).get("candidate_generation_is_acceptance") is not False:
        failures.append("media_candidate_generation_acceptance_boundary_missing")
    if coordination.get("media_candidate_contract", {}).get("promotion_decision_required_for_accepted_asset") is not True:
        failures.append("media_asset_promotion_boundary_missing")
    if coordination.get("media_candidate_contract", {}).get("release_decision_separate_from_asset_promotion") is not True:
        failures.append("media_release_boundary_missing")

    patterns = set(coordination.get("patterns", {}))
    required_patterns = {
        "SERIAL_DEPENDENCY",
        "INDEPENDENT_PARALLEL",
        "FAN_OUT_FAN_IN",
        "CONSULTATIVE_ADVICE",
        "COMPETITIVE_CANDIDATES",
        "STRUCTURED_CRITIQUE_AND_REVISION",
        "OWNER_ADJUDICATION",
        "QUORUM_OR_PANEL_REVIEW",
    }
    if not required_patterns <= patterns:
        failures.append("coordination_patterns_incomplete")

    workflow_stages = [item.get("id") for item in workflow.get("stages", [])]
    plan_stages = list(planner.config.get("stages", {}))
    if workflow_stages != plan_stages:
        failures.append("workflow_execution_plan_stage_order_drift")

    used_agents: set[str] = set()
    workflow_by_stage = {
        item["id"]: item for item in workflow.get("stages", []) if item.get("id")
    }
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
            failures.append(
                f"workflow_required_role_without_review_task:{stage}:{','.join(missing)}"
            )

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
        if coordination.get("version") != package_version:
            failures.append("coordination_policy_package_version_drift")

    return {
        "scope": "package",
        "package_version": package_version,
        "workflow_version": workflow.get("version"),
        "agent_registry_version": agents.config.get("version"),
        "execution_plan_version": planner.config.get("version"),
        "coordination_policy_version": coordination.get("version"),
        "failures": failures,
        "pass": not failures,
    }


def _media_business_failures(root: Path, runtime_version: str) -> list[str]:
    failures: list[str] = []
    product_doc = root / "docs/media_business_os.md"
    benchmark_doc = root / "docs/provider_benchmark_protocol.md"
    flywheel_path = root / "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json"
    evolution_path = root / "audits/EVOLUTION_INDEX.json"

    for path, label in (
        (product_doc, "media_business_os_missing"),
        (benchmark_doc, "provider_benchmark_protocol_missing"),
        (flywheel_path, "business_flywheel_missing"),
        (evolution_path, "evolution_index_missing"),
    ):
        if not path.is_file():
            failures.append(label)

    if product_doc.is_file():
        text = product_doc.read_text(encoding="utf-8")
        for token in (
            "Program -> Series -> Episode -> Sequence -> Scene -> Shot -> Take",
            "generation admission != asset promotion != release admission",
            "AI-native media business operating system",
        ):
            if token not in text:
                failures.append(f"media_business_os_semantic_missing:{token}")

    if benchmark_doc.is_file():
        text = benchmark_doc.read_text(encoding="utf-8")
        for benchmark_id in ("B01", "B04", "B06", "B08", "B10"):
            if benchmark_id not in text:
                failures.append(f"provider_benchmark_archetype_missing:{benchmark_id}")

    if flywheel_path.is_file():
        flywheel = _json(flywheel_path)
        if flywheel.get("owner") != "VIDEO_GROWTH_AGENT":
            failures.append("business_flywheel_owner_drift")
        loop_ids = {str(item.get("id")) for item in flywheel.get("loops", [])}
        required = {
            "AUDIENCE_TO_PORTFOLIO",
            "PORTFOLIO_TO_IP",
            "IP_TO_GROWTH",
            "PORTFOLIO_TO_COMMERCIAL",
            "COMMERCIAL_TO_PRODUCTION",
            "PRODUCTION_TO_PORTFOLIO",
            "ALL_OUTCOMES_TO_EVOLUTION",
        }
        if not required <= loop_ids:
            failures.append("business_flywheel_required_loops_missing")
        serialized = json.dumps(flywheel, ensure_ascii=False)
        if "views" not in serialized.lower():
            failures.append("business_flywheel_views_counterexample_missing")

    if evolution_path.is_file():
        evolution = _json(evolution_path)
        if evolution.get("owner") != "DOMAIN:video":
            failures.append("video_evolution_owner_drift")
        if evolution.get("common_behavior_assurance_min") != "1.2.0":
            failures.append("video_evolution_common_behavior_min_drift")
        if not evolution.get("current_open_items") and not evolution.get("recent_resolved_or_promoted"):
            failures.append("video_evolution_index_empty")

    required_runtime_files = (
        "video_growth_agent/media_graph.py",
        "video_growth_agent/production_os.py",
        "video_growth_agent/timeline.py",
        "video_growth_agent/business_objects.py",
        "video_growth_agent/model_registry.py",
        "video_growth_agent/business_metrics.py",
        "video_growth_agent/owner_behavior_admission.py",
    )
    for rel in required_runtime_files:
        if not (root / rel).is_file():
            failures.append(f"media_business_runtime_missing:{rel}")

    return failures


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
    skill_lower = skill_text.lower()
    if "current-session capability handshake" not in skill_lower:
        failures.append("uaos_skill_session_capability_handshake_missing")
    if "D1traverser-debug/universal-agent-os@main" not in skill_text:
        failures.append("uaos_skill_controller_binding_missing")
    if "normal business turns do not traverse a live uaos business proxy" not in skill_lower:
        failures.append("uaos_skill_direct_domain_activation_missing")
    if "projects/project_index.json" not in skill_lower:
        failures.append("uaos_skill_child_project_index_missing")
    if "no parent/child id equality requirement" not in skill_lower:
        failures.append("uaos_skill_identity_boundary_missing")
    if "unbounded" not in skill_lower or "peer chat" not in skill_lower:
        failures.append("uaos_skill_bounded_negotiation_missing")
    if "candidate generation, project-asset promotion and release are separate boundaries" not in skill_lower:
        failures.append("uaos_skill_candidate_promotion_release_boundary_missing")
    if "audits/evolution_index.json" not in skill_lower:
        failures.append("uaos_skill_evolution_entrypoint_missing")

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
        if capability.get("profile_version") != 8:
            failures.append("uaos_capability_profile_drift")
        if capability.get("uaos_common_capabilities_contract_min") != "1.6.0":
            failures.append("uaos_common_capability_minimum_drift")
        if capability.get("uaos_common_behavior_assurance_min") != "1.2.0":
            failures.append("uaos_common_behavior_minimum_drift")
        if capability.get("canonical_evolution_entrypoint") != "audits/EVOLUTION_INDEX.json":
            failures.append("uaos_capability_evolution_entrypoint_drift")
        required_common = set(capability.get("required_uaos_common_capabilities", []))
        for required in (
            "product_requirements_and_architecture_governance",
            "domain_internal_work_orchestration",
            "adaptive_deliberation_and_parent_guidance",
            "governed_self_evolution",
        ):
            if required not in required_common:
                failures.append(f"uaos_required_common_capability_missing:{required}")
        floor = capability.get("hosted_cognition_semantics", {}).get("problem_response_floor")
        if floor != [
            "MICRO_DIAGNOSIS",
            "MACRO_GOAL_AND_TOPOLOGY_ALIGNMENT",
            "GOVERNING_ASSUMPTION_CHALLENGE",
            "EXTERNAL_METHOD_OR_ARCHITECTURE_RESEARCH",
        ]:
            failures.append("uaos_problem_response_floor_drift")
        capability_ids = {str(item.get("capability_id")) for item in capability.get("capabilities", [])}
        for required_id in (
            "media_business_program_orchestration",
            "canonical_media_graph",
            "shot_asset_production_os",
            "non_destructive_editorial_timeline",
            "shared_growth_ip_commercial_objects",
            "evidence_bound_model_routing",
            "business_outcome_measurement",
            "owner_common_behavior_admission",
            "studio_work_order_orchestration",
            "critical_blind_multimodal_review",
            "deterministic_media_qa",
            "learning_and_evolution",
        ):
            if required_id not in capability_ids:
                failures.append(f"media_business_capability_missing:{required_id}")

    manifest_path = root / ".uaos/MANIFEST.json"
    if manifest_path.is_file():
        manifest = _json(manifest_path)
        if manifest.get("controller") != "D1traverser-debug/universal-agent-os@main":
            failures.append("uaos_manifest_controller_drift")
        if manifest.get("status") != "UAOS_CONTROL_PLANE_ACTIVE":
            failures.append("uaos_manifest_status_drift")
        if manifest.get("skill", {}).get("entrypoint") != "UAOS_SKILL.md":
            failures.append("uaos_manifest_skill_entrypoint_drift")
        runtime = manifest.get("runtime", {})
        if runtime.get("version") != runtime_version:
            failures.append("uaos_manifest_runtime_version_drift")
        expected_runtime_refs = {
            "episode_workflow": "video_growth_agent/data/workflow.json",
            "program_orchestration": "video_growth_agent/program_orchestration.py",
            "media_graph": "video_growth_agent/media_graph.py",
            "media_business_os": "video_growth_agent/production_os.py",
            "timeline": "video_growth_agent/timeline.py",
            "business_objects": "video_growth_agent/business_objects.py",
            "model_registry": "video_growth_agent/model_registry.py",
            "business_metrics": "video_growth_agent/business_metrics.py",
            "owner_behavior_admission": "video_growth_agent/owner_behavior_admission.py",
            "system_audit": "vga system-audit --repo-root .",
        }
        for key, expected in expected_runtime_refs.items():
            if runtime.get(key) != expected:
                failures.append(f"uaos_manifest_runtime_ref_drift:{key}")
        domain_authority = manifest.get("domain_authority", {})
        if domain_authority.get("project_index") != "projects/PROJECT_INDEX.json":
            failures.append("uaos_manifest_project_index_drift")
        if domain_authority.get("architecture") != "docs/media_business_os.md":
            failures.append("uaos_manifest_media_business_architecture_drift")
        if domain_authority.get("canonical_evolution_entrypoint") != "audits/EVOLUTION_INDEX.json":
            failures.append("uaos_manifest_evolution_entrypoint_drift")
        if domain_authority.get("integrated_business_flywheel") != "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json":
            failures.append("uaos_manifest_business_flywheel_drift")

    adapter_path = root / ".uaos/ADAPTER.json"
    if adapter_path.is_file():
        adapter = _json(adapter_path)
        if adapter.get("controller_task_identity_authority") != "UAOS":
            failures.append("uaos_adapter_controller_identity_authority_drift")
        if adapter.get("domain_business_identity_authority") != "VIDEO_GROWTH_AGENT":
            failures.append("uaos_adapter_domain_identity_authority_drift")
        if "NO_EQUALITY_REQUIREMENT" not in str(adapter.get("identity_boundary", "")):
            failures.append("uaos_adapter_identity_namespace_collapsed")
        if "OPAQUE_CHILD_STATE_REFERENCE_ONLY" not in str(adapter.get("parent_reference_semantics", "")):
            failures.append("uaos_adapter_parent_ref_not_opaque")
        if not str(adapter.get("session_activation", "")).startswith("DIRECT_VIDEO_WORK_PLANE"):
            failures.append("uaos_adapter_direct_activation_drift")
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
    for path in global_docs:
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = str(path)
        if not path.is_file():
            failures.append(f"global_reference_missing:{rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if any(
            stale in text
            for stale in (
                "config/workflow.json",
                "config/roles.json",
                "config/quality-rubric.json",
                "config/techniques.json",
            )
        ):
            failures.append(f"stale_root_config_reference:{rel}")
        match = VERSIONED_PROJECT_STATE_RE.search(text)
        if match:
            failures.append(f"project_version_state_pollution:{rel}:{match.group(0)}")

    project_index_path = root / "projects/PROJECT_INDEX.json"
    if project_index_path.is_file():
        project_index = _json(project_index_path)
        if project_index.get("authority") != "VIDEO_GROWTH_AGENT":
            failures.append("project_index_authority_drift")
        if project_index.get("default_project_id") != "ai-self-media-commercialization":
            failures.append("project_index_default_program_drift")
        projects = project_index.get("projects", [])
        by_id = {str(item.get("project_id")): item for item in projects}
        if set(by_id) < {"ai-self-media-commercialization", "pilot-002"}:
            failures.append("project_index_required_projects_missing")
        integrated_aliases = set(by_id.get("ai-self-media-commercialization", {}).get("aliases", []))
        for alias in ("AI自媒体视频商业化", "AI视频涨粉与商业化", "原创数字IP"):
            if alias not in integrated_aliases:
                failures.append(f"project_index_integrated_alias_missing:{alias}")
        pilot_aliases = set(by_id.get("pilot-002", {}).get("aliases", []))
        if "video-growth:main" not in pilot_aliases:
            failures.append("pilot002_legacy_alias_missing")
        if "video-growth:main" in integrated_aliases:
            failures.append("project_index_legacy_alias_collision")

    pilot_state_path = root / "projects/pilot-002/PROGRAM_STATE.json"
    if not pilot_state_path.is_file():
        failures.append("pilot002_program_state_missing")
    else:
        pilot = _json(pilot_state_path)
        if pilot.get("project_id") != "pilot-002":
            failures.append("pilot002_project_identity_drift")
        if pilot.get("runtime_version") != runtime_version:
            failures.append("pilot002_program_runtime_version_drift")
        if pilot.get("owner") != "VIDEO_GROWTH_AGENT":
            failures.append("pilot002_owner_drift")
        if "video-growth:main" not in set(pilot.get("legacy_aliases", [])):
            failures.append("pilot002_legacy_alias_state_missing")
        if "UAOS task identity" not in str(pilot.get("legacy_alias_semantics", "")):
            failures.append("pilot002_legacy_alias_semantics_missing")
        serialized = json.dumps(pilot, ensure_ascii=False)
        for retired_marker in (
            "continuity_protocol_version",
            "resume_epoch",
            "active_lease",
            "Universal Continuity",
        ):
            if retired_marker in serialized:
                failures.append(f"pilot002_program_legacy_control_marker:{retired_marker}")
        if pilot.get("controller_authority") or pilot.get("controller_task_ref"):
            failures.append("pilot002_parent_business_identity_returned")
        if pilot.get("stage_state", {}).get("previous_release_gate_valid") is not False:
            failures.append("pilot002_rejected_release_gate_resurrected")
        if "CANDIDATE_GENERATION_ALLOWED_ONLY_AFTER_CURRENT_0_7_ADMISSION" not in str(
            pilot.get("stage_state", {}).get("shot_a_status", "")
        ):
            failures.append("pilot002_candidate_promotion_migration_missing")

    integrated_state_path = root / "projects/ai-self-media-commercialization/PROGRAM_STATE.json"
    graph_path = root / "projects/ai-self-media-commercialization/SUBTASK_GRAPH.json"
    manifest_project_path = root / "projects/ai-self-media-commercialization/PROJECT_MANIFEST.json"
    flywheel_path = root / "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json"
    if not integrated_state_path.is_file():
        failures.append("integrated_program_state_missing")
    else:
        integrated = _json(integrated_state_path)
        if integrated.get("program_id") != "ai-self-media-commercialization":
            failures.append("integrated_program_identity_drift")
        if integrated.get("owner") != "VIDEO_GROWTH_AGENT":
            failures.append("integrated_program_owner_drift")
        workstreams = set(integrated.get("workstreams", {}))
        if workstreams != {
            "MEDIA_GROWTH",
            "ORIGINAL_DIGITAL_IP",
            "COMMERCIALIZATION",
            "PRODUCTION_SYSTEM",
        }:
            failures.append("integrated_program_workstream_set_drift")
        if integrated.get("current_focus") != "ORIGINAL_DIGITAL_IP/H1_SCULPTURAL_MASSING_V2":
            failures.append("integrated_program_h1_focus_drift")
        if "A2 positive-morph upper-face edit" not in str(integrated.get("current_next_action", "")):
            failures.append("integrated_program_h1_next_action_drift")
        if integrated.get("business_flywheel_ref") != "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json":
            failures.append("integrated_program_business_flywheel_ref_drift")

    if manifest_project_path.is_file():
        project_manifest = _json(manifest_project_path)
        if project_manifest.get("business_flywheel_ref") != "BUSINESS_FLYWHEEL.json":
            failures.append("integrated_project_manifest_flywheel_ref_drift")
        if project_manifest.get("product_architecture_ref") != "../../docs/media_business_os.md":
            failures.append("integrated_project_manifest_architecture_ref_drift")
    else:
        failures.append("integrated_project_manifest_missing")

    if not graph_path.is_file():
        failures.append("integrated_subtask_graph_missing")
    else:
        try:
            graph_payload = _json(graph_path)
            graph = ProgramGraph(graph_payload)
            run = ProgramOrchestrator(graph)
            ready = {node.node_id for node in run.ready()}
            declared_parallel = set(graph_payload.get("parallel_now", []))
            if ready != declared_parallel:
                failures.append(
                    "integrated_program_parallel_readiness_drift:"
                    + f"ready={sorted(ready)}:declared={sorted(declared_parallel)}"
                )
            groups = graph.decision_groups()
            for required_group in ("commercial_offer_architecture", "pilot_topic_slate"):
                if len(groups.get(required_group, ())) < 2:
                    failures.append(f"integrated_program_competition_missing:{required_group}")
        except (ValueError, KeyError, TypeError) as exc:
            failures.append(f"integrated_subtask_graph_invalid:{exc}")

    failures.extend(_media_business_failures(root, runtime_version))

    coordination = _json(root / "video_growth_agent/data/coordination-policy.json")
    workflow = _json(root / "video_growth_agent/data/workflow.json")
    execution_plan = _json(root / "video_growth_agent/data/execution-plan.json")
    agents = _json(root / "video_growth_agent/data/agents.json")
    failures.extend(_artifact_reachability_failures(workflow, execution_plan))
    if coordination.get("version") != runtime_version:
        failures.append("coordination_policy_repo_version_drift")
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
