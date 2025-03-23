from datetime import datetime
from typing import Iterable, NoReturn, TypeVar

import aiohttp
import pytz

from config import settings
from entities.tasks import Task
from entities.users import User
from exceptions.constants import status
from exceptions.tasks import (
    TaskAlreadyDoneException,
    TaskAlreadyExistsException,
    TaskAnotherAuthorException,
    TaskIncorrectDeadline,
    TaskNotFoundException,
)
from schemas.tasks import TaskSchema, TaskShortSchema

TelegramUserId = TypeVar("TelegramUserId")


class TaskRepository:
    def __init__(self, user: User):
        self._user = user

    @property
    def headers(self):
        return {"User-Id": self._user.user_id}

    @staticmethod
    def _get_list_url() -> str:
        return f"{settings.API_URL}/api/v1/tasks/"

    @staticmethod
    def _get_detail_url(pk: str) -> str:
        return f"{settings.API_URL}/api/v1/tasks/{pk}/"

    @staticmethod
    def _get_complete_url(pk: str) -> str:
        return f"{settings.API_URL}/api/v1/tasks/{pk}/complete/"

    @staticmethod
    def _get_create_payload(task: Task) -> dict:
        return {
            "title": task.title,
            "description": task.description,
            "deadline": task.deadline.isoformat(),
            "categories": [category.id for category in task.categories],
        }

    @staticmethod
    def _get_correct_tz_time(date: datetime) -> datetime:
        tz = pytz.timezone("America/Adak")
        return date.astimezone(tz)

    async def create_task(self, task_payload: dict) -> TaskShortSchema:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._get_list_url(), json=task_payload, headers=self.headers
            ) as response:
                try:
                    response.raise_for_status()
                    task = await response.json()
                    task_entity = Task.to_entity(task)
                    return TaskShortSchema.to_schema(task_entity)
                except aiohttp.ClientResponseError as e:
                    match e.status:
                        case status.HTTP_400_BAD_REQUEST:
                            raise TaskIncorrectDeadline
                        case status.HTTP_409_CONFLICT:
                            raise TaskAlreadyExistsException
                        case _:
                            raise e

    async def update_task(
        self, task_payload: Task, task_id: str
    ) -> TaskShortSchema:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                self._get_detail_url(task_id),
                json=task_payload,
                headers=self.headers,
            ) as response:
                try:
                    response.raise_for_status()
                    task = await response.json()
                    task_entity = Task.to_entity(task)
                    return TaskShortSchema.to_schema(task_entity)
                except aiohttp.ClientResponseError as e:
                    match e.status:
                        case status.HTTP_400_BAD_REQUEST:
                            raise TaskIncorrectDeadline
                        case status.HTTP_409_CONFLICT:
                            raise TaskAlreadyExistsException
                        case status.HTTP_403_FORBIDDEN:
                            raise TaskAnotherAuthorException
                        case _:
                            raise e

    async def get_user_today_tasks(
        self, page: int, page_size: int = 5
    ) -> Iterable[TaskShortSchema] | Iterable[None]:
        async with aiohttp.ClientSession() as session:
            today = (
                self._get_correct_tz_time(datetime.today()).date().isoformat()
            )
            async with session.get(
                self._get_list_url(),
                params={
                    "user_id": self._user.user_id,
                    "deadline": today,
                    "page": page,
                    "page_size": page_size,
                    "ordering": "deadline",
                },
                headers=self.headers,
            ) as response:
                response.raise_for_status()
                task = await response.json()
                task_entities = [
                    Task.to_entity(task) for task in task["results"]
                ]
                return (
                    [
                        TaskShortSchema.to_schema(task_entity)
                        for task_entity in task_entities
                    ],
                    task["next"],
                    task["previous"],
                )

    async def get_user_active_tasks(
        self, page: int, page_size: int = 5
    ) -> (
        tuple[Iterable[TaskShortSchema], str | None, str | None]
        | Iterable[None]
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._get_list_url(),
                params={
                    "user_id": self._user.user_id,
                    "page": page,
                    "page_size": page_size,
                    "is_active": "true",
                    "ordering": "deadline",
                },
                headers=self.headers,
            ) as response:
                response.raise_for_status()
                task = await response.json()
                task_entities = [
                    Task.to_entity(task) for task in task["results"]
                ]
                return (
                    [
                        TaskShortSchema.to_schema(task_entity)
                        for task_entity in task_entities
                    ],
                    task["next"],
                    task["previous"],
                )

    async def get_user_not_active_tasks(
        self, page: int, page_size: int = 5
    ) -> (
        tuple[Iterable[TaskShortSchema], str | None, str | None]
        | Iterable[None]
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._get_list_url(),
                params={
                    "user_id": self._user.user_id,
                    "page": page,
                    "page_size": page_size,
                    "is_active": "false",
                    "ordering": "deadline",
                },
                headers=self.headers,
            ) as response:
                response.raise_for_status()
                task = await response.json()
                task_entities = [
                    Task.to_entity(task) for task in task["results"]
                ]
                return (
                    [
                        TaskShortSchema.to_schema(task_entity)
                        for task_entity in task_entities
                    ],
                    task["next"],
                    task["previous"],
                )

    async def get_detail_task(self, task_id: str) -> TaskSchema | NoReturn:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._get_detail_url(task_id), headers=self.headers
            ) as response:
                try:
                    response.raise_for_status()
                    task = await response.json()
                    task["user"] = self._user
                    task_entity = Task.to_entity(task)
                    return TaskSchema.to_schema(task_entity)
                except aiohttp.ClientResponseError as e:
                    if e.status == status.HTTP_404_NOT_FOUND:
                        raise TaskNotFoundException
                    raise e

    async def complete_task(self, task_id: str) -> NoReturn:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._get_complete_url(task_id), headers=self.headers
            ) as response:
                try:
                    response.raise_for_status()

                except aiohttp.ClientResponseError as e:
                    match e.status:
                        case status.HTTP_404_NOT_FOUND:
                            raise TaskNotFoundException
                        case status.HTTP_409_CONFLICT:
                            raise TaskAlreadyDoneException
                        case status.HTTP_403_FORBIDDEN:
                            raise TaskAnotherAuthorException
                        case _:
                            raise e

    async def delete_task(self, task_id):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                self._get_detail_url(task_id), headers=self.headers
            ) as response:
                try:
                    response.raise_for_status()
                except aiohttp.ClientResponseError as e:
                    if e.status == status.HTTP_403_FORBIDDEN:
                        raise TaskAnotherAuthorException
                    raise e
