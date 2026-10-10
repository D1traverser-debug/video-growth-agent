from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .resources import data_path


@dataclass(frozen=True)
class RoleSpec:
    role: str
    prompt: str
    veto: tuple[str, ...]


class RoleRegistry:
    def __init__(self, config_path: Path | None = None):
        path = config_path or data_path("roles.json")
        self.config = json.loads(path.read_text(encoding="utf-8"))
        prompt_source_local = str(self.config.get("prompt_source_local") or "").strip()
        if not prompt_source_local:
            raise ValueError("roles.json must declare prompt_source_local")
        source = path.parent / prompt_source_local
        if not source.is_file():
            raise FileNotFoundError(f"Missing local role prompt source: {source}")
        self.sections = self._parse_sections(source.read_text(encoding="utf-8"))

    @staticmethod
    def _parse_sections(text: str) -> dict[str, str]:
        parts = re.split(r"(?m)^##\s+(.+?)\s*$", text)
        sections: dict[str, str] = {}
        for i in range(1, len(parts), 2):
            sections[parts[i].strip()] = parts[i + 1].strip()
        return sections

    def get(self, role: str) -> RoleSpec:
        data = self.config["roles"].get(role)
        if data is None:
            raise KeyError(f"Unknown role: {role}")
        section = data["prompt_section"]
        prompt = self.sections.get(section)
        if not prompt:
            raise ValueError(f"Missing prompt section {section!r} for role {role!r}")
        return RoleSpec(role=role, prompt=prompt, veto=tuple(data.get("veto", [])))

    def validate_workflow(self, workflow_path: Path | None = None) -> list[str]:
        path = workflow_path or data_path("workflow.json")
        workflow = json.loads(path.read_text(encoding="utf-8"))
        errors: list[str] = []
        for stage in workflow["stages"]:
            for role in stage.get("required_roles", []):
                try:
                    self.get(role)
                except (KeyError, ValueError) as exc:
                    errors.append(f"{stage['id']}: {exc}")
        return errors
