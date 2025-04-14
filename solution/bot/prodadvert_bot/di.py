from dishka import Provider, from_context, Scope, provide

from prodadvert_bot.application.interfaces.advertisers import AdvertiserService
from prodadvert_bot.application.interfaces.campaigns import CampaignService
from prodadvert_bot.application.interfaces.plotter import Plotter
from prodadvert_bot.application.interfaces.text_generator import TextGenerator
from prodadvert_bot.config import Config
from prodadvert_bot.infrastructure.advertiser_service import AdvertiserServiceImpl
from prodadvert_bot.infrastructure.campaign_service import CampaignServiceImpl
from prodadvert_bot.infrastructure.text_generator import TextGeneratorImpl
from prodadvert_bot.plotter import PlotterImpl


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    advertiser_service = provide(
        AdvertiserServiceImpl,
        scope=Scope.REQUEST,
        provides=AdvertiserService
    )
    campaign_service = provide(
        CampaignServiceImpl,
        scope=Scope.REQUEST,
        provides=CampaignService,
    )
    plotter_impl = provide(
        PlotterImpl,
        scope=Scope.APP,
        provides=Plotter
    )
    text_generator = provide(
        TextGeneratorImpl,
        scope=Scope.APP,
        provides=TextGenerator
    )
