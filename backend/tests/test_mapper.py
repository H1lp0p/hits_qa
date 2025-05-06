import unittest
from common.mapper import Mapper
from data.taskModel import *
import datetime
from bson import ObjectId

class TestMapper(unittest.TestCase):
    def setUp(self):
        self.map = Mapper()
    

    def test_map_to_task_success(self):
        mock_id = ObjectId()
        data = {
            "_id": str(mock_id),
            "name": "Test task !2 !before 01.01.2025",
            "description": "desc",
            "create_time": str(datetime.datetime.today()),
            "priority": TaskPriority.medium,
            "done": False
        }

        expectedTask = Task(
            **data,
            id=str(mock_id)
        )

        result = self.map.to_task(data)
        print("!!!!!!!!!!!!!!!", result)

        self.assertEqual(result, expectedTask)


if __name__ == "__main__":
    unittest.main()