from dataclasses import dataclass
from enum import Enum
from typing import final

from pydantic import BaseModel


@final
@dataclass
class Advertiser:
    """Represents an advertiser."""

    id: str
    name: str


class TargetingGender(Enum):
    """Represents a targeting gender."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"


@final
@dataclass
class Campaign:
    """Represents a campaign."""

    id: str
    advertiser_id: str
    ad_title: str
    ad_text: str
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    start_date: int
    end_date: int
    target_gender: TargetingGender | None
    target_age_from: int | None
    target_age_to: int | None
    target_location: str | None
    image_uri: str | None = None


class MetricsResponse(BaseModel):
    impressions_count: int = 0
    clicks_count: int = 0
    conversion: float = 0
    spent_impressions: float = 0
    spent_clicks: float = 0
    spent_total: float = 0


class MetricsWithDateResponse(MetricsResponse):
    date: int = 0
