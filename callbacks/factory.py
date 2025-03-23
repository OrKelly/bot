from aiogram.filters.callback_data import CallbackData


class TaskCallback(CallbackData, prefix="task"):
    action: str
    task_id: str
