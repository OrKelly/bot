from abc import ABC, abstractmethod
from datetime import datetime

import pytz
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, CalendarConfig, Multiselect, Row
from aiogram_dialog.widgets.kbd.calendar_kbd import CalendarData
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.widget_event import WidgetEventProcessor
from pydantic import ValidationError

from entities.users import User
from repositories.categories import CategoryRepository
from repositories.tasks import TaskRepository


class TaskBaseCreateUpdateDialog(ABC):
    def __init__(self):
        """Базовый класс создания диалогов для отправки запроса на
        редактирование/создание задачи.

        Для использования переопределить _execute - метод, который выполняет
        нужное действие после завершения диалога,
        create_dialog, где и будет сам диалог.
        """

        self._calendar_config = CalendarConfig(
            timezone=pytz.timezone("America/Adak")
        )
        self._task_repository = TaskRepository
        self._category_repository = CategoryRepository

    @staticmethod
    def _validate_title(value: str) -> str:
        if not value:
            raise ValidationError("Заголовок не может быть пустым.")
        if len(value) > 100:
            raise ValidationError(
                "Заголовок слишком длинный (максимум 100 символов)."
            )
        return value

    @staticmethod
    def _validate_time(time_str: str) -> str:
        try:
            datetime.strptime(time_str, "%H:%M")
            return time_str
        except ValueError:
            raise ValueError(
                "Некорректный формат времени. Введите время в формате ЧЧ:ММ."
            )

    async def _get_categories(self, dialog_manager: DialogManager, **kwargs):
        if "cached_categories" not in dialog_manager.dialog_data:
            user = User.from_message(dialog_manager.event)
            categories = await self._category_repository(
                user
            ).get_all_categories()
            categories_dicts = [
                {"id": category.id, "name": category.name}
                for category in categories
            ]

            dialog_manager.dialog_data["cached_categories"] = categories_dicts

        selected_categories = dialog_manager.dialog_data.get("categories", [])

        return {
            "categories": dialog_manager.dialog_data["cached_categories"],
            "checked": selected_categories,
        }

    async def _on_categories_selected(
        self,
        callback: WidgetEventProcessor,
        select: Multiselect,
        dialog_manager: DialogManager,
        selected: list,
    ):
        if "categories" not in dialog_manager.dialog_data:
            dialog_manager.dialog_data["categories"] = []

        dialog_manager.dialog_data["categories"].extend(selected)

        dialog_manager.dialog_data["categories"] = list(
            set(dialog_manager.dialog_data["categories"])
        )

    async def _on_title_entered(
        self,
        message: Message,
        widget: WidgetEventProcessor,
        dialog_manager: DialogManager,
    ):
        try:
            title = self._validate_title(message.text)
            dialog_manager.dialog_data["title"] = title
            await dialog_manager.next()
        except ValidationError as e:
            await message.answer(str(e))

    async def _on_description_entered(
        self,
        message: Message,
        widget: WidgetEventProcessor,
        dialog_manager: DialogManager,
    ):
        dialog_manager.dialog_data["description"] = message.text
        await dialog_manager.next()

    async def _on_skip_button(
        self,
        message: Message,
        widget: WidgetEventProcessor,
        dialog_manager: DialogManager,
    ):
        await dialog_manager.next()

    async def _on_deadline_date_entered(
        self,
        callback: CallbackQuery,
        widget,
        dialog_manager: DialogManager,
        selected_date: CalendarData,
    ):
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        dialog_manager.dialog_data["deadline_date"] = selected_date_str
        await dialog_manager.next()

    async def _on_deadline_time_entered(
        self,
        message: Message,
        widget: WidgetEventProcessor,
        dialog_manager: DialogManager,
    ):
        try:
            time = self._validate_time(message.text)
            dialog_manager.dialog_data["deadline_time"] = time
            await dialog_manager.next()
        except ValidationError as e:
            await message.answer(str(e))

    @property
    def skip_button(self):
        return Row(
            Button(
                Const("Пропустить"),
                id="skip_button",
                on_click=self._on_skip_button,
            ),
        )

    @staticmethod
    def _get_request_body(dialog_manager: DialogManager) -> dict:
        data = dialog_manager.dialog_data
        request_body = {}

        if "categories" in data:
            request_body["categories"] = data["categories"]

        if "title" in data:
            request_body["title"] = data["title"]

        if "description" in data:
            request_body["description"] = data["description"]

        if "deadline_date" in data and "deadline_time" in data:
            deadline_date = data["deadline_date"]
            deadline_time = data["deadline_time"]
            if deadline_date and deadline_time:
                request_body["deadline"] = (
                    f"{deadline_date}T{deadline_time}:00.000Z"
                )

        return request_body

    @abstractmethod
    def _execute(
        self,
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
    ):
        """Переопределить в дочерних классах"""
        ...

    @abstractmethod
    def create_dialog(self):
        """Переопределить в дочерних классах"""
        ...
