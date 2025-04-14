from _operator import attrgetter
from typing import Mapping
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.application.interfaces.metrics import MetricsGateway, DailyMetrics, Metrics
from prodadvert.domain.entities import Campaign
from prodadvert.infrastructure.persistence.cache import Cache
from prodadvert.infrastructure.persistence.models import MetricModel, MetricType


class MetricsGatewayImpl(MetricsGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_views_for_each(self) -> Mapping[UUID, int]:
        if Cache.cached_views:
            return Cache.cached_views
        views = {}
        query = text("""
            SELECT campaigns.id, cnt FROM campaigns
            LEFT JOIN (
                SELECT metrics.campaign_id, count(metrics.id) as cnt
                FROM metrics
                WHERE fact = 'SHOW'
                GROUP BY metrics.campaign_id
            ) as intr ON intr.campaign_id = campaigns.id;
        """)
        rows = await self._session.execute(query)
        for campaign_id, cnt in rows:
            views[UUID(str(campaign_id))] = int(cnt or 0)
        Cache.cached_views = views
        return views

    async def get_clicks_for_each(self) -> Mapping[UUID, int]:
        if Cache.cached_clicks:
            return Cache.cached_clicks
        clicks = {}
        query = text("""
            SELECT campaigns.id, cnt FROM campaigns
            LEFT JOIN (
                SELECT metrics.campaign_id, count(metrics.id) as cnt
                FROM metrics
                WHERE fact = 'CLICK'
                GROUP BY metrics.campaign_id
            ) as intr ON intr.campaign_id = campaigns.id;
        """)
        rows = await self._session.execute(query)
        for campaign_id, cnt in rows:
            clicks[UUID(str(campaign_id))] = int(cnt or 0)
        Cache.cached_clicks = clicks
        return clicks

    async def count_click(
            self, client_id: UUID, campaign: Campaign, date: int
    ) -> None:
        models = await self._session.execute(
            select(MetricModel).filter(
                MetricModel.fact == MetricType.CLICK,
                MetricModel.client_id == client_id,
                MetricModel.campaign_id == campaign.id
            )
        )
        if models.first():  # pragma: no cover
            # generally should not happen, as there are many checks behind
            return
        if Cache.cached_clicks and campaign.id in Cache.cached_clicks:
            Cache.cached_clicks[campaign.id] += 1
        elif Cache.cached_clicks:
            Cache.cached_clicks[campaign.id] = 1
        model = MetricModel(
            fact=MetricType.CLICK,
            client_id=client_id,
            campaign_id=campaign.id,
            cost=campaign.cost_per_click,
            date=date,
        )
        self._session.add(model)
        await self._session.commit()

    async def count_view(
            self, client_id: UUID, campaign: Campaign, date: int
    ) -> None:
        models = await self._session.execute(
            select(MetricModel).filter(
                MetricModel.fact == MetricType.SHOW,
                MetricModel.client_id == client_id,
                MetricModel.campaign_id == campaign.id
            )
        )
        if models.first():  # pragma: no cover
            # generally should not happen, as there are many checks behind
            return
        if Cache.cached_views and campaign.id in Cache.cached_views:
            Cache.cached_views[campaign.id] += 1
        elif Cache.cached_views:
            Cache.cached_views[campaign.id] = 1
        model = MetricModel(
            fact=MetricType.SHOW,
            client_id=client_id,
            campaign_id=campaign.id,
            cost=campaign.cost_per_impression,
            date=date,
        )
        self._session.add(model)
        await self._session.commit()

    async def get_stats_of_campaign(self, campaign_id: UUID) -> Metrics:
        query = text(f"""
            SELECT fact, count(fact), sum(cost)
            FROM metrics
            WHERE campaign_id = '{campaign_id}'
            GROUP BY fact;
        """)
        rows = await self._session.execute(query)
        views_count: int = 0
        clicks_count: int = 0
        spent_views: float = 0
        spent_clicks: float = 0
        for fact, count, cost in rows:
            if fact == "SHOW":
                views_count = count
                spent_views = cost
            else:
                clicks_count = count
                spent_clicks = cost
        return Metrics(views_count, clicks_count, spent_views, spent_clicks)

    async def get_stats_of_advertiser(self, advertiser_id: UUID) -> Metrics:
        query = text(f"""
            SELECT subt.fact, sum(subt.metric_count), sum(subt.sum_cost) FROM (
                SELECT fact, count(fact) as metric_count, sum(cost) as sum_cost FROM metrics
                JOIN campaigns c on c.id = metrics.campaign_id
                WHERE c.advertiser_id = '{advertiser_id}'
                GROUP BY fact, campaign_id
            ) AS subt
            GROUP BY subt.fact;
        """)
        rows = await self._session.execute(query)
        views_count: int = 0
        clicks_count: int = 0
        spent_views: float = 0
        spent_clicks: float = 0
        for fact, count, cost in rows:
            if fact == "SHOW":
                views_count = count
                spent_views = cost
            else:
                clicks_count = count
                spent_clicks = cost
        return Metrics(views_count, clicks_count, spent_views, spent_clicks)

    async def get_daily_stats_of_campaign(
            self,
            campaign_id: UUID,
            from_day: int = 0,
            to_day: int = -1
    ) -> list[DailyMetrics]:
        paginate = _create_pagination_clause(from_day, to_day)
        query = text(f"""
            SELECT fact, date, count(fact), sum(cost)
            FROM metrics
            WHERE campaign_id = '{campaign_id}' AND {paginate}
            GROUP BY fact, date;
        """)
        rows = await self._session.execute(query)
        metrics = {}
        for fact, date, count, cost in rows:
            if date not in metrics:
                metrics[date] = DailyMetrics(0, 0, 0, 0, date)
            if fact == "SHOW":
                metrics[date].views = count
                metrics[date].spent_views = cost
            else:
                metrics[date].clicks = count
                metrics[date].spent_clicks = cost
        return sorted(
            metrics.values(),
            key=attrgetter("date")
        )

    async def get_daily_stats_of_advertiser(
            self,
            advertiser_id: UUID,
            from_day: int = 0,
            to_day: int = -1
    ) -> list[DailyMetrics]:
        paginate = _create_pagination_clause(from_day, to_day)
        query = text(f"""
            SELECT subt.fact, subt.date, sum(subt.metric_count), sum(subt.sum_cost) FROM (
                SELECT fact, date as date, count(fact) as metric_count, sum(cost) as sum_cost FROM metrics
                JOIN campaigns c on c.id = metrics.campaign_id
                WHERE c.advertiser_id = '{advertiser_id}' AND {paginate}
                GROUP BY fact, campaign_id, date
            ) AS subt
            GROUP BY subt.fact, date;
        """)
        rows = await self._session.execute(query)
        metrics = {}
        for fact, date, count, cost in rows:
            if date not in metrics:
                metrics[date] = DailyMetrics(0, 0, 0, 0, date)
            if fact == "SHOW":
                metrics[date].views = count
                metrics[date].spent_views = cost
            else:
                metrics[date].clicks = count
                metrics[date].spent_clicks = cost
        return sorted(
            metrics.values(),
            key=attrgetter("date")
        )

    async def get_client_seen(self, client_id: UUID) -> set[UUID]:
        models = await self._session.execute(
            select(MetricModel).filter(
                MetricModel.fact == MetricType.SHOW,
                MetricModel.client_id == client_id,
            )
        )
        return set(
            _ensure_uuid(metric.campaign_id)
            for metric in models.scalars().all()
        )


def _create_pagination_clause(from_day: int = 0, to_day: int = -1) -> str:
    clause = f"date >= {from_day}"
    if to_day > 0:
        clause += f" AND date <= {to_day}"
    return f"({clause})"


def _ensure_uuid(uid: str | UUID) -> UUID:
    return uid if isinstance(uid, UUID) else UUID(uid)
