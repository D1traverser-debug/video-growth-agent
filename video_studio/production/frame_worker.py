from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import traceback


def main() -> int:
    config_path = Path(sys.argv[1])
    config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_output = sys.stdout.buffer
    sys.stdout = sys.stderr
    renderer_path = Path(config["renderer_path"]).resolve()
    sys.path.insert(0, str(renderer_path.parent))
    spec = importlib.util.spec_from_file_location("video_project_renderer", renderer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load renderer source module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    render_frame = getattr(module, config["entrypoint"])
    from PIL import Image
    width, height = int(config["width"]), int(config["height"])
    fps, frame_count = float(config["fps"]), int(config["frame_count"])
    assets, params = config["assets"], config["params"]
    for index in range(frame_count):
        frame = render_frame(index / fps, width, height, assets, params)
        if not isinstance(frame, Image.Image):
            raise TypeError("render_frame(t, width, height, assets, params) must return a PIL.Image.Image")
        if frame.size != (width, height):
            frame = frame.resize((width, height), Image.Resampling.LANCZOS)
        raw_output.write(frame.convert("RGB").tobytes())
        raw_output.flush()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise SystemExit(1)
