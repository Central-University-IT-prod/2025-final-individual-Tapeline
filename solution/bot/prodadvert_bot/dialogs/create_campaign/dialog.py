from _operator import itemgetter
from typing import Any

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Next, Select, SwitchTo, Radio
from aiogram_dialog.widgets.text import Const, Format, Jinja
from magic_filter import F

from prodadvert_bot.dialogs.common.callbacks import InputSetAndNext, InputSetAndSwitchTo
from prodadvert_bot.dialogs.common.getters import get_from_dialog_data
from prodadvert_bot.dialogs.create_campaign import functions
from prodadvert_bot.dialogs.create_campaign.states import CreateCampaignStates


async def error_must_be_an_integer(
        message: Message,
        dialog: Any,
        manager: DialogManager,
        error: ValueError
):
    await message.answer("❌ <b>Value must be an integer.</b>")


async def error_must_be_a_float(
        message: Message,
        dialog: Any,
        manager: DialogManager,
        error: ValueError
):
    await message.answer("❌ <b>Value must be a float.</b>")


_cancel_btn = Button(
    Const("🚫 Cancel"), id="cancel", on_click=functions.to_advertiser_menu
)


create_campaign_dialog = Dialog(
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set the name of the campaign.\n"
            "<i>Current: {{ad_title}}</i>"
        ),
        TextInput(
            id="ad_title",
            on_success=InputSetAndNext(),
            type_factory=str,
        ),
        Next(Const("⏩ Next"), when=F["ad_title"]),
        _cancel_btn,
        state=CreateCampaignStates.set_ad_title
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set the text of the campaign:\n"
            "<i>Current: {{ad_text}}</i>"
        ),
        TextInput(
            id="ad_text",
            on_success=InputSetAndNext(),
            type_factory=str,
        ),
        SwitchTo(
            Const("🤖 Generate with AI"),
            id="generate_with_ai",
            state=CreateCampaignStates.ai_gen,
        ),
        Next(Const("⏩ Next"), when=F["ad_text"]),
        _cancel_btn,
        state=CreateCampaignStates.set_ad_text
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set impressions target value:\n"
            "<i>Current: {{impressions_limit}}</i>"
        ),
        TextInput(
            id="impressions_limit",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next"), when=F["impressions_limit"]),
        _cancel_btn,
        state=CreateCampaignStates.set_impressions_target
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set clicks target value:\n"
            "<i>Current: {{clicks_limit}}</i>"
        ),
        TextInput(
            id="clicks_limit",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next"), when=F["clicks_limit"]),
        _cancel_btn,
        state=CreateCampaignStates.set_clicks_target
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set impression cost:\n"
            "<i>Current: {{impression_cost}}</i>"
        ),
        TextInput(
            id="impression_cost",
            on_error=error_must_be_a_float,
            on_success=InputSetAndNext(),
            type_factory=float,
        ),
        Next(Const("⏩ Next"), when=F["impression_cost"]),
        _cancel_btn,
        state=CreateCampaignStates.set_impression_cost
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set click cost:\n"
            "<i>Current: {{click_cost}}</i>"
        ),
        TextInput(
            id="click_cost",
            on_error=error_must_be_a_float,
            on_success=InputSetAndNext(),
            type_factory=float,
        ),
        Next(Const("⏩ Next"), when=F["click_cost"]),
        _cancel_btn,
        state=CreateCampaignStates.set_clicks_cost
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set start date: {{start_date}}\n"
            "<i>Current: {{start_date}}</i>"
        ),
        TextInput(
            id="start_date",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next"), when=F["start_date"]),
        _cancel_btn,
        state=CreateCampaignStates.set_start_date
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set end date:\n"
            "<i>Current: {{end_date}}</i>"
        ),
        TextInput(
            id="end_date",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next"), when=F["end_date"]),
        _cancel_btn,
        state=CreateCampaignStates.set_end_date
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set targeting gender:\n"
            "<i>Current: {{target_gender}}</i>"
        ),
        Select(
            Format("{item[1]}"),
            id="target_gender",
            item_id_getter=itemgetter(0),
            items=lambda *a, **k: [
                ("MALE", "🚹 Male"),
                ("FEMALE", "🚺 Female"),
                ("ALL", "🚻 All"),
            ],
            on_click=functions.select_target_gender
        ),
        Next(Const("⏩ Next")),
        _cancel_btn,
        state=CreateCampaignStates.set_targeting_gender
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set targeting age from:\n"
            "<i>Current: {{target_age_from}}</i>"
        ),
        TextInput(
            id="target_age_from",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next")),
        _cancel_btn,
        state=CreateCampaignStates.set_targeting_age_from
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>\n"
            "\n"
            "Set targeting age to:\n"
            "<i>Current: {{target_age_to}}</i>"
        ),
        TextInput(
            id="target_age_to",
            on_error=error_must_be_an_integer,
            on_success=InputSetAndNext(),
            type_factory=int,
        ),
        Next(Const("⏩ Next")),
        _cancel_btn,
        state=CreateCampaignStates.set_targeting_age_to
    ),
    Window(
        Jinja(
            "📣 <b>Creating campaign.</b>"
            "\n"
            "Set targeting location:\n"
            "<i>Current: {{target_location}}</i>"
        ),
        TextInput(
            id="target_location",
            on_success=InputSetAndNext(),
            type_factory=str,
        ),
        Next(Const("⏩ Next")),
        _cancel_btn,
        state=CreateCampaignStates.set_targeting_location
    ),
    Window(
        Jinja(
            "Confirm campaign creation.\n"
            "\n"
            "💬 Title: {{ad_title}}\n"
            "<pre>{{ ad_text }}</pre>\n"
            "🎯 Target limits: "
            "<code>{{impressions_limit}}</code> views / "
            "<code>{{clicks_limit}}</code> clicks\n"
            "💵 Costs: <code>{{impression_cost}}</code> per view"
            " / <code>{{click_cost}}</code> per click\n"
            "📆 Dates: <code>{{start_date}}</code> - "
            "<code>{{end_date}}</code>\n"
            "🎯 Targeting:\n"
            "    🚻 Gender: <code>{{target_gender}}</code>\n"
            "    🕓 Ages: <code>{{target_age_from}}</code> - "
            "<code>{{target_age_to}}</code>\n"
            "    📍 Location: <code>{{target_location}}</code>",
        ),
        SwitchTo(
            Const("✏️ Re-enter values"),
            id="back",
            state=CreateCampaignStates.set_ad_title
        ),
        Button(
            Const("✅ Create"),
            id="create_btn",
            on_click=functions.create
        ),
        state=CreateCampaignStates.confirm,
    ),
    Window(
        Jinja(
            "❗️ Errors during campaign creation:\n"
            "{{error_message}}\n"
            "Please fix and retry."
        ),
        SwitchTo(
            Const("✏️ Re-enter values"),
            id="back",
            state=CreateCampaignStates.set_ad_title
        ),
        _cancel_btn,
        state=CreateCampaignStates.error_message
    ),
    Window(
        Jinja(
            "🤖 <b>AI generation.</b>\n"
            "Generate texts for your adverts in no time with AI.\n"
            "\n"
            "📣 Topic (based on campaign name): <code>{{ai_topic}}</code>\n"
            "📣 Additional parameters: <code>{{ai_additional}}</code>"
        ),
        Radio(
            Format("🔳 {item[1]}"),
            Format("⬜️ {item[1]}"),
            id="ai_lang",
            item_id_getter=itemgetter(0),
            items=lambda *a, **k: [
                ("EN", "🇬🇧 English"),
                ("RU", "🇷🇺 Russian"),
            ],
            on_state_changed=functions.select_ai_language
        ),
        SwitchTo(
            Const("📝 Change topic"),
            id="change_topic",
            state=CreateCampaignStates.ai_gen_change_topic
        ),
        SwitchTo(
            Const("📝 Change additional params"),
            id="change_additional",
            state=CreateCampaignStates.ai_gen_change_additional
        ),
        Button(
            Const("🤖 Generate"),
            id="generate",
            on_click=functions.generate_ai,
        ),
        SwitchTo(
            Const("⬅️ Back to text"),
            id="back",
            state=CreateCampaignStates.set_ad_text
        ),
        getter=functions.ai_topic_auto_getter,
        state=CreateCampaignStates.ai_gen
    ),
    Window(
        Jinja(
            "📝 <b>Change AI topic:</b>"
        ),
        TextInput(
            id="ai_topic",
            on_success=InputSetAndSwitchTo(CreateCampaignStates.ai_gen),
            type_factory=str,
        ),
        SwitchTo(
            Const("⬅️ Back to AI"),
            id="back",
            state=CreateCampaignStates.ai_gen,
        ),
        state=CreateCampaignStates.ai_gen_change_topic
    ),
    Window(
        Jinja(
            "📝 <b>Change AI additional prompt:</b>"
        ),
        TextInput(
            id="ai_additional",
            on_success=InputSetAndSwitchTo(CreateCampaignStates.ai_gen),
            type_factory=str,
        ),
        Button(
            Const("⭕️ Make empty"),
            id="make_empty",
            on_click=functions.make_ai_additional_empty
        ),
        SwitchTo(
            Const("⬅️ Back to AI"),
            id="back",
            state=CreateCampaignStates.ai_gen,
        ),
        state=CreateCampaignStates.ai_gen_change_additional
    ),
    getter=get_from_dialog_data
)
