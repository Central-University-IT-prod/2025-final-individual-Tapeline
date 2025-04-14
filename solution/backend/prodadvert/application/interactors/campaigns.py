"""Defines campaign interactors."""
import uuid
from io import BytesIO
from typing import Sequence
from uuid import UUID

from PIL import Image
from dishka import FromDishka

from prodadvert.application.dto import NewCampaignDTO, UpdateCampaignDTO
from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException, InvalidDataException
from prodadvert.application.interfaces.campaigns import CampaignGateway
from prodadvert.application.interfaces.advertisers import AdvertiserGateway
from prodadvert.application.interfaces.common import PaginationParameters
from prodadvert.application.interfaces.date import DateProvider
from prodadvert.application.interfaces.profanity import ProfanityGateway
from prodadvert.application.interfaces.storage import FileStorage
from prodadvert.decorators import raises
from prodadvert.domain.entities import Campaign
from prodadvert.domain.moderation import TextModerator


class GetCampaignInteractor:
    """Get campaign by ID."""

    def __init__(self, gateway: FromDishka[CampaignGateway]) -> None:
        self.gateway = gateway

    @raises(NotFoundException)
    async def __call__(self, uid: UUID, advertiser_id: UUID,) -> Campaign:
        return await self.gateway.get_by_id(uid, advertiser_id)


class CreateCampaignInteractor:
    """Create campaign."""

    def __init__(
            self,
            campaign_gateway: FromDishka[CampaignGateway],
            advertiser_gateway: FromDishka[AdvertiserGateway],
            date_provider: FromDishka[DateProvider],
            profanity_gateway: FromDishka[ProfanityGateway]
    ) -> None:
        self.campaign_gateway = campaign_gateway
        self.advertiser_gateway = advertiser_gateway
        self.date_provider = date_provider
        self.profanity_gateway = profanity_gateway

    @raises(AlreadyExistsException)
    @raises(InvalidDataException)
    async def __call__(
            self,
            advertiser_id: UUID,
            campaign: NewCampaignDTO
    ) -> Campaign:
        await self.date_provider.load()
        self._validate(campaign)
        await self._check_profanity(campaign)
        advertiser = await self.advertiser_gateway.get_advertiser_by_id(
            advertiser_id
        )
        campaign_entity = Campaign(
            id=uuid.uuid4(),
            advertiser=advertiser,
            ad_text=campaign.ad_text,
            ad_title=campaign.ad_title,
            end_date=campaign.end_date,
            start_date=campaign.start_date,
            clicks_limit=campaign.clicks_limit,
            cost_per_click=campaign.cost_per_click,
            impressions_limit=campaign.impressions_limit,
            cost_per_impression=campaign.cost_per_impression,
            target_gender=campaign.target.gender,
            target_age_to=campaign.target.age_to,
            target_age_from=campaign.target.age_from,
            target_location=campaign.target.location,
        )
        await self.campaign_gateway.create(campaign_entity)
        return campaign_entity

    @raises(InvalidDataException)
    def _validate(self, campaign: NewCampaignDTO) -> None:
        if campaign.end_date < campaign.start_date:
            raise InvalidDataException(
                "End date must be greater than start date"
            )
        if (
            campaign.end_date < self.date_provider.today()
            or campaign.start_date < self.date_provider.today()
        ):
            raise InvalidDataException(
                "Dates must be at least today or further"
            )
        if (
            campaign.target.age_to is not None
            and campaign.target.age_from is not None
            and campaign.target.age_from > campaign.target.age_to
        ):
            raise InvalidDataException(
                "age_from must be less than or equal to age_to"
            )

    @raises(InvalidDataException)
    async def _check_profanity(self, dto: NewCampaignDTO) -> None:
        is_enabled = await self.profanity_gateway.is_moderation_enabled()
        if not is_enabled:
            return
        blacklist = await self.profanity_gateway.get_blacklist()
        _check_profanity_in_text(blacklist, dto.ad_title, dto.ad_text)


class ListCampaignsInteractor:
    def __init__(self, gateway: FromDishka[CampaignGateway]) -> None:
        self.gateway = gateway

    async def __call__(
            self,
            advertiser_id: UUID,
            pagination: PaginationParameters
    ) -> Sequence[Campaign]:
        return await self.gateway.get_all(advertiser_id, pagination)


