from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from entities.categories import Category
from entities.users import User
from enums.tasks import TaskStatusEnum


@dataclass
class Task:
    user: User
    title: str
    description: str
    deadline: datetime
    status: TaskStatusEnum
    id: str | None = None
    categories: Iterable[Category] | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def to_entity(cls, task_data: dict) -> "Task":
        return cls(
            user=task_data.get("user"),
            title=task_data.get("title"),
            description=task_data.get("description"),
            deadline=cls.parse_date(task_data.get("deadline")),
            status=task_data.get("status"),
            id=task_data.get("id"),
            categories=cls.get_categories(task_data.get("categories")),
            created_at=cls.parse_date(task_data.get("created_at")),
            completed_at=cls.parse_date(task_data.get("completed_at")),
        )

    @classmethod
    def get_categories(
        cls, categories_data: dict
    ) -> Iterable[Category] | None:
        if categories_data:
            return [
                Category.to_entity(category) for category in categories_data
            ]
        return None

    @classmethod
    def parse_date(cls, date_str: str) -> datetime | None:
        if date_str:
            return datetime.fromisoformat(date_str)
        return None
