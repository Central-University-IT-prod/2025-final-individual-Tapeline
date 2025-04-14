import uuid


from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, subsets
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_campaign_delete(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure campaigns are deleted."""
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
    response = await test_client.delete(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
    )
    assert response.status_code == 204
    response = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    )
    assert response.status_code == 404


async def test_campaign_not_found(test_client: AppClient, rollback: DBRollback):
    """Ensure 404 response on not found."""
    advertiser_id, advertiser_data = advertiser_json()
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.delete(
        f"/advertisers/{advertiser_id}/campaigns/{uuid.uuid4()}",
    )
    assert response.status_code == 404


async def test_advertiser_not_found(test_client: AppClient):
    """Ensure 404 response on advertiser not found."""
    response = await test_client.delete(
        f"/advertisers/{uuid.uuid4()}/campaigns/{uuid.uuid4()}",
    )
    assert response.status_code == 404
