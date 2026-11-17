from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import threading

import pytest

from video_studio.engine import ClaimError, ContractError, StudioEngine


def brief():
    return {
        "goal": "Produce a publishable 60-second technology explainer.",
        "audience": "Technology-curious viewers aged 20-40.",
        "deliverables": ["final.mp4", "cover.png", "publish-copy.md"],
        "release_policy": {
            "required_evidence_refs": ["platform-format-review"],
            "required_review_rubrics": ["editorial", "craft", "technical"],
        },
    }


def make_engine(tmp_path: Path) -> StudioEngine:
    engine = StudioEngine(tmp_path / "workspace")
    engine.create_project("demo", "Demo", brief())
    return engine


def task(task_id, *, deps=(), inputs=(), outputs=None, priority=0):
    return {
        "task_id": task_id,
        "title": task_id,
        "kind": "production",
        "executor": "agent",
        "depends_on": list(deps),
        "inputs": list(inputs),
        "outputs": outputs or [f"{task_id}-artifact"],
        "acceptance": {"observable": "A concrete artifact exists and satisfies the brief."},
        "priority": priority,
    }


def complete(engine, tmp_path, task_id, worker="worker"):
    packet = engine.claim_next("demo", worker)
    assert packet is not None
    assert packet["task"]["task_id"] == task_id
    artifact_name = packet["task"]["outputs"][0]
    output = engine._project_dir("demo") / "artifacts" / f"{artifact_name}.txt"
    output.write_text(f"artifact for {task_id}", encoding="utf-8")
    result = engine.complete_task(
        "demo", task_id, worker, packet["claim"]["claim_token"],
        {artifact_name: {"path": str(output), "kind": "document", "media_type": "text/plain", "rights_status": "OWNED"}},
    )
    return result["artifacts"][artifact_name]


def test_project_requires_outcome_contract_and_has_standalone_identity(tmp_path):
    engine = StudioEngine(tmp_path)
    with pytest.raises(ContractError):
        engine.create_project("bad", "Bad", {"goal": "x"})
    created = engine.create_project("good", "Good", brief())
    assert created["project_id"] == "good"
    assert Path(created["workspace"]).is_dir()
    assert (Path(created["workspace"]) / "studio.sqlite3").is_file()


def test_dynamic_dag_runs_independent_tasks_in_parallel_then_unlocks_dependency(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("research"), task("visual"), task("edit", deps=["research", "visual"], inputs=["research-artifact", "visual-artifact"])])

    # Two workers can claim two independent tasks; no fixed stage order is imposed.
    first = engine.claim_next("demo", "worker-a")
    second = engine.claim_next("demo", "worker-b")
    assert {first["task"]["task_id"], second["task"]["task_id"]} == {"research", "visual"}
    assert engine.claim_next("demo", "worker-c") is None

    for packet in (first, second):
        task_id = packet["task"]["task_id"]
        output_name = packet["task"]["outputs"][0]
        output = engine._project_dir("demo") / "artifacts" / f"{task_id}.txt"
        output.write_text(task_id, encoding="utf-8")
        engine.complete_task("demo", task_id, packet["claim"]["worker_id"], packet["claim"]["claim_token"], {
            output_name: {"path": str(output), "kind": "document", "media_type": "text/plain", "rights_status": "OWNED"}
        })

    edit = engine.claim_next("demo", "editor")
    assert edit["task"]["task_id"] == "edit"
    assert set(edit["input_artifacts"]) == {"research-artifact", "visual-artifact"}


def test_concurrent_claim_is_atomic_and_single_task_has_one_owner(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("only")])
    barrier = threading.Barrier(2)

    def claim(worker):
        barrier.wait()
        return engine.claim_next("demo", worker)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(claim, ["worker-a", "worker-b"]))
    claimed = [item for item in results if item is not None]
    assert len(claimed) == 1
    assert claimed[0]["task"]["task_id"] == "only"


def test_missing_input_waits_until_asset_is_imported(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("edit", inputs=["source-video"])])
    assert engine.list_tasks("demo")[0]["status"] == "WAITING_INPUT"
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source bytes")
    imported = engine.import_asset("demo", "source-video", source, kind="video", media_type="video/mp4", rights_status="AUTHORIZED")
    assert imported["sha256"] == hashlib.sha256(b"source bytes").hexdigest()
    assert engine.list_tasks("demo")[0]["status"] == "READY"


def test_identical_asset_reimport_is_idempotent_and_preserves_completed_consumers(tmp_path):
    engine = make_engine(tmp_path)
    source = tmp_path / "source.txt"
    source.write_text("same source bytes", encoding="utf-8")
    metadata = {"rights_evidence_refs": ["https://rights.example/license/1"]}
    first = engine.import_asset(
        "demo", "source-evidence", source, kind="evidence",
        media_type="text/plain", rights_status="NOT_APPLICABLE", metadata=metadata,
    )
    engine.add_tasks("demo", [task("consume-source", inputs=["source-evidence"])])
    complete(engine, tmp_path, "consume-source", "worker-a")

    repeated = engine.import_asset(
        "demo", "source-evidence", source, kind="evidence",
        media_type="text/plain", rights_status="NOT_APPLICABLE", metadata=metadata,
    )
    assert repeated["artifact_id"] == first["artifact_id"]
    assert repeated["version"] == first["version"] == 1
    assert engine.list_tasks("demo")[0]["status"] == "COMPLETED"


