from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import date

from data.taskModel import *
from data.requestBodies import *

from common.mapper import Mapper
from common import TaskNotFound, PaginationError

from typing import Tuple
from pymongo import ASCENDING, DESCENDING

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

        lst = list(map(Mapper.to_task, res_list))

        return lst
    
    async def get_list(self, ordering_type: OrderingType, ordering: Ordering, page_size: int = 5, page_num: int = 1) -> Tuple[List[Task], int]:
        query = self.collection.find({})

        query = query.sort("priority" if ordering == Ordering.byPriority else "deadline"
                   , ASCENDING if ordering_type == OrderingType.ascending else DESCENDING)

        count = await self.collection.count_documents({})

        if (page_size <= 0) or (page_num <= 0) or (page_num > 1 and count // page_size < (page_num - 1)):
            raise PaginationError()

        query = query.skip((page_num - 1) * page_size).limit(page_size)

        tasks = list(map(Mapper.to_task, await query.to_list(length=page_size)))

        return (tasks, count)

    async def get_task(self, id: str) -> Task:
        res = await self.collection.find_one({"_id": ObjectId(id)})
        if not res:
            raise TaskNotFound()
        print(res)
        task = Mapper.to_task(res)
        return task

    async def delete_task(self, id: str) -> bool:
        task = await self.collection.find_one({"_id": ObjectId(id)})
        if not task:
            raise TaskNotFound()
        return (await self.collection.delete_one({"_id": ObjectId(id)})).deleted_count == 1

    async def create_task(self, new_task: CreateTaskModel) -> Task:

        nowTime = date.today()

        print("repo-create_task-new_task", new_task)

        from_name_proiroty, from_name_deadline = self.format_task_name(new_task.name)

        result_priority = from_name_proiroty if from_name_proiroty != None else TaskPriority.medium

        result_deadline = datetime.combine(from_name_deadline, datetime.min.time()) if from_name_deadline else None

        if new_task.priority:
            result_priority = new_task.priority
        
        if new_task.deadline:
            result_deadline = datetime.combine(new_task.deadline, datetime.min.time())
        
        print("repo-create_task-from_name", from_name_proiroty, from_name_deadline)
        print("repo-create_task-result", result_priority, result_deadline)

        task = Task(
            name=new_task.name,
            description=new_task.description,
            deadline=result_deadline,
            priority=result_priority,
            create_time=datetime.combine(nowTime, datetime.min.time()),
            done=False
        )

        result = await self.collection.insert_one(task.model_dump())
        created_object = await self.collection.find_one({"_id": result.inserted_id})

        return Mapper.to_task(created_object)

    async def edit_task(self, edit_data: EditTaskModel, id: str) -> Task:
        mongo_data = await self.collection.find_one({"_id": ObjectId(id)})
        if mongo_data:
            print(f"mongo>> {mongo_data}")
            task = Mapper.to_task(mongo_data)

            task.name = edit_data.name if edit_data.name != None else task.name
            task.description = edit_data.description if edit_data.description != None else task.description
            task.done = edit_data.done if edit_data.done != None else task.done
            task.redacted_time = datetime.today()

            result_priority = task.priority
            result_deadline = task.deadline

            from_name_proiroty, from_name_deadline = self.format_task_name(edit_data.name) if edit_data.name != None else (None, None)

            result_priority = from_name_proiroty if from_name_proiroty != None else result_priority

            result_deadline = datetime.combine(from_name_deadline, datetime.min.time()) if from_name_deadline else result_deadline

            if edit_data.priority:
                result_priority = edit_data.priority
            
            if edit_data.deadline:
                result_deadline = datetime.combine(edit_data.deadline, datetime.min.time())


            task.priority = result_priority
            task.deadline = result_deadline

            await self.collection.replace_one({"_id": ObjectId(id)}, task.model_dump())
            
            result_data = await self.collection.find_one({"_id": ObjectId(id)})

            return Mapper.to_task(result_data)

        else:
            raise TaskNotFound()

    def format_task_name(self, name: str):
        reg_priority = r"(\s|^)!([1-4])"
        reg_deadline = r"(\s|^)!before ((\d\d)\.(\d\d)\.(\d\d\d\d)|(\d\d)\-(\d\d)\-(\d\d\d\d))\s?"

        priority = re.findall(reg_priority, name)
        deadline = re.findall(reg_deadline, name)

        res_priority = None
        res_deadline = None
        if len(deadline) > 0:
            res_deadline = re.split(r"[\.\-]", deadline[0][1])
            try:

                res_deadline = date(
                    day=int(res_deadline[0]),
                    month=int(res_deadline[1]),
                    year=int(res_deadline[2])
                )
            except ValueError as error:
                raise ValueError(f"incorrect date in task name {deadline[0][1]}")

        if len(priority) > 0:
            print(priority)
            res_priority = int(priority[0][1])
            res_priority = TaskPriority(res_priority - 1)

        return (res_priority,
                res_deadline)