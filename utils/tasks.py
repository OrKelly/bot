from datetime import datetime
from typing import Iterable

from schemas.tasks import TaskSchema, TaskShortSchema


def get_tasks_list(tasks: Iterable[TaskShortSchema]) -> str:
    message_text = "Ваши задачи:\n\n"

    for task in tasks:
        created_at_str = get_date_strf(task.created_at)
        deadline_str = get_date_strf(task.deadline)

        message_text += (
            f"<b>{task.title}</b>\n"
            f"<b>Создана:</b> {created_at_str}\n"
            f"<b>Дедлайн:</b> {deadline_str}\n"
            f"\n"
        )

    return message_text.strip()


def get_detail_task(task: TaskSchema) -> str:
    task_completed_at = (
        get_date_strf(task.completed_at)
        if task.completed_at is not None
        else "Не выполнена"
    )

    return (
        f"📝 <b>Заголовок:</b> <b>{task.title}</b>\n"
        f"📜 <b>Описание:</b> <b>{task.description if task.description else 'Нет описания'}</b>\n"
        f"📅 <b>Создана:</b> <b>{get_date_strf(task.created_at)}</b>\n"
        f"⏰ <b>Дедлайн:</b> <b>{get_date_strf(task.deadline)}</b>\n"
        f"🔖 <b>Статус:</b> <b>{task.status}</b>\n"
        f"📂 <b>Категории:</b> <b>{', '.join([category.name for category in task.categories]) if task.categories else 'Нет категорий'}</b>\n"
        f"✅ <b>Дата выполнения:</b> <b>{task_completed_at}</b>"
    )


def get_date_strf(date: datetime) -> str:
    return date.strftime("%d.%m.%Y, %H:%M:%S")
