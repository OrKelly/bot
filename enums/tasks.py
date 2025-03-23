from enum import Enum


class TaskStatusEnum(Enum):
    ACTIVE = 1, "Активная"
    DONE = 2, "Выполнена"
    OVERDUE = 3, "Просрочена"

    def __str__(self):
        return self.value[1]

    @classmethod
    def from_value(cls, value: int):
        for item in cls:
            if item.value[0] == value:
                return item
        raise ValueError(f"{value} is not a valid {cls.__name__}")
