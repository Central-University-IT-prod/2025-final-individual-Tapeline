import uuid

from prodadvert.infrastructure.persistence.models import ClientModel
from tests.e2e.data_gen import client_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback


async def test_client_retrieval(test_client: AppClient, rollback: DBRollback):
    """Ensure clients are retrieved."""
    client_id, client_data = client_json()
    rollback.rollback_id(ClientModel, client_id)
    await test_client.post("/clients/bulk", json=[client_data])
    response = await test_client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json() == client_data


async def test_client_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    response = await test_client.get(f"/clients/{uuid.uuid4()}")
    assert response.status_code == 404
