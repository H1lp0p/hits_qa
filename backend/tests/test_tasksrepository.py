import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from bson import ObjectId
import datetime

from common.exceptions import TaskNotFound, PaginationError
from data.taskModel import Task, TaskPriority
from data.requestBodies import OrderingType, Ordering
from data.requestBodies import CreateTaskModel, EditTaskModel

class TestTasksRepository(unittest.IsolatedAsyncioTestCase):

    @staticmethod
    def to_task(data: dict) -> Task:
        data["_id"] = str(data["_id"])
        task = Task(**data)
        return task

    def setUp(self):
        #Импорт тут для корректной работы patch
        from domain.TasksRepository import TasksRepository

        # Мок клиента и коллекции
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        # Настраиваем доступ client[db][collection]
        self.mock_client.__getitem__.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_collection

        self.repo = TasksRepository(client=self.mock_client, datatabase_name="test_db", collection_name="test_collection")
        self.repo.collection = self.mock_collection

        #погенерим таски
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

        self.test_tasks = testTasks

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_get_all_tasks(self, mock_to_task):
        # Мок find().to_list()
        self.mock_collection.find.return_value.to_list = AsyncMock(return_value=self.test_tasks)

        tasks = await self.repo.get_all()

        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), len(self.test_tasks))
        self.assertEqual(tasks[0].name, self.test_tasks[0]["name"])

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_get_list_success(self, mock_to_task):

        page = 1
        size = 3

        # Мокаем цепочку find().sort().skip().limit().to_list()
        mock_query = MagicMock()
        mock_query.sort.return_value = mock_query
        mock_query.skip.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.to_list = AsyncMock(return_value=self.test_tasks[(page - 1) * size : page * size])
        self.mock_collection.find.return_value = mock_query
        self.mock_collection.count_documents = AsyncMock(return_value=3)

        tasks, count = await self.repo.get_list(OrderingType.ascending, Ordering.byPriority, page_size=size, page_num=page)
        self.assertEqual(count, size)
        self.assertEqual(len(tasks), size)
        self.assertTrue(all(isinstance(t, Task) for t in tasks))

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_get_list_pagination_error(self, mock_to_task):
        self.mock_collection.count_documents = AsyncMock(return_value=3)
        mock_query = MagicMock()
        mock_query.sort.return_value = mock_query
        self.mock_collection.find.return_value = mock_query

        # page_size <= 0
        with self.assertRaises(PaginationError):
            await self.repo.get_list(OrderingType.ascending, Ordering.byPriority, page_size=0, page_num=1)
        # page_num <= 0
        with self.assertRaises(PaginationError):
            await self.repo.get_list(OrderingType.ascending, Ordering.byPriority, page_size=2, page_num=0)
        # page_num слишком большой
        with self.assertRaises(PaginationError):
            await self.repo.get_list(OrderingType.ascending, Ordering.byPriority, page_size=2, page_num=3)

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_get_list_sorting(self, mock_to_task):
        mock_query = MagicMock()
        mock_query.sort.return_value = mock_query
        mock_query.skip.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.to_list = AsyncMock(return_value=self.test_tasks)
        self.mock_collection.find.return_value = mock_query
        self.mock_collection.count_documents = AsyncMock(return_value=1)

        await self.repo.get_list(OrderingType.ascending, Ordering.byPriority)
        mock_query.sort.assert_called_with("priority", 1)
        await self.repo.get_list(OrderingType.descending, Ordering.byDeadline)
        mock_query.sort.assert_called_with("deadline", -1)

    
    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_create_task_success(self, mock_to_task):
        create_model = CreateTaskModel(
            name="Test task !2 !before 01.01.2025",
            description="desc",
            deadline=None,
            priority=None
        )
        fake_id = ObjectId()
        result_task = {
            "_id": str(fake_id),
            "name": "Test task !2 !before 01.01.2025",
            "description": "desc",
            "create_time": str(datetime.datetime.today()),
            "priority": TaskPriority.medium,
            "done": False
        }

        data_to_insert = {
            'id': None,
            'name': 'Test task !2 !before 01.01.2025', 
            'description': 'desc', 
            'deadline': datetime.datetime(2025, 1, 1, 0, 0), 
            'create_time': datetime.datetime(2025, 5, 5, 0, 0), 
            'redacted_time': None,
            'priority': TaskPriority.medium, 
            'done': False
            }

        self.mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=fake_id))
        self.mock_collection.find_one = AsyncMock(return_value=result_task)

        task = await self.repo.create_task(create_model)

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, create_model.name)
        self.mock_collection.insert_one.assert_awaited_with(data_to_insert)
        self.mock_collection.find_one.assert_awaited_with({"_id": fake_id})

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_create_task_parameters_priority(self, mock_to_task):
        create_model = CreateTaskModel(
            name="Test task !2 !before 01.01.2025",
            description="desc",
            deadline=datetime.date.today(),
            priority=TaskPriority.critical
        )
        fake_id = ObjectId()

        result_task = {
            "_id": str(fake_id),
            "name": "Test task !2 !before 01.01.2025",
            "description": "desc",
            "create_time": datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time()),
            "priority": create_model.priority,
            'deadline': datetime.datetime.combine(create_model.deadline, datetime.datetime.min.time()),
            "done": False
        }

        data_to_insert = {
            'id': None, 
            'name': create_model.name, 
            'description': create_model.description, 
            'deadline': datetime.datetime.combine(create_model.deadline, datetime.datetime.min.time()), 
            'create_time': datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time()), 
            'redacted_time': None, 
            'priority': create_model.priority, 
            'done': False
        }

        self.mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=fake_id))
        self.mock_collection.find_one = AsyncMock(return_value=result_task)

        task = await self.repo.create_task(create_model)

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, create_model.name)
        self.assertEqual(task.priority, create_model.priority)
        self.assertEqual(task.deadline.date(), create_model.deadline)
        self.mock_collection.insert_one.assert_awaited_with(data_to_insert)
        self.mock_collection.find_one.assert_awaited_with({"_id": fake_id})

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_edit_task(self, mock_to_task):
        edit_model = EditTaskModel(
            name="Test task !2 !before 01.01.2025",
            description="desc",
            deadline=None,
            priority=None
        )
        
        first_task = {
                "_id": str(ObjectId()),
                "name": f"test task num 0",
                "description": f"description 0",
                "create_time": str(datetime.datetime.today()),
                "done": False
            }

        edited_task = {
                "_id": first_task["_id"],
                "name": "Test task !2 !before 01.01.2025",
                "description": f"desc",
                "create_time": str(datetime.datetime.today()),
                "deadline": datetime.datetime(2025, 1, 1, 0, 0),
                "priority": TaskPriority.medium,
                "done": False
        }

        fake_id = first_task["_id"]

        self.mock_collection.replace_one = AsyncMock(return_value=MagicMock(modified_count=1))
        self.mock_collection.find_one = AsyncMock(side_effect=[first_task, edited_task])

        task = await self.repo.edit_task(edit_model, fake_id)

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, edit_model.name)
        self.mock_collection.replace_one.assert_awaited()
        self.mock_collection.find_one.assert_awaited_with({"_id": ObjectId(fake_id)})

    @patch("common.mapper.Mapper.to_task", side_effect=to_task)
    async def test_edit_task_parameters_priority(self, mock_to_task):
        edit_model = EditTaskModel(
            name="Test task !2 !before 01.01.2022",
            description="desc",
            deadline=datetime.date.today(),
            priority=TaskPriority.critical
        )
        
        first_task = {
                "_id": str(ObjectId()),
                "name": f"test task num 0",
                "description": f"description 0",
                "create_time": str(datetime.datetime.today()),
                "done": False
            }

        edited_task = {
                "_id": first_task["_id"],
                "name": "Test task !2 !before 01.01.2022",
                "description": f"desc",
                "create_time": str(datetime.datetime.today()),
                "deadline": datetime.datetime.combine(edit_model.deadline, datetime.datetime.min.time()),
                "priority": edit_model.priority,
                "done": False
        }

        fake_id = first_task["_id"]

        self.mock_collection.replace_one = AsyncMock(return_value=MagicMock(modified_count=1))
        self.mock_collection.find_one = AsyncMock(side_effect=[first_task, edited_task])

        task = await self.repo.edit_task(edit_model, fake_id)

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, edit_model.name)
        self.mock_collection.replace_one.assert_awaited()
        self.mock_collection.find_one.assert_awaited_with({"_id": ObjectId(fake_id)})

    def test_format_task_name_priority_and_deadline(self):
        priority, deadline = self.repo.format_task_name("Some task !1 !before 01.01.2025")
        self.assertEqual(priority, TaskPriority.low)
        self.assertEqual(deadline, datetime.date(2025, 1, 1))

    def test_format_task_name_only_priority(self):
        priority, deadline = self.repo.format_task_name("Some task !4")
        self.assertEqual(priority, TaskPriority.critical)
        self.assertIsNone(deadline)

    def test_format_task_name_only_deadline(self):
        priority, deadline = self.repo.format_task_name("Some !before 15-12-2024")
        self.assertIsNone(priority)
        self.assertEqual(deadline, datetime.date(2024, 12, 15))

    def test_format_task_name_no_priority_deadline(self):
        priority, deadline = self.repo.format_task_name("Just a task")
        self.assertIsNone(priority)
        self.assertIsNone(deadline)

    def test_format_task_name_incorrect_deadline(self):
        with self.assertRaises(ValueError):
            priority, deadline = self.repo.format_task_name("Just a task !before 32.01.2025")


    async def test_get_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.get_task(str(ObjectId()))

    async def test_delete_task_success(self):
        task_id = str(ObjectId())
        self.mock_collection.find_one = AsyncMock(return_value={"_id": ObjectId(task_id)})
        self.mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))

        result = await self.repo.delete_task(task_id)
        self.mock_collection.find_one.assert_awaited_with({"_id": ObjectId(task_id)})
        self.mock_collection.delete_one.assert_awaited_with({"_id": ObjectId(task_id)})
        self.assertTrue(result)

    async def test_delete_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.delete_task(str(ObjectId()))

    async def test_edit_task_not_found_raises(self):
        self.mock_collection.find_one = AsyncMock(return_value=None)
        with self.assertRaises(TaskNotFound):
            await self.repo.edit_task(EditTaskModel(name=None, description=None, done=None, priority=None, deadline=None), str(ObjectId()))

if __name__ == "__main__":
    unittest.main()