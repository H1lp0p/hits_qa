from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import date

from models.taskModel import *
from models.requestBodies import *

from middleware.mapper import Mapper

from pydantic import ValidationError

import re

__all__ = ("TasksRepository",)

class TasksRepository:
    def __init__(self, client: AsyncIOMotorClient, datatabase_name: str, collection_name: str):
        self.client = client
        self.collection = self.client[datatabase_name][collection_name]

    def close(self):
        self.client.close()

    async def get_all(self) -> List[Task]:
        res_list = await self.collection.find({}).to_list(length=None)
        lst = []

        for item in res_list:
            task_item = Mapper.to_task(item)
            if not self.is_correct(task_item):
                edited_task = self.update_status(task_item)
                await self.collection.replace_one({"_id": ObjectId(edited_task.id)}, edited_task.model_dump())
                task_item = edited_task
            lst.append(task_item)

        return lst
    
    async def get_list(self, page_size: int, page_num: int, rodering_type: OrideringType, ordering: Ordering) -> List[Task]:
        pass

    async def get_task(self, id: str) -> Task:
        res = await self.collection.find({"_id": ObjectId(id)})
        task = Mapper.to_task(res)
        return task

    async def delete_task(self, id: str) -> bool:
        return (await self.collection.delete_one({"_id": ObjectId(id)})).deleted_count == 1

    async def create_task(self, new_task: CreateTaskModel) -> Task:

        nowTime = date.today()

        task = Task(
            name=new_task.name,
            description=new_task.description,
            deadline= datetime.combine(new_task.deadline, datetime.min.time()) if new_task.deadline else None,
            priority=new_task.priority if new_task.priority != None else TaskPriority.medium,
            create_time=datetime.combine(nowTime, datetime.min.time())
        )

        from_name_proiroty, from_name_deadline = self.format_task_name(task.name)

        if new_task.deadline == None and not from_name_deadline:
            task.deadline = date(from_name_deadline)
        
        if new_task.priority == None and from_name_proiroty:
            task.priority = from_name_proiroty

        print(task)
        task = self.update_status(task)
        print(task)

        result = await self.collection.insert_one(task.model_dump())
        created_object = await self.collection.find_one({"_id": result.inserted_id})

        return Mapper.to_task(created_object)

    async def edit_task(self, edit_data: EditTaskModel, id: str) -> Task:
        task = Mapper.to_task(await self.collection.find({"_id": ObjectId(id)}))
        task.name = edit_data.name if edit_data.name else task.name
        task.description = edit_data.description if edit_data.description else task.description
        task.deadline = datetime.combine(edit_data.deadline, datetime.min.time()) if edit_data.deadline else task.deadline
        task.priority = edit_data.priority if edit_data.priority else task.priority

        task = self.update_status(task)
        await self.collection.replace_one({"_id": ObjectId(task.id)}, task.model_dump())
        return task
        #TODO: insert
    
    def is_correct(self, task: Task) -> bool:
        nowDate = date.today()
        res = True

        if task.done:
            if task.deadline < datetime.combine(nowDate, datetime.min.time()):
                res = task.status == TaskStatus.late
            else:
                res = task.status == TaskStatus.completed
        else:
            if task.deadline < datetime.combine(nowDate, datetime.min.time()):
                res = task.status == TaskStatus.overdue
            else:
                res = task.status == TaskStatus.active
            
        return res

    def update_status(self, task: Task) -> Task:
        copy = task.model_copy()

        nowDate = date.today()

        if task.done:
            if task.deadline < datetime.combine(nowDate, datetime.min.time()):
                copy.status = TaskStatus.late
            else:
                copy.status = TaskStatus.completed
        else:
            if task.deadline < datetime.combine(nowDate, datetime.min.time()):
                copy.status = TaskStatus.overdue
            else:
                copy.status = TaskStatus.active
        
        print("copy", copy)

        return copy

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