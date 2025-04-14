from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable


def is_null(data_name: str):
    def inner(data: dict, widget: Whenable, manager: DialogManager):
        return data.get(data_name) is None
    return inner
