"""Defines advertiser interactors."""

from typing import Sequence
from uuid import UUID

from dishka import FromDishka

from prodadvert.application.dto import NewAdvertiserDTO
from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.advertisers import AdvertiserGateway
from prodadvert.decorators import raises
from prodadvert.domain.entities import Advertiser


class GetAdvertiserInteractor:
    """Get advertiser by ID."""

    def __init__(self, gateway: FromDishka[AdvertiserGateway]) -> None:
        self.gateway = gateway

    @raises(NotFoundException)
    async def __call__(self, uid: UUID) -> Advertiser:
        return await self.gateway.get_advertiser_by_id(uid)


class BulkAdvertiserCreateInteractor:
    """Create many advertisers at once."""

    def __init__(self, gateway: FromDishka[AdvertiserGateway]) -> None:
        self.gateway = gateway

    @raises(AlreadyExistsException)
    async def __call__(
            self,
            advertisers: Sequence[NewAdvertiserDTO]
    ) -> Sequence[Advertiser]:
        adv_ids = set(advertiser.advertiser_id for advertiser in advertisers)
        if len(adv_ids) != len(advertisers):
            raise AlreadyExistsException
        # return [
        #     await self.gateway.create_advertiser(
        #         advertiser.advertiser_id,
        #         advertiser.name
        #     )
        #     for advertiser in advertisers
        # ]
        return await self.gateway.create_many([
            Advertiser(
                id=advertiser.advertiser_id,
                name=advertiser.name
            ) for advertiser in advertisers
        ])


class SetMLScoreInteractor:
    """Set ML score on a relation of advertiser and client."""

    def __init__(self, gateway: FromDishka[AdvertiserGateway]) -> None:
        self.gateway = gateway

    @raises(NotFoundException)
    async def __call__(
            self,
            client_id: UUID,
            advertiser_id: UUID,
            score: int
    ) -> None:
        return await self.gateway.set_score(client_id, advertiser_id, score)
