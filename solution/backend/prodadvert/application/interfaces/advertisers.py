"""Defines application-level interfaces for advertisers."""

from abc import ABC, abstractmethod
from uuid import UUID

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.decorators import raises
from prodadvert.domain.entities import Advertiser


class AdvertiserGateway(ABC):
    """Provides access to advertiser storage."""

    @abstractmethod
    @raises(NotFoundException)
    async def get_advertiser_by_id(self, advertiser_id: UUID) -> Advertiser:
        """Get advertiser by his UUID."""

    @abstractmethod
    @raises(AlreadyExistsException)
    async def create_advertiser(
            self,
            advertiser_id: UUID,
            name: str,
    ) -> Advertiser:
        """Create advertiser."""

    @abstractmethod
    @raises(NotFoundException)
    async def set_score(
            self,
            client_id: UUID,
            advertiser_id: UUID,
            score: int
    ) -> None:
        """Get ML score."""

    @abstractmethod
    async def create_many(
            self, advertisers: list[Advertiser]
    ) -> list[Advertiser]:
        """Bulk upsert."""
