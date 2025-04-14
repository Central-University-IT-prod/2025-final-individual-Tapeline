import uuid

import pytest

from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, key_remover
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_enable_disable_endpoints(test_client: AppClient):
    response1 = await test_client.put("/profanity/enable")
    response_a = await test_client.get("/profanity/enabled")
    response2 = await test_client.put("/profanity/disable")
    response_b = await test_client.get("/profanity/enabled")
    assert response1.status_code == 204
    assert response2.status_code == 204
    assert response_a.json()["is_enabled"]
    assert not response_b.json()["is_enabled"]


@pytest.mark.parametrize(
    "campaign_data",
    [
        {"ad_title": "Курсы", "ad_text": "Записывайтесь на курсы по питону!"},
        {"ad_title": "питон", "ad_text": "Записывайтесь на курсы!"},
    ]
)
async def test_campaign_moderation_on_create(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day,
        campaign_data: dict
):
    """Ensure campaigns are moderated correctly."""
    await set_current_day(1)
    await test_client.put("/profanity/enable")
    await test_client.put("/profanity/blacklist", json=["питон", "питону"])
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        **campaign_data
    )
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    rollback.rollback_query(
        CampaignModel, CampaignModel.advertiser_id == advertiser_id
    )
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    assert response.status_code == 400
    data = response.json()
    assert "Profanity" in data["detail"]


@pytest.mark.parametrize(
    "campaign_data_insertion",
    [
        {"ad_title": "Курсы", "ad_text": "Записывайтесь на курсы по питону!"},
        {"ad_title": "питон", "ad_text": "Записывайтесь на курсы!"},
    ]
)
async def test_campaign_moderation_on_update(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day,
        campaign_data_insertion
):
    """Ensure campaigns are moderated correctly."""
    await set_current_day(1)
    await test_client.put("/profanity/enable")
    await test_client.put("/profanity/blacklist", json=["питон", "питону"])
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        ad_text="Записывайтесь на курсы!"
    )
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_query(
        CampaignModel, CampaignModel.advertiser_id == advertiser_id
    )
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    response = await test_client.put(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
        json=campaign_data_insertion
    )
    assert response.status_code == 400
    data = response.json()
    assert "Profanity" in data["detail"]


async def test_campaign_moderation_disabled_on_create(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    """Ensure campaigns are not moderated when moderation is disabled."""
    await set_current_day(1)
    await test_client.put("/profanity/enable")
    await test_client.put("/profanity/blacklist", json=["питон", "питону"])
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        ad_text="Записывайтесь на курсы по питону!"
    )
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    await test_client.put("/profanity/disable")
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    rollback.rollback_query(
        CampaignModel, CampaignModel.advertiser_id == advertiser_id
    )
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    assert response.status_code == 201
