from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .resources import data_path


@dataclass(frozen=True)
class Technique:
    technique_id: str
    name: str
    status: str
    tags: tuple[str, ...]
    use_when: str
    avoid_when: str
    cost_level: int
    engines: tuple[str, ...]
    evidence_refs: tuple[str, ...]


class TechniqueLibrary:
    def __init__(self, path: Path | None = None):
        path = path or data_path("techniques.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.version = payload["version"]
        self.techniques = {
            item["id"]: Technique(
                technique_id=item["id"],
                name=item["name"],
                status=item.get("status", "candidate"),
                tags=tuple(item.get("tags", [])),
                use_when=item.get("use_when", ""),
                avoid_when=item.get("avoid_when", ""),
                cost_level=int(item.get("cost_level", 0)),
                engines=tuple(item.get("engines", [])),
                evidence_refs=tuple(item.get("evidence_refs", [])),
            )
            for item in payload["techniques"]
        }

    def get(self, technique_id: str) -> Technique:
        return self.techniques[technique_id]

    def find(self, tags: set[str], max_cost: int = 5, validated_only: bool = False) -> list[Technique]:
        candidates = []
        for technique in self.techniques.values():
            if technique.cost_level > max_cost:
                continue
            if validated_only and technique.status != "validated":
                continue
            overlap = len(tags.intersection(technique.tags))
            if overlap:
                candidates.append((overlap, -technique.cost_level, technique.technique_id, technique))
        candidates.sort(reverse=True)
        return [item[-1] for item in candidates]
