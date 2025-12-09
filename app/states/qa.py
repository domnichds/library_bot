from aiogram.fsm.state import StatesGroup, State


class QAStates(StatesGroup):
    waiting_for_question = State()