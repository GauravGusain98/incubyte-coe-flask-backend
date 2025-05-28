from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Date, text
from sqlalchemy.orm import relationship
from .base import db, TimestampMixin
import enum

class PriorityEnum(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class StatusEnum(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class Task(db.Model, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    due_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=True)
    priority = Column(Enum(PriorityEnum, name="priority_enum"), nullable=False, server_default=text("'low'"))
    status = Column(Enum(StatusEnum, name="status_enum"), nullable=False, server_default=text("'pending'"))

    assignee = relationship("User", back_populates="tasks", foreign_keys=[assignee_id], passive_deletes=True)
    created_by = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id], passive_deletes=True)
