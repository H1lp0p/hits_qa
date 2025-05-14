import unittest
from common.mapper import Mapper
from data.responseBodies import TaskInfo, TaskStatus
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
    
    @staticmethod
    def correctStatus(deadline: datetime.datetime, done: bool):
        today = datetime.datetime.today()
        is_missed = deadline.date() >= today.date()
        if done:
            return TaskStatus.late if is_missed else TaskStatus.completed
        else:
            return TaskStatus.overdue if is_missed else TaskStatus.completed

            

    def test_map_to_info(self):
        mock_id = ObjectId()
        attrs = [
            (
                Task(
                    _id=str(mock_id),
                    name="name",
                    description="desc",
                    done= False,
                    create_time=datetime.datetime.today(),
                    deadline=datetime.datetime.today().replace(day=datetime.datetime.today().day + 2)
                    ),
                TaskStatus.active
            ),
            (
                Task(
                    _id=str(mock_id),
                    name="name",
                    description="desc",
                    done= True,
                    create_time=datetime.datetime.today(),
                    deadline=datetime.datetime.today().replace(day=datetime.datetime.today().day + 2)
                    ),
                TaskStatus.completed
            ),
            (
                Task(
                    _id=str(mock_id),
                    name="name",
                    description="desc",
                    done= False,
                    create_time=datetime.datetime.today(),
                    deadline=datetime.datetime.today().replace(day=datetime.datetime.today().day - 2)
                    ),
                TaskStatus.overdue
            ),
            (
                Task(
                    _id=str(mock_id),
                    name="name",
                    description="desc",
                    done= True,
                    create_time=datetime.datetime.today(),
                    deadline=datetime.datetime.today().replace(day=datetime.datetime.today().day - 2)
                    ),
                TaskStatus.late
            ) 
        ]
        
        for task, res in attrs:
            with self.subTest(task=task, res=res):
                rs = self.map.to_info(task)
                self.assertEqual(rs.status, res)



if __name__ == "__main__":
    unittest.main()