from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel, ClientModel, MLScoreModel, \
    MetricModel
from tests.e2e.data_gen import campaign_json, advertiser_json, key_remover, client_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def test_advert_display(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        start_date=0,
        end_date=7,
        targeting={
            "gender": None,
            "age_from": None,
            "age_to": None,
            "location": None
        }
    )
    client_id, client_data = client_json()
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
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    response = await test_client.get(
        "/ads", params={"client_id": str(client_id)}
    )
    assert response.status_code == 200
    assert response.json()["ad_id"] == str(campaign_id)


async def test_advert_not_found(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        start_date=0,
        end_date=7,
        targeting={
            "gender": None,
            "age_from": None,
            "age_to": None,
            "location": None
        }
    )
    client_id, client_data = client_json()
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
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    await set_current_day(100)
    response = await test_client.get(
        "/ads", params={"client_id": str(client_id)}
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_advert_click(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        start_date=0,
        end_date=7,
        targeting={
            "gender": None,
            "age_from": None,
            "age_to": None,
            "location": None
        }
    )
    client_id, client_data = client_json()
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
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    response = await test_client.get(
        "/ads", params={"client_id": str(client_id)}
    )
    ad_id = response.json()["ad_id"]
    response = await test_client.post(
        f"/ads/{ad_id}/click",
        json={"client_id": str(client_id)}
    )
    assert response.status_code == 204


async def test_advert_cannot_click(
        test_client: AppClient,
        rollback: DBRollback,
        set_current_day
):
    await set_current_day(0)
    advertiser_id, advertiser_data = advertiser_json()
    campaign_data = campaign_json(
        advertiser_id=str(advertiser_id),
        start_date=0,
        end_date=7,
        targeting={
            "gender": None,
            "age_from": None,
            "age_to": None,
            "location": None
        }
    )
    client_id, client_data = client_json()
    await test_client.post("/clients/bulk", json=[client_data])
    await test_client.post("/advertisers/bulk", json=[advertiser_data])
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    rollback.rollback_query(MetricModel, MetricModel.client_id == client_id)
    rollback.rollback_id(CampaignModel, campaign_id)
    rollback.rollback_query(MLScoreModel, MLScoreModel.client_id == client_id)
    rollback.rollback_id(AdvertiserModel, advertiser_id)
    rollback.rollback_id(ClientModel, client_id)
    response = await test_client.post(
        f"/ads/{campaign_id}/click",
        json={"client_id": str(client_id)}
    )
    assert response.status_code == 403
