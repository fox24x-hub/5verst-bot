# states/report.py
from aiogram.fsm.state import State, StatesGroup


class ReportStates(StatesGroup):
    """
    Состояния для сбора субботнего отчёта 5 вёрст.
    """
    waiting_total = State()         # сколько участников всего
    waiting_first_timers = State()  # сколько были впервые
    waiting_guests = State()        # гости из других локаций
    waiting_volunteers = State()    # сколько волонтёров помогали
    waiting_highlight = State()     # особенный момент встречи (или "нет")
