from datetime import date
from typing import Optional

from pydantic import BaseModel

from models.taskModel import TaskPriority

class CreateTaskModel(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[TaskPriority] = None

class EditTaskModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[TaskPriority] = None