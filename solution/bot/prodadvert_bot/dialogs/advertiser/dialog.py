from _operator import attrgetter

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Group, Button, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Jinja, Const, Format

from prodadvert_bot.dialogs.advertiser import functions
from prodadvert_bot.dialogs.advertiser.states import AdvertiserMenuStates


def advertiser_not_found(data: dict, widget: Whenable, manager: DialogManager):
    return data.get("advertiser") is None


def advertiser_found(data: dict, widget: Whenable, manager: DialogManager):
    return data.get("advertiser") is not None


advertiser_menu = Dialog(
    Window(
        Jinja(
            "💈 <b>Advertiser {{ advertiser.name }}.</b>\n"
            "(<code>{{ advertiser.id }}</code>)",
            when=advertiser_found
        ),
        Jinja(
            "❌ Advertiser <code>{{ advertiser_id }}</code> is not found.",
            when=advertiser_not_found
        ),
        Group(
            Group(
                Button(
                    Const("📣 List campaigns"),
                    id="list_campaigns",
                    on_click=functions.to_list_campaigns
                ),
                Button(
                    Const("🆕 Create campaign"),
                    id="create_campaign",
                    on_click=functions.to_create_campaign
                ),
                width=2
            ),
            Group(
                Button(
                    Const("📊 Total stats"),
                    id="total_stats",
                    on_click=functions.to_total_stats
                ),
                Button(
                    Const("📈 Daily stats"),
                    id="daily_stats",
                    on_click=functions.to_daily_stats
                ),
                width=2
            ),
            when=advertiser_found
        ),
        Button(
            Const("⬅️ To main menu"),
            id="to_main_menu",
            on_click=functions.to_main_menu
        ),
        state=AdvertiserMenuStates.overview
    ),
    Window(
        Jinja(
            "<b>Campaigns of {{ advertiser.name }}.</b>"
        ),
        ScrollingGroup(
            Select(
                Format("📣 {item.ad_title}"),
                id="campaign_id",
                item_id_getter=attrgetter("id"),
                items="campaigns",
                on_click=functions.select_campaign_id
            ),
            width=1,
            height=8,
            id="campaign_scrolling"
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=AdvertiserMenuStates.overview
        ),
        getter=functions.get_campaigns,
        state=AdvertiserMenuStates.campaign_list,
    ),
    Window(
        Jinja(
            "📊 <b>{{ advertiser.name }} stats.</b>\n"
            "\n"
            "👁 Views: <code>{{metrics.impressions_count}}</code>\n"
            "👆 Clicks: <code>{{metrics.clicks_count}}</code>\n"
            "🔄 Conversion: <code>{{metrics.conversion}}</code>\n"
            "💵 Expenses:\n"
            "<pre>"
            "Views .... {{metrics.spent_impressions}}\n"
            "Clicks ... {{metrics.spent_clicks}}\n"
            "Total .... {{metrics.spent_total}}"
            "</pre>"
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=AdvertiserMenuStates.overview
        ),
        getter=functions.stats_getter,
        state=AdvertiserMenuStates.total_stats
    ),
    Window(
        StaticMedia(
            path=Format("{metrics_photo}"),
            type=ContentType.PHOTO,
        ),
        Jinja(
            "📈 <b>{{ advertiser.name }} daily stats.</b>"
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=AdvertiserMenuStates.overview
        ),
        getter=functions.daily_stats_getter,
        state=AdvertiserMenuStates.daily_stats
    ),
    getter=functions.get_advertiser,
)
