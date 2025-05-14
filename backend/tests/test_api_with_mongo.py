"""Use only with correct mongo db service on localhost:27017"""

"""use pytest .\ests\est_api_with_mongo.py -s -k asyncio """

'''Just don't this shit don't want to work with async in normal ways'''

from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from fastapi import Response
import httpx
import pytest

import pytest_asyncio

from unittest.mock import AsyncMock

from data.taskModel import *
from data.requestBodies import *
from data.responseBodies import *
from common.exceptions import *

from domain.TasksRepository import TasksRepository

from bson import ObjectId
from datetime import datetime, date

from os import environ

mock_create_time = datetime.today()

environ["MONGO_URI"] = "mongodb://admin:pass@localhost:27017/database?authSource=admin&retryWrites=true&w=majority"
environ["DATABASE"] = "database"
environ["COLLECTION"] = "task"

from main import app, get_tasks_repository
import motor.motor_asyncio

seeding_count = 10
priorities = [TaskPriority.low, TaskPriority.medium, TaskPriority.high, TaskPriority.critical]
tasks = [
        Task( 
            name=f"test task num {i}",
            description=f"test task desc {i}",
            create_time=datetime.combine(date=datetime.today().date(), time=datetime.min.time()),
            deadline= (datetime.combine(date=datetime.today().date().replace(day=datetime.today().day + i % 3 - 2), time=datetime.min.time())) if i % 3 != 0 else None,
            priority=priorities[i % len(priorities)],
            done=(i % 2 == 0)
            )
        for i in range(seeding_count)
    ]

tasks_ids = []

async def get_id(): 
    collect = motor.motor_asyncio.AsyncIOMotorClient(environ["MONGO_URI"])[environ["DATABASE"]][environ["COLLECTION"]]
    return list(map(lambda x: x["_id"], (await collect.find({}).to_list())))

@pytest.fixture
async def seeding(repo: TasksRepository):
    global tasks_ids
    collection = repo.collection
    await collection.delete_many({})

    res = await collection.insert_many(map(lambda x: x.model_dump(), tasks))
    tasks_ids = res.inserted_ids
    print("!" * 200)
    print(tasks_ids)

@pytest.fixture
async def tasks_repository():
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(environ["MONGO_URI"])
    repo = TasksRepository(mongodb_client, environ["DATABASE"], environ["COLLECTION"])
    await seeding(repo)

    yield repo

    await repo.close()

@pytest_asyncio.fixture
async def cli(tasks_repository):
    app.dependency_overrides[get_tasks_repository] = lambda: tasks_repository
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

"""Base tests of incorrect path and method (404 and 405)"""

@pytest.mark.anyio
async def test_incorrect_path():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get("/incorrect")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_method_not_allowed():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.post("/tasks/all")
    assert response.status_code == 405

"""Success tests of all end points with async default parameters (query/path)"""

@pytest.mark.anyio
async def test_get_all_success():
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get("/tasks/all")
    assert response.status_code == 200
    print(response.json())
    #assert response.json()

@pytest.mark.anyio
async def test_get_list_success():
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get("/tasks/list", params={})

    assert response.status_code == 200
    #assert response.json() == expect

@pytest.mark.anyio
async def test_get_single_task_success():
    
    test_id = (await get_id())[0]

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get(f"/tasks/{test_id}")

    assert response.status_code == 200
    #assert response.json() == expect

@pytest.mark.anyio
async def test_delete_task_success():
    
    test_id = (await get_id())[0]

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.delete(f"/tasks/{test_id}")

    assert response.status_code == 200
    #assert response.json() == expect

@pytest.mark.anyio
async def test_put_task_success():
    
    test_id = (await get_id())[0]
    edit_data = EditTaskModel()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.put(f"/tasks/{test_id}", json=edit_data.model_dump())

    assert response.status_code == 200
    #assert response.json() == expect


"""Tests for simple exceptions (Not found and pagination error) on tasks. 
Because of middleware we need only one check for each"""

@pytest.mark.anyio
async def test_get_task_not_found():
    new_id = str(ObjectId())

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get(f"/tasks/{new_id}")

    expect = "task not found"

    assert response.status_code == 404
    assert response.json() == expect

@pytest.mark.anyio
async def test_get_pagiantion_exception():

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
        response = await cli.get(f"/tasks/list", params={})

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

# @pytest.mark.anyio
# @pytest.mark.parametrize("data", test_data)
# async def test_get_list_validation(data):
#     async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
#         response = await cli.get("/tasks/list", params=data["input"])
#     assert response.status_code == data["expect"]["status"]

#create model
correct = {
    'id': str(tasks[0].id), 
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
            } if i < TaskPriority.critical or i > TaskPriority.low else None
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

# @pytest.mark.anyio
# @pytest.mark.parametrize("data", test_data)
# async def test_create_task_validation(data):

#     async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
#         response = await cli.post("/tasks", json=data["input"])
#     #print("data", data)
#     print(response.json())

#     assert response.status_code == data["expect"]["status"]
#     #assert data["expect"]["status"] == 200 or response.json() == jsonable_encoder(data["expect"]["data"])

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

# @pytest.mark.anyio
# @pytest.mark.parametrize("data", test_data)
# async def test_edit_task_validation(data):
    
#     test_id = str((await collection.find_one({}))["_id"])
#     async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cli:
#         response = await cli.put(f"/tasks/{test_id}", json=data["input"])
#     #print("data", data)
#     print(response.json())

#     assert response.status_code == data["expect"]["status"]
#     #assert response.json() == jsonable_encoder(data["expect"]["data"])