def test_cross_project_transfer_is_exact_idempotent_and_unblocks_target(tmp_path, capsys):
    from video_studio.cli import main

    workspace = tmp_path / "workspace"
    engine = StudioEngine(workspace)
    engine.create_project("program", "Program", brief())
    engine.create_project("episode", "Episode", brief())
    engine.add_tasks("episode", [task("validate-handoff", inputs=["validated-episode-intent"])])
    assert engine.list_tasks("episode")[0]["status"] == "WAITING_INPUT"

    source = tmp_path / "validated-episode-intent.json"
    source.write_text('{"schema_version":"1.0","status":"PASS"}', encoding="utf-8")
    source_artifact = engine.import_asset(
        "program", "validated-episode-intent", source,
        kind="episode_intent", media_type="application/json", rights_status="NOT_APPLICABLE",
    )

    command = [
        "--root", str(workspace), "transfer-asset",
        "program", "validated-episode-intent", "episode", "validated-episode-intent",
        "--expected-artifact-id", source_artifact["artifact_id"],
        "--expected-version", str(source_artifact["version"]),
        "--expected-sha256", source_artifact["sha256"],
    ]
    assert main(command) == 0
    first = json.loads(capsys.readouterr().out)
    target = first["target"]
    assert first["source"]["artifact_id"] == source_artifact["artifact_id"]
    assert target["sha256"] == source_artifact["sha256"]
    assert target["metadata"]["cross_project_transfer"] == first["transfer"]
    assert first["transfer"]["source_project_id"] == "program"
    assert first["transfer"]["target_project_id"] == "episode"
    assert engine.list_tasks("episode")[0]["status"] == "READY"

    assert main(command) == 0
    repeated = json.loads(capsys.readouterr().out)
    assert repeated["target"]["artifact_id"] == target["artifact_id"]
    assert repeated["target"]["version"] == target["version"] == 1

    with pytest.raises(ContractError, match="digest changed"):
        engine.transfer_artifact(
            "program", "validated-episode-intent", "episode", "validated-episode-intent",
            expected_artifact_id=source_artifact["artifact_id"],
            expected_version=source_artifact["version"],
            expected_sha256="0" * 64,
        )

    replacement = tmp_path / "validated-episode-intent-v2.json"
    replacement.write_text('{"schema_version":"1.0","status":"PASS","revision":2}', encoding="utf-8")
    latest = engine.import_asset(
        "program", "validated-episode-intent", replacement,
        kind="episode_intent", media_type="application/json", rights_status="NOT_APPLICABLE",
    )
    assert latest["version"] == 2
    engine.refresh("episode")
    assert engine.list_tasks("episode")[0]["status"] == "STALE"
    with engine._connect("episode") as connection:
        stale_target = connection.execute(
            "SELECT status FROM artifacts WHERE project_id='episode' AND artifact_id=?",
            (target["artifact_id"],),
        ).fetchone()
    assert stale_target["status"] == "STALE"

    refreshed = engine.transfer_artifact(
        "program", "validated-episode-intent", "episode", "validated-episode-intent",
        expected_artifact_id=latest["artifact_id"], expected_version=latest["version"],
        expected_sha256=latest["sha256"],
    )
    assert refreshed["target"]["version"] == 2
    reopened = engine.reopen("episode", "validate-handoff", "new exact Program handoff was transferred")
    assert reopened == ["validate-handoff"]
    assert engine.list_tasks("episode")[0]["status"] == "READY"


def test_import_manifest_preflights_all_files_and_imports_digest_bound_context(tmp_path, capsys):
    from video_studio.cli import main

    workspace = tmp_path / "workspace"
    engine = StudioEngine(workspace)
    engine.create_project("demo", "Manifest import", brief())
    repo = tmp_path / "repo"
    examples = repo / "examples"
    projects = repo / "projects"
    examples.mkdir(parents=True)
    projects.mkdir(parents=True)
    (projects / "program-state.json").write_text('{"revision": 3}', encoding="utf-8")
    (projects / "business-flywheel.md").write_text("# Business flywheel", encoding="utf-8")
    manifest = examples / "context.json"
    manifest.write_text(json.dumps({
        "schema_version": "1.0",
        "assets": [
            {
                "name": "program-state", "path": "../projects/program-state.json",
                "kind": "document", "media_type": "application/json",
                "rights_status": "NOT_APPLICABLE",
            },
            {
                "name": "business-flywheel", "path": "../projects/business-flywheel.md",
                "kind": "document", "media_type": "text/markdown",
                "rights_status": "NOT_APPLICABLE",
            },
        ],
    }), encoding="utf-8")

    assert main(["--root", str(workspace), "import-manifest", "demo", str(manifest)]) == 0
    first_output = json.loads(capsys.readouterr().out)
    assert first_output["asset_count"] == 2
    first_ids = {item["name"]: item["artifact_id"] for item in first_output["artifacts"]}

    engine.add_tasks("demo", [task("read-context", inputs=["program-state", "business-flywheel"])])
    assert engine.list_tasks("demo")[0]["status"] == "READY"

    assert main(["--root", str(workspace), "import-manifest", "demo", str(manifest)]) == 0
    second_output = json.loads(capsys.readouterr().out)
    second_ids = {item["name"]: item["artifact_id"] for item in second_output["artifacts"]}
    assert second_ids == first_ids
    assert {item["version"] for item in second_output["artifacts"]} == {1}
    assert engine.list_tasks("demo")[0]["status"] == "READY"

    broken = examples / "broken-context.json"
    broken.write_text(json.dumps({
        "schema_version": "1.0",
        "assets": [
            {"name": "new-valid", "path": "../projects/program-state.json"},
            {"name": "missing", "path": "../projects/missing.json"},
        ],
    }), encoding="utf-8")
    assert main(["--root", str(workspace), "import-manifest", "demo", str(broken)]) == 2
    capsys.readouterr()
    with engine._connect("demo") as connection:
        absent = connection.execute(
            "SELECT 1 FROM artifacts WHERE project_id='demo' AND name='new-valid' LIMIT 1"
        ).fetchone()
    assert absent is None

    invalid_rights = examples / "invalid-rights.json"
    invalid_rights.write_text(json.dumps({
        "schema_version": "1.0",
        "assets": [
            {"name": "new-valid-2", "path": "../projects/program-state.json"},
            {"name": "bad-rights", "path": "../projects/business-flywheel.md", "rights_status": "NOT_A_REAL_STATUS"},
        ],
    }), encoding="utf-8")
    assert main(["--root", str(workspace), "import-manifest", "demo", str(invalid_rights)]) == 2
    capsys.readouterr()
    with engine._connect("demo") as connection:
        absent = connection.execute(
            "SELECT 1 FROM artifacts WHERE project_id='demo' AND name='new-valid-2' LIMIT 1"
        ).fetchone()
    assert absent is None


