import random
import time
import uuid
from dataclasses import dataclass

from prodadvert.domain.entities import Client, Campaign, Advertiser, Gender
from prodadvert.domain.recommendation import Recommender


class SimulatedCampaign:
    def __init__(self, campaign: Campaign) -> None:
        self.campaign = campaign
        self.clicks = set()
        self.views = set()

    def click(self, client: "SimulatedClient"):
        self.clicks.add(client.client.id)

    def view(self, client: "SimulatedClient"):
        self.views.add(client.client.id)


class SimulatedClient:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.seen = set()

    def make_decision(self, campaign: SimulatedCampaign) -> bool:
        relation = self.client.relations.get(
            campaign.campaign.advertiser.id, 0
        )
        relation_score = relation / max(self.client.relations.values())
        should_click = random.random() >= relation_score
        campaign.view(self)
        self.seen.add(campaign.campaign.id)
        if should_click:
            campaign.click(self)
        return should_click


def generate_advertisers(n: int) -> list[Advertiser]:
    adv = []
    for i in range(n):
        adv.append(Advertiser(uuid.uuid4(), str(i)))
    return adv


def generate_campaigns_for_adv(
        advertiser: Advertiser, n: int,
        client_count: int
) -> list[Campaign]:
    cmp = []
    for i in range(n):
        cmp.append(Campaign(
            id=uuid.uuid4(),
            advertiser=advertiser,
            ad_title=f"{advertiser.name}_{i}",
            ad_text=f"{advertiser.name}_{i}",
            start_date=0,
            end_date=7,
            impressions_limit=random.randint(5, client_count // 2),
            clicks_limit=random.randint(5, client_count // 2),
            cost_per_impression=random.randint(10, 10000) / 100,
            cost_per_click=random.randint(10, 10000) / 100,
            target_gender=None,
            target_location=None,
            target_age_to=None,
            target_age_from=None
        ))
    return cmp


def generate_clients(n: int) -> list[Client]:
    return [
        Client(
            id=uuid.uuid4(),
            login=str(i),
            location="test",
            age=18,
            gender=Gender.MALE,
            relations={}
        )
        for i in range(n)
    ]


def populate_ml_scores(
        clients: list[Client],
        advertisers: list[Advertiser]
):
    for client in clients:
        for advertiser in advertisers:
            client.relations[advertiser.id] = random.randint(0, 10000)


@dataclass
class SimScoreParameter:
    min: float
    max: float
    avg: float
    sum: float
    top: float

    def _det_sym(self, x: float) -> str:
        if x > 0.75:
            return "⣿"
        if x > 0.50:
            return "⣶"
        if x > 0.25:
            return "⣤"
        if x > 0.0:
            return "⣀"
        return "⠀"

    def _det_syms(self, x: float) -> tuple[str, str, str]:
        return (
            self._det_sym(min(max([0, x - 0.66]) / 0.33, 1)),
            self._det_sym(min(max([0, x - 0.33]) / 0.33, 1)),
            self._det_sym(min(max([0, x]) / 0.33, 1)),
        )

    def _det_hor_sym(self, x: float) -> str:
        if x < 0.3:
            return " "
        if x < 0.6:
            return "▌"
        return "█"

    def _det_hor_syms(self, x: float) -> str:
        syms = []
        s = 0.0
        while s < 1:
            syms.append(self._det_hor_sym(min(max([0, x - s]) / 0.04, 1)))
            s += 0.04
        return "".join(syms)

    def print(self, name: str, horizontal=True):
        if horizontal:
            print(f"{name}" + " "*(28-len(name)) + "|-100%")
            print(f"min {self._det_hor_syms(self.min)}")
            print(f"max {self._det_hor_syms(self.max)}")
            print(f"avg {self._det_hor_syms(self.avg)}")
            print(f"sum {self.sum}")
            print(f"top {self.top}")
            print("----------------------------------")
        else:
            print(f"{name}: (sum={self.sum}; top={self.top})")
            print("min max avg")
            min_s = self._det_syms(self.min)
            max_s = self._det_syms(self.max)
            avg_s = self._det_syms(self.avg)
            print(f" {min_s[0]}   {max_s[0]}   {avg_s[0]}")
            print(f" {min_s[1]}   {max_s[1]}   {avg_s[1]}")
            print(f" {min_s[2]}   {max_s[2]}   {avg_s[2]}")
            print("-----------")


@dataclass
class SimScore:
    income: SimScoreParameter
    relevancy: SimScoreParameter
    targets: SimScoreParameter

    @property
    def total_avg(self) -> float:
        return (
            0.5 * self.income.avg +
            0.25 * self.relevancy.avg +
            0.15 * self.targets.avg
        )


@dataclass
class SimSpace:
    clients: list[Client]
    advertisers: list[Advertiser]
    campaigns: list[Campaign]
    _sim_clients = None
    _sim_campaigns = None

    def __init__(self, clients, advertisers, campaigns) -> None:
        self.clients = clients
        self.advertisers = advertisers
        self.campaigns = campaigns
        self._incomes = []
        self._ml_scores = []

    @property
    def sim_clients(self):
        if not self._sim_clients:
            self._sim_clients = [
                SimulatedClient(client) for client in self.clients
            ]
        return self._sim_clients

    @property
    def sim_campaigns(self):
        if not self._sim_campaigns:
            self._sim_campaigns = {
                campaign.id: SimulatedCampaign(campaign)
                for campaign in self.campaigns
            }
        return self._sim_campaigns

    @classmethod
    def generate(
            cls,
            n_clients: int,
            n_advertisers: int,
            n_campaigns_per_advertiser: int
    ) -> "SimSpace":
        clients = generate_clients(n_clients)
        advertisers = generate_advertisers(n_advertisers)
        populate_ml_scores(clients, advertisers)
        campaigns = []
        for advertiser in advertisers:
            campaigns.extend(generate_campaigns_for_adv(
                advertiser, n_campaigns_per_advertiser,
                n_clients
            ))
        return SimSpace(
            clients=clients,
            advertisers=advertisers,
            campaigns=campaigns
        )

    def run_sim(self, recommender_class):
        for client in self.sim_clients:
            recommender = recommender_class(
                client.client,
                self.campaigns,
                0,
                {
                    cmp.campaign.id: len(cmp.clicks)
                    for cmp in self.sim_campaigns.values()
                },
                {
                    cmp.campaign.id: len(cmp.views)
                    for cmp in self.sim_campaigns.values()
                },
                client.seen
            )
            best = recommender.get_best_campaign()
            self._ml_scores.append(
                client.client.relations[best.advertiser.id]
            )
            clicked = client.make_decision(self.sim_campaigns[best.id])
            if clicked:
                self._incomes.append(
                    best.cost_per_click + best.cost_per_impression
                )
            else:
                self._incomes.append(best.cost_per_impression)

    def determine_scores(self) -> SimScore:
        top_costs = [
            cmp.cost_per_click + cmp.cost_per_impression
            for cmp in self.campaigns
        ]
        top_ml_scores = [
            max(client.relations.values())
            for client in self.clients
        ]
        targeting = [
            (
                len(sim_cmp.clicks) / sim_cmp.campaign.clicks_limit +
                len(sim_cmp.views) / sim_cmp.campaign.impressions_limit
            ) / 2
            for sim_cmp in self.sim_campaigns.values()
        ]
        costs_parameter = _det_param(self._incomes, top_costs)
        ml_score_parameter = _det_param(self._ml_scores, top_ml_scores)
        targeting_parameter = _det_param(
            targeting,
            [1.0] * len(targeting)
        )
        return SimScore(
            targets=targeting_parameter,
            income=costs_parameter,
            relevancy=ml_score_parameter
        )


def _det_param(
        collection: list[float], top_collection: list[float]
) -> SimScoreParameter:
    return SimScoreParameter(
        min=min(collection) / max(top_collection),
        max=max(collection) / max(top_collection),
        sum=sum(collection),
        avg=(sum(collection) / len(collection)) / max(top_collection),
        top=max(top_collection)
    )


def run_for_recommender(recommender_class):
    print(f"{recommender_class.__name__}:")
    random.seed(1337)
    #space = SimSpace.generate(10000, 500, 20)
    space = SimSpace.generate(1000, 100, 100)
    s = time.time()
    space.run_sim(recommender_class)
    e = time.time()
    print(e - s)
    results = space.determine_scores()
    results.income.print("income")
    results.relevancy.print("relevancy")
    results.targets.print("targets")
    print("===\n\n")


def main():
    run_for_recommender(Recommender)
    #run_for_recommender(MaxCostRecommender)
    #run_for_recommender(MaxMLScoreRecommender)
    #run_for_recommender(MaxTargetRecommender)


if __name__ == '__main__':
    main()
