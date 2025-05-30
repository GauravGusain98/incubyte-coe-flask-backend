import pytest
from faker import Faker

faker = Faker()

def register_user(client, password: str = "secret123"):
    user_data = {
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "email": faker.unique.email(),
        "password": password
    }
    response = client.post("/user/register", json=user_data)
    assert response.status_code == 201, "User registration failed"
    return response.get_json()["userId"], user_data["email"], user_data["password"]


def login_user(client, email: str, password: str):
    response = client.post("/user/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200, "Login failed"
    json_data = response.get_json()
    return json_data["accessToken"], json_data.get("refreshToken")


def test_register_user(client):
    user_data = {
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "email": faker.unique.email(),
        "password": "secret123"
    }
    response = client.post("/user/register", json=user_data)
    assert response.status_code == 201
    assert "userId" in response.get_json()


def test_login_user(client):
    _, email, password = register_user(client)
    response = client.post("/user/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "accessToken" in response.get_json()


def test_update_user_route(client):
    user_id, email, password = register_user(client, "update123")
    access_token, _ = login_user(client, email, "update123")

    update_data = {"firstName": faker.first_name()}
    response = client.put(
        f"/user/{user_id}",
        json=update_data,
        headers={"Cookie": f"access_token={access_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "User data updated successfully"


def test_delete_user_route(client):
    user_id, email, password = register_user(client, "toDelete123")
    access_token, _ = login_user(client, email, "toDelete123")

    response = client.delete(
        f"/user/{user_id}",
        headers={"Cookie": f"access_token={access_token}"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "User removed successfully"


def test_refresh_token(client):
    _, email, password = register_user(client, "refresh123")
    _, refresh_token = login_user(client, email, "refresh123")

    response = client.post(
        "/user/token/refresh",
        headers={"Cookie": f"refresh_token={refresh_token}"}
    )

    assert response.status_code == 200
    assert "accessToken" in response.get_json()
