from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factory import TaskCallback
from enums.tasks import TaskStatusEnum
from schemas.tasks import TaskSchema, TaskShortSchema


def get_tasks_list_keyboard(
    tasks: Iterable[TaskShortSchema],
    current_page: int,
    has_next: bool,
    has_previous: bool,
    callback_data: str,
):
    buttons = []
    for task in tasks:
        task_button = [
            InlineKeyboardButton(
                text=f"📄 Подробности о {task.title}",  # Добавлен смайлик
                callback_data=TaskCallback(
                    action="details", task_id=task.id
                ).pack(),
            )
        ]
        buttons.append(task_button)

    pagination_buttons = []
    if has_previous:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{callback_data}_{current_page - 1}",
            )
        )
    if has_next:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"{callback_data}_{current_page + 1}",
            )
        )

    if pagination_buttons:
        buttons.append(pagination_buttons)
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад к списку задач", callback_data="all_tasks"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_type_choose_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="📋 Активные", callback_data="active_tasks"
            ),  # Добавлен смайлик
            InlineKeyboardButton(
                text="📁 Завершенные", callback_data="archive_tasks"
            ),  # Добавлен смайлик
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_detail_keyboard(task: TaskSchema):
    buttons = []

    if task.status != TaskStatusEnum.DONE:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ Завершить задачу",
                    callback_data=TaskCallback(
                        action="complete_task", task_id=task.id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="✏️ Редактировать задачу",
                    callback_data=TaskCallback(
                        action="update_task", task_id=task.id
                    ).pack(),
                ),
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать задачу",
                    callback_data=TaskCallback(
                        action="update_task", task_id=task.id
                    ).pack(),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="🗑️ Удалить задачу",
                callback_data=TaskCallback(
                    action="delete_task", task_id=task.id
                ).pack(),
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад к списку задач", callback_data="all_tasks"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="🔙 Назад к списку задач", callback_data="all_tasks"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