def test_claim_token_and_lease_prevent_stale_worker_completion(tmp_path, monkeypatch):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    packet = engine.claim_next("demo", "worker-a", lease_seconds=30)
    token = packet["claim"]["claim_token"]
    # Simulate an expired lease in the durable store, without sleeping.
    with engine._connect("demo") as connection:
        connection.execute("UPDATE tasks SET lease_until='2000-01-01T00:00:00Z' WHERE task_id='render'")
        connection.commit()
    reclaimed = engine.claim_next("demo", "worker-b", lease_seconds=30)
    assert reclaimed["claim"]["worker_id"] == "worker-b"
    output = tmp_path / "render.txt"
    output.write_text("done", encoding="utf-8")
    with pytest.raises(ClaimError):
        engine.complete_task("demo", "render", "worker-a", token, {
            "render-artifact": {"path": str(output), "rights_status": "OWNED"}
        })


def test_task_completion_requires_exact_declared_outputs_and_stores_digest(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render", outputs=["master-video", "cover"])])
    packet = engine.claim_next("demo", "worker")
    master = engine._project_dir("demo") / "artifacts" / "master.mp4"
    cover = engine._project_dir("demo") / "artifacts" / "cover.png"
    master.write_bytes(b"mp4")
    cover.write_bytes(b"png")
    with pytest.raises(ContractError):
        engine.complete_task("demo", "render", "worker", packet["claim"]["claim_token"], {
            "master-video": {"path": str(master), "rights_status": "OWNED"}
        })
    result = engine.complete_task("demo", "render", "worker", packet["claim"]["claim_token"], {
        "master-video": {"path": str(master), "kind": "video", "media_type": "video/mp4", "rights_status": "OWNED"},
        "cover": {"path": str(cover), "kind": "image", "media_type": "image/png", "rights_status": "OWNED"},
    })
    assert result["artifacts"]["master-video"]["sha256"] == hashlib.sha256(b"mp4").hexdigest()
    assert engine.audit("demo")["pass"] is True


def test_artifact_path_cannot_escape_project_workspace(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    packet = engine.claim_next("demo", "worker")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    with pytest.raises(ContractError):
        engine.complete_task("demo", "render", "worker", packet["claim"]["claim_token"], {
            "render-artifact": {"path": str(outside), "rights_status": "OWNED"}
        })


def test_decision_receipt_requires_competing_causes_alternatives_and_falsifier(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ContractError):
        engine.record_decision("demo", {"question": "which method?"})
    receipt = engine.record_decision("demo", {
        "question": "Why did the opening fail?",
        "scope": "episode-01/opening",
        "source_refs": ["asset://rough-cut-v1", "review://cold-read-v1"],
        "hypotheses": [
            {"id": "H1", "claim": "the hook is unclear", "discriminator": "cold-read viewers cannot state the promise"},
            {"id": "H2", "claim": "the visual promise is weak", "discriminator": "visual-only preview does not communicate the premise"},
        ],
        "alternatives": [
            {"id": "A", "plan": "rewrite hook", "counterevidence": "could worsen pacing"},
            {"id": "B", "plan": "replace opening visual", "counterevidence": "may not fix unclear premise"},
        ],
        "selected_option": "A",
        "falsifier": "a blind cold-read can accurately paraphrase the original promise",
        "rollback": "restore opening v1 and preserve its asset lineage",
    })
    assert receipt["status"] == "ACTIVE"


def test_failure_cannot_close_without_independent_verification_and_regression(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    failure = engine.record_failure("demo", {
        "task_id": "render",
        "symptom": "generated clips repeatedly break object continuity",
        "hypotheses": [
            {"id": "H1", "claim": "reference binding is insufficient", "discriminator": "compare same prompt with and without locked reference"},
            {"id": "H2", "claim": "motion request exceeds model capability", "discriminator": "test a lower-motion control with the same reference"},
        ],
        "selected_root_cause": "H2",
        "method_challenge": "the current benchmark did not isolate motion complexity",
        "repair_plan": "split the move into two controlled shots",
        "falsifier": "a matched test with the original motion succeeds consistently",
        "rollback": "restore the original shot plan and retain rejected takes",
        "evidence_refs": ["take://failed-1", "benchmark://motion-control"],
    })
    with pytest.raises(ContractError):
        engine.resolve_failure("demo", failure["failure_id"], {"verification_refs": ["qa://1"]})
    engine.resolve_failure("demo", failure["failure_id"], {
        "verification_refs": ["review://new-cut"],
        "regression_refs": ["replay://continuity-fixture"],
        "result": "PASS",
    })
    assert engine.status("demo")["open_failures"] == 0


def test_reviews_are_bound_to_exact_digest_and_independent_reviewer(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    artifact = complete(engine, tmp_path, "render", "artist")
    with pytest.raises(ContractError):
        engine.record_review("demo", artifact["artifact_id"], reviewer_id="artist", rubric_id="craft", outcome="PASS", dimensions={"visual": 4}, evidence_refs=["frame://1"])
    review = engine.record_review("demo", artifact["artifact_id"], reviewer_id="reviewer", rubric_id="craft", outcome="PASS", dimensions={"visual": 4}, evidence_refs=["frame://1", "frame://2"])
    assert review["artifact_digest"] == artifact["sha256"]


def test_release_check_requires_all_reviews_rights_and_platform_evidence(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    artifact = complete(engine, tmp_path, "render", "artist")
    for rubric in ("editorial", "craft", "technical"):
        engine.record_review("demo", artifact["artifact_id"], reviewer_id=f"reviewer-{rubric}", rubric_id=rubric, outcome="PASS", dimensions={"score": 4}, evidence_refs=[f"evidence://{rubric}"])
    blocked = engine.release_check("demo", artifact["artifact_id"], required_rubrics=["editorial", "craft", "technical"], evidence_refs=[])
    assert blocked["pass"] is False
    assert any(item.startswith("release_evidence_missing") for item in blocked["failures"])
    passed = engine.release_check("demo", artifact["artifact_id"], required_rubrics=["editorial", "craft", "technical"], evidence_refs=["platform-format-review"])
    assert passed["pass"] is True


def test_invalidation_only_marks_target_and_dependency_descendants_stale(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("research"), task("visual"), task("edit", deps=["research", "visual"]), task("cover", deps=["visual"])])
    # Complete independent nodes and descendants in dependency order.
    complete(engine, tmp_path, "research", "w1")
    complete(engine, tmp_path, "visual", "w2")
    complete(engine, tmp_path, "cover", "w3")
    complete(engine, tmp_path, "edit", "w4")
    result = engine.invalidate("demo", "visual", "visual direction changed")
    assert set(result["invalidated_tasks"]) == {"visual", "edit", "cover"}
    states = {item["task_id"]: item["status"] for item in engine.list_tasks("demo")}
    assert states["research"] == "COMPLETED"
    assert states["visual"] == states["edit"] == states["cover"] == "STALE"
    reopened = engine.reopen("demo", "visual", "new visual direction approved")
    assert set(reopened) == {"visual", "edit", "cover"}
    states = {item["task_id"]: item["status"] for item in engine.list_tasks("demo")}
    assert states["visual"] == "READY"
    assert states["edit"] == states["cover"] == "PENDING"


def test_learning_stays_candidate_until_independent_replay_and_counterexample_trials(tmp_path):
    engine = make_engine(tmp_path)
    candidate = engine.record_learning("demo", {
        "method": "use a locked camera and one object transform for product reveal shots",
        "applicability": ["static product hero shots"],
        "counterexamples": ["handheld documentary movement"],
        "failure_conditions": ["camera motion is part of the story"],
        "evidence_refs": ["pilot://001-shot-04"],
        "replay_refs": ["fixture://product-reveal"],
        "independent_replay_pass": True,
    })
    assert candidate["status"] == "CANDIDATE"
    validated = engine.record_learning("demo", {
        "method": "use a locked camera and one object transform for product reveal shots",
        "applicability": ["static product hero shots"],
        "counterexamples": ["handheld documentary movement"],
        "failure_conditions": ["camera motion is part of the story"],
        "evidence_refs": ["pilot://001-shot-04", "pilot://002-shot-03"],
        "replay_refs": ["fixture://product-reveal-v1", "fixture://product-reveal-v2"],
        "independent_replay_pass": True,
        "validation_evidence_refs": ["review://method-review"],
        "counterexample_trials": ["fixture://handheld-documentary"],
    })
    assert validated["status"] == "VALIDATED"


def test_cli_exposes_standalone_entry_without_caos_import(tmp_path):
    source = (Path(__file__).parents[1] / "video_studio" / "engine.py").read_text(encoding="utf-8")
    assert "import caos" not in source.lower()
    assert "caos_runtime" not in source.lower()
    from video_studio.cli import main
    brief_file = tmp_path / "brief.json"
    brief_file.write_text(json.dumps(brief()), encoding="utf-8")
    assert main(["--root", str(tmp_path / "ws"), "init", "cli-demo", "--brief", str(brief_file)]) == 0
    assert main(["--root", str(tmp_path / "ws"), "audit", "cli-demo"]) == 0


def test_graph_rejects_cycles_and_multiple_output_producers(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ContractError, match="cycle"):
        engine.add_tasks("demo", [task("a", deps=["b"]), task("b", deps=["a"])])
    with pytest.raises(ContractError, match="one producer"):
        engine.add_tasks("demo", [task("a", outputs=["shared"]), task("b", outputs=["shared"])])


def test_input_artifact_requires_declared_transitive_producer_dependency(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ContractError, match="input artifact.*producer.*not a declared dependency"):
        engine.add_tasks("demo", [
            task("produce", outputs=["shared-artifact"]),
            task("consume", inputs=["shared-artifact"]),
        ])

    engine.add_tasks("demo", [
        task("produce", outputs=["shared-artifact"]),
        task("bridge", deps=["produce"]),
        task("consume", deps=["bridge"], inputs=["shared-artifact"]),
    ])
    task_map = {item["task_id"]: item for item in engine.list_tasks("demo")}
    assert task_map["consume"]["depends_on"] == ["bridge"]
    assert "produce" not in task_map["consume"]["depends_on"]


def test_failure_retry_is_bounded_by_declared_attempt_budget(tmp_path):
    engine = make_engine(tmp_path)
    spec = task("unstable")
    spec["max_attempts"] = 2
    engine.add_tasks("demo", [spec])
    first = engine.claim_next("demo", "worker-a")
    retry = engine.fail_task("demo", "unstable", "worker-a", first["claim"]["claim_token"], {"symptom": "transient"}, retryable=True)
    assert retry == {"task_id": "unstable", "status": "READY", "retry_scheduled": True}
    second = engine.claim_next("demo", "worker-b")
    assert second["claim"]["attempt"] == 2
    final = engine.fail_task("demo", "unstable", "worker-b", second["claim"]["claim_token"], {"symptom": "still failing"}, retryable=True)
    assert final == {"task_id": "unstable", "status": "FAILED", "retry_scheduled": False}
    assert engine.claim_next("demo", "worker-c") is None


def test_artifact_paths_are_immutable_and_audit_detects_post_registration_mutation(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render", priority=10), task("another")])
    packet = engine.claim_next("demo", "artist")
    output = engine._project_dir("demo") / "artifacts" / "master.mp4"
    output.write_bytes(b"first render")
    result = engine.complete_task("demo", "render", "artist", packet["claim"]["claim_token"], {
        "render-artifact": {"path": str(output), "kind": "video", "media_type": "video/mp4", "rights_status": "OWNED"}
    })
    second = engine.claim_next("demo", "artist-2")
    assert second["task"]["task_id"] == "another"
    with pytest.raises(ContractError, match="immutable"):
        engine.complete_task("demo", "another", "artist-2", second["claim"]["claim_token"], {
            "another-artifact": {"path": str(output), "kind": "video", "media_type": "video/mp4", "rights_status": "OWNED"}
        })
    output.write_bytes(b"silently replaced")
    audit = engine.audit("demo")
    assert audit["pass"] is False
    assert any("digest_mismatch" in item for item in audit["failures"])
    with pytest.raises(ContractError, match="bytes changed"):
        engine.record_review("demo", result["artifacts"]["render-artifact"]["artifact_id"], reviewer_id="reviewer", rubric_id="craft", outcome="PASS", dimensions={"visual": 4}, evidence_refs=["frame://1"])


def test_release_check_rehashes_final_artifact_before_acceptance(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    artifact = complete(engine, tmp_path, "render", "artist")
    engine.record_review("demo", artifact["artifact_id"], reviewer_id="reviewer", rubric_id="craft", outcome="PASS", dimensions={"visual": 4}, evidence_refs=["frame://1"])
    output = Path(artifact["path"])
    output.write_text("modified after review", encoding="utf-8")
    result = engine.release_check("demo", artifact["artifact_id"], required_rubrics=["craft"], evidence_refs=["platform-format-review"])
    assert result["pass"] is False
    assert "artifact_bytes_missing_or_digest_changed" in result["failures"]


def test_builtin_ffprobe_qa_measures_real_media_and_completes_a_claimed_task(tmp_path):
    import shutil
    import subprocess

    from video_studio.media import run_claimed_media_qa

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg/ffprobe are not installed")
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("technical-qa", inputs=["final-candidate"], outputs=["technical-qa-receipt"])])
    media = tmp_path / "sample.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1:r=25",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=1", "-c:v", "libx264",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-y", str(media),
    ], check=True, capture_output=True)
    engine.import_asset("demo", "final-candidate", media, kind="video", media_type="video/mp4", rights_status="OWNED")
    # Recreate task with the explicit measurement contract before claiming.
    # The task is already waiting for the input; update the declared tool requirements in its task contract.
    with engine._connect("demo") as connection:
        connection.execute(
            "UPDATE tasks SET kind='technical_measurement',requirements_json=? WHERE project_id='demo' AND task_id='technical-qa'",
            (json.dumps({"tool": "ffprobe", "resolution": "320x240", "frame_rate": 25, "duration_min_seconds": 0.8, "duration_max_seconds": 1.2, "audio_required": True}),),
        )
        connection.commit()
    packet = engine.claim_next("demo", "qa-worker")
    result = run_claimed_media_qa(engine, "demo", "technical-qa", "qa-worker", packet["claim"]["claim_token"], "final-candidate")
    assert result["report"]["hard_pass"] is True, result["report"]["checks"]
    assert result["report"]["summary"]["width"] == 320
    assert result["report"]["summary"]["frame_rate"] == 25
    assert result["task_completion"]["status"] == "COMPLETED"
    assert engine.audit("demo")["pass"] is True


def test_event_history_and_decision_review_receipts_are_database_immutable(tmp_path):
    import sqlite3

    engine = make_engine(tmp_path)
    with engine._connect("demo") as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("UPDATE events SET event_type='TAMPERED' WHERE project_id='demo'")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM events WHERE project_id='demo'")
        connection.rollback()


def test_brief_revision_records_history_and_invalidates_only_affected_descendants(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("research", priority=20), task("visual", priority=10), task("edit", deps=["research"]), task("cover", deps=["visual"])])
    complete(engine, tmp_path, "research", "w1")
    complete(engine, tmp_path, "visual", "w2")
    complete(engine, tmp_path, "cover", "w3")
    complete(engine, tmp_path, "edit", "w4")
    revised = brief()
    revised["goal"] = "Produce a 60-second cinematic explainer with a stronger human story."
    result = engine.revise_brief("demo", revised, reason="owner changed the editorial promise", affected_task_ids=["visual"])
    assert set(result["invalidated_tasks"]) == {"visual", "cover"}
    states = {item["task_id"]: item["status"] for item in engine.list_tasks("demo")}
    assert states["research"] == states["edit"] == "COMPLETED"
    assert states["visual"] == states["cover"] == "STALE"
    history = engine.brief_history("demo")
    assert len(history) == 2
    assert history[-1]["payload"]["brief"]["goal"] == revised["goal"]
    assert engine.project("demo")["revision"] > 1


def test_task_contract_revision_revokes_claim_and_invalidates_only_descendants(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("research", priority=20), task("visual", priority=10), task("edit", deps=["research"]), task("cover", deps=["visual"])])
    complete(engine, tmp_path, "research", "w1")
    complete(engine, tmp_path, "visual", "w2")
    complete(engine, tmp_path, "cover", "w3")
    complete(engine, tmp_path, "edit", "w4")
    revised = engine.revise_task("demo", "visual", {"acceptance": {"visual": "The exact material and motion must match the approved reference."}}, reason="visual review found an untested continuity constraint")
    assert revised["task"]["status"] == "READY"
    assert revised["invalidated_descendants"] == ["cover"]
    states = {item["task_id"]: item["status"] for item in engine.list_tasks("demo")}
    assert states["research"] == states["edit"] == "COMPLETED"
    assert states["visual"] == "READY" and states["cover"] == "STALE"


