import pytest
from flask import Flask, Request as request
from jose import jwt
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request as WerkzeugRequest
from coe.services import auth_service
from coe.schemas.user import CreateUser
from coe.services.user_service import create_user
from config import Config as settings
from faker import Faker

faker = Faker()
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def create_test_user(db):
    data = CreateUser(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        password="testpass"
    )
    user = create_user(data, db)
    return user


def test_create_access_token_contains_user_id():
    data = {"user_id": 1}
    token = auth_service.create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user_id"] == 1
    assert "exp" in payload


def test_create_refresh_token_has_type_refresh():
    data = {"user_id": 1}
    token = auth_service.create_refresh_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user_id"] == 1
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_get_current_user(app, db):
    user = create_test_user(db)
    token = auth_service.create_access_token({"user_id": user.id})

    # Simulate a Flask request context with the token in cookies
    builder = EnvironBuilder(path="/", headers={"Cookie": f"access_token={token}"})
    env = builder.get_environ()
    req = WerkzeugRequest(env)

    with app.test_request_context(environ_base=env):
        current_user = auth_service.get_current_user()

    assert current_user.id == user.id
    assert current_user.email == user.email


def test_get_current_user_invalid_token(app, db):
    builder = EnvironBuilder(path="/", headers={"Cookie": "access_token=invalid-token"})
    env = builder.get_environ()

    with app.test_request_context(environ_base=env):
        with pytest.raises(Exception) as exc:
            auth_service.get_current_user()

        assert "401" in str(exc.value) or hasattr(exc.value, "status_code") and exc.value.status_code == 401
