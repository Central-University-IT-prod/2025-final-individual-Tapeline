from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from prodadvert_bot.application.interfaces.advertisers import AdvertiserService, convert_daily_stats_for_plotter
from prodadvert_bot.application.interfaces.campaigns import CampaignService
from prodadvert_bot.application.interfaces.plotter import Plotter
from prodadvert_bot.dialogs.advertiser.states import AdvertiserMenuStates
from prodadvert_bot.dialogs.campaign.states import CampaignMenuStates
from prodadvert_bot.dialogs.create_campaign.states import CreateCampaignStates
from prodadvert_bot.dialogs.main_menu.states import MainMenuStates


async def select_campaign_id(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        item_id: str
):
    manager.current_context().dialog_data["campaign_id"] = item_id
    await manager.start(
        CampaignMenuStates.overview,
        data={
            "advertiser_id": manager.start_data["advertiser_id"],
            "campaign_id": item_id
        },
        mode=StartMode.RESET_STACK
    )


@inject
async def get_campaigns(
        dialog_manager: DialogManager,
        campaign_service: FromDishka[CampaignService],
        **kwargs
):
    campaigns = await campaign_service.get_of_advertiser(
        dialog_manager.start_data["advertiser_id"]
    )
    return {
        "campaigns": campaigns
    }


@inject
async def get_advertiser(
        dialog_manager: DialogManager,
        advertiser_service: FromDishka[AdvertiserService],
        **kwargs
):
    advertiser = await advertiser_service.get_advertiser(
        dialog_manager.start_data["advertiser_id"]
    )
    dialog_manager.dialog_data["advertiser"] = advertiser
    return {
        "advertiser": advertiser
    }


async def to_list_campaigns(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.switch_to(AdvertiserMenuStates.campaign_list)


async def to_create_campaign(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.start(
        CreateCampaignStates.set_ad_title,
        data={
            "advertiser_id": manager.start_data["advertiser_id"],
        },
        mode=StartMode.RESET_STACK
    )


async def to_total_stats(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.switch_to(AdvertiserMenuStates.total_stats)


async def to_daily_stats(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.switch_to(AdvertiserMenuStates.daily_stats)


async def to_main_menu(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.start(
        MainMenuStates.main,
        mode=StartMode.RESET_STACK
    )


@inject
async def stats_getter(
        dialog_manager: DialogManager,
        advertiser_service: FromDishka[AdvertiserService],
        **kwargs
):
    metrics = await advertiser_service.get_stats(
        dialog_manager.dialog_data["advertiser"].id
    )
    return {
        "metrics": metrics
    }


@inject
async def daily_stats_getter(
        dialog_manager: DialogManager,
        advertiser_service: FromDishka[AdvertiserService],
        plotter: FromDishka[Plotter],
        **kwargs
):
    metrics = await advertiser_service.get_daily_stats(
        dialog_manager.dialog_data["advertiser"].id
    )
    days, views, clicks = convert_daily_stats_for_plotter(metrics)
    photo_path = plotter.plot_views_and_clicks(days, views, clicks)
    return {
        "metrics_photo": photo_path
    }
