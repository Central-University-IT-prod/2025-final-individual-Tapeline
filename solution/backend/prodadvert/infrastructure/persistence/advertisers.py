from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.advertisers import AdvertiserGateway
from prodadvert.decorators import raises
from prodadvert.domain.entities import Advertiser
from prodadvert.infrastructure.persistence.cache import Cache
from prodadvert.infrastructure.persistence.models import AdvertiserModel, MLScoreModel, ClientModel


class AdvertiserGatewayImpl(AdvertiserGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    @raises(NotFoundException)
    async def get_advertiser_by_id(self, advertiser_id: UUID) -> Advertiser:
        query = select(AdvertiserModel).filter(
            AdvertiserModel.id == advertiser_id
        )
        models = await self._session.execute(query)
        try:
            return _to_entity(models.scalars().one())
        except NoResultFound as exc:
            raise NotFoundException from exc

    @raises(AlreadyExistsException)
    async def create_advertiser(
            self,
            advertiser_id: UUID,
            name: str
    ) -> Advertiser:
        models = await self._session.execute(
            select(AdvertiserModel).filter(
                AdvertiserModel.id == advertiser_id
            )
        )
        model = models.scalars().first()
        if model:
            model.name = name
            await self._session.commit()
            return _to_entity(model)
        model = AdvertiserModel(id=advertiser_id, name=name)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def create_many(
            self, advertisers: list[Advertiser]
    ) -> list[Advertiser]:
        values = [
            {
                "id": advertiser.id,
                "name": advertiser.name,
            } for advertiser in advertisers
        ]
        stmt = insert(AdvertiserModel).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="advertisers_pkey",
            set_={
                "name": stmt.excluded.name,
            }
        )
        await self._session.execute(stmt)
        await self._session.commit()
        return advertisers

    async def set_score(
            self,
            client_id: UUID,
            advertiser_id: UUID,
            score: int
    ) -> None:
        await self._ensure_client_and_advertiser_exist(
            client_id, advertiser_id
        )
        models = await self._session.execute(
            select(MLScoreModel).filter(
                and_(
                    MLScoreModel.advertiser_id == advertiser_id,
                    MLScoreModel.client_id == client_id,
                )
            )
        )
        existing_score = models.scalars().first()
        if existing_score:
            existing_score.score = score
            self._session.add(existing_score)
            await self._session.commit()
        else:
            model = MLScoreModel(
                client_id=client_id,
                advertiser_id=advertiser_id,
                score=score
            )
            self._session.add(model)
        Cache.place_score(client_id, advertiser_id, score)
        await self._session.commit()

    async def _ensure_client_and_advertiser_exist(
            self,
            client_id: UUID,
            advertiser_id: UUID
    ) -> None:
        advertisers = await self._session.execute(
            select(AdvertiserModel).filter(
                AdvertiserModel.id == advertiser_id
            )
        )
        clients = await self._session.execute(
            select(ClientModel).filter(
                ClientModel.id == client_id
            )
        )
        try:
            advertisers.scalars().one()
            clients.scalars().one()
        except NoResultFound as exc:
            raise NotFoundException from exc


def _to_entity(model: AdvertiserModel) -> Advertiser:
    return Advertiser(
        id=_ensure_uuid(model.id),
        name=model.name
    )


def _ensure_uuid(uid: str | UUID) -> UUID:
    return uid if isinstance(uid, UUID) else UUID(uid)
