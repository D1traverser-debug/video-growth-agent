from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ProductionTaskContext:
    engine: Any
    packet: Mapping[str, Any]
    project_id: str
    task_id: str
    worker_id: str
    claim_token: str
    config: Mapping[str, Any]
    output_dir: Path

    @property
    def task(self) -> Mapping[str, Any]:
        return self.packet["task"]

    @property
    def inputs(self) -> Mapping[str, Mapping[str, Any]]:
        return self.packet["input_artifacts"]

    @property
    def outputs(self) -> set[str]:
        return set(self.task.get("outputs", []))
