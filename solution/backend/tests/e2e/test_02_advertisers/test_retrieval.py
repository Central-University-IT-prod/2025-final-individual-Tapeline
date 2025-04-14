import uuid

from prodadvert.infrastructure.persistence.models import AdvertiserModel
from tests.e2e.data_gen import advertiser_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback


async def test_advertiser_retrieval(test_client: AppClient, rollback: DBRollback):
    """Ensure advertisers are retrieved."""
    advertiser_id, advertiser_data = advertiser_json()
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.get(f"/advertisers/{advertiser_id}")
    assert response.status_code == 200
    assert response.json() == advertiser_data


async def test_advertiser_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    response = await test_client.get(f"/advertisers/{uuid.uuid4()}")
    assert response.status_code == 404
