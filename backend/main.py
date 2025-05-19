from os import environ
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import uvicorn

from typing import Annotated

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

origins = [
    "http://localhost:5173"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,         
    allow_methods=["*"],            
    allow_headers=["*"],
)

app.middleware("http")(error_handler)

def get_tasks_repository() -> TasksRepository:
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    repo = TasksRepository(mongodb_client, DATABASE, COLLECTION)

    return repo


@app.get(
        "/tasks/all",
        response_model=List[TaskInfo])
async def get_all_tasks(repo: TasksRepository = Depends(get_tasks_repository)):
    return await repo.get_all()

@app.post("/test/clear")
async def clear_db(repo: TasksRepository = Depends(get_tasks_repository)):
    await repo.clear_db()
    return True

@app.get(
        "/tasks/list",
        response_model=TaskList
        )
async def get_tasks_list(
    ordering: Ordering = Ordering.byPriority,
    ordering_type: OrderingType = OrderingType.ascending,
    page: int = 1,
    page_size: int = 5,
    repo: TasksRepository = Depends(get_tasks_repository)
):
    task, count = await repo.get_list(
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
async def get_task(id: str, repo: TasksRepository = Depends(get_tasks_repository)):
    task = await repo.get_task(id)
    return Mapper.to_info(task)


@app.post(
        "/tasks",
        response_model=TaskInfo)
async def create_task(new_task: CreateTaskModel, repo: TasksRepository = Depends(get_tasks_repository)):
    task = await repo.create_task(new_task)
    return Mapper.to_info(task)


@app.delete(
        "/tasks/{id}"
        )
async def delete_task(id: str, repo: TasksRepository = Depends(get_tasks_repository)):
    result = await repo.delete_task(id)
    return result


@app.put(
        "/tasks/{id}",
        response_model=TaskInfo
        )
async def edit_task(id: str, edit_model: EditTaskModel, repo: TasksRepository = Depends(get_tasks_repository)):
    result = await repo.edit_task(edit_model, id)
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