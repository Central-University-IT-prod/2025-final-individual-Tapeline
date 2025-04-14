from typing import Mapping
from uuid import UUID

from prodadvert.domain.entities import Client, Campaign


class _MaximizingRecommenderBase:
    _allowed_overlimit: float = 0.05

    def __init__(
            self,
            client: Client,
            campaigns: list[Campaign],
            current_date: int,
            campaign_clicks: Mapping[UUID, int],
            campaign_shows: Mapping[UUID, int],
            client_seen: set[UUID] | None = None
    ) -> None:
        self.client = client
        self.campaigns = campaigns
        self.current_date = current_date
        self.campaign_clicks = campaign_clicks
        self.campaign_shows = campaign_shows
        self.client_seen = client_seen or set()
        self.best_relation: float = max(
            rel_value for rel_value in self.client.relations.values()
        )
        self.best_price = 1

    def _are_limits_kept(self, campaign: Campaign) -> bool:
        return (
            campaign.clicks_limit * (1 + self._allowed_overlimit)
            > self.campaign_clicks[campaign.id]
            and campaign.impressions_limit * (1 + self._allowed_overlimit)
            > self.campaign_shows[campaign.id]
        )

    def _filter_campaigns(self) -> None:
        self.campaigns = list(filter(
            lambda campaign: (
                self._are_limits_kept(campaign)
                and campaign.id not in self.client_seen
            ),
            self.campaigns
        ))
        if not self.campaigns:
            return
        self.best_price = max(
            campaign.cost_per_click + campaign.cost_per_impression
            for campaign in self.campaigns
        )

    def maximize_cost(self, campaign: Campaign) -> float:
        return campaign.cost_per_impression + campaign.cost_per_click

    def maximize_ml_score(self, campaign: Campaign) -> float:
        return self.client.relations[campaign.advertiser.id]

    def maximize_targets(self, campaign: Campaign) -> float:
        return campaign.impressions_limit - self.campaign_shows.get(campaign.id, 0)


class MaxCostRecommender(_MaximizingRecommenderBase):
    def get_best_campaign(self) -> Campaign | None:
        self._filter_campaigns()
        return sorted(self.campaigns, key=self.maximize_cost, reverse=True)[0]


class MaxMLScoreRecommender(_MaximizingRecommenderBase):
    def get_best_campaign(self) -> Campaign | None:
        self._filter_campaigns()
        return sorted(self.campaigns, key=self.maximize_ml_score, reverse=True)[0]


class MaxTargetRecommender(_MaximizingRecommenderBase):
    def get_best_campaign(self) -> Campaign | None:
        self._filter_campaigns()
        return sorted(self.campaigns, key=self.maximize_targets, reverse=True)[0]
