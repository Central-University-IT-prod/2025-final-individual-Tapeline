from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from prodadvert_bot.dialogs.main_menu import functions
from prodadvert_bot.dialogs.main_menu.states import MainMenuStates

main_menu = Dialog(
    Window(
        Const("Welcome to <b>PROD</b>advert!"),
        Button(
            Const("Manage advertiser"),
            id="manage_advertiser",
            on_click=functions.to_advertiser_id_input
        ),
        state=MainMenuStates.main
    ),
    Window(
        Const("💈 <b>Enter advertiser id:</b>"),
        TextInput(
            id="advertiser_id",
            on_success=functions.ToManageAdvertisers(),
            type_factory=str,
        ),
        state=MainMenuStates.enter_advertiser_id,
    ),
)
