from pydantic import BaseModel

from entities.users import User


class UserSchema(BaseModel):
    user_id: str
    username: str
    first_name: str
    last_name: str

    @classmethod
    def to_schema(cls, user: User) -> "UserSchema":
        return cls(
            user_id=user.user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
