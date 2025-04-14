from typing import Mapping
from uuid import UUID

from prodadvert.domain.entities import Client, Campaign


class Recommender:
    """
    Responsible for recommending advertisements.

    Algorithm:
        0. Filter by date
        1. Filter by limiting
        2. Filter by targeting
        3. Sort by ml score
        4. Sort by cost
    """

    _click_coeff: float = 1/3
    _view_coeff: float = 2/3
    # Actually should be 0.5, but works better with 0.9
    _cost_coeff: float = 0.9
    _ml_score_coeff: float = 0.25
    _allowed_overlimit: float = 0.05
    _target_coeff: float = 0.15

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
        self.best_price_per_click: float = 1
        self.best_price_per_view: float = 1

    def _is_date_applicable(self, campaign: Campaign) -> bool:
        return campaign.start_date <= self.current_date <= campaign.end_date

    def _are_limits_kept(self, campaign: Campaign) -> bool:
        return (
            campaign.clicks_limit * (1 + self._allowed_overlimit)
            > self.campaign_clicks.get(campaign.id, 0)
            and campaign.impressions_limit * (1 + self._allowed_overlimit)
            > self.campaign_shows.get(campaign.id, 0)
        )

    def _is_targeting_correct(self, campaign: Campaign) -> bool:
        return (
            (
                campaign.target_gender is None
                or self.client.gender in campaign.target_gender.genders
            ) and (
                campaign.target_location is None
                or campaign.target_location == self.client.location
            ) and (
                campaign.target_age_from is None
                or campaign.target_age_from <= self.client.age
            ) and (
                campaign.target_age_to is None
                or campaign.target_age_to >= self.client.age
            )
        )

    def _filter_campaigns(self) -> None:
        self.campaigns = list(filter(
            lambda campaign: (
                self._is_date_applicable(campaign)
                and self._are_limits_kept(campaign)
                and self._is_targeting_correct(campaign)
                and campaign.id not in self.client_seen
            ),
            self.campaigns
        ))
        if not self.campaigns:
            return
        self.best_price_per_click = max(
            campaign.cost_per_click
            for campaign in self.campaigns
        )
        self.best_price_per_view = max(
            campaign.cost_per_impression
            for campaign in self.campaigns
        )

    def _campaign_score(self, campaign: Campaign) -> float:
        click_score = (
            campaign.cost_per_click / self.best_price_per_click
            if self.best_price_per_click != 0 else 0
        )
        view_score = (
            campaign.cost_per_impression / self.best_price_per_view
            if self.best_price_per_view != 0 else 0
        )
        ml_score: float = self.client.relations[campaign.advertiser.id]
        if self.best_relation != 0:
            ml_score /= self.best_relation
        return (
            (
                click_score * self._click_coeff +
                view_score * self._view_coeff
            ) * self._cost_coeff +
            ml_score * self._ml_score_coeff +
            (1 - self.campaign_shows.get(campaign.id, 0)) * self._target_coeff
        )

    def _sort_campaigns(self) -> None:
        self.campaigns.sort(key=self._campaign_score, reverse=True)

    def get_best_campaign(self) -> Campaign | None:
        self._filter_campaigns()
        self._sort_campaigns()
        if self.campaigns:
            return self.campaigns[0]
        return None
