from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from bson import ObjectId

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
    id: Optional[str] = Field(min_length=24, max_length=24, examples=["67fa7d39ec58e7ca2f74bd91"], alias="_id", default=None)
    name: str = Field(min_length=4)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    create_time: datetime
    redacted_time: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    done: bool = False