import uuid

from prodadvert.domain.entities import Campaign, Advertiser, Gender, Client


def new_campaign(title: str, **kwargs) -> Campaign:
    args = {
        "id": uuid.uuid4(),
        "ad_title": title,
        "ad_text": "Campaign text",
        "cost_per_click": 1,
        "cost_per_impression": 1,
        "impressions_limit": 10,
        "clicks_limit": 10,
        "start_date": 0,
        "end_date": 7,
        "target_gender": None,
        "target_age_from": None,
        "target_age_to": None,
        "target_location": None,
        "advertiser": Advertiser(uuid.uuid4(), "Advertiser")
    }
    return Campaign(**(args | kwargs))


def new_client(relations: dict[uuid.UUID, int], **kwargs) -> Client:
    args = {
        "id": uuid.uuid4(),
        "login": "client",
        "age": 18,
        "location": "Moscow",
        "gender": Gender.MALE,
        "relations": relations
    }
    return Client(**(args | kwargs))
