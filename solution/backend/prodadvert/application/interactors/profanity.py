from dishka import FromDishka

from prodadvert.application.interfaces.profanity import ProfanityGateway
from prodadvert.domain.moderation import enrich_blacklist


class SetWordsBlacklistInteractor:
    def __init__(
            self, profanity_gateway: FromDishka[ProfanityGateway]
    ) -> None:
        self.profanity_gateway = profanity_gateway

    async def __call__(self, blacklist: list[str]) -> None:
        enriched = enrich_blacklist(blacklist)
        await self.profanity_gateway.set_blacklist(enriched)


class ToggleModerationInteractor:
    def __init__(
            self, profanity_gateway: FromDishka[ProfanityGateway]
    ) -> None:
        self.profanity_gateway = profanity_gateway

    async def __call__(self, enabled: bool) -> None:
        await self.profanity_gateway.set_moderation_enabled(enabled)
