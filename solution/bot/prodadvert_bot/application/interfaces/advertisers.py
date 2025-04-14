from abc import ABC, abstractmethod

from prodadvert_bot.application.entities import Advertiser, MetricsResponse, MetricsWithDateResponse


class AdvertiserService(ABC):
    @abstractmethod
    async def get_advertiser(self, uid: str) -> Advertiser | None:
        """Get advertiser or none if not found."""

    @abstractmethod
    async def get_stats(self, uid: str) -> MetricsResponse:
        """Get total stats."""

    @abstractmethod
    async def get_daily_stats(self, uid: str) -> list[MetricsWithDateResponse]:
        """Get dailt stats."""


def convert_daily_stats_for_plotter(
        metrics: list[MetricsWithDateResponse]
) -> tuple[list[int], list[int], list[int]]:
    if not metrics:
        return [], [], []
    max_day = max(metric.date for metric in metrics)
    days = {
        metric.date: metric for metric in metrics
    }
    start_day = max(0, max_day - 14)
    days_scale = list(range(start_day, max_day + 1))
    views = [
        (days[day].impressions_count if day in days else 0)
        for day in days_scale
    ]
    clicks = [
        (days[day].clicks_count if day in days else 0)
        for day in days_scale
    ]
    return days_scale, views, clicks
