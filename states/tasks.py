from aiogram.fsm.state import State, StatesGroup


class TaskCreateStates(StatesGroup):
    CATEGORY = State()
    TITLE = State()
    DESCRIPTION = State()
    DEADLINE_DATE = State()
    DEADLINE_TIME = State()
    DONE = State()


class TaskUpdateStates(StatesGroup):
    CATEGORY = State()
    TITLE = State()
    DESCRIPTION = State()
    DEADLINE_DATE = State()
    DEADLINE_TIME = State()
    DONE = State()
