from _operator import itemgetter
from typing import Any, Optional

from aiogram.enums import ContentType
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Group, Button, SwitchTo, Radio
from aiogram_dialog.widgets.media import StaticMedia, Media
from aiogram_dialog.widgets.text import Jinja, Const, Format
from magic_filter import F

from prodadvert_bot.dialogs.campaign import functions
from prodadvert_bot.dialogs.campaign.functions import InputAndApply
from prodadvert_bot.dialogs.campaign.states import CampaignMenuStates
from prodadvert_bot.dialogs.common.filters import is_null


class EditCampaignPropertyWindow(Window):
    def __init__(
            self,
            prop_name: str,
            prop_display_name: str,
            prop_type: type,
            display_at: State,
            data_transform=lambda x: x,
            hint=""
    ) -> None:
        super().__init__(
            Jinja(
                f"✏ <b>Edit {prop_display_name}</b>.\n<i>{hint}</i>"
                "💬 Current: {{campaign." + prop_name + "}}\n" +
                "New:"
            ),
            TextInput(
                id=prop_name,
                on_success=InputAndApply(prop_name, data_transform),
                type_factory=prop_type,
            ),
            SwitchTo(
                Const("🚫 Cancel"), id="cancel", state=CampaignMenuStates.settings
            ),
            state=display_at
        )


async def error_invalid_age_range(
        message: Message,
        dialog: Any,
        manager: DialogManager,
        error: ValueError
):
    await message.answer("❌ Age range must be AGE_FROM-AGE_TO\nExample: 10-20")


