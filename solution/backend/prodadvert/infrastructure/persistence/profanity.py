from _operator import attrgetter

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.application.interfaces.profanity import ProfanityGateway
from prodadvert.infrastructure.persistence.models import BannedWordModel, StoredSettings


class ProfanityGatewayImpl(ProfanityGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def set_blacklist(self, blacklist: list[str]) -> None:
        await self._session.execute(delete(BannedWordModel))
        for i, word in enumerate(blacklist):
            self._session.add(BannedWordModel(id=i, word=word))
        await self._session.commit()

    async def get_blacklist(self) -> list[str]:
        models = await self._session.execute(select(BannedWordModel))
        return list(map(attrgetter("word"), models.scalars().all()))

    async def is_moderation_enabled(self) -> bool:
        settings = await StoredSettings.load(self._session)
        return settings.moderation_enabled

    async def set_moderation_enabled(self, enabled: bool) -> None:
        await self._session.execute(
            update(StoredSettings).values(moderation_enabled=enabled)
        )
        await self._session.commit()
