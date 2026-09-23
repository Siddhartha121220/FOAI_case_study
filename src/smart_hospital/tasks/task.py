"""Task model for coordinator-driven task allocation (CLAUDE.md #16)."""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum, auto


class TaskStatus(Enum):
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    FAILED = auto()


_id_counter = itertools.count(1)


@dataclass
class Task:
    patient_id: str
    required_agent_type: str
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str | None = None
    dependencies: list[str] = field(default_factory=list)
    task_id: str = field(default_factory=lambda: f"TASK-{next(_id_counter):04d}")

    def is_ready(self, completed_task_ids: set[str]) -> bool:
        return all(dep in completed_task_ids for dep in self.dependencies)
