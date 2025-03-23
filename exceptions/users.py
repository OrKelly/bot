from exceptions.base import NotFoundException


class UserNotFoundException(NotFoundException):
    @property
    def message(self):
        return "Пользователь не найден!"
