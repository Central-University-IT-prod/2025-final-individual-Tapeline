import uuid

import pytest

from prodadvert.domain.entities import Client, Gender, TargetingGender, Advertiser
from prodadvert.domain.recommendation import Recommender
from tests.unit.data_gen import new_campaign


def _client(age, gender, location):
    return Client(
        id=uuid.uuid4(),
        login="login",
        age=age,
        gender=Gender(gender),
        location=location
    )


_client1 = _client(18, "MALE", "Ufa")
_matching = []
for g in [None, TargetingGender.MALE, TargetingGender.ALL]:
    for af in [None, 10, 18]:
        for at in [None, 24, 50]:
            for loc in [None, "Ufa"]:
                _matching.append(
                    new_campaign(
                        "matching",
                        target_gender=g,
                        target_age_from=af,
                        target_age_to=at,
                        target_location=loc
                    )
                )
_non_matching = []
for af, at in [(10, 16), (23, 35)]:
    for loc in ["Piter", "Moscow"]:
        _non_matching.append(
            new_campaign(
                "matching",
                target_gender=TargetingGender.FEMALE,
                target_age_from=af,
                target_age_to=at,
                target_location=loc
            )
        )

@pytest.mark.parametrize(
    "campaign", _matching
)
def test_matching_targeting(campaign):
    advertiser = Advertiser(uuid.uuid4(), "Advertiser")
    campaign.advertiser = advertiser
    _client1.relations[advertiser.id] = 1
    recommender = Recommender(
        _client1,
        [campaign],
        current_date=1,
        campaign_clicks={campaign.id: 0},
        campaign_shows={campaign.id: 0},
        client_seen=set()
    )
    campaign = recommender.get_best_campaign()
    assert campaign is not None


@pytest.mark.parametrize(
    "campaign", _non_matching
)
def test_non_matching_targeting(campaign):
    advertiser = Advertiser(uuid.uuid4(), "Advertiser")
    campaign.advertiser = advertiser
    _client1.relations[advertiser.id] = 1
    recommender = Recommender(
        _client1,
        [campaign],
        current_date=1,
        campaign_clicks={campaign.id: 0},
        campaign_shows={campaign.id: 0},
        client_seen=set()
    )
    campaign = recommender.get_best_campaign()
    assert campaign is None
