"""Defines metrics interactors."""

from uuid import UUID

from dishka import FromDishka

from prodadvert.application.exceptions import NotFoundException
from prodadvert.application.interfaces.advertisers import AdvertiserGateway
from prodadvert.application.interfaces.campaigns import CampaignGateway
from prodadvert.application.interfaces.metrics import MetricsGateway, Metrics, DailyMetrics
from prodadvert.decorators import raises


class GetCampaignMetricsInteractor:
    """Get metrics for campaign."""

    def __init__(
            self,
            campaign_gateway: FromDishka[CampaignGateway],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.campaign_gateway = campaign_gateway
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    async def __call__(self, campaign_id: UUID) -> Metrics:
        await self.campaign_gateway.get_by_only_id(campaign_id)
        return await self.metrics_gateway.get_stats_of_campaign(campaign_id)


class GetDailyCampaignMetricsInteractor:
    """Get daily metrics for campaign."""

    def __init__(
            self,
            campaign_gateway: FromDishka[CampaignGateway],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.campaign_gateway = campaign_gateway
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    async def __call__(
            self,
            campaign_id: UUID,
            from_day: int,
            to_day: int
    ) -> list[DailyMetrics]:
        await self.campaign_gateway.get_by_only_id(campaign_id)
        return await self.metrics_gateway.get_daily_stats_of_campaign(
            campaign_id, from_day, to_day
        )


class GetAdvertiserMetricsInteractor:
    """Get aggregated metrics for advertiser."""

    def __init__(
            self,
            advertiser_gateway: FromDishka[AdvertiserGateway],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.advertiser_gateway = advertiser_gateway
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    async def __call__(self, advertiser_id: UUID) -> Metrics:
        await self.advertiser_gateway.get_advertiser_by_id(advertiser_id)
        return await self.metrics_gateway.get_stats_of_advertiser(
            advertiser_id
        )


class GetDailyAdvertiserMetricsInteractor:
    """Get daily aggregated metrics for advertiser."""

    def __init__(
            self,
            advertiser_gateway: FromDishka[AdvertiserGateway],
            metrics_gateway: FromDishka[MetricsGateway]
    ) -> None:
        self.advertiser_gateway = advertiser_gateway
        self.metrics_gateway = metrics_gateway

    @raises(NotFoundException)
    async def __call__(
            self,
            advertiser_id: UUID,
            from_day: int,
            to_day: int
    ) -> list[DailyMetrics]:
        await self.advertiser_gateway.get_advertiser_by_id(advertiser_id)
        return await self.metrics_gateway.get_daily_stats_of_advertiser(
            advertiser_id, from_day, to_day
        )