class UpdateCampaignInteractor:
    def __init__(
            self,
            gateway: FromDishka[CampaignGateway],
            date_provider: FromDishka[DateProvider],
            profanity_gateway: FromDishka[ProfanityGateway]
    ) -> None:
        self.gateway = gateway
        self.date_provider = date_provider
        self.profanity_gateway = profanity_gateway

    @raises(NotFoundException)
    @raises(InvalidDataException)
    async def __call__(
            self,
            advertiser_id: UUID,
            campaign_id: UUID,
            updates: UpdateCampaignDTO,
    ) -> Campaign:
        campaign = await self.gateway.get_by_id(campaign_id, advertiser_id)
        await self._check_profanity(updates)
        old_state = campaign.copy()
        campaign.ad_text = updates.ad_text or campaign.ad_text
        campaign.ad_title = updates.ad_title or campaign.ad_title
        if updates.cost_per_click is not None:
            campaign.cost_per_click = updates.cost_per_click
        if updates.cost_per_impression is not None:
            campaign.cost_per_impression = updates.cost_per_impression
        if updates.clicks_limit is not None:
            campaign.clicks_limit = updates.clicks_limit
        if updates.impressions_limit is not None:
            campaign.impressions_limit = updates.impressions_limit
        if updates.start_date is not None:
            campaign.start_date = updates.start_date
        if updates.end_date is not None:
            campaign.end_date = updates.end_date
        campaign.target_gender = updates.target.gender
        campaign.target_location = updates.target.location
        campaign.target_age_to = updates.target.age_to
        campaign.target_age_from = updates.target.age_from
        self._validate(old_state, campaign)
        await self.gateway.update(campaign)
        return campaign

    @raises(InvalidDataException)
    def _validate(self, old_state: Campaign, campaign: Campaign) -> None:
        if (
            campaign.target_age_from is not None
            and campaign.target_age_to is not None
            and campaign.target_age_from > campaign.target_age_to
        ):
            raise InvalidDataException(
                "age_from must be less than or equal to age_to"
            )
        if old_state.start_date > self.date_provider.today():
            return
        if (
            campaign.start_date != old_state.start_date
            or campaign.end_date != old_state.end_date
        ):
            raise InvalidDataException(
                "Cannot set dates after campaign start"
            )
        if (
            campaign.clicks_limit != old_state.clicks_limit
            or campaign.impressions_limit != old_state.impressions_limit
        ):
            raise InvalidDataException(
                "Cannot set limits after campaign start"
            )

    @raises(InvalidDataException)
    async def _check_profanity(self, dto: UpdateCampaignDTO) -> None:
        is_enabled = await self.profanity_gateway.is_moderation_enabled()
        if not is_enabled:
            return
        blacklist = await self.profanity_gateway.get_blacklist()
        _check_profanity_in_text(blacklist, dto.ad_title, dto.ad_text)


class DeleteCampaignInteractor:
    """Delete campaign by ID."""

    def __init__(self, gateway: FromDishka[CampaignGateway]) -> None:
        self.gateway = gateway

    @raises(NotFoundException)
    async def __call__(self, uid: UUID, advertiser_id: UUID) -> None:
        await self.gateway.delete(uid, advertiser_id)


class SetCampaignImageInteractor:
    """Set campaign image."""

    def __init__(
            self,
            gateway: FromDishka[CampaignGateway],
            file_storage: FromDishka[FileStorage]
    ) -> None:
        self.gateway = gateway
        self.file_storage = file_storage

    @raises(NotFoundException)
    async def __call__(
            self, uid: UUID, filename: str | None, file: bytes | None
    ) -> None:
        campaign = await self.gateway.get_by_only_id(uid)
        if file is None or filename is None:
            campaign.image_uri = None
        else:
            # TODO refactor at some point in future
            image = Image.open(BytesIO(file))
            image.thumbnail((960, 960))
            image_io = BytesIO()
            image.save(image_io, format="png")
            uri = await self.file_storage.upload_file(
                filename, image_io.getvalue(), "image/png"
            )
            campaign.image_uri = uri
        await self.gateway.update(campaign)


def _check_profanity_in_text(blacklist, title: str | None, text: str | None):
    moderator = TextModerator(blacklist)
    if title:
        result = moderator.moderate(title)
        if not result.is_ok:
            raise InvalidDataException(
                "Profanity found in title",
                extra={"word": result.banned_fragment}
            )
    if text:
        result = moderator.moderate(text)
        if not result.is_ok:
            raise InvalidDataException(
                "Profanity found in text",
                extra={"word": result.banned_fragment}
            )
