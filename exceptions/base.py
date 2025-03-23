from dataclasses import dataclass

from exceptions.constants import status


@dataclass
class ServerException(Exception):
    """
    Базовый класс эксепшенов.
    Для создания своего собственного отнаследоваться от него
    и переопределить.

    :param code: HTTP статус код, возвращаемый в респонсе
    :param error_code: код самой ошибки. Нужен для более
    гибкого логирования и сбора метрик в будущем.
    """

    code: status.HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    error_code: status.HTTP_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST

    @property
    def message(self):
        return "Произошла непредвиденная ошибка во время работы приложения"


@dataclass
class NotFoundException(ServerException):
    code: status.HTTP_404_NOT_FOUND = status.HTTP_404_NOT_FOUND
    error_code: status.HTTP_404_NOT_FOUND = status.HTTP_404_NOT_FOUND
