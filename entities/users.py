from dataclasses import dataclass

from aiogram.types import CallbackQuery, Message


@dataclass
class User:
    user_id: str
    username: str
    first_name: str
    last_name: str

    @classmethod
    def to_entity(cls, user_data: dict) -> "User":
        return cls(
            user_id=user_data.get("user_id"),
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
        )

    @classmethod
    def from_message(cls, message: Message) -> "User":
        return cls(
            user_id=str(message.from_user.id),
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

    @classmethod
    def from_callback(cls, callback: CallbackQuery) -> "User":
        return cls(
            user_id=str(callback.from_user.id),
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
        )
