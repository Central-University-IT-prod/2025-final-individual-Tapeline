import uuid
import pytest

from prodadvert.domain.entities import Advertiser
from prodadvert.domain.recommendation import Recommender
from tests.unit.data_gen import new_campaign, new_client


@pytest.mark.parametrize(
    ("campaigns", "expected"),
    [
        (
            [
                new_campaign("A", cost_per_impression=1),
                new_campaign("B", cost_per_impression=2)
            ],
            "B"
        ),
        (
            [
                new_campaign("A", cost_per_impression=2, cost_per_click=1),
                new_campaign("B", cost_per_impression=1, cost_per_click=2)
            ],
            "A"
        ),
        (
            [
                new_campaign("A", cost_per_impression=2, cost_per_click=1),
                new_campaign("B", cost_per_impression=1, cost_per_click=2),
                new_campaign("C", cost_per_impression=2, cost_per_click=2)
            ],
            "C"
        )
    ]
)
def test_algorithm_single_advertiser(
        campaigns,
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
        campaign_shows={campaign.id: 0 for campaign in campaigns}
    )
    campaign = recommender.get_best_campaign()
    assert campaign is not None, "Campaign is none"
    assert campaign.ad_title == expected


_advertiser_1 = Advertiser(uuid.uuid4(), "Adv1")
_advertiser_2 = Advertiser(uuid.uuid4(), "Adv2")
_relations = {_advertiser_1.id: 1, _advertiser_2.id: 3}


@pytest.mark.parametrize(
    ("campaigns", "expected"),
    [
        (
            [
                new_campaign(
                    "A",
                    cost_per_impression=1,
                    advertiser=_advertiser_1
                ),
                new_campaign(
                    "B",
                    cost_per_impression=2,
                    advertiser=_advertiser_2
                ),
            ],
            "B"
        ),
        (
            [
                new_campaign(
                    "A",
                    cost_per_impression=2,
                    cost_per_click=1,
                    advertiser=_advertiser_2
                ),
                new_campaign(
                    "B",
                    cost_per_impression=1,
                    cost_per_click=2,
                    advertiser=_advertiser_1
                ),
            ],
            "A"
        ),
        (
            [
                new_campaign(
                    "A",
                    cost_per_impression=2,
                    cost_per_click=1,
                    advertiser=_advertiser_1
                ),
                new_campaign(
                    "B",
                    cost_per_impression=1,
                    cost_per_click=2,
                    advertiser=_advertiser_1
                ),
                new_campaign(
                    "C",
                    cost_per_impression=1.7,
                    cost_per_click=1.7,
                    advertiser=_advertiser_2
                ),
            ],
            "C"
        )
    ]
)
def test_algorithm_multiple_advertisers(
        campaigns,
        expected
):
    client = new_client(_relations)
    recommender = Recommender(
        client,
        campaigns,
        current_date=1,
        campaign_clicks={campaign.id: 0 for campaign in campaigns},
        campaign_shows={campaign.id: 0 for campaign in campaigns}
    )
    campaign = recommender.get_best_campaign()
    assert campaign is not None, "Campaign is none"
    assert campaign.ad_title == expected
