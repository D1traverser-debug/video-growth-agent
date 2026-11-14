import json
from pathlib import Path
import shutil

import pytest

from video_growth_agent.media_graph import (
    AssetRef,
    ContextRecord,
    DecisionRecord,
    EvidenceRecord,
    MediaGraph,
    MediaGraphStore,
    AssetVersion,
)
from video_growth_agent.programmatic_graphics import (
    ChartDatum,
    GraphicSpec,
    ProgrammaticGraphicsError,
    graphic_spec_from_dict,
    register_graph_candidate,
    render_programmatic_graphic,
    shot_contract_from_dict,
    validate_shot_graph_bindings,
    _drawtext,
)
from video_growth_agent.production_os import ReferenceBinding, ShotContract

FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def make_shot(**overrides):
    values = {
        "shot_id": "shot-01",
        "sequence_id": "sequence-01",
        "narrative_job": "Explain the key information visually",
        "duration_seconds": 2.0,
        "truth_mode": "SYNTHETIC",
        "risk": "LOW",
        "allowed_modes": frozenset({"PROGRAMMATIC_GRAPHICS"}),
        "required_capabilities": frozenset({"ffmpeg.drawtext"}),
        "quality_targets": {"readability": 4.0},
        "disclosure_required": True,
        "editorial_plan_ref": "editorial-plan:v1",
        "beat_id": "beat-01",
        "source_claim_ids": ("claim-01",),
    }
    values.update(overrides)
    return ShotContract(**values)


def make_spec(kind="TITLE_CARD", **overrides):
    values = {
        "spec_id": "spec-01",
        "kind": kind,
        "title": "The edit took it literally",
        "subtitle": "A real headline meets a fictional visual",
        "kicker": "NEWS / VISUAL SATIRE",
        "duration_seconds": 2.0,
        "width": 640,
        "height": 640,
        "fps": 24,
    }
    if kind == "STAT_CARD":
        values.update({"metric": "2.4x", "metric_label": "Illustrative ratio"})
    if kind == "BAR_CHART":
        values.update({
            "chart_data": (
                ChartDatum("Alpha", 42, "42%"),
                ChartDatum("Beta", 78, "78%"),
                ChartDatum("Gamma", 56, "56%"),
            )
        })
    values.update(overrides)
    return GraphicSpec(**values)


def make_graph():
    graph = MediaGraph()
    graph.add_context(ContextRecord("program-01", "PROGRAM"))
    graph.add_context(ContextRecord("series-01", "SERIES", "program-01"))
    graph.add_context(ContextRecord("episode-01", "EPISODE", "series-01"))
    graph.add_context(ContextRecord("sequence-01", "SEQUENCE", "episode-01"))
    graph.add_context(ContextRecord("shot-01", "SHOT", "sequence-01"))
    return graph


def require_render_tools():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe") or not FONT.is_file():
        pytest.skip("FFmpeg/ffprobe/DejaVu font unavailable")


def test_title_card_renders_real_mp4_and_registers_only_candidate(tmp_path):
    require_render_tools()
    shot = make_shot()
    spec = make_spec(title="CEO: 'stepped down'?", subtitle="The fight scene is fictional.")
    output = tmp_path / "title-card.mp4"
    receipt = render_programmatic_graphic(
        shot, spec, output_path=output, font_path=FONT,
    )
    assert output.is_file() and output.stat().st_size > 0
    assert receipt["candidate_only"] is True
    assert receipt["promotion_authorized"] is False
    assert receipt["release_authorized"] is False
    assert receipt["paid_service_used"] is False
    assert receipt["network_access_used"] is False
    assert receipt["audio_mode"] == "INTENTIONAL_SILENCE_FOR_VISUAL_PREVIEW"
    assert receipt["media_sha256"] and len(receipt["media_sha256"]) == 64
    assert receipt["qa"]["hard_pass"] is True

    graph = make_graph()
    asset_key = register_graph_candidate(graph, shot, spec, receipt)
    asset_ref = AssetRef.from_key(asset_key)
    assert graph.assets[asset_ref].state == "CANDIDATE"
    assert graph.promoted_versions == {}
    assert len(graph.evidence) == 1
    assert len(graph.tasks) == 1
    assert graph.tasks[next(iter(graph.tasks))].state == "COMPLETED"


