from data import *
from common.exceptions import *

from domain.TasksRepository import TasksRepository

from bson import ObjectId
from datetime import datetime, date

from os import environ

environ["MONGO_URI"] = "mongodb://admin:pass@localhost:27017/database?authSource=admin&retryWrites=true&w=majority"
environ["DATABASE"] = "database"
environ["COLLECTION"] = "task"

from main import app, get_tasks_repository
import motor.motor_asyncio

seeding_count = 10
priorities = [TaskPriority.low, TaskPriority.medium, TaskPriority.high, TaskPriority.critical]
tasks = [
        Task( 
            name=f"test task num {i}",
            description=f"test task desc {i}",
            create_time=datetime.combine(date=datetime.today().date(), time=datetime.min.time()),
            deadline= (datetime.combine(date=datetime.today().date().replace(day=datetime.today().day + i % 3 - 2), time=datetime.min.time())) if i % 3 != 0 else None,
            priority=priorities[i % len(priorities)],
            done=(i % 2 == 0)
            )
        for i in range(seeding_count)
    ]

async def seeding(repo: TasksRepository):
    global tasks_ids
    collection = repo.collection
    await collection.delete_many({})

    res = await collection.insert_many(map(lambda x: x.model_dump(), tasks))
    tasks_ids = res.inserted_ids
    print("!" * 200)
    print(tasks_ids)


mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(environ["MONGO_URI"])
repo = TasksRepository(mongodb_client, environ["DATABASE"], environ["COLLECTION"])

if __name__ == "__main__":
    seeding(repo)
