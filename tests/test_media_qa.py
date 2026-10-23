import subprocess

import pytest

from video_growth_agent.media_qa import MediaQAChecker


@pytest.mark.skipif(not MediaQAChecker.tools_available(), reason="ffmpeg/ffprobe unavailable")
def test_real_media_qa_detects_streams_and_extracts_frames(tmp_path):
    media = tmp_path / "sample.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0x345b8c:s=540x960:r=30:d=2", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(media)], check=True)
    checker = MediaQAChecker(); report = checker.inspect(media)
    assert report.hard_pass
    ids = {check.check_id: check for check in report.checks}
    assert ids["video_stream"].status == "PASS"; assert ids["stream_duration_match"].status == "PASS"; assert ids["true_peak"].status == "PASS"
    assert len(report.metadata["sha256"]) == 64
    frames = checker.extract_frames(media, tmp_path / "frames", count=5)
    assert len(frames) == 5; assert all((tmp_path / "frames" / f.split("/")[-1]).exists() for f in frames)

@pytest.mark.skipif(not MediaQAChecker.tools_available(), reason="ffmpeg/ffprobe unavailable")
def test_directed_take_review_binds_real_file_but_never_certifies_film_quality(tmp_path):
    import hashlib
    import json
    import sys
    from pathlib import Path
    from video_growth_agent.media_qa import prepare_directed_media_review

    root = Path(__file__).parent
    plan_path = root / "fixtures" / "prompt_ip_5s.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    take = tmp_path / "test-pattern-not-a-model-render.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=0x345b8c:s=320x568:r=24:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(take),
    ], check=True)
    sheet = prepare_directed_media_review(
        plan, take, frames_dir=tmp_path / "samples", frame_count=3
    )
    assert sheet["media_asset_ref"]["sha256"] == hashlib.sha256(take.read_bytes()).hexdigest()
    assert sheet["media_asset_ref"]["byte_count"] == take.stat().st_size
    assert sheet["timeline_alignment"] == "DURATION_MISMATCH__EDIT_CONFORM_REQUIRED"
    assert sheet["technical_media_qa"]["metadata"]["sha256"] == sheet["media_asset_ref"]["sha256"]
    assert len(sheet["frame_samples"]) == 3
    assert all(Path(item).is_file() for item in sheet["frame_samples"])
    assert sheet["assessment"] == "NOT_STARTED__REAL_MEDIA_BOUND"
    assert sheet["first_pass_viewing"]["reviewer_blinding_verified"] is False
    assert sheet["first_pass_viewing"]["responses"] is None
    assert sheet["reviewer_independence"] == "NOT_ESTABLISHED"
    assert all(shot["actual_result"] == "UNREVIEWED" for shot in sheet["shots"])

    command = [
        sys.executable, "-m", "video_growth_agent.cli",
        "direct-prompts", str(plan_path), "--review-sheet", "--media", str(take),
    ]
    called = subprocess.run(command, capture_output=True, text=True)
    assert called.returncode == 0, called.stderr
    assert json.loads(called.stdout)["media_asset_ref"]["sha256"] == sheet["media_asset_ref"]["sha256"]

    bare_media = subprocess.run(
        command[:4] + ["--media", str(take)], capture_output=True, text=True
    )
    assert bare_media.returncode == 2
    assert "--media requires --review-sheet" in bare_media.stderr


def test_directed_review_refuses_nonexistent_or_zero_byte_media(tmp_path):
    import json
    from pathlib import Path
    from video_growth_agent.media_qa import prepare_directed_media_review

    fixture = Path(__file__).parent / "fixtures" / "prompt_ip_5s.json"
    plan = json.loads(fixture.read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="nonempty local video"):
        prepare_directed_media_review(plan, tmp_path / "missing.mp4")
    empty = tmp_path / "empty.mp4"
    empty.write_bytes(b"")
    with pytest.raises(ValueError, match="nonempty local video"):
        prepare_directed_media_review(plan, empty)
