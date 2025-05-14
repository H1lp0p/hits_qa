
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from fastapi import Response
import pytest

from unittest.mock import AsyncMock

from data.taskModel import *
from data.requestBodies import *
from data.responseBodies import *
from common.exceptions import *

from domain.TasksRepository import TasksRepository

from bson import ObjectId
from datetime import datetime, date

from os import environ

mock_id = str(ObjectId())
mock_create_time = datetime.today()


environ["MONGO_URI"] = "test_uri"
environ["DATABASE"] = "test_db"
environ["COLLECTION"] = "test_collection"

from main import app, get_tasks_repository

"""run with pytest .\tests\test_api.py -s"""

repo = AsyncMock()

@pytest.fixture
def cli():
    app.dependency_overrides[get_tasks_repository] = lambda: repo
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()

"""Base tests of incorrect path and method (404 and 405)"""

def test_incorrect_path(cli):
    response = cli.get("/incorrect")
    assert response.status_code == 404

def test_method_not_allowed(cli):
    response = cli.post("/tasks/all")
    assert response.status_code == 405

"""Success tests of all end points with default parameters (query/path)"""

def test_get_all_success(cli):

    test_task_info = TaskInfo(
        id=mock_id,
        name="test task",
        create_time=mock_create_time.date(),
        done=False
    )

    repo.get_all.return_value = [test_task_info]

    expect = jsonable_encoder([test_task_info])

    response = cli.get("/tasks/all")
    assert response.status_code == 200
    assert response.json() == expect

def test_get_list_success(cli):

    test_task = Task(
        _id=mock_id,
        name="test task",
        create_time=mock_create_time,
        done=False
    )

    test_task_info = TaskInfo(
        id=mock_id,
        name="test task",
        create_time=mock_create_time.date(),
        done=False
    )

    repo.get_list.return_value = ([test_task], 1)
    

    res_list = TaskList(
        tasks=[test_task_info],
        pagination= Pagination(
            items_count=1,
            page=1,
            page_size=5
        )
    )

    expect = jsonable_encoder(res_list)

    response = cli.get("/tasks/list", params={})

    repo.get_list.assert_called_with(OrderingType.ascending, Ordering.byPriority, 5, 1)

    assert response.status_code == 200
    assert response.json() == expect

def test_get_single_task_success(cli):

    test_task = Task(
        _id=mock_id,
        name="test task",
        create_time=mock_create_time,
        done=False
    )

    test_task_info = TaskInfo(
        id=mock_id,
        name="test task",
        create_time=mock_create_time.date(),
        done=False
    )

    expect = jsonable_encoder(test_task_info)
    repo.get_task.return_value = test_task

    response = cli.get(f"/tasks/{mock_id}")
    
    repo.get_task.assert_called_with(mock_id)

    assert response.status_code == 200
    assert response.json() == expect

def test_delete_task_success(cli):
    repo.delete_task.return_value = True

    expect = jsonable_encoder(True)

    response = cli.delete(f"/tasks/{mock_id}")

    repo.delete_task.assert_called_with(mock_id)

    assert response.status_code == 200
    assert response.json() == expect

def test_put_task_success(cli):

    test_task = Task(
        _id=mock_id,
        name="test task",
        create_time=mock_create_time,
        done=False
    )

    test_task_info = TaskInfo(
        id=mock_id,
        name="test task",
        create_time=mock_create_time.date(),
        done=False
    )

    edit_data = EditTaskModel()

    repo.edit_task.return_value = test_task

    expect = jsonable_encoder(test_task_info)

    response = cli.put(f"/tasks/{mock_id}", json=edit_data.model_dump())

    repo.edit_task.assert_called_with(edit_data, mock_id)

    assert response.status_code == 200
    assert response.json() == expect


"""Tests for simple exceptions (Not found and pagination error) on tasks. 
Because of middleware we need only one check for each"""

