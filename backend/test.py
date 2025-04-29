from datetime import datetime, date
from data.taskModel import Task
from data.responseBodies import TaskInfo
from middleware.mapper import Mapper

fir = date.today()


sec = date(day=12, month=4, year=2025)


print(sec < fir)