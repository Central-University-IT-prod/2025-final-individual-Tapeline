"""Defines client interactors."""
from typing import Sequence
from uuid import UUID

from dishka import FromDishka

from prodadvert.application.dto import NewClientDTO
from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.clients import ClientGateway
from prodadvert.decorators import raises
from prodadvert.domain.entities import Client, Gender


class GetClientInteractor:
    """Get client by ID."""

    def __init__(self, client_gateway: FromDishka[ClientGateway]) -> None:
        self.client_gateway = client_gateway

    @raises(NotFoundException)
    async def __call__(self, client_id: UUID) -> Client:
        return await self.client_gateway.get_client_by_id(client_id)


class BulkClientCreateInteractor:
    """Create many clients at once."""

    def __init__(self, client_gateway: FromDishka[ClientGateway]) -> None:
        self.client_gateway = client_gateway

    @raises(AlreadyExistsException)
    async def __call__(
            self,
            clients: Sequence[NewClientDTO]
    ) -> Sequence[Client]:
        client_ids = set(client.client_id for client in clients)
        if len(client_ids) != len(clients):
            raise AlreadyExistsException
        # return [
        #     await self.client_gateway.create_client(
        #         client.client_id,
        #         client.login,
        #         client.age,
        #         client.location,
        #         client.gender
        #     )
        #     for client in clients
        # ]
        return await self.client_gateway.create_many([
            Client(
                client.client_id,
                client.login,
                client.age,
                client.location,
                Gender(client.gender)
            ) for client in clients
        ])