campaign_menu = Dialog(
    Window(
        StaticMedia(
            url=Format("{image_url}"),
            type=ContentType.PHOTO,
            when=F["image_url"],
            use_pipe=True
        ),
        Jinja(
            "📣 <b>Campaign {{ campaign.ad_title }}.</b>\n"
            "(<code>{{ campaign.id }}</code>)\n"
            "\n"
            "<pre>{{ campaign.ad_text }}</pre>\n"
            "🎯 Target limits: "
            "<code>{{campaign.impressions_limit}}</code> views / "
            "<code>{{campaign.clicks_limit}}</code> clicks\n"
            "💵 Costs: <code>{{campaign.cost_per_impression}}</code> per view"
            " / <code>{{campaign.cost_per_click}}</code> per click\n"
            "📆 Dates: <code>{{campaign.start_date}}</code> - "
            "<code>{{campaign.end_date}}</code>\n"
            "🎯 Targeting:\n"
            "    🚻 Gender: <code>{{campaign.target_gender}}</code>\n"
            "    🕓 Ages: <code>{{campaign.target_age_from}}</code> - "
            "<code>{{campaign.target_age_to}}</code>\n"
            "    📍 Location: <code>{{campaign.target_location}}</code>",
            when=F["campaign"]
        ),
        Jinja(
            "❌ <b>Campaign <code>{{ campaign_id }}</code> is not found.</b>",
            when=is_null("campaign")
        ),
        Group(
            Group(
                SwitchTo(
                    Const("📊 Total stats"),
                    id="total_stats",
                    state=CampaignMenuStates.total_stats
                ),
                SwitchTo(
                    Const("📈 Daily stats"),
                    id="daily_stats",
                    state=CampaignMenuStates.daily_stats
                ),
                width=2
            ),
            when=F["campaign"]
        ),
        SwitchTo(
            Const("⚙ Settings"),
            id="settings",
            state=CampaignMenuStates.settings
        ),
        Button(
            Const("⬅️ To advertiser menu"),
            id="to_advertiser_menu",
            on_click=functions.to_advertiser_menu
        ),
        state=CampaignMenuStates.overview
    ),
    Window(
        Jinja(
            "📊 <b>{{ campaign.ad_title }} stats.</b>\n"
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
            state=CampaignMenuStates.overview
        ),
        getter=functions.stats_getter,
        state=CampaignMenuStates.total_stats
    ),
    Window(
        StaticMedia(
            path=Format("{metrics_photo}"),
            type=ContentType.PHOTO,
        ),
        Jinja(
            "📈 <b>{{ campaign.ad_title }} daily stats.</b>\n"
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=CampaignMenuStates.overview
        ),
        getter=functions.daily_stats_getter,
        state=CampaignMenuStates.daily_stats,
    ),
    Window(
        Jinja(
            "⚙ <b>Settings {{campaign.ad_title}}.</b>",
        ),
        Group(
            Group(
                SwitchTo(
                    Const("✏ Ad title 📝"),
                    id="ad_title",
                    state=CampaignMenuStates.edit_ad_title
                ),
                SwitchTo(
                    Const("✏ Ad text 💬"),
                    id="ad_text",
                    state=CampaignMenuStates.edit_ad_text
                ),
                width=2
            ),
            Group(
                SwitchTo(
                    Const("✏ Target views 👁"),
                    id="target_views",
                    state=CampaignMenuStates.edit_impressions_limit
                ),
                SwitchTo(
                    Const("✏ Target clicks 👆"),
                    id="target_clicks",
                    state=CampaignMenuStates.edit_clicks_limit
                ),
                width=2
            ),
            Group(
                SwitchTo(
                    Const("✏ View cost 👁"),
                    id="view_cost",
                    state=CampaignMenuStates.edit_cost_per_click
                ),
                SwitchTo(
                    Const("✏ Click cost 👆"),
                    id="click_cost",
                    state=CampaignMenuStates.edit_cost_per_impression
                ),
                width=2
            ),
            Group(
                SwitchTo(
                    Const("✏ Start date 📆"),
                    id="start_date",
                    state=CampaignMenuStates.edit_start_date
                ),
                SwitchTo(
                    Const("✏ End date 📆"),
                    id="end_date",
                    state=CampaignMenuStates.edit_end_date
                ),
                width=2
            ),
        ),
        SwitchTo(
            Const("✏ Targeting 🎯"),
            id="targeting",
            state=CampaignMenuStates.edit_targeting
        ),
        Button(
            Const("✏ Image 🖼"),
            id="image",
            on_click=functions.to_image_settings
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=CampaignMenuStates.overview
        ),
        state=CampaignMenuStates.settings
    ),
    EditCampaignPropertyWindow(
        "ad_title", "Title", str, CampaignMenuStates.edit_ad_title
    ),
    EditCampaignPropertyWindow(
        "ad_text", "Text", str, CampaignMenuStates.edit_ad_text
    ),
    EditCampaignPropertyWindow(
        "impressions_limit",
        "Target views count",
        int,
        CampaignMenuStates.edit_impressions_limit
    ),
    EditCampaignPropertyWindow(
        "clicks_limit",
        "Target clicks count",
        int,
        CampaignMenuStates.edit_clicks_limit
    ),
    EditCampaignPropertyWindow(
        "cost_per_impression",
        "Cost per view",
        float,
        CampaignMenuStates.edit_cost_per_impression
    ),
    EditCampaignPropertyWindow(
        "cost_per_click",
        "Cost per click",
        float,
        CampaignMenuStates.edit_cost_per_click
    ),
    EditCampaignPropertyWindow(
        "start_date",
        "Start date",
        int,
        CampaignMenuStates.edit_start_date
    ),
    EditCampaignPropertyWindow(
        "end_date",
        "End date",
        int,
        CampaignMenuStates.edit_end_date
    ),
    Window(
        Jinja("⚙ <b>{{campaign.ad_title}} targeting settings 🎯.</b>"),
        Radio(
            Format("🔳 {item[1]}"),
            Format("⬜️ {item[1]}"),
            id="target_gender",
            item_id_getter=itemgetter(0),
            items=lambda *a, **k: [
                ("MALE", "🚹 Male"),
                ("FEMALE", "🚺 Female"),
                ("ALL", "🚻 All"),
            ],
            on_state_changed=functions.apply_target_gender
        ),
        SwitchTo(
            Const("✏ Set age range 📆"),
            id="set_age_range",
            state=CampaignMenuStates.edit_targeting_age_range
        ),
        SwitchTo(
            Const("✏ Set location 📍"),
            id="set_location",
            state=CampaignMenuStates.edit_targeting_location
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=CampaignMenuStates.settings
        ),
        state=CampaignMenuStates.edit_targeting
    ),
    Window(
        Const("🎯 <b>Targeting age range 📆.</b>"),
        TextInput(
            id="age_range",
            type_factory=functions.AgeRange,
            on_error=error_invalid_age_range,
            on_success=functions.ApplyAgeRange()
        ),
        SwitchTo(
            Const("🚫 Cancel"),
            id="back",
            state=CampaignMenuStates.settings
        ),
        state=CampaignMenuStates.edit_targeting_age_range,
    ),
    EditCampaignPropertyWindow(
        "target_location",
        "Targeting location",
        str,
        CampaignMenuStates.edit_targeting_location,
        data_transform=lambda x: None if x.strip() == "-" else x,
        hint="(Enter <code>-</code> to remove targeting)\n"
    ),
    Window(
        Const("🎯 <b>Edit campaign image 🖼.</b>"),
        Button(
            Const("🗑 Delete image"),
            id="del_img",
            on_click=functions.apply_delete_image
        ),
        SwitchTo(
            Const("⬆️ Upload image"),
            id="upload_img",
            state=CampaignMenuStates.edit_image_input
        ),
        SwitchTo(
            Const("⬅️ Back"),
            id="back",
            state=CampaignMenuStates.settings
        ),
        state=CampaignMenuStates.edit_image
    ),
    Window(
        Const("🖼 <b>Send an image to set it.</b>"),
        MessageInput(
            functions.image_handler,
            content_types=[ContentType.PHOTO]
        ),
        SwitchTo(
            Const("🚫 Cancel"),
            id="back",
            state=CampaignMenuStates.edit_image
        ),
        state=CampaignMenuStates.edit_image_input
    ),
    getter=functions.get_campaign,
)
