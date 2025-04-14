from typing import Sequence, Any
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.campaigns import CampaignGateway
from prodadvert.application.interfaces.common import PaginationParameters
from prodadvert.decorators import raises
from prodadvert.domain.entities import Campaign, Advertiser, TargetingGender
from prodadvert.infrastructure.persistence.models import CampaignModel, MetricModel


class CampaignGatewayImpl(CampaignGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    @raises(NotFoundException)
    async def get_by_id(self, cid: UUID, advertiser_id: UUID) -> Campaign:
        query = (
            select(CampaignModel)
            .filter(
                CampaignModel.id == str(cid),
                CampaignModel.advertiser_id == advertiser_id
            )
            .options(joinedload(CampaignModel.advertiser))
        )
        models = await self._session.execute(query)
        try:
            return _to_campaign_entity(models.scalars().one())
        except NoResultFound as exc:
            raise NotFoundException from exc

    @raises(NotFoundException)
    async def get_by_only_id(self, cid: UUID) -> Campaign:
        query = (
            select(CampaignModel)
            .filter(
                CampaignModel.id == str(cid),
            )
            .options(joinedload(CampaignModel.advertiser))
        )
        models = await self._session.execute(query)
        try:
            return _to_campaign_entity(models.scalars().one())
        except NoResultFound as exc:
            raise NotFoundException from exc

    @raises(AlreadyExistsException)
    @raises(NotFoundException)
    async def create(
            self,
            campaign: Campaign
    ) -> None:
        model = CampaignModel(
            id=campaign.id,
            advertiser_id=campaign.advertiser.id,
            **_to_model_kwargs(campaign)
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

    async def update(self, campaign: Campaign) -> None:
        models = await self._session.execute(
            select(CampaignModel).filter(
                CampaignModel.id == campaign.id,
                CampaignModel.advertiser_id == campaign.advertiser.id
            )
        )
        campaign_model = models.scalars().first()
        for attribute, value in _to_model_kwargs(campaign).items():
            setattr(campaign_model, attribute, value)
        await self._session.commit()

    async def get_all(
            self,
            advertiser_id: UUID,
            pagination: PaginationParameters
    ) -> Sequence[Campaign]:
        query = (
            select(CampaignModel).filter(
                CampaignModel.advertiser_id == advertiser_id
            )
            .options(joinedload(CampaignModel.advertiser))
        )
        if pagination.page >= 0 and pagination.page_size >= 0:
            query = (
                query.limit(pagination.page_size)
                .offset(pagination.page_size * pagination.page)
            )
        models = await self._session.execute(query)
        return list(map(_to_campaign_entity, models.scalars().all()))

    async def get_all_from_all_advertisers(self) -> list[Campaign]:
        models = await self._session.execute(
            select(CampaignModel)
            .options(joinedload(CampaignModel.advertiser))
        )
        return list(map(_to_campaign_entity, models.scalars().all()))

    @raises(NotFoundException)
    async def delete(self, campaign_id: UUID, advertiser_id: UUID) -> None:
        models = await self._session.execute(
            select(CampaignModel).filter(
                CampaignModel.id == campaign_id,
                CampaignModel.advertiser_id == advertiser_id,
            )
        )
        campaign_model = models.first()
        if not campaign_model:
            raise NotFoundException
        await self._session.execute(
            delete(MetricModel).where(MetricModel.campaign_id == campaign_id)
        )
        await self._session.execute(
            delete(CampaignModel).where(
                CampaignModel.id == campaign_id,
                CampaignModel.advertiser_id == advertiser_id,
            )
        )
        await self._session.commit()


def _to_campaign_entity(model: CampaignModel) -> Campaign:
    return Campaign(
        id=_ensure_uuid(model.id),
        advertiser=Advertiser(
            _ensure_uuid(model.advertiser_id),
            model.advertiser.name
        ),
        ad_text=model.ad_text,
        ad_title=model.ad_title,
        end_date=model.end_date,
        start_date=model.start_date,
        clicks_limit=model.clicks_limit,
        cost_per_click=model.cost_per_click,
        impressions_limit=model.impressions_limit,
        cost_per_impression=model.cost_per_impression,
        target_gender=_ensure_gender_enum(model.target_gender),
        target_age_to=model.target_age_to,
        target_age_from=model.target_age_from,
        target_location=model.target_location,
        image_uri=model.image_uri
    )


def _to_model_kwargs(campaign: Campaign) -> dict[str, Any]:
    return {
        "ad_text": campaign.ad_text,
        "ad_title": campaign.ad_title,
        "end_date": campaign.end_date,
        "start_date": campaign.start_date,
        "clicks_limit": campaign.clicks_limit,
        "cost_per_click": campaign.cost_per_click,
        "impressions_limit": campaign.impressions_limit,
        "cost_per_impression": campaign.cost_per_impression,
        "target_gender": campaign.target_gender,
        "target_age_to": campaign.target_age_to,
        "target_age_from": campaign.target_age_from,
        "target_location": campaign.target_location,
        "image_uri": campaign.image_uri
    }


def _ensure_uuid(uid: str | UUID) -> UUID:
    return uid if isinstance(uid, UUID) else UUID(uid)


def _ensure_gender_enum(
        gender: str | TargetingGender | None
) -> TargetingGender | None:
    if not gender:
        return None
    return (
        gender if isinstance(gender, TargetingGender)
        else TargetingGender(gender)
    )
