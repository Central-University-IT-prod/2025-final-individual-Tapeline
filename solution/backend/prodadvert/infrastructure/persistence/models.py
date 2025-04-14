import enum
from typing import Optional, Self

from sqlalchemy import Integer, Enum, String, UUID, ForeignKey, Float, Boolean, select, Index
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from sqlalchemy.sql import expression

from prodadvert.domain.entities import Gender, TargetingGender
from prodadvert.infrastructure.persistence.database import Base, LoadSingleton


class ClientModel(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4
    )
    login: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(Enum(Gender))


class AdvertiserModel(Base):
    __tablename__ = "advertisers"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String)


class MLScoreModel(Base):
    __tablename__ = "ml_scores"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4
    )
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    client: Mapped[ClientModel] = relationship()
    advertiser_id: Mapped[str] = mapped_column(ForeignKey("advertisers.id"))
    advertiser: Mapped[AdvertiserModel] = relationship()
    score: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        Index('ml_client_id_index', client_id, postgresql_using='hash'),
        Index('ml_advertiser_id_index', advertiser_id, postgresql_using='hash'),
    )


class CampaignModel(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4
    )
    impressions_limit: Mapped[int] = mapped_column(Integer)
    clicks_limit: Mapped[int] = mapped_column(Integer)
    cost_per_impression: Mapped[float] = mapped_column(Float)
    cost_per_click: Mapped[float] = mapped_column(Float)
    ad_title: Mapped[str] = mapped_column(String)
    ad_text: Mapped[str] = mapped_column(String)
    start_date: Mapped[int] = mapped_column(Integer)
    end_date: Mapped[int] = mapped_column(Integer)
    target_gender: Mapped[Optional[str]] = mapped_column(
        Enum(TargetingGender),
        nullable=True,
        default=None
    )
    target_age_from: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )
    target_age_to: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )
    target_location: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None
    )

    advertiser_id: Mapped[str] = mapped_column(ForeignKey("advertisers.id"))
    advertiser: Mapped[AdvertiserModel] = relationship()

    image_uri: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None
    )


class MetricType(enum.Enum):
    SHOW = "SHOW"
    CLICK = "CLICK"


class MetricModel(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4
    )
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"))
    client: Mapped[ClientModel] = relationship()
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"))
    campaign: Mapped[CampaignModel] = relationship()
    fact: Mapped[str] = mapped_column(Enum(MetricType))
    date: Mapped[int] = mapped_column(Integer)
    cost: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        Index('client_id_index', client_id, postgresql_using='hash'),
        Index('campaign_id_index', campaign_id, postgresql_using='hash'),
    )


class StoredSettings(Base, LoadSingleton):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        default=1
    )
    current_day: Mapped[int] = mapped_column(Integer, default=0)
    moderation_enabled: Mapped[bool] = mapped_column(
        Boolean,
        server_default=expression.false(),
        default=expression.false()
    )

    @classmethod
    async def load(cls, session: AsyncSession) -> Self:
        try:
            return (
                await session.execute(
                    select(StoredSettings).where(StoredSettings.id == 1)
                )
            ).scalar_one()
        except NoResultFound:  # pragma: no cover
            try:
                instance = StoredSettings(id=1)
                session.add(instance)
                await session.commit()
                return instance
            except IntegrityError:
                return (
                    await session.execute(
                        select(StoredSettings).where(StoredSettings.id == 1)
                    )
                ).scalar_one()


class BannedWordModel(Base):
    __tablename__ = "words_blacklist"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        default=1
    )
    word: Mapped[str] = mapped_column(String)
