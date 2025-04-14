import uuid

from dataclasses import dataclass
from typing import final

import pytest

from prodadvert.domain.entities import Advertiser
from prodadvert.domain.recommendation import Recommender
from tests.unit.data_gen import new_campaign, new_client


@dataclass
@final
class CampaignMetrics:
    views: int
    clicks: int


@pytest.mark.parametrize("current_date", [3])
@pytest.mark.parametrize(
    ("campaigns", "expected"),
    [
        (
            [
                new_campaign("A", cost_per_impression=1),
                new_campaign("B", cost_per_impression=2, end_date=2)
            ],
            "A"
        ),
        (
            [
                new_campaign("A", cost_per_impression=2, start_date=4),
                new_campaign("B", cost_per_impression=1)
            ],
            "B"
        ),
        (
            [
                new_campaign("A", start_date=4),
                new_campaign("B", end_date=2),
            ],
            None
        )
    ]
)
def test_algorithm_filter_date(
        campaigns,
        expected,
        current_date
):
    advertiser = Advertiser(uuid.uuid4(), "Advertiser")
    for campaign in campaigns:
        campaign.advertiser = advertiser
    client = new_client({advertiser.id: 1})
    recommender = Recommender(
        client,
        campaigns,
        current_date,
        campaign_clicks={campaign.id: 0 for campaign in campaigns},
        campaign_shows={campaign.id: 0 for campaign in campaigns},
        client_seen=set()
    )
    campaign = recommender.get_best_campaign()
    if expected:
        assert campaign is not None, "Campaign is none"
        assert campaign.ad_title == expected
    else:
        assert campaign is None


@pytest.mark.parametrize(
    ("campaigns", "metrics", "expected"),
    [
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            [
                CampaignMetrics(12, 12),
                CampaignMetrics(0, 0)
            ],
            "B"
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            [
                CampaignMetrics(0, 12),
                CampaignMetrics(0, 0)
            ],
            "B"
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            [
                CampaignMetrics(12, 0),
                CampaignMetrics(0, 0)
            ],
            "B"
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            [
                CampaignMetrics(12, 0),
                CampaignMetrics(0, 12)
            ],
            None
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            [
                CampaignMetrics(10, 0),
                CampaignMetrics(0, 12)
            ],
            "A"
        ),
    ]
)
def test_algorithm_filter_limits(
        campaigns,
        metrics,
        expected
):
    advertiser = Advertiser(uuid.uuid4(), "Advertiser")
    for campaign in campaigns:
        campaign.advertiser = advertiser
    client = new_client({advertiser.id: 1})
    recommender = Recommender(
        client,
        campaigns,
        current_date=1,
        campaign_clicks={
            campaign.id: metrics[i].clicks
            for i, campaign in enumerate(campaigns)
        },
        campaign_shows={
            campaign.id: metrics[i].views
            for i, campaign in enumerate(campaigns)
        },
        client_seen=set()
    )
    campaign = recommender.get_best_campaign()
    if expected:
        assert campaign is not None, "Campaign is none"
        assert campaign.ad_title == expected
    else:
        assert campaign is None


@pytest.mark.parametrize(
    ("campaigns", "seen", "expected"),
    [
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            {"A"},
            "B"
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=20),
                new_campaign("C", cost_per_impression=2),
            ],
            {"B"},
            "A"
        ),
        (
            [
                new_campaign("A", cost_per_impression=20),
                new_campaign("B", cost_per_impression=2),
            ],
            {"A", "B"},
            None
        ),
    ]
)
def test_algorithm_filter_seen(
        campaigns,
        seen,
        expected
):
    advertiser = Advertiser(uuid.uuid4(), "Advertiser")
    for campaign in campaigns:
        campaign.advertiser = advertiser
    client = new_client({advertiser.id: 1})
    recommender = Recommender(
        client,
        campaigns,
        current_date=1,
        campaign_clicks={campaign.id: 0 for campaign in campaigns},
        campaign_shows={campaign.id: 0 for campaign in campaigns},
        client_seen={
            next(
                campaign.id for campaign in campaigns
                if campaign.ad_title == title
            )
            for title in seen
        }
    )
    campaign = recommender.get_best_campaign()
    if expected:
        assert campaign is not None, "Campaign is none"
        assert campaign.ad_title == expected
    else:
        assert campaign is None
