from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.clients import ClientGateway
from prodadvert.decorators import raises
from prodadvert.domain.entities import Gender, Client
from prodadvert.infrastructure.persistence.cache import Cache
from prodadvert.infrastructure.persistence.models import ClientModel, MLScoreModel, AdvertiserModel


class ClientGatewayImpl(ClientGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    @raises(NotFoundException)
    async def get_client_by_id(self, cid: UUID) -> Client:
        query = select(ClientModel).filter(ClientModel.id == str(cid))
        models = await self._session.execute(query)
        try:
            client = _to_entity(models.scalars().one())
        except NoResultFound as exc:
            raise NotFoundException from exc
        #print(Cache.cached_scores)
        if not Cache.cached_scores or cid not in Cache.cached_scores:
            query = select(AdvertiserModel, MLScoreModel)  # type: ignore
            query = query.join(
                MLScoreModel,
                MLScoreModel.advertiser_id == AdvertiserModel.id,
                isouter=True
            )
            models = await self._session.execute(query)
            for advertiser, ml_score in models:
                if ml_score:
                    client.relations[advertiser.id] = ml_score.score
                else:
                    client.relations[advertiser.id] = 0
            if not Cache.cached_scores:
                Cache.cached_scores = {}
            Cache.cached_scores[cid] = client.relations
        else:
            client.relations = Cache.cached_scores[cid]
        return client

    @raises(AlreadyExistsException)
    async def create_client(
            self,
            client_id: UUID,
            login: str,
            age: int,
            location: str,
            gender: Gender
    ) -> Client:
        models = await self._session.execute(
            select(ClientModel).filter(
                ClientModel.id == client_id
            )
        )
        model = models.scalars().first()
        if model:
            model.login = login
            model.age = age
            model.location = location
            model.gender = gender  # type: ignore
            await self._session.commit()
            return _to_entity(model)
        model = ClientModel(
            id=client_id,
            login=login,
            age=age,
            location=location,
            gender=gender
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    @raises(AlreadyExistsException)
    async def create_many(self, clients: list[Client]) -> list[Client]:
        values = [
            {
                "id": client.id,
                "login": client.login,
                "age": client.age,
                "location": client.location,
                "gender": client.gender.value
            } for client in clients
        ]
        stmt = insert(ClientModel).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="clients_pkey",
            set_={
                "login": stmt.excluded.login,
                "age": stmt.excluded.age,
                "location": stmt.excluded.location,
                "gender": stmt.excluded.gender,
            }
        )
        await self._session.execute(stmt)
        await self._session.commit()
        return clients


def _to_entity(model: ClientModel) -> Client:
    return Client(
        id=model.id,  # type: ignore
        login=model.login,
        age=model.age,
        location=model.location,
        gender=model.gender  # type: ignore
    )
