import re
from datetime import datetime
from enum import IntEnum

class TaskPriority(IntEnum):
    low = 0
    medium = 1
    high = 2
    critical = 3


def format_task_name(name: str):
    reg_priority = r"\!([1-4])"
    reg_deadline = r"!before ((\d\d)\.(\d\d)\.(\d\d\d\d)|(\d\d)\-(\d\d)\-(\d\d\d\d))"

    priority = re.findall(reg_priority, name)
    deadline = re.findall(reg_deadline, name)

    res_priority = None
    res_deadline = None
    if len(deadline) > 0:
        res_deadline = re.split(r"[\.\-]", deadline[0][0])
        res_deadline = datetime(
            day=int(res_deadline[0]),
            month=int(res_deadline[1]),
            year=int(res_deadline[2])
        )

    if len(priority) > 0:
        res_priority = int(priority[0])
        res_priority = TaskPriority(res_priority - 1)

    return (res_priority,
            res_deadline)

test_name = "!before 01.01.2025 Very important task !2"

res = format_task_name(test_name)

print(res)