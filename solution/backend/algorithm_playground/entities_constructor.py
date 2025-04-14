import uuid
from collections import defaultdict

from prodadvert.domain.entities import Campaign, Client, Advertiser, Gender


def construct_campaign(decl) -> tuple[Campaign, float, int]:
    name, decl = decl.strip().split("\n", maxsplit=1)
    args = parse_adv_decl(decl)
    return Campaign(
        id=uuid.uuid4(),
        ad_title=name,
        ad_text=name,
        advertiser=...,
        clicks_limit=args["v"][1],
        impressions_limit=args["v"][1],
        start_date=0,
        end_date=7,
        cost_per_click=args["ccost"],
        cost_per_impression=args["vcost"],
        target_gender=None,
        target_age_from=None,
        target_age_to=None,
        target_location=None,
    ), args["ml"], args["v"][0]


def parse_adv_decl(decl: str) -> dict:
    args = {k: eval(v) for k, v in (row.split() for row in decl.strip().split("\n"))}
    return args


def inject_entities(
        client: Client, campaigns: list[tuple[Campaign, float, int]]
) -> dict[uuid.UUID, int]:
    scores = defaultdict(list)
    views_dict = {}
    for campaign, ml, views in campaigns:
        scores[ml].append(campaign)
        views_dict[campaign.id] = views
    for ml, cs in scores.items():
        advertiser = Advertiser(uuid.uuid4(), "advertiser")
        for c in cs:
            c.advertiser = advertiser
        client.relations[advertiser.id] = ml
    return views_dict


def create_entities(
        code: list[str]
) -> tuple[Client, list[Campaign], dict[uuid.UUID, int]]:
    campaigns = [construct_campaign(args) for args in code]
    client = Client(uuid.uuid4(), "login", 18, "", Gender.MALE, {})
    views = inject_entities(client, campaigns)
    return client, [c[0] for c in campaigns], views
