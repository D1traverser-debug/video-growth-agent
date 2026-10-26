from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import ProjectState, utcnow_iso
from .checkpoint_io import read_snapshot, write_snapshot

_PROJECT_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}$")


class ProjectStore:
    """Filesystem checkpoint store with atomic state writes and immutable receipts."""

    def __init__(self, root: Path | None = None):
        default_root = Path(os.environ.get("VGA_PROJECTS_DIR", str(Path.cwd() / "projects")))
        self.root = Path(root or default_root)
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
        manifest = {"project_id": project_id, "title": title, "metadata": metadata or {}, "created_at": utcnow_iso()}
        self._atomic_json(project_dir / "project.json", manifest)
        state = ProjectState(project_id=project_id)
        self.save(state)
        self.append_receipt(project_id, "PROJECT_CREATED", manifest)
        return state

    def exists(self, project_id: str) -> bool:
        return (self.project_dir(project_id) / "state.json").exists()

    def load(self, project_id: str) -> ProjectState:
        path = self.project_dir(project_id) / "state.json"
        payload, revision = read_snapshot(path)
        if payload is None:
            raise FileNotFoundError(f"Project state not found: {project_id}")
        state = ProjectState.from_dict(payload)
        state._checkpoint_revision = revision
        state._checkpoint_path = str(path.resolve())
        return state

    def save(self, state: ProjectState) -> None:
        path = self.project_dir(state.project_id) / "state.json"
        if getattr(state, "_checkpoint_path", str(path.resolve())) != str(path.resolve()):
            raise ValueError("project state belongs to another checkpoint; reload destination")
        revision = write_snapshot(
            path, state.to_dict(),
            expected_revision=getattr(state, "_checkpoint_revision", None),
        )
        state._checkpoint_revision = revision
        state._checkpoint_path = str(path.resolve())

    def append_receipt(self, project_id: str, event: str, payload: dict[str, Any]) -> str:
        receipt_id = f"{utcnow_iso().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:10]}"
        receipt = {"receipt_id": receipt_id, "event": event, "project_id": project_id, "created_at": utcnow_iso(), "payload": payload}
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
        # Used for newly-created project manifests. Refuse accidental overwrite.
        write_snapshot(path, payload, expected_revision=None)
