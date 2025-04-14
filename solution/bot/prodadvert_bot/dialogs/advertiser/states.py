from aiogram.fsm.state import State, StatesGroup


class AdvertiserMenuStates(StatesGroup):
    overview = State()
    campaign_list = State()
    total_stats = State()
    daily_stats = State()
