from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post
from litestar.params import Parameter

from prodadvert.application.exceptions import NotFoundException
from prodadvert.application.interactors.advertisements import GetAdvertInteractor, ClickAdvertInteractor
from prodadvert.application.interactors.metrics import GetCampaignMetricsInteractor, GetAdvertiserMetricsInteractor, \
    GetDailyCampaignMetricsInteractor, GetDailyAdvertiserMetricsInteractor
from prodadvert.controllers.http.openapi import error_spec, success_spec
from prodadvert.controllers.http.schemas import AdvertisementResponse, ClickRequestSchema, MetricsResponse, \
    MetricsWithDateResponse


class AdvertisementsController(Controller):
    path = "/ads"
    tags = ["Advertisements"]

    @get(
        path="",
        description=(
            "Get the best advertisement for given `client_id`. "
            "If no suitable advertisement found, 404 returned."
        ),
        responses={
            200: success_spec("Advertisement found", AdvertisementResponse),
            404: error_spec("No advertisement or client found"),
            400: error_spec("Bad request"),
        }
    )
    @inject
    async def get_advert(
            self,
            client_id: UUID,
            interactor: FromDishka[GetAdvertInteractor],
    ) -> AdvertisementResponse:
        campaign = await interactor(client_id)
        if campaign is None:
            raise NotFoundException
        return AdvertisementResponse(
            ad_id=campaign.id,
            ad_title=campaign.ad_title,
            ad_text=campaign.ad_text,
            advertiser_id=campaign.advertiser.id
        )

    @post(
        path="/{ad_id:uuid}/click",
        status_code=204,
        description=(
            "Count click of given `client_id` on given `ad_id`. "
            "Click can be only counted if client has already seen "
            "the advertisement."
        ),
        responses={
            204: success_spec("Click counted."),
            404: error_spec("No advertisement or client found."),
            403: error_spec("Client hasn't seen this advertisement."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def count_click(
            self,
            ad_id: UUID,
            data: ClickRequestSchema,
            interactor: FromDishka[ClickAdvertInteractor]
    ) -> None:
        await interactor(ad_id, data.client_id)


class MetricsController(Controller):
    path = "/stats"
    tags = ["Statistics"]

    @get(
        path="/campaigns/{campaign_id:uuid}",
        description=(
            "Get aggregated stats for given `campaign_id`."
        ),
        responses={
            200: success_spec("Stats successfully retrieved", MetricsResponse),
            404: error_spec("No such campaign found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def get_campaign_metrics(
            self,
            campaign_id: UUID,
            interactor: FromDishka[GetCampaignMetricsInteractor]
    ) -> MetricsResponse:
        metrics = await interactor(campaign_id)
        return MetricsResponse(
            impressions_count=metrics.views,
            clicks_count=metrics.clicks,
            spent_impressions=metrics.spent_views,
            spent_clicks=metrics.spent_clicks,
            spent_total=metrics.spent_total,
            conversion=metrics.conversion
        )

    @get(
        path="/advertisers/{advertiser_id:uuid}/campaigns",
        description=(
            "Get aggregated stats for given `advertiser_id`. "
            "Summarises all stats of all campaigns of given "
            "advertiser."
        ),
        responses={
            200: success_spec("Stats successfully retrieved", MetricsResponse),
            404: error_spec("No such advertiser found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def get_advertiser_metrics(
            self,
            advertiser_id: UUID,
            interactor: FromDishka[GetAdvertiserMetricsInteractor]
    ) -> MetricsResponse:
        metrics = await interactor(advertiser_id)
        return MetricsResponse(
            impressions_count=metrics.views,
            clicks_count=metrics.clicks,
            spent_impressions=metrics.spent_views,
            spent_clicks=metrics.spent_clicks,
            spent_total=metrics.spent_total,
            conversion=metrics.conversion
        )

    @get(
        path="/campaigns/{campaign_id:uuid}/daily",
        description=(
            "Get aggregated stats history for given `campaign_id` by days. "
            "\n\n"
            "Note: only days with at least some activity on campaign are "
            "returned. If there were no clicks/views on day `x` => it won't "
            "be included in the response."
            "\n\n"
            "Supports pagination by days."
        ),
        responses={
            200: success_spec("Stats successfully retrieved", list[MetricsResponse]),
            404: error_spec("No such campaign found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def get_daily_campaign_metrics(
            self,
            campaign_id: UUID,
            interactor: FromDishka[GetDailyCampaignMetricsInteractor],
            date_from: Annotated[
                int,
                Parameter(description="Start of pagination range.")
            ] = 0,
            date_to: Annotated[
                int, Parameter(description=(
                    "End of pagination range (inclusive). "
                    "If -1, then unlimited"
                ))
            ] = -1,
    ) -> list[MetricsWithDateResponse]:
        metrics = await interactor(campaign_id, date_from, date_to)
        return [
            MetricsWithDateResponse(
                impressions_count=metric.views,
                clicks_count=metric.clicks,
                spent_impressions=metric.spent_views,
                spent_clicks=metric.spent_clicks,
                spent_total=metric.spent_total,
                conversion=metric.conversion,
                date=metric.date
            ) for metric in metrics
        ]

    @get(
        path="/advertisers/{advertiser_id:uuid}/campaigns/daily",
        description=(
            "Get aggregated stats history for given `advertiser_id` by days. "
            "\n\n"
            "Note: only days with at least some activity on any of campaigns "
            "of this advertiser are returned. If there were no clicks/views "
            "on day `x` => it won't be included in the response."
            "\n\n"
            "Supports pagination by days."
        ),
        responses={
            200: success_spec("Stats successfully retrieved", list[MetricsResponse]),
            404: error_spec("No such advertiser found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def get_daily_advertiser_metrics(
            self,
            advertiser_id: UUID,
            interactor: FromDishka[GetDailyAdvertiserMetricsInteractor],
            date_from: Annotated[
                int,
                Parameter(description="Start of pagination range.")
            ] = 0,
            date_to: Annotated[
                int, Parameter(description=(
                        "End of pagination range (inclusive). "
                        "If -1, then unlimited"
                ))
            ] = -1,
    ) -> list[MetricsWithDateResponse]:
        metrics = await interactor(advertiser_id, date_from, date_to)
        return [
            MetricsWithDateResponse(
                impressions_count=metric.views,
                clicks_count=metric.clicks,
                spent_impressions=metric.spent_views,
                spent_clicks=metric.spent_clicks,
                spent_total=metric.spent_total,
                conversion=metric.conversion,
                date=metric.date
            ) for metric in metrics
        ]