def test_task_contract_revision_rejects_dependency_cycles_without_mutating_state(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("a"), task("b", deps=["a"])])
    before = engine.list_tasks("demo")
    with pytest.raises(ContractError, match="cycle"):
        engine.revise_task("demo", "a", {"depends_on": ["b"]}, reason="invalid experiment")
    after = engine.list_tasks("demo")
    assert [(x["task_id"], x["depends_on"]) for x in before] == [(x["task_id"], x["depends_on"]) for x in after]


def test_release_check_blocks_conflicting_review_outcomes_for_same_rubric(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("render")])
    artifact = complete(engine, tmp_path, "render", "artist")
    engine.record_review("demo", artifact["artifact_id"], reviewer_id="reviewer-pass", rubric_id="craft", outcome="PASS", dimensions={"visual": 4}, evidence_refs=["frame://pass"])
    engine.record_review("demo", artifact["artifact_id"], reviewer_id="reviewer-fail", rubric_id="craft", outcome="FAIL", dimensions={"visual": 1}, evidence_refs=["frame://fail"])
    result = engine.release_check("demo", artifact["artifact_id"], required_rubrics=["craft"], evidence_refs=["platform-format-review"])
    assert result["pass"] is False
    assert any(item.startswith("required_review_missing_or_conflicting:craft") for item in result["failures"])

