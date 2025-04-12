from os import environ
from fastapi import FastAPI
import motor.motor_asyncio
import uvicorn

from middleware import *
from models import *

from contextlib import asynccontextmanager

from sys import argv

dev = len(argv) == 2 and argv[1] == "test"

MONGODB_URI = "mongodb://admin:pass@localhost:27017/database?authSource=admin&retryWrites=true&w=majority"
DATABASE = "database"
COLLECTION = "task"

if not dev:
    MONGODB_URI = environ["MONGO_URI"]
    DATABASE = environ["DATABASE"]
    COLLECTION = environ["COLLECTION"]
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    app.TasksRepository = TasksRepository(mongodb_client, DATABASE, COLLECTION)
    try:    
        yield
    finally:
        app.TasksRepository.close()


app = FastAPI(lifespan=lifespan)


@app.get(
        "/tasks/all",
        response_model=List[TaskInfo])
async def get_all_tasks():
    result = await app.TasksRepository.get_all()

    print("TaskList", result)

    taskList = [Mapper.to_info(item) for item in result]

    tasks = taskList

    return tasks


@app.get(
        "/tasks/list",
        response_model=TaskList
        )
async def get_tasks_list(
    ordering: Ordering,
    ordering_type: OrideringType,
    page: int = 0,
    page_size: int = 5, #TODO: ordering enum
):
    pass


@app.get(
        "/tasks/{id}",
         response_model=TaskInfo)
async def get_task(id: str):
    return await app.TasksRepository.get_task(id)


@app.post(
        "/tasks",
        response_model=TaskInfo)
async def create_task(new_task: CreateTaskModel):
    task = await app.TasksRepository.create_task(new_task)
    return Mapper.to_info(task)


@app.delete(
        "/task/{id}"
        )
async def delete_task(id: str):
    result = await app.TasksRepository.delete_task(id)
    return result


@app.put(
        "/task/{id}"
        )
async def edit_task(id: str, edit_model: EditTaskModel):
    #TODO: implement
    pass


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
    )

#TODO: edit task in repository
#TODO: errors handling and custom errors