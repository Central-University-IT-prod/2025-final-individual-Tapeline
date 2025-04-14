import uuid

import pytest

from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, key_remover
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_campaign_creation(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    """Ensure campaigns are created correctly."""
    await set_current_day(1)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(advertiser_id=str(advertiser_id))
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    rollback.rollback_id(CampaignModel, response.json()["campaign_id"])
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    assert response.status_code == 201
    assert key_remover("campaign_id")(response.json()) == campaign_data


_clashing_id = str(uuid.uuid4())


@pytest.mark.parametrize(
    "campaign",
    [
        campaign_json(start_date=3, end_date=1),
        campaign_json(
            targeting={
                "age_from": 15,
                "age_to": 14
            }
        ),
    ]
)
async def test_campaign_creation_bad_request(
        test_client: AppClient,
        campaign: dict,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(1)
    campaign_data = campaign
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data["advertiser_id"] = str(advertiser_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    assert response.status_code == 400


async def test_campaign_advertiser_not_found(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day,
):
    await set_current_day(1)
    campaign_data = campaign_json()
    response = await test_client.post(
        f"/advertisers/{uuid.uuid4()}/campaigns",
        json=campaign_data
    )
    assert response.status_code == 404, response.json()


@pytest.mark.parametrize(
    ("current_day", "campaign"),
    [
        (15, campaign_json(start_date=14)),
        (15, campaign_json(end_date=14)),
    ]
)
async def test_cannot_date_back(
        test_client: AppClient,
        current_day: int,
        campaign: dict,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(current_day)
    advertiser_id, advertiser_data = advertiser_json()
    campaign["advertiser_id"] = str(advertiser_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign
    )
    assert response.status_code == 400, (response.status_code, response.json())
    detail = response.json()["detail"].lower()
    assert "date" in detail
