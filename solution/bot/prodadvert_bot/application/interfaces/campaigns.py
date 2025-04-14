from abc import ABC, abstractmethod

from prodadvert_bot.application.entities import Campaign, MetricsResponse, MetricsWithDateResponse
from prodadvert_bot.application.exceptions import CampaignCreateException
from prodadvert_bot.decorators import raises


class CampaignService(ABC):
    @abstractmethod
    async def get_of_advertiser(self, advertiser_id: str) -> list[Campaign]:
        """Get all campaigns."""

    @abstractmethod
    @raises(CampaignCreateException)
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
        """Create campaign."""

    @abstractmethod
    async def get(self, advertiser_uid: str, uid: str) -> Campaign | None:
        """Get campaign by UUID."""

    @abstractmethod
    async def get_stats(self, uid: str) -> MetricsResponse:
        """Get total stats."""

    @abstractmethod
    async def get_daily_stats(self, uid: str) -> list[MetricsWithDateResponse]:
        """Get dailt stats."""

    @abstractmethod
    @raises(CampaignCreateException)
    async def update(
            self,
            advertiser_uid: str,
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
        """Update campaign."""

    @abstractmethod
    async def delete_image(self, advertiser_uid: str, uid: str) -> bool:
        """Delete campaign image."""

    @abstractmethod
    async def upload_image(
            self,
            advertiser_uid: str,
            uid: str,
            image
    ) -> bool:
        """Upload campaign image."""