def test_bar_chart_renderer_creates_visual_candidate(tmp_path):
    require_render_tools()
    shot = make_shot(source_claim_ids=("claim-a", "claim-b", "claim-c"))
    receipt = render_programmatic_graphic(
        shot, make_spec("BAR_CHART"), output_path=tmp_path / "chart.mp4", font_path=FONT,
    )
    assert receipt["qa_hard_pass"] is True
    assert receipt["graphic_spec"]["kind"] == "BAR_CHART"


def test_shot_must_explicitly_allow_programmatic_graphics():
    shot = make_shot(allowed_modes=frozenset({"T2V", "I2V"}))
    with pytest.raises(ProgrammaticGraphicsError, match="does not allow"):
        render_programmatic_graphic(
            shot, make_spec(), output_path="unused.mp4", font_path=FONT,
        )


def test_renderer_never_claims_product_truth():
    ref = ReferenceBinding("product", "v1", "sha256:abc", "PRODUCT_REFERENCE", "rights://product")
    shot = make_shot(truth_mode="PRODUCT_TRUTH", references=(ref,))
    with pytest.raises(ProgrammaticGraphicsError, match="not observed real/product-truth"):
        render_programmatic_graphic(
            shot, make_spec(), output_path="unused.mp4", font_path=FONT,
        )


def test_renderer_blocks_ipos_identity_dependent_shots():
    shot = make_shot(
        ip_identity_required=True,
        ip_identity_bundle_ref="ipos://bundle/v1",
        ip_identity_approval_ref="approval://owner/v1",
    )
    with pytest.raises(ProgrammaticGraphicsError, match="IPOS identity-dependent"):
        render_programmatic_graphic(
            shot, make_spec(), output_path="unused.mp4", font_path=FONT,
        )


def test_synthetic_graphic_requires_platform_disclosure_contract():
    shot = make_shot(disclosure_required=False)
    with pytest.raises(ProgrammaticGraphicsError, match="disclosure_required=true"):
        render_programmatic_graphic(
            shot, make_spec(), output_path="unused.mp4", font_path=FONT,
        )


def test_claim_backed_graphics_require_source_claim_ids():
    shot = make_shot(source_claim_ids=())
    with pytest.raises(ProgrammaticGraphicsError, match="source_claim_ids"):
        render_programmatic_graphic(
            shot, make_spec("BAR_CHART"), output_path="unused.mp4", font_path=FONT,
        )


def test_graphic_duration_must_match_shot_contract():
    with pytest.raises(ProgrammaticGraphicsError, match="duration must match"):
        render_programmatic_graphic(
            make_shot(), make_spec(duration_seconds=3.0),
            output_path="unused.mp4", font_path=FONT,
        )


def test_mixed_disclosed_requires_source_references():
    shot = make_shot(truth_mode="MIXED_DISCLOSED", references=())
    with pytest.raises(ProgrammaticGraphicsError, match="source/reference bindings"):
        render_programmatic_graphic(
            shot, make_spec(), output_path="unused.mp4", font_path=FONT,
        )


def test_renderer_never_overwrites_existing_output(tmp_path):
    require_render_tools()
    output = tmp_path / "candidate.mp4"
    shot, spec = make_shot(), make_spec()
    render_programmatic_graphic(shot, spec, output_path=output, font_path=FONT)
    with pytest.raises(FileExistsError):
        render_programmatic_graphic(shot, spec, output_path=output, font_path=FONT)


def test_graph_registration_requires_existing_shot_context():
    shot, spec = make_shot(), make_spec()
    graph = MediaGraph()
    with pytest.raises(ProgrammaticGraphicsError, match="must already contain SHOT context"):
        register_graph_candidate(
            graph, shot, spec,
            {"media_sha256": "a" * 64, "media_path": "/not-used.mp4"},
        )


def test_graph_registration_rejects_missing_exact_reference_version(tmp_path):
    require_render_tools()
    ref = ReferenceBinding("ref-asset", "v7", "sha256:source", "VISUAL_REFERENCE", "rights://ref")
    shot = make_shot(references=(ref,))
    spec = make_spec()
    receipt = render_programmatic_graphic(
        shot, spec, output_path=tmp_path / "candidate.mp4", font_path=FONT,
    )
    graph = make_graph()
    with pytest.raises(ProgrammaticGraphicsError, match="reference assets missing"):
        register_graph_candidate(graph, shot, spec, receipt)


