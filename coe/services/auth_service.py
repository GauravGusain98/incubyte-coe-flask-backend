from datetime import datetime, timedelta
from jose import jwt
from functools import wraps
from flask import request
from werkzeug.exceptions import Unauthorized
from coe.models import User
from jose import JWTError
from coe.models.base import db
from config import Config as settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: int = payload.get("user_id")
    return user_id


def get_current_user():
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise Unauthorized("Not authenticated")

    try:
        user_id = decode_token(access_token)
    except Exception:
        raise Unauthorized("Invalid or expired token")

    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise Unauthorized("User not found")

    return user

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        get_current_user()
        return fn(*args, **kwargs)
    return wrapper
