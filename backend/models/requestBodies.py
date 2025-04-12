from datetime import date
from typing import Optional

from pydantic import BaseModel, Field
from enum import Enum

from models.taskModel import TaskPriority

class Ordering(str, Enum):
    byPriority = "priority"
    byDeadline = "deadline"

class OrideringType(str, Enum):
    ascending = "asc"
    descending = "desc"


class CreateTaskModel(BaseModel):
    name: str = Field(min_length=4)
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[TaskPriority] = None

class EditTaskModel(BaseModel):
    name: Optional[str] = Field(min_length=4, default=None)
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[TaskPriority] = None