def test_json_contract_parsers_fail_closed_on_wrong_shapes():
    with pytest.raises(ProgrammaticGraphicsError):
        graphic_spec_from_dict({"spec_id": "x", "kind": [], "title": "bad"})
    with pytest.raises(ProgrammaticGraphicsError):
        shot_contract_from_dict({"allowed_modes": [{"not": "hashable"}]})
    with pytest.raises(ProgrammaticGraphicsError):
        shot_contract_from_dict({"references": ["not-an-object"]})


def test_cli_render_writes_a_receipt_and_reports_unregistered_candidate(tmp_path, capsys):
    require_render_tools()
    from video_growth_agent.cli import main

    request = {
        "font_path": str(FONT),
        "shot_contract": {
            "shot_id": "shot-01",
            "sequence_id": "sequence-01",
            "narrative_job": "Explain a system visually",
            "duration_seconds": 2.0,
            "truth_mode": "SYNTHETIC",
            "risk": "LOW",
            "allowed_modes": ["PROGRAMMATIC_GRAPHICS"],
            "required_capabilities": ["ffmpeg.drawtext"],
            "quality_targets": {"readability": 4.0},
            "disclosure_required": True,
            "editorial_plan_ref": "editorial-plan:v1",
            "beat_id": "beat-01",
            "source_claim_ids": ["claim-01"],
        },
        "graphic": {
            "spec_id": "cli-demo",
            "kind": "TITLE_CARD",
            "title": "Local render",
            "subtitle": "No paid API and no network request",
            "duration_seconds": 2.0,
            "width": 640,
            "height": 640,
            "fps": 24,
        },
    }
    request_path = tmp_path / "request.json"
    output = tmp_path / "cli.mp4"
    graph_path = tmp_path / "media-graph.json"
    MediaGraphStore(graph_path).save(make_graph())
    request_path.write_text(json.dumps(request), encoding="utf-8")
    assert main([
        "render-graphic", str(request_path), "--output", str(output),
        "--graph", str(graph_path),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["candidate_only"] is True
    assert result["graph_registration"] == "CANDIDATE_REGISTERED"
    assert result["media_graph_asset_ref"]
    assert Path(result["receipt_path"]).is_file()
    graph = MediaGraphStore(graph_path).load()
    asset_ref = AssetRef.from_key(result["media_graph_asset_ref"])
    assert graph.assets[asset_ref].state == "CANDIDATE"
    assert graph.promoted_versions == {}

def test_capability_registry_and_domain_manifest_advertise_only_bounded_scope():
    root = Path(__file__).resolve().parents[1]
    capabilities = json.loads(
        (root / "video_growth_agent/data/capabilities.json").read_text(encoding="utf-8")
    )
    entry = next(
        item for item in capabilities["capabilities"]
        if item["capability_id"] == "programmatic_motion_graphics_render"
    )
    assert entry["assurance_ceiling"] == "SESSION_EXECUTABLE"
    assert entry["executor_ref"].startswith("video_growth_agent/programmatic_graphics.py")
    assert "NO_AUTOMATIC_PROMOTION_OR_RELEASE" in entry["safe_degraded_modes"]
    assert next(
        item for item in capabilities["capabilities"]
        if item["capability_id"] == "quality_critical_generation_gateway"
    )["assurance_ceiling"] == "DECLARED_ONLY"
    manifest = json.loads(
        (root / "video_growth_agent/data/domain_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["runtime"]["programmatic_graphics"] == "video_growth_agent/programmatic_graphics.py"

def test_current_agent_operability_scenario_documents_graphics_route():
    root = Path(__file__).resolve().parents[1]
    scenarios = (root / "docs/agent_operability_scenarios.md").read_text(encoding="utf-8")
    assert "Scenario 11 — Local information-graphic shot without paid generation" in scenarios
    assert "silent preview is mistaken for final audio" in scenarios

def test_graph_registration_rejects_receipt_bound_to_different_spec(tmp_path):
    require_render_tools()
    shot, spec = make_shot(), make_spec()
    receipt = render_programmatic_graphic(
        shot, spec, output_path=tmp_path / "candidate.mp4", font_path=FONT,
    )
    changed_spec = make_spec(title="A different editorial statement")
    with pytest.raises(ProgrammaticGraphicsError, match="exact ShotContract/spec/media"):
        register_graph_candidate(make_graph(), shot, changed_spec, receipt)

def test_graph_registration_rejects_failed_technical_qa(tmp_path):
    require_render_tools()
    shot, spec = make_shot(), make_spec()
    receipt = render_programmatic_graphic(
        shot, spec, output_path=tmp_path / "candidate.mp4", font_path=FONT,
    )
    receipt["qa_hard_pass"] = False
    with pytest.raises(ProgrammaticGraphicsError, match="technical QA must hard-pass"):
        register_graph_candidate(make_graph(), shot, spec, receipt)

def test_drawtext_treats_percent_and_expansion_sequences_as_literal():
    filter_text = _drawtext(
        "metric.txt", font_size=42, x="10", y="20", color="#FFFFFF",
    )
    assert "expansion=none" in filter_text

def test_graph_binding_digest_must_match_promoted_exact_version():
    binding = ReferenceBinding(
        "ref-asset", "v7", "sha256:" + "a" * 64, "SOURCE_REFERENCE", "rights://source",
    )
    shot = make_shot(truth_mode="MIXED_DISCLOSED", references=(binding,))
    graph = make_graph()
    ref = AssetRef("ref-asset", "v7")
    graph.add_asset(AssetVersion(
        ref, "episode-01", "SOURCE_REFERENCE", "file:///source.mp4",
        "sha256:" + "b" * 64,
    ))
    graph.add_evidence(EvidenceRecord(
        "source-review", "ASSET", ref.key(), "SOURCE_REVIEW",
        ("review://source",), "2026-11-14T00:00:00Z",
    ))
    graph.add_decision(DecisionRecord(
        "source-promotion", "PROMOTION", "reviewer", (ref.key(),),
        ("criteria://source",), ("source-review",), "PROMOTE",
        "2026-11-14T00:01:00Z",
    ))
    graph.promote_asset(ref, decision_id="source-promotion")
    with pytest.raises(ProgrammaticGraphicsError, match="digest mismatch"):
        register_graph_candidate(graph, shot, make_spec(), {})

def test_cli_preflight_rejects_reference_digest_mismatch_before_render(tmp_path, capsys):
    from video_growth_agent.cli import main

    graph = make_graph()
    ref = AssetRef("source-asset", "v3")
    graph.add_asset(AssetVersion(
        ref, "episode-01", "SOURCE_REFERENCE", "file:///source.mp4",
        "sha256:" + "b" * 64,
    ))
    graph.add_evidence(EvidenceRecord(
        "source-review", "ASSET", ref.key(), "SOURCE_REVIEW",
        ("review://source",), "2026-11-14T00:00:00Z",
    ))
    graph.add_decision(DecisionRecord(
        "source-promotion", "PROMOTION", "reviewer", (ref.key(),),
        ("criteria://source",), ("source-review",), "PROMOTE",
        "2026-11-14T00:01:00Z",
    ))
    graph.promote_asset(ref, decision_id="source-promotion")
    graph_path = tmp_path / "media-graph.json"
    MediaGraphStore(graph_path).save(graph)
    request = {
        "font_path": str(FONT),
        "shot_contract": {
            "shot_id": "shot-01", "sequence_id": "sequence-01",
            "narrative_job": "Explain a sourced fact", "duration_seconds": 2.0,
            "truth_mode": "MIXED_DISCLOSED", "risk": "LOW",
            "allowed_modes": ["PROGRAMMATIC_GRAPHICS"],
            "required_capabilities": ["ffmpeg.drawtext"],
            "quality_targets": {"readability": 4.0}, "disclosure_required": True,
            "editorial_plan_ref": "editorial-plan:v1", "beat_id": "beat-01",
            "source_claim_ids": ["claim-01"],
            "references": [{
                "asset_id": "source-asset", "version_id": "v3",
                "digest": "sha256:" + "a" * 64,
                "role": "SOURCE_REFERENCE", "rights_ref": "rights://source",
            }],
        },
        "graphic": {
            "spec_id": "mismatch-demo", "kind": "TITLE_CARD",
            "title": "Source-linked visual", "subtitle": "Digest must match",
            "duration_seconds": 2.0, "width": 640, "height": 640, "fps": 24,
        },
    }
    request_path = tmp_path / "request.json"
    output = tmp_path / "should-not-render.mp4"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    with pytest.raises(SystemExit):
        main([
            "render-graphic", str(request_path), "--output", str(output),
            "--graph", str(graph_path),
        ])
    assert not output.exists()
    assert "reference digest mismatch" in capsys.readouterr().err

def test_long_stat_metric_is_measured_and_shrunk_before_real_render(tmp_path):
    require_render_tools()
    shot = make_shot()
    spec = make_spec(
        "STAT_CARD", width=1080, height=1920,
        metric="1,234,567", metric_label="Reported quarterly revenue",
    )
    output = tmp_path / "long-metric.mp4"
    receipt = render_programmatic_graphic(
        shot, spec, output_path=output, font_path=FONT,
    )
    metric = receipt["text_layout"]["metric"]
    assert output.is_file() and output.stat().st_size > 0
    assert metric["fit"] is True
    assert metric["font_size"] < int(spec.height * 0.13)
    assert metric["measured_width_px"] <= metric["max_width_px"]
    assert receipt["text_layout_digest"]
    assert receipt["qa_hard_pass"] is True


def test_unfit_stat_metric_fails_before_creating_media(tmp_path):
    require_render_tools()
    output = tmp_path / "must-not-render.mp4"
    spec = make_spec(
        "STAT_CARD", width=1080, height=1920,
        metric="9" * 300, metric_label="Unreasonably long value",
    )
    with pytest.raises(ProgrammaticGraphicsError, match="metric cannot fit"):
        render_programmatic_graphic(
            make_shot(), spec, output_path=output, font_path=FONT,
        )
    assert not output.exists()


def test_title_and_subtitle_layout_receipt_contains_pixel_bounded_lines(tmp_path):
    require_render_tools()
    spec = make_spec(
        width=1080, height=1920,
        title="A statistic is only useful when the whole number is visible",
        subtitle="The layout engine measures actual glyph widths instead of counting characters.",
    )
    receipt = render_programmatic_graphic(
        make_shot(), spec, output_path=tmp_path / "wrapped-title.mp4", font_path=FONT,
    )
    for key in ("title", "subtitle"):
        item = receipt["text_layout"][key]
        assert item["fit"] is True
        assert item["line_count"] <= (3 if key == "title" else 4)
        assert all(width <= item["max_width_px"] for width in item["line_widths_px"])

def test_long_bar_chart_value_is_shrunk_to_its_actual_column_width(tmp_path):
    require_render_tools()
    spec = make_spec(
        "BAR_CHART", width=1080, height=1920,
        chart_data=(
            ChartDatum("Revenue", 42, "12,345,678"),
            ChartDatum("Costs", 78, "9,876,543"),
            ChartDatum("Margin", 56, "42%"),
        ),
    )
    receipt = render_programmatic_graphic(
        make_shot(source_claim_ids=("revenue", "costs", "margin")),
        spec, output_path=tmp_path / "long-chart-values.mp4", font_path=FONT,
    )
    value = receipt["text_layout"]["chart_value_0"]
    assert value["fit"] is True
    assert value["font_size"] < max(18, int(spec.height * 0.019))
    assert value["measured_width_px"] <= value["max_width_px"]
    assert receipt["qa_hard_pass"] is True

def test_six_row_square_chart_keeps_two_line_last_label_inside_frame(tmp_path):
    require_render_tools()
    spec = make_spec(
        "BAR_CHART", width=640, height=640,
        chart_data=(
            ChartDatum("Revenue", 42, "42%"),
            ChartDatum("Costs", 78, "78%"),
            ChartDatum("Growth", 56, "56%"),
            ChartDatum("Margin", 31, "31%"),
            ChartDatum("Forecast", 64, "64%"),
            ChartDatum("Alpha\nBeta", 22, "22%"),
        ),
    )
    receipt = render_programmatic_graphic(
        make_shot(source_claim_ids=("a", "b", "c", "d", "e", "f")),
        spec, output_path=tmp_path / "six-row-square-chart.mp4", font_path=FONT,
    )
    geometry = receipt["text_layout"]["chart_geometry"]
    assert geometry["fit"] is True
    assert len(geometry["rows"]) == 6
    for row in geometry["rows"]:
        assert row["label_y_px"] >= row["row_top_px"]
        assert row["label_y_px"] + row["label_height_px"] <= row["row_bottom_px"]
        assert row["value_y_px"] >= row["row_top_px"]
        assert row["value_y_px"] + row["value_height_px"] <= row["row_bottom_px"]
        assert row["bar_y_px"] >= row["row_top_px"]
        assert row["bar_y_px"] + row["bar_height_px"] <= row["row_bottom_px"]
    last_label = receipt["text_layout"]["chart_label_5"]
    assert last_label["line_count"] == 2
    assert last_label["total_height_px"] <= geometry["label_height_budget_px"]
    assert receipt["qa_hard_pass"] is True


def test_chart_label_that_cannot_fit_vertical_row_fails_before_render(tmp_path):
    require_render_tools()
    spec = make_spec(
        "BAR_CHART", width=640, height=640,
        chart_data=(
            ChartDatum("A\nB\nC", 42, "42%"),
            ChartDatum("Costs", 78, "78%"),
        ),
    )
    output = tmp_path / "must-not-render-chart.mp4"
    with pytest.raises(ProgrammaticGraphicsError, match="chart_label_0 cannot fit"):
        render_programmatic_graphic(
            make_shot(source_claim_ids=("a", "b")),
            spec, output_path=output, font_path=FONT,
        )
    assert not output.exists()

def test_shot_graph_binding_rejects_sequence_contract_mismatch_before_registration():
    graph = make_graph()
    graph.add_context(ContextRecord("sequence-02", "SEQUENCE", "episode-01"))
    shot = make_shot(sequence_id="sequence-02")
    with pytest.raises(ProgrammaticGraphicsError, match="sequence ancestry mismatch"):
        validate_shot_graph_bindings(graph, shot)
    with pytest.raises(ProgrammaticGraphicsError, match="sequence ancestry mismatch"):
        register_graph_candidate(graph, shot, make_spec(), {})


def test_shot_graph_binding_accepts_scene_between_shot_and_sequence():
    graph = MediaGraph()
    graph.add_context(ContextRecord("program-01", "PROGRAM"))
    graph.add_context(ContextRecord("series-01", "SERIES", "program-01"))
    graph.add_context(ContextRecord("episode-01", "EPISODE", "series-01"))
    graph.add_context(ContextRecord("sequence-01", "SEQUENCE", "episode-01"))
    graph.add_context(ContextRecord("scene-01", "SCENE", "sequence-01"))
    graph.add_context(ContextRecord("shot-01", "SHOT", "scene-01"))
    validate_shot_graph_bindings(graph, make_shot())


def test_cli_preflight_rejects_sequence_ancestry_mismatch_before_render(tmp_path, capsys):
    from video_growth_agent.cli import main

    graph = make_graph()
    graph.add_context(ContextRecord("sequence-02", "SEQUENCE", "episode-01"))
    graph_path = tmp_path / "media-graph.json"
    MediaGraphStore(graph_path).save(graph)
    request = {
        "font_path": str(FONT),
        "shot_contract": {
            "shot_id": "shot-01", "sequence_id": "sequence-02",
            "narrative_job": "Explain a sourced fact", "duration_seconds": 2.0,
            "truth_mode": "SYNTHETIC", "risk": "LOW",
            "allowed_modes": ["PROGRAMMATIC_GRAPHICS"],
            "required_capabilities": ["ffmpeg.drawtext"],
            "quality_targets": {"readability": 4.0}, "disclosure_required": True,
            "editorial_plan_ref": "editorial-plan:v1", "beat_id": "beat-01",
            "source_claim_ids": ["claim-01"],
        },
        "graphic": {
            "spec_id": "wrong-sequence", "kind": "TITLE_CARD",
            "title": "Sequence mismatch", "subtitle": "Must fail closed",
            "duration_seconds": 2.0, "width": 640, "height": 640, "fps": 24,
        },
    }
    request_path = tmp_path / "request.json"
    output = tmp_path / "must-not-render.mp4"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    with pytest.raises(SystemExit):
        main([
            "render-graphic", str(request_path), "--output", str(output),
            "--graph", str(graph_path),
        ])
    assert not output.exists()
    assert "sequence ancestry mismatch" in capsys.readouterr().err
