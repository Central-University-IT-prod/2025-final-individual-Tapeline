import aiohttp

from prodadvert_bot.application.entities import MetricsResponse, MetricsWithDateResponse
from prodadvert_bot.application.exceptions import CampaignCreateException
from prodadvert_bot.application.interfaces.campaigns import CampaignService, Campaign
from prodadvert_bot.config import Config


class CampaignServiceImpl(CampaignService):
    def __init__(self, config: Config) -> None:
        self.base_url = config.api.base_url

    async def get_of_advertiser(self, advertiser_id: str) -> list[Campaign]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/advertisers/{advertiser_id}/campaigns"
            ) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                return [
                    _create_campaign(campaign)
                    for campaign in data
                ]

    async def create(
            self,
            advertiser_id: str,
            ad_title: str,
            ad_text: str,
            impressions_limit: int,
            clicks_limit: int,
            cost_per_impression: float,
            cost_per_click: float,
            start_date: int,
            end_date: int,
            target_gender: str | None,
            target_age_from: int | None,
            target_age_to: int | None,
            target_location: str | None,
    ) -> Campaign:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/advertisers/{advertiser_id}/campaigns",
                json={
                    "ad_title": ad_title,
                    "ad_text": ad_text,
                    "impressions_limit": impressions_limit,
                    "clicks_limit": clicks_limit,
                    "cost_per_click": cost_per_click,
                    "cost_per_impression": cost_per_impression,
                    "start_date": start_date,
                    "end_date": end_date,
                    "targeting": {
                        "gender": target_gender,
                        "age_from": target_age_from,
                        "age_to": target_age_to,
                        "location": target_location
                    }
                }
            ) as response:
                if response.status != 201:
                    raise CampaignCreateException(await response.json())
                campaign = await response.json()
                return _create_campaign(campaign)

    async def get(self, advertiser_id: str, uid: str) -> Campaign | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/advertisers/{advertiser_id}/campaigns/{uid}"
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return _create_campaign(data)

    async def get_stats(self, uid: str) -> MetricsResponse:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stats/campaigns/{uid}"
            ) as response:
                if response.status != 200:
                    return MetricsResponse()
                data = await response.json()
                return MetricsResponse(**data)

    async def get_daily_stats(self, uid: str) -> list[MetricsWithDateResponse]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stats/campaigns/{uid}/daily"
            ) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                return [
                    MetricsWithDateResponse(**day)
                    for day in data
                ]

    async def update(
            self,
            advertiser_id: str,
            uid: str,
            ad_title: str | None = None,
            ad_text: str | None = None,
            impressions_limit: int | None = None,
            clicks_limit: int | None = None,
            cost_per_impression: float | None = None,
            cost_per_click: float | None = None,
            start_date: int | None = None,
            end_date: int | None = None,
            target_gender: str | None = None,
            target_age_from: int | None = None,
            target_age_to: int | None = None,
            target_location: str | None = None,
    ) -> Campaign:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/advertisers/{advertiser_id}/campaigns/{uid}",
                json={
                    "ad_title": ad_title,
                    "ad_text": ad_text,
                    "impressions_limit": impressions_limit,
                    "clicks_limit": clicks_limit,
                    "cost_per_click": cost_per_click,
                    "cost_per_impression": cost_per_impression,
                    "start_date": start_date,
                    "end_date": end_date,
                    "targeting": {
                        "gender": target_gender,
                        "age_from": target_age_from,
                        "age_to": target_age_to,
                        "location": target_location
                    }
                }
            ) as response:
                if response.status != 200:
                    raise CampaignCreateException(await response.json())
                data = await response.json()
                return _create_campaign(data)

    async def delete_image(self, advertiser_uid: str, uid: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/advertisers/{advertiser_uid}"
                f"/campaigns/{uid}/image",
            ) as response:
                return response.status == 204

    async def upload_image(
            self, advertiser_uid: str, uid: str, image
    ) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/advertisers/{advertiser_uid}"
                f"/campaigns/{uid}/image",
                data={"image.png": image}
            ) as response:
                return response.status == 204


def _create_campaign(campaign: dict) -> Campaign:
    return Campaign(
        id=campaign["campaign_id"],
        advertiser_id=campaign["advertiser_id"],
        ad_title=campaign["ad_title"],
        ad_text=campaign["ad_text"],
        impressions_limit=campaign["impressions_limit"],
        clicks_limit=campaign["clicks_limit"],
        cost_per_impression=campaign["cost_per_impression"],
        cost_per_click=campaign["cost_per_click"],
        start_date=campaign["start_date"],
        end_date=campaign["end_date"],
        target_gender=campaign["targeting"]["gender"],
        target_age_from=campaign["targeting"]["age_from"],
        target_age_to=campaign["targeting"]["age_to"],
        target_location=campaign["targeting"]["location"],
        image_uri=campaign["image_uri"],
    )
