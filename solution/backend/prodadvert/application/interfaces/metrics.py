"""Defines application-level interfaces for metrics."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, final
from uuid import UUID

from attrs import frozen

from prodadvert.domain.entities import Campaign


@final
@frozen
class Metrics:
    views: int
    clicks: int
    spent_views: float
    spent_clicks: float

    @property
    def conversion(self) -> float:
        """Get conversion percentage."""
        return self.clicks / self.views * 100 if self.views != 0 else 0

    @property
    def spent_total(self) -> float:
        """Get total for metrics."""
        return self.spent_views + self.spent_clicks


@final
@dataclass
class DailyMetrics:
    views: int
    clicks: int
    spent_views: float
    spent_clicks: float
    date: int

    @property
    def conversion(self) -> float:
        """Get conversion percentage."""
        return self.clicks / self.views * 100 if self.views != 0 else 0

    @property
    def spent_total(self) -> float:
        """Get total for metrics."""
        return self.spent_views + self.spent_clicks


class MetricsGateway(ABC):
    """Provides access to metrics storage."""

    @abstractmethod
    async def get_views_for_each(self) -> Mapping[UUID, int]:
        """Get views for each campaign."""

    @abstractmethod
    async def get_clicks_for_each(self) -> Mapping[UUID, int]:
        """Get clicks for each campaign."""

    @abstractmethod
    async def count_click(
            self, client_id: UUID, campaign: Campaign, date: int
    ) -> None:
        """Count click (if hasn't been done before)."""

    @abstractmethod
    async def count_view(
            self, client_id: UUID, campaign: Campaign, date: int
    ) -> None:
        """Count view (if hasn't been done before)."""

    @abstractmethod
    async def get_stats_of_campaign(self, campaign_id: UUID) -> Metrics:
        """Get stats of campaign."""

    @abstractmethod
    async def get_stats_of_advertiser(
            self, advertiser_id: UUID
    ) -> Metrics:
        """Get aggregated stats of advertiser."""

    @abstractmethod
    async def get_daily_stats_of_campaign(
            self,
            campaign_id: UUID,
            from_day: int = 0,
            to_day: int = -1
    ) -> list[DailyMetrics]:
        """Get stats of campaign grouped by days."""

    @abstractmethod
    async def get_daily_stats_of_advertiser(
            self,
            advertiser_id: UUID,
            from_day: int = 0,
            to_day: int = -1
    ) -> list[DailyMetrics]:
        """Get aggregated stats of advertiser grouped by days."""

    @abstractmethod
    async def get_client_seen(self, client_id: UUID) -> set[UUID]:
        """Get adverts that client has already seen."""
