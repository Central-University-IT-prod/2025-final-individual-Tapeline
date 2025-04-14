from aiogram_dialog import DialogManager


async def get_from_dialog_data(
        dialog_manager: DialogManager,
        **kwargs
):
    return dialog_manager.dialog_data