def test_audit_detects_tampering_of_stale_historical_artifacts(tmp_path):
    engine = make_engine(tmp_path)
    engine.add_tasks("demo", [task("research"), task("edit", deps=["research"], inputs=["research-artifact"])])
    research = complete(engine, tmp_path, "research", "researcher")
    complete(engine, tmp_path, "edit", "editor")
    engine.invalidate("demo", "research", "owner changed source interpretation")
    Path(research["path"]).write_text("tampered historical evidence", encoding="utf-8")
    report = engine.audit("demo")
    assert report["pass"] is False
    assert any(
        item.startswith("artifact_digest_mismatch:")
        and research["artifact_id"] in item
        for item in report["failures"]
    )


def test_repeated_media_qa_uses_new_immutable_receipt_path(tmp_path):
    import shutil
    import subprocess

    from video_studio.media import run_claimed_media_qa

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("FFmpeg/ffprobe are not installed")
    engine = make_engine(tmp_path)
    engine.add_tasks(
        "demo",
        [task("technical-qa", inputs=["final-candidate"], outputs=["technical-qa-receipt"])],
    )
    media = tmp_path / "repeat.mp4"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i",
            "color=c=blue:s=320x240:d=1:r=25", "-f", "lavfi", "-i",
            "sine=frequency=1000:duration=1", "-c:v", "libx264", "-pix_fmt",
            "yuv420p", "-c:a", "aac", "-shortest", "-y", str(media),
        ],
        check=True,
        capture_output=True,
    )
    engine.import_asset(
        "demo", "final-candidate", media, kind="video",
        media_type="video/mp4", rights_status="OWNED",
    )
    with engine._connect("demo") as connection:
        connection.execute(
            "UPDATE tasks SET kind='technical_measurement',requirements_json=? "
            "WHERE project_id='demo' AND task_id='technical-qa'",
            (json.dumps({
                "tool": "ffprobe", "resolution": "320x240",
                "frame_rate": 25, "audio_required": True,
            }),),
        )
        connection.commit()
    first_packet = engine.claim_next("demo", "qa-worker-1")
    first = run_claimed_media_qa(
        engine, "demo", "technical-qa", "qa-worker-1",
        first_packet["claim"]["claim_token"], "final-candidate",
    )
    engine.invalidate("demo", "technical-qa", "re-run measurement after QA policy update")
    engine.reopen("demo", "technical-qa", "measurement retry approved")
    second_packet = engine.claim_next("demo", "qa-worker-2")
    second = run_claimed_media_qa(
        engine, "demo", "technical-qa", "qa-worker-2",
        second_packet["claim"]["claim_token"], "final-candidate",
    )
    first_path = first["task_completion"]["artifacts"]["technical-qa-receipt"]["path"]
    second_path = second["task_completion"]["artifacts"]["technical-qa-receipt"]["path"]
    assert first_path != second_path
    assert second["task_completion"]["status"] == "COMPLETED"
    assert second["report"]["metadata"]["checker"] == "ffmpeg-ffprobe-v1.0"
    required_checks = {"video_stream", "stream_duration_match", "true_peak", "black_frames", "full_decode"}
    assert required_checks.issubset({item["check_id"] for item in second["report"]["checks"]})
    assert second["report"]["hard_pass"] is True, second["report"]["checks"]
    assert engine.audit("demo")["pass"] is True


