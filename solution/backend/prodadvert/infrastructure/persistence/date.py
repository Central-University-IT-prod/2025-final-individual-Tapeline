from typing import Final

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.application.interfaces.date import DateProvider
from prodadvert.infrastructure.persistence.models import StoredSettings

_DEFAULT_DATE: Final[int] = 0


class CachedDatabaseDateProvider(DateProvider):
    _current_date: int | None = None

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def today(self) -> int:
        return CachedDatabaseDateProvider._current_date or _DEFAULT_DATE

    async def load(self) -> None:
        if CachedDatabaseDateProvider._current_date is not None:
            return
        settings = await StoredSettings.load(self._session)
        CachedDatabaseDateProvider._current_date = settings.current_day

    async def set_today(self, current_date: int) -> None:
        CachedDatabaseDateProvider._current_date = current_date
        await self._session.execute(
            update(StoredSettings).values(current_day=current_date)
        )
        await self._session.commit()
