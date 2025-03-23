from dataclasses import dataclass


@dataclass
class Category:
    id: int
    name: str

    @classmethod
    def to_entity(cls, category_data: dict) -> "Category":
        return cls(id=category_data.get("id"), name=category_data.get("name"))
