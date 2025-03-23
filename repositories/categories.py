from typing import Iterable

import aiohttp

from config import settings
from entities.categories import Category
from entities.users import User
from schemas.categories import CategorySchema


class CategoryRepository:
    def __init__(self, user: User):
        self._user = user

    @property
    def headers(self):
        return {"User-Id": self._user.user_id}

    @staticmethod
    def _get_list_url() -> str:
        return f"{settings.API_URL}/api/v1/tasks/categories/"

    async def get_all_categories(
        self,
    ) -> Iterable[CategorySchema] | Iterable[None]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self._get_list_url(), headers=self.headers
            ) as response:
                response.raise_for_status()
                response = await response.json()
                categories_entities = [
                    Category.to_entity(category)
                    for category in response["results"]
                ]
                return [
                    CategorySchema.to_schema(category)
                    for category in categories_entities
                ]
