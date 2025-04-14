from uuid import UUID

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post, Response

from prodadvert.application.dto import NewAdvertiserDTO
from prodadvert.application.interactors.advertisers import (
    GetAdvertiserInteractor,
    BulkAdvertiserCreateInteractor, SetMLScoreInteractor
)
from prodadvert.controllers.http.openapi import success_spec, error_spec
from prodadvert.controllers.http.schemas import AdvertiserSchema, AdvertiserUpsertSchema, SetMLScoreSchema
from prodadvert.domain.entities import Advertiser


class AdvertisersController(Controller):
    path = ""
    tags = ["Advertisers"]

    @get(
        path="/advertisers/{advertiser_id:uuid}",
        description=(
            "Get advertiser by his id."
        ),
        responses={
            200: success_spec("Advertiser retrieved.", AdvertiserSchema),
            404: error_spec("No such advertiser."),
        }
    )
    @inject
    async def get_advertiser(
            self,
            advertiser_id: UUID,
            interactor: FromDishka[GetAdvertiserInteractor],
    ) -> AdvertiserSchema:
        return _serialize_advertiser(await interactor(advertiser_id))

    @post(
        path="/advertisers/bulk",
        description=(
            "Bulk upsert of advertisers."
            "\n\n"
            "Note: there cannot be two or more advertisers "
            "with the same id in one request!"
        ),
        responses={
            201: success_spec("Advertisers created/updated."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def bulk_create(
            self,
            data: list[AdvertiserUpsertSchema],
            interactor: FromDishka[BulkAdvertiserCreateInteractor]
    ) -> list[AdvertiserSchema]:
        advertisers = await interactor([
            NewAdvertiserDTO(**advertiser.model_dump())
            for advertiser in data
        ])
        return list(map(_serialize_advertiser, advertisers))

    @post(
        path="/ml-scores",
        status_code=200,
        description=(
            "Set ML-score relation of specific client to specific advertiser"
        ),
        responses={
            200: success_spec("Score set."),
            404: error_spec("No advertiser or client found."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def set_ml_score(
            self,
            data: SetMLScoreSchema,
            interactor: FromDishka[SetMLScoreInteractor],
    ) -> Response:
        await interactor(data.client_id, data.advertiser_id, data.score)
        return Response(
            content={"status": "ok", "score": data.score},
            status_code=200
        )


def _serialize_advertiser(advertiser: Advertiser) -> AdvertiserSchema:
    return AdvertiserSchema(
        advertiser_id=advertiser.id,
        name=advertiser.name
    )
