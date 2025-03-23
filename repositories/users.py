from typing import TypeVar

import aiohttp

from config import settings
from entities.users import User
from exceptions.users import UserNotFoundException
from schemas.users import UserSchema

TelegramUserId = TypeVar("TelegramUserId")


class UserRepository:
    @staticmethod
    def _get_list_url() -> str:
        return f"{settings.API_URL}/api/v1/users/"

    @staticmethod
    def _get_detail_url(pk: int) -> str:
        return f"{settings.API_URL}/api/v1/users/{pk}"

    @staticmethod
    def _get_create_payload(user: User) -> dict:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    async def create_user(self, user: User) -> UserSchema:
        async with aiohttp.ClientSession() as session:
            payload = self._get_create_payload(user)
            async with session.post(
                self._get_list_url(), json=payload
            ) as response:
                response.raise_for_status()
                user = await response.json()
                user_entity = User.to_entity(user)
                return UserSchema.to_schema(user_entity)

    async def get_user_by_user_id(
        self, user_id: TelegramUserId
    ) -> UserSchema | None:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self._get_detail_url(user_id)
                ) as response:
                    response.raise_for_status()
                    user = await response.json()
                    user_entity = User.to_entity(user)
                    return UserSchema.to_schema(user_entity)
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise UserNotFoundException
                raise e
