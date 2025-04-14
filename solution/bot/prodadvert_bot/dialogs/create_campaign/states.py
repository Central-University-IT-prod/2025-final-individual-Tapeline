from aiogram.fsm.state import StatesGroup, State


class CreateCampaignStates(StatesGroup):
    set_ad_title = State()
    set_ad_text = State()
    set_impressions_target = State()
    set_clicks_target = State()
    set_impression_cost = State()
    set_clicks_cost = State()
    set_start_date = State()
    set_end_date = State()
    set_targeting_gender = State()
    set_targeting_age_from = State()
    set_targeting_age_to = State()
    set_targeting_location = State()
    error_message = State()
    confirm = State()
    ai_gen = State()
    ai_gen_change_topic = State()
    ai_gen_change_additional = State()
