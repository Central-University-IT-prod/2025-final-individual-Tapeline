import uuid

import pytest

from prodadvert.infrastructure.persistence.models import AdvertiserModel
from tests.e2e.data_gen import advertiser_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback
from tests.utils import unzip


async def test_advertiser_creation(test_client: AppClient, rollback: DBRollback):
    """Ensure advertisers are created correctly."""
    advertiser_id, advertiser_data = advertiser_json()
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    response = await test_client.post(
        "/advertisers/bulk", json=[advertiser_data]
    )
    assert response.status_code == 201
    assert response.json() == [advertiser_data]


_clashing_id = str(uuid.uuid4())


@pytest.mark.parametrize(
    "advertiser",
    [
        (..., {"advertiser_id": "invalid_uuid"}),
        (uuid.UUID(_clashing_id), {"client_id": _clashing_id}),
        advertiser_json(name=""),
    ]
)
async def test_advertiser_creation_bad_request(
        test_client: AppClient,
        advertiser: tuple[uuid.UUID, dict],
        rollback: DBRollback
):
    advertiser_id, advertiser_data = advertiser
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    response = await test_client.post(
        "/advertisers/bulk", json=[advertiser_data]
    )
    assert response.status_code == 400
    assert "Validation failed" in response.json()["detail"]


@pytest.mark.parametrize(
    "advertisers",
    [
        [
            advertiser_json(advertiser_id=_clashing_id),
            advertiser_json(advertiser_id=_clashing_id),
        ],
    ]
)
async def test_advertiser_creation_conflict_simultaneous(
        test_client: AppClient,
        advertisers: list[tuple[uuid.UUID, dict]],
        rollback: DBRollback
):
    advertisers_ids, advertisers_data = unzip(advertisers)
    for adv_id in advertisers_ids:
        rollback.rollback_id(AdvertiserModel, adv_id)
    response = await test_client.post(
        "/advertisers/bulk", json=advertisers_data
    )
    assert response.status_code == 409
    detail = response.json()["detail"].lower()
    assert "conflicts with existing resource" in detail


@pytest.mark.parametrize(
    "advertisers",
    [
        [
            advertiser_json(advertiser_id=_clashing_id, name="initial"),
            advertiser_json(advertiser_id=_clashing_id, name="changed"),
            advertiser_json(advertiser_id=_clashing_id, name="changed2"),
        ]
    ]
)
async def test_client_upsert_sequential(
        test_client: AppClient,
        advertisers: list[tuple[uuid.UUID, dict]],
        rollback: DBRollback
):
    advertisers_ids, advertisers_data = unzip(advertisers)
    for adv_id in advertisers_ids:
        rollback.rollback_id(AdvertiserModel, adv_id)
    await test_client.post("/advertisers/bulk", json=[advertisers_data[0]])
    response = await test_client.post(
        "/advertisers/bulk", json=[advertisers_data[1]]
    )
    assert response.status_code == 201
    response = await test_client.post(
        "/advertisers/bulk", json=[advertisers_data[2]]
    )
    assert response.status_code == 201
    response = await test_client.get(f"/advertisers/{_clashing_id}")
    assert response.json() == advertisers_data[-1]
