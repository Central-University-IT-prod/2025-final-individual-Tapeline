from aiogram import Bot, Router, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from prodadvert_bot.dialogs.advertiser.dialog import advertiser_menu
from prodadvert_bot.dialogs.campaign.dialog import campaign_menu
from prodadvert_bot.dialogs.create_campaign.dialog import create_campaign_dialog
from prodadvert_bot.dialogs.main_menu.dialog import main_menu
from prodadvert_bot.dialogs.main_menu.states import MainMenuStates


class AppBot(Bot):
    """Main bot class."""

    def __init__(self, token: str):
        super().__init__(
            token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.storage = MemoryStorage()
        self.dispatcher = Dispatcher(storage=self.storage)
        self.router = Router()

        self.dispatcher.include_router(main_menu)
        self.dispatcher.include_router(advertiser_menu)
        self.dispatcher.include_router(create_campaign_dialog)
        self.dispatcher.include_router(campaign_menu)
        self.dispatcher.message(Command("start"))(self.start_command)

        setup_dialogs(self.dispatcher)

    async def run(self):
        """Starts the bot."""
        await self.dispatcher.start_polling(self)

    async def start_command(self, message: Message, dialog_manager: DialogManager):
        await dialog_manager.start(
            MainMenuStates.main,
            mode=StartMode.RESET_STACK
        )
