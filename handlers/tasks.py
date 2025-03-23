from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from callbacks.factory import TaskCallback
from dialogs.tasks.create_task import TaskCreateDialog
from dialogs.tasks.update_task import TaskUpdateDialog
from entities.users import User
from exceptions.base import ServerException
from keyboards.tasks import (
    get_back_keyboard,
    get_task_detail_keyboard,
    get_task_type_choose_keyboard,
    get_tasks_list_keyboard,
)
from messages.tasks import (
    NO_TASKS,
    TASK_COMPLETED,
    TASK_DELETED,
    TASK_TYPE_CHOOSE,
)
from repositories.tasks import TaskRepository
from states.tasks import TaskCreateStates, TaskUpdateStates
from utils.tasks import get_detail_task, get_tasks_list

router = Router()
task_create_dialog = TaskCreateDialog().create_dialog()
task_update_dialog = TaskUpdateDialog().create_dialog()
router.include_router(task_create_dialog)
router.include_router(task_update_dialog)


@router.callback_query(F.data.startswith("today_tasks"))
async def active_tasks_handler(callback: CallbackQuery):
    page = (
        int(callback.data.split("_")[-1])
        if callback.data != "today_tasks"
        else 1
    )

    user = User.from_callback(callback)
    tasks_data, has_next_page, has_prev_page = await TaskRepository(
        user
    ).get_user_today_tasks(page=page)

    if not tasks_data:
        await callback.answer(NO_TASKS, show_alert=True)
        return

    text = get_tasks_list(tasks_data)
    keyboard = get_tasks_list_keyboard(
        tasks_data,
        page,
        has_next_page is not None,
        has_prev_page is not None,
        "today_tasks",
    )

    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode="HTML"
    )


@router.callback_query(F.data == "all_tasks")
async def my_tasks_handler(callback: CallbackQuery):
    await callback.message.answer(
        TASK_TYPE_CHOOSE, reply_markup=get_task_type_choose_keyboard()
    )


@router.callback_query(F.data.startswith("active_tasks"))
async def active_tasks_handler(callback: CallbackQuery):
    page = (
        int(callback.data.split("_")[-1])
        if callback.data != "active_tasks"
        else 1
    )

    user = User.from_callback(callback)
    tasks_data, has_next_page, has_prev_page = await TaskRepository(
        user
    ).get_user_active_tasks(page=page)

    if not tasks_data:
        await callback.answer(NO_TASKS, show_alert=True)
        return

    text = get_tasks_list(tasks_data)
    keyboard = get_tasks_list_keyboard(
        tasks_data,
        page,
        has_next_page is not None,
        has_prev_page is not None,
        "active_tasks",
    )

    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("archive_tasks"))
async def archive_tasks_handler(callback: CallbackQuery):
    page = (
        int(callback.data.split("_")[-1])
        if callback.data != "archive_tasks"
        else 1
    )

    user = User.from_callback(callback)
    tasks_data, has_next_page, has_prev_page = await TaskRepository(
        user
    ).get_user_not_active_tasks(page=page)

    if not tasks_data:
        await callback.answer(NO_TASKS, show_alert=True)
        return

    text = get_tasks_list(tasks_data)
    keyboard = get_tasks_list_keyboard(
        tasks_data,
        page,
        has_next_page is not None,
        has_prev_page is not None,
        "archive_tasks",
    )

    await callback.message.edit_text(
        text, reply_markup=keyboard, parse_mode="HTML"
    )


@router.callback_query(TaskCallback.filter(F.action == "details"))
async def detail_task_handler(
    callback: CallbackQuery, callback_data: TaskCallback
):
    task_id = callback_data.task_id
    user = User.from_callback(callback)
    try:
        task = await TaskRepository(user).get_detail_task(task_id)
        text = get_detail_task(task)
        keyboard = get_task_detail_keyboard(task)
        await callback.message.answer(
            text, parse_mode="HTML", reply_markup=keyboard
        )
    except ServerException as e:
        await callback.message.answer(e.message, show_alert=True)


@router.callback_query(TaskCallback.filter(F.action == "complete_task"))
async def complete_task_handler(
    callback: CallbackQuery, callback_data: TaskCallback
):
    task_id = callback_data.task_id
    user = User.from_callback(callback)
    try:
        await TaskRepository(user).complete_task(task_id)
        keyboard = get_back_keyboard()
        await callback.message.answer(TASK_COMPLETED, reply_markup=keyboard)
    except ServerException as e:
        await callback.message.answer(e.message, show_alert=True)


@router.callback_query(TaskCallback.filter(F.action == "delete_task"))
async def delete_task_handler(
    callback: CallbackQuery, callback_data: TaskCallback
):
    task_id = callback_data.task_id
    user = User.from_callback(callback)
    try:
        await TaskRepository(user).delete_task(task_id)
        keyboard = get_back_keyboard()
        await callback.message.answer(TASK_DELETED, reply_markup=keyboard)
    except ServerException as e:
        await callback.message.answer(e.message, show_alert=True)


@router.callback_query(F.data == "create_task")
async def create_task_handler(
    callback: CallbackQuery, dialog_manager: DialogManager
):
    await dialog_manager.start(
        TaskCreateStates.CATEGORY, mode=StartMode.RESET_STACK
    )


@router.callback_query(TaskCallback.filter(F.action == "update_task"))
async def update_task_handler(
    callback: CallbackQuery,
    callback_data: TaskCallback,
    dialog_manager: DialogManager,
):
    task_id = callback_data.task_id
    user = User.from_callback(callback)
    task = await TaskRepository(user).get_detail_task(task_id)
    await dialog_manager.start(
        TaskUpdateStates.CATEGORY,
        data={"task_id": task_id, "task_data": task},
        mode=StartMode.RESET_STACK,
    )
