from models import *
from datetime import datetime

class Mapper:
    @staticmethod
    def to_info(task: Task) -> TaskInfo:
        return TaskInfo(
            id=task.id,
            name=task.name,
            description=task.description,
            deadline=task.deadline.date() if task.deadline else None,
            create_time=task.create_time.date(),
            redacted_time=task.redacted_time.date() if task.redacted_time else None,
            status=task.status,
            priority=task.priority,
            done=task.done
        )
    
    @staticmethod
    def to_task(data: dict) -> Task:
        data["_id"] = str(data["_id"])
        task = Task(**data)
        return task