from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from .base import db, TimestampMixin
from .task import Task

class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False)

    tasks = relationship("Task", back_populates="assignee", foreign_keys=[Task.assignee_id])
    created_tasks = relationship("Task", back_populates="created_by", foreign_keys=[Task.created_by_id])
