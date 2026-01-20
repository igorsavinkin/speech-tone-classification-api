from fastapi import HTTPException

from app.queue import InMemoryQueue
from app.schemas import (
    ClassifyResponse,
    HumanLabel,
    Label,
    TaskResponse,
    TaskStatus,
)
from app.services.model import SimpleSentimentModel
from app.strategies.base import AggregationStrategy


class TaskService:
    def __init__(
        self,
        queue: InMemoryQueue,
        model: SimpleSentimentModel,
        aggregator: AggregationStrategy,
        confidence_threshold: float = 0.9,
    ) -> None:
        self.queue = queue
        self.model = model
        self.aggregator = aggregator
        self.confidence_threshold = confidence_threshold

    def classify(self, text: str) -> ClassifyResponse:
        prediction = self.model.predict(text)
        if prediction.confidence > self.confidence_threshold:
            return ClassifyResponse(
                status=TaskStatus.completed,
                label=prediction.label,
                confidence=prediction.confidence,
            )
        task = self.queue.create_task(
            text=text,
            model_label=prediction.label,
            model_confidence=prediction.confidence,
        )
        return ClassifyResponse(
            status=TaskStatus.waiting_for_humans, task_id=task.task_id
        )

    def get_task(self, task_id: str) -> TaskResponse:
        task = self.queue.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponse(
            task_id=task.task_id,
            text=task.text,
            status=task.status,
            model_label=task.model_label,
            model_confidence=task.model_confidence,
            human_labels=[
                HumanLabel(label=entry.label, worker_id=entry.worker_id)
                for entry in task.human_labels
            ],
            final_label=task.final_label,
        )

    def list_tasks(self) -> list[TaskResponse]:
        tasks = self.queue.list_tasks()
        return [
            TaskResponse(
                task_id=task.task_id,
                text=task.text,
                status=task.status,
                model_label=task.model_label,
                model_confidence=task.model_confidence,
                human_labels=[
                    HumanLabel(label=entry.label, worker_id=entry.worker_id)
                    for entry in task.human_labels
                ],
                final_label=task.final_label,
            )
            for task in tasks
        ]

    def submit_label(
        self, task_id: str, label: Label, worker_id: str | None
    ) -> TaskResponse:
        task = self.queue.add_human_label(task_id, label, worker_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        labels = [entry.label for entry in task.human_labels]
        final_label = self.aggregator.aggregate(labels)
        if final_label is not None:
            self.queue.finalize_task(task_id, final_label)

        return self.get_task(task_id)
