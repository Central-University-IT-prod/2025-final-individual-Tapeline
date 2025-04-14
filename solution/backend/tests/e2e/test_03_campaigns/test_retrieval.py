import uuid

import pytest

from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, key_remover
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_campaign_retrieval(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure campaigns are retrieved."""
    await set_current_day(1)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(advertiser_id=str(advertiser_id))
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    response = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    )
    assert response.status_code == 200
    assert key_remover("campaign_id")(response.json()) == campaign_data


async def test_campaign_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    advertiser_id, advertiser_data = advertiser_json()
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{uuid.uuid4()}"
    )
    assert response.status_code == 404


async def test_advertiser_not_found(test_client: AppClient):
    """Ensure 404 response on advertiser not found."""
    response = await test_client.get(
        f"/advertisers/{uuid.uuid4()}/campaigns/{uuid.uuid4()}"
    )
    assert response.status_code == 404


async def test_campaign_different_advertisers(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure campaigns are retrieved only of specific advertiser."""
    await set_current_day(1)
    advertiser1_id, advertiser1_data = advertiser_json()
    advertiser2_id, advertiser2_data = advertiser_json()
    campaign1_data = campaign_json(advertiser_id=str(advertiser1_id))
    campaign2_data = campaign_json(advertiser_id=str(advertiser2_id))
    await test_client.post(
        "/advertisers/bulk",
        json=[advertiser1_data, advertiser2_data]
    )
    response = await test_client.post(
        f"/advertisers/{advertiser1_id}/campaigns",
        json=campaign1_data
    )
    campaign1_id = response.json()["campaign_id"]
    response = await test_client.post(
        f"/advertisers/{advertiser2_id}/campaigns",
        json=campaign2_data
    )
    campaign2_id = response.json()["campaign_id"]
    rollback.rollback_id(CampaignModel, campaign1_id)
    rollback.rollback_id(CampaignModel, campaign2_id)
    rollback.rollback_id(AdvertiserModel, advertiser1_id)
    rollback.rollback_id(AdvertiserModel, advertiser2_id)
    response = await test_client.get(
        f"/advertisers/{advertiser1_id}/campaigns"
    )
    assert response.status_code == 200
    clean_response1 = list(map(key_remover("campaign_id"), response.json()))
    assert clean_response1 == [campaign1_data]
    response = await test_client.get(
        f"/advertisers/{advertiser2_id}/campaigns"
    )
    assert response.status_code == 200
    clean_response2 = list(map(key_remover("campaign_id"), response.json()))
    assert clean_response2 == [campaign2_data]


_advertiser_id, _advertiser_data = advertiser_json()
_single_campaign = [campaign_json(advertiser_id=str(_advertiser_id))]
_20_campaigns = [
    campaign_json(advertiser_id=str(_advertiser_id))
    for _ in range(20)
]


@pytest.mark.parametrize(
    ("campaigns", "pagination", "expected"),
    [
        (_single_campaign, {}, _single_campaign),
        (_single_campaign, {"page": 0, "size": 1}, _single_campaign),
        (_single_campaign, {"page": 0, "size": 0}, []),
        (_20_campaigns, {}, _20_campaigns[:10]),
        (_20_campaigns, {"page": 1}, _20_campaigns[10:]),
        (_20_campaigns, {"size": 1}, _20_campaigns[:1]),
        (_20_campaigns, {"size": 5, "page": 1}, _20_campaigns[5:10]),
        (_single_campaign, {"page": 3}, []),
        (_single_campaign, {"size": 3, "page": 1}, []),
    ]
)
async def test_campaign_list(
        test_client: AppClient,
        rollback: DBRollback,
        campaigns: list[dict],
        pagination: dict,
        expected: list[dict],
        set_current_day
):
    """Ensure pagination works correctly."""
    await set_current_day(1)
    await test_client.post("/advertisers/bulk", json=[_advertiser_data])
    for campaign in campaigns:
        response = await test_client.post(
            f"/advertisers/{_advertiser_id}/campaigns",
            json=campaign
        )
        campaign_id = response.json()["campaign_id"]
        rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_id(AdvertiserModel, _advertiser_id)
    response = await test_client.get(
        f"/advertisers/{_advertiser_id}/campaigns",
        params=pagination
    )
    clean_response = list(map(key_remover("campaign_id"), response.json()))
    assert response.status_code == 200
    assert clean_response == expected


async def test_list_campaign_advertiser_not_found(test_client: AppClient):
    """Ensure empty list returned on advertiser not found."""
    response = await test_client.get(
        f"/advertisers/{uuid.uuid4()}/campaigns"
    )
    assert response.status_code == 200
    assert response.json() == []
