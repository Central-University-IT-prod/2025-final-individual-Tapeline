from uuid import UUID

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get, post

from prodadvert.application.dto import NewClientDTO
from prodadvert.application.interactors.clients import (
    GetClientInteractor,
    BulkClientCreateInteractor
)
from prodadvert.controllers.http.openapi import success_spec, error_spec
from prodadvert.controllers.http.schemas import ClientSchema, ClientUpsertSchema
from prodadvert.domain.entities import Client


class ClientsController(Controller):
    path = "/clients"
    tags = ["Clients"]

    @get(
        path="/{client_id:uuid}",
        description=(
            "Get client by his id."
        ),
        responses={
            200: success_spec("Client retrieved.", ClientSchema),
            404: error_spec("No such client."),
        }
    )
    @inject
    async def get_client(
            self,
            client_id: UUID,
            interactor: FromDishka[GetClientInteractor],
    ) -> ClientSchema:
        client = await interactor(client_id)
        return _serialize_client(client)

    @post(
        path="/bulk",
        description=(
            "Bulk upsert of clients."
            "\n\n"
            "Note: there cannot be two or more clients "
            "with the same id in one request!"
        ),
        responses={
            201: success_spec("Clients created/updated."),
            400: error_spec("Bad request."),
        }
    )
    @inject
    async def bulk_client_create(
            self,
            data: list[ClientUpsertSchema],
            interactor: FromDishka[BulkClientCreateInteractor]
    ) -> list[ClientSchema]:
        clients = await interactor([
            NewClientDTO(**client.model_dump())
            for client in data
        ])
        return list(map(_serialize_client, clients))


def _serialize_client(client: Client) -> ClientSchema:
    return ClientSchema(
        client_id=client.id,
        login=client.login,
        age=client.age,
        location=client.location,
        gender=client.gender,
    )
