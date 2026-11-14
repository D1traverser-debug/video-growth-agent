import json
from pathlib import Path
import shutil

import pytest

from video_growth_agent.media_graph import (
    AssetRef,
    ContextRecord,
    MediaGraph,
)
from video_growth_agent.programmatic_graphics import (
    ChartDatum,
    GraphicSpec,
    ProgrammaticGraphicsError,
    graphic_spec_from_dict,
    register_graph_candidate,
    render_programmatic_graphic,
    shot_contract_from_dict,
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
                ChartDatum("Alpha", 42, "42"),
                ChartDatum("Beta", 78, "78"),
                ChartDatum("Gamma", 56, "56"),
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
    request_path.write_text(json.dumps(request), encoding="utf-8")
    assert main(["render-graphic", str(request_path), "--output", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["candidate_only"] is True
    assert result["graph_registration"] == "NOT_REGISTERED__STANDALONE_CANDIDATE"
    assert Path(result["receipt_path"]).is_file()
