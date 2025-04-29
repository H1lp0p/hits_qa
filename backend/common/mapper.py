from data import *
from datetime import datetime

class Mapper:
    @staticmethod
    def to_info(task: Task) -> TaskInfo:

        current_status : TaskStatus = None

        nowDate = date.today()
        is_deadline_missed =  nowDate >= task.deadline.date()
        
        if task.done:
            current_status = TaskStatus.late if is_deadline_missed else TaskStatus.completed
        else:
            current_status = TaskStatus.overdue if is_deadline_missed else TaskStatus.active

        return TaskInfo(
            id=task.id,
            name=task.name,
            description=task.description,
            deadline=task.deadline.date() if task.deadline else None,
            create_time=task.create_time.date(),
            redacted_time=task.redacted_time.date() if task.redacted_time else None,
            status=current_status,
            priority=task.priority,
            done=task.done
        )

    @staticmethod
    def to_task(data: dict) -> Task:
        data["_id"] = str(data["_id"])
        print(f">>> {data}")
        task = Task(**data)
        return task