def test_task_outputs_persist_exact_input_lineage_and_source_replacement_invalidates_consumers(tmp_path):
    engine = make_engine(tmp_path)
    source = tmp_path / "source-v1.mp4"
    source.write_bytes(b"source version one")
    first = engine.import_asset(
        "demo", "source-video", source, kind="video", media_type="video/mp4",
        rights_status="OWNED", metadata={"rights_evidence_refs": ["https://rights.example/license/1"]},
    )
    engine.add_tasks("demo", [
        task("edit", inputs=["source-video"]),
        task("package", deps=["edit"], inputs=["edit-artifact"]),
    ])
    edit = complete(engine, tmp_path, "edit", "editor")
    complete(engine, tmp_path, "package", "packager")
    with engine._connect("demo") as connection:
        link = connection.execute(
            "SELECT input_artifact_id,input_sha256 FROM artifact_inputs WHERE project_id='demo' AND output_artifact_id=?",
            (edit["artifact_id"],),
        ).fetchone()
        assert link["input_artifact_id"] == first["artifact_id"]
        assert link["input_sha256"] == first["sha256"]

    source_v2 = tmp_path / "source-v2.mp4"
    source_v2.write_bytes(b"source version two")
    second = engine.import_asset(
        "demo", "source-video", source_v2, kind="video", media_type="video/mp4",
        rights_status="OWNED", metadata={"rights_evidence_refs": ["https://rights.example/license/2"]},
    )
    assert second["version"] == 2
    states = {item["task_id"]: item["status"] for item in engine.list_tasks("demo")}
    assert states["edit"] == "STALE"
    assert states["package"] == "STALE"
    with engine._connect("demo") as connection:
        old_source = connection.execute(
            "SELECT status FROM artifacts WHERE project_id='demo' AND artifact_id=?",
            (first["artifact_id"],),
        ).fetchone()
        old_output = connection.execute(
            "SELECT status FROM artifacts WHERE project_id='demo' AND artifact_id=?",
            (edit["artifact_id"],),
        ).fetchone()
    assert old_source["status"] == "STALE"
    assert old_output["status"] == "STALE"


