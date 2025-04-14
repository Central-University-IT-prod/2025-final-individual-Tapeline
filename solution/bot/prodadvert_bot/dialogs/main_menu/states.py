from aiogram.fsm.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    main = State()
    enter_advertiser_id = State()
