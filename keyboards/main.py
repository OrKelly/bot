from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="📝 Посмотреть мои задачи", callback_data="all_tasks"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📅 Задачи на сегодня", callback_data="today_tasks"
            ),
            InlineKeyboardButton(
                text="➕ Создать новую задачу", callback_data="create_task"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
