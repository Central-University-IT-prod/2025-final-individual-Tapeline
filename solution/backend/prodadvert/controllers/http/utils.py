from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, post, get, put

from prodadvert.application.interactors.profanity import SetWordsBlacklistInteractor, ToggleModerationInteractor
from prodadvert.application.interfaces.date import DateProvider
from prodadvert.application.interfaces.profanity import ProfanityGateway
from prodadvert.controllers.http.openapi import success_spec, error_spec
from prodadvert.controllers.http.schemas import AdvanceTimeSchema, PingResponse, ProfanitySystemStatusResponse


class TimeController(Controller):
    path = "/time"
    tags = ["Utilities"]

    @post(
        path="/advance",
        status_code=200,
        description=(
            "Set the current date in the system."
        )
    )
    @inject
    async def advance_time(
            self,
            data: AdvanceTimeSchema,
            date_provider: FromDishka[DateProvider],
    ) -> AdvanceTimeSchema:
        await date_provider.set_today(data.current_date)
        return AdvanceTimeSchema(current_date=date_provider.today())


class PingController(Controller):
    tags = ["Utilities"]

    @get(
        path="/ping",
        description=(
            "Check if system is alive."
        )
    )
    @inject
    async def ping(
            self, date_provider: FromDishka[DateProvider]
    ) -> PingResponse:
        await date_provider.load()
        return PingResponse(
            current_date=date_provider.today()
        )


class ProfanityController(Controller):
    path = "/profanity"
    tags = ["Moderation"]

    @put(
        path="/blacklist",
        status_code=204,
        description=(
            "Set blacklist of words (please include all possible forms!)"
        ),
        responses={
            204: success_spec("Blacklist set."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def set_blacklist(
            self,
            data: list[str],
            interactor: FromDishka[SetWordsBlacklistInteractor]
    ) -> None:
        await interactor(data)

    @put(
        path="/enable",
        status_code=204,
        description=(
            "Enable automatic moderation"
        ),
    )
    @inject
    async def enable_moderation(
            self,
            interactor: FromDishka[ToggleModerationInteractor]
    ) -> None:
        await interactor(True)

    @put(
        path="/disable",
        status_code=204,
        description=(
            "Disable automatic moderation"
        ),
    )
    @inject
    async def disable_moderation(
            self,
            interactor: FromDishka[ToggleModerationInteractor]
    ) -> None:
        await interactor(False)

    @get(
        path="/enabled",
        description=(
            "Check if automatic moderation is enabled"
        ),
    )
    @inject
    async def get_moderation_enabled(
            self,
            profanity_gateway: FromDishka[ProfanityGateway]
    ) -> ProfanitySystemStatusResponse:
        return ProfanitySystemStatusResponse(
            is_enabled=await profanity_gateway.is_moderation_enabled()
        )
