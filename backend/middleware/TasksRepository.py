from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import date

from models.taskModel import *
from models.requestBodies import *

from pydantic import ValidationError

import re

__all__ = ("TasksRepository",)

class TasksRepository:
    def __init__(self, client: AsyncIOMotorClient, datatabase_name: str, collection_name: str):
        self.client = client
        self.collection = self.client[datatabase_name][collection_name]

    def close(self):
        self.client.close()

    async def get_all(self):
        return await self.collection.find({}).to_list(length=None)
    
    async def get_list(self, page_size: int, page_num: int):
        pass

    async def get_task(self, id: str):
        return await self.collection.find({"_id": ObjectId(id)})

    async def delete_task(self, id: str):
        return await self.collection.delete_one({"_id": ObjectId(id)})

    async def create_task(self, new_task: CreateTaskModel):

        nowTime = date.today()

        task = None

        task = Task(
            name=new_task.name,
            description=new_task.description,
            deadline= datetime.combine(new_task.deadline, datetime.min.time()),
            priority=new_task.priority if new_task.priority != None else TaskPriority.medium,
            create_time=datetime.combine(nowTime, datetime.min.time())
        )

        from_name_proiroty, from_name_deadline = self.format_task_name(task.name)

        if task.deadline != None and datetime.combine(nowTime, datetime.min.time()) > task.deadline:
            task.status = TaskStatus.overdue

        if new_task.deadline == None and not from_name_deadline:
            task.deadline = date(from_name_deadline)
        
        if new_task.priority == None and not from_name_proiroty:
            task.priority = from_name_proiroty

        result = await self.collection.insert_one(task.model_dump())
        created_object = await self.collection.find_one({"_id": result.inserted_id})

        return Task(**created_object)

    async def edit_task(self, edit_data: EditTaskModel, id: str):
        task = await self.collection.find({"_id": ObjectId(id)})
        #TODO: edit task

    def format_task_name(self, name: str):
        reg_priority = r"\!([1-4])"
        reg_deadline = r"!before ((\d\d)\.(\d\d)\.(\d\d\d\d)|(\d\d)\-(\d\d)\-(\d\d\d\d))"

        priority = re.findall(reg_priority, name)
        deadline = re.findall(reg_deadline, name)

        res_priority = None
        res_deadline = None
        if len(deadline) > 0:
            res_deadline = re.split(r"[\.\-]", deadline[0][0])
            res_deadline = date(
                day=int(res_deadline[0]),
                month=int(res_deadline[1]),
                year=int(res_deadline[2])
            )

        if len(priority) > 0:
            res_priority = int(priority[0])
            res_priority = TaskPriority(res_priority - 1)

        return (res_priority,
                res_deadline)