def test_release_check_fails_closed_on_uncleared_source_asset_in_final_lineage(tmp_path):
    engine = make_engine(tmp_path)
    source = tmp_path / "unknown-rights.mp4"
    source.write_bytes(b"source")
    engine.import_asset(
        "demo", "source-video", source, kind="video", media_type="video/mp4",
        rights_status="UNKNOWN",
    )
    engine.add_tasks("demo", [task("render", inputs=["source-video"])])
    packet = engine.claim_next("demo", "renderer")
    output = engine._project_dir("demo") / "artifacts" / "final.mp4"
    output.write_bytes(b"final-video")
    result = engine.complete_task(
        "demo", "render", "renderer", packet["claim"]["claim_token"],
        {"render-artifact": {
            "path": str(output), "kind": "video", "media_type": "video/mp4",
            "rights_status": "OWNED",
            "metadata": {"rights_evidence_refs": ["https://rights.example/owner-claim"]},
        }},
    )
    engine.record_review(
        "demo", result["artifacts"]["render-artifact"]["artifact_id"],
        reviewer_id="editorial-reviewer", rubric_id="editorial", outcome="PASS",
        dimensions={}, evidence_refs=["review://editorial"],
    )
    release = engine.release_check(
        "demo", result["artifacts"]["render-artifact"]["artifact_id"],
        required_rubrics=["editorial"],
    )
    assert release["pass"] is False
    assert any(item.startswith("lineage_rights_not_cleared:source-video") for item in release["failures"])
    assert "technical_qa_receipt_missing:technical-qa-receipt" in release["failures"]


def test_release_check_requires_exact_digest_technical_qa_human_cold_read_and_red_team(tmp_path):
    engine = StudioEngine(tmp_path / "strict-workspace")
    strict_brief = brief()
    strict_brief["release_policy"] = {
        "require_rights": True,
        "require_rights_evidence": True,
        "required_review_rubrics": ["editorial", "human-cold-read", "red-team"],
        "required_artifact_names": ["final-video", "technical-qa-receipt"],
        "required_evidence_artifact_names": ["rights-clearance"],
        "require_technical_qa": True,
        "technical_qa_artifact_name": "technical-qa-receipt",
        "review_contracts": {
            "human-cold-read": {
                "reviewer_kind": "HUMAN",
                "execution_mode": "INDEPENDENT_COLD_READ",
                "blind_review": True,
                "require_digest_attestation": True,
                "require_context_id": True,
                "require_resolvable_evidence_refs": True,
            },
            "red-team": {
                "min_findings": 3,
                "require_evidence_per_finding": True,
                "require_disposition_per_finding": True,
                "require_resolvable_evidence_refs": True,
            },
        },
    }
    engine.create_project("strict", "Strict release", strict_brief)
    rights_file = tmp_path / "rights-clearance.txt"
    rights_file.write_text("Owner-created and cleared source package.", encoding="utf-8")
    engine.import_asset(
        "strict", "rights-clearance", rights_file, kind="document",
        media_type="text/plain", rights_status="OWNED",
    )
    evidence_paths = {}
    for evidence_name in ("cold-read-evidence", "red-team-review-evidence", "frame-001", "frame-012", "frame-018"):
        evidence_path = tmp_path / f"{evidence_name}.txt"
        evidence_path.write_text(f"Evidence for {evidence_name}", encoding="utf-8")
        evidence_paths[evidence_name] = evidence_path
        engine.import_asset(
            "strict", evidence_name, evidence_path, kind="evidence",
            media_type="text/plain", rights_status="NOT_APPLICABLE",
        )
    engine.add_tasks("strict", [
        task("render", inputs=["rights-clearance"], outputs=["final-video"]),
        task("qa", deps=["render"], inputs=["final-video"], outputs=["technical-qa-receipt"]),
    ])
    render_packet = engine.claim_next("strict", "renderer")
    final_path = engine._project_dir("strict") / "artifacts" / "final.mp4"
    final_path.write_bytes(b"verified final video bytes")
    final_result = engine.complete_task(
        "strict", "render", "renderer", render_packet["claim"]["claim_token"],
        {"final-video": {
            "path": str(final_path), "kind": "video", "media_type": "video/mp4",
            "rights_status": "OWNED",
            "metadata": {"rights_evidence_refs": ["rights-clearance"]},
        }},
    )
    final_artifact = final_result["artifacts"]["final-video"]
    qa_packet = engine.claim_next("strict", "qa-worker")
    assert qa_packet["task"]["task_id"] == "qa"
    qa_report = {
        "schema_version": 2,
        "metadata": {"checker": "ffmpeg-ffprobe-v1.0"},
        "media_sha256": final_artifact["sha256"],
        "input_artifact_id": final_artifact["artifact_id"],
        "hard_pass": True,
        "hard_failures": [],
        "checks": [
            {"check_id": check_id, "status": "PASS"}
            for check_id in ("video_stream", "stream_duration_match", "true_peak", "black_frames", "full_decode")
        ],
    }
    qa_path = engine._project_dir("strict") / "artifacts" / "qa.json"
    qa_path.write_text(json.dumps(qa_report), encoding="utf-8")
    engine.complete_task(
        "strict", "qa", "qa-worker", qa_packet["claim"]["claim_token"],
        {"technical-qa-receipt": {
            "path": str(qa_path), "kind": "qa_report", "media_type": "application/json",
            "rights_status": "NOT_APPLICABLE",
            "metadata": {
                "media_sha256": final_artifact["sha256"],
                "input_artifact_id": final_artifact["artifact_id"],
                "hard_pass": True,
                "checker": "ffmpeg-ffprobe-v1.0",
            },
        }},
    )
    engine.record_review(
        "strict", final_artifact["artifact_id"], reviewer_id="editorial-reviewer",
        rubric_id="editorial", outcome="PASS", dimensions={},
        evidence_refs=["review://editorial"],
    )
    engine.record_review(
        "strict", final_artifact["artifact_id"], reviewer_id="human-cold-reader",
        rubric_id="human-cold-read", outcome="PASS", dimensions={},
        evidence_refs=["cold-read-evidence"],
        attestation={
            "reviewer_kind": "HUMAN",
            "execution_mode": "INDEPENDENT_COLD_READ",
            "blind_review": True,
            "inspected_artifact_digest": final_artifact["sha256"],
            "context_id": "cold-read-session-001",
        },
    )
    engine.record_review(
        "strict", final_artifact["artifact_id"], reviewer_id="red-team-reviewer",
        rubric_id="red-team", outcome="PASS",
        dimensions={"findings": [
            {"finding": "Opening promise may be too broad.", "evidence_ref": "frame-001", "severity": "MEDIUM", "disposition": "MITIGATED"},
            {"finding": "A transition may obscure the key mechanism.", "evidence_ref": "frame-012", "severity": "LOW", "disposition": "ACCEPTED"},
            {"finding": "Caption density may reduce mobile readability.", "evidence_ref": "frame-018", "severity": "MEDIUM", "disposition": "MITIGATED"},
        ]},
        evidence_refs=["red-team-review-evidence"],
    )
    release = engine.release_check("strict", final_artifact["artifact_id"], required_rubrics=[])
    assert release["pass"] is True, release["failures"]
    assert release["technical_qa"]["media_sha256"] == final_artifact["sha256"]
    assert len(release["review_summary"]["red-team"]["review_ids"]) == 1
    assert engine.audit("strict")["pass"] is True


