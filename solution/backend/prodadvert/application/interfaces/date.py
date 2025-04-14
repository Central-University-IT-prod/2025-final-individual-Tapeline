from abc import ABC, abstractmethod


class DateProvider(ABC):
    @abstractmethod
    def today(self) -> int:
        """Get current day."""

    @abstractmethod
    async def load(self) -> None:
        """Load date cache."""

    @abstractmethod
    async def set_today(self, current_date: int) -> None:
        """Set current date."""
