from pydantic import BaseModel

from entities.categories import Category


class CategorySchema(BaseModel):
    id: int
    name: str

    @classmethod
    def to_schema(cls, category: Category) -> "CategorySchema":
        return cls(id=category.id, name=category.name)
