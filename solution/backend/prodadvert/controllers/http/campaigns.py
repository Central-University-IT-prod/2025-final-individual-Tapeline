from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post, put, delete
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Parameter

from prodadvert.application.dto import NewCampaignDTO, CampaignTargetingDTO, UpdateCampaignDTO
from prodadvert.application.interactors.campaigns import (
    GetCampaignInteractor,
    CreateCampaignInteractor,
    UpdateCampaignInteractor,
    ListCampaignsInteractor,
    DeleteCampaignInteractor, SetCampaignImageInteractor,
)
from prodadvert.application.interfaces.common import PaginationParameters
from prodadvert.controllers.http.openapi import success_spec, error_spec
from prodadvert.controllers.http.schemas import CampaignSchema, CreateCampaignSchema, UpdateCampaignSchema, \
    CampaignTargetingSchema
from prodadvert.domain.entities import Campaign


class CampaignsController(Controller):
    path = "/advertisers/{advertiser_id:uuid}/campaigns"
    tags = ["Campaigns"]

    @get(
        path="/{campaign_id:uuid}",
        description=(
            "Get a single campaign by its uuid."
        ),
        responses={
            200: success_spec("Campaign retrieved.", CampaignSchema),
            404: error_spec("Not found."),
        }
    )
    @inject
    async def get_campaign(
            self,
            advertiser_id: UUID,
            campaign_id: UUID,
            interactor: FromDishka[GetCampaignInteractor],
    ) -> CampaignSchema:
        campaign = await interactor(campaign_id, advertiser_id)
        return _serialize_campaign(campaign)

    @post(
        path="",
        description=(
            "Create a campaign for given advertiser."
            "\n\n"
            "Features an auto-moderation tool."
        ),
        responses={
            201: success_spec("Campaign successfully created.", CampaignSchema),
            404: error_spec("No advertiser found."),
            400: error_spec("Bad request (including moderation error)."),
        }
    )
    @inject
    async def create_campaign(
            self,
            advertiser_id: UUID,
            data: CreateCampaignSchema,
            interactor: FromDishka[CreateCampaignInteractor]
    ) -> CampaignSchema:
        campaign = await interactor(
            advertiser_id,
            NewCampaignDTO(
                advertiser_id=advertiser_id,
                ad_title=data.ad_title,
                ad_text=data.ad_text,
                end_date=data.end_date,
                start_date=data.start_date,
                clicks_limit=data.clicks_limit,
                cost_per_click=data.cost_per_click,
                impressions_limit=data.impressions_limit,
                cost_per_impression=data.cost_per_impression,
                target=CampaignTargetingDTO(
                    gender=data.targeting.gender,
                    age_to=data.targeting.age_to,
                    age_from=data.targeting.age_from,
                    location=data.targeting.location
                )
            )
        )
        return _serialize_campaign(campaign)

    @get(
        path="",
        description=(
            "Get all campaigns of given advertiser with pagination."
        ),
        responses={
            200: success_spec("Campaigns retrieved.", list[CampaignSchema]),
            404: error_spec("Not found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def list_campaigns(
            self,
            advertiser_id: UUID,
            interactor: FromDishka[ListCampaignsInteractor],
            page: Annotated[
                int,
                Parameter(description=(
                    "Pagination page number (starting from 0)."
                ))
            ] = 0,
            size: Annotated[
                int, Parameter(description=(
                    "Size of pagination page. "
                    "If -1, then unlimited"
                ))
            ] = 10,
    ) -> list[CampaignSchema]:
        campaigns = await interactor(advertiser_id, PaginationParameters(
            page=page, page_size=size
        ))
        return list(map(_serialize_campaign, campaigns))

    @put(
        path="/{campaign_id:uuid}",
        description=(
            "Update a campaign.\n\n"
            "Updating `start_date`, `end_date`, `impressions_limit`, "
            "`clicks_limit` is only allowed BEFORE the start of the "
            "campaign. After that, provide either null or the same "
            "value as it has got at the moment or do not provide it "
            "at all.\n\n"
            "Features an auto-moderation tool."
        ),
        responses={
            200: success_spec("Campaigns retrieved.", list[CampaignSchema]),
            404: error_spec("Not found."),
            400: error_spec("Bad request (including moderation errors)."),
        }
    )
    @inject
    async def update_campaign(
            self,
            advertiser_id: UUID,
            campaign_id: UUID,
            data: UpdateCampaignSchema,
            interactor: FromDishka[UpdateCampaignInteractor],
    ) -> CampaignSchema:
        targeting = data.targeting or CampaignTargetingSchema()
        campaign = await interactor(
            advertiser_id,
            campaign_id,
            UpdateCampaignDTO(
                ad_title=data.ad_title,
                ad_text=data.ad_text,
                cost_per_click=data.cost_per_click,
                cost_per_impression=data.cost_per_impression,
                target=CampaignTargetingDTO(
                    gender=targeting.gender,
                    age_to=targeting.age_to,
                    age_from=targeting.age_from,
                    location=targeting.location
                ),
                end_date=data.end_date,
                start_date=data.start_date,
                clicks_limit=data.clicks_limit,
                impressions_limit=data.impressions_limit
            )
        )
        return _serialize_campaign(campaign)

    @delete(
        path="/{campaign_id:uuid}",
        description=(
            "Delete given campaign."
            "\n\n"
            "Beware! Deleting campaign also deletes all associated "
            "statistics (views and clicks)!"
        ),
        responses={
            200: success_spec("Campaign deleted."),
            404: error_spec("Not found."),
        }
    )
    @inject
    async def delete_campaign(
            self,
            advertiser_id: UUID,
            campaign_id: UUID,
            interactor: FromDishka[DeleteCampaignInteractor],
    ) -> None:
        await interactor(campaign_id, advertiser_id)

    @post(
        path="/{campaign_id:uuid}/image",
        status_code=204,
        description=(
            "Upload a campaign image."
            "\n\n"
            "Note: the image is automatically resized to max of 960x960 "
            "resolution (aspect ratio is kept)."
        ),
        responses={
            204: success_spec("File uploaded."),
            404: error_spec("Not found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def set_campaign_image(
            self,
            campaign_id: UUID,
            data: Annotated[
                UploadFile,
                Body(media_type=RequestEncodingType.MULTI_PART)
            ],
            interactor: FromDishka[SetCampaignImageInteractor],
    ) -> None:
        content = await data.read()
        await interactor(campaign_id, data.filename, content)

    @delete(
        path="/{campaign_id:uuid}/image",
        description=(
            "Delete the campaign image."
            "\n\n"
            "Note: does not delete the file, just nullifies the field in "
            "campaign entity."
        ),
        responses={
            204: success_spec("Image deleted."),
            404: error_spec("Not found."),
        }
    )
    @inject
    async def delete_campaign_image(
            self,
            campaign_id: UUID,
            interactor: FromDishka[SetCampaignImageInteractor]
    ) -> None:
        await interactor(campaign_id, None, None)


def _serialize_campaign(campaign: Campaign) -> CampaignSchema:
    return CampaignSchema(
        campaign_id=campaign.id,
        advertiser_id=campaign.advertiser.id,
        ad_title=campaign.ad_title,
        ad_text=campaign.ad_text,
        end_date=campaign.end_date,
        start_date=campaign.start_date,
        clicks_limit=campaign.clicks_limit,
        cost_per_click=campaign.cost_per_click,
        impressions_limit=campaign.impressions_limit,
        cost_per_impression=campaign.cost_per_impression,
        targeting=CampaignTargetingSchema(
            gender=campaign.target_gender,
            age_to=campaign.target_age_to,
            age_from=campaign.target_age_from,
            location=campaign.target_location
        ),
        image_uri=campaign.image_uri
    )
