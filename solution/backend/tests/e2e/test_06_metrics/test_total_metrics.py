from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel, ClientModel, MLScoreModel, \
    MetricModel
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day
from tests.e2e.request_utils import request_advert, create_campaign, prepare_advertiser_and_client


async def test_campaign_stats(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, _, client_id, _ = await prepare_advertiser_and_client(
        test_client, rollback
    )
    campaign_id = await create_campaign(advertiser_id, test_client)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    await request_advert(test_client, client_id, should_click=True)
    response = await test_client.get(
        f"/stats/campaigns/{campaign_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["impressions_count"] == 1
    assert data["clicks_count"] == 1
    assert data["conversion"] == 100.0


async def test_advertiser_stats(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, _, client_id, _ = await prepare_advertiser_and_client(
        test_client, rollback
    )
    campaign1_id = await create_campaign(advertiser_id, test_client)
    campaign2_id = await create_campaign(advertiser_id, test_client)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign1_id)
    rollback.rollback_id(CampaignModel, campaign2_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    await request_advert(test_client, client_id, should_click=True)
    await request_advert(test_client, client_id)
    response = await test_client.get(
        f"/stats/advertisers/{advertiser_id}/campaigns"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["impressions_count"] == 2
    assert data["clicks_count"] == 1
    assert data["conversion"] == 50.0
