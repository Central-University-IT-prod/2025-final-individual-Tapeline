"""Defines application-level interfaces for advertisers."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.application.interfaces.common import PaginationParameters
from prodadvert.decorators import raises
from prodadvert.domain.entities import Campaign


class CampaignGateway(ABC):
    """Provides access to advertiser storage."""

    @abstractmethod
    @raises(NotFoundException)
    async def get_by_id(
            self,
            campaign_id: UUID,
            advertiser_id: UUID,
    ) -> Campaign:
        """Get campaign by its and advertiser's UUID."""

    @abstractmethod
    @raises(NotFoundException)
    async def get_by_only_id(self, campaign_id: UUID) -> Campaign:
        """Get campaign only by its UUID."""

    @abstractmethod
    @raises(AlreadyExistsException)
    @raises(NotFoundException)
    async def create(self, campaign: Campaign) -> None:
        """Create campaign."""

    @abstractmethod
    @raises(NotFoundException)
    async def update(self, campaign: Campaign) -> None:
        """Update campaign."""

    @abstractmethod
    async def get_all(
            self,
            advertiser_id: UUID,
            pagination: PaginationParameters
    ) -> Sequence[Campaign]:
        """Get campaigns of this advertiser with pagination."""

    @abstractmethod
    async def get_all_from_all_advertisers(self) -> list[Campaign]:
        """Get ALL campaigns."""

    @abstractmethod
    @raises(NotFoundException)
    async def delete(
            self,
            campaign_id: UUID,
            advertiser_id: UUID,
    ) -> None:
        """Delete campaign."""
