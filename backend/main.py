from os import environ
from fastapi import FastAPI
import motor.motor_asyncio
import uvicorn

from domain.TasksRepository import *
from data import *
from common import error_handler, Mapper

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

app.middleware("http")(error_handler)

@app.get(
        "/tasks/all",
        response_model=List[TaskInfo])
async def get_all_tasks():
    return await app.TasksRepository.get_all()


@app.get(
        "/tasks/list",
        response_model=TaskList
        )
async def get_tasks_list(
    ordering: Ordering,
    ordering_type: OrderingType,
    page: int = 1,
    page_size: int = 5,
):
    task, count = await app.TasksRepository.get_list(
        ordering_type,
        ordering,
        page_size,
        page,
    )

    tasks_list = TaskList(
        tasks=map(Mapper.to_info, task),
        pagination= Pagination(
            items_count=count,
            page=page,
            page_size=page_size
        )
    )

    return tasks_list



@app.get(
        "/tasks/{id}",
         response_model=TaskInfo)
async def get_task(id: str):
    task = await app.TasksRepository.get_task(id)
    print(task)
    return Mapper.to_info(task)


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
        "/task/{id}",
        response_model=TaskInfo
        )
async def edit_task(id: str, edit_model: EditTaskModel):
    result = await app.TasksRepository.edit_task(edit_model, id)
    return Mapper.to_info(result)


if __name__ == "__main__":
    if dev:
        uvicorn.run(app)
    else:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
        )

#TODO: errors handling and custom errors