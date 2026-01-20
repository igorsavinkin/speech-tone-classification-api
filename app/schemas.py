from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Label(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class TaskStatus(str, Enum):
    waiting_for_humans = "waiting_for_humans"
    completed = "completed"


class ClassifyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class ClassifyResponse(BaseModel):
    status: TaskStatus
    label: Optional[Label] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    task_id: Optional[str] = None


class HumanLabel(BaseModel):
    label: Label
    worker_id: Optional[str] = None


class HumanLabelRequest(BaseModel):
    label: Label
    worker_id: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    text: str
    status: TaskStatus
    model_label: Optional[Label] = None
    model_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    human_labels: List[HumanLabel] = Field(default_factory=list)
    final_label: Optional[Label] = None