def test_get_task_not_found(cli):
    new_id = str(ObjectId())

    repo.get_task.side_effect = TaskNotFound()

    response = cli.get(f"/tasks/{new_id}")

    expect = "task not found"

    assert response.status_code == 404
    assert response.json() == expect

def test_get_pagiantion_exception(cli):
    repo.get_list.side_effect = PaginationError()

    response = cli.get(f"/tasks/list", params={})

    expect = "incorrect pagination data"

    assert response.status_code == 400
    assert response.json() == expect


"""Now we will test validation errors"""

#query params and it's validation (pagination + ordering)
test_data = [
    {
        "input": {
            "ordering": "priority",
            "ordering_type": "asc",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 200
        }
    },
    {
        "input": {
            "ordering": "priority",
            "ordering_type": "desc",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 200
        }
    },
        {
        "input": {
            "ordering": "priority",
            "ordering_type": "ascending",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 422
        }
    },
    {
        "input": {
            "ordering": "deadline",
            "ordering_type": "asc",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 200
        }
    },
    {
        "input": {
            "ordering": "deeeeeeeeeeeeeeaadline",
            "ordering_type": "desc",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 422
        }
    },
    {
        "input": {
            "ordering": "create_time",
            "ordering_type": "asc",
            "page": "1",
            "page_size": "5"
        }, 
        "expect": {
            "status": 422
        }
    },
    {
        "input": {
            "ordering": "create_time",
            "ordering_type": "asc",
            "page": "first",
            "page_size": "5"
        }, 
        "expect": {
            "status": 422
        }
    },
    {
        "input": {
            "ordering": "create_time",
            "ordering_type": "asc",
            "page": "1",
            "page_size": "all"
        }, 
        "expect": {
            "status": 422
        }
    }
]

@pytest.mark.parametrize("data", test_data)
def test_get_list_validation(data, cli):
    repo.get_list.side_effect = None
    response = cli.get("/tasks/list", params=data["input"])
    assert response.status_code == data["expect"]["status"]

#create model
correct = {
    'id': mock_id, 
    'name': 'result task', 
    'description': None, 
    'deadline': None, 
    'create_time': '2025-05-12', 
    'redacted_time': None, 
    'status': 'active', 
    'priority': 2, 
    'done': False
}

test_data = [
    {
        "input" : CreateTaskModel(
            name="task"
            ).model_dump(),
        "expect": {
            "status": 200,
            "data": correct
        }
    },
    {
        "input" : {
            "name": ""
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'string_too_short', 
                        'loc': ['body', 'name'], 
                        'msg': 'String should have at least 4 characters', 
                        'input': '', 
                        'ctx': {'min_length': 4}
                    }
                ]
            }            
        }
    },
    {
        "input" : {},
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'missing', 
                        'loc': ['body', 'name'], 
                        'msg': 'Field required',
                        'input': {}
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": str(mock_create_time.date()),
            "priority": TaskPriority.medium
        },
        "expect": {
            "status": 200,
            "data": correct
        }
    }
] 

"""all about priority"""

test_data += [
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": str(mock_create_time.date()),
            "priority": i
        },
        "expect": {
            "status": 200 if i >= TaskPriority.critical and i <= TaskPriority.low else 422,
            "data": {
                'detail': [
                    {
                        'type': 'enum', 
                        'loc': ['body', 'priority'], 
                        'msg': 'Input should be 3, 2, 1 or 0', 
                        'input': i, 
                        'ctx': {'expected': '3, 2, 1 or 0'}
                    }
                ]
            } if i < TaskPriority.critical or i > TaskPriority.low else correct
        }
    } for i in range(TaskPriority.critical - 1, TaskPriority.low + 2)]

"""incorrect deadline"""

