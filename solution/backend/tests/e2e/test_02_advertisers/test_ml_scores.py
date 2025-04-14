import uuid

from sqlalchemy import and_

from prodadvert.infrastructure.persistence.models import AdvertiserModel, ClientModel, MLScoreModel
from tests.e2e.data_gen import advertiser_json, client_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback


async def test_set_ml_score(test_client: AppClient, rollback: DBRollback):
    """Ensure ML score is set correctly."""
    advertiser_id, advertiser_data = advertiser_json()
    client_id, client_data = client_json()
    rollback.rollback_query(MLScoreModel, and_(
        MLScoreModel.advertiser_id == advertiser_id,
        MLScoreModel.client_id == client_id,
    ))
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    await test_client.post("/clients/bulk", json=[client_data])
    await test_client.post("/advertisers/bulk", json=[advertiser_data])

    response = await test_client.post(
        "/ml-scores",
        json={
            "client_id": str(client_id),
            "advertiser_id": str(advertiser_id),
            "score": 100,
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "score": 100}


async def test_set_ml_score_twice(test_client: AppClient, rollback: DBRollback):
    """Ensure ML score is updated correctly."""
    advertiser_id, advertiser_data = advertiser_json()
    client_id, client_data = client_json()
    rollback.rollback_query(MLScoreModel, and_(
        MLScoreModel.advertiser_id == advertiser_id,
        MLScoreModel.client_id == client_id,
    ))
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    await test_client.post("/clients/bulk", json=[client_data])
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    await test_client.post(
        "/ml-scores",
        json={
            "client_id": str(client_id),
            "advertiser_id": str(advertiser_id),
            "score": 100,
        }
    )

    response = await test_client.post(
        "/ml-scores",
        json={
            "client_id": str(client_id),
            "advertiser_id": str(advertiser_id),
            "score": 80,
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "score": 80}


async def test_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    response = await test_client.post(
        "/ml-scores",
        json={
            "client_id": str(uuid.uuid4()),
            "advertiser_id": str(uuid.uuid4()),
            "score": 100,
        }
    )
    assert response.status_code == 404
