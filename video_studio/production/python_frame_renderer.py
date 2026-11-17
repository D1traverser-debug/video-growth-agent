from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
from typing import Any, Mapping

from .contracts import FrameRenderSpec, ProductionContractError
from .ffmpeg_assembler import RenderExecutionError, sha256_file, _write_json_exclusive


class PythonFrameRenderer:
    """Execute an explicitly trusted project-owned Python frame function and encode a silent shot candidate."""

    @staticmethod
    def render(
        spec: FrameRenderSpec, *, input_artifacts: Mapping[str, Mapping[str, Any]],
        output_dir: str | Path, expected_outputs: set[str], project_root: str | Path,
    ) -> dict[str, Any]:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise RenderExecutionError("ffmpeg and ffprobe are required for Python frame rendering")
        spec.validate_inputs(set(input_artifacts))
        if expected_outputs != {spec.video_output, spec.receipt_output}:
            raise ProductionContractError("frame render task outputs must exactly match video_output and receipt_output")
        root = Path(output_dir).resolve()
        root.mkdir(parents=True, exist_ok=True)
        project_dir = Path(project_root).resolve()
        video_path = root / f"{spec.video_output}.mp4"
        receipt_path = root / f"{spec.receipt_output}.json"
        if video_path.exists() or receipt_path.exists():
            raise RenderExecutionError("refusing to overwrite an existing frame-render output")

        def verified_input(name: str) -> tuple[Path, dict[str, Any]]:
            artifact = input_artifacts[name]
            path = Path(str(artifact.get("path", ""))).resolve()
            if not path.is_file() or path.stat().st_size <= 0:
                raise RenderExecutionError(f"frame-render input is missing or empty: {name}")
            digest = sha256_file(path)
            declared = artifact.get("sha256") or artifact.get("digest")
            if declared and declared != digest:
                raise RenderExecutionError(f"frame-render input digest changed: {name}")
            return path, {
                "name": name, "artifact_id": artifact.get("artifact_id"), "sha256": digest,
                "bytes": path.stat().st_size, "kind": artifact.get("kind"), "media_type": artifact.get("media_type"),
            }

        renderer_path, renderer_meta = verified_input(spec.renderer_input)
        renderer_artifact = input_artifacts[spec.renderer_input]
        renderer_type = str(renderer_artifact.get("media_type", "")).lower()
        if renderer_artifact.get("kind") != "source_code" or renderer_type not in {"text/x-python", "text/plain", "text/x-python-script"}:
            raise ProductionContractError("renderer_input must be a registered Python source_code artifact")
        asset_paths: dict[str, str] = {}
        input_meta = [renderer_meta]
        for name in spec.asset_inputs:
            path, meta = verified_input(name)
            asset_paths[name] = str(path)
            input_meta.append(meta)

        worker_script = Path(__file__).with_name("frame_worker.py")
        if not worker_script.is_file():
            raise RenderExecutionError("packaged frame_worker.py is missing")
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONNOUSERSITE": "1", "PYTHONUNBUFFERED": "1"}
        for key in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"):
            if os.environ.get(key):
                env[key] = os.environ[key]
        with tempfile.TemporaryDirectory(prefix="vga-frame-", dir=root) as temp_dir:
            temp = Path(temp_dir)
            config_path = temp / "worker-config.json"
            config = {
                "renderer_path": str(renderer_path), "entrypoint": spec.entrypoint,
                "width": spec.width, "height": spec.height, "fps": spec.fps,
                "frame_count": spec.frame_count, "assets": asset_paths, "params": dict(spec.params),
            }
            config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
            worker_log = (temp / "worker.stderr.log").open("wb")
            ffmpeg_log = (temp / "ffmpeg.stderr.log").open("wb")
            worker = subprocess.Popen(
                [sys.executable, "-I", str(worker_script), str(config_path)],
                cwd=str(project_dir), env=env, stdout=subprocess.PIPE, stderr=worker_log,
            )
            ffmpeg = subprocess.Popen([
                "ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-xerror", "-n",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{spec.width}x{spec.height}",
                "-r", f"{spec.fps:.6f}", "-i", "pipe:0", "-an", "-frames:v", str(spec.frame_count),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                "-movflags", "+faststart", str(video_path),
            ], stdin=subprocess.PIPE, stderr=ffmpeg_log)
            frame_bytes = spec.width * spec.height * 3
            timeout_timer = threading.Timer(900, lambda: (worker.kill(), ffmpeg.kill()))
            timeout_timer.daemon = True
            timeout_timer.start()
            try:
                if worker.stdout is None or ffmpeg.stdin is None:
                    raise RenderExecutionError("failed to create frame-render pipes")
                for frame_index in range(spec.frame_count):
                    frame = worker.stdout.read(frame_bytes)
                    if len(frame) != frame_bytes:
                        raise RenderExecutionError(f"renderer produced {frame_index} complete frames; expected {spec.frame_count}")
                    ffmpeg.stdin.write(frame)
                ffmpeg.stdin.close()
                worker_code = worker.wait(timeout=900)
                ffmpeg_code = ffmpeg.wait(timeout=900)
            except Exception:
                worker.terminate()
                ffmpeg.terminate()
                worker.wait(timeout=10)
                ffmpeg.wait(timeout=10)
                raise
            finally:
                timeout_timer.cancel()
                if worker.stdout:
                    worker.stdout.close()
                worker_log.close()
                ffmpeg_log.close()
            if worker_code != 0:
                log = (temp / "worker.stderr.log").read_text(encoding="utf-8", errors="replace")
                raise RenderExecutionError(f"project frame renderer failed: {log[-5000:]}")
            if ffmpeg_code != 0:
                log = (temp / "ffmpeg.stderr.log").read_text(encoding="utf-8", errors="replace")
                raise RenderExecutionError(f"FFmpeg frame encoding failed: {log[-5000:]}")

        if not video_path.is_file() or video_path.stat().st_size <= 0:
            raise RenderExecutionError("Python frame renderer produced no video output")
        probe_result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video_path)],
            capture_output=True, text=True, timeout=120, check=False,
        )
        if probe_result.returncode != 0:
            raise RenderExecutionError(f"FFprobe could not inspect rendered shot: {probe_result.stderr[-3000:]}")
        probe = json.loads(probe_result.stdout)
        stream = next((item for item in probe.get("streams", []) if item.get("codec_type") == "video"), None)
        if stream is None:
            raise RenderExecutionError("rendered shot has no video stream")
        duration = float(stream.get("duration") or probe.get("format", {}).get("duration") or 0)
        if abs(duration - spec.duration_seconds) > max(0.08, 2.0 / spec.fps):
            raise RenderExecutionError(f"rendered shot duration mismatch: {duration:.3f}s")
        frame_count = int(stream.get("nb_frames") or 0)
        if frame_count and frame_count != spec.frame_count:
            raise RenderExecutionError(f"rendered shot frame count mismatch: {frame_count} != {spec.frame_count}")
        receipt = {
            "schema_version": "1.0", "project_id": spec.project_id, "entrypoint": spec.entrypoint,
            "trusted_project_code_execution": True,
            "execution_security_note": "Project Python source was executed as explicitly trusted code; this is not an OS/network sandbox.",
            "width": spec.width, "height": spec.height, "fps": spec.fps,
            "duration_seconds": duration, "frame_count": spec.frame_count,
            "inputs": input_meta,
            "output": {"path": video_path.name, "sha256": sha256_file(video_path), "bytes": video_path.stat().st_size},
            "renderer": "python-frame-renderer-v1", "candidate_only": True,
            "promotion_authorized": False, "release_authorized": False,
        }
        _write_json_exclusive(receipt_path, receipt)
        return {"video_path": str(video_path), "receipt_path": str(receipt_path), "receipt": receipt}
