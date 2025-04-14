from typing import AsyncIterable

from dishka import Provider, from_context, Scope, provide, AnyOf
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from prodadvert.application.interactors.advertisements import GetAdvertInteractor, ClickAdvertInteractor
from prodadvert.application.interactors.advertisers import GetAdvertiserInteractor, BulkAdvertiserCreateInteractor, \
    SetMLScoreInteractor
from prodadvert.application.interactors.ai import TextGenerationInteractor
from prodadvert.application.interactors.campaigns import GetCampaignInteractor, ListCampaignsInteractor, \
    CreateCampaignInteractor, UpdateCampaignInteractor, DeleteCampaignInteractor, SetCampaignImageInteractor
from prodadvert.application.interactors.clients import GetClientInteractor, BulkClientCreateInteractor
from prodadvert.application.interactors.metrics import GetCampaignMetricsInteractor, GetDailyCampaignMetricsInteractor, \
    GetDailyAdvertiserMetricsInteractor, GetAdvertiserMetricsInteractor
from prodadvert.application.interactors.profanity import SetWordsBlacklistInteractor, ToggleModerationInteractor
from prodadvert.application.interfaces.advertisers import AdvertiserGateway
from prodadvert.application.interfaces.ai import TextGenerator
from prodadvert.application.interfaces.campaigns import CampaignGateway
from prodadvert.application.interfaces.clients import ClientGateway
from prodadvert.application.interfaces.common import DBSession
from prodadvert.application.interfaces.date import DateProvider
from prodadvert.application.interfaces.metrics import MetricsGateway
from prodadvert.application.interfaces.profanity import ProfanityGateway
from prodadvert.application.interfaces.storage import FileStorage
from prodadvert.config import Config
from prodadvert.infrastructure.ai.text_generator import TextGeneratorImpl
from prodadvert.infrastructure.persistence.advertisers import AdvertiserGatewayImpl
from prodadvert.infrastructure.persistence.campaigns import CampaignGatewayImpl
from prodadvert.infrastructure.persistence.clients import ClientGatewayImpl
from prodadvert.infrastructure.persistence.database import create_session_maker
from prodadvert.infrastructure.persistence.date import CachedDatabaseDateProvider
from prodadvert.infrastructure.persistence.metrics import MetricsGatewayImpl
from prodadvert.infrastructure.persistence.profanity import ProfanityGatewayImpl
from prodadvert.infrastructure.persistence.s3 import S3Storage


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return create_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AnyOf[AsyncSession, DBSession]]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_date_provider(self, session: AsyncSession) -> DateProvider:
        provider = CachedDatabaseDateProvider(session)
        await provider.load()
        return provider

    client_gateway = provide(
        ClientGatewayImpl,
        scope=Scope.REQUEST,
        provides=ClientGateway
    )
    advertiser_gateway = provide(
        AdvertiserGatewayImpl,
        scope=Scope.REQUEST,
        provides=AdvertiserGateway
    )
    campaign_gateway = provide(
        CampaignGatewayImpl,
        scope=Scope.REQUEST,
        provides=CampaignGateway
    )
    metrics_gateway = provide(
        MetricsGatewayImpl,
        scope=Scope.REQUEST,
        provides=MetricsGateway
    )
    profanity_gateway = provide(
        ProfanityGatewayImpl,
        scope=Scope.REQUEST,
        provides=ProfanityGateway
    )
    s3_storage = provide(
        S3Storage,
        scope=Scope.REQUEST,
        provides=FileStorage
    )
    text_generator = provide(
        TextGeneratorImpl,
        scope=Scope.REQUEST,
        provides=TextGenerator
    )

    get_client_interactor = provide(
        GetClientInteractor, scope=Scope.REQUEST
    )
    create_clients_interactor = provide(
        BulkClientCreateInteractor, scope=Scope.REQUEST
    )
    get_advertiser_interactor = provide(
        GetAdvertiserInteractor, scope=Scope.REQUEST
    )
    create_advertisers_interactor = provide(
        BulkAdvertiserCreateInteractor, scope=Scope.REQUEST
    )
    set_ml_score_interactor = provide(
        SetMLScoreInteractor, scope=Scope.REQUEST
    )
    get_campaign_interactor = provide(
        GetCampaignInteractor, scope=Scope.REQUEST
    )
    list_campaigns_interactor = provide(
        ListCampaignsInteractor, scope=Scope.REQUEST
    )
    create_campaign_interactor = provide(
        CreateCampaignInteractor, scope=Scope.REQUEST
    )
    update_campaign_interactor = provide(
        UpdateCampaignInteractor, scope=Scope.REQUEST
    )
    delete_campaign_interactor = provide(
        DeleteCampaignInteractor, scope=Scope.REQUEST
    )
    get_advert_interactor = provide(
        GetAdvertInteractor, scope=Scope.REQUEST
    )
    count_click_interactor = provide(
        ClickAdvertInteractor, scope=Scope.REQUEST
    )
    get_campaign_metrics_interactor = provide(
        GetCampaignMetricsInteractor, scope=Scope.REQUEST
    )
    get_daily_campaign_metrics_interactor = provide(
        GetDailyCampaignMetricsInteractor, scope=Scope.REQUEST
    )
    get_advertiser_metrics_interactor = provide(
        GetAdvertiserMetricsInteractor, scope=Scope.REQUEST
    )
    get_daily_advertiser_metrics_interactor = provide(
        GetDailyAdvertiserMetricsInteractor, scope=Scope.REQUEST
    )
    set_campaign_image_interactor = provide(
        SetCampaignImageInteractor, scope=Scope.REQUEST
    )
    set_word_blacklist_interactor = provide(
        SetWordsBlacklistInteractor, scope=Scope.REQUEST
    )
    text_generation_interactor = provide(
        TextGenerationInteractor, scope=Scope.REQUEST
    )
    toggle_moderation_interactor = provide(
        ToggleModerationInteractor, scope=Scope.REQUEST
    )
