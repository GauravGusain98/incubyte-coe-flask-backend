import pytest
from datetime import date
from faker import Faker

from coe.services import task_service
from coe.services.user_service import create_user
from coe.models.task import Task, PriorityEnum
from coe.schemas.user import CreateUser
from coe.schemas.task import (
    CreateTaskRequestSchema,
    UpdateTaskRequestSchema,
    TaskFilters,
    TaskSort
)

fake = Faker()

@pytest.fixture
def sample_user(db):
    user_data = CreateUser(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.unique.email(),
        password="testpassword"
    )
    return create_user(user_data, db)

@pytest.fixture
def sample_task(db, sample_user):
    task = Task(
        name="Sample Task",
        description="Sample description",
        created_by_id=sample_user.id,
        due_date=date(2025, 6, 1),
        start_date=date(2025, 5, 20),
        priority=PriorityEnum.medium
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def test_create_task(db, sample_user):
    task_data = CreateTaskRequestSchema(
        name="Test Task",
        description="A test description",
        assignee_id=None,
        due_date=date(2025, 6, 1),
        start_date=date(2025, 5, 20),
        priority=PriorityEnum.high
    )

    task = task_service.create_task(task_data, db, sample_user)

    assert task.id is not None
    assert task.name == task_data.name
    assert db.query(Task).filter_by(id=task.id).first() is not None

def test_find_task_by_id(db, sample_task):
    found_task = task_service.find_task_by_id(sample_task.id, db)

    assert found_task is not None
    assert found_task.id == sample_task.id
    assert found_task.name == sample_task.name

def test_get_tasks_list(db, sample_user):
    task1 = Task(name="Task 1", description="Test", created_by_id=sample_user.id,
                 due_date=date(2025, 6, 1), start_date=date(2025, 5, 20), priority=PriorityEnum.high)
    task2 = Task(name="Task 2", description="Test", created_by_id=sample_user.id,
                 due_date=date(2025, 6, 2), start_date=date(2025, 5, 21), priority=PriorityEnum.low)
    
    db.add_all([task1, task2])
    db.commit()

    filters = TaskFilters()
    sort = TaskSort(sort_by="id", sort_order="asc")

    tasks, total = task_service.get_tasks_list(db, filters, sort)

    assert isinstance(tasks, list)
    assert total >= 2
    assert all(isinstance(t, Task) for t in tasks)

def test_update_task_details(db, sample_task):
    update_data = UpdateTaskRequestSchema(
        name="Updated Name",
        description="Updated Description",
        assignee_id=None,
        due_date=date(2025, 6, 3),
        start_date=date(2025, 5, 22),
        priority=PriorityEnum.high
    )

    updated = task_service.update_task_details(sample_task.id, update_data, db)

    assert updated is True

    db.refresh(sample_task)
    assert sample_task.name == update_data.name
    assert sample_task.description == update_data.description
    assert sample_task.priority.value == update_data.priority.value

def test_update_task_details_not_found(db):
    update_data = UpdateTaskRequestSchema(
        name="Ghost Task",
        description="Should not exist",
        assignee_id=None,
        due_date=date(2025, 6, 3),
        start_date=date(2025, 5, 22),
        priority=PriorityEnum.low
    )

    result = task_service.update_task_details(99999, update_data, db)

    assert result is False

def test_remove_task_found(db, sample_task):
    result = task_service.remove_task(sample_task.id, db)

    assert result is True
    assert db.query(Task).filter_by(id=sample_task.id).first() is None

def test_remove_task_not_found(db):
    result = task_service.remove_task(99999, db)

    assert result is False
