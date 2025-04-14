"""Defines advertisements interactors."""
from uuid import UUID

from dishka import FromDishka

from prodadvert.application.exceptions import NotFoundException, ForbiddenException
from prodadvert.application.interfaces.campaigns import CampaignGateway
from prodadvert.application.interfaces.clients import ClientGateway
from prodadvert.application.interfaces.date import DateProvider
from prodadvert.application.interfaces.metrics import MetricsGateway
from prodadvert.decorators import raises
from prodadvert.domain.entities import Campaign
from prodadvert.domain.recommendation import Recommender


class GetAdvertInteractor:
    """Get advert for client."""

    def __init__(
            self,
            client_gateway: FromDishka[ClientGateway],
            campaign_gateway: FromDishka[CampaignGateway],
            date_provider: FromDishka[DateProvider],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.client_gateway = client_gateway
        self.campaign_gateway = campaign_gateway
        self.date_provider = date_provider
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    async def __call__(self, client_id: UUID) -> Campaign | None:
        #s = time.time()
        client = await self.client_gateway.get_client_by_id(client_id)
        #print("CLIENT", (time.time() - s)*1000)
        #s = time.time()
        all_campaigns = await self.campaign_gateway.get_all_from_all_advertisers()
        #print("all_campaigns", (time.time() - s)*1000)
        #s = time.time()
        campaigns_clicks = await self.metrics_gateway.get_clicks_for_each()
        #print("campaigns_clicks", (time.time() - s)*1000)
        #s = time.time()
        campaigns_views = await self.metrics_gateway.get_views_for_each()
        #print("campaigns_views", (time.time() - s)*1000)
        #s = time.time()
        client_seen = await self.metrics_gateway.get_client_seen(client_id)
        #print("client_seen", (time.time() - s)*1000)
        #s = time.time()
        await self.date_provider.load()
        current_date = self.date_provider.today()
        #print("current_date", (time.time() - s)*1000)
        recommender = Recommender(
            client,
            all_campaigns,
            current_date,
            campaigns_clicks,
            campaigns_views,
            client_seen
        )
        #s = time.time()
        best_campaign = recommender.get_best_campaign()
        #print("best_campaign", (time.time() - s)*1000)
        if not best_campaign:
            return None
        #s = time.time()
        await self.metrics_gateway.count_view(
            client_id,
            best_campaign,
            self.date_provider.today()
        )
        #print("count_view", (time.time() - s)*1000)
        return best_campaign


class ClickAdvertInteractor:
    def __init__(
            self,
            client_gateway: FromDishka[ClientGateway],
            campaign_gateway: FromDishka[CampaignGateway],
            date_provider: FromDishka[DateProvider],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.client_gateway = client_gateway
        self.campaign_gateway = campaign_gateway
        self.date_provider = date_provider
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    @raises(ForbiddenException)
    async def __call__(
            self, ad_id: UUID, client_id: UUID
    ) -> None:
        client = await self.client_gateway.get_client_by_id(client_id)
        campaign = await self.campaign_gateway.get_by_only_id(ad_id)
        client_seen = await self.metrics_gateway.get_client_seen(client_id)
        if ad_id not in client_seen:
            raise ForbiddenException
        await self.date_provider.load()
        await self.metrics_gateway.count_click(
            client.id,
            campaign,
            self.date_provider.today()
        )
