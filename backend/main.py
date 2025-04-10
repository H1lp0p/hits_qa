from os import environ
from fastapi import FastAPI
import motor.motor_asyncio
import uvicorn

from middleware import *
from models import *

from contextlib import asynccontextmanager

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
        app.TaskRepository.close()


app = FastAPI(lifespan=lifespan)


@app.get(
        "/"
        )
async def test():
    list = await app.TasksRepository.get_all()
    print(f"> list all:")
    print(list)
    return {"status": 200}


@app.get(
        "/tasks",
        response_model=TaskList
        )
async def get_all_tasks():
    result = await app.TasksRepository.get_all()

    return result


@app.get("/tasks/list")
async def get_tasks_list(
    priority_ordered: bool,
    date_rodered: bool,
    ordering_type: bool, #TODO: ordering enum
):
    pass


@app.get(
        "/tasks/{id}",
         response_model=TaskInfo)
async def get_task(id: str):
    return await app.TasksRepository.get_task(id)


@app.post(
        "/tasks"
        )
async def create_task(new_task: CreateTaskModel):
    task = await app.TasksRepository.create_task(new_task)
    return task


@app.delete(
        "/task/{id}"
        )
async def delete_task(id: str):
    #TODO: test
    result = app.TasksRepository.delete_task(id)
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