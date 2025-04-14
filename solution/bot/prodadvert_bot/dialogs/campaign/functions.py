from _operator import attrgetter
from typing import Any, cast
from io import BytesIO

from aiogram.types import CallbackQuery, Message, URLInputFile
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.input.text import OnSuccess, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from prodadvert_bot.application.entities import Campaign
from prodadvert_bot.application.exceptions import CampaignCreateException
from prodadvert_bot.application.interfaces.advertisers import convert_daily_stats_for_plotter
from prodadvert_bot.application.interfaces.campaigns import CampaignService
from prodadvert_bot.application.interfaces.plotter import Plotter
from prodadvert_bot.config import Config
from prodadvert_bot.dialogs.advertiser.states import AdvertiserMenuStates
from prodadvert_bot.dialogs.campaign.states import CampaignMenuStates


@inject
async def get_campaign(
        dialog_manager: DialogManager,
        campaign_service: FromDishka[CampaignService],
        config: FromDishka[Config],
        **kwargs
):
    campaign = await campaign_service.get(
        dialog_manager.start_data["advertiser_id"],
        dialog_manager.start_data["campaign_id"],
    )
    image_url = None
    if campaign.image_uri:
        image_url = f"{config.s3.base_url}{campaign.image_uri}"
    dialog_manager.dialog_data["image_url"] = image_url
    dialog_manager.dialog_data["campaign"] = campaign
    print(image_url)
    return {
        "campaign": campaign,
        "image_url": image_url
    }


async def to_advertiser_menu(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.start(
        AdvertiserMenuStates.overview,
        data={
            "advertiser_id": manager.start_data["advertiser_id"]
        },
        mode=StartMode.RESET_STACK
    )


@inject
async def stats_getter(
        dialog_manager: DialogManager,
        campaign_service: FromDishka[CampaignService],
        **kwargs
):
    metrics = await campaign_service.get_stats(
        dialog_manager.dialog_data["campaign"].id
    )
    print(metrics)
    return {
        "metrics": metrics
    }


@inject
async def daily_stats_getter(
        dialog_manager: DialogManager,
        campaign_service: FromDishka[CampaignService],
        plotter: FromDishka[Plotter],
        **kwargs
):
    metrics = await campaign_service.get_daily_stats(
        dialog_manager.dialog_data["campaign"].id
    )
    days, views, clicks = convert_daily_stats_for_plotter(metrics)
    photo_path = plotter.plot_views_and_clicks(days, views, clicks)
    return {
        "metrics_photo": photo_path
    }


class InputAndApply[T](OnSuccess[T]):
    def __init__(self, prop_name: str, data_transform):
        super().__init__()
        self.prop_name = prop_name
        self.data_transform = data_transform

    async def __call__(
            self,
            message: Message,
            widget: ManagedTextInput[T],
            dialog_manager: DialogManager,
            data: T,
    ) -> Any:
        data = self.data_transform(data)
        campaign = cast(
            Campaign,
            dialog_manager.current_context().dialog_data["campaign"]
        )
        try:
            await _update(campaign.advertiser_id, campaign.id, {
                "ad_title": campaign.ad_title,
                "ad_text": campaign.ad_text,
                "target_gender": campaign.target_gender,
                "target_age_from": campaign.target_age_from,
                "target_age_to": campaign.target_age_to,
                "target_location": campaign.target_location
            } | {self.prop_name: data})
            setattr(campaign, self.prop_name, data)
        except CampaignCreateException as exc:
            await message.reply("Error: " + str(exc))
        await dialog_manager.switch_to(CampaignMenuStates.settings)


async def _update(
        adv_id, cmp_id, dict_args,
):
    # Because @inject does not want to work with class above
    from prodadvert_bot.main import config
    from prodadvert_bot.infrastructure.campaign_service import CampaignServiceImpl
    campaign_service = CampaignServiceImpl(config)
    await campaign_service.update(adv_id, cmp_id, **dict_args)


class AgeRange:
    def __init__(self, data: str) -> None:
        components = data.split("-")
        if len(components) != 2:
            raise ValueError
        self.start, self.end = components
        if not self.start:
            self.start = None
        else:
            self.start = int(self.start)
        if not self.end:
            self.end = None
        else:
            self.end = int(self.end)


class ApplyAgeRange(OnSuccess[AgeRange]):
    async def __call__(
            self,
            message: Message,
            widget: ManagedTextInput[AgeRange],
            dialog_manager: DialogManager,
            data: AgeRange,
    ) -> Any:
        campaign = cast(
            Campaign,
            dialog_manager.current_context().dialog_data["campaign"]
        )
        try:
            await _update(campaign.advertiser_id, campaign.id, {
                "ad_title": campaign.ad_title,
                "ad_text": campaign.ad_text,
                "target_gender": campaign.target_gender,
                "target_age_from": data.start,
                "target_age_to": data.end,
                "target_location": campaign.target_location
            })
            campaign.target_age_from = data.start
            campaign.target_age_to = data.end
        except CampaignCreateException as exc:
            await message.reply("Error: " + str(exc))
        await dialog_manager.switch_to(CampaignMenuStates.settings)


@inject
async def apply_target_gender(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        item_id: str,
        campaign_service: FromDishka[CampaignService]
):
    campaign = cast(
        Campaign,
        manager.current_context().dialog_data["campaign"]
    )
    try:
        await _update(campaign.advertiser_id, campaign.id, {
            "ad_title": campaign.ad_title,
            "ad_text": campaign.ad_text,
            "target_gender": item_id,
            "target_age_from": campaign.target_age_from,
            "target_age_to": campaign.target_age_to,
            "target_location": campaign.target_location
        })
        campaign.target_gender = item_id
    except CampaignCreateException as exc:
        await callback.reply("Error: " + str(exc))
    await manager.switch_to(CampaignMenuStates.settings)


@inject
async def apply_delete_image(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        campaign_service: FromDishka[CampaignService]
):
    await campaign_service.delete_image(
        manager.current_context().start_data["advertiser_id"],
        manager.current_context().start_data["campaign_id"]
    )
    await manager.switch_to(CampaignMenuStates.settings)


@inject
async def image_handler(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager,
        campaign_service: FromDishka[CampaignService]
):
    photo = max(message.photo, key=attrgetter("width"))
    file = await message.bot.get_file(photo.file_id)
    f_io = BytesIO()
    await message.bot.download_file(file.file_path, f_io)
    await campaign_service.upload_image(
        manager.current_context().start_data["advertiser_id"],
        manager.current_context().start_data["campaign_id"],
        f_io
    )
    await manager.switch_to(CampaignMenuStates.settings)


@inject
async def to_image_settings(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
):
    # if "image_url" in manager.current_context().dialog_data:
    #     await callback.message.answer_photo(
    #         URLInputFile(
    #             manager.current_context().dialog_data["image_url"],
    #             filename="thumbnail.png"
    #         )
    #     )
    await manager.switch_to(CampaignMenuStates.edit_image)
