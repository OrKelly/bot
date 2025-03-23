from exceptions.base import NotFoundException, ServerException


class TaskNotFoundException(NotFoundException):
    @property
    def message(self):
        return "Задача не найдена!"


class TaskAlreadyDoneException(ServerException):
    @property
    def message(self):
        return "Задача уже завершена"


class TaskAnotherAuthorException(ServerException):
    @property
    def message(self):
        return "Задача создана другим пользователем"


class TaskAlreadyExistsException(ServerException):
    @property
    def message(self):
        return "Такая задача уже существует"


class TaskIncorrectDeadline(ServerException):
    @property
    def message(self):
        return "Дедлайн не может быть раньше текущего дня"
