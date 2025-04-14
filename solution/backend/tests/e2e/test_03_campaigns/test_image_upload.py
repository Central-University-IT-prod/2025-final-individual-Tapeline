import uuid
from typing import Final

import pytest

from prodadvert.infrastructure.persistence.models import CampaignModel, AdvertiserModel
from tests.e2e.data_gen import campaign_json, advertiser_json, subsets, key_remover
from tests.e2e.fixtures import AppClient, DBRollback, test_client, rollback, set_current_day


async def _create_campaign(
        test_client: AppClient, rollback: DBRollback
):
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
    return advertiser_id, campaign_id


async def test_pic_upload(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure campaign images can be updated."""
    await set_current_day(1)
    advertiser_id, campaign_id = await _create_campaign(test_client, rollback)
    img_file = open("tests/fixtures/duke.jpg", "rb")
    response1 = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}/image",
        files={
            "duke.jpg": img_file
        }
    )
    response2 = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    )
    assert response1.status_code == 204
    assert response2.json()["image_uri"] is not None


async def test_pic_remove(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure campaign images can be updated."""
    await set_current_day(1)
    advertiser_id, campaign_id = await _create_campaign(test_client, rollback)
    img_file = open("tests/fixtures/duke.jpg", "rb")
    response1 = await test_client.post(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}/image",
        files={
            "duke.jpg": img_file
        }
    )
    response2 = await test_client.delete(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}/image"
    )
    response3 = await test_client.get(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
    )
    assert response1.status_code == 204
    assert response2.status_code == 204
    assert response3.json()["image_uri"] is None


async def test_campaign_not_found(
        test_client: AppClient, rollback: DBRollback, set_current_day
):
    """Ensure 404 not campaign not found."""
    await set_current_day(1)
    img_file = open("tests/fixtures/duke.jpg", "rb")
    response1 = await test_client.post(
        f"/advertisers/{uuid.uuid4()}/campaigns/{uuid.uuid4()}/image",
        files={
            "duke.jpg": img_file
        }
    )
    assert response1.status_code == 404
