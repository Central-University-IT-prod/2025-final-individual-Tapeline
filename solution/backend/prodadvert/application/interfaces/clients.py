"""Defines application-level interfaces for clients."""

from abc import ABC, abstractmethod
from uuid import UUID

from prodadvert.application.exceptions import NotFoundException, AlreadyExistsException
from prodadvert.decorators import raises
from prodadvert.domain.entities import Client, Gender


class ClientGateway(ABC):
    """Provides access to client storage."""

    @abstractmethod
    @raises(NotFoundException)
    async def get_client_by_id(self, cid: UUID) -> Client:
        """Get client by his UUID."""

    @abstractmethod
    @raises(AlreadyExistsException)
    async def create_client(
            self,
            client_id: UUID,
            login: str,
            age: int,
            location: str,
            gender: Gender
    ) -> Client:
        """Create client."""

    @abstractmethod
    @raises(AlreadyExistsException)
    async def create_many(self, clients: list[Client]) -> list[Client]:
        """Bulk create."""
