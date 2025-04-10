from pydantic import BaseModel

from datetime import date
from typing import Optional, List

from models.taskModel import TaskPriority, TaskStatus


class Pagination(BaseModel):
    items_count: int
    page: int
    page_size: int


class TaskInfo(BaseModel):
    _id: str = None
    name: str
    description: str
    deadline: Optional[date] = None
    create_time: date
    redacted_time: date
    status: TaskStatus = TaskStatus.active
    priority: TaskPriority = TaskPriority.medium


class TaskList(BaseModel):
    tasks: List[TaskInfo]
    pagination: Pagination