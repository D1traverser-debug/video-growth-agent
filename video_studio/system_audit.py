from __future__ import annotations

import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import tempfile
import tomllib
from typing import Any

from .engine import StudioEngine


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _check(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: Any) -> None:
    checks.append({"id": check_id, "pass": bool(passed), "detail": detail})


def _authority_paths(root: Path, manifest_path: Path, manifest: dict[str, Any]) -> dict[str, str]:
    return {
        str((manifest_path.parent / item["path"]).resolve()): str(item["name"])
        for item in manifest.get("assets", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str) and isinstance(item.get("path"), str)
    }


def run_system_audit(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Audit the standalone Video Studio contract without invoking CAOS or paid providers.

    This is a repository-level structural/readiness audit. It exercises the project
    engine in temporary directories and never mutates the repository or user workspace.
    A structural PASS does not mean a video has been generated, reviewed or released.
    """
    root = Path(repo_root).expanduser().resolve() if repo_root else Path(__file__).resolve().parents[1]
    checks: list[dict[str, Any]] = []
    capability_gaps: list[str] = []
    owner_inputs_required: list[str] = []

    required_paths = [
        root / "STUDIO_ENTRY.md",
        root / "pyproject.toml",
        root / "video_studio" / "data" / "studio_manifest.json",
        root / "video_studio" / "system_audit.py",
        root / "examples" / "technology-explainer.brief.json",
        root / "examples" / "technology-explainer.tasks.json",
        root / "examples" / "news-fictional-media.brief.json",
        root / "examples" / "news-fictional-media.tasks.json",
        root / "examples" / "ai-self-media-commercialization.brief.json",
        root / "examples" / "ai-self-media-commercialization.tasks.json",
        root / "examples" / "ai-self-media-commercialization.context.json",
        root / "examples" / "program-linked-episode.brief.json",
        root / "examples" / "program-linked-episode.tasks.json",
        root / "projects" / "ai-self-media-commercialization" / "BUSINESS_FLYWHEEL.json",
        root / "examples" / "standalone-domain-adapters.brief.json",
        root / "examples" / "standalone-domain-adapters.tasks.json",
    ]
    missing = [str(path.relative_to(root)) for path in required_paths if not path.is_file()]
    _check(checks, "required_repository_contract_files", not missing, {"missing": missing})
    if missing:
        return {
            "schema_version": "1.0",
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "repository_root": str(root),
            "pass": False,
            "structural_status": "FAIL",
            "production_readiness": "BLOCKED",
            "checks": checks,
            "capability_gaps": [],
            "owner_inputs_required": [],
        }

    try:
        entry = (root / "STUDIO_ENTRY.md").read_text(encoding="utf-8")
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        studio_manifest = _read_json(root / "video_studio" / "data" / "studio_manifest.json")
        program_brief = _read_json(root / "examples" / "ai-self-media-commercialization.brief.json")
        program_tasks = _read_json(root / "examples" / "ai-self-media-commercialization.tasks.json")
        episode_tasks = _read_json(root / "examples" / "program-linked-episode.tasks.json")
        context_path = root / "examples" / "ai-self-media-commercialization.context.json"
        context_manifest = _read_json(context_path)
        business_flywheel = _read_json(root / "projects" / "ai-self-media-commercialization" / "BUSINESS_FLYWHEEL.json")
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, TypeError, KeyError) as exc:
        _check(checks, "repository_contract_parse", False, f"{type(exc).__name__}: {exc}")
        return {
            "schema_version": "1.0",
            "audited_at": datetime.now(timezone.utc).isoformat(),
            "repository_root": str(root),
            "pass": False,
            "structural_status": "FAIL",
            "production_readiness": "BLOCKED",
            "checks": checks,
            "capability_gaps": [],
            "owner_inputs_required": [],
        }

    governance = studio_manifest.get("governance", {})
    entry_ok = (
        "video_studio.engine.StudioEngine" in entry
        and "vga-studio" in entry
        and "ai-self-media-commercialization" in entry
        and "import-manifest" in entry
        and "system-audit" in entry
        and studio_manifest.get("system_audit") == "video_studio.system_audit.run_system_audit"
        and governance.get("system") == "VIDEO_STUDIO_NATIVE"
        and governance.get("mode") == "STANDALONE"
        and governance.get("caos_runtime_dependency") is False
        and governance.get("caos_api_dependency") is False
        and governance.get("caos_skill_dependency") is False
        and governance.get("parent_task_or_lease_dependency") is False
    )
    _check(checks, "standalone_entry_and_governance", entry_ok, {
        "entry": "STUDIO_ENTRY.md",
        "runtime": studio_manifest.get("runtime"),
        "governance": governance,
    })

    scripts = pyproject.get("project", {}).get("scripts", {})
    cli_source = (root / "video_studio" / "cli.py").read_text(encoding="utf-8")
    cli_registered = (
        scripts.get("vga-studio") == "video_studio.cli:main"
        and "system-audit" in cli_source and "import-manifest" in cli_source
        and "transfer-asset" in cli_source and hasattr(StudioEngine, "transfer_artifact")
    )
    _check(checks, "standalone_cli_registration", cli_registered, scripts)

    import_failures: list[str] = []
    scanned_files = sorted((root / "video_studio").rglob("*.py"))
    for path in scanned_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            import_failures.append(f"{path.relative_to(root)}: {type(exc).__name__}: {exc}")
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
            for module in modules:
                if module == "caos" or module.startswith("caos.") or module.startswith("cognition_agent_os"):
                    import_failures.append(f"{path.relative_to(root)} imports {module}")
                if module == "video_growth_agent" or module.startswith("video_growth_agent."):
                    if path.name != "adapters.py":
                        import_failures.append(f"{path.relative_to(root)} imports legacy domain code outside the explicit adapter bridge: {module}")
    _check(checks, "runtime_dependency_boundary", not import_failures, import_failures)

    adapter_source = (root / "video_studio" / "adapters.py").read_text(encoding="utf-8")
    implemented_adapters = set(re.findall(r"""(?:if|elif) name == ["']([^"']+)["']""", adapter_source))
    declared_adapters = set(studio_manifest.get("capabilities", {}).get("domain_adapters", {}))
    from .adapters import SUPPORTED_DOMAIN_ADAPTERS, supports_domain_adapter
    supported_adapters = set(SUPPORTED_DOMAIN_ADAPTERS)
    adapter_registry_ok = declared_adapters == implemented_adapters == supported_adapters
    _check(checks, "domain_adapter_registry_matches_manifest", adapter_registry_ok, {
        "declared_count": len(declared_adapters),
        "implemented_count": len(implemented_adapters),
        "supported_count": len(supported_adapters),
        "undeclared_supported": sorted(supported_adapters - declared_adapters),
        "declared_without_implementation": sorted(declared_adapters - implemented_adapters),
        "implemented_without_support_registration": sorted(implemented_adapters - supported_adapters),
    })

    from .production.executors import tool_executor_for_task

    tool_binding_failures = []
    for task in program_tasks:
        if task.get("executor") != "tool":
            continue
        requirements = task.get("requirements", {})
        adapter = requirements.get("domain_adapter") if isinstance(requirements, dict) else None
        if isinstance(adapter, dict):
            name = str(adapter.get("name") or "").strip()
            if not name or name not in declared_adapters or not supports_domain_adapter(name):
                tool_binding_failures.append(f"{task.get('task_id')}: domain adapter is not declared and executable: {name!r}")
        elif not tool_executor_for_task(task):
            tool_binding_failures.append(f"{task.get('task_id')}: no registered production/domain executor")
    _check(checks, "program_tool_tasks_have_registered_executors", not tool_binding_failures, tool_binding_failures)

    all_example_tool_failures = []
    all_example_tool_count = 0
    for task_path in sorted((root / "examples").glob("*.tasks.json")):
        for task in _read_json(task_path):
            if task.get("executor") != "tool":
                continue
            all_example_tool_count += 1
            executor_ref = tool_executor_for_task(task)
            if not executor_ref:
                all_example_tool_failures.append(
                    f"{task_path.name}:{task.get('task_id')}: no registered executor"
                )
                continue
            requirements = task.get("requirements", {})
            adapter = requirements.get("domain_adapter") if isinstance(requirements, dict) else None
            if isinstance(adapter, dict):
                name = str(adapter.get("name") or "").strip()
                if name not in declared_adapters or not supports_domain_adapter(name):
                    all_example_tool_failures.append(
                        f"{task_path.name}:{task.get('task_id')}: undeclared domain adapter {name!r}"
                    )
    _check(checks, "all_example_tool_tasks_have_registered_executors", not all_example_tool_failures, {
        "example_task_graph_count": len(list((root / "examples").glob("*.tasks.json"))),
        "tool_task_count": all_example_tool_count,
        "failures": all_example_tool_failures,
    })

    task_ids = {str(task.get("task_id")) for task in program_tasks}
    output_producers = {
        output: str(task.get("task_id"))
        for task in program_tasks
        for output in task.get("outputs", [])
    }
    flywheel_failures = []
    for loop_name, loop in business_flywheel.get("execution_bindings", {}).items():
        loop_task_ids = set(loop.get("task_ids", []))
        for task_id in sorted(loop_task_ids - task_ids):
            flywheel_failures.append(f"{loop_name}: unknown task {task_id}")
        for artifact_name in loop.get("handoff_artifacts", []):
            producer = output_producers.get(artifact_name)
            if producer is None:
                flywheel_failures.append(f"{loop_name}: handoff artifact has no producer: {artifact_name}")
            elif producer not in loop_task_ids:
                flywheel_failures.append(f"{loop_name}: producer {producer} for {artifact_name} is not in the loop task set")
    _check(checks, "cross_workstream_flywheel_handoffs_resolve", not flywheel_failures, flywheel_failures)

    program_handoff_validator = next(
        (task for task in program_tasks if task.get("task_id") == "validate-episode-production-handoff"), {}
    )
    episode_handoff_validator = next(
        (task for task in episode_tasks if task.get("task_id") == "validate-program-handoff"), {}
    )
    program_handoff_outputs = set(program_handoff_validator.get("outputs", []))
    episode_handoff_inputs = set(episode_handoff_validator.get("inputs", []))
    source_artifact_inputs = set(
        program_handoff_validator.get("requirements", {}).get("domain_adapter", {}).get("source_artifact_inputs", [])
    )
    expected_source_artifact_inputs = {
        "portfolio-allocation-decision", "pilot-topic-slate-decision",
        "production-strategy", "commercial-production-constraints", "growth-baseline",
    }
    cross_project_handoff_failures = []
    if program_handoff_outputs != {"validated-episode-intent"}:
        cross_project_handoff_failures.append(f"Program validator must emit validated-episode-intent: {sorted(program_handoff_outputs)}")
    if episode_handoff_inputs != program_handoff_outputs:
        cross_project_handoff_failures.append(
            f"Episode input names must exactly match Program output names: {sorted(episode_handoff_inputs)} != {sorted(program_handoff_outputs)}"
        )
    if source_artifact_inputs != expected_source_artifact_inputs:
        cross_project_handoff_failures.append(f"Program source artifact binding set is incomplete: {sorted(source_artifact_inputs)}")
    episode_adapter = episode_handoff_validator.get("requirements", {}).get("domain_adapter", {})
    if episode_adapter.get("require_validated_transfer") is not True:
        cross_project_handoff_failures.append("Episode validator must require immutable validated cross-project transfer metadata")
    if episode_adapter.get("handoff_input") != "validated-episode-intent":
        cross_project_handoff_failures.append("Episode validator input binding does not match the canonical Program handoff")
    _check(checks, "cross_project_program_episode_handoff_contract", not cross_project_handoff_failures, {
        "program_outputs": sorted(program_handoff_outputs),
        "episode_inputs": sorted(episode_handoff_inputs),
        "source_artifact_inputs": sorted(source_artifact_inputs),
        "failures": cross_project_handoff_failures,
    })

    from .production.registry import PRODUCTION_EXECUTORS

    local_operations = set(PRODUCTION_EXECUTORS.operations())
    expected_operations = {"python_frame_render", "ffmpeg_assemble", "delivery_package", "ffprobe_media_qa"}
    _check(checks, "local_production_executor_registry", local_operations == expected_operations, {
        "registered": sorted(local_operations),
        "expected": sorted(expected_operations),
    })

    names_by_path = _authority_paths(root, context_path, context_manifest)
    authority_failures: list[str] = []
    for key, reference in program_brief.get("program_context", {}).items():
        if key.endswith("_ref") and isinstance(reference, str) and reference.startswith(("projects/", "docs/")):
            if str((root / reference).resolve()) not in names_by_path:
                authority_failures.append(f"brief.program_context.{key} is not imported: {reference}")
    for task in program_tasks:
        requirements = task.get("requirements", {})
        refs = list(requirements.get("authority_refs", []))
        if requirements.get("authority_ref"):
            refs.append(requirements["authority_ref"])
        for reference in refs:
            resolved = str((root / reference).resolve())
            asset_name = names_by_path.get(resolved)
            if asset_name is None:
                authority_failures.append(f"{task.get('task_id')} authority ref is absent from context manifest: {reference}")
            elif asset_name not in task.get("inputs", []):
                authority_failures.append(f"{task.get('task_id')} does not bind {reference} as input {asset_name}")
    _check(checks, "program_authority_refs_are_digest_bound_inputs", not authority_failures, authority_failures)

    graph_failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="vga-standalone-audit-") as temp_root:
        for project_id, brief_name, tasks_name in (
            ("explainer", "technology-explainer.brief.json", "technology-explainer.tasks.json"),
            ("satire", "news-fictional-media.brief.json", "news-fictional-media.tasks.json"),
            ("adapter-demo", "standalone-domain-adapters.brief.json", "standalone-domain-adapters.tasks.json"),
            ("program-linked-episode", "program-linked-episode.brief.json", "program-linked-episode.tasks.json"),
        ):
            try:
                engine = StudioEngine(Path(temp_root) / project_id)
                brief = _read_json(root / "examples" / brief_name)
                tasks = _read_json(root / "examples" / tasks_name)
                engine.create_project(project_id, project_id, brief)
                engine.add_tasks(project_id, tasks)
                audit = engine.audit(project_id)
                if audit.get("pass") is not True:
                    graph_failures.append(f"{project_id}: {audit}")
                if project_id == "program-linked-episode":
                    task_map = {item["task_id"]: item for item in engine.list_tasks(project_id)}
                    if task_map.get("validate-program-handoff", {}).get("status") != "WAITING_INPUT":
                        graph_failures.append("program-linked-episode must fail closed until the validated Program handoff artifact is imported")
            except Exception as exc:
                graph_failures.append(f"{project_id}: {type(exc).__name__}: {exc}")
        try:
            engine = StudioEngine(Path(temp_root) / "program")
            engine.create_project("program", "Integrated media program", program_brief)
            for asset in context_manifest.get("assets", []):
                source = (context_path.parent / asset["path"]).resolve(strict=True)
                engine.import_asset(
                    "program", asset["name"], source,
                    kind=asset["kind"], media_type=asset["media_type"],
                    rights_status=asset["rights_status"], metadata=asset.get("metadata", {}),
                )
            engine.add_tasks("program", program_tasks)
            program_audit = engine.audit("program")
            task_map = {item["task_id"]: item for item in engine.list_tasks("program")}
            expected_ready = {
                "growth-baseline-and-topic-hypotheses",
                "commercial-advertiser-map",
                "production-economics-baseline",
                "provider-capability-benchmark",
                "media-graph-bootstrap",
                "jensen-case-fact-audit",
            }
            for task_id in sorted(expected_ready):
                if task_map.get(task_id, {}).get("status") != "READY":
                    graph_failures.append(f"program task should be READY: {task_id} -> {task_map.get(task_id, {}).get('status')}")
            for task_id in ("jensen-source-media-inspection", "jensen-rights-identity-audit"):
                if task_map.get(task_id, {}).get("status") != "WAITING_INPUT":
                    graph_failures.append(f"owner-media task should WAIT_INPUT: {task_id} -> {task_map.get(task_id, {}).get('status')}")
            if task_map.get("ipos-video-identity-bundle-import", {}).get("status") != "PENDING":
                graph_failures.append("IPOS import must remain dependency-pending until MediaGraph bootstrap is completed")
            if program_audit.get("pass") is not True:
                graph_failures.append(f"program graph audit failed: {program_audit}")
            from .production.worker_pool import run_ready_tool_tasks
            tool_smoke = run_ready_tool_tasks(engine, "program", worker_prefix="system-audit", max_workers=2, max_rounds=10)
            completed_tool_ids = {item["task_id"] for item in tool_smoke.get("completed", [])}
            if "media-graph-bootstrap" not in completed_tool_ids:
                graph_failures.append(f"Program local tool smoke did not execute media-graph-bootstrap: {tool_smoke}")
            if tool_smoke.get("failed") or tool_smoke.get("ready_tool_tasks_without_registered_executor"):
                graph_failures.append(f"Program local tool smoke found execution failures or unregistered tools: {tool_smoke}")
            post_smoke_tasks = {item["task_id"]: item for item in engine.list_tasks("program")}
            if post_smoke_tasks.get("media-graph-bootstrap", {}).get("status") != "COMPLETED":
                graph_failures.append("media-graph-bootstrap must complete through the registered local tool executor")
            if post_smoke_tasks.get("ipos-video-identity-bundle-import", {}).get("status") != "WAITING_INPUT":
                graph_failures.append("IPOS import must wait for the missing owner-approved bundle after MediaGraph bootstrap")
            if engine.audit("program").get("pass") is not True:
                graph_failures.append("Program graph audit failed after the real local tool execution smoke")
        except Exception as exc:
            graph_failures.append(f"program: {type(exc).__name__}: {exc}")
    _check(checks, "example_graphs_and_default_program_execution", not graph_failures, graph_failures)

    explainer_brief = _read_json(root / "examples" / "technology-explainer.brief.json")
    satire_brief = _read_json(root / "examples" / "news-fictional-media.brief.json")
    hard_gate_failures = []
    for name, brief in (("technology-explainer", explainer_brief), ("news-fictional-media", satire_brief)):
        policy = brief.get("release_policy", {})
        if policy.get("require_rights") is not True or policy.get("require_rights_evidence") is not True:
            hard_gate_failures.append(f"{name}: rights and evidence must be required")
        if policy.get("no_auto_publish") is not True:
            hard_gate_failures.append(f"{name}: no_auto_publish must be true")
    red_team = explainer_brief.get("release_policy", {}).get("review_contracts", {}).get("red-team", {})
    if int(red_team.get("min_findings", 0)) < 3:
        hard_gate_failures.append("technology-explainer: Red Team must require at least three findings")
    _check(checks, "hard_release_gates", not hard_gate_failures, hard_gate_failures)

    provider_state = (
        studio_manifest.get("capabilities", {})
        .get("domain_adapter_execution", {})
        .get("external_provider_generation", "UNSPECIFIED")
    )
    if str(provider_state).startswith("NOT_CONNECTED"):
        capability_gaps.append(
            "No repository-registered generative-video executor. Agent tasks may use a currently available session tool only after operation, availability, rights and cost checks; paid generation requires explicit owner approval."
        )
    owner_inputs_required.extend(["jensen-source-video", "ipos-ready-for-video-bundle"])
    owner_inputs_required = sorted(set(owner_inputs_required))

    failed_checks = [item for item in checks if not item["pass"]]
    return {
        "schema_version": "1.0",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(root),
        "pass": not failed_checks,
        "structural_status": "PASS" if not failed_checks else "FAIL",
        "production_readiness": "PARTIAL" if capability_gaps or owner_inputs_required else "READY",
        "checks": checks,
        "capability_gaps": capability_gaps,
        "owner_inputs_required": owner_inputs_required,
        "boundary": {
            "caos_runtime_dependency": False,
            "paid_provider_calls_made": False,
            "automatic_publication": False,
            "temporary_workspace_only": True,
        },
    }
