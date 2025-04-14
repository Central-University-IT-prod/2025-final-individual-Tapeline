from tests.e2e.data_gen import campaign_json, advertiser_json, key_remover, client_json
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def prepare_advertiser_and_client(test_client: AppClient, rollback: DBRollback):
    advertiser_id, advertiser_data = advertiser_json()
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
    return advertiser_id, advertiser_data, client_id, client_data


async def prepare_client_for_advertiser(test_client: AppClient, advertiser_id):
    client_id, client_data = client_json()
    await test_client.post("/clients/bulk", json=[client_data])
    await test_client.post(
        "/ml-scores",
        json={
            "client_id": str(client_id),
            "advertiser_id": str(advertiser_id),
            "score": 100,
        }
    )
    return client_id, client_data


async def create_campaign(advertiser_id, test_client: AppClient):
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
    response = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns",
        json=campaign_data
    )
    campaign_id = response.json()["campaign_id"]
    return campaign_id


async def request_advert(test_client: AppClient, client_id, should_click=False):
    response = await test_client.get(
        "/ads", params={"client_id": str(client_id)}
    )
    if should_click:
        ad_id = response.json()["ad_id"]
        await test_client.post(
            f"/ads/{ad_id}/click",
            json={"client_id": str(client_id)}
        )