from datetime import date, timedelta
from faker import Faker
import pytest

fake = Faker()


@pytest.fixture
def auth_client(client):
    """Creates and authenticates a user, returning a client with the auth cookie set."""
    email = fake.unique.email()
    password = "secret123"

    # Register the user
    register_response = client.post("/user/register", json={
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": email,
        "password": password
    })
    assert register_response.status_code == 201

    # Login and extract token
    login_response = client.post("/user/login", json={"email": email, "password": password})
    assert login_response.status_code == 200

    token = login_response.json.get("accessToken")
    assert token is not None

    # Set the auth token manually (assuming you’re using cookies for auth)
    client.set_cookie(key="access_token", value=token)
    return client


def test_create_task(auth_client):
    payload = {
        "name": "Test Task",
        "description": "Test task description",
        "dueDate": str(date.today() + timedelta(days=7)),
        "priority": "medium"
    }

    res = auth_client.post("/task/add", json=payload)
    assert res.status_code == 201
    res_data = res.get_json()
    assert res_data["message"] == "Task created successfully"
    assert "taskId" in res_data


def test_get_task_by_id(auth_client):
    payload = {
        "name": "Test Task Fetch",
        "description": "To fetch later",
        "dueDate": str(date.today() + timedelta(days=3)),
        "priority": "low"
    }
    create_res = auth_client.post("/task/add", json=payload)
    task_id = create_res.get_json()["taskId"]

    res = auth_client.get(f"/task/{task_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == payload["name"]


def test_get_non_existing_task(auth_client):
    res = auth_client.get("/task/999999")
    assert res.status_code == 404
    assert res.get_json()["detail"] == "Task not found"


def test_update_task(auth_client):
    create_payload = {
        "name": "Initial Task",
        "description": "Before update",
        "dueDate": str(date.today() + timedelta(days=3)),
        "priority": "low"
    }
    create_res = auth_client.post("/task/add", json=create_payload)
    task_id = create_res.get_json()["taskId"]

    update_payload = {
        "name": "Updated Task",
        "description": "After update",
        "dueDate": str(date.today() + timedelta(days=5)),
        "priority": "high"
    }
    res = auth_client.put(f"/task/{task_id}", json=update_payload)
    assert res.status_code == 200
    assert res.get_json()["message"] == "Task data updated successfully"


def test_delete_task(auth_client):
    payload = {
        "name": "Task to delete",
        "description": "Will be deleted",
        "dueDate": str(date.today() + timedelta(days=1))
    }
    task_id = auth_client.post("/task/add", json=payload).get_json()["taskId"]

    delete_res = auth_client.delete(f"/task/{task_id}")
    assert delete_res.status_code == 200
    assert delete_res.get_json()["message"] == "Task removed successfully"

    fetch_res = auth_client.get(f"/task/{task_id}")
    assert fetch_res.status_code == 404


def test_get_task_list(auth_client):
    for i in range(3):
        auth_client.post("/task/add", json={
            "name": f"Task {i}",
            "description": f"Description {i}",
            "dueDate": str(date.today() + timedelta(days=i)),
            "priority": "medium"
        })

    res = auth_client.get("/task/list?page=1&records_per_page=2")
    assert res.status_code == 200
    data = res.get_json()
    assert "tasks" in data
    assert "pagination" in data
    assert data["pagination"]["count"] == 2
