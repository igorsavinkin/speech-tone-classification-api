from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

from app.schemas import Label, TaskStatus


@dataclass
class HumanLabelEntry:
    label: Label
    worker_id: Optional[str] = None


@dataclass
class TaskEntry:
    task_id: str
    text: str
    status: TaskStatus
    model_label: Optional[Label] = None
    model_confidence: Optional[float] = None
    human_labels: List[HumanLabelEntry] = field(default_factory=list)
    final_label: Optional[Label] = None


class InMemoryQueue:
    """Simple in-memory task queue that emulates a Redis-backed task store."""

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskEntry] = {}
        self._pending: List[str] = []

    def reset(self) -> None:
        self._tasks.clear()
        self._pending.clear()

    def create_task(
        self,
        text: str,
        model_label: Optional[Label],
        model_confidence: Optional[float],
    ) -> TaskEntry:
        task_id = uuid4().hex
        task = TaskEntry(
            task_id=task_id,
            text=text,
            status=TaskStatus.waiting_for_humans,
            model_label=model_label,
            model_confidence=model_confidence,
        )
        self._tasks[task_id] = task
        self._pending.append(task_id)
        return task

    def get_task(self, task_id: str) -> Optional[TaskEntry]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[TaskEntry]:
        return list(self._tasks.values())

    def add_human_label(
        self, task_id: str, label: Label, worker_id: Optional[str]
    ) -> Optional[TaskEntry]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.human_labels.append(HumanLabelEntry(label=label, worker_id=worker_id))
        return task

    def finalize_task(self, task_id: str, final_label: Label) -> Optional[TaskEntry]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.final_label = final_label
        task.status = TaskStatus.completed
        if task_id in self._pending:
            self._pending.remove(task_id)
        return task
