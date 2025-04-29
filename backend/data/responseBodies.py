from pydantic import BaseModel

from datetime import date
from typing import Optional, List

from data.taskModel import TaskPriority, TaskStatus


class Pagination(BaseModel):
    items_count: int
    page: int = 0
    page_size: int = 5


class TaskInfo(BaseModel):
    id: str
    name: str
    description: str
    deadline: Optional[date] = None
    create_time: date
    redacted_time: Optional[date] = None
    status: TaskStatus = TaskStatus.active
    priority: TaskPriority = TaskPriority.medium
    done: bool


class TaskList(BaseModel):
    tasks: List[TaskInfo]
    pagination: Pagination