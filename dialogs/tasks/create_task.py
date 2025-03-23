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
from messages.tasks import TASK_CREATED
from states.tasks import TaskCreateStates


class TaskCreateDialog(TaskBaseCreateUpdateDialog):
    async def _execute(
        self,
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
    ):
        request_body = self._get_request_body(dialog_manager)
        user = User.from_callback(callback)
        try:
            await self._task_repository(user=user).create_task(request_body)
            keyboard = get_back_keyboard()
            await callback.message.answer(TASK_CREATED, reply_markup=keyboard)
        except ServerException as e:
            await callback.message.answer(e.message)
        finally:
            await dialog_manager.done()

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
                state=TaskCreateStates.CATEGORY,
                getter=self._get_categories,
            ),
            Window(
                Const("Введите заголовок:"),
                MessageInput(self._on_title_entered),
                state=TaskCreateStates.TITLE,
            ),
            Window(
                Const("Введите описание (или нажмите 'Пропустить'):"),
                MessageInput(self._on_description_entered),
                self.skip_button,
                state=TaskCreateStates.DESCRIPTION,
            ),
            Window(
                Const("Введите дату дедлайна:"),
                Calendar(
                    id="calendar",
                    on_click=self._on_deadline_date_entered,
                    config=self._calendar_config,
                ),
                state=TaskCreateStates.DEADLINE_DATE,
            ),
            Window(
                Const("Введите время дедлайна (в формате ЧЧ:ММ):"),
                MessageInput(self._on_deadline_time_entered),
                state=TaskCreateStates.DEADLINE_TIME,
            ),
            Window(
                Const(
                    "Ваш запрос сформирован. Нажмите 'Готово' для завершения."
                ),
                Button(
                    Const("Готово"), id="done_button", on_click=self._execute
                ),
                Cancel(Const("Отмена"), id="cancel_button"),
                state=TaskCreateStates.DONE,
            ),
        )
