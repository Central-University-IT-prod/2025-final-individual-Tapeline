from abc import abstractmethod
from asyncio import Protocol
from dataclasses import dataclass


class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        """Commit."""

    @abstractmethod
    async def flush(self) -> None:
        """Flush."""


@dataclass
class PaginationParameters:
    page: int = 0
    page_size: int = 10
