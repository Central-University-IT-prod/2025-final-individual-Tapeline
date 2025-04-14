import uuid

import pytest

from prodadvert.infrastructure.persistence.models import ClientModel
from tests.e2e.data_gen import client_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback
from tests.utils import unzip


async def test_client_creation(test_client: AppClient, rollback: DBRollback):
    """Ensure clients are created correctly."""
    client_id, client_data = client_json()
    rollback.rollback_id(ClientModel, client_id)
    response = await test_client.post("/clients/bulk", json=[client_data])
    assert response.status_code == 201
    assert response.json() == [client_data]


_clashing_id = str(uuid.uuid4())


@pytest.mark.parametrize(
    "client",
    [
        (..., {"client_id": "invalid_uuid"}),
        (uuid.UUID(_clashing_id), {"client_id": _clashing_id}),
        client_json(age=-1),
        client_json(age=1000),
        client_json(age=2.3),
        client_json(location=""),
        client_json(location="   \n"),
        client_json(login=""),
        client_json(login="   "),
        client_json(gender="INVALID"),
    ]
)
async def test_client_creation_bad_request(
        test_client: AppClient,
        client: tuple[uuid.UUID, dict],
        rollback: DBRollback
):
    client_id, client_data = client
    rollback.rollback_id(ClientModel, client_id)
    response = await test_client.post("/clients/bulk", json=[client_data])
    assert response.status_code == 400
    assert "Validation failed" in response.json()["detail"]


@pytest.mark.parametrize(
    "clients",
    [
        [
            client_json(client_id=_clashing_id),
            client_json(client_id=_clashing_id),
        ],
    ]
)
async def test_client_creation_conflict_simultaneous(
        test_client: AppClient,
        clients: list[tuple[uuid.UUID, dict]],
        rollback: DBRollback
):
    clients_ids, clients_data = unzip(clients)
    for client_id in clients_ids:
        rollback.rollback_id(ClientModel, client_id)
    response = await test_client.post("/clients/bulk", json=clients_data)
    assert response.status_code == 409
    detail = response.json()["detail"].lower()
    assert "conflicts with existing resource" in detail


@pytest.mark.parametrize(
    "clients",
    [
        [
            client_json(client_id=_clashing_id, login="initial"),
            client_json(client_id=_clashing_id, login="changed"),
            client_json(client_id=_clashing_id, login="changed2"),
        ],
    ]
)
async def test_client_upsert_sequential(
        test_client: AppClient,
        clients: list[tuple[uuid.UUID, dict]],
        rollback: DBRollback
):
    clients_ids, clients_data = unzip(clients)
    for client_id in clients_ids:
        rollback.rollback_id(ClientModel, client_id)
    await test_client.post("/clients/bulk", json=[clients_data[0]])
    response = await test_client.post("/clients/bulk", json=[clients_data[1]])
    assert response.status_code == 201
    response = await test_client.post("/clients/bulk", json=[clients_data[2]])
    assert response.status_code == 201
    response = await test_client.get(f"/clients/{_clashing_id}")
    assert response.json() == clients_data[-1]