test_data += [
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "yesterday",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, input is too short', 
                        'input': 'yesterday', 
                        'ctx': {'error': 'input is too short'}
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "32-01-2025",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, invalid character in year', 
                        'input': '32-01-2025', 
                        'ctx': {'error': 'invalid character in year'}
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "01.01.2025",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, invalid character in year', 
                        'input': '01.01.2025', 
                        'ctx': {'error': 'invalid character in year'}
                    }
                ]
            }
        }
    }
]

@pytest.mark.parametrize("data", test_data)
def test_create_task_validation(data, cli):
    repo.create_task.return_value = Task(_id=mock_id, name="result task", create_time=mock_create_time, done=False)

    response = cli.post("/tasks", json=data["input"])
    #print("data", data)
    print(response.json())

    assert response.status_code == data["expect"]["status"]
    assert response.json() == jsonable_encoder(data["expect"]["data"])

#edit model
test_data = [
    {
        "input" : EditTaskModel(
            name="task"
            ).model_dump(),
        "expect": {
            "status": 200,
            "data": correct
        }
    },
    {
        "input" : {
            "name": ""
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'string_too_short', 
                        'loc': ['body', 'name'], 
                        'msg': 'String should have at least 4 characters', 
                        'input': '', 
                        'ctx': {'min_length': 4}
                    }
                ]
            }            
        }
    },
    {
        "input" : {},
        "expect": {
            "status": 200,
            "data": correct
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": str(mock_create_time.date()),
            "priority": TaskPriority.medium
        },
        "expect": {
            "status": 200,
            "data": correct
        }
    }
] 

"""all about priority"""

test_data += [
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": str(mock_create_time.date()),
            "priority": i
        },
        "expect": {
            "status": 200 if i >= TaskPriority.critical and i <= TaskPriority.low else 422,
            "data": {
                'detail': [
                    {
                        'type': 'enum', 
                        'loc': ['body', 'priority'], 
                        'msg': 'Input should be 3, 2, 1 or 0', 
                        'input': i, 
                        'ctx': {'expected': '3, 2, 1 or 0'}
                    }
                ]
            } if i < TaskPriority.critical or i > TaskPriority.low else correct
        }
    } for i in range(TaskPriority.critical - 1, TaskPriority.low + 2)]

"""incorrect deadline"""

test_data += [
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "yesterday",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, input is too short', 
                        'input': 'yesterday', 
                        'ctx': {'error': 'input is too short'}
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "32-01-2025",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, invalid character in year', 
                        'input': '32-01-2025', 
                        'ctx': {'error': 'invalid character in year'}
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "name": "test name",
            "description": "test desc",
            "deadline": "01.01.2025",
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'date_from_datetime_parsing', 
                        'loc': ['body', 'deadline'], 
                        'msg': 'Input should be a valid date or datetime, invalid character in year', 
                        'input': '01.01.2025', 
                        'ctx': {'error': 'invalid character in year'}
                    }
                ]
            }
        }
    }
]

"""parameter 'done' """

test_data += [
    {
        "input" : {
            "done": False
        },
        "expect": {
            "status": 200,
            "data": correct
        }
    },
    {
        "input" : {
            "done": "not done yet"
        },
        "expect": {
            "status": 422,
            "data": {
                'detail': [
                    {
                        'type': 'bool_parsing', 
                        'loc': ['body', 'done'], 
                        'msg': 'Input should be a valid boolean, unable to interpret input', 
                        'input': 'not done yet'
                    }
                ]
            }
        }
    },
    {
        "input" : {
            "done": 0,
        },
        "expect": {
            "status": 200,
            "data": correct
        }
    },
]

@pytest.mark.parametrize("data", test_data)
def test_edit_task_validation(data, cli):
    repo.edit_task.return_value = Task(_id=mock_id, name="result task", create_time=mock_create_time, done=False)

    response = cli.put(f"/tasks/{mock_id}", json=data["input"])
    #print("data", data)
    print(response.json())

    assert response.status_code == data["expect"]["status"]
    assert response.json() == jsonable_encoder(data["expect"]["data"])