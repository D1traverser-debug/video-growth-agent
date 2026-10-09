import subprocess

import pytest

from video_growth_agent.media_qa import MediaQAChecker


@pytest.mark.skipif(not MediaQAChecker.tools_available(), reason="ffmpeg/ffprobe unavailable")
def test_real_media_qa_detects_streams_and_extracts_frames(tmp_path):
    media = tmp_path / "sample.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=0x345b8c:s=540x960:r=30:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(media)
    ], check=True)
    checker = MediaQAChecker(); report = checker.inspect(media)
    assert report.hard_pass
    ids = {check.check_id: check for check in report.checks}
    assert ids["video_stream"].status == "PASS"
    assert ids["stream_duration_match"].status == "PASS"
    assert ids["true_peak"].status == "PASS"
    frames = checker.extract_frames(media, tmp_path / "frames", count=5)
    assert len(frames) == 5
    assert all((tmp_path / "frames" / f.split("/")[-1]).exists() for f in frames)
