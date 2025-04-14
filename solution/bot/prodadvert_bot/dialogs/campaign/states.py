from aiogram.fsm.state import State, StatesGroup


class CampaignMenuStates(StatesGroup):
    overview = State()
    total_stats = State()
    daily_stats = State()
    settings = State()
    edit_ad_title = State()
    edit_ad_text = State()
    edit_impressions_limit = State()
    edit_clicks_limit = State()
    edit_cost_per_impression = State()
    edit_cost_per_click = State()
    edit_start_date = State()
    edit_end_date = State()
    edit_targeting = State()
    edit_targeting_age_range = State()
    edit_targeting_location = State()
    edit_image = State()
    edit_image_input = State()
