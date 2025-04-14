import uuid
from typing import Final

import pytest

from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, subsets, key_remover
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


_new_data_base: Final[dict] = {
    "ad_title": "NEW",
    "ad_text": "NEW",
    "cost_per_click": 12345.0,
    "cost_per_impression": 12345.0,
    "clicks_limit": 12345,
    "impressions_limit": 12345,
    "start_date": 111,
    "end_date": 222,
    "targeting": {
        "gender": None,
        "age_from": None,
        "age_to": None,
        "location": None
    }
}
_targeting: Final[dict] = {
    "gender": "ALL",
    "age_from": 15,
    "age_to": 35,
    "location": "NEW"
}
_new_data_with_targeting: Final[dict] = _new_data_base | {
    "targeting": _targeting
}


def _nullify_targeting(new_data: dict, *keys: str) -> dict:
    new_data = new_data.copy()
    for key in keys:
        new_data["targeting"][key] = None
    return new_data


@pytest.mark.parametrize(
    "new_data",
    [
        _new_data_base,
        _new_data_with_targeting,
        _nullify_targeting(
            _new_data_with_targeting,
            "gender",
        ),
        _nullify_targeting(
            _new_data_with_targeting,
            "age_from",
        ),
        _nullify_targeting(
            _new_data_with_targeting,
            "age_to",
        ),
        _nullify_targeting(
            _new_data_with_targeting,
            "location",
        ),
        _nullify_targeting(
            _new_data_with_targeting,
            "age_from",
            "age_to",
        ),
        _nullify_targeting(
            _new_data_with_targeting,
            "location",
            "gender",
        ),
    ]
)
async def test_campaign_update(
        test_client: AppClient, rollback: DBRollback, new_data: dict,
        set_current_day
):
    """Ensure campaigns are updated."""
    await set_current_day(1)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id), start_date=5, end_date=10
    )
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    new_campaign = campaign_data | new_data
    await test_client.put(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
        json=new_data
    )
    response = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    )
    assert response.status_code == 200
    assert key_remover("campaign_id")(response.json()) == new_campaign


async def test_campaign_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    advertiser_id, advertiser_data = advertiser_json()
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.put(
        f"/advertisers/{advertiser_id}/campaigns/{uuid.uuid4()}",
        json=_targeting
    )
    assert response.status_code == 404


async def test_advertiser_not_found(test_client: AppClient):
    """Ensure 404 response on advertiser not found."""
    response = await test_client.put(
        f"/advertisers/{uuid.uuid4()}/campaigns/{uuid.uuid4()}",
        json=_targeting
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("new_data", "update_day", "keyword"),
    [
        (
            {"targeting": {"age_from": 15, "age_to": 14}},
            0,
            "age"
        ),
        (
            {"start_date": 5},
            2,
            "after campaign start"
        ),
        (
            {"end_date": 5},
            2,
            "after campaign start"
        ),
        (
            {"clicks_limit": 100},
            2,
            "after campaign start"
        ),
        (
            {"impressions_limit": 100},
            2,
            "after campaign start"
        ),
    ]
)
async def test_campaign_update_bad_request(
        test_client: AppClient,
        rollback: DBRollback,
        new_data: dict,
        update_day,
        keyword,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id), start_date=0
    )
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await set_current_day(update_day)
    response = await test_client.put(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
        json=new_data
    )
    assert response.status_code == 400
    assert keyword in response.json()["detail"]
