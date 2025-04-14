from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from prodadvert_bot.application.exceptions import CampaignCreateException
from prodadvert_bot.application.interfaces.campaigns import CampaignService
from prodadvert_bot.application.interfaces.text_generator import TextGenerator
from prodadvert_bot.dialogs.advertiser.states import AdvertiserMenuStates
from prodadvert_bot.dialogs.create_campaign.states import CreateCampaignStates


async def to_advertiser_menu(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.start(
        AdvertiserMenuStates.overview,
        data={
            "advertiser_id": manager.start_data["advertiser_id"],
        },
        mode=StartMode.RESET_STACK
    )


async def select_target_gender(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        item_id: str
):
    manager.current_context().dialog_data["target_gender"] = item_id
    await manager.next()


@inject
async def create(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        campaign_service: FromDishka[CampaignService]
):
    target_gender = (
        manager.dialog_data["target_gender"]
        if "target_gender" in manager.dialog_data else None
    )
    print(manager.dialog_data)
    try:
        await campaign_service.create(
            advertiser_id=manager.start_data["advertiser_id"],
            ad_title=manager.dialog_data["ad_title"],
            ad_text=manager.dialog_data["ad_text"],
            impressions_limit=manager.dialog_data["impressions_limit"],
            clicks_limit=manager.dialog_data["clicks_limit"],
            cost_per_click=manager.dialog_data["click_cost"],
            cost_per_impression=manager.dialog_data["impression_cost"],
            start_date=manager.dialog_data["start_date"],
            end_date=manager.dialog_data["end_date"],
            target_gender=target_gender,
            target_location=manager.dialog_data.get("target_location"),
            target_age_to=manager.dialog_data.get("target_age_to"),
            target_age_from=manager.dialog_data.get("target_age_from"),
        )
    except CampaignCreateException as exc:
        manager.current_context().dialog_data["error_message"] = str(exc)
        await manager.switch_to(CreateCampaignStates.error_message)
        return
    await callback.answer("Successfully created campaign")
    await manager.start(
        AdvertiserMenuStates.overview,
        data={
            "advertiser_id": manager.start_data["advertiser_id"],
        },
        mode=StartMode.RESET_STACK
    )


async def select_ai_language(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        item_id: str
):
    manager.current_context().dialog_data["ai_lang"] = item_id


async def make_ai_additional_empty(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    manager.current_context().dialog_data["ai_additional"] = ""
    await manager.switch_to(CreateCampaignStates.ai_gen)


@inject
async def generate_ai(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        text_generator: FromDishka[TextGenerator]
):
    text = await text_generator.generate(
        (
            manager.current_context().dialog_data.get("ai_topic")
            or manager.current_context().dialog_data["ad_title"]
        ),
        manager.current_context().dialog_data.get("ai_lang") or "EN",
        manager.current_context().dialog_data.get("ai_additional")
    )
    manager.current_context().dialog_data["ad_text"] = text
    await manager.switch_to(CreateCampaignStates.set_ad_text)


async def ai_topic_auto_getter(
        dialog_manager: DialogManager,
        **kwargs
):
    if "ai_topic" not in dialog_manager.current_context().dialog_data:
        return {
            "ai_topic": dialog_manager.current_context().dialog_data["ad_title"]
        }
    return {}
