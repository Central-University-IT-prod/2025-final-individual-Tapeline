import itertools
import random
import uuid
from typing import Callable
from uuid import UUID

from mimesis import Person, Address, Finance, Text


def client_json(**data) -> tuple[UUID, dict]:
    gen = {
        "client_id": str(uuid.uuid4()),
        "login": Person().username(),
        "age": random.randint(13, 120),
        "location": Address().address(),
        "gender": random.choice(("MALE", "FEMALE"))
    } | data
    return UUID(gen["client_id"]), gen


def advertiser_json(**data) -> tuple[UUID, dict]:
    gen = {
        "advertiser_id": str(uuid.uuid4()),
        "name": Finance().company(),
    } | data
    return UUID(gen["advertiser_id"]), gen


def campaign_json(**data) -> dict:
    gen = {
        "impressions_limit": random.randint(1, 100),
        "clicks_limit": random.randint(1, 100),
        "cost_per_impression": random.randint(1, 100) / random.randint(1, 100),
        "cost_per_click": random.randint(1, 100) / random.randint(1, 100),
        "ad_title": Text().word(),
        "ad_text": Text().sentence(),
        "start_date": random.randint(1, 100),
        "end_date": 100 + random.randint(1, 100),
        "targeting": {
            "gender": random.choice(("MALE", "FEMALE", "ALL", None)),
            "age_from": 13,
            "age_to": 45,
            "location": Address().address()
        },
        "image_uri": None
    } | data
    return gen


def subsets[T](data: set[T]) -> list[set[T]]:
    sets = [set()]
    for i in range(1, len(data)):
        for combination in itertools.combinations(data, i):
            sets.append(set(combination))
    return sets


def key_remover(*key_names: str) -> Callable[[dict], dict]:
    def inner(dictionary: dict) -> dict:
        copy = dictionary.copy()
        for key in key_names:
            copy.pop(key)
        return copy
    return inner
