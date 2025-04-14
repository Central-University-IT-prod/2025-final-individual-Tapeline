import aiohttp

from prodadvert_bot.application.entities import Advertiser, MetricsResponse, MetricsWithDateResponse
from prodadvert_bot.application.interfaces.advertisers import AdvertiserService
from prodadvert_bot.config import Config


class AdvertiserServiceImpl(AdvertiserService):
    def __init__(self, config: Config) -> None:
        self.base_url = config.api.base_url

    async def get_advertiser(self, uid: str) -> Advertiser | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/advertisers/{uid}"
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return Advertiser(
                    id=data["advertiser_id"],
                    name=data["name"]
                )

    async def get_stats(self, uid: str) -> MetricsResponse:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stats/advertisers/{uid}/campaigns"
            ) as response:
                if response.status != 200:
                    return MetricsResponse()
                data = await response.json()
                return MetricsResponse(**data)

    async def get_daily_stats(self, uid: str) -> list[MetricsWithDateResponse]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/stats/advertisers/{uid}/campaigns/daily"
            ) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                return [
                    MetricsWithDateResponse(**day)
                    for day in data
                ]
