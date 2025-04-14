import json
import time
from _operator import itemgetter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import requests

@dataclass
class Measurement:
    values: list

    @property
    def max(self):
        return max(self.values) if self.values else None

    @property
    def min(self):
        return min(self.values) if self.values else None

    @property
    def avg(self):
        return sum(self.values) / len(self.values) if self.values else None

    def __str__(self) -> str:
        return f"min: {self.min}  max: {self.max}  avg: {self.avg}"


_MEASUREMENTS: dict[str, Measurement] = {}


@contextmanager
def measure_time(name, divide_by: int = 1):
    s = time.time()
    yield
    e = time.time()
    m = (1000 * (e - s)) / divide_by if divide_by != 0 else 0
    if name in _MEASUREMENTS:
        _MEASUREMENTS[name].values.append(m)
    else:
        _MEASUREMENTS[name] = Measurement([m])


def endpoint(path):
    return f"http://REDACTED:8080{path}"


def create_clients():
    clients = json.loads(Path("bulk_clients.json").read_text())
    with measure_time("clients", 1):
        requests.post(
            endpoint("/clients/bulk"),
            json=clients
        )
    return list(map(itemgetter("client_id"), clients))


def create_advertisers():
    with measure_time("advertisers", 1):
        requests.post(
            endpoint("/advertisers/bulk"),
            json=json.loads(Path("advertisers.json").read_text())
        )


def create_scores():
    scores = json.loads(Path("ml_scores.json").read_text())
    with measure_time("scores", len(scores)):
        for data in scores:
            requests.post(endpoint("/ml-scores"), json=data)


def create_campaigns():
    campaigns = json.loads(Path("campaigns.json").read_text())
    with measure_time("campaigns", len(campaigns)):
        for campaign in campaigns:
            requests.post(
                endpoint(f"/advertisers/{campaign['advertiser_id']}/campaigns"),
                json=campaign["campaign_data"]
            )


def get_for_clients(client_ids):
    ads = {}
    for client_id in client_ids:
        with measure_time("ads", 1):
            response = requests.get(
                endpoint("/ads"),
                params={"client_id": client_id}
            )
            if response.status_code == 200:
                ads[client_id] = response.json()["ad_id"]
    return ads


def click(ads):
    with measure_time("clicks", len(ads)):
        for client_id, ad_id in ads.items():
            requests.post(
                endpoint(f"/ads/{ad_id}/click"),
                json={"client_id": client_id}
            )


def set_date(date):
    with measure_time("date", 1):
        requests.post(
            endpoint("/time/advance"),
            json={"current_date": date}
        )


def main():
    print("Creating clients")
    clients = create_clients()
    print("Creating advertisers")
    #create_advertisers()
    print("Creating scores")
    #create_scores()
    print("Creating campaigns")
    #create_campaigns()
    for day in range(1, 21):
        print(f"---- Day {day} ----")
        print("Getting ads")
        ads = get_for_clients(clients)
        print(ads)
        print("Clicking ads")
        click(ads)
    for k, v in _MEASUREMENTS.items():
        print(f"{k}: {v} ms")


if __name__ == '__main__':
    main()
