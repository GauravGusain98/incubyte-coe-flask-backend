from pydantic import Field, constr, conint, field_validator
from coe.models.base import CamelModel
from typing import Optional, List, Literal
from enum import Enum
from datetime import date, datetime

NameStr = constr(strip_whitespace=True, min_length=1, max_length=128)
TextStr = constr(strip_whitespace=True, min_length=0, max_length=20000)
PasswordStr = constr(min_length=8, max_length=128)
ID = conint(gt=0)

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class PaginationSchema(CamelModel):
    page: int
    limit: int
    count: int
    total: int
    total_pages: int

### Request Schemas

class TaskFilters(CamelModel):
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    search: Optional[str] = None

class TaskSort(CamelModel):
    sort_by: Optional[str] = None
    sort_order: Optional[Literal["asc", "desc"]] = None

class CreateTaskRequestSchema(CamelModel):
    name: NameStr = Field(..., description="First name of the task")
    description: str = Field(..., description="Description of the task")
    assignee_id: Optional[ID] = None
    due_date: date
    start_date: Optional[date] = None
    priority: Optional[PriorityEnum] = None

class UpdateTaskRequestSchema(CamelModel):
    name: Optional[NameStr] = Field(default=None)
    description: Optional[str] = Field(default=None)
    assignee_id: Optional[ID] = Field(default=None)
    due_date: Optional[date] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None

    @field_validator('name', 'description', 'due_date', mode='before')
    @classmethod
    def not_none_if_present(cls, value, field):
        if value is None:
            # Raise error only if the field was actually passed with value null
            raise ValueError(f"{field.field_name} cannot be null")
        return value

### Response Schemas
class CreateTaskResponseSchema(CamelModel):
    message: str
    task_id: int

class UpdateTaskResponseSchema(CamelModel):
    message: str

class GetTaskResponseSchema(CamelModel):
    id: int
    name: str
    description: str
    created_by_id: int
    assignee_id: Optional[int] = None
    due_date: date
    start_date: Optional[date] = None
    priority: PriorityEnum
    status: StatusEnum
    created_at: datetime
    updated_on: Optional[datetime]

class GetTaskListResponseSchema(CamelModel):
    message: str
    tasks: List[GetTaskResponseSchema]
    pagination: PaginationSchema

class UpdateTaskResponseSchema(CamelModel):
    message: str

class DeleteTaskResponseSchema(CamelModel):
    message: str

class ErrorResponse(CamelModel):
    detail: str