"""Contains entities."""
import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import final, Sequence, Self
from uuid import UUID


class Gender(Enum):
    """Represents a gender."""

    MALE = "MALE"
    FEMALE = "FEMALE"


@final
@dataclass
class Client:
    """Represents a client."""

    id: UUID
    login: str
    age: int
    location: str
    gender: Gender
    relations: dict[UUID, int] = field(default_factory=dict)


@final
@dataclass
class Advertiser:
    """Represents an advertiser."""

    id: UUID
    name: str


class TargetingGender(Enum):
    """Represents a targeting gender."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"

    @property
    def genders(self) -> Sequence[Gender]:
        if self == TargetingGender.MALE:
            return [Gender.MALE]
        if self == TargetingGender.FEMALE:
            return [Gender.FEMALE]
        if self == TargetingGender.ALL:
            return [Gender.MALE, Gender.FEMALE]
        return []  # pragma: no cover


@final
@dataclass
class Campaign:
    id: UUID
    advertiser: Advertiser
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

    def copy(self) -> Self:
        return dataclasses.replace(self)
