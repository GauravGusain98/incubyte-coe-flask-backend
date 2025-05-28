from sqlalchemy import Column, DateTime, func
from flask_sqlalchemy import SQLAlchemy
from coe.utils.format_utils import to_camel
from pydantic import BaseModel

db = SQLAlchemy()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class CamelModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True, 
    }