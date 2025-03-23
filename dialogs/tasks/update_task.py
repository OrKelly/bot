from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Calendar,
    Cancel,
    Multiselect,
)
from aiogram_dialog.widgets.text import Const, Format

from dialogs.tasks.base import TaskBaseCreateUpdateDialog
from entities.users import User
from exceptions.base import ServerException
from keyboards.tasks import get_back_keyboard
from messages.tasks import TASK_UPDATED
from states.tasks import TaskUpdateStates


class TaskUpdateDialog(TaskBaseCreateUpdateDialog):
    async def _execute(
        self,
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
    ):
        request_body = self._get_request_body(dialog_manager)
        task_id = dialog_manager.start_data.get("task_id")
        user = User.from_callback(callback)
        try:
            await self._task_repository(user=user).update_task(
                request_body, task_id
            )
            keyboard = get_back_keyboard()
            await callback.message.answer(TASK_UPDATED, reply_markup=keyboard)
        except ServerException as e:
            await callback.message.answer(e.message)
        finally:
            await dialog_manager.done()

    @staticmethod
    def _get_request_body(dialog_manager: DialogManager) -> dict:
        data = dialog_manager.dialog_data
        task = dialog_manager.start_data.get("task_data")
        request_body = {}

        if "categories" in data:
            request_body["categories"] = data["categories"]

        if "title" in data:
            request_body["title"] = data["title"]

        if "description" in data:
            request_body["description"] = data["description"]

        if "deadline_date" in data or "deadline_time" in data:
            deadline_date = data.get(
                "deadline_date", task.deadline.date().strftime("%Y-%m-%d")
            )
            deadline_time = data.get(
                "deadline_time", task.deadline.time().strftime("%H:%M")
            )

            if deadline_date and deadline_time:
                request_body["deadline"] = (
                    f"{deadline_date}T{deadline_time}:00.000Z"
                )

        return request_body

    def create_dialog(self):
        return Dialog(
            Window(
                Const("Выберите категории (можно несколько):"),
                Multiselect(
                    Format("✓ {item[name]}"),
                    Format("{item[name]}"),
                    id="category_multiselect",
                    item_id_getter=lambda x: x["id"],
                    items="categories",
                    on_click=self._on_categories_selected,
                ),
                Button(
                    Const("Далее"),
                    id="next_button",
                    on_click=lambda callback,
                    widget,
                    dialog_manager: dialog_manager.next(),
                ),
                state=TaskUpdateStates.CATEGORY,
                getter=self._get_categories,
            ),
            Window(
                Const("Введите заголовок:"),
                MessageInput(self._on_title_entered),
                self.skip_button,
                state=TaskUpdateStates.TITLE,
            ),
            Window(
                Const("Введите описание:"),
                MessageInput(self._on_description_entered),
                self.skip_button,
                state=TaskUpdateStates.DESCRIPTION,
            ),
            Window(
                Const("Введите дату дедлайна:"),
                Calendar(
                    id="calendar",
                    on_click=self._on_deadline_date_entered,
                    config=self._calendar_config,
                ),
                self.skip_button,
                state=TaskUpdateStates.DEADLINE_DATE,
            ),
            Window(
                Const("Введите время дедлайна (в формате ЧЧ:ММ):"),
                MessageInput(self._on_deadline_time_entered),
                self.skip_button,
                state=TaskUpdateStates.DEADLINE_TIME,
            ),
            Window(
                Const(
                    "Ваш запрос сформирован. Нажмите 'Готово' для завершения."
                ),
                Button(
                    Const("Готово"), id="done_button", on_click=self._execute
                ),
                Cancel(Const("Отмена"), id="cancel_button"),
                state=TaskUpdateStates.DONE,
            ),
        )
