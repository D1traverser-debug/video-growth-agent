from __future__ import annotations

import json
from pathlib import Path
import tomllib

from video_studio.engine import StudioEngine

ROOT = Path(__file__).resolve().parents[1]


def test_standalone_studio_is_the_new_entry_and_has_no_parent_runtime_dependency():
    manifest = json.loads((ROOT / "video_studio/data/studio_manifest.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    skill = (ROOT / "skills/video-growth-agent/SKILL.md").read_text(encoding="utf-8")
    entry = (ROOT / "STUDIO_ENTRY.md").read_text(encoding="utf-8")
    source = (ROOT / "video_studio/engine.py").read_text(encoding="utf-8")

    assert manifest["governance"]["system"] == "VIDEO_STUDIO_NATIVE"
    assert manifest["governance"]["mode"] == "STANDALONE"
    assert manifest["governance"]["caos_runtime_dependency"] is False
    assert manifest["governance"]["caos_api_dependency"] is False
    assert manifest["governance"]["caos_skill_dependency"] is False
    assert manifest["execution"]["fixed_stage_machine"] is False
    assert set(manifest["business_workstreams"]) == {"MEDIA_GROWTH", "ORIGINAL_DIGITAL_IP", "COMMERCIALIZATION", "PRODUCTION_SYSTEM"}
    assert manifest["domain_adapter_policy"]["legacy_fixed_stage_orchestrator"] == "NOT_A_CONTROLLER"
    assert pyproject["project"]["scripts"]["vga-studio"] == "video_studio.cli:main"
    assert "STUDIO_ENTRY.md" in skill and "STUDIO_ENTRY.md" in entry
    assert "CAOS_VIDEO_ENTRY.md" not in skill
    assert "import caos" not in source.lower()
    assert "from caos" not in source.lower()


def test_example_graphs_are_valid_dynamic_dags(tmp_path):
    engine = StudioEngine(tmp_path)
    for project_id, brief_name, tasks_name in (
        ("explainer", "technology-explainer.brief.json", "technology-explainer.tasks.json"),
        ("satire", "news-fictional-media.brief.json", "news-fictional-media.tasks.json"),
        ("media-program", "ai-self-media-commercialization.brief.json", "ai-self-media-commercialization.tasks.json"),
        ("adapter-demo", "standalone-domain-adapters.brief.json", "standalone-domain-adapters.tasks.json"),
        ("program-linked-episode", "program-linked-episode.brief.json", "program-linked-episode.tasks.json"),
    ):
        brief = json.loads((ROOT / "examples" / brief_name).read_text(encoding="utf-8"))
        tasks = json.loads((ROOT / "examples" / tasks_name).read_text(encoding="utf-8"))
        engine.create_project(project_id, project_id, brief)
        engine.add_tasks(project_id, tasks)
        assert engine.audit(project_id)["pass"] is True
        status = engine.status(project_id)
        if project_id == "program-linked-episode":
            task_map = {item["task_id"]: item for item in engine.list_tasks(project_id)}
            assert task_map["validate-program-handoff"]["status"] == "WAITING_INPUT"
            assert status["task_counts"].get("READY", 0) == 0
        else:
            assert status["task_counts"]["READY"] >= 1


def test_engine_uses_no_external_runtime_dependency():
    source = (ROOT / "video_studio/engine.py").read_text(encoding="utf-8")
    assert "requests" not in source
    assert "httpx" not in source
    assert "openai" not in source.lower()
    assert "sqlite3" in source
    assert "video_growth_agent" not in source

def test_legacy_engine_import_is_only_a_compatibility_shim():
    from video_growth_agent.studio_engine import StudioEngine as LegacyImport
    from video_studio.engine import StudioEngine as CanonicalEngine

    assert LegacyImport is CanonicalEngine


def test_standalone_control_plane_is_independent_and_domain_bridge_is_explicit():
    for module in ("__init__.py", "__main__.py", "cli.py", "engine.py", "media.py"):
        source = (ROOT / "video_studio" / module).read_text(encoding="utf-8")
        assert "video_growth_agent" not in source
        assert "from caos" not in source.lower()
        assert "import caos" not in source.lower()

    adapters = (ROOT / "video_studio" / "adapters.py").read_text(encoding="utf-8")
    assert "from video_growth_agent." in adapters
    assert "from caos" not in adapters.lower()
    assert "import caos" not in adapters.lower()
    assert "run_claimed_domain_adapter" in adapters


def test_standalone_manifest_registers_explicit_domain_adapters_and_font_rights_metadata():
    manifest = json.loads((ROOT / "video_studio" / "data" / "studio_manifest.json").read_text(encoding="utf-8"))
    adapters = manifest["capabilities"]["domain_adapters"]
    assert {
        "editorial_plan_validate", "shot_contract_materialize", "ipos_bundle_import",
        "ipos_shot_bind", "ipos_continuity_snapshot", "ipos_continuity_link",
        "media_graph_initialize", "timeline_validate", "continuity_assess",
        "shot_route", "business_outcome_metrics", "extended_media_qa",
        "programmatic_graphic_render", "business_object_validate", "episode_intent_validate",
    }.issubset(adapters)
    font_metadata = json.loads((ROOT / "examples" / "adapter-demo-font.metadata.json").read_text(encoding="utf-8"))
    assert font_metadata["rights_evidence_refs"] == ["rights-clearance"]


def test_program_task_graph_and_cross_workstream_handoffs_share_one_current_authority():
    manifest = json.loads((ROOT / "projects/ai-self-media-commercialization/PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "examples/ai-self-media-commercialization.tasks.json").read_text(encoding="utf-8"))
    flywheel = json.loads((ROOT / "projects/ai-self-media-commercialization/BUSINESS_FLYWHEEL.json").read_text(encoding="utf-8"))
    assert manifest["subtask_graph_ref"] == "../../examples/ai-self-media-commercialization.tasks.json"
    assert len(tasks) == 50
    task_ids = {item["task_id"] for item in tasks}
    producers = {output: item["task_id"] for item in tasks for output in item["outputs"]}
    for loop_name, loop in flywheel["execution_bindings"].items():
        assert set(loop["task_ids"]).issubset(task_ids), loop_name
        for artifact in loop["handoff_artifacts"]:
            assert artifact in producers, (loop_name, artifact)
            assert producers[artifact] in loop["task_ids"], (loop_name, artifact, producers[artifact])
    assert "episode-outcome-analysis" in flywheel["execution_bindings"]["AUDIENCE_TO_PORTFOLIO"]["task_ids"]
    assert "validated-episode-intent" in flywheel["execution_bindings"]["COMMERCIAL_TO_PRODUCTION"]["handoff_artifacts"]
    program_validator = next(item for item in tasks if item["task_id"] == "validate-episode-production-handoff")
    episode_tasks = json.loads((ROOT / "examples/program-linked-episode.tasks.json").read_text(encoding="utf-8"))
    episode_validator = next(item for item in episode_tasks if item["task_id"] == "validate-program-handoff")
    program_output = program_validator["outputs"][0]
    assert program_output == "validated-episode-intent"
    assert episode_validator["inputs"] == [program_output]
    assert episode_validator["requirements"]["domain_adapter"]["require_validated_transfer"] is True
    assert set(program_validator["requirements"]["domain_adapter"]["source_artifact_inputs"]) == {
        "portfolio-allocation-decision", "pilot-topic-slate-decision", "production-strategy",
        "commercial-production-constraints", "growth-baseline",
    }
    assert flywheel["execution_bindings"]["IP_TO_PRODUCTION"]["mode"].endswith("SHOT_BINDING_REMAINS_EPISODE_SCOPED")


def test_example_briefs_preserve_nonnegotiable_video_release_gates():
    root = ROOT / "examples"
    explainer = json.loads((root / "technology-explainer.brief.json").read_text(encoding="utf-8"))
    satire = json.loads((root / "news-fictional-media.brief.json").read_text(encoding="utf-8"))
    program = json.loads((root / "ai-self-media-commercialization.brief.json").read_text(encoding="utf-8"))

    policy = explainer["release_policy"]
    assert policy["require_rights"] is True
    assert policy["require_rights_evidence"] is True
    assert policy["require_technical_qa"] is True
    assert "red-team" in policy["required_review_rubrics"]
    assert policy["review_contracts"]["red-team"]["min_findings"] >= 3
    assert policy["review_contracts"]["human-cold-read"]["execution_mode"] == "INDEPENDENT_COLD_READ"
    assert satire["release_policy"]["required_asset_names"] == ["source-video"]
    assert satire["release_policy"]["no_auto_publish"] is True
    assert program["program_context"]["ip_identity_authority"] == "IPOS"
    assert program["program_context"]["caos_runtime_dependency"] is False


def test_program_example_keeps_independent_workstreams_parallel_and_ipos_fail_closed(tmp_path):
    engine = StudioEngine(tmp_path)
    brief_path = ROOT / "examples" / "ai-self-media-commercialization.brief.json"
    tasks_path = ROOT / "examples" / "ai-self-media-commercialization.tasks.json"
    project_brief = json.loads(brief_path.read_text(encoding="utf-8"))
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    engine.create_project("program", "Integrated media program", project_brief)
    context_manifest_path = ROOT / "examples" / "ai-self-media-commercialization.context.json"
    context_manifest = json.loads(context_manifest_path.read_text(encoding="utf-8"))
    for asset in context_manifest["assets"]:
        source_path = (context_manifest_path.parent / asset["path"]).resolve(strict=True)
        engine.import_asset(
            "program", asset["name"], source_path,
            kind=asset["kind"], media_type=asset["media_type"],
            rights_status=asset["rights_status"], metadata=asset.get("metadata", {}),
        )
    engine.add_tasks("program", tasks)
    status = engine.status("program")
    task_map = {item["task_id"]: item for item in engine.list_tasks("program")}
    assert task_map["growth-baseline-and-topic-hypotheses"]["status"] == "READY"
    assert task_map["commercial-advertiser-map"]["status"] == "READY"
    assert task_map["media-graph-bootstrap"]["status"] == "READY"
    assert task_map["ipos-video-identity-bundle-import"]["status"] == "PENDING"
    assert task_map["jensen-source-media-inspection"]["status"] == "WAITING_INPUT"
    assert task_map["commercial-offer-native-integration"]["status"] == "PENDING"
    assert status["task_counts"]["READY"] >= 4
    assert engine.audit("program")["pass"] is True


def test_standalone_system_audit_passes_structure_and_reports_unfinished_media_capabilities():
    from video_studio.system_audit import run_system_audit

    report = run_system_audit(ROOT)
    assert report["pass"] is True, report
    assert report["structural_status"] == "PASS"
    assert report["production_readiness"] == "PARTIAL"
    assert report["boundary"]["caos_runtime_dependency"] is False
    assert report["boundary"]["paid_provider_calls_made"] is False
    assert report["boundary"]["automatic_publication"] is False
    assert report["owner_inputs_required"] == ["ipos-ready-for-video-bundle", "jensen-source-video"]
    assert any("No repository-registered generative-video executor" in item for item in report["capability_gaps"])
    assert all(item["pass"] for item in report["checks"])


def test_standalone_adapter_demo_wires_editorial_to_real_local_render_and_qa(tmp_path):
    engine = StudioEngine(tmp_path)
    brief_path = ROOT / "examples" / "standalone-domain-adapters.brief.json"
    tasks_path = ROOT / "examples" / "standalone-domain-adapters.tasks.json"
    project_brief = json.loads(brief_path.read_text(encoding="utf-8"))
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    engine.create_project("adapter-demo", "Standalone adapter demo", project_brief)
    engine.add_tasks("adapter-demo", tasks)
    task_map = {item["task_id"]: item for item in engine.list_tasks("adapter-demo")}
    assert task_map["author-editorial-plan"]["status"] == "READY"
    assert task_map["validate-editorial-plan"]["status"] == "PENDING"
    assert task_map["render-programmatic-graphic"]["executor"] == "tool"
    assert task_map["render-programmatic-graphic"]["requirements"]["domain_adapter"]["name"] == "programmatic_graphic_render"
    assert task_map["technical-qa"]["kind"] == "technical_measurement"
    assert engine.audit("adapter-demo")["pass"] is True



def test_integrated_program_authority_refs_are_digest_bound_task_inputs():
    manifest_path = ROOT / "examples" / "ai-self-media-commercialization.context.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "examples" / "ai-self-media-commercialization.tasks.json").read_text(encoding="utf-8"))
    brief = json.loads((ROOT / "examples" / "ai-self-media-commercialization.brief.json").read_text(encoding="utf-8"))

    names_by_repo_path = {
        str((manifest_path.parent / item["path"]).resolve()): item["name"]
        for item in manifest["assets"]
    }
    for key, reference in brief["program_context"].items():
        if key.endswith("_ref") and isinstance(reference, str) and reference.startswith(("projects/", "docs/")):
            resolved = str((ROOT / reference).resolve())
            assert resolved in names_by_repo_path, f"program context ref is not imported: {reference}"

    for task_item in tasks:
        requirements = task_item.get("requirements", {})
        refs = list(requirements.get("authority_refs", []))
        if requirements.get("authority_ref"):
            refs.append(requirements["authority_ref"])
        for reference in refs:
            resolved = str((ROOT / reference).resolve())
            assert resolved in names_by_repo_path, f"task authority ref is not imported: {task_item['task_id']} -> {reference}"
            assert names_by_repo_path[resolved] in task_item.get("inputs", []), (
                f"task {task_item['task_id']} does not bind authority ref as an input: {reference}"
            )

    imported_names = {item["name"] for item in manifest["assets"]}
    assert "jensen-source-video" not in imported_names
    assert "ipos-ready-for-video-bundle" not in imported_names
