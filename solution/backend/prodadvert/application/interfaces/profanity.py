"""Defines application-level interfaces for word blacklist."""

from abc import ABC, abstractmethod


class ProfanityGateway(ABC):
    """Provides access to word blacklist storage."""

    @abstractmethod
    async def set_blacklist(
            self, blacklist: list[str]
    ) -> None:
        """Set word blacklist."""

    @abstractmethod
    async def get_blacklist(self) -> list[str]:
        """Get word blacklist."""

    @abstractmethod
    async def is_moderation_enabled(self) -> bool:
        """Check if moderation is enabled."""

    @abstractmethod
    async def set_moderation_enabled(self, enabled: bool) -> None:
        """Set moderation feature enable flag."""
