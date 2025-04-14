from typing import final
from uuid import UUID

from attrs import frozen

from prodadvert.domain.entities import TargetingGender


@frozen
@final
class NewClientDTO:
    client_id: UUID
    login: str
    age: int
    location: str
    gender: str


@frozen
@final
class NewAdvertiserDTO:
    advertiser_id: UUID
    name: str


@frozen
@final
class CampaignTargetingDTO:
    gender: TargetingGender | None = None
    age_from: int | None = None
    age_to: int | None = None
    location: str | None = None


@frozen
@final
class NewCampaignDTO:
    advertiser_id: UUID
    ad_title: str
    ad_text: str
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    start_date: int
    end_date: int
    target: CampaignTargetingDTO = CampaignTargetingDTO()


@frozen
@final
class UpdateCampaignDTO:
    cost_per_impression: float | None = None
    cost_per_click: float | None = None
    ad_title: str | None = None
    ad_text: str | None = None
    start_date: int | None = None
    end_date: int | None = None
    impressions_limit: int | None = None
    clicks_limit: int | None = None
    target: CampaignTargetingDTO = CampaignTargetingDTO()
