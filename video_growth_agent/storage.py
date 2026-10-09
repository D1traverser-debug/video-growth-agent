from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

from .models import ProjectState, utcnow_iso

ROOT = Path(__file__).resolve().parents[1]
_PROJECT_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}$")


class ProjectStore:
    """Filesystem checkpoint store with atomic state writes and immutable receipts."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root or ROOT / "projects")
        self.root.mkdir(parents=True, exist_ok=True)

    def project_dir(self, project_id: str) -> Path:
        if not _PROJECT_RE.fullmatch(project_id):
            raise ValueError("project_id must be 1-96 safe filename characters")
        return self.root / project_id

    def create(self, project_id: str, title: str = "", metadata: dict[str, Any] | None = None) -> ProjectState:
        project_dir = self.project_dir(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "receipts").mkdir(exist_ok=True)
        state_path = project_dir / "state.json"
        if state_path.exists():
            raise FileExistsError(f"Project already exists: {project_id}")
        manifest = {
            "project_id": project_id,
            "title": title,
            "metadata": metadata or {},
            "created_at": utcnow_iso(),
        }
        self._atomic_json(project_dir / "project.json", manifest)
        state = ProjectState(project_id=project_id)
        self.save(state)
        self.append_receipt(project_id, "PROJECT_CREATED", manifest)
        return state

    def exists(self, project_id: str) -> bool:
        return (self.project_dir(project_id) / "state.json").exists()

    def load(self, project_id: str) -> ProjectState:
        path = self.project_dir(project_id) / "state.json"
        if not path.exists():
            raise FileNotFoundError(f"Project state not found: {project_id}")
        return ProjectState.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def save(self, state: ProjectState) -> None:
        self._atomic_json(self.project_dir(state.project_id) / "state.json", state.to_dict())

    def append_receipt(self, project_id: str, event: str, payload: dict[str, Any]) -> str:
        receipt_id = f"{utcnow_iso().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:10]}"
        receipt = {
            "receipt_id": receipt_id,
            "event": event,
            "project_id": project_id,
            "created_at": utcnow_iso(),
            "payload": payload,
        }
        rel = Path("receipts") / f"{receipt_id}.json"
        path = self.project_dir(project_id) / rel
        if path.exists():
            raise FileExistsError(path)
        path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        with (self.project_dir(project_id) / "events.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(receipt, ensure_ascii=False) + "\n")
        return rel.as_posix()

    @staticmethod
    def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)
