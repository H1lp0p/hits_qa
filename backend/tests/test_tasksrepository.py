import unittest
from unittest.mock import MagicMock, AsyncMock
from bson import ObjectId
import datetime

from domain.TasksRepository import TasksRepository
from common.exceptions import TaskNotFound, PaginationError
from data.taskModel import TaskPriority
from data.requestBodies import OrderingType, Ordering
from data.requestBodies import CreateTaskModel, EditTaskModel

class TestTasksRepository(unittest.IsolatedAsyncioTestCase):

    async def test_dummy(self):
        print("Dummy test running")
        self.assertTrue(True)

    def setUp(self):
        # Мок клиента и коллекции
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        # Настраиваем доступ client[db][collection]
        self.mock_client.__getitem__.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_collection

        self.repo = TasksRepository(client=self.mock_client, datatabase_name="test_db", collection_name="test_collection")
        self.repo.collection = self.mock_collection

    async def test_get_all_tasks(self):
        # Мок find().to_list()

        testTasks = []
        for i in range(10):
            new_test = {
                "_id": str(ObjectId()),
                "name": f"test task num {i}",
                "description": f"description ${i}",
                "create_time": str(datetime.datetime.today()),
                "done": str(i % 2 == 0)
            }
            testTasks.append(new_test)

        self.mock_collection.find.return_value.to_list = AsyncMock(return_value=testTasks)

        tasks = await self.repo.get_all()

        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), len(testTasks))
        self.assertEqual(tasks[0].name, testTasks[0]["name"])
        print("DONE!!!!")

    async def test_get_list_default(self):

        testTasks = []
        for i in range(10):
            new_test = {
                "_id": str(ObjectId()),
                "name": f"test task num {i}",
                "description": f"description ${i}",
                "create_time": str(datetime.datetime.today()),
                "done": str(i % 2 == 0)
            }
            testTasks.append(new_test)

        task_id = str(ObjectId())
        self.mock_collection.find_one = AsyncMock(return_value={"_id": ObjectId(task_id), "name": "Task 1"})

        task = await self.repo.get_task(task_id)

        self.assertEqual(task.name, "Task 1")

    async def test_get_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.get_task(str(ObjectId()))

    async def test_delete_task_success(self):
        task_id = str(ObjectId())
        self.mock_collection.find_one = AsyncMock(return_value={"_id": ObjectId(task_id)})
        self.mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))

        result = await self.repo.delete_task(task_id)
        self.assertTrue(result)

    async def test_delete_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.delete_task(str(ObjectId()))

    async def test_create_task_returns_task(self):
        new_task = CreateTaskModel(name="Test task", description="desc", deadline=date.today(), priority=None)

        inserted_id = ObjectId()
        self.mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=inserted_id))
        self.mock_collection.find_one = AsyncMock(return_value={"_id": inserted_id, "name": "Test task"})

        task = await self.repo.create_task(new_task)

        self.assertEqual(task.name, "Test task")

    async def test_edit_task_success(self):
        task_id = str(ObjectId())
        existing_task = {"_id": ObjectId(task_id), "name": "Old name", "priority": TaskPriority.medium, "deadline": None, "done": False}
        self.mock_collection.find_one = AsyncMock(side_effect=[existing_task, existing_task])
        self.mock_collection.replace_one = AsyncMock(return_value=None)

        edit_data = EditTaskModel(name="New name", description=None, done=True, priority=None, deadline=None)

        task = await self.repo.edit_task(edit_data, task_id)

        self.assertIsNotNone(task)

    async def test_edit_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.edit_task(EditTaskModel(name=None, description=None, done=None, priority=None, deadline=None), str(ObjectId()))

    async def test_get_list_pagination_error(self):
        # Мок цепочку вызовов find().sort().skip().limit().to_list()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        self.mock_collection.find.return_value = mock_cursor
        self.mock_collection.count_documents = AsyncMock(return_value=10)

        with self.assertRaises(PaginationError):
            await self.repo.get_list(OrderingType.ascending, Ordering.byPriority, page_size=5, page_num=0)

if __name__ == "__main__":
    unittest.main()