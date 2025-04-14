from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from prodadvert.application.interfaces.ai import Language
from prodadvert.domain.entities import Gender, TargetingGender


class CommonErrorSchema(BaseModel):
    code: str
    details: str
    extra: dict | None = None


class ClientSchema(BaseModel):
    client_id: UUID
    login: str = Field(min_length=1)
    age: int = Field(ge=1, le=200)
    location: str = Field(min_length=1)
    gender: Gender

    @field_validator("location")
    def validate_location(cls, value: str) -> str:
        if not any(char.isalnum() for char in value):
            raise ValueError("Location should contain at least one alphanumeric symbol")
        return value

    @field_validator("login")
    def validate_login(cls, value: str) -> str:
        if not any(char.isalnum() for char in value):
            raise ValueError("Login should contain at least one alphanumeric symbol")
        return value


class ClientUpsertSchema(ClientSchema):
    ...


class AdvertiserSchema(BaseModel):
    advertiser_id: UUID
    name: str = Field(min_length=1)


class AdvertiserUpsertSchema(AdvertiserSchema):
    ...


class SetMLScoreSchema(BaseModel):
    client_id: UUID
    advertiser_id: UUID
    score: int


class CampaignTargetingSchema(BaseModel):
    gender: TargetingGender | None = None
    age_from: int | None = None
    age_to: int | None = None
    location: str | None = None


class BaseCampaignSchema(BaseModel):
    ad_title: str
    ad_text: str
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float = Field(gt=0)
    cost_per_click: float = Field(gt=0)
    start_date: int
    end_date: int
    targeting: CampaignTargetingSchema = CampaignTargetingSchema()


class CreateCampaignSchema(BaseCampaignSchema):
    ...


class CampaignSchema(BaseCampaignSchema):
    campaign_id: UUID
    advertiser_id: UUID
    image_uri: str | None


class UpdateCampaignSchema(BaseModel):
    ad_title: str | None = None
    ad_text: str | None = None
    cost_per_impression: float | None = None
    cost_per_click: float | None = None
    start_date: int | None = None
    end_date: int | None = None
    impressions_limit: int | None = None
    clicks_limit: int | None = None
    targeting: CampaignTargetingSchema | None = CampaignTargetingSchema()


class AdvanceTimeSchema(BaseModel):
    current_date: int


class PingResponse(BaseModel):
    status: str = "ok"
    current_date: int


class ClickRequestSchema(BaseModel):
    client_id: UUID


class AdvertisementResponse(BaseModel):
    ad_id: UUID
    ad_title: str
    ad_text: str
    advertiser_id: UUID


class MetricsResponse(BaseModel):
    impressions_count: int
    clicks_count: int
    conversion: float
    spent_impressions: float
    spent_clicks: float
    spent_total: float


class MetricsWithDateResponse(MetricsResponse):
    date: int


class TextGenerationSchema(BaseModel):
    topic: str
    language: Language
    additional: str | None = None


class TextGenerationResponse(BaseModel):
    result: str


class ProfanitySystemStatusResponse(BaseModel):
    is_enabled: bool
