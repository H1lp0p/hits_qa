from datetime import datetime
from typing import Optional

from taskModel import TaskPriority

class CreateTaskModel:
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    create_time: datetime
    redacted_time: datetime
    priority: Optional[TaskPriority] = None

class EditTaskModel:
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None