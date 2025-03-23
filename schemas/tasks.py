from datetime import datetime
from typing import Iterable

import pytz
from pydantic import BaseModel, Field

from entities.categories import Category
from entities.tasks import Task
from enums.tasks import TaskStatusEnum
from schemas.categories import CategorySchema
from schemas.users import UserSchema


class TaskSchema(BaseModel):
    user: UserSchema
    title: str
    deadline: datetime
    status: TaskStatusEnum
    id: str | None = None
    categories: Iterable[CategorySchema] | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    description: str | None = Field(default=None)

    @classmethod
    def to_schema(cls, task: Task) -> "TaskSchema":
        return cls(
            user=UserSchema.to_schema(task.user),
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            created_at=task.created_at,
            completed_at=task.completed_at,
            status=TaskStatusEnum.from_value(task.status).value,
            id=task.id,
            categories=cls.get_categories(task.categories),
        )

    @classmethod
    def get_categories(
        cls, categories: Iterable[Category] | None
    ) -> Iterable[CategorySchema] | None:
        if categories:
            return [
                CategorySchema.to_schema(category) for category in categories
            ]
        return None


class TaskShortSchema(BaseModel):
    id: str
    title: str
    deadline: datetime
    created_at: datetime

    @classmethod
    def to_schema(cls, task: Task) -> "TaskShortSchema":
        return cls(
            id=task.id,
            title=task.title,
            deadline=cls.get_correct_tz_date(task.deadline),
            created_at=cls.get_correct_tz_date(task.created_at),
        )

    @classmethod
    def get_correct_tz_date(cls, date: datetime):
        tz = pytz.timezone("America/Adak")
        return date.astimezone(tz)
