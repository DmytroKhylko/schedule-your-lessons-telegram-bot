from aiogram.fsm.state import State, StatesGroup


class ScheduleCreationStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_duration = State()
    waiting_for_subject = State()
    waiting_for_location = State()
    waiting_for_recurrence = State()
    waiting_for_recurrence_days = State()
    waiting_for_participants = State()
    confirming = State()
