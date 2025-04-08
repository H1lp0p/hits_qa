from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from enum import Enum, IntEnum
from typing import Optional


class TaskStatus(str, Enum):
    active = "active"
    completed = "completed"
    overdue = "overdue"
    late = "late"


class TaskPriority(IntEnum):
    low = 0
    medium = 1
    high = 2
    critical = 3


class Task(BaseModel):
    _id: Optional[str] = None
    name: str
    description: str
    deadline: Optional[datetime] = None
    create_time: datetime
    redacted_time: datetime
    status: TaskStatus = TaskStatus.active
    priority: TaskPriority = TaskPriority.medium
