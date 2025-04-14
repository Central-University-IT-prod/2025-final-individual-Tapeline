from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import OnSuccess, ManagedTextInput


class InputSetAndNext[T](OnSuccess[T]):
    async def __call__(
            self,
            message: Message,
            widget: ManagedTextInput[T],
            dialog_manager: DialogManager,
            data: T
    ) -> Any:
        dialog_manager.current_context().dialog_data[
            widget.widget.widget_id
        ] = data
        await dialog_manager.next()


class InputSetAndSwitchTo[T](OnSuccess[T]):
    def __init__(self, target):
        self.target = target

    async def __call__(
            self,
            message: Message,
            widget: ManagedTextInput[T],
            dialog_manager: DialogManager,
            data: T
    ) -> Any:
        dialog_manager.current_context().dialog_data[
            widget.widget.widget_id
        ] = data
        await dialog_manager.switch_to(self.target)