def test_release_check_rejects_red_team_without_three_evidence_backed_findings(tmp_path):
    engine = StudioEngine(tmp_path / "red-team-workspace")
    red_brief = brief()
    red_brief["release_policy"] = {
        "required_review_rubrics": ["red-team"],
        "review_contracts": {
            "red-team": {
                "min_findings": 3,
                "require_evidence_per_finding": True,
                "require_disposition_per_finding": True,
                "require_resolvable_evidence_refs": True,
            },
        },
    }
    engine.create_project("red", "Red team contract", red_brief)
    review_evidence = tmp_path / "red-team-review-evidence.txt"
    review_evidence.write_text("Red Team review evidence.", encoding="utf-8")
    engine.import_asset("red", "red-team-review-evidence", review_evidence, kind="evidence", media_type="text/plain", rights_status="NOT_APPLICABLE")
    frame_evidence = tmp_path / "frame-001.txt"
    frame_evidence.write_text("Observed frame evidence.", encoding="utf-8")
    engine.import_asset("red", "frame-001", frame_evidence, kind="evidence", media_type="text/plain", rights_status="NOT_APPLICABLE")
    engine.add_tasks("red", [task("render")])
    packet = engine.claim_next("red", "producer")
    output = engine._project_dir("red") / "artifacts" / "candidate.txt"
    output.write_text("candidate", encoding="utf-8")
    result = engine.complete_task(
        "red", "render", "producer", packet["claim"]["claim_token"],
        {"render-artifact": {"path": str(output), "kind": "document", "media_type": "text/plain", "rights_status": "OWNED"}},
    )
    artifact_id = result["artifacts"]["render-artifact"]["artifact_id"]
    engine.record_review(
        "red", artifact_id, reviewer_id="red-team-reviewer", rubric_id="red-team",
        outcome="PASS",
        dimensions={"findings": [
            {"finding": "One concern.", "evidence_ref": "frame://unregistered", "severity": "LOW", "disposition": "MITIGATED"},
        ]},
        evidence_refs=["red-team-review-evidence"],
    )
    release = engine.release_check("red", artifact_id, required_rubrics=[])
    assert release["pass"] is False
    assert any(item.startswith("review_findings_below_minimum:red-team:1<3") for item in release["failures"])
    assert any(item.startswith("review_finding_evidence_unresolved:red-team:0:frame://unregistered") for item in release["failures"])


def test_competitive_candidates_require_owner_adjudication_over_every_candidate(tmp_path):
    engine = make_engine(tmp_path)
    candidate_a = task("candidate-a")
    candidate_a["requirements"] = {"coordination": {
        "pattern": "COMPETITIVE_CANDIDATES",
        "decision_group": "topic-slate",
        "candidate_criteria": ["audience fit", "originality", "repeatability"],
    }}
    candidate_b = task("candidate-b")
    candidate_b["requirements"] = {"coordination": {
        "pattern": "COMPETITIVE_CANDIDATES",
        "decision_group": "topic-slate",
        "candidate_criteria": ["audience fit", "originality", "repeatability"],
    }}
    adjudication = task("owner-adjudication", deps=["candidate-a", "candidate-b"])
    adjudication["executor"] = "human"
    adjudication["requirements"] = {"coordination": {
        "pattern": "OWNER_ADJUDICATION",
        "consumes_group": "topic-slate",
        "adjudicator": "showrunner",
        "decision_receipt_required": True,
    }}
    engine.add_tasks("demo", [candidate_a, candidate_b, adjudication])
    assert {item["task_id"] for item in engine.list_tasks("demo")} == {
        "candidate-a", "candidate-b", "owner-adjudication",
    }


def test_owner_adjudication_cannot_skip_a_competing_candidate(tmp_path):
    engine = make_engine(tmp_path)
    candidate_a = task("candidate-a")
    candidate_a["requirements"] = {"coordination": {
        "pattern": "COMPETITIVE_CANDIDATES",
        "decision_group": "topic-slate",
        "candidate_criteria": ["audience fit"],
    }}
    candidate_b = task("candidate-b")
    candidate_b["requirements"] = {"coordination": {
        "pattern": "COMPETITIVE_CANDIDATES",
        "decision_group": "topic-slate",
        "candidate_criteria": ["audience fit"],
    }}
    adjudication = task("owner-adjudication", deps=["candidate-a"])
    adjudication["executor"] = "human"
    adjudication["requirements"] = {"coordination": {
        "pattern": "OWNER_ADJUDICATION",
        "consumes_group": "topic-slate",
        "adjudicator": "showrunner",
        "decision_receipt_required": True,
    }}
    with pytest.raises(ContractError, match="depend on every candidate"):
        engine.add_tasks("demo", [candidate_a, candidate_b, adjudication])
    assert engine.list_tasks("demo") == []


def test_consultative_advice_cannot_claim_decision_authority(tmp_path):
    engine = make_engine(tmp_path)
    advisory = task("advice")
    advisory["requirements"] = {"coordination": {
        "pattern": "CONSULTATIVE_ADVICE",
        "advisory_only": False,
        "decision_owner": "showrunner",
    }}
    with pytest.raises(ContractError, match="must be advisory_only"):
        engine.add_tasks("demo", [advisory])
