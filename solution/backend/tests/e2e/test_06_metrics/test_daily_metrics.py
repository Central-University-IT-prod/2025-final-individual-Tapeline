from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel, ClientModel, MLScoreModel, \
    MetricModel
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day
from tests.e2e.request_utils import request_advert, create_campaign, prepare_advertiser_and_client, prepare_client_for_advertiser


async def test_campaign_stats(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, _, client1_id, _ = await prepare_advertiser_and_client(
        test_client, rollback
    )
    client2_id, _ = await prepare_client_for_advertiser(
        test_client, advertiser_id
    )
    campaign_id = await create_campaign(advertiser_id, test_client)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client1_id)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client2_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client1_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client2_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client1_id)
    rollback.rollback_id(ClientModel, client2_id)
    await set_current_day(0)
    await request_advert(test_client, client1_id, should_click=True)
    await set_current_day(1)
    await request_advert(test_client, client2_id, should_click=False)
    response = await test_client.get(
        f"/stats/campaigns/{campaign_id}/daily"
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["impressions_count"] == 1
    assert data[0]["clicks_count"] == 1
    assert data[0]["conversion"] == 100.0
    assert data[0]["date"] == 0
    assert data[1]["impressions_count"] == 1
    assert data[1]["clicks_count"] == 0
    assert data[1]["conversion"] == 0.0
    assert data[1]["date"] == 1


async def test_advertiser_stats(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, _, client1_id, _ = await prepare_advertiser_and_client(
        test_client, rollback
    )
    client2_id, _ = await prepare_client_for_advertiser(
        test_client, advertiser_id
    )
    campaign1_id = await create_campaign(advertiser_id, test_client)
    campaign2_id = await create_campaign(advertiser_id, test_client)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client1_id)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client2_id)
    rollback.rollback_id(CampaignModel, campaign1_id)
    rollback.rollback_id(CampaignModel, campaign2_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client1_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client2_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client1_id)
    rollback.rollback_id(ClientModel, client2_id)
    await set_current_day(0)
    await request_advert(test_client, client1_id, should_click=True)
    await request_advert(test_client, client2_id, should_click=True)
    await set_current_day(1)
    await request_advert(test_client, client1_id, should_click=False)
    await request_advert(test_client, client2_id, should_click=True)
    response = await test_client.get(
        f"/stats/advertisers/{advertiser_id}/campaigns/daily"
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["impressions_count"] == 2
    assert data[0]["clicks_count"] == 2
    assert data[0]["conversion"] == 100.0
    assert data[0]["date"] == 0
    assert data[1]["impressions_count"] == 2
    assert data[1]["clicks_count"] == 1
    assert data[1]["conversion"] == 50.0
    assert data[1]["date"] == 1


async def test_pagination(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, _, client1_id, _ = await prepare_advertiser_and_client(
        test_client, rollback
    )
    client2_id, _ = await prepare_client_for_advertiser(
        test_client, advertiser_id
    )
    campaign1_id = await create_campaign(advertiser_id, test_client)
    campaign2_id = await create_campaign(advertiser_id, test_client)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client1_id)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client2_id)
    rollback.rollback_id(CampaignModel, campaign1_id)
    rollback.rollback_id(CampaignModel, campaign2_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client1_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client2_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client1_id)
    rollback.rollback_id(ClientModel, client2_id)
    await set_current_day(0)
    await request_advert(test_client, client1_id, should_click=True)
    await request_advert(test_client, client2_id, should_click=True)
    await set_current_day(1)
    await request_advert(test_client, client1_id, should_click=False)
    await request_advert(test_client, client2_id, should_click=True)
    response = await test_client.get(
        f"/stats/advertisers/{advertiser_id}/campaigns/daily",
        params={"date_from": 1, "date_to": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["date"] == 1
