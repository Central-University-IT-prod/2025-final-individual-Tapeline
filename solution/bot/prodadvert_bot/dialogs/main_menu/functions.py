from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.input.text import OnSuccess, T
from aiogram_dialog.widgets.kbd import Button

from prodadvert_bot.dialogs.advertiser.states import AdvertiserMenuStates
from prodadvert_bot.dialogs.main_menu.states import MainMenuStates


async def to_advertiser_id_input(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager
):
    await manager.switch_to(MainMenuStates.enter_advertiser_id)


class ToManageAdvertisers(OnSuccess[str]):
    async def __call__(
            self,
            message: Message,
            widget: ManagedTextInput[T],
            dialog_manager: DialogManager,
            data: T
    ) -> Any:
        print(data)
        await dialog_manager.start(
            AdvertiserMenuStates.overview,
            data={
                "advertiser_id": data,
            },
            mode=StartMode.RESET_STACK
